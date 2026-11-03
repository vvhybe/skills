# Foundations

Build each piece once, move every screen onto it, then delete the old variants. A second way of doing the same thing is how dashboards drift back into inconsistency.

`Ref:` paths are in the public reference implementation, [jnaninyoga/dashboard](https://github.com/jnaninyoga/dashboard). Adapt names to the target repo.

## Create and edit: the form sheet

- A side sheet on desktop and a bottom drawer on phones. Ref: `components/form-sheet.tsx`, `components/ui/drawer.tsx`.
- **Dirty guard**: snapshot the form's `FormData` a frame after it opens and compare on every dismiss attempt. With changes, an outside click, Escape, swipe or Cancel asks "Discard changes?". While saving, the sheet is locked.
- The primary action says what happens ("Save client", "Record payment"), in a footer that stays visible on long forms.
- Dialogs remain only for short confirmations.

## Lists: one data table

- A table on desktop and cards on phones, with the same empty state, sorting, and paging only when there is more than one page. Ref: `components/data-table.tsx`, `components/empty-state.tsx`.
- A phone card shows what the operator needs at a glance (name, status, the one number) and 40 px actions (call, WhatsApp).
- Hover tooltips never appear on phones: write alerts (such as health notes) on the card.
- Grids and flex rows on phones: `grid-cols-1` (which is `minmax(0, 1fr)`) and `min-w-0` on children, or long content pushes the page sideways.

## Row actions

- One "⋮" trigger: 40 px on phones, with an `aria-label` naming whose actions they are. Ref: `components/row-actions-trigger.tsx`.
- Keep menus on plain Radix `DropdownMenu`; animate-ui's version caused hydration id mismatches.
- When a whole card is a link, put the actions layer above the link overlay (`z-20` on the reference's partner cards) and confirm with `covered-controls.js`.

## Feedback and errors

- **One toast helper** for success, error, warning and info, so every message looks and reads alike. Ref: `lib/feedback/notify.tsx`, `components/feedback/toaster.tsx` (top-centre on phones, bottom-right on desktop).
- **Error codes**: server actions catch unexpected failures with `logServerError(scope, error)`, which logs under a short code (`JY-` plus 6 characters with no look-alikes) and returns it; the action returns `{ error, ref }`; the client calls `notifyActionError(result)`. Ref: `lib/errors/server.ts`.
- **Error report**: the code, what happened, when (business time and exact UTC), the page, the device and the app version. It can be copied or emailed to the developer, whose address comes from an env var. Ref: `lib/errors/report.ts` and its tests.
- **One error screen** for every route `error.tsx` and for `global-error`: calm copy, one "Try again", the code, copy and email buttons, technical details folded away. When the message shows a cut connection ("Error in input stream", "Failed to fetch", "Load failed"), say that instead. Build the report only in the browser (`useSyncExternalStore` with a server snapshot of `false`). Ref: `components/feedback/error-screen.tsx`.
- **Confirmations**: replace `window.alert` and `window.confirm` with a provider and `await confirm({...})`, with a destructive variant. Ref: `components/feedback/confirm.tsx`.

## Data and money

- **A domain module** for every money rule: pure functions in integer cents, unit-tested. Ref: `lib/domain/billing/payments.ts` (which statuses are payable, and how a payment is split across invoices: the viewed invoice first, the excess to the rest).
- **Server actions** call those functions inside one transaction, with `SELECT … FOR UPDATE` on the rows they change.
- **Double taps** (check-in, payment) must not write twice: lock the wallet or ledger rows in the same transaction that writes.
- **Decimal input**: turn commas into dots, then strip everything except digits and the dot, then parse. Ref: `lib/utils/currency.ts` (`normalizeDecimalInput`, `parseAmountInput`).
- **Form numbers**: inputs give strings; coerce with one shared zod helper and type forms with `z.input` and `z.output`. Ref: `lib/validators/shared.ts` (`numberFromInput`).
- **Optional fields**: an empty string becomes `null` on the server, not a validation error.
- **Time**: one helper module with the business zone name (`Africa/Casablanca`); never a hard-coded offset. Ref: `lib/utils/time.ts`.
- **CI**: lint, typecheck, unit tests, a schema-drift guard (`drizzle-kit generate`, then `git diff --exit-code` on the migrations folder) and a build with placeholder env values. Ref: `.github/workflows/ci.yml` and the `db:check` script in `package.json`.

## Dev-only playground

A `/dev/playground` route, allowed by the middleware only in development, that renders every primitive plus the real forms and tables with fixture data, without sign-in. It's the fastest way to check UI at every width, and it works when the operator's account can't be used. Ref: `app/dev/playground/` and the `/dev/` rule in `proxy.ts`.
