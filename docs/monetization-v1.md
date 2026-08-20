# Monetization v1

Written: 2026-08-20. **A product document, not a phase.** Nothing here is scheduled, no code depends
on it, and no acceptance criterion in `PLANS.md` references it. It exists so that the pricing
decision, when it is taken, is taken against written assumptions rather than against a memory of a
conversation — the same reason the measurement pre-registrations exist.

Every price below is a **placeholder**. The structure is the argument; the numbers are not.

## What is actually being sold

Seven pre-registered measurements returned nothing, and 9D-4 said why: what can be computed from
public data is already in the price. Phase 10 drew the conclusion — **context rather than
conclusion**. Monetization has to be built from that property, not in spite of it.

So the sellable thing is not a forecast. It is four things the project already has and most of the
market does not:

1. **A clean, provenance-checked cross-section.** 44 of 45 pairs, 224,587 daily bars, every pair
   present in every year 2007–2026, plus 5,855 monthly interbank rates for all ten currencies. No
   fabricated rows — `load_history` refuses them, and 39 were removed in 9A-5. Absences are named,
   never substituted.
2. **An explainer that cannot invent a number.** The Phase 8A validator is fail-closed and rejects
   any figure absent from its input. 8D measured it rather than assumed it: `gpt-oss-20b` went from
   20% to 85% acceptance with the validator untouched, median latency 3.4s.
3. **A forward ledger that is checkable per row.** 9C-1 stores `recorded_at` and `as_of` both, so a
   row written after its own future is self-identifying. Verified against real EURUSD: 384 rows,
   zero mismatches.
4. **The nulls themselves.** Seven measurements, criteria fixed in advance, published with the
   evidence — including the one that was retracted after the data underneath it was found to be 28%
   synthetic.

Points 2, 3 and 4 are not trading products at all. That is the important observation in this
document.

## Checked before writing

**1. There is no public API surface.** `app/api/routes` holds `health.py` and `system.py`. Every
user-facing feature today is a Telegram command — `/snapshot`, `/digest`, `/review`, `/explain` —
authorized to a single configured user ID. Any tier that promises an API is promising unwritten code.

**2. `/review` currently renders a verdict from rules 9C-2 measured to separate nothing.** It cannot
be sold as it stands. 10-1 says so explicitly and defers the reconciliation to 10-2. **No tier may
ship before that reconciliation**, or the product's first paid impression is a confident-looking
status derived from rules known not to predict.

**3. The descriptive analytics are not built.** 10-2 (percentiles, decomposition, correlations) and
10-3 do not exist; 10-1 is plumbing that keeps the universe from rotting. Everything in the tier
grid below except the raw context of one pair is **unwritten**.

**4. 45 pairs are not 45 observations.** `app/domain/currency_universe.py` states it: ten currencies
give forty-five ratios, but the independent dimensions number closer to nine. A tier that advertises
"44 instruments" against a free tier's "3" is selling breadth that is partly an illusion, and the
product copy must not pretend otherwise.

**5. The economic calendar is blocked behind a paid plan.** Verified 2026-08-01: `402 Restricted
Endpoint` on FMP's free tier, a control call to `/stable/quote` returned 200. Any event-context
feature carries a data cost before it carries a price.

## The two audiences

The commonly proposed ladder — free → beginner → professional — hides two populations with opposite
economics, and treating them as one ladder is the main error to avoid.

| | Retail beginner | Professional / semi-professional |
| --- | --- | --- |
| Wants | to be told what to do | clean data and context, no opinions |
| This product | **refuses**, by architecture and by test | does exactly that |
| Expected ARPU | low, churn high | high, churn low |
| Support cost | high | near zero |
| Regulatory exposure | higher | lower |
| Values the nulls | no — reads as "it does not work" | yes — saves months of their own work |

The defining property of this project, that it does not predict, is a dealbreaker for the first
column and a purchase argument for the second. **The professional tier is therefore not the top of a
retail ladder — it is a different product**, and it is the one with a business underneath it.

Retail is worth building as a funnel and a reputation surface. It should not carry the revenue plan.

## Axes that may be gated

Each of these is gated at no cost to honesty, and the first three map onto machinery that exists.

1. **Instrument breadth.** Free: three majors. Paid: the full universe. Zero honesty cost, subject to
   finding 4 above being stated plainly.
2. **Freshness.** Free: yesterday's close, published once at a fixed UTC hour — which is exactly what
   10-1's cron job produces. Paid: as soon as ingested.
3. **Width of context.** Free answers one question about one pair. Paid adds the cross-section (9D-2
   machinery), the carry decomposition (9D-4), correlations, and the data-quality panel.
4. **Volume of variable-cost work.** Explanations per month and alerts per month. **This is the only
   axis that tracks real marginal cost**, which makes it the one that can be metered without
   arbitrariness.
5. **Export and programmatic access.** CSV and API always paid — when they exist.

`EXPLANATION_PROVIDER=disabled|openai|local` is already a margin lever in the codebase. Free and
entry tiers answered by the local model at 85% acceptance; the paid tier by the frontier model. A
free user then costs electricity, not API spend.

## Axes that must never be gated

**Language register is not a tier.** Plain wording and term glossaries are the hardest and most
valuable part to build, and putting them behind a wall charges beginners for the ability to
understand what they bought. Professionals read plain language too. Register is a **toggle on every
tier, including free**.

**Depth of history is not a quality gate.** A percentile against one year and a percentile against
nineteen do not merely differ in precision — **they can contradict each other**, and the free user
would systematically get the misleading one: in a quiet year every move looks extreme, and in
2008 or 2020 nothing does. That inverts the warning exactly when it matters. A restricted-history
free tier would frighten people during calm and reassure them during an event. For a project whose
only asset is honesty, this is the worst available bug. Gate the number of pairs, not the sample
behind the number.

**Trust infrastructure stays free and public.** The methodology, the seven nulls, the
pre-registration archive, the forward ledger, the disclaimers, the glossary. These are not features
withheld to create an upgrade — they are the reason anything above them can be charged for. The
forward ledger in particular should be a public page: no retail analytics competitor can show
levels fixed before the outcome existed, with a schema in which backdating is self-evident.

## The tier grid

Placeholder prices, EUR, monthly.

**Free — "Overview".** Funnel, not revenue. Three pairs, yesterday's close, **full-history**
percentile, plain-language mode, local model, no alerts.

**~12 — "Context".** Where both the student and the serious amateur land. Full universe, the
cross-section, both language registers, glossary, ~5 alerts, ~30 explanations per month.

**~59 — "Professional".** The reference use. Carry decomposition and the FRED rates, correlation and
regime views, per-instrument data-quality and provenance panel, unlimited alerts, CSV export, the
methodology and pre-registration archive, frontier model.

**From ~300 — "Team / B2B".** API seats, white-label widget, a freshness SLA the 10-1 machinery can
actually honour, custom pre-registered tests.

**"Student" is a discount, not a tier.** Verified academic status, 50–70% off the same full product.
A dumbed-down student edition trains the wrong habit and produces a user who has never seen the
thing they are meant to renew.

## Beyond subscriptions

Ranked by revenue per unit of build effort, not by how interesting they are.

- **The explanation validator as a component.** Phase 8A rejects any number absent from its input,
  fail-closed. Sold to fintechs, brokers, media desks and compliance teams. Not a trading product,
  and plausibly the most valuable single artefact in the repository — in a market saturated with
  unchecked model output, "cannot state a figure that is not in the source" is a specification
  people are looking for.
- **The measurement bench as a service.** "Send your idea, get a pre-registered test and a report
  either way." The nulls are the deliverable: 9C-4 established that a candidate needs roughly 6.5
  points over the base rate on EURUSD M15 merely to break even at 42.86%, and knowing an idea does
  not clear that bar is worth money to someone about to spend a quarter finding out.
- **B2B white-label.** A broker or an educational product cannot easily give advice either. A
  market-context widget that is *provably* non-advisory — enforced by tests, not by policy — is
  attractive to their product and compliance teams simultaneously. B2B pays multiples of retail.
- **Alerts.** The one thing retail pays for that is not a signal: "tell me when EURSEK enters the top
  1% of realized volatility since 2007." Historically the strongest single conversion trigger in
  tools of this shape.
- **A periodic written market-context report.** Cheap to produce from 10-2 output, sells low, and
  functions mainly as the top of the funnel.
- **Raw data access.** Listed last deliberately — see blockers.

## Assumptions, and what would falsify each

The commercial analogue of pre-registration. Each assumption is written before the evidence, with
the observation that would kill it.

1. **Professionals will pay for context without conclusions.** Falsified if, after twenty structured
   conversations with the target profile, fewer than five say they would pay at the "Professional"
   placeholder price — or if a paid pilot converts under 20%.
2. **Retail free-to-paid conversion is under 2%.** This is the assumption the plan is built on, not a
   fear. Falsified — happily — if conversion exceeds 2% within 90 days at 500 or more free users, in
   which case retail deserves more investment than this document gives it.
3. **The nulls are an asset rather than a liability.** Measurable: whether visitors who reach the
   methodology page convert better or worse than those who do not, and whether churn differs.
   Falsified if either comparison runs the wrong way.
4. **The validator is sellable standalone.** Falsified if fifteen outbound conversations produce no
   second meeting.
5. **Explanations are the dominant variable cost.** Falsified by the first month of real billing if
   data or infrastructure exceeds model spend, in which case the metered axis is the wrong one.

If 1 and 4 both fail, the honest reading is that this is a research bench with no product attached,
and the correct response is to say so rather than to reprice.

## Blockers

1. **Data redistribution rights are unverified.** Nothing in this repository establishes what Twelve
   Data's terms permit. Derived statistics and raw bar redistribution are usually treated very
   differently, and the API tier above assumes an answer nobody has looked up. **Check before any
   tier that implies data access is published.** FRED is public domain and is not affected.
2. **The regulatory line runs where the code already draws it.** Context, data and education are
   generally outside licensed advice; the moment a tier promises direction or "signals" it is a
   different legal regime. `REAL_TRADING_ENABLED` stays `False` permanently and no function returns a
   `SignalDirection` — that constraint is now also a commercial asset and must not be traded away for
   a tier.
3. **10-2 does not exist.** The grid describes a product that is one to three slices away. Selling
   before it is built means selling `/review`, and finding 2 above says why that must not happen.

## Explicitly not in this document

- **No decision.** Nothing here is approved, scheduled, or a commitment to build.
- **No prices.** The numbers are placeholders for a structure and have had no market contact.
- **No changes to `PLANS.md`, `README.md`, or the roadmap.** This document is referenced by nothing.
- **No legal advice.** Blocker 1 needs the terms read and blocker 2 needs a lawyer, and this
  document is neither.
- **No personalization.** Nothing proposed here segments output by a user's positions, capital or
  circumstances, which is the line between a context product and an advisory one.
