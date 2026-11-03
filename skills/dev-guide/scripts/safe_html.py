"""The book's last line of defence: one parser-based pass over the finished HTML.

A guide's pages may come from a repository you don't control, and their raw HTML reaches the book.
Before the PDF engine sees anything, enforce() parses the whole book once and:

  - keeps only an allowlist of tags (unknown tags are unwrapped, dangerous ones removed with their
    content) and an allowlist of attributes;
  - checks every URL that a PDF engine could fetch (img src, CSS url() in style attributes and
    <style> elements) against the folders the book may read, and data: images;
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
    "html", "head", "body", "title", "meta", "style",
    "section", "header", "footer", "main", "article", "aside", "nav", "div", "span", "p", "a", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd", "blockquote",
    "pre", "code", "kbd", "samp", "var", "em", "strong", "b", "i", "u", "s", "del", "ins", "sub", "sup",
    "small", "mark", "abbr", "q", "figure", "figcaption", "img",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "colgroup", "col", "details", "summary",
    # inline SVG icons drawn by the build
    "svg", "g", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "text", "tspan", "defs",
}
REMOVE_WITH_CONTENT = {
    "script", "link", "object", "embed", "iframe", "frame", "frameset", "base", "form", "input", "button",
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
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)


class UnsafeBook(Exception):
    """The build's own stylesheet points somewhere the book may not read: a bug, not an attack."""


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
        return url[5:].lstrip().lower().startswith("image/") or url[5:].lstrip().lower().startswith("font/")
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


def css_ok(css: str, roots: list[Path], base: Path) -> bool:
    if re.search(r"@import|expression\s*\(", css, re.I):
        return False
    return all(fetchable_ok(m.group(2), roots, base) for m in CSS_URL.finditer(css))


def enforce(html: str, roots, base: Path | None = None) -> str:
    roots = [Path(r).resolve() for r in roots]
    base = (base or roots[-1]).resolve()                # relative URLs resolve against the book's folder
    soup = BeautifulSoup(html, "html.parser")
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()
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
        if name == "style":
            if tag.find_parent("head") is None:
                tag.decompose()                         # only the book's own stylesheet, in <head>
                continue
            if not css_ok(tag.get_text(), roots, base):
                raise UnsafeBook("the book's stylesheet references a file outside the allowed folders")
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
                keep = css_ok(value, roots, base)
            if not keep:
                del tag.attrs[attr]
        if name == "img" and not tag.get("src"):
            tag.replace_with(tag.get("alt", ""))
    return str(soup)
