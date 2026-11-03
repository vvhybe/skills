"""Print an HTML file to PDF with WeasyPrint, letting it read only the folders it needs.

Usage: render_pdf.py <in.html> <out.pdf> <allowed-dir> [<allowed-dir> ...]

The book's pages come from a repository's Markdown, which may contain raw HTML. WeasyPrint would
otherwise fetch any URL a page names: local files, attachments, the network. This fetcher allows
file:// URLs under the given folders and data: URIs, and refuses everything else.
Works with WeasyPrint 70+ (the URLFetcher class) and with older versions (a fetcher function).
"""
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def allowed_url(url, roots):
    parsed = urlparse(url)
    if parsed.scheme == "data":
        return True
    if parsed.scheme == "file":
        path = Path(unquote(parsed.path)).resolve()
        return any(path.is_relative_to(root) for root in roots)
    return False


def safe_fetcher(allowed):
    roots = [Path(a).resolve() for a in allowed]
    try:
        from weasyprint.urls import URLFetcher  # WeasyPrint 70+

        class GuideFetcher(URLFetcher):
            def fetch(self, url, headers=None):
                if not allowed_url(url, roots):
                    raise ValueError(f"blocked resource outside the guide's folders: {url}")
                return super().fetch(url, headers)

        return GuideFetcher(allowed_protocols=["file", "data"])
    except ImportError:  # older WeasyPrint: a plain function
        from weasyprint import default_url_fetcher

        def fetch(url, *args, **kwargs):
            if not allowed_url(url, roots):
                raise ValueError(f"blocked resource outside the guide's folders: {url}")
            return default_url_fetcher(url, *args, **kwargs)

        return fetch


def render(html_path, pdf_path, allowed):
    from weasyprint import HTML  # imported here so the URL policy above can be tested without WeasyPrint

    html_path = Path(html_path).resolve()
    HTML(filename=str(html_path), base_url=str(html_path.parent) + "/",
         url_fetcher=safe_fetcher([html_path.parent, *allowed])).write_pdf(str(pdf_path))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    render(sys.argv[1], sys.argv[2], sys.argv[3:])
