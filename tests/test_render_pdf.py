"""The PDF renderer's URL policy: only data: URIs and files under the allowed folders.
Run: python3 -m unittest discover -s tests -p 'test_*.py'  (no WeasyPrint needed)"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "dev-guide" / "scripts"))
from render_pdf import allowed_url  # noqa: E402

ROOTS = [Path("/work/guide").resolve(), Path("/work/build").resolve()]


class AllowedUrl(unittest.TestCase):
    def test_files_inside_the_allowed_folders(self):
        self.assertTrue(allowed_url("file:///work/guide/assets/chart.svg", ROOTS))
        self.assertTrue(allowed_url("file:///work/build/diagrams/a.png", ROOTS))

    def test_data_uris(self):
        self.assertTrue(allowed_url("data:image/png;base64,iVBORw0KGgo=", ROOTS))

    def test_files_outside_are_refused(self):
        self.assertFalse(allowed_url("file:///etc/passwd", ROOTS))
        self.assertFalse(allowed_url("file:///work/guide/../secret.txt", ROOTS))
        self.assertFalse(allowed_url("file:///work/guide%2F..%2Fsecret.txt", ROOTS))
        self.assertFalse(allowed_url("file:///work/guidebook/x.png", ROOTS))

    def test_network_is_refused(self):
        for url in ("https://example.com/x.png", "http://169.254.169.254/latest/meta-data", "ftp://x/y"):
            self.assertFalse(allowed_url(url, ROOTS), url)


if __name__ == "__main__":
    unittest.main()
