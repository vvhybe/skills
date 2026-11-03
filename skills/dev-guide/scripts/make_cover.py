"""The book's cover: a public-domain plate printed in one ink above a panel in the volume's colour.

Usage: make_cover.py <config.json> <work-dir> <repo-root> [--preview out.pdf]

Reads `cover` from the config (see references/cover.md) and writes, in the work dir:
  cover-plate.png   the plate, cleaned up and printed in the cover's ink (style "plate")
  cover.html        the cover page fragment that build_book.py places first
  back.html         the back cover fragment
With --preview it also renders the cover alone to a one-page PDF, for fast iteration.
"""
import html
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

CFG_PATH = Path(sys.argv[1])
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
BUILD = Path(sys.argv[2]).resolve()
REPO = Path(sys.argv[3]).resolve()
SKILL = Path(__file__).resolve().parent.parent
BUILD.mkdir(parents=True, exist_ok=True)
COVER = CFG.get("cover", {})
STYLE = COVER.get("style", "plate")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def colour(key, default):
    """Colours go into a style attribute: accept #rrggbb only."""
    value = str(COVER.get(key, default))
    if not HEX.match(value):
        sys.exit(f"cover.{key} must be a #rrggbb colour, not {value!r}")
    return value


INK = colour("ink", "#1d1b18")            # the plate's printing ink
PAPER = colour("paper", "#fbfaf7")        # the ground of the upper cover
COLOUR = colour("colour", "#1f3a5f")      # the volume's colour: the lower panel
ON = colour("on_colour", "#fbfaf7")       # type on the panel
e = html.escape


def rgb(hex_colour):
    h = hex_colour.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def plate():
    """Clean the scan and print it in one ink on the cover's paper. Returns (src, credit, caption)."""
    spec = COVER.get("plate") or {}
    src = (REPO / spec["file"]).resolve()
    if not src.is_relative_to(REPO):
        sys.exit(f"cover plate must be inside the repository (docs/guide/assets/cover/): {spec['file']}")
    if not src.is_file():
        sys.exit(f"cover plate not found: {src}")
    credit = spec.get("credit")
    sidecar = src.with_suffix(".json")
    if not credit and sidecar.is_file():
        credit = json.loads(sidecar.read_text(encoding="utf-8")).get("credit")
    if not credit:
        sys.exit(f"cover plate has no credit: add cover.plate.credit or {sidecar.name} (find_plate.py --get writes it)")
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        ground = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(ground, im)
    im = im.convert("L")
    if crop := spec.get("crop"):                       # fractions: [left, top, right, bottom]
        w, h = im.size
        im = im.crop((round(crop[0] * w), round(crop[1] * h), round(crop[2] * w), round(crop[3] * h)))
    # Old paper reads as grey or yellow. An engraving is mostly paper, so the scan's paper tone is a
    # high percentile of its histogram: map it (and anything lighter) to the cover's paper, and the
    # darkest ink to the cover's ink. `paper`/`ink` in the spec override the measured percentiles.
    hist = im.histogram()
    total = sum(hist)

    def level_at(fraction):
        seen = 0
        for value, count in enumerate(hist):
            seen += count
            if seen >= fraction * total:
                return value
        return 255

    black = level_at(spec.get("ink", 0.01))
    white = max(black + 1, level_at(spec.get("paper", 0.55)) - 8)
    im = im.point(lambda v: 0 if v <= black else 255 if v >= white else round((v - black) * 255 / (white - black)))
    im.thumbnail((2600, 2600), Image.LANCZOS)          # about 300 dpi at cover size
    out = ImageOps.colorize(im, black=rgb(INK), white=rgb(PAPER))
    out.save(BUILD / "cover-plate.png", optimize=True)
    caption = spec.get("caption") or credit
    return out.size, credit, caption


def cover_html():
    series = COVER.get("series") or CFG.get("org", "")
    volume = COVER.get("volume", "")
    title = CFG["title"]
    subtitle = CFG.get("subtitle", "Developer Guide")
    if STYLE == "plate":
        (pw, ph), credit, caption = plate()
        figure = (f'<figure class="plate {"wide" if pw > ph else "tall"}">'
                  f'<img src="cover-plate.png" alt="{e(caption)}">'
                  f'<figcaption>{e(caption)}</figcaption></figure>')
    else:  # "type": no picture; the volume's mark set large in its colour
        mark = COVER.get("mark") or title[:1]
        figure = f'<div class="type-mark" aria-hidden="true">{e(mark)}</div>'
        credit = ""
    (BUILD / "cover-credit.txt").write_text(credit or "", encoding="utf-8")
    return f'''<section class="cover" style="--paper:{PAPER};--colour:{COLOUR};--on:{ON};--ink:{INK}">
  <header class="cover-head"><span>{e(series)}</span><span>{e(volume)}</span></header>
  <div class="cover-art">{figure}</div>
  <div class="cover-panel">
    <div class="title">{e(title)}</div>
    <div class="subtitle">{e(subtitle)}</div>
    <p class="tagline">{e(CFG["tagline"])}</p>
    <footer class="cover-foot"><span>{e(CFG.get("author") or CFG.get("org", ""))}</span><span>{e(CFG.get("edition", ""))}</span></footer>
  </div>
</section>
'''


def back_html():
    engine = "PrinceXML" if os.environ.get("ENGINE", "weasyprint") == "prince" else "WeasyPrint"
    credit = (BUILD / "cover-credit.txt").read_text(encoding="utf-8")
    extra = f"<p>{e(CFG['colophon'])}</p>" if CFG.get("colophon") else ""
    cover_credit = f'<p class="credit">Cover: {e(credit)}</p>' if credit else ""
    return f'''<section class="backcover" style="--colour:{COLOUR};--on:{ON}">
  <div class="colophon">
    <p class="big">{e(CFG["title"])}: {e(CFG.get("subtitle", "Developer Guide"))}</p>
    <p>This book is built from the Markdown pages in <code>{e(CFG.get("guide_dir", "docs/guide"))}/</code> of the
       <code>{e(CFG["repo_name"])}</code> repository. Read them on GitHub or in any Markdown editor; this printed
       edition is generated from the same source. Diagrams are drawn with Mermaid, and the pages are set with {engine}
       in Inter and EB Garamond.</p>
    {extra}
    <p>Written against the repository as it stood on {e(CFG["as_of"])}.</p>
    {cover_credit}
    <p class="legal">{e(CFG.get("legal", ""))}</p>
  </div>
</section>
'''


def preview(out_pdf):
    """The cover alone, for iterating on the design without building the book."""
    css = (SKILL / "assets" / "book.css").read_text(encoding="utf-8").replace("{{FONTS}}", str(SKILL / "assets" / "fonts"))
    css = css.replace("{{BUILD}}", str(BUILD)).replace("{{TABPOS}}", "0 0").replace("{{FOOTER}}", "")
    page = BUILD / "cover-preview.html"
    page.write_text(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>{css}</style></head>'
                    f'<body>{(BUILD / "cover.html").read_text(encoding="utf-8")}</body></html>', encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from render_pdf import render
    render(page, out_pdf, [SKILL / "assets", BUILD])


def main():
    (BUILD / "cover.html").write_text(cover_html(), encoding="utf-8")
    (BUILD / "back.html").write_text(back_html(), encoding="utf-8")
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    print("cover ok:", STYLE)


if __name__ == "__main__":
    main()
