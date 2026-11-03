# Verification

Look at everything in a real browser, and run the real server actions against a local database, before claiming it works. Screenshots are for judgment; scripted checks and database rows are the facts.

## Environment (phase 0)

- **Local database**: Postgres in Docker on a non-default port (for example a container named `<app>-pg-dev` on 54329). `.env.local` overrides `DATABASE_URL`; apply the migrations there. Never touch the production database; auto mode blocks reads of it too.
- **Memory**: the owner's machine runs out of memory when the dev server, `tsc`, a full `eslint` and Playwright run together. Run heavy tools one at a time, check `free -m` first, and lint only changed files.
- **Dev server**: note the port. If it vanishes and the browser shows "Connection closed." or "Error in input stream", the server stopped mid-response. Check memory and swap, and ask for the server's terminal output.
- **Signed-in pages**: use the test account the owner allows, or the dev-only playground. Never type the operator's real password.

## Browser loop

1. Load the route or the playground section.
2. Screenshot at 1440 and 390 (and 320 for dense lists), **look at it** with the Read tool, fix and repeat.
3. At phone width, run `overflow.js`, `covered-controls.js` and `tap-targets.js`.
4. Open every "⋮" menu and every sheet. Type into a form, click outside: it must ask before discarding.
5. Dark mode: toggle the theme class or storage key, then reload.
6. Reduced motion: `browser_emulate_media` with `reducedMotion: "reduce"`; final states shown, decorative scenes still.
7. Console: no hydration warnings or errors. If the playground warns only when every demo renders together, check each part alone before chasing it.

## Facts, not pixels

- **Server actions**: run them through `assets/action-harness/` on the local database. Cover partial and excess payments, a decimal comma, and empty optional fields. For concurrency, warm the connection pool first; five parallel check-ins must write exactly one ledger row.
- **Unit tests** for every domain module: money splits, decimal parsing, time-zone formatting (with dates every tz-data version agrees on), error codes and reports.
- **Menus**: a menu works only if `elementFromPoint` at the trigger's centre is the trigger or inside it. That is what `covered-controls.js` checks.
- **Motion**: measure, don't guess. The jerky dialog was confirmed by reading its transform mid-animation (20° tilt, 0.8 scale, a 500 ms tail).

## When a dev server won't fit in memory

Render the component to static HTML with `assets/static-preview.tsx` and serve the output with `python3 -m http.server <port> --bind 127.0.0.1` from its folder. The Playwright MCP blocks `file://` URLs and only saves screenshots inside the workspace (use `.playwright-mcp/`). Tell the owner it was checked statically, not in the running app.

## Before each commit

- Typecheck, lint on the changed files, and the unit tests pass. Build when config or dependencies changed; build in an isolated copy so the dev server keeps running (see `site-upgrade`'s `references/verification.md`).
- `.playwright-mcp/` is in `.gitignore`.
- Scan the staged diff for secrets and, in a public repo, for client details.
