# Verification

Look at everything you build in a real browser before you claim it works. Screenshots are for judgment, scripted checks are for facts, and the critique (critique.md) turns judgment into a score.

## Contents

1. Kickoff: baseline and before captures
2. The loop for each section
3. Widths, themes and preferences
4. Scripted checks
5. Interactions and APIs
6. Production builds without breaking the dev server
7. Platform checks
8. Before every commit

## 1. Kickoff: baseline and before captures

- Start the dev server and note the real port.
- Copy the Playwright scripts into the workspace once: `mkdir -p .playwright-mcp && cp <skill>/scripts/playwright/*.js .playwright-mcp/`, and make sure `.playwright-mcp/` is git-ignored.
- Capture the **before** set: each page at 1440×900 and 390×844, full page after `reveal-scroll.js`. The after set later uses the same viewports, so the report compares like with like.
- When capturing a live site, block analytics hosts first so the captures don't send hits, and dismiss the consent card:

  ```js
  await page.route(/(clarity\.ms|googletagmanager|google-analytics|cloudflareinsights|bing\.com)/, (r) => r.abort());
  ```

## 2. The loop for each section

1. Load the page.
2. Run `reveal-scroll.js` (as the `filename` of `browser_run_code_unsafe`).
3. Scroll the section into view and wait out its animation.
4. Screenshot it, then **look at it** with the Read tool. Fix what's off, and batch fixes before the next look rather than screenshotting after every tweak.

To capture one section without a fixed navbar over it, add `[data-shot-hide]{display:none!important}` in a style tag, set `data-shot-hide` on the bar, then take the element screenshot.

## 3. Widths, themes and preferences

Check every section in each of these:

- **Widths:** 1440 (desktop), **1920×710** (a short laptop window; it exposes bottom-of-page reveal bugs), 390 and 320 (phones). Add 768 when the layout changes there.
- **Themes:** light and dark if the site has both (set the stored theme, then reload).
- **Reduced motion:** `page.emulateMedia({ reducedMotion: 'reduce' })`. Intro targets must be visible, no video may autoplay, tiles and counters show their end state.
- **Languages:** every locale's home page and one inner page, looking for overflow from longer words.

## 4. Scripted checks

- **`page-audit.js`** on each page and at 390: one `<h1>`, headings over two lines, text under 12 px, tap targets under 40×40 at phone width, controls without an accessible name, images without `alt`, sections without a heading, and whether the browser surfaces (selection, scrollbar, caret, accent) are themed.
- **`overflow.js`** on each page: `scrollWidth − clientWidth` and the offending elements per width.
- **`reveal-scroll.js`**: text still hidden after a full scroll is a reveal that failed.
- **`console-scan.js`** on a production server: console errors, page errors, failed requests, 4xx/5xx and CSP violations across every sitemap page.
- **`slop-scan.mjs`** on the source: tells, invented proof, genre copy, dead links. Every remaining finding is either fixed or an earned exception with a `site-upgrade-allow` comment.
- **`ssr-audit.sh`** on a production server: server-rendered pages, one `<h1>`, canonical, social image, headers, crawler files.

## 5. Interactions and APIs

- Check real state, not only pixels: the video's `currentTime` and `paused` after clicking a chapter; a live region's text after changing a quantity; which values flashed after one edit; the prefilled field after arriving from the catalog.
- **Auto-advance:** leave the page alone and log the active chapter and `currentTime` every second for 25 s.
- **API branches:** call `fetch('/api/...')` from inside the page; fake responses with `page.route`.
- **Keyboard:** tab through the page; every control reachable in reading order with a visible focus ring; the menu closes on Escape; galleries respond to arrow keys.

## 6. Production builds without breaking the dev server

`next build` and a running `next dev` share `.next/`, and the build knocks out the dev server. Build in an isolated copy instead:

```bash
B=<scratchpad>/prodcheck && rm -rf "$B" && mkdir -p "$B"
rsync -a --exclude={node_modules,.next,out,dist,.git,.playwright-mcp} ./ "$B"/   # the working tree, uncommitted changes included
ln -s "$PWD/node_modules" "$B/node_modules"
cp .env "$B/.env" 2>/dev/null || true     # when the build reads env values (prices, store URLs)
(cd "$B" && ./node_modules/.bin/next build && nohup ./node_modules/.bin/next start -p 3100 > ../prod.log 2>&1 &)
```

- Call the framework binary directly in the copy. A package manager run there may rewrite the shared `node_modules/.bin` wrappers with the copy's path (pnpm does), which breaks the repo once the copy is gone.
- For a static export, serve `out/` instead (`npx serve out -l 3100`, or the host's local runner for Functions).
- **Stopping it:** find the PID by port (`ss -ltnp | grep :3100`) and kill that. `pkill -f` patterns can match your own shell's command line and kill it. The framework's server child keeps the port too; if a restart fails with `EADDRINUSE`, kill it as well, or you'll be testing the old build.
- When rechecking a rebuilt static site, the browser may serve cached HTML heuristically. Disable the cache or add a `?v=` query.

## 7. Platform checks

- **iPhone Safari:** reload the page and check that the status bar keeps the page's color (gotchas.md § iOS status bar).
- **Bot checks:** headless browsers don't get Turnstile tokens on production hosts. Test the form end to end on localhost, or ask the owner to submit once from their browser.
- **Functions:** run the host's local runner against the production build (for Cloudflare Pages: `npx wrangler pages dev out`) to exercise middleware, redirects and API routes with the production CSP.
- **Deploy previews:** after pushing, wait for the preview build (`gh pr checks <n>`) and open it. A transient "failed to publish Functions" after assets uploaded is often a host-side hiccup; retry the deployment once before changing code.

## 8. Before every commit

- The repo's lint, type check and format command, and a production build, all pass.
- Remove `.playwright-mcp/` artifacts from the repo root; the MCP writes snapshots there.
- Scan the staged diff for secrets, tokens and env files (only `.env.example` is committed).
- Stage specific files. Owners keep local drafts in the repo root; `git add -A` sweeps them in.
