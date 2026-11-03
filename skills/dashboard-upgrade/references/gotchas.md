# Gotchas, with fixes

## Data and actions

- **Every payment fails in production**: the schema has an enum value that no migration added. Write the migration (`ALTER TYPE … ADD VALUE IF NOT EXISTS`) and add the schema-drift check to CI.
- **A double tap writes twice** (check-in, payment): do the read and the write in one transaction with `FOR UPDATE` on the rows involved.
- **"500,50" saved as 50,050**: the input stripped the comma. Normalize commas to dots first, then strip.
- **"Expected number, received string"**: form values are strings. Coerce with one shared zod helper.
- **An optional select rejected**: the form sent `""` where the schema expected `null`. Map empty to `null` on the server.
- **An edit silently ignored**: the action wrote the old values. Check it reads the submitted fields.
- **A `ReferenceError` only on the auth error path** (a variable used before it was defined): exercise the error branches, not just the happy path.
- **A second payment stuck on "Recording…"**: the dialog kept the first submission's request id and submit latch. Reset them, and reload the current balance, every time it opens.
- **`crypto.randomUUID` is undefined** when the app is opened over plain HTTP on the LAN (not a secure context), so a phone test breaks idempotency keys. Fall back to a UUID built from `crypto.getRandomValues`.

## Time

- **Node bundles its own tz data**: Morocco moved to UTC+0 on 2026-09-20, but Node 24.12 (tz 2025b) still says UTC+1. Format through `Intl` with the zone name, write tests on dates every tz version agrees on, and keep servers on a current Node.
- **"Today" is wrong on the server**: server code runs in UTC. Compute the day in the business zone.

## UI

- **animate-ui DropdownMenu** gives hydration id mismatches: use plain Radix.
- **animate-ui Dialog** flips in 3D and feels jerky: use plain Radix with `zoom-in-95` and `slide-in-from-bottom-2`, 300 ms in and 150 ms out.
- **A "⋮" that does nothing**: a card's link overlay at the same z-index covers it. Lift the actions layer (`z-20`) and check with `covered-controls.js`.
- **Cards push the page sideways on phones**: implicit grid tracks size to their content. Use `grid-cols-1` or `minmax(0, 1fr)` and `min-w-0`.
- **A link inside a toast** is invalid HTML because the sileo toast is a `<button>`. Use one action button instead.
- **Toast titles in Title Case**: override with `[data-sileo-viewport] [data-sileo-title] { text-transform: none }`.
- **Hydration mismatch from decoration**: `Math.random()` positions differ between server and browser. Use deterministic spacing (golden-ratio steps).
- **Browser-only values** (URL, device, a generated code) in a client component: use `useSyncExternalStore` with a server snapshot, not `useEffect` plus `setState`.
- **A JSX comment inside a ternary's parentheses** breaks parsing: move it outside.
- **Flat 3D**: `perspective` only applies to direct children. Put it on the 3D-transformed element's parent; a `filter` on an ancestor flattens the 3D.
- **A muddy scene in dark mode**: the theme's "secondary" tokens become dark surfaces. Give decorative scenes their own light and dark palette.

## Dev environment

- **OOM kills** (exit 137, or the dev server vanishing): the dev server, `tsc`, `eslint` and Playwright together exceed memory. Run them one at a time.
- **A failed check that looks green**: `pnpm typecheck | tail -3 && git commit` commits anyway, because a pipe returns the last command's status (`tail`, 0). Redirect to a log and test `$?`, or use `set -o pipefail`, before chaining a commit.
- **zsh**: `--include=*.tsx` gives "no matches found" (quote it); `$F` isn't word-split (use `${=F}`).
- **`pkill -f pattern`** matches its own shell and kills it (exit 144): use a bracket pattern such as `[h]ttp.server`.
- **A "covered" control in dev**: when `elementFromPoint` returns `nextjs-portal`, it's the Next.js dev overlay's issues badge, not the app. `covered-controls.js` skips it.
- **Out of memory mid-check (exit 137)**: the type-check, a dev server and a signed-in browser together exceed memory. Cap tsc with `NODE_OPTIONS=--max-old-space-size=2500`, or stop the dev server first.
- **Playwright MCP**: `file://` is blocked and screenshots are saved only inside the workspace. Serve over HTTP and save to `.playwright-mcp/`.
- **A tsx script outside the repo can't find packages**: set `NODE_PATH=$PWD/node_modules`. With the classic JSX transform, set `globalThis.React`.
- **A production build in an isolated copy fails** with "Symlink node_modules is invalid, it points out of the filesystem root": Turbopack refuses a symlinked `node_modules`. `next build --webpack` accepts it and is a fair test of React behaviour (hydration, server actions).
- **A hydration mismatch only in dev**: confirm on a production build before chasing it. Production React doesn't log attribute mismatches, so test the effect (for example a menu trigger's `id` against the menu's `aria-labelledby`).
- **Server actions outside Next**: `next/cache` must be stubbed, and an ESM `.mts` script loses the repo's named exports. Use the CommonJS harness in `assets/action-harness/`.
