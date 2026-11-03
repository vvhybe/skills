"""The per-part thumb-tab page backgrounds (A4 SVGs the part pages use as backgrounds).

Usage: make_art.py <config.json> <work-dir>
The four part colours are the book's house palette; book.css and the diagram theme use the same four.
"""

import json
import sys
from pathlib import Path

CFG = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
BUILD = Path(sys.argv[2]).resolve()
BUILD.mkdir(parents=True, exist_ok=True)
COL = {1: "#2a78d6", 2: "#139a6b", 3: "#eb6834", 4: "#4a3aa7"}


def tabs():
    """A4 page backgrounds with a coloured thumb tab on the outer edge, one slot per part."""
    labels = {1: "I", 2: "II", 3: "III", 4: "IV"}
    for n, colour in COL.items():
        top = 38 + (n - 1) * 44
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
            f'<path d="M210 {top}h-9a3 3 0 0 0-3 3v34a3 3 0 0 0 3 3h9z" fill="{colour}"/>'
            f'<text x="204.2" y="{top + 20}" transform="rotate(90 204.2 {top + 20})" text-anchor="middle" '
            f'font-family="Montserrat" font-weight="700" font-size="4.6" fill="#ffffff">PART {labels[n]}</text>'
            "</svg>"
        )
        (BUILD / f"tab{n}.svg").write_text(svg, encoding="utf-8")



tabs()
print("art ok")
