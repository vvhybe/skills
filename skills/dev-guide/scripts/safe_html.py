"""The book's last line of defence: one parser-based pass over the finished HTML.

A guide's pages may come from a repository you don't control, and their raw HTML reaches the book.
Before the PDF engine sees anything, enforce() parses the whole book once and:

  - keeps only an allowlist of tags (unknown tags are unwrapped, dangerous ones removed with their
    content) and an allowlist of attributes;
  - checks every URL that a PDF engine could fetch (img src) against the folders the book may read,
    and allows raster data: images only;
  - removes every <style> element and allows style attributes only in the one form the build
    writes (width in mm), so no CSS from a page is ever parsed; the book's own stylesheet is added
    after enforcement (with_stylesheet), never trusted because of where it sits;
  - keeps link targets that a reader clicks (a href) only for #anchors, http(s) and mailto;
  - drops rel= everywhere, so no link can become an embedded attachment.

It returns the re-serialized tree, so the engine parses exactly what was checked.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Comment

ALLOWED_TAGS = {
    "html", "head", "body", "title", "meta",
    "section", "header", "footer", "main", "article", "aside", "nav", "div", "span", "p", "a", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd", "blockquote",
    "pre", "code", "kbd", "samp", "var", "em", "strong", "b", "i", "u", "s", "del", "ins", "sub", "sup",
    "small", "mark", "abbr", "q", "figure", "figcaption", "img",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "colgroup", "col", "details", "summary",
    # inline SVG icons drawn by the build
    "svg", "g", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "text", "tspan", "defs",
}
REMOVE_WITH_CONTENT = {
    "script", "style", "link", "object", "embed", "iframe", "frame", "frameset", "base", "form", "input", "button",
    "textarea", "select", "option", "audio", "video", "source", "track", "image", "use", "foreignobject",
    "math", "applet", "param", "noscript", "template", "canvas", "picture", "portal", "svg:image",
}
ALLOWED_ATTRS = {
    "alt", "class", "id", "title", "lang", "dir", "colspan", "rowspan", "width", "height", "start", "type",
    "open", "href", "src", "style", "charset", "name", "content", "xmlns",
    # SVG geometry and paint
    "viewbox", "d", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "stroke-dasharray",
    "cx", "cy", "r", "rx", "ry", "x", "y", "x1", "y1", "x2", "y2", "points", "transform", "opacity",
    "fill-opacity", "stroke-opacity", "fill-rule", "clip-rule", "font-family", "font-size", "font-weight",
    "text-anchor", "dominant-baseline", "letter-spacing",
}
STYLE_ATTR = re.compile(r"^\s*width:\s*\d+(\.\d+)?mm\s*;?\s*$")   # what the build writes on figures
RASTER_DATA = re.compile(r"^data:image/(png|jpe?g|gif|webp)[;,]", re.I)


def _inside(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(root) for root in roots)


def fetchable_ok(url: str, roots: list[Path], base: Path) -> bool:
    """May the PDF engine fetch this URL? data: images, and files inside the roots."""
    url = url.strip()
    if not url:
        return False
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme == "data":
        return bool(RASTER_DATA.match(url))            # never data:image/svg+xml: it can carry references
    if scheme == "file":
        return _inside(Path(unquote(parsed.path)), roots)
    if scheme:
        return False                                   # http, https, ftp, javascript, …: never fetched
    path = Path(unquote(parsed.path))
    return _inside(path if path.is_absolute() else base / path, roots)


def link_ok(url: str) -> bool:
    """A link the reader may click: an anchor in the book, the web, or email."""
    url = url.strip()
    scheme = urlparse(url).scheme.lower()
    return url.startswith("#") or scheme in ("http", "https", "mailto")


def enforce(html: str, roots, base: Path | None = None) -> str:
    roots = [Path(r).resolve() for r in roots]
    base = (base or roots[-1]).resolve()                # relative URLs resolve against the book's folder
    soup = BeautifulSoup(html, "html.parser")
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()
    # html, head and body only at the top of the document; anywhere else they're unwrapped
    top = soup.find("html")
    keep = {id(top), id(top.find("head", recursive=False)), id(top.find("body", recursive=False))} if top else set()
    for tag in soup.find_all(["html", "head", "body"]):
        if id(tag) not in keep:
            tag.unwrap()
    for tag in soup.find_all(True):
        if tag.decomposed:
            continue
        name = tag.name.lower()
        if name in REMOVE_WITH_CONTENT:
            tag.decompose()
            continue
        if name not in ALLOWED_TAGS:
            tag.unwrap()
            continue
        if name == "meta" and (tag.get("http-equiv") or "url" in str(tag.get("content", "")).lower()):
            tag.decompose()
            continue
        for attr in list(tag.attrs):
            key = attr.lower()
            value = tag.attrs[attr]
            value = " ".join(value) if isinstance(value, list) else str(value)
            keep = key in ALLOWED_ATTRS or (key.startswith("data-") and key != "data")
            if keep and key == "href":
                keep = name == "a" and link_ok(value)
            if keep and key == "src":
                keep = name == "img" and fetchable_ok(value, roots, base)
            if keep and key == "style":
                keep = bool(STYLE_ATTR.match(value))
            if not keep:
                del tag.attrs[attr]
        if name == "img" and not tag.get("src"):
            tag.replace_with(tag.get("alt", ""))
    return str(soup)


def with_stylesheet(html: str, css: str) -> str:
    """Add the book's own stylesheet after enforcement. enforce() guarantees the only </head> left
    is the document's own (nested heads are unwrapped, and page text is escaped)."""
    if "</head>" not in html:
        raise ValueError("the book has no <head>")
    return html.replace("</head>", f"<style>{css}</style></head>", 1)
