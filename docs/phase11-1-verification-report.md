# Phase 11-1 Verification Report — The Visual Layer

Generated: 2026-08-25

`PROJECT_PHASE = "phase_11_1_visual_layer"`

Pre-registered in [`docs/phase11-1-preregistration.md`](phase11-1-preregistration.md), committed
before any code (`3f3b52c`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | Exactly one module emits markup | **Pass** |
| 2 | The primitive set is closed and pinned | **Pass** — four, asserted against the module's own public names |
| 3 | **No time-series line primitive exists** | **Pass** — in the module *and* in the rendered page |
| 4 | A drawn median never travels without its edges | **Pass** — checked against each function's source |
| 5 | Colour is keyed to sign, not quality | **Pass** |
| 6 | Every chart carries its `n` and window inside the image | **Pass** |
| 7 | The page is self-contained | **Pass** — verified on the real output |
| 8 | A live run from the stored universe | **Pass** — 23 KB, 9 charts, 5 sections |

## Criterion 3, which decided the slice

**There is no price line, and the rendered file proves it rather than the module claiming it.**

```
<polyline    present: False
<path        present: False
http://      present: False
https://     present: False
<script      present: False
```

A line over time is the one chart everybody draws, and a line ending at the right edge of a canvas
is read as a beginning — the eye completes it whether or not a caption says not to. Seven
pre-registered measurements say we cannot complete it, so the invitation is not drawn. The test
scans for `<polyline`, `<path`, `d="M`, `sparkline` and `trendline`, and the live output was scanned
for the same.

## The four permitted forms

| primitive | what makes it honest |
| --- | --- |
| `distribution_strip` | the whole sample is the chart; the current value is a marker *on* it, so "94th percentile" is literally what the reader sees |
| `ranked_bars` | every bar carries the low-to-high range it was averaged over — a mean of zero over ±2% must not look like a mean of zero over ±0.1% |
| `matrix_grid` | every cell shows its number, so colour is redundant; a reader who ignores it entirely loses nothing |
| `plain_rows` | the plumbing block, read first here as in every report since 9D-1 |

The set is pinned by comparing `PRIMITIVES` against the module's own public callables, so a fifth
shape cannot be added quietly — it fails the test until it is named.

## Colour carries no verdict

`SIGN_POSITIVE` is a blue and `SIGN_NEGATIVE` an amber. **Green and red are absent on purpose:** in
this domain they already mean good and bad, so using them for direction would smuggle approval into
a stylesheet — the same move the Phase 10-2 vocabulary ban exists to stop in a sentence. The page
says so in its own legend rather than relying on a reader to notice.

## Two faults found while building, both of the same kind

**A docstring explaining the vocabulary ban tripped the vocabulary ban** by quoting a forbidden word
while explaining why it is forbidden. Identical to the 10-2 case where a comment in the review
formatter quoted the strings it had just removed. Reworded to name the rule rather than reproduce
it.

**A CSS class called `.median` tripped the lone-median scan.** A substring collision, not a
violation — the third of its kind after "long" inside "belongs" and "carry" inside "carrying". Fixed
by renaming the class to `.mid-tick`, **which keeps the rule tight rather than widening the list of
files allowed to render a middle.** The rename is also the clearer name.

## The amendment, made as pre-registered

A distribution that is *drawn* has to read `.median` to place a tick, and drawing the whole spread
is the most honest form available rather than a violation. So `charts.py` joined `readings.py` on
the short list of files permitted to touch a central tendency — and paid for it with a stricter
test: **any function reading `.median` must read `.p05` and `.p95` in the same function**, verified
by inspecting the function's own source. A primitive drawing only the middle cannot get past it.

This was named in the pre-registration before any code existed, which is the only reason it reads
as a design decision rather than as a rule bent to fit what was built.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 144 source files |
| `uv run pytest` | Passed; **981 passed**, 9 skipped (14 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Live render | 22,987 bytes, 9 charts, 5 sections, no external reference |

One structural change worth recording: the file write moved out of the coroutine into `main()`. It
is a plain synchronous call and belonged there; the linter caught it, and the fix is better code
rather than a suppression.

No schema change, no new dependency, no JavaScript.

## What this settles

Nothing about markets. It settles that this project can show its readings as pictures without any of
them implying a forecast — and that the constraint is enforced by tests over form, because a
vocabulary ban cannot reach a shape.

The natural next questions are product ones rather than measurement ones: whether the page is ever
served rather than written to a file, and whether the two-level rendering discussed in 10-2 is worth
building now that the content has been stable across two phases. Both are decisions, not
measurements, and neither needs to be taken today.
