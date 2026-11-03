#!/usr/bin/env bash
# Build the PDF and Word editions of a repo's developer guide from its Markdown pages.
#
# Usage:  build.sh <repo>/docs/guide/.print.json
# Env:    ENGINE=weasyprint|prince  PDF engine (default weasyprint, which stamps nothing)
#         PRINCE_LICENSE=<file>   ENGINE=prince only; without it Prince stamps a logo on page 1
#         KEEP_DIAGRAMS=1         reuse diagrams rendered by the previous run (only changed ones re-render)
#         SKIP_WORD=1             build the PDF only
#         DEV_GUIDE_WORK=<dir>    work directory (default ~/.cache/dev-guide/<repo_name>)
#         DEV_GUIDE_OUT=<dir>     write the PDF, Word file and cover image there instead of the repo (previews)
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$(realpath "$1")"
REPO="$(git -C "$(dirname "$CFG")" rev-parse --show-toplevel)"
cfg() { python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); print(c.get(sys.argv[2], sys.argv[3]))' "$CFG" "$1" "$2"; }
NAME="$(cfg repo_name guide)"
[[ "$NAME" =~ ^[A-Za-z0-9._-]+$ && "$NAME" != . && "$NAME" != .. ]] || { echo "repo_name must be a plain name: $NAME" >&2; exit 1; }
PDF_OUT="$REPO/$(cfg pdf docs/developer-guide.pdf)"
DOCX_OUT="$REPO/$(cfg docx docs/developer-guide.docx)"
COVER_OUT="$REPO/$(cfg cover_image "${PDF_OUT#"$REPO"/}")"
COVER_OUT="${COVER_OUT%.pdf}"; [ "${COVER_OUT%.png}" = "$COVER_OUT" ] && COVER_OUT="$COVER_OUT-cover.png"
# Outputs stay inside the repository (or DEV_GUIDE_OUT): a config can never write elsewhere.
inside() { case "$(realpath -m "$1")" in "$(realpath -m "$2")"/*) return 0 ;; *) return 1 ;; esac; }
for out in "$PDF_OUT" "$DOCX_OUT" "$COVER_OUT"; do
  inside "$out" "$REPO" || { echo "output path leaves the repository: $out" >&2; exit 1; }
done
GUIDE_DIR="$(realpath -m "$REPO/$(cfg guide_dir docs/guide)")"
inside "$GUIDE_DIR/x" "$REPO" || { echo "guide_dir leaves the repository" >&2; exit 1; }
if [ -n "${DEV_GUIDE_OUT:-}" ]; then
  mkdir -p "$DEV_GUIDE_OUT"
  PDF_OUT="$DEV_GUIDE_OUT/$(basename "$PDF_OUT")"; DOCX_OUT="$DEV_GUIDE_OUT/$(basename "$DOCX_OUT")"; COVER_OUT="$DEV_GUIDE_OUT/$(basename "$COVER_OUT")"
fi
CACHE="$HOME/.cache/dev-guide"
WORK="${DEV_GUIDE_WORK:-$CACHE/$NAME}"
mkdir -p "$WORK" "$CACHE"

need() { command -v "$1" >/dev/null || { echo "missing tool: $1 — $2" >&2; exit 1; }; }
# WeasyPrint is the default because it is free software and adds no licence stamp; it lives in
# the skill's own venv, so only Prince needs a tool on PATH.
ENGINE="${ENGINE:-weasyprint}"
export ENGINE
case "$ENGINE" in
  weasyprint) ;;
  prince) need prince "install PrinceXML: https://www.princexml.com/download/" ;;
  *) echo "unknown ENGINE: $ENGINE (use weasyprint or prince)" >&2; exit 1 ;;
esac
need mmdc     "npm install -g @mermaid-js/mermaid-cli"
need node     "install Node.js 18 or newer"
need pdftoppm "install poppler-utils"

# Python packages, in a venv owned by the skill.
PY="$CACHE/venv/bin/python"
if [ ! -x "$PY" ] || ! "$PY" -c "import markdown_it, bs4, pygments, PIL, weasyprint" 2>/dev/null; then
  python3 -m venv "$CACHE/venv"
  "$PY" -m pip install -q markdown-it-py beautifulsoup4 pygments pillow weasyprint
fi
# docx-js for the Word edition.
if [ ! -d "$CACHE/node/node_modules/docx" ]; then
  mkdir -p "$CACHE/node"
  (cd "$CACHE/node" && npm init -y >/dev/null && npm install --silent docx@9 >/dev/null)
fi
export NODE_PATH="$CACHE/node/node_modules"

# A headless Chrome for mermaid-cli: Playwright's shell if present, else puppeteer's default.
CHROME="$(ls -d "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | tail -1 || true)"
if [ -n "$CHROME" ]; then
  printf '{"executablePath":"%s","args":["--no-sandbox"]}\n' "$CHROME" > "$WORK/puppeteer.json"
else
  echo '{"args":["--no-sandbox"]}' > "$WORK/puppeteer.json"
fi

# The guide's fonts, visible to Chrome (so diagrams measure text in Inter) and to Prince.
cat > "$WORK/fonts.conf" <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>$SKILL/assets/fonts</dir>
  <cachedir>$WORK/fccache</cachedir>
</fontconfig>
EOF
export FONTCONFIG_FILE="$WORK/fonts.conf"
LIC_ARGS=()
if [ -n "${PRINCE_LICENSE:-}" ]; then LIC_ARGS=(--license-file="$PRINCE_LICENSE"); fi

cd "$WORK"
[ "${KEEP_DIAGRAMS:-0}" = 1 ] || rm -rf diagrams

# ---- PDF ---------------------------------------------------------------------------------
"$PY" "$SKILL/scripts/make_art.py" "$CFG" "$WORK" >/dev/null
"$PY" "$SKILL/scripts/make_cover.py" "$CFG" "$WORK" "$REPO" >/dev/null
"$PY" "$SKILL/scripts/build_book.py" "$REPO" "$CFG" "$WORK"
if [ "$ENGINE" = prince ]; then
  if ! prince --no-network book.html "${LIC_ARGS[@]}" -o book.pdf > render.log 2>&1; then cat render.log >&2; exit 1; fi
else
  # render_pdf.py lets WeasyPrint read only the guide, the skill's assets and the work dir.
  if ! "$PY" "$SKILL/scripts/render_pdf.py" book.html book.pdf "$GUIDE_DIR" "$SKILL/assets" "$WORK" > render.log 2>&1; then cat render.log >&2; exit 1; fi
fi
if grep -qi "error" render.log; then grep -i "error" render.log | head -5 >&2; fi
mkdir -p "$(dirname "$PDF_OUT")" && cp book.pdf "$PDF_OUT"
echo "PDF:  $PDF_OUT ($(pdfinfo book.pdf | awk '/Pages/ {print $2}') pages)"
# The cover as an image: the README thumbnail, and what file browsers and link previews show.
pdftoppm -png -singlefile -f 1 -l 1 -scale-to-x 1240 -scale-to-y -1 book.pdf cover-thumb
mkdir -p "$(dirname "$COVER_OUT")" && cp cover-thumb.png "$COVER_OUT"
echo "Cover: $COVER_OUT"
[ "${SKIP_WORD:-0}" = 1 ] && exit 0

# ---- Word --------------------------------------------------------------------------------
"$PY" "$SKILL/scripts/rasterize.py" "$REPO" "$CFG" "$WORK" >/dev/null
MONO_FONT="$(fc-match -f '%{file}' 'DejaVu Sans Mono' 2>/dev/null || true)" node "$SKILL/scripts/build_docx.cjs" "$WORK" >/dev/null
"$PY" "$SKILL/scripts/patch_docx.py" guide.docx guide-patched.docx >/dev/null
cp guide-patched.docx guide-final.docx

# Fill the Word contents page: render with LibreOffice (with the guide's fonts installed for
# the duration), read each chapter's page, write the numbers into the TOC field, repeat until
# stable. Word refreshes the field on open anyway; this makes it right before that, and in
# LibreOffice. Snap LibreOffice can only read non-hidden folders in $HOME, hence LO below.
SOFFICE="$(command -v libreoffice || command -v soffice || true)"
if [ -n "$SOFFICE" ]; then
  LO="$HOME/dev-guide-lo-tmp"; FD="$HOME/.local/share/fonts/dev-guide-preview-tmp"
  cleanup() { rm -rf "$FD" "$LO"; fc-cache -f "$HOME/.local/share/fonts" >/dev/null 2>&1 || true; }
  trap cleanup EXIT
  mkdir -p "$LO" "$FD"
  cp "$SKILL"/assets/fonts/{Inter-Regular,Inter-SemiBold,Montserrat-SemiBold,Anton-Regular}.ttf "$FD/"
  fc-cache "$FD" >/dev/null 2>&1 || true
  render() {
    cp "$1" "$LO/guide.docx"; rm -f "$LO/guide.pdf"
    (cd "$LO" && timeout 300 "$SOFFICE" --headless --convert-to pdf guide.docx --outdir "$LO" >/dev/null 2>&1)
  }
  render guide-patched.docx
  : > toc.prev
  for _ in 1 2 3; do
    rm -f toc.json
    "$PY" "$SKILL/scripts/toc_pages.py" "$LO/guide.pdf" >/dev/null
    # No toc.json means the render's text would not extract; Word fills the field on open.
    [ -f toc.json ] || { echo "note: contents page left for Word to fill" >&2; break; }
    if cmp -s toc.json toc.prev; then break; fi
    cp toc.json toc.prev
    "$PY" "$SKILL/scripts/patch_docx.py" guide.docx guide-patched.docx toc.json >/dev/null
    render guide-patched-toc.docx
  done
  [ -f guide-patched-toc.docx ] && cp guide-patched-toc.docx guide-final.docx
  cp "$LO/guide.pdf" docx-preview.pdf
else
  echo "note: LibreOffice not found; the Word contents page fills when Word updates fields" >&2
fi
mkdir -p "$(dirname "$DOCX_OUT")" && cp guide-final.docx "$DOCX_OUT"
echo "Word: $DOCX_OUT${SOFFICE:+ (preview: $WORK/docx-preview.pdf)}"
