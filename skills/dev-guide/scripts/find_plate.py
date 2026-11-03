"""Find a public-domain plate (engraving, scientific or technical plate) for a book cover.

Searches open collections that need no API key, keeps only public-domain or CC0 images by default,
and records the credit line the colophon prints.

  find_plate.py "printing press engraving"                 list candidates
  find_plate.py "printing press engraving" --sheet out.png  also a contact sheet to look at
  find_plate.py --get commons:File:Name.jpg --out <dir>     download one, with <slug>.json credit
  find_plate.py --get met:12345 --out <dir>
  find_plate.py --get aic:27992 --out <dir>

Sources: Wikimedia Commons, The Metropolitan Museum of Art, the Art Institute of Chicago.
--allow-by also lists CC BY and CC BY-SA files (credit required; check the licence terms).
Standard library only; Pillow is needed for --sheet.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

UA = "dev-guide-cover/1.0 (https://github.com/vvhybe/skills; book cover research)"
OPEN = re.compile(r"public domain|^pd\b|pd-|cc0|no restrictions", re.I)
BY = re.compile(r"^cc[ -]by(-sa)?\b", re.I)


def get_json(url):
    # the Art Institute of Chicago asks API clients to identify themselves in AIC-User-Agent
    req = urllib.request.Request(url, headers={"User-Agent": UA, "AIC-User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def commons(q, n, allow_by):
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": n * 2, "prop": "imageinfo",
        "iiprop": "url|size|extmetadata", "iiurlwidth": 600,
    }
    data = get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))
    out = []
    for page in (data.get("query", {}).get("pages") or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        if not (OPEN.search(lic) or (allow_by and BY.search(lic))):
            continue
        out.append({
            "ref": "commons:" + page["title"].replace(" ", "_"),
            "title": strip_html(meta.get("ObjectName", {}).get("value", "")) or page["title"][5:],
            "creator": strip_html(meta.get("Artist", {}).get("value", "")) or "unknown",
            "date": strip_html(meta.get("DateTimeOriginal", {}).get("value", "")),
            "licence": lic, "width": info.get("width"), "height": info.get("height"),
            "page": info.get("descriptionurl"), "thumb": info.get("thumburl"), "full": info.get("url"),
            "collection": "Wikimedia Commons",
        })
    return out[:n]


def met(q, n, _allow_by):
    ids = get_json("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q="
                   + urllib.parse.quote(q)).get("objectIDs") or []
    out = []
    for oid in ids[: n * 3]:
        try:
            o = get_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        except Exception:
            continue
        if not (o.get("isPublicDomain") and o.get("primaryImage")):
            continue
        out.append({
            "ref": f"met:{oid}", "title": o.get("title", ""), "creator": o.get("artistDisplayName") or "unknown",
            "date": o.get("objectDate", ""), "licence": "Public domain (CC0, The Met Open Access)",
            "width": None, "height": None, "page": o.get("objectURL"),
            "thumb": o.get("primaryImageSmall") or o.get("primaryImage"), "full": o.get("primaryImage"),
            "collection": "The Metropolitan Museum of Art",
        })
        if len(out) >= n:
            break
    return out


def aic(q, n, _allow_by):
    params = {"q": q, "limit": n * 2, "fields": "id,title,image_id,artist_display,date_display,is_public_domain"}
    data = get_json("https://api.artic.edu/api/v1/artworks/search?" + urllib.parse.urlencode(params))
    base = (data.get("config") or {}).get("iiif_url", "https://www.artic.edu/iiif/2")
    out = []
    for a in data.get("data", []):
        if not (a.get("is_public_domain") and a.get("image_id")):
            continue
        out.append({
            "ref": f"aic:{a['id']}", "title": a.get("title", ""), "creator": (a.get("artist_display") or "unknown").split("\n")[0],
            "date": a.get("date_display", ""), "licence": "Public domain (CC0, Art Institute of Chicago)",
            "width": None, "height": None, "page": f"https://www.artic.edu/artworks/{a['id']}",
            "thumb": f"{base}/{a['image_id']}/full/600,/0/default.jpg", "full": f"{base}/{a['image_id']}/full/3000,/0/default.jpg",
            "collection": "Art Institute of Chicago",
        })
    return out[:n]


SOURCES = {"commons": commons, "met": met, "aic": aic}


def resolve(ref, allow_by=True):
    """Look one reference up again, so --get never trusts a stale listing."""
    source, _, key = ref.partition(":")
    if source == "commons":
        params = {"action": "query", "format": "json", "titles": key.replace("_", " "), "prop": "imageinfo",
                  "iiprop": "url|size|extmetadata"}
        page = next(iter(get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))["query"]["pages"].values()))
        info = page["imageinfo"][0]
        meta = info.get("extmetadata", {})
        return {"ref": ref, "title": strip_html(meta.get("ObjectName", {}).get("value", "")) or key[5:],
                "creator": strip_html(meta.get("Artist", {}).get("value", "")) or "unknown",
                "date": strip_html(meta.get("DateTimeOriginal", {}).get("value", "")),
                "licence": strip_html(meta.get("LicenseShortName", {}).get("value", "")),
                "page": info["descriptionurl"], "full": info["url"], "collection": "Wikimedia Commons"}
    if source == "met":
        o = get_json(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{key}")
        if not o.get("isPublicDomain"):
            sys.exit(f"{ref} is not public domain")
        return {"ref": ref, "title": o.get("title", ""), "creator": o.get("artistDisplayName") or "unknown",
                "date": o.get("objectDate", ""), "licence": "Public domain (CC0, The Met Open Access)",
                "page": o.get("objectURL"), "full": o.get("primaryImage"), "collection": "The Metropolitan Museum of Art"}
    if source == "aic":
        a = get_json(f"https://api.artic.edu/api/v1/artworks/{key}?fields=id,title,image_id,artist_display,date_display,is_public_domain")
        d, base = a["data"], a["config"]["iiif_url"]
        if not d.get("is_public_domain"):
            sys.exit(f"{ref} is not public domain")
        return {"ref": ref, "title": d.get("title", ""), "creator": (d.get("artist_display") or "unknown").split("\n")[0],
                "date": d.get("date_display", ""), "licence": "Public domain (CC0, Art Institute of Chicago)",
                "page": f"https://www.artic.edu/artworks/{key}", "full": f"{base}/{d['image_id']}/full/3000,/0/default.jpg",
                "collection": "Art Institute of Chicago"}
    sys.exit(f"unknown source in {ref} (use commons:, met: or aic:)")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "plate"


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())


def contact_sheet(items, out):
    from io import BytesIO
    from PIL import Image, ImageDraw
    cell, pad = 300, 12
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + 40 + pad) + pad), "#f2f0eb")
    draw = ImageDraw.Draw(sheet)
    for i, it in enumerate(items):
        x, y = pad + (i % cols) * (cell + pad), pad + (i // cols) * (cell + 40 + pad)
        try:
            req = urllib.request.Request(it["thumb"], headers={"User-Agent": UA})
            img = Image.open(BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert("RGB")
            img.thumbnail((cell, cell))
            sheet.paste(img, (x + (cell - img.width) // 2, y + (cell - img.height) // 2))
        except Exception as e:  # keep going; one broken thumbnail shouldn't sink the sheet
            draw.text((x + 8, y + 8), f"no preview: {e}"[:40], fill="#a33")
        draw.text((x, y + cell + 4), f"[{i}] {it['ref']}"[:48], fill="#111")
        draw.text((x, y + cell + 20), f"{it['title']}"[:48], fill="#555")
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?")
    ap.add_argument("-n", type=int, default=8, help="candidates per source (default 8)")
    ap.add_argument("--sources", default="commons", help="commons (default), aic (may refuse some networks). met: refs still download; its search API was retired")
    ap.add_argument("--allow-by", action="store_true", help="also list CC BY / CC BY-SA files")
    ap.add_argument("--sheet", help="write a contact sheet PNG of the candidates")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--get", help="download one reference (commons:File:…, met:<id>, aic:<id>)")
    ap.add_argument("--out", default=".", help="folder for --get (default: current)")
    a = ap.parse_args()

    if a.get:
        it = resolve(a.get)
        if not (OPEN.search(it["licence"]) or (a.allow_by and BY.search(it["licence"]))):
            sys.exit(f"refusing {a.get}: licence is '{it['licence']}' (pass --allow-by for CC BY / BY-SA)")
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        name = slug(it["title"] or a.get)
        ext = Path(urllib.parse.urlparse(it["full"]).path).suffix.lower() or ".jpg"
        if ext not in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"):
            ext = ".jpg"
        download(it["full"], out / f"{name}{ext}")
        it["file"] = f"{name}{ext}"
        it["retrieved"] = date.today().isoformat()
        it["credit"] = f"{it['title']}" + (f", {it['creator']}" if it["creator"] != "unknown" else "") + \
                       (f", {it['date']}" if it["date"] else "") + f". {it['collection']}, {it['licence']}."
        (out / f"{name}.json").write_text(json.dumps(it, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"saved {out / it['file']}\ncredit: {it['credit']}")
        return

    if not a.query:
        ap.error("give a query, or --get <ref>")
    found = []
    for name in a.sources.split(","):
        try:
            found += SOURCES[name.strip()](a.query, a.n, a.allow_by)
        except Exception as e:
            print(f"# {name}: {e}", file=sys.stderr)
    if a.json:
        print(json.dumps(found, indent=2, ensure_ascii=False))
    else:
        for i, it in enumerate(found):
            size = f"{it['width']}×{it['height']}" if it.get("width") else ""
            print(f"[{i}] {it['ref']}\n     {it['title'][:90]} — {it['creator'][:50]} {it['date'][:20]}\n     {it['licence']} {size}  {it['page']}")
    if a.sheet and found:
        contact_sheet(found, a.sheet)
        print(f"sheet: {a.sheet}", file=sys.stderr if a.json else sys.stdout)


if __name__ == "__main__":
    main()
