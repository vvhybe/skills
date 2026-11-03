"""Rasterize the guide's SVG figures and the cover page to PNG, for the Word edition.

Usage: rasterize.py <repo-root> <config.json> <work-dir>

Each SVG is set on a page of its own size with WeasyPrint (so its text uses the guide's fonts) and
rasterized with poppler's pdftoppm. The cover is page 1 of the finished book.pdf. Both tools are
free software, so the Word edition never needs a commercial PDF engine.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_pdf import render  # noqa: E402

REPO = Path(sys.argv[1]).resolve()
CFG = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
BUILD = Path(sys.argv[3]).resolve()
ASSETS = REPO / CFG.get("guide_dir", "docs/guide") / "assets"
FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
OUT = BUILD / "raster"
OUT.mkdir(parents=True, exist_ok=True)
DPI = 240

FACES = "\n".join(
    f"@font-face {{ font-family: {family}; font-weight: {weight}; src: url('{FONTS}/{file}') }}"
    for family, weight, file in [
        ("Inter", 400, "Inter-Regular.ttf"), ("Inter", 600, "Inter-SemiBold.ttf"), ("Inter", 700, "Inter-Bold.ttf"),
        ("Montserrat", 700, "Montserrat-Bold.ttf"),
    ])


def svg_to_png(svg: Path) -> Path:
    txt = svg.read_text(encoding="utf-8")
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', txt)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (800.0, 600.0)
    page = OUT / f"{svg.stem}.html"
    page.write_text(f'''<html><head><style>{FACES}
@page {{ size: {w}px {h}px; margin: 0 }} body {{ margin: 0 }}
svg {{ display: block; width: {w}px; height: {h}px }}
</style></head><body>{txt}</body></html>''', encoding="utf-8")
    pdf = OUT / f"{svg.stem}.pdf"
    render(page, pdf, [FONTS, OUT])  # the SVG is inline; it may read only the fonts and this folder
    subprocess.run(["pdftoppm", "-png", "-singlefile", "-r", str(DPI), str(pdf), str(OUT / svg.stem)], check=True)
    return OUT / f"{svg.stem}.png"


def main():
    for svg in sorted(ASSETS.glob("*.svg")) if ASSETS.is_dir() else []:
        out = svg_to_png(svg)
        print(out.name, out.stat().st_size)
    # The cover, exactly as printed: page 1 of the book.
    subprocess.run(["pdftoppm", "-png", "-singlefile", "-r", "200", "-f", "1", "-l", "1",
                    str(BUILD / "book.pdf"), str(OUT / "cover")], check=True)
    print("cover.png", (OUT / "cover.png").stat().st_size)


if __name__ == "__main__":
    main()
