"""Build the printed edition of a repo's developer guide (HTML for WeasyPrint or PrinceXML).

Usage: build_book.py <repo-root> <config.json> <work-dir>

The guide's Markdown pages are the single source. This script:
  1. renders every ```mermaid block to a PNG with mermaid-cli (Inter loaded);
  2. turns each page into HTML with markdown-it, then restyles it with
     BeautifulSoup: callouts, chapter openers, figures, quizzes, stat tiles;
  3. wraps the chapters in the cover (make_cover.py), a table of contents and part dividers;
  4. writes book.html and a JSON model the DOCX builder reads.

Run it through build.sh, which sets up Python, FONTCONFIG_FILE and puppeteer.json.
"""

from __future__ import annotations

import hashlib
import html as htmllib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_model import chapter_model  # noqa: E402
from safe_html import enforce, with_stylesheet  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
REPO = Path(sys.argv[1]).resolve()
CFG = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
BUILD = Path(sys.argv[3]).resolve()
GUIDE = (REPO / CFG.get("guide_dir", "docs/guide")).resolve()
if not GUIDE.is_relative_to(REPO):
    sys.exit(f"guide_dir must be inside the repository: {GUIDE}")
FONTS = SKILL / "assets" / "fonts"
DIAGRAMS = BUILD / "diagrams"
DIAGRAMS.mkdir(parents=True, exist_ok=True)

# Part titles go into HTML: escape them there, and keep the raw text for the Word model.
PARTS = [{**p, "n": i + 1, "title_raw": p["title"], "title": htmllib.escape(p["title"]),
          "roman": htmllib.escape(p["roman"])} for i, p in enumerate(CFG["parts"])]
E = {k: htmllib.escape(str(v)) for k, v in CFG.items() if isinstance(v, (str, int, float))}
PART_COLOURS = {
    1: {"main": "#2a78d6", "dark": "#1b5aa6", "tint": "#eaf2fc", "soft": "#dbe9fb", "ink": "#0b2545"},
    2: {"main": "#139a6b", "dark": "#0d7a54", "tint": "#e8f6f0", "soft": "#d9f3e8", "ink": "#08372a"},
    3: {"main": "#eb6834", "dark": "#c24e1f", "tint": "#fdf0ea", "soft": "#fde3d7", "ink": "#4a1a06"},
    4: {"main": "#4a3aa7", "dark": "#372a85", "tint": "#f0eefa", "soft": "#e6e3f7", "ink": "#1d1640"},
}
CALLOUTS = {
    "NOTE": ("note", "Note"),
    "TIP": ("tip", "Tip"),
    "IMPORTANT": ("why", "Why?"),
    "WARNING": ("warn", "Watch out"),
    "CAUTION": ("never", "Never"),
}
LANG_ALIASES = {"jinja": "html+jinja", "jsonc": "json", "text": None, "": None, "bash": "bash",
                "html": "html+jinja", "css": "css", "json": "json", "js": "js"}
LANG_LABEL = {"jinja": "Jinja", "jsonc": "JSON", "json": "JSON", "bash": "Shell", "html": "HTML",
              "css": "CSS", "text": "", "js": "JavaScript"}

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


# --- Mermaid ----------------------------------------------------------------------

def render_mermaid(source: str) -> Path:
    """Render one diagram to PNG (cached by content hash)."""
    key = hashlib.sha1(source.encode()).hexdigest()[:12]
    png = DIAGRAMS / f"{key}.png"
    if png.exists():
        return png
    mmd = DIAGRAMS / f"{key}.mmd"
    mmd.write_text(source, encoding="utf-8")
    cmd = ["mmdc", "-p", str(BUILD / "puppeteer.json"), "-c", str(SKILL / "assets" / "mermaid-print.json"),
           "-i", str(mmd), "-o", str(png), "-s", "3", "-w", "1400", "-b", "white", "-q"]
    subprocess.run(cmd, check=True, timeout=180, env=os.environ)
    return png


def png_size(path: Path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


# --- Markdown → HTML ----------------------------------------------------------------

FIG_LIMIT_W, FIG_LIMIT_H = 168.0, 150.0   # mm


def fig_width_mm(px_w: int, px_h: int, scale: int = 3, shrink: float = 0.7) -> float:
    """Printed width: natural size shrunk to body-text scale, capped by the text block."""
    natural = px_w / scale * 0.2646 * shrink
    by_height = FIG_LIMIT_H * px_w / px_h
    return round(min(natural, FIG_LIMIT_W, by_height), 1)


def code_html(src: str, lang: str) -> str:
    lexer_name = LANG_ALIASES.get(lang, lang)
    label = LANG_LABEL.get(lang, lang.upper())
    body = None
    if lexer_name:
        try:
            lexer = get_lexer_by_name(lexer_name)
            body = highlight(src, lexer, HtmlFormatter(nowrap=True))
        except ClassNotFound:
            body = None
    if body is None:
        from html import escape
        body = escape(src)
    tag = f'<span class="lang">{label}</span>' if label else ""
    return f'<pre class="code lang-{lang or "text"}">{tag}<code>{body.rstrip()}</code></pre>\n'


def fence_rule(self, tokens, idx, options, env):
    tok = tokens[idx]
    lang = (tok.info or "").strip().split(" ")[0]
    if lang == "mermaid":
        png = render_mermaid(tok.content)
        w, h = png_size(png)
        env.setdefault("diagrams", []).append(str(png))
        return (f'<figure class="fig diagram"><img src="{png}" data-px="{w}x{h}" '
                f'style="width:{fig_width_mm(w, h)}mm"/></figure>\n')
    return code_html(tok.content, lang)


md.add_render_rule("fence", fence_rule)


def slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s]+", "-", s)


def load_page(stem: str) -> tuple[str, str]:
    path = next(GUIDE.glob(f"{stem}*.md")) if stem != "glossary" else GUIDE / "glossary.md"
    text = path.read_text(encoding="utf-8")
    text = text.split("<!-- nav -->")[0]
    text = re.sub(r"^\[Home\]\(README\.md\) › [^\n]*\n", "", text, flags=re.M)
    text = text.replace("<!-- -->\n", "")
    return path.name, text


def rewrite_links(soup: BeautifulSoup) -> None:
    for a in soup.find_all("a"):
        href = a.get("href", "")
        m = re.match(r"^(\d\d)-[\w-]+\.md(#.*)?$", href)
        if m:
            a["href"] = f"#ch-{m.group(1)}"
            a["class"] = ["xref"]
        elif href.startswith("glossary.md"):
            frag = href.split("#", 1)[1] if "#" in href else ""
            a["href"] = f"#gl-{frag}" if frag else "#glossary"
            a["class"] = ["xref", "gloss"]
        elif href == "README.md":
            a["href"] = "#about"
            a["class"] = ["xref"]
        elif href.startswith(("http", "mailto")):
            a["class"] = ["ext"]
        else:
            # repo files, other docs, relative downloads: plain text in print
            a.unwrap()


ICONS = {
    "note": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/><rect x="11" y="10" width="2" height="7" rx="1" fill="#fff"/><circle cx="12" cy="7.2" r="1.3" fill="#fff"/></svg>',
    "tip": '<svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-4 12.7V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.3A7 7 0 0 0 12 2z" fill="currentColor"/><rect x="9" y="19.2" width="6" height="2.3" rx="1" fill="currentColor"/></svg>',
    "why": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M9.3 9.2a2.8 2.8 0 1 1 3.9 2.6c-.8.4-1.2.9-1.2 1.8v.6" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/><circle cx="12" cy="17.3" r="1.3" fill="#fff"/></svg>',
    "warn": '<svg viewBox="0 0 24 24"><path d="M12 2.5 1.8 20.5h20.4z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><rect x="11" y="8.5" width="2" height="6.5" rx="1" fill="#fff"/><circle cx="12" cy="17.6" r="1.2" fill="#fff"/></svg>',
    "never": '<svg viewBox="0 0 24 24"><path d="M7.9 2h8.2L22 7.9v8.2L16.1 22H7.9L2 16.1V7.9z" fill="currentColor"/><rect x="6.5" y="10.8" width="11" height="2.4" rx="1.2" fill="#fff"/></svg>',
    "goal": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="5.5" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="1.8" fill="currentColor"/></svg>',
    "quiz": '<svg viewBox="0 0 24 24"><path d="M4 20l1.2-4.6L16.3 4.3a2 2 0 0 1 2.8 0l.6.6a2 2 0 0 1 0 2.8L8.6 18.8z" fill="currentColor"/><path d="M4 20l4.6-1.2" stroke="currentColor" stroke-width="2"/></svg>',
}


def transform_callouts(soup: BeautifulSoup) -> Tag | None:
    """Turn GitHub alert blockquotes into styled boxes; return the 'In this chapter' box."""
    objectives = None
    for bq in soup.find_all("blockquote"):
        first = bq.find("p")
        if not first or not first.contents:
            continue
        head = first.contents[0]
        if not isinstance(head, NavigableString):
            continue
        m = re.match(r"\s*\[!(\w+)\]\s*", str(head))
        if not m or m.group(1) not in CALLOUTS:
            continue
        kind, default_title = CALLOUTS[m.group(1)]
        rest = str(head)[m.end():]
        head.replace_with(rest)
        title = default_title
        # a leading <strong> is the box's own title
        nodes = [n for n in first.contents if not (isinstance(n, NavigableString) and not n.strip())]
        if nodes and isinstance(nodes[0], Tag) and nodes[0].name == "strong":
            title = nodes[0].get_text().rstrip(".:")
            nodes[0].extract()
            # strip the whitespace/punctuation left behind
            while first.contents and isinstance(first.contents[0], NavigableString) and not first.contents[0].strip():
                first.contents[0].extract()
            if first.contents and isinstance(first.contents[0], NavigableString):
                first.contents[0].replace_with(str(first.contents[0]).lstrip())
        if not first.get_text(strip=True) and not first.find(True):
            first.decompose()
        box = soup.new_tag("div", attrs={"class": f"callout {kind}"})
        if title.lower() == "in this chapter":
            box["class"] = "objectives"
            kind = "goal"
        label = soup.new_tag("div", attrs={"class": "callout-title"})
        label.append(BeautifulSoup(f'<span class="ico">{ICONS[kind]}</span>', "html.parser"))
        label.append(title)
        body = soup.new_tag("div", attrs={"class": "callout-body"})
        for child in list(bq.children):
            body.append(child.extract())
        box.append(label)
        box.append(body)
        bq.replace_with(box)
        if box.get("class") == "objectives":
            objectives = box
    return objectives


def transform_tasks(soup: BeautifulSoup) -> None:
    for li in soup.find_all("li"):
        text = li.find(string=True)
        if text and re.match(r"^\[[ x]\] ", str(text)):
            li["class"] = ["task"]
            text.replace_with(str(text)[4:])
            li.insert(0, BeautifulSoup('<span class="box"></span>', "html.parser"))


def transform_stats(soup: BeautifulSoup) -> None:
    for comment in soup.find_all(string=lambda s: isinstance(s, NavigableString) and "stats" in s and s.__class__.__name__ == "Comment"):
        table = comment.find_next("table")
        if not table:
            continue
        numbers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        labels = [td.get_text(strip=True) for td in table.find("tbody").find_all("td")]
        wrap = soup.new_tag("div", attrs={"class": "stats"})
        for i, (n, l) in enumerate(zip(numbers, labels)):
            wrap.append(BeautifulSoup(f'<div class="stat tile-{i % 5}"><div class="n">{htmllib.escape(n)}</div><div class="l">{htmllib.escape(l)}</div></div>', "html.parser"))
        table.replace_with(wrap)
        comment.extract()


def transform_figures(soup: BeautifulSoup, ch_label: str) -> list:
    """Attach 'Figure: …' captions to the diagram or image before them; number them."""
    figures = []
    for p in soup.find_all("p"):
        em = p.find("em")
        if not em or p.get_text(strip=True) != em.get_text(strip=True):
            continue
        text = em.get_text(strip=True)
        if not text.startswith("Figure:"):
            continue
        caption = em.decode_contents().split("Figure:", 1)[1].strip()
        caption = caption[0].upper() + caption[1:]
        prev = p.find_previous_sibling()
        fig = None
        if prev is not None and prev.name == "figure":
            fig = prev
        elif prev is not None and prev.name == "p" and prev.find("img") and len(prev.find_all(True)) == 1:
            img = prev.find("img")
            fig = soup.new_tag("figure", attrs={"class": "fig chart"})
            src = img["src"]
            fig.append(soup.new_tag("img", attrs={"src": src, "alt": img.get("alt", ""),
                                                    "style": "width:170mm"}))
            prev.replace_with(fig)
        if fig is None:
            continue
        n = len(figures) + 1
        cap = soup.new_tag("figcaption")
        cap.append(BeautifulSoup(f'<span class="fignum">Figure {ch_label}.{n}</span> {caption}', "html.parser"))
        fig.append(cap)
        figures.append((f"{ch_label}.{n}", caption, fig))
        p.decompose()
    return figures


def transform_quiz(soup: BeautifulSoup) -> None:
    h2 = next((h for h in soup.find_all("h2") if h.get_text(strip=True) == "Check yourself"), None)
    if not h2:
        return
    quiz = soup.new_tag("div", attrs={"class": "quiz"})
    title = soup.new_tag("div", attrs={"class": "quiz-title"})
    title.append(BeautifulSoup(f'<span class="ico">{ICONS["quiz"]}</span>Check yourself', "html.parser"))
    quiz.append(title)
    nodes = []
    sib = h2.next_sibling
    while sib is not None:
        nxt = sib.next_sibling
        nodes.append(sib.extract())
        sib = nxt
    h2.replace_with(quiz)
    for node in nodes:
        if isinstance(node, Tag) and node.name == "details":
            summary = node.find("summary")
            if summary:
                summary.decompose()
            ans = soup.new_tag("div", attrs={"class": "answer"})
            ans.append(BeautifulSoup('<span class="a-label">Answer</span> ', "html.parser"))
            for c in list(node.children):
                ans.append(c.extract())
            quiz.append(ans)
        elif isinstance(node, Tag):
            if node.name == "p":
                node["class"] = ["question"]
            quiz.append(node)


def details_fix(html: str) -> str:
    """markdown-it passes <details> through as raw HTML blocks; normalise them."""
    return html


def css_string(text: str) -> str:
    """A value safe inside a CSS double-quoted string (and inside a <style> element)."""
    return (str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
            .replace("<", "\\3C ").replace(">", "\\3E "))


def check_images(soup: BeautifulSoup, page: str) -> None:
    """Images may only come from the guide folder, or from the work dir where diagrams are rendered."""
    for img in soup.find_all("img"):
        src = str(img.get("src", ""))
        target = None
        if src and ":" not in src:
            target = Path(src).resolve() if src.startswith("/") else (GUIDE / src).resolve()
        allowed = target is not None and (target.is_relative_to(GUIDE) or target.is_relative_to(BUILD))
        if not allowed or not target.is_file():
            print(f"warning: {page}: dropped image outside the guide folder: {src}", file=sys.stderr)
            img.replace_with(img.get("alt", ""))
        else:
            img["src"] = str(target)


def page_html(stem: str) -> tuple[BeautifulSoup, dict]:
    name, text = load_page(stem)
    env = {}
    html = md.render(text, env)
    soup = BeautifulSoup(html, "html.parser")
    # the printed editions do not advertise themselves (the note may carry the cover thumbnail)
    for bq in soup.find_all("blockquote"):
        if "Printable editions" in bq.get_text():
            bq.decompose()
    check_images(soup, name)
    info = {"file": name, "diagrams": env.get("diagrams", [])}
    h1 = soup.find("h1")
    info["h1"] = " ".join(h1.get_text().split()) if h1 else ""
    return soup, info


# --- Chapters -----------------------------------------------------------------------

def descriptions() -> dict:
    """One-line chapter descriptions, read from the README's contents tables."""
    text = (GUIDE / "README.md").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\| \[(?:(\d+) · )?([^\]]+)\]\(([^)]+)\) \| ([^|]+) \|$", text, re.M):
        stem = m.group(3).split("-")[0].replace(".md", "")
        out[stem] = m.group(4).strip()
    return out


def build_chapter(stem: str, part: dict) -> tuple[str, dict]:
    soup, info = page_html(stem)
    is_gloss = stem == "glossary"
    h1 = soup.find("h1")
    full = " ".join(h1.get_text().split())
    if is_gloss:
        num, title = "", "Glossary"
        ch_id, ch_label = "glossary", "G"
    else:
        num, title = full.split(" · ", 1)
        ch_id, ch_label = f"ch-{int(num):02d}", str(int(num))
    h1.decompose()

    rewrite_links(soup)
    objectives = transform_callouts(soup)
    if objectives:
        objectives.extract()
    transform_tasks(soup)
    transform_stats(soup)
    figures = transform_figures(soup, ch_label)
    transform_quiz(soup)

    # lead paragraph: the first paragraph of the body
    lead = soup.find("p", recursive=False)
    lead_html = ""
    if lead is not None and not lead.find("img"):
        lead_html = f'<p class="lead">{lead.decode_contents()}</p>'
        lead.decompose()

    for h2 in soup.find_all("h2"):
        hid = ("gl-" if is_gloss else f"{ch_id}-") + slug(h2.get_text())
        h2["id"] = hid

    c = PART_COLOURS[part["n"]]
    opener = f'''
<header class="opener">
  <div class="kicker">Part {part["roman"]} · {part["title"]}</div>
  <div class="numrow">{f'<span class="num">{int(num):02d}</span>' if num else '<span class="num gl">A–Z</span>'}</div>
  <h1 data-running="{htmllib.escape(title)}" data-part="Part {part["roman"]} · {part["title"]}">{htmllib.escape(title)}</h1>
  {lead_html}
</header>'''
    obj_html = str(objectives) if objectives else ""
    cls = f"chapter part{part['n']}" + (" glossary" if is_gloss else "")
    section = (f'<section class="{cls}" id="{ch_id}" data-part="Part {part["roman"]} · {part["title"]}">'
               f'{opener}{obj_html}<div class="body">{soup.decode()}</div></section>\n')
    info.update({"id": ch_id, "num": num, "title": title, "part": part["n"], "figures": [f[:2] for f in figures],
                 "html": section})
    return section, info


def build_about() -> str:
    soup, _ = page_html("README")
    soup.find("h1").decompose()
    # the printed book has its own table of contents
    h2 = next(h for h in soup.find_all("h2") if h.get_text(strip=True) == "Contents")
    node = h2
    while node is not None:
        nxt = node.next_sibling
        if isinstance(node, Tag) and node.name == "h2" and node is not h2:
            break
        node.extract()
        node = nxt
    rewrite_links(soup)
    transform_callouts(soup)
    transform_stats(soup)
    figs = transform_figures(soup, "0")
    lead = soup.find("p", recursive=False)
    lead_html = f'<p class="lead">{lead.decode_contents()}</p>' if lead else ""
    if lead:
        lead.decompose()
    # the reading-path table: chapter numbers become cross-references with pages
    return (f'<section class="front about" id="about"><header class="opener">'
            f'<div class="kicker">Before you start</div><h1 data-running="About this guide">About this guide</h1>'
            f'{lead_html}</header><div class="body">{soup.decode()}</div></section>\n')


def part_divider(part: dict, chapters: list, desc: dict) -> str:
    items = []
    for ch in chapters:
        key = ch["num"] and f'{int(ch["num"]):02d}' or "glossary"
        d = desc.get(key, desc.get(ch["num"], ""))
        label = f'{int(ch["num"]):02d}' if ch["num"] else "A–Z"
        items.append(f'<li><a href="#{ch["id"]}"><span class="pn">{label}</span>'
                     f'<span class="pt">{htmllib.escape(ch["title"])}</span><span class="pd">{htmllib.escape(d)}</span></a></li>')
    return (f'<section class="divider div{part["n"]}" id="part-{part["n"]}">'
            f'<div class="roman">{part["roman"]}</div><div class="plabel">Part {part["roman"]}</div>'
            f'<h1 class="ptitle">{part["title"]}</h1><ol class="pchapters">{"".join(items)}</ol></section>\n')


def toc(all_parts: list) -> str:
    rows = ['<li class="toc-front"><a href="#about"><span class="t">About this guide</span></a></li>']
    for part, chapters in all_parts:
        rows.append(f'<li class="toc-part p{part["n"]}"><a href="#part-{part["n"]}">'
                    f'<span class="pr">Part {part["roman"]}</span><span class="t">{part["title"]}</span></a></li>')
        for ch in chapters:
            label = f'{int(ch["num"])}' if ch["num"] else "A–Z"
            rows.append(f'<li class="toc-ch p{part["n"]}"><a href="#{ch["id"]}"><span class="cn">{label}</span>'
                        f'<span class="t">{htmllib.escape(ch["title"])}</span></a></li>')
    return (f'<section class="toc" id="toc"><h1 data-running="Contents">Contents</h1>'
            f'<ol class="toc-list">{"".join(rows)}</ol></section>\n')


def cover() -> str:
    """The cover page, written by make_cover.py."""
    return (BUILD / "cover.html").read_text(encoding="utf-8")


def back_cover() -> str:
    """The back cover with the colophon and the plate's credit, written by make_cover.py."""
    return (BUILD / "back.html").read_text(encoding="utf-8")


def main():
    desc = descriptions()
    all_parts = []
    chapters_html = []
    model = {"parts": [], "meta": CFG, "fonts_dir": str(FONTS)}
    for part in PARTS:
        chs = []
        for stem in part["files"]:
            html, info = build_chapter(stem, part)
            chs.append(info)
        all_parts.append((part, chs))
    about_html = build_about()
    body = [cover(), toc(all_parts), about_html]
    model["about"] = chapter_model(about_html)
    for part, chs in all_parts:
        body.append(part_divider(part, chs, desc))
        for ch in chs:
            body.append(ch["html"])
        model["parts"].append({"n": part["n"], "roman": part["roman"], "title": part["title_raw"],
                               "chapters": [{**{k: v for k, v in ch.items() if k != "html"}, **chapter_model(ch["html"]),
                                             "desc": desc.get(f'{int(ch["num"]):02d}' if ch["num"] else "glossary", "")}
                                            for ch in chs]})
    body.append(back_cover())

    css = (SKILL / "assets" / "book.css").read_text(encoding="utf-8")  # noqa: the book's own stylesheet
    # Where a named page's background image is anchored. Prince paints it over the whole sheet;
    # WeasyPrint anchors it to the content box, which would push the part tab off the right
    # edge, so it is shifted back by the page's left and top margins.
    tabpos = "0 0" if os.environ.get("ENGINE", "weasyprint") == "prince" else "-20mm -24mm"
    css = (css.replace("{{FONTS}}", str(FONTS)).replace("{{BUILD}}", str(BUILD))
              .replace("{{TABPOS}}", tabpos)
              .replace("{{FOOTER}}", css_string(CFG.get("footer", f'{CFG["title"]} · {CFG.get("subtitle", "Developer Guide")}'))))
    pyg = HtmlFormatter(style="friendly").get_style_defs(".code code")
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{E["title"]} — {E.get("subtitle", "Developer Guide")}</title>
<meta name="author" content="{E.get("author", "")}">
<meta name="subject" content="{E["tagline"]}">
</head><body>
{"".join(body)}
</body></html>'''
    # One parser-based pass over the finished book: an allowlist of tags and attributes, and every
    # URL checked against the folders the book may read. The engine then parses exactly this tree.
    html = enforce(html, [GUIDE, SKILL / "assets", BUILD])
    html = with_stylesheet(html, f"{css}\n{pyg}")      # the book's own stylesheet, added after the checks
    (BUILD / "book.html").write_text(html, encoding="utf-8")
    (BUILD / "model.json").write_text(json.dumps(model, indent=1), encoding="utf-8")
    print("chapters:", sum(len(c) for _, c in all_parts), "diagrams:", len(list(DIAGRAMS.glob("*.png"))))


if __name__ == "__main__":
    main()
