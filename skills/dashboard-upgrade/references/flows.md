# Phase 4: Flows

Goal: each recurring job from discovery takes the fewest steps on the operator's device, and the next step is always obvious.

## Home is their day

- **Greeting and now**: their name from the sign-in profile, the time of day in the business time zone, and what's next ("Vinyasa in 20 min, 6 booked"). Ref: `components/dashboard/greeting.tsx`, `components/dashboard/day-period-icon.tsx`, `lib/utils/user.ts`.
- **Needs you**: items that each resolve with one tap: cards expiring this week, overdue invoices, unpaid balances, health notes for today's attendees, a calendar sync that failed. When there are none, a calm "all clear".
- **No KPI tiles for their own sake.** A number earns its place only if it changes what they do today.

## Core loops

Walk each job on a phone and count taps and screens. Then fix:

- **Entry points**: reachable from where they already are (home, the client, the session), not only from a menu.
- **Defaults**: today's date, the obvious client, the remaining amount.
- **One name through the flow**: the "Record payment" button opens "Record payment" and ends with "Payment recorded".
- **Show the result where they look next**, such as the new balance on the card, not only in a toast.
- **Reverse, don't just delete**: anything that moves money or credits gets a reversal that keeps the history.

## History

- Schedules and logs need the past, not only the coming week: a full list with filters and "show earlier".
- Relative dates where they help ("in 20 min", "yesterday"); absolute dates in the business time zone where precision matters (invoices, receipts).

## Money flows

- **Model the rule the owner states**, not a textbook one. In the reference: one quote, then one or many invoices over time; the portion is chosen per invoice, by line quantities or by amount or percentage.
- **Show the running state** on the parent document: billed so far and remaining.
- **Enforce the limits on the server**: refuse an invoice that would go over the quote, not just warn in the form.
- **Payments**: the owner's allocation rule (in the reference: the viewed invoice first, the excess to the others, oldest first). Show the split before confirming.
- **The same "amount due" everywhere**, from the domain module.

## Navigation

- Group by their workflow (Today, Clients, Schedule, Billing), not by database tables.
- On phones, the menu closes on navigation and the main action sits within thumb reach.

## Words and language

- Their vocabulary everywhere. If they're bilingual, offer one language toggle (cookie-based); generated documents use the language their clients and the law need.
- An error says what happened and what to do next. It doesn't apologize and never stops at "Something went wrong".

## Sign-in and connected services

- An allowlist of who may sign in, in code, even when the OAuth app is restricted.
- When a connected service's access lapses (an expired Google token), show a reconnect banner instead of silently redirecting to the login page. After sign-in, return them to the page they were on.
- Google OAuth in testing mode expires refresh tokens after 7 days. Whether to publish the app is the owner's decision; the reference stayed in testing mode until the whole epic was verified.
