# Media: video, images, logos and protected assets

## Contents

1. ffmpeg without a system install
2. Video for the web
3. Images
4. App screenshots in a device frame
5. Brand logos from a CDN
6. QR codes with a logo
7. Rendering SVG or HTML to PNG
8. Fonts for social cards
9. Protecting proprietary assets

## 1. ffmpeg without a system install

`scripts/video-prep.sh` finds `ffmpeg` on the PATH and otherwise falls back to the binary bundled with the Python package `imageio_ffmpeg` (`python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`). There's no `ffprobe` there; `ffmpeg -i <file>` prints the same stream info.

## 2. Video for the web

Run `scripts/video-prep.sh <source> <out-dir> [name]`. It:

1. prints duration, size, streams and scene cuts (`select='gt(scene,0.12)'`), which make chapter boundaries, and writes `<name>-contact.jpg`, a contact sheet of the first minute for studying palette, type and story
2. writes `<name>.webm` (VP9) and `<name>.mp4` (H.264, `+faststart`) at 720 on the short side, 30 fps and **silent**, with a keyframe every second plus forced keyframes at each cut, so seeking between chapters is instant
3. writes `<name>-poster.webp`
4. writes `<name>-preview.webm` and `.mp4`: a 240 px square, center-cropped, silent clip for live thumbnails

A 14 MB 1080p60 product reel came down to 1.9 MB WebM and 3.0 MB MP4. Pin exact chapter times by eyeballing a strip around each cut (`fps=5,scale=180:-1,tile=6x1`).

Serve WebM first, then MP4, with `playsInline muted loop preload="metadata"` and the poster. Play only while on screen (an IntersectionObserver at 0.5), never autoplay under reduced motion, and keep a pause button. A reel made for phones (portrait) wants the full screen on phones (building-blocks.md § Scroll story).

When the product's UI changes, check the reel: a finished video with no source project can't be patched. Flag it as stale rather than claiming the site is up to date.

## 3. Images

- **Real outputs** (documents, templates, renders): WebP at about 2× the display size (`PIL ... .save(path, 'WEBP', quality=80, method=6)`). An A4 render at 840×1188 is about 45 KB.
- **Convert PNG and JPEG photos to WebP** for mobile; keep PNG only where transparency and hard edges need it.
- **Rounded icons for email:** bake the radius into the PNG with a mask; Outlook ignores `border-radius` on `<img>`.
- **Maskable PWA icon:** the brand's background full-bleed with the mark at about 50% of the canvas, inside the 80% safe circle.
- Always set `width` and `height` (or `aspect-ratio`) so nothing shifts as images load; `loading="eager"` and `fetchpriority="high"` on the largest image above the fold.

## 4. App screenshots in a device frame

Reuse one good device frame instead of redrawing a phone. Composite each new screen into its screen area, mask it with the frame's bezel ring, then copy the Dynamic Island (or notch) back on top. Record the screen rectangle (for example 828×1802 at (86,84) in a 1000×1970 frame) next to the frame file so the next release takes minutes. Update the hero, the social card and any feature crops together, so no visual shows the previous version's UI.

## 5. Brand logos from a CDN

Other companies' logos (store badges, integrations, a catalog of systems) come from a brand-logo CDN such as Brandfetch's Logo Link instead of static SVGs that go stale. Gotchas found by rendering each one:

- **Check the brand is the real one.** Search results include look-alike and spam domains that serve a betting or streaming logo under a familiar name. Google Play, for example, lives under the `play.google` brand; `play.google.com` resolves to Google's "G".
- **`theme` is the logo's own color.** `dark` means a dark logo for a light background. The wrong one is invisible.
- **Ask only for assets that exist.** A missing type (no `symbol` for a brand) returns the CDN's fallback mark. Vector types come as SVG; `icon` is a PNG sized through the URL.
- **Terms:** hotlinking is usually the only allowed use (no self-hosting), with the site's origin as referrer. Plain `curl` and default headless Chrome may be redirected to the guidelines page; test with a desktop browser user agent. Add the CDN host to the CSP's `img-src`.
- The client ID is a public value in an env var (`NEXT_PUBLIC_…`), not a secret.

## 6. QR codes with a logo

A QR code that is the link (to a store listing, to the app) can carry the logo, done properly: generate the code as SVG with error correction H (or Q), clear the **whole modules** under the logo's area, draw the logo in the gap, and verify it scans (decode it with `jsQR` from a rendered PNG at the size it ships). Placing a logo on top of an untouched code is the cheap version; it breaks scanning and owners notice. Show it large enough to scan from a laptop screen.

## 7. Rendering SVG or HTML to PNG

For email images, social-card art, posters and anything needing filters or real fonts:

1. Write a standalone HTML page in the scratchpad with the fonts linked and the SVG inline.
2. In Playwright, open it as a `file://` URL, wait for `document.fonts.ready`, and screenshot the element with `omitBackground: true` for transparency.
3. For crispness, render at 2× the CSS size, then downscale with PIL.
4. Shrink with `im.quantize(colors=48, method=Image.Quantize.FASTOCTREE)`; an ink seal went from 147 KB to 11 KB.

`browser_run_code_unsafe` can't `require('fs')`; navigate to the file URL instead.

## 8. Fonts for social cards

The social-card renderer (satori, behind `next/og`) reads TTF, OTF and WOFF, not WOFF2. Fetch the Google Fonts CSS with an old user agent to get TTF URLs:

```bash
curl -s -A "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=<Family>:wght@500;600"
```

Commit the TTFs with the family's licence text (OFL.txt from the google/fonts repository) in the same folder.

## 9. Protecting proprietary assets

When the site shows something the company sells (templates, designs, a dataset), publish previews, never the product:

- **Static snapshot.** A script copies what the site needs from one release commit of the source repo (reading git objects, not the working tree) and records that commit. The build never runs it, and the site never calls the product's API, bucket or CDN.
- **Small sizes only:** catalog thumbnails around 240 px and close-ups around 640 px. Keep full-size originals and mockups out of `public/`.
- **Source never ships.** Template code (`.j2`, `.liquid`, source files) stays out of the build output entirely.
- **Headers and metadata:** `Cross-Origin-Resource-Policy: same-site` on those image paths, copyright in the image EXIF.
- **Licence holds:** skip any item whose source marks it not for publication (third-party fonts or art without a publishing licence) and list what was held.
- **Tests enforce it:** a test that fails when a source file, an oversized image or a held item appears in `public/`.
- Watermarks are a last resort: they make thumbnails ugly, and owners usually drop them.
