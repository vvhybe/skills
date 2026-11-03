# Gotchas, with fixes

Traps hit on real upgrades. Search this file when something behaves oddly.

## Contents

- Rendering and layout
- Motion and media
- Next.js, static exports and the edge
- Mobile browsers
- Third parties
- 3D
- Shell and tooling
- Copy and claims

## Rendering and layout

- **Every page ships "Loading..."**: a `<Suspense>` in the layout around `useSearchParams()` forces client-side rendering. Remove the hook (often unused) or isolate it in a leaf component. Check with `scripts/ssr-audit.sh`.
- **Reveals never fire at the bottom of short screens**: ScrollTrigger measures once; when content changes height later, triggers near the end sit beyond the maximum scroll. Mount `assets/ScrollTriggerRefresh.tsx` and keep footers and closing calls to action free of reveals.
- **Sticky doesn't stick**: the grid item stretches to the row height (add `self-start`), or an ancestor has `overflow: hidden` (use `overflow: clip`).
- **Horizontal scroll on phones**: implicit grid tracks size to their content. Use `grid-cols-1` (`minmax(0, 1fr)`) and `min-w-0` on items holding scroll rows. Also look for fixed-width boxes holding rotated cards, and decorative marks positioned at `left: 100%` (show them only once the frame stands clear of the screen edge).
- **Text tangled under a pinned phone player**: on phones the reading line sits below the pinned media, not at 50%.
- **Markers overlap the mascot on phones**: progress dots, station markers and anchor bubbles positioned for desktop land on the character at 390. Check every station at every phone width.
- **`ResizeObserver loop completed with undelivered notifications`**: the callback resizes the element it observes. Observe the width source and resize an unobserved wrapper.
- **Site styles leak into embedded documents**: give text inside "paper" UIs an explicit size and color, or dark mode turns it light on white.
- **Buttons lowercase their labels**: a `.btn` that lowercases and re-capitalizes breaks "FAQ"; use `normal-case` on those labels.
- **The phone menu ghosts the hero through it**: make the panel solid.
- **A long word overflows in one language**: check every locale's headings at 320.

## Motion and media

- **Intro elements flash before the timeline starts, or stay hidden when the script is late**: hide them only under a class an inline `<head>` script adds to `<html>`, inside `prefers-reduced-motion: no-preference`; reveal with `autoAlpha`, and let a timeout in that inline script remove the class if the timeline never runs (building-blocks.md § Cinematic hero).
- **GSAP transforms fight CSS ones**: put pointer, intro and static rotation on separate nested elements. Tailwind 4's `rotate`, `scale` and `translate` utilities are separate CSS properties and compose with GSAP's `transform`.
- **Chapter seeks are slow or land wrong**: re-encode with a keyframe every second plus forced keyframes at the cuts (`scripts/video-prep.sh`).
- **A slot roll spins backwards when it wraps**: duplicate the first item at the end, then snap back without a transition on `transitionend`.
- **A "changed" flash fires everywhere on the first edit**: track change per value with derived state, not with a global "armed" flag.
- **Descenders clipped in masked headline reveals**: add bottom padding and an equal negative margin to the mask.

## Next.js, static exports and the edge

- **`react-dom/server` crashes in a route handler** ("Cannot set properties of undefined (setting 'recentlyCreatedOwnerStacks')"): route handlers use React's server build. Render emails with `assets/render-email.ts`.
- **`@react-email/render` bloats the edge bundle**: its edge build imports prettier and html-to-text. Use the individual component packages and the static renderer.
- **Social-card routes pull fonts and images into the worker**: drop the runtime export so they prerender at build with `node:fs`.
- **Social-card renderer limits**: no `inset`, no `closest-side`, no `backgroundSize` patterns, `display: flex` on every multi-child element, TTF/OTF/WOFF fonts only. A query string on `/opengraph-image` returns 404 in dev.
- **Social-card URL inside a route group is hashed** (`/fr/opengraph-image-k0kfef`): never hard-code it. A Node-only image route in a group is inherited by edge-runtime children and breaks their build.
- **"Missing `<html>` and `<body>` tags in the root layout"**: when a `[lang]` layout renders `<html>`, the root layout renders none, so anything rendered through the root alone (`app/not-found.tsx`, `app/page.tsx`) must bring its own document or redirect.
- **`next dev` throws "missing param in generateStaticParams" with `output: 'export'`** for an address the catch-all matches but no page exists for: that's the dev check; production serves the 404. Set `dynamicParams = false` where only listed params exist.
- **Full-stack adapters fail on static routes** (for example "Invalid prerender config" for every `[lang]` route, or npm peer-dependency errors after a tooling update): a static export plus a few Functions is usually the reliable path on Cloudflare Pages.
- **Pages Functions bundle with their own wrangler version**, which honors the root `tsconfig` (`"jsx": "preserve"` breaks email templates): give the templates folder its own `tsconfig.json` with `"jsx": "react-jsx"`.
- **`wrangler pages dev --proxy` applies the production CSP to `next dev` pages**, which need eval, so they crash. Test Functions against a production build instead.
- **Turbopack serves stale state** (a renamed token, a route that moved between groups): touch `next.config.*` to restart the dev server, and verify markup changes on a production build.
- **Next 16's `next dev` appends an agent-rules block to `AGENTS.md`**: `agentRules: false` in the config stops it. Keep it out of PRs unless the owner wants it.
- **IDE "canonical class" warnings** (`max-w-[540px]` as `max-w-135`) are suggestions; match the codebase.

## Mobile browsers

- **iPhone Safari's status bar turns white after a reload** (iOS 26+): Safari tints it from the page canvas, not the `theme-color` tag, and samples before the hero paints. Set the theme color as the `<html>` background inline. A floating pill navbar doesn't count as a full-width header.
- **The contact button disappears on phones**: the bar hid it and the menu never listed it. Every action in the bar is also in the menu.
- **Hover-only interactions**: logo color on hover, tooltips and previews need a tap or always-on equivalent; gate hover styles with `@media (hover: hover)`.

## Third parties

- **An element with `id="clarity"` stops Microsoft Clarity from installing**: element ids become window properties. Never give a script that id.
- **Third-party analytics cookies cost Lighthouse Best Practices**: a known trade-off once the owner chose it; record it so later audits don't undo it.
- **Brand-logo CDN returns a fallback "B"** for an asset type the brand doesn't have, and a guidelines redirect to `curl` and default headless Chrome (media.md § 5).
- **Headless browsers never get Turnstile tokens on production hosts**: test on localhost or in a real browser.
- **A scheduler iframe** clashes with the design and widens the CSP; proxy its API instead.

## 3D

- **Grooves on a model that looked fine in Blender**: inward-facing faces. Flip them in the export script.
- **Draco or meshopt models fail to load**: their decoders need WebAssembly, which a CSP without `'wasm-unsafe-eval'` blocks.
- **The mascot looks different in each section**: one lighting setup and one camera language for every placement.

## Shell and tooling

- **`ls` may be aliased** (eza, exa): use `command ls` for raw output.
- **zsh doesn't split an unquoted `$VAR`** holding several words: use arrays or `xargs`. zsh globs in `grep --include=*.ts` fail with "no matches found"; quote them.
- **`echo ======` fails in zsh** (`=` expansion): quote it.
- **`kill $(ps … | grep pattern)` can kill your own shell**: the pattern matches the command line running it. Find servers by port (`ss -ltnp | grep :PORT`).
- **`cd` inside a tool call** can move the session's working directory; use absolute paths or subshells.
- **`git rm` refuses files with local changes**: use `rm` and let the deletion show in `git status`.
- **A local `main` lags after squash merges**: fetch and compare with `origin/main`.
- **`yarn -s` isn't valid in Yarn 4**: use plain `yarn <script>`.
- **pnpm in a scratch copy with a symlinked `node_modules`** rewrites the shared `.bin` wrappers; call `./node_modules/.bin/<tool>` there. Repair with `pnpm install --frozen-lockfile --offline --force`.
- **Install scripts** (sharp, esbuild) may need an explicit allow list in `pnpm-workspace.yaml` for the hosting build to work.
- **Downloads from `raw.githubusercontent.com` can hang**: use a timeout and check the output file.
- **The Playwright MCP refuses a `filename` outside the workspace**: copy the script into `.playwright-mcp/`. A trailing `;` after the function gives "Unexpected token ';'".
- **`ffprobe` isn't installed**: `ffmpeg -i <file>` prints the stream info.
- **React 19 ignores `defaultProps` on function components**: icon libraries that set size and color that way draw nothing; wrap them once with explicit defaults and import only the wrapper.

## Copy and claims

- **The product's own paywall or onboarding copy overpromises**: verify each claim in code.
- **A feature screen exists but nothing links to it**: it isn't shipped.
- **A button only toasts "coming soon"**: it isn't shipped.
- **Leftover template calls to action** promise trials and newsletters that don't exist: delete them.
- **Env flags say "live" but the store disagrees**: ask the owner and check the live listing.
- **Two documents disagree on a fact** (a phone number, an address): the public business profile or the legal entity's own record wins; keep every copy identical.
- **Localized store prices look wrong** (a storefront shows a different number than the base price): stores set per-country prices including tax. Quote the base price and say the store shows the local one.
