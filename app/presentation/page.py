"""One self-contained document, assembled from the primitives and nothing else.

Phase 11-1. Inline SVG, inline CSS, **no JavaScript and no external request of any kind**. A page
that reaches out is a page that can be tracked, can break offline, and can show something other than
what was measured — and a file whose claims cannot be checked against what was stored is not worth
producing in a project built on checkable claims.

The document is read in the same order every report in this project is: **plumbing first**, then the
content, then the sentence about what the page is not.
"""

from app.presentation.charts import GRID_LINE, SIGN_NEGATIVE, SIGN_POSITIVE

#: Light by default, dark when the reader's system asks for it. Every colour is declared here; a
#: value that only exists inside a media query would leave the other theme borrowing whatever the
#: host paints.
_STYLE = f"""
:root {{
  --bg: #fbfaf8; --panel: #ffffff; --ink: #1c1a17; --muted: #6b6560;
  --grid: #ded8d1; --band: #e9e4dd;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #16151a; --panel: #1e1d23; --ink: #ece9e4; --muted: #9a938c;
    --grid: #3a3740; --band: #2a2830;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 20px 48px; background: var(--bg); color: var(--ink);
  font: 15px/1.55 ui-sans-serif, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
main {{ max-width: 820px; margin: 0 auto; }}
h1 {{ font-size: 22px; margin: 0 0 4px; letter-spacing: -0.01em; }}
h2 {{ font-size: 16px; margin: 30px 0 8px; font-weight: 620; }}
p.sub {{ color: var(--muted); margin: 0 0 22px; }}
section {{
  background: var(--panel); border: 1px solid var(--grid); border-radius: 10px;
  padding: 14px 16px; margin: 10px 0; overflow-x: auto;
}}
svg.chart {{ display: block; width: 100%; height: auto; max-width: 100%; }}
.lbl {{ fill: var(--ink); font-size: 12px; }}
.tick {{ fill: var(--muted); font-size: 11px; }}
.cell {{ fill: var(--ink); font-size: 10px; }}
.axis {{ stroke: {GRID_LINE}; stroke-width: 1; }}
.band {{ fill: var(--band); }}
.mid-tick {{ stroke: var(--muted); stroke-width: 2; }}
.whisker {{ stroke: {GRID_LINE}; stroke-width: 2; }}
table.rows {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
table.rows caption {{ text-align: left; color: var(--muted); padding-bottom: 6px; }}
table.rows th {{ text-align: left; font-weight: 500; padding: 3px 12px 3px 0; }}
table.rows td {{ text-align: right; font-variant-numeric: tabular-nums; }}
p.absent {{ color: var(--muted); margin: 4px 0; }}
p.footer {{ color: var(--muted); margin-top: 26px; font-size: 13px; }}
.key span {{ display: inline-block; margin-right: 14px; font-size: 12px; color: var(--muted); }}
.key i {{
  display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px;
}}
"""

#: Stated on the page rather than assumed known. Green and red are absent on purpose.
_KEY = (
    '<p class="key">'
    f'<span><i style="background:{SIGN_POSITIVE}"></i>значение выше нуля</span>'
    f'<span><i style="background:{SIGN_NEGATIVE}"></i>ниже нуля</span>'
    "<span>Цвет означает знак, а не оценку.</span>"  # noqa: RUF001
    "</p>"
)

_FOOTER = (
    "Это описание состояния, а не прогноз. Здесь нет ни одной линии, продолжающейся за последнее "  # noqa: RUF001
    "наблюдение, потому что глаз достраивает такую линию сам, а семь предрегистрированных "  # noqa: RUF001
    "измерений проекта показали, что достраивать нечем."
)


def build_page(*, title: str, subtitle: str, sections: tuple[tuple[str, str], ...]) -> str:
    """Assemble one document. `sections` is `(heading, inner markup)` in the order to read them."""
    body = "".join(f"<h2>{heading}</h2><section>{markup}</section>" for heading, markup in sections)
    return (
        "<!doctype html>"
        '<html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{title}</title><style>{_STYLE}</style></head>"
        f'<body><main><h1>{title}</h1><p class="sub">{subtitle}</p>{_KEY}'
        f'{body}<p class="footer">{_FOOTER}</p></main></body></html>'
    )
