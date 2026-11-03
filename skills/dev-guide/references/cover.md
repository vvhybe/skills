# The cover

The cover is the guide's thumbnail: the first page of the PDF, the Word file's first page, the image in the README, what a file browser and a link preview show. It decides whether the guide looks like a book someone made, or a document someone exported.

## Contents

1. What professional technical covers do
2. The plate style
3. Choosing the plate
4. Finding it
5. Treatment and layout
6. Series
7. The type style (no plate)
8. Configuration
9. Checks

## 1. What professional technical covers do

Look at the covers developers keep on their shelves and the same few decisions repeat:

- **One picture, and it is real.** Long-running technical series put a single engraving on every cover: animals, historical costume figures, scientific and botanical plates. The picture is an artefact of the world, printed cleanly, never a drawing of the product's UI.
- **A series system.** Every title in a series shares the grid, the type and the position of each element. Only the picture, the title and one colour change. Readers recognise the series before they read the title.
- **Classic type, set large.** A book face (a Garamond, a Caslon) or one confident sans, two or three sizes, nothing else.
- **Colour as identity.** One colour per volume, usually a deep print ink (green, blue, oxblood), filling a panel or band.
- **Restraint.** No badges, no icons, no gradients, no floating UI cards, no blobs. Those make a cover look like a slide.

The skill builds exactly that system. Learn from these series, but never copy any one publisher's trade dress (a specific publisher's combination of animal engraving, white ground, red band and logo). The plate, the grid and the colours here are their own.

## 2. The plate style

The default style. The upper cover is paper with the plate printed in one ink and captioned like a book plate; the lower third is a panel in the volume's colour carrying the title (EB Garamond), the subtitle in italic, the tagline and a footer with the author and edition. A header rule carries the series name and volume.

## 3. Choosing the plate

Find the picture the way you'd find the idea for a website: from the subject, not the category.

- **The project's name.** A project named after a plant, a tool or a place can take that thing itself, in a period plate: a botanical woodcut, an instrument, a map.
- **What it does, in an older craft.** A PDF engine is a printing press: an 1819 encyclopaedia plate of a common press. A template kit is typesetting: Diderot's *Encyclopédie* plate of compositors at the type case, with set type in the foreground.
- **Its mechanism.** Queues, gears, looms, signals, maps, instruments, anatomy: the pre-digital ancestor of what the code does.
- **Its world.** The trade or domain it serves (shipping, accounting, medicine) in a period plate.

Prefer technical, scientific and botanical plates: they're precise, mostly line work, print beautifully in one ink, and carry no people's likenesses. Avoid anything a modern rights holder owns (logos, modern photographs, recent illustrations), images of identifiable private people, and symbols that carry political or hateful meaning.

Search vocabulary that finds plates: *engraving*, *plate*, *woodcut*, *lithograph*, *etching*, *botanical illustration*, *encyclopedia*, *Encyclopédie*, *Cyclopaedia*, *patent drawing*, *technical drawing*, *diagram*, with a date ("19th century").

## 4. Finding it

```bash
PY=~/.cache/dev-guide/venv/bin/python       # created by the first build; any Python with Pillow works
$PY <skill>/scripts/find_plate.py "printing press engraving" --sheet press.png
```

It searches Wikimedia Commons by default (which mirrors most open library scans), keeps only public-domain and CC0 files, and prints each candidate's reference, title, creator, date and licence. `--sources commons,aic` adds the Art Institute of Chicago's open-access collection, which refuses some networks. `--allow-by` also lists CC BY and CC BY-SA files (credit required; the owner must accept the licence).

**Look before choosing.** Open the contact sheet. Pick for clarity at thumbnail size, line work over muddy tone, and a subject that reads at a glance. Show the owner two or three and recommend one. Then:

```bash
$PY <skill>/scripts/find_plate.py --get "commons:File:Printing_press.jpg" --out docs/guide/assets/cover
```

It downloads the full-resolution file and writes `<name>.json` beside it with the source page, licence and a ready credit line. Commit both, so the book builds offline and the credit travels with the image. Aim for at least 2000 px on the long side.

## 5. Treatment and layout

`make_cover.py` does this on every build:

- converts the plate to grayscale and crops it (`cover.plate.crop`, fractions of the image: `[left, top, right, bottom]`)
- measures the scan's paper tone and maps it to the cover's paper, and its darkest ink to the cover's ink, so yellowed or grey scans print clean (`cover.plate.paper` and `cover.plate.ink` override the measured percentiles)
- prints it in one ink (`cover.ink`, a warm black by default) on the cover's paper (`cover.paper`)
- places it in a 174 × 146 mm box, landscape plates by width and portrait plates by height, centred, with the caption below
- writes the credit onto the back cover

Preview the cover alone while iterating (a few seconds, no full build):

```bash
$PY <skill>/scripts/make_cover.py docs/guide/.print.json /tmp/cover-work . --preview /tmp/cover.pdf
pdftoppm -png -r 60 -singlefile /tmp/cover.pdf /tmp/cover
```

## 6. Series

Several related repositories become volumes of one series:

- the same `cover.series` (for example "Acme developer guides")
- `cover.volume`: "Volume I", "Volume II", …
- one plate per volume, from one family of subjects (for a document toolchain, a history of writing and printing: a writing material, the press, the type case)
- one colour per volume: the brand's colour for the main volume, then companion inks of similar depth (a deep green, a deep blue, an oxblood red). Test them side by side.

## 7. The type style (no plate)

When no plate fits, or the guide must build offline without one: `"style": "type"`. The upper cover carries one large mark in the volume's colour (`cover.mark`, by default the title's first letter); everything else stays the same, so a type-style volume still belongs to its series.

## 8. Configuration

In `.print.json`:

```json
"cover": {
  "style": "plate",
  "series": "Acme developer guides",
  "volume": "Volume II",
  "colour": "#1F3A5F",
  "plate": {
    "file": "docs/guide/assets/cover/printing-press.jpg",
    "caption": "Perspective view of a common printing press. Engraving by John Farey, 1819.",
    "crop": [0, 0, 1, 1]
  }
}
```

Optional: `ink` (default `#1d1b18`), `paper` (default `#fbfaf7`), `on_colour` (type on the panel, default the paper colour), `plate.credit` (overrides the sidecar's credit), `mark` (type style). The title, subtitle, tagline, author and edition come from the top level of the config.

## 9. Checks

- **At thumbnail size:** look at the cover PNG at 160 px wide. The title must read and the plate must still be a recognisable thing.
- **The caption** sits fully above the panel, and the title fits its panel without wrapping awkwardly.
- **The credit** is on the back cover, with the licence.
- **The series:** volumes side by side share every position; only the plate, title and colour differ.
