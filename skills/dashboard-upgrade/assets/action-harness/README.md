# Action harness

Runs a repo's real server actions and domain code against the **local** database, without Next.js. Use it for facts the browser can't show: rows written, balances after a split payment, races.

## Setup (once per session)

```bash
H=<scratchpad>/harness && mkdir -p $H
cp <skill>/assets/action-harness/{next-cache-stub.ts,require-user-stub.ts,example.ts} $H/
sed -e "s|<REPO>|$PWD|g" -e "s|<HARNESS>|$H|g" \
  <skill>/assets/action-harness/tsconfig.template.json > $H/tsconfig.json
```

Edit `$H/example.ts` (or copy it per scenario), then run it **from the repo root** with the local database URL:

```bash
DATABASE_URL=postgresql://postgres:dev@localhost:54329/app npx tsx --tsconfig $H/tsconfig.json $H/example.ts
```

Use the repo's package manager (`pnpm exec tsx` in a pnpm repo).

## Rules

- **Local database only.** Pass `DATABASE_URL` explicitly. dotenv doesn't override a variable that's already set, so `.env` (production) is ignored. Never point it at production.
- **CommonJS `.ts` with `async function main()`.** An ESM `.mts` script loses the named exports of repo files, and CommonJS forbids top-level `await`.
- **Stubs**: `next/cache` is mapped to a no-op stub, and the app's session check (`@/lib/auth/require-user` in the reference implementation) to a stub returning a test user. Adapt that path to the target repo's own session helper.
- **Races**: warm the connection pool first (the example shows how). On a cold pool, postgres-js pipelines everything on one connection and a race never reproduces.
- **Test data**: tag the rows you insert with a random suffix so runs don't collide, and leave the local database usable.
- **Before and after**: to prove a fix, run the same script against the old code (`git stash push -- <file>`, run, `git stash pop`).
