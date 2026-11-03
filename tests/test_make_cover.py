"""Regression tests for skills/dev-guide/scripts/make_cover.py. Run: python3 -m unittest discover tests

Only Pillow is needed: the tests stop before the PDF preview, which needs WeasyPrint.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "dev-guide" / "scripts" / "make_cover.py"
PAPER = (251, 250, 247)


def config(tmp: Path, **cover):
    cfg = {
        "repo_name": "acme-api", "title": "Acme API", "subtitle": "Developer Guide", "org": "Acme",
        "tagline": "What happens to a request.", "edition": "Edition 1", "as_of": "1 March 2027",
        "cover": {"series": "Acme developer guides", "volume": "Volume I", "colour": "#1F3A5F", **cover},
    }
    path = tmp / "print.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def yellowed_scan(path: Path):
    """An 'engraving': dark line work on yellowed, uneven paper, like an old book scan."""
    im = Image.new("RGB", (900, 1200), (226, 214, 180))
    d = ImageDraw.Draw(im)
    for i in range(0, 900, 6):
        d.point((i, (i * 7) % 1200), fill=(214, 202, 168))   # paper noise
    for x in range(200, 700, 14):
        d.line([(x, 250), (x + 60, 950)], fill=(35, 30, 25), width=3)
    im.save(path)


def run(cfg: Path, work: Path, repo: Path):
    return subprocess.run([sys.executable, str(SCRIPT), str(cfg), str(work), str(repo)], capture_output=True, text=True)


class MakeCover(unittest.TestCase):
    def test_plate_cover_cleans_the_paper_and_credits_the_plate(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            yellowed_scan(tmp / "plate.png")
            (tmp / "plate.json").write_text(json.dumps({"credit": "A press. Engraving, 1819. Public domain."}))
            cfg = config(tmp, style="plate", plate={"file": "plate.png", "caption": "A common press, 1819."})
            result = run(cfg, tmp / "work", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            cover = (tmp / "work" / "cover.html").read_text(encoding="utf-8")
            self.assertIn("Acme API", cover)
            self.assertIn("Volume I", cover)
            self.assertIn('class="plate tall"', cover)
            self.assertIn("A common press, 1819.", cover)
            back = (tmp / "work" / "back.html").read_text(encoding="utf-8")
            self.assertIn("Cover: A press. Engraving, 1819. Public domain.", back)
            plate = Image.open(tmp / "work" / "cover-plate.png").convert("RGB")
            # the yellowed paper prints as the cover's own paper, and the ink stays dark
            self.assertEqual(plate.getpixel((10, 10)), PAPER)
            self.assertLess(plate.convert("L").getextrema()[0], 40)

    def test_plate_without_a_credit_fails(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            yellowed_scan(tmp / "plate.png")
            cfg = config(tmp, style="plate", plate={"file": "plate.png"})
            result = run(cfg, tmp / "work", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no credit", result.stderr)

    def test_type_style_needs_no_plate(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            cfg = config(tmp, style="type", mark="A")
            result = run(cfg, tmp / "work", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            cover = (tmp / "work" / "cover.html").read_text(encoding="utf-8")
            self.assertIn('class="type-mark"', cover)
            self.assertNotIn("Cover:", (tmp / "work" / "back.html").read_text(encoding="utf-8"))

    def test_text_is_escaped(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            cfg = config(tmp, style="type")
            data = json.loads(cfg.read_text())
            data["tagline"] = "Tags like <script> stay text & so do ampersands."
            cfg.write_text(json.dumps(data))
            self.assertEqual(run(cfg, tmp / "work", tmp).returncode, 0)
            cover = (tmp / "work" / "cover.html").read_text(encoding="utf-8")
            self.assertIn("&lt;script&gt;", cover)
            self.assertNotIn("<script>", cover)


if __name__ == "__main__":
    unittest.main()
