# Build, verify, ship

## Contents

1. Requirements
2. Building
3. What the build does
4. Verify
5. Ship
6. Safety
7. Gotchas

## 1. Requirements

- **Python 3.10+.** `build.sh` creates its own venv in `~/.cache/dev-guide/venv` with markdown-it-py, BeautifulSoup, Pygments, Pillow and WeasyPrint.
- **Node 18+** and **mermaid-cli** (`npm install -g @mermaid-js/mermaid-cli`) for diagrams. It needs a headless Chrome; `build.sh` uses Playwright's if present.
- **poppler-utils** (`pdftoppm`, `pdfinfo`, `pdftotext`).
- **LibreOffice** (optional): fills the Word edition's contents page numbers and writes a preview. Without it, Word fills them when the file is opened.
- **PrinceXML** (optional): `ENGINE=prince`. Without a licence Prince stamps a logo on page 1; pass a genuine licence with `PRINCE_LICENSE=<file>`, or stay on WeasyPrint.

## 2. Building

```bash
bash <skill>/scripts/build.sh docs/guide/.print.json
```

About a minute for a 50-page guide, two to three for a 100-page one. Outputs go where the config says (`pdf`, `docx`, `cover_image`, which defaults to the PDF's name with `-cover.png`). For a preview that doesn't touch the repo: `DEV_GUIDE_OUT=/tmp/guide-preview`. `KEEP_DIAGRAMS=1` re-renders only the diagrams that changed; `SKIP_WORD=1` stops after the PDF.

## 3. What the build does

1. `make_art.py` draws the four part tabs; `make_cover.py` prepares the plate and writes the cover and back cover.
2. `build_book.py` renders every Mermaid block to PNG, turns each page into HTML, restyles callouts, openers, quizzes and stats, and assembles cover, contents, about page, part dividers, chapters, glossary and back cover into `book.html` (plus `model.json` for Word).
3. WeasyPrint (or Prince) prints `book.pdf`; page 1 becomes the cover thumbnail.
4. `rasterize.py` turns SVG figures and the cover into PNGs; `build_docx.cjs` writes the Word file; `patch_docx.py` embeds the fonts; LibreOffice and `toc_pages.py` fill the contents page.

## 4. Verify

- **Every page, by eye:** `python <skill>/scripts/contact_sheet.py docs/<name>.pdf /tmp/sheet` and open each sheet. Look for blank pages, a chapter opener stranded at a page bottom, overflowing tables, diagrams too small to read.
- **Diagram sizes:** `python <skill>/scripts/diagram_sizes.py <work-dir>`; reshape anything under about 6.5 pt.
- **The cover** at full size and at 160 px (cover.md § 9).
- **The Word edition:** open the LibreOffice preview (`<work>/docx-preview.pdf`); the cover is page 1 and the contents page 2.
- **Fonts:** `pdffonts docs/<name>.pdf` lists only the guide's fonts, all embedded.
- **Links:** every relative link in `docs/guide/*.md` resolves; previous/next links chain through every chapter.
- **Facts:** re-run the fact sheet's counting commands; every number on the pages still matches.

## 5. Ship

- On the guide's home page, end with the printable editions and the cover:

  ```markdown
  > **Printable editions.** The same guide as a designed book: [PDF](../<name>-developer-guide.pdf) for printing, [Word](../<name>-developer-guide.docx) for editing. Both are built from these pages; rebuild them when the pages change.

  [![The printed edition's cover](../<name>-developer-guide-cover.png)](../<name>-developer-guide.pdf)
  ```

- Link the guide from the repository's README.
- Commit the pages, `assets/` (with the plate and its credit), `.print.json` and the built files together, following the repo's commit rules, and open a PR.
- When the code changes, update the pages, re-check the numbers, bump `edition` and `as_of`, and rebuild.

## 6. Safety

A guide's pages may come from a repository you don't control, so the build treats them as untrusted:

- **One enforcement pass over the finished book** (`safe_html.py`): the assembled HTML is parsed once, only an allowlist of tags and attributes survives, every URL a PDF engine could fetch (`img src`, CSS `url()`) must resolve inside the guide folder, the skill's assets or the work dir, links keep only anchors, http(s) and mailto, and `rel` is dropped so nothing becomes an attachment. The engine then reads the re-serialized tree, so it parses exactly what was checked.
- **Images** in the pages must resolve inside the guide folder (or the work dir, for rendered diagrams); anything else is dropped with a warning.
- **WeasyPrint's fetcher** (`render_pdf.py`) is a second wall: it reads only those folders and never the network. Prince has no such hook; it runs with `--no-network` behind the same enforcement pass. Prefer WeasyPrint for repositories you don't trust. Without these, a page could embed local files as PDF attachments.
- **Outputs stay inside the repository** (or `DEV_GUIDE_OUT`); `repo_name` must be a plain name and `guide_dir` must be inside the repo.
- **Config text is escaped** wherever it lands in HTML or CSS.

## 7. Gotchas

- **Node treats `.js` as an ES module** inside any folder whose `package.json` says `"type": "module"`; that's why the Word builder is `build_docx.cjs`. Keep it `.cjs`.
- **WeasyPrint anchors a named page's background to the content box**, not the sheet; the build shifts the part tabs back by the page margins (`{{TABPOS}}`). If you change page margins in `book.css`, change that offset too.
- **Snap-packaged LibreOffice** can only read non-hidden folders in your home directory; the build uses temporary folders there and cleans them up.
- **A session killed with exit 137** is the kernel's out-of-memory killer, usually taking a different process with it (an indexer, an editor). Check `journalctl -k | grep -i oom` before blaming the build.
- **Prince's evaluation stamp** comes from its licence. Never strip it from output or use a licence file you weren't issued. Build with WeasyPrint, or buy a licence.
- **Diagram text measured in the wrong font** means Chrome didn't see the guide's fonts: `build.sh` points fontconfig at `assets/fonts`; keep `FONTCONFIG_FILE` set when running mermaid-cli yourself.
