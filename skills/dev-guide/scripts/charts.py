"""Chart helpers for a developer guide: honest, print-friendly SVG bar charts.

Import from a small per-repo script and write the SVG into <guide>/assets/:

    import sys; sys.path.insert(0, "<skill>/scripts")
    from charts import hbar_chart
    hbar_chart(Path("docs/guide/assets/endpoints.svg"),
               "Endpoints by router", "Counted from app/routes, 26 September 2026.",
               [("render", 4), ("health", 2)], maxv=5,
               colour_of=lambda label, v: "#2a78d6")

Rules baked in (dataviz): one hue per chart (a second, lighter step may mark a
subgroup), thin bars with a 4px rounded data end, values at the tip or inside a
long bar, a recessive grid, and a white card so the SVG reads on dark pages.
Use real, verified numbers only, and say where they came from in the subtitle.
"""

from pathlib import Path
from xml.sax.saxutils import escape

FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8983"
GRID = "#e4e3df"
CARD = "#ffffff"
DARK_BARS = {"#2a78d6", "#139a6b", "#eb6834", "#4a3aa7"}


def bar_path(x0, y, length, thick, r=4):
    """A bar square at the baseline, rounded at its data end."""
    if length <= r:
        return f'<rect x="{x0}" y="{y}" width="{max(length, 1)}" height="{thick}"/>'
    x1 = x0 + length
    return (
        f'<path d="M{x0} {y} H{x1 - r} Q{x1} {y} {x1} {y + r} '
        f'V{y + thick - r} Q{x1} {y + thick} {x1 - r} {y + thick} H{x0} Z"/>'
    )


def hbar_chart(path, title, subtitle, rows, maxv, colour_of, ref=None, note=None):
    width = 760
    label_w = 150
    x0 = 24 + label_w + 12
    plot_w = width - x0 - 64
    band, thick = 26, 16
    top = 84
    height = top + band * len(rows) + (70 if note else 48)
    scale = plot_w / maxv
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(title)}" font-family="{FONT}">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{CARD}" stroke="{GRID}"/>',
        f'<text x="24" y="36" font-size="17" font-weight="600" fill="{INK}">{escape(title)}</text>',
        f'<text x="24" y="58" font-size="12.5" fill="{INK2}">{escape(subtitle)}</text>',
    ]
    # recessive grid
    step = 10 if maxv <= 20 else 20
    ticks = list(range(0, int(maxv) + 1, step))
    bottom = top + band * len(rows)
    for t in ticks:
        x = x0 + t * scale
        parts.append(f'<line x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{bottom}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{bottom + 16}" font-size="11" fill="{MUTED}" text-anchor="middle">{t}</text>')
    if ref is not None:
        x = x0 + ref[0] * scale
        parts.append(
            f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{bottom}" stroke="{INK2}" '
            f'stroke-width="1" stroke-dasharray="3 3"/>'
        )
        parts.append(f'<text x="{x:.1f}" y="{top - 14}" font-size="11" fill="{INK2}" text-anchor="middle">{escape(ref[1])}</text>')
    for i, (label, value) in enumerate(rows):
        y = top + i * band + (band - thick) / 2
        cy = y + thick / 2 + 4
        parts.append(f'<text x="{x0 - 12}" y="{cy:.1f}" font-size="12.5" fill="{INK}" text-anchor="end">{escape(label)}</text>')
        parts.append(f'<g fill="{colour_of(label, value)}">{bar_path(x0, y, value * scale, thick)}</g>')
        length = value * scale
        if length > 60:
            # the value fits inside the bar end: dark text on a light bar, white on a dark one
            fill = "#ffffff" if colour_of(label, value) in DARK_BARS else INK
            parts.append(
                f'<text x="{x0 + length - 8:.1f}" y="{cy:.1f}" font-size="12" font-weight="600" fill="{fill}" text-anchor="end">{value}</text>'
            )
        else:
            parts.append(
                f'<text x="{x0 + length + 6:.1f}" y="{cy:.1f}" font-size="12" font-weight="600" fill="{INK2}">{value}</text>'
            )
    if note:
        parts.append(f'<text x="24" y="{height - 18}" font-size="11.5" fill="{INK2}">{escape(note)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


