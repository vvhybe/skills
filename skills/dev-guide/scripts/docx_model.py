"""Turn the processed chapter HTML into a JSON block model for the DOCX builder."""

from __future__ import annotations

import re
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from pygments.token import STANDARD_TYPES

_STYLE = get_style_by_name("friendly")
CLASS_COLOUR = {}
for ttype, cls in STANDARD_TYPES.items():
    if not cls:
        continue
    t = ttype
    while t is not None:
        spec = _STYLE.style_for_token(t)
        if spec.get("color"):
            CLASS_COLOUR[cls] = {"color": spec["color"], "b": bool(spec.get("bold")), "i": bool(spec.get("italic"))}
            break
        t = t.parent

INLINE = {"strong", "b", "em", "i", "code", "a", "span", "br", "sup", "sub", "s", "del", "u", "small"}


def runs(node, style=None, out=None):
    style = dict(style or {})
    out = [] if out is None else out
    if isinstance(node, Comment):
        return out
    if isinstance(node, NavigableString):
        text = re.sub(r"\s+", " ", str(node))
        if text:
            out.append({**style, "text": text})
        return out
    if not isinstance(node, Tag):
        return out
    name = node.name
    cls = node.get("class") or []
    if name == "span" and "ico" in cls:
        return out
    if name == "br":
        out.append({"br": True})
        return out
    if name in ("strong", "b"):
        style["b"] = True
    elif name in ("em", "i"):
        style["i"] = True
    elif name == "code":
        style["code"] = True
    elif name == "a":
        href = node.get("href", "")
        if href:
            style["link"] = href
    for child in node.children:
        runs(child, style, out)
    return out


def tidy(rs):
    """Trim leading/trailing spaces of a paragraph's runs and merge neighbours."""
    rs = [r for r in rs if r.get("br") or r.get("text")]
    if rs and rs[0].get("text"):
        rs[0]["text"] = rs[0]["text"].lstrip()
    if rs and rs[-1].get("text"):
        rs[-1]["text"] = rs[-1]["text"].rstrip()
    merged = []
    for r in rs:
        if merged and not r.get("br") and not merged[-1].get("br") and \
                {k: v for k, v in r.items() if k != "text"} == {k: v for k, v in merged[-1].items() if k != "text"}:
            merged[-1]["text"] += r["text"]
        else:
            merged.append(dict(r))
    return [r for r in merged if r.get("br") or r.get("text")]


def code_runs(code: Tag):
    out = []
    for node in code.descendants:
        if isinstance(node, NavigableString):
            parent = node.parent
            cls = (parent.get("class") or [None])[0] if parent is not code else None
            style = CLASS_COLOUR.get(cls, {}) if cls else {}
            out.append({"text": str(node), **style})
    return out


def list_block(el: Tag):
    items = []
    for li in el.find_all("li", recursive=False):
        inline, children = [], []
        task = "task" in (li.get("class") or [])
        for c in li.children:
            if isinstance(c, Tag) and c.name in ("ul", "ol"):
                children.append(list_block(c))
            elif isinstance(c, Tag) and c.name == "p":
                if inline:
                    children.append({"t": "p", "runs": tidy(runs(c))})
                else:
                    inline = runs(c)
            elif isinstance(c, Tag) and "box" in (c.get("class") or []):
                continue
            else:
                inline += runs(c)
        items.append({"runs": tidy(inline), "children": children, "task": task})
    return {"t": "list", "ordered": el.name == "ol", "items": items}


def blocks(container: Tag):
    out = []
    for el in container.children:
        if isinstance(el, NavigableString):
            if el.strip() and not isinstance(el, Comment):
                out.append({"t": "p", "runs": tidy(runs(el))})
            continue
        if not isinstance(el, Tag):
            continue
        cls = el.get("class") or []
        n = el.name
        if n in ("h2", "h3"):
            out.append({"t": n, "runs": tidy(runs(el)), "id": el.get("id")})
        elif n == "p":
            out.append({"t": "p", "runs": tidy(runs(el)), "cls": " ".join(cls)})
        elif n in ("ul", "ol"):
            out.append(list_block(el))
        elif n == "pre":
            lab = el.find("span", class_="lang")
            code = el.find("code")
            out.append({"t": "code", "lang": lab.get_text() if lab else "", "runs": code_runs(code)})
        elif n == "table":
            head = [tidy(runs(th)) for th in el.select("thead th")]
            rows = [[tidy(runs(td)) for td in tr.find_all("td")] for tr in el.select("tbody tr")]
            out.append({"t": "table", "head": head, "rows": rows})
        elif n == "div" and ("callout" in cls or "objectives" in cls):
            kind = "goal" if "objectives" in cls else [c for c in cls if c != "callout"][0]
            title = el.find(class_="callout-title").get_text(strip=True)
            out.append({"t": "callout", "kind": kind, "title": title, "blocks": blocks(el.find(class_="callout-body"))})
        elif n == "div" and "stats" in cls:
            items = [[s.find(class_="n").get_text(strip=True), s.find(class_="l").get_text(strip=True)] for s in el.find_all(class_="stat")]
            out.append({"t": "stats", "items": items})
        elif n == "div" and "quiz" in cls:
            qa = []
            for c in el.children:
                if isinstance(c, Tag) and "question" in (c.get("class") or []):
                    qa.append({"t": "q", "runs": tidy(runs(c))})
                elif isinstance(c, Tag) and "answer" in (c.get("class") or []):
                    lab = c.find(class_="a-label")
                    if lab:
                        lab.extract()
                    qa.append({"t": "a", "runs": tidy(runs(c))})
            out.append({"t": "quiz", "items": qa})
        elif n == "figure":
            img = el.find("img")
            cap = el.find("figcaption")
            num = cap.find(class_="fignum").get_text(strip=True) if cap else ""
            if cap and cap.find(class_="fignum"):
                cap.find(class_="fignum").extract()
            w_mm = None
            m = re.search(r"width:([\d.]+)mm", img.get("style", ""))
            if m:
                w_mm = float(m.group(1))
            out.append({"t": "figure", "src": img["src"], "w_mm": w_mm, "num": num,
                        "caption": tidy(runs(cap)) if cap else []})
        elif n == "div":
            out.extend(blocks(el))
        elif n == "blockquote":
            out.append({"t": "callout", "kind": "note", "title": "Note", "blocks": blocks(el)})
    return out


def chapter_model(section_html: str):
    soup = BeautifulSoup(section_html, "html.parser")
    sec = soup.find("section")
    opener = sec.find("header", class_="opener")
    lead = opener.find("p", class_="lead")
    obj = sec.find("div", class_="objectives", recursive=False)
    return {
        "kicker": opener.find(class_="kicker").get_text(strip=True),
        "lead": tidy(runs(lead)) if lead else [],
        "objectives": blocks(BeautifulSoup(str(obj), "html.parser")) if obj else [],
        "body": blocks(sec.find("div", class_="body")),
    }
