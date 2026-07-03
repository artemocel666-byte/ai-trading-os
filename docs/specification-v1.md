# Specification v1

AI Trading OS will become a modular Forex analysis and paper-trading platform.

## MVP Direction

- Forex only.
- Seven major pairs.
- M15 and H1 analysis windows.
- Paper trading before any real trading consideration.
- High-quality filtered scenarios, not high-frequency signals.
- Russian explanations for user-facing decisions.
- Structured recording of inputs, decisions, explanations, and results.
- Telegram reports after deterministic checks approve delivery.

## Current Foundation

The current implementation provides runtime, configuration, persistence, scheduler, Telegram, and safety contracts. It does not implement strategy, indicators, live market data, calendar ingestion, OpenAI calls, signal generation, execution, or backtesting.

## Safety Boundary

The project must never include automatic real trading unless a future separately approved scope changes the product definition. The current repository has no mechanism for opening, modifying, or closing real financial positions.

