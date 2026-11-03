"""The final enforcement pass over the book (skills/dev-guide/scripts/safe_html.py).
Run: python3 -m unittest discover -s tests -p 'test_*.py'  (needs beautifulsoup4)"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "dev-guide" / "scripts"))
from safe_html import enforce, with_stylesheet  # noqa: E402

ROOTS = ["/work/guide", "/work/skill/assets", "/work/build"]


def run(body, head=""):
    return enforce(f"<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>", ROOTS)


class Enforce(unittest.TestCase):
    def test_keeps_what_a_guide_needs(self):
        out = run('<details><summary>Answer</summary><code>x</code></details>'
                  '<img src="/work/build/diagrams/a.png" alt="d" style="width:120mm">'
                  '<a href="#ch-02">next</a> <a href="https://example.com">web</a>')
        for kept in ("<details>", "<summary>", "<code>x</code>", 'src="/work/build/diagrams/a.png"',
                     'style="width:120mm"', 'href="#ch-02"', 'href="https://example.com"'):
            self.assertIn(kept, out)

    def test_removes_fetching_and_active_tags_with_content(self):
        out = run('<script>steal()</script><link rel="attachment" href="file:///etc/passwd">'
                  '<object data="file:///etc/passwd">x</object><iframe src="file:///etc/passwd"></iframe>'
                  '<svg><image href="file:///etc/passwd"/><use href="file:///etc/passwd#a"/></svg>')
        for gone in ("script", "steal()", "<link", "<object", "<iframe", "<image", "<use", "/etc/passwd"):
            self.assertNotIn(gone, out)

    def test_images_must_stay_inside_the_folders(self):
        out = run('<img src="/etc/passwd" alt="one"><img src="file:///work/guide/../../etc/passwd" alt="two">'
                  '<img src="https://evil.example/x.png" alt="three"><img src="../../etc/passwd" alt="four">')
        self.assertNotIn("<img", out)
        for alt in ("one", "two", "three", "four"):
            self.assertIn(alt, out)

    def test_style_attributes_only_in_the_builds_own_form(self):
        out = run('<p style="background:url(file:///etc/passwd)">a</p>'
                  '<p style="background:u\\72l(/etc/passwd)">b</p>'
                  '<p style="width:120mm; background:url(/etc/passwd)">c</p>'
                  '<img src="/work/build/a.png" style="width:120.5mm">')
        self.assertNotIn("passwd", out)
        self.assertNotIn("u\\72l", out)
        self.assertIn('style="width:120.5mm"', out)

    def test_svg_data_images_are_refused(self):
        out = run('<img src="data:image/svg+xml,<svg><image href=\'file:///etc/passwd\'/></svg>" alt="svg">'
                  '<img src="data:image/png;base64,iVBORw0KGgo=" alt="png">')
        self.assertNotIn("svg+xml", out)
        self.assertIn("data:image/png", out)

    def test_entity_encoded_markup_stays_text(self):
        out = run("<p>&lt;link rel=&quot;attachment&quot; href=&quot;file:///etc/passwd&quot;&gt;</p>")
        self.assertNotIn("<link", out)
        self.assertIn("&lt;link", out)

    def test_no_attachments_and_no_script_links(self):
        out = run('<a rel="attachment" href="https://example.com/x">a</a>'
                  '<a href="javascript:alert(1)">b</a><a href="file:///etc/passwd">c</a><a href="data:text/html,x">d</a>'
                  '<p onclick="x()" onerror="y()">e</p>')
        self.assertNotIn("rel=", out)
        for gone in ("javascript:", "file:///etc", "data:text", "onclick", "onerror"):
            self.assertNotIn(gone, out)

    def test_unknown_tags_are_unwrapped_and_comments_dropped(self):
        out = run("<marquee>hello</marquee><!-- hidden -->")
        self.assertIn("hello", out)
        self.assertNotIn("marquee", out)
        self.assertNotIn("hidden", out)

    def test_every_style_element_is_removed(self):
        out = run("<style>p{background:url(file:///etc/passwd)}</style><p>x</p>",
                  head="<style>@font-face{src:url('/etc/fonts/x.ttf')}</style>")
        self.assertNotIn("<style", out)
        self.assertNotIn("passwd", out)

    def test_nested_head_cannot_carry_a_stylesheet(self):
        out = run("<head><style>p{background:url(file:///etc/passwd)}</style></head><p>x</p>")
        self.assertNotIn("passwd", out)
        self.assertEqual(out.count("<head>"), 1)

    def test_the_books_stylesheet_is_added_after_enforcement(self):
        out = with_stylesheet(run("<p>&lt;/head&gt; stays text</p>"), "body{color:red}")
        self.assertEqual(out.count("<style>"), 1)
        self.assertLess(out.index("<style>"), out.index("<body>"))
        self.assertIn("&lt;/head&gt; stays text", out)


if __name__ == "__main__":
    unittest.main()
