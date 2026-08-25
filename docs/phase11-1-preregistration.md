# Phase 11-1 Pre-registration — The Visual Layer, and Which Forms Are Allowed

Written: 2026-08-25. **Committed before any code**, as 10-1 established.

## Context

10-4 closed the descriptive shortlist. The content has stopped adding new *kinds* of reading — the
signal agreed during 10-3 for when a visual layer becomes the right next step rather than a
distraction from unstable content.

**This phase is where the honesty policy is hardest to hold, not easiest.** Phase 10-2 made the rule
executable in text: one renderer, a banned vocabulary, no central tendency without its spread. None
of that reaches a picture. A line rising to the right edge of a canvas implies continuation without
a single word, and no list of forbidden Russian stems can catch it.

So the criteria here are about **permitted forms**. The vocabulary ban stays and is inherited; it is
simply no longer sufficient.

## Checked before planning

**There is no markup anywhere in the project** — no SVG, no HTML, no template engine, no JavaScript.
Genuinely new ground, so there is no duplication risk and no existing convention to honour or fight.

**`app/presentation/` already exists and is covered by the Phase 10-2 safety tests**, which scan it
for a banned vocabulary and for anything formatting a lone `.median`. A charts module placed there
inherits both, which is the reason to put it there.

**That second test needs one deliberate amendment.** A distribution *drawn* has to read `.median` to
position a tick — and drawing the whole spread is the most honest form available, not a violation.
The rule's purpose is that no lone central tendency reaches a person, so the amendment is precise:
**a function that reads `.median` must read `.p05` and `.p95` in the same function.** Verified by
inspecting the function's own source, so a primitive drawing only the middle cannot compile past the
test.

## Design

**A script writes one self-contained HTML file.** Not an API route: serving means auth, a live
surface and a product decision not yet taken, while a file can be opened, kept, versioned and
compared. Every phase so far has been a read-only script and this is one more.

**Self-contained means self-contained.** Inline SVG, inline CSS, no JavaScript, no external request
of any kind. A page that reaches out is a page that can be tracked, can break offline, and can show
something other than what was measured.

**One module may emit markup, and it exposes a closed set of primitives.** The same shape as the
10-2 text renderer. Adding a chart form becomes a visible decision in a diff rather than something
that appears because it looked nice.

### The permitted primitives

| primitive | what it draws | why it is honest |
| --- | --- | --- |
| `distribution_strip` | the full spread with the current value marked | the literal picture of "94th percentile"; the sample is the chart |
| `ranked_bars` | a ranking, each bar carrying its own low–high range | a mean without its range is the 10-2 failure in pictures |
| `matrix_grid` | a labelled grid, colour symmetric about zero | every cell shows its number; colour is redundant, not load-bearing |
| `plain_rows` | numbers with their `n` | the plumbing block, which is read first here too |

### Forbidden, and the reasoning for each

- **No price line over time.** This is the single most important prohibition, and it bans the one
  chart everybody draws. A line ending at the right edge is read as a beginning; the eye completes
  it. Seven pre-registered measurements say we cannot complete it, so we do not draw the invitation.
- **No trend lines, channels, arrows, or projections.** All of them extend past the data by
  construction.
- **No smoothing that reaches beyond the last observation.**
- **No gauge or dial.** A needle inside a coloured zone says where the value *should* be.
- **Colour encodes sign, never quality.** Red is negative, not bad. A palette keyed to good/bad
  smuggles a recommendation into a stylesheet.
- **No axis without a labelled scale**, and no chart whose `n` and window live outside the image
  where a crop can lose them.

## Acceptance criteria — fixed here, before the code

1. **Exactly one module emits markup.** A source scan over every person-facing path finds `<svg`,
   `<div` or `<html` nowhere else.
2. **The primitive set is closed and pinned**, so adding a fifth form is a visible diff.
3. **No time-series line primitive exists**, asserted by name and by the absence of any polyline
   drawn over dates.
4. **A function reading `.median` reads `.p05` and `.p95` in the same function**, verified against
   the function's own source.
5. **Colour is keyed to sign**: a test finds no `good`, `bad`, `bull`, `bear`, `buy` or `sell` in the
   palette or its callers.
6. **Every rendered chart carries its `n` and its window inside the image.**
7. **The page is self-contained**: the output contains no `http://`, `https://`, `<script` or
   `@import`.
8. **A live run** producing the page from the stored universe, with the plumbing block first.

If criterion 3 cannot be demonstrated, the slice is not done. Every other criterion improves the
page; that one is the difference between a description and an invitation to extrapolate.

## Changes

1. `app/presentation/charts.py` — new, and the only module allowed to emit markup.
2. `app/presentation/page.py` — new: assembles primitives into one self-contained document.
3. `scripts/render_market_page.py` — new, read-only; writes the file and prints where it went.
4. Tests, including all eight criteria; the 10-2 safety block amended as described above.
5. `docs/phase11-1-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No API route and no served page.** Whether this ever becomes a live surface is a separate
  decision, and it is easier to take once the page exists and has been looked at.
- **No interactivity.** No JavaScript at all: a page that recomputes on hover is a page whose claims
  cannot be checked against a stored file.
- **No two-level rendering.** Still the 10-2 position — the split comes when the content has been
  stable through a phase that did not change it, and this phase changes how it is shown.
- **No new measurement, no new data source, no forecast.** Everything drawn is already computed and
  already tested.
- **No schema change.**
