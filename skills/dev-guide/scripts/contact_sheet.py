"""Tile every page of a PDF into contact sheets for a quick visual review.

Usage: contact_sheet.py <file.pdf> <out-prefix> [dpi=28] [per-sheet=40]
Writes <out-prefix>-1.png, -2.png, … ; Read them to spot broken pages.
"""
import glob, subprocess, sys, tempfile
from PIL import Image, ImageDraw

pdf, prefix = sys.argv[1], sys.argv[2]
dpi = sys.argv[3] if len(sys.argv) > 3 else "28"
per = int(sys.argv[4]) if len(sys.argv) > 4 else 40
tmp = tempfile.mkdtemp()
subprocess.run(["pdftoppm", "-r", dpi, "-png", pdf, f"{tmp}/p"], check=True)
files = sorted(glob.glob(f"{tmp}/p-*.png"))
w, h = Image.open(files[0]).size
cols = 10
for s in range(0, len(files), per):
    chunk = files[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 22) + 8), "#888")
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 22)
        sheet.paste(Image.open(f), (x, y))
        d.text((x + 2, y + h + 4), f.split("-")[-1][:-4], fill="white")
    out = f"{prefix}-{s // per + 1}.png"
    sheet.save(out)
    print(out)
