"""Find the page each part and chapter starts on in a rendered PDF; write toc.json.

Usage (in the work dir, next to model.json): toc_pages.py <rendered.pdf>
"""
import json, subprocess, sys
pdf = sys.argv[1]
model = json.load(open("model.json"))
n = int([l for l in subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout.splitlines() if l.startswith("Pages")][0].split()[-1])
pages = [" ".join(subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout.split()) for i in range(1, n + 1)]
class NotLocated(Exception):
    """The rendered PDF has no extractable copy of this heading."""


def find(text, start):
    for i in range(start, n):
        if text in pages[i]:
            return i
    raise NotLocated(text)
entries, cur = [], 2
try:
    i = find("About this guide", cur); entries.append({"level": 2, "text": "About this guide", "anchor": "about", "page": i + 1}); cur = i
    for part in model["parts"]:
        i = find(part["title"], cur + 1); entries.append({"level": 1, "text": f"Part {part['roman']} · {part['title']}", "anchor": f"part_{part['n']}", "page": i + 1}); cur = i
        for ch in part["chapters"]:
            i = find(ch["title"], cur + 1)
            label = f"{int(ch['num'])}" if ch["num"] else "A–Z"
            entries.append({"level": 2, "text": f"{label}\t{ch['title']}", "anchor": ch["id"].replace("-", "_"), "page": i + 1}); cur = i
except NotLocated as missing:
    # A LibreOffice render whose text will not extract (a broken embedded font tag,
    # say) must not fail the build: Word recomputes the field when the file opens.
    print(f"toc: skipped, {missing} not found in the rendered PDF")
    raise SystemExit(0)
colours = {1: "2A78D6", 2: "139A6B", 3: "EB6834", 4: "4A3AA7"}
part = 0
for e in entries:
    if e["level"] == 1:
        part += 1
    e["colour"] = colours.get(part, "EB6834")
json.dump(entries, open("toc.json", "w"), indent=1)
print([(e["text"][:28], e["page"]) for e in entries])
