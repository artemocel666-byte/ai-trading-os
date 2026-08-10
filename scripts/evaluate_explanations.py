"""Measure whether a given model can produce an explanation this project would accept.

The Phase 8A validator is strict on purpose: Russian, short, no emoji, no trading language, and no
number that was not in the input. A large hosted model clears that most of the time. A small model
running on a laptop may not, and "may not" is not a number.

This script makes it one. It walks real windows, asks the configured model to explain each, and
reports the share accepted plus **why the rest were rejected** — which is the useful part. A run
dominated by `UNKNOWN_NUMBER` means the model invents figures; by `ACTIONABLE_TEXT` that it gives
advice it was told not to; by `TOO_LONG` that the prompt needs tightening rather than the model
replacing.

Read-only in both directions: it writes nothing to storage, and it calls `explain_validated`, so no
unchecked model text is ever printed as though it had passed.
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from collections import Counter
from datetime import timedelta
from decimal import Decimal

import httpx

from app.adapters.chat_completions_explanations import (
    LOCAL_PROVIDER_NAME,
    OPENAI_PROVIDER_NAME,
    ChatCompletionsExplanationAdapter,
    build_completion_timeout,
)
from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Timeframe
from app.domain.entities.explanation import ExplanationOutcome
from app.domain.explanation_contract import build_explanation_input
from app.domain.rule_replay import (
    DEFAULT_WINDOW_CANDLES,
    iter_replay_windows,
    order_candles,
)
from app.domain.snapshot_review import build_snapshot_backed_review
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from scripts.replay_rules import load_history

#: Long enough for a slow local model to answer at all. The point here is to learn what the model
#: produces, not to enforce the interactive budget `/explain` uses.
DEFAULT_TIMEOUT_SECONDS = 180.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ask a model to explain real windows and report how often the Phase 8A validator "
            "accepted the answer, and why it rejected the rest. Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--sample-size", type=int, default=20, help="how many windows to ask about")
    parser.add_argument(
        "--provider",
        choices=("local", "openai"),
        default="local",
        help="which model to measure; independent of EXPLANATION_PROVIDER",
    )
    parser.add_argument("--base-url", default=None, help="overrides the configured base URL")
    parser.add_argument("--model", default=None, help="overrides the configured model name")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--samples-to-print", type=int, default=2)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--exclude-closed-market",
        action="store_true",
        help="ask only about windows built entirely from traded candles",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _build_adapter(
    args: argparse.Namespace,
    settings: Settings,
    client: httpx.AsyncClient,
) -> ChatCompletionsExplanationAdapter:
    """Built here rather than through the factory, so a run does not depend on the live switch.

    Measuring a model and configuring one for `/explain` are different acts: you should be able to
    try a candidate model without pointing the bot at it first.
    """
    local = args.provider == "local"
    api_key = None
    if not local:
        if settings.openai_api_key is None:
            raise ValueError("измерение OpenAI требует OPENAI_API_KEY")
        api_key = settings.openai_api_key.get_secret_value()
    return ChatCompletionsExplanationAdapter(
        client=client,
        provider_name=LOCAL_PROVIDER_NAME if local else OPENAI_PROVIDER_NAME,
        api_key=api_key,
        base_url=args.base_url
        or (settings.local_llm_base_url if local else settings.openai_base_url),
        model=args.model or (settings.local_llm_model if local else settings.openai_model),
        timeout=build_completion_timeout(args.timeout_seconds),
        # One attempt. A retry would hide a model that is simply too slow, which is exactly the
        # thing worth learning about a local one.
        retry_count=0,
        retry_backoff_seconds=0.0,
        max_output_tokens=(
            settings.local_llm_max_output_tokens if local else settings.openai_max_output_tokens
        ),
    )


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(int(fraction * len(ordered)), len(ordered) - 1)
    return ordered[index]


async def _main() -> int:
    args = _parse_args()
    if args.sample_size < 1:
        raise ValueError("--sample-size must be at least one window")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)

    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        candles, events = await load_history(
            build_uow_factory(create_session_factory(engine)),
            pair=pair,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            window_candles=DEFAULT_WINDOW_CANDLES,
        )
        ordered = order_candles(candles, pair=pair, timeframe=timeframe)
        if len(ordered) < DEFAULT_WINDOW_CANDLES:
            raise ValueError("not enough stored candles to build a single window")

        windows = list(
            iter_replay_windows(
                pair=pair,
                timeframe=timeframe,
                ordered_candles=ordered,
                ordered_events=sorted(events, key=lambda event: event.scheduled_at),
                window_candles=DEFAULT_WINDOW_CANDLES,
                skip_closed_market=args.exclude_closed_market,
            )
        )
    except ValueError as error:
        print(f"Measurement could not run: {error}")
        await engine.dispose()
        return 1
    finally:
        await engine.dispose()

    if not windows:
        print("No windows in that range.")
        return 1

    # Evenly spaced across the range rather than the newest N: a model's behaviour should be
    # measured over varied market states, not over one afternoon.
    step = max(len(windows) // args.sample_size, 1)
    sampled = windows[::step][: args.sample_size]

    accepted = 0
    failures: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    durations: list[float] = []
    errors: Counter[str] = Counter()
    accepted_samples: list[tuple[str, str]] = []
    rejected_samples: list[tuple[str, str]] = []

    async with httpx.AsyncClient() as client:
        adapter = _build_adapter(args, settings, client)
        print(
            f"Measuring {adapter.provider_name} / {adapter.model_name} "
            f"on {len(sampled)} {pair.value} {timeframe.value} windows...",
            file=sys.stderr,
        )
        for index, window in enumerate(sampled, start=1):
            snapshot = window.snapshot
            as_of = snapshot.window.as_of
            decision = build_snapshot_backed_review(snapshot, as_of).decision
            statuses[decision.status.value] += 1
            explanation_input = build_explanation_input(decision, snapshot)

            started = time.monotonic()
            try:
                outcome: ExplanationOutcome = await adapter.explain_validated(
                    explanation_input, utc_now()
                )
            except Exception as error:  # a provider failure is data about the model, not a crash
                errors[type(error).__name__] += 1
                print(f"  [{index}/{len(sampled)}] {as_of} error", file=sys.stderr)
                continue
            durations.append(time.monotonic() - started)

            if outcome.validation.accepted:
                accepted += 1
                if len(accepted_samples) < args.samples_to_print and outcome.text:
                    accepted_samples.append((str(as_of), outcome.text))
            else:
                codes = sorted({issue.code.value for issue in outcome.validation.issues})
                for code in codes:
                    failures[code] += 1
                if len(rejected_samples) < args.samples_to_print:
                    rejected_samples.append((str(as_of), ", ".join(codes)))
            print(
                f"  [{index}/{len(sampled)}] {as_of} "
                f"{'accepted' if outcome.validation.accepted else 'rejected'}",
                file=sys.stderr,
            )

    answered = len(durations)
    acceptance = Decimal(accepted) / Decimal(answered) if answered else None

    if args.format == "json":
        print(
            json.dumps(
                {
                    "provider": adapter.provider_name,
                    "model": adapter.model_name,
                    "pair": pair.value,
                    "timeframe": timeframe.value,
                    "windows_asked": len(sampled),
                    "windows_answered": answered,
                    "accepted": accepted,
                    "acceptance_share": None if acceptance is None else str(acceptance),
                    "rejection_codes": dict(failures),
                    "decision_statuses": dict(statuses),
                    "provider_errors": dict(errors),
                    "seconds": {
                        "median": statistics.median(durations) if durations else None,
                        "p90": _percentile(durations, 0.9) if durations else None,
                        "max": max(durations) if durations else None,
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    print(f"\nModel: {adapter.provider_name} / {adapter.model_name}")
    print(f"Windows: asked {len(sampled)}, answered {answered}, accepted {accepted}")
    if acceptance is not None:
        print(f"Acceptance: {acceptance * 100:.1f}%")
    if durations:
        print(
            f"Seconds:    median {statistics.median(durations):.1f}, "
            f"p90 {_percentile(durations, 0.9):.1f}, max {max(durations):.1f}"
        )
    if errors:
        print("Provider errors: " + ", ".join(f"{k}={v}" for k, v in errors.most_common()))
    if failures:
        print("\nWhy answers were rejected (a rejection can have several reasons):")
        for code, count in failures.most_common():
            print(f"  {code:<18} {count}")
    print("\nWindows by pipeline verdict: " + ", ".join(f"{k}={v}" for k, v in statuses.items()))

    for label, samples in (("Accepted", accepted_samples), ("Rejected", rejected_samples)):
        for as_of, detail in samples:
            print(f"\n{label} — {as_of}\n  {detail}")

    print(
        "\nRejected text is never printed: `explain_validated` drops it, so nothing unchecked "
        "reaches this output."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
