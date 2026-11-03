"""Estimate the printed text size of every Mermaid diagram in book.html.

Usage: diagram_sizes.py <work-dir>
Diagrams are rendered at 16px and scaled to fit the page; anything under
~6.5pt is hard to read on paper. Reshape those: split long chains into
two rows (subgraphs with direction LR inside a flowchart TB, linked
subgraph-to-subgraph), use a mindmap for trees, LR for wide fans.
"""
import re, sys
from pathlib import Path

work = Path(sys.argv[1])
html = (work / "book.html").read_text(encoding="utf-8")
for m in re.finditer(r'<img data-px="(\d+)x(\d+)" src="[^"]+/diagrams/(\w+)\.png" style="width:([\d.]+)mm"', html):
    w, h, key, wmm = int(m.group(1)), int(m.group(2)), m.group(3), float(m.group(4))
    pt = 16 * 0.75 * (wmm / (w / 3 * 0.2646))
    src = [l for l in (work / "diagrams" / f"{key}.mmd").read_text().split("\n") if l.strip()]
    flag = "  <-- small" if pt < 6.5 else ""
    print(f"{pt:4.1f}pt  {wmm:5.1f}mm  {src[0][:16]:16s} {src[1].strip()[:44]}{flag}")
