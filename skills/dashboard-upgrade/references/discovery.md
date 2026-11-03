# Phase 1: Discovery

Goal: know the operator's day and what is really broken before designing anything. End the phase with an honest rating, a phased plan and the owner's decisions, then continue.

## 1. Map the operator's day

- **Who and where**: who uses it, on which device, in what setting, how often, with which interruptions. In the reference: one instructor, on a phone at the studio door and between classes; partner billing at month end on a laptop.
- **Recurring jobs**: write each as "when …, I want to …, so that …", with how often and on which device. Check-in a client, sell a card, see today's sessions, invoice a partner, record a payment.
- **Their words**: what they call things ("cards", "sessions", "partners"). Use those words in the UI, not table names.
- **Sources**: the owner's notes and emails with the client (quotation, feature requests, complaints), the client's own reports, and what the data shows (which tables fill up, how many rows a day).
- Save a short persona note to project memory.

## 2. Audit every route and action

Start the dev server and sign in with the test account the owner allows, or use the dev-only playground. For each route, at 1440 and 390:

- **Actions**: does every button, menu item and form do something visible? Run `covered-controls.js` for dead menus and buttons under overlays.
- **Forms**: outside click, Escape and back with unsaved input; a decimal comma ("500,50"); empty optional fields (null vs empty string); validation messages a person can act on.
- **Lists**: phone layout (`overflow.js`), paging, sorting, and how many empty-state messages show at once.
- **Feedback**: `alert()` and `confirm()` calls, silent failures, console errors, a bare "Something went wrong".
- **Time**: dates computed on the server clock instead of the business time zone; "today" on the server.
- **Access**: who can sign in, and whether each server action checks the caller.

Then the code behind money and counts. Launch a read-only `Explore` agent in the background with a concrete brief, asking for file paths and a word limit:

- entities and relations, and the migrations versus the schema (in the reference, an enum value missing in production failed every payment)
- every server action: transaction use, row locks, idempotency (a double-tapped check-in wrote twice), what it returns on failure
- every money or credit calculation and where it lives (duplicates mean different numbers on different screens)
- time-zone handling, auth checks, third-party sync (calendar, contacts) and what happens when it fails
- dead code, unreachable screens, TODOs

## 3. Truth sources

- **The schema and the migrations** say what production really has.
- **Business rules come from the owner.** Write each one to memory as soon as they state or correct it. In the reference: one quote becomes one or many invoices over time, the portion is chosen per invoice by line quantities or by amount or percentage, and invoices never exceed the quote.
- **Never read the production database**, even read-only. Ask the owner for facts, or seed the local copy.

## 4. Rate it honestly

Score each axis from 1 to 10 with a one-line reason, now and after each round of work:

| Axis | The question |
| --- | --- |
| Design harmony | One identity, applied consistently: type scale, badges, spacing, danger states? |
| UI/UX | Can the operator finish each job without confusion, dead ends or lost input? |
| Fluidity | Does it feel quick and calm: motion, loading, no layout jumps? |
| Functionality | Are the numbers right and the actions reliable? |
| Practicality | Does it fit their day and their device? |

List what keeps each axis from 10; that list becomes the plan. Don't inflate: the owner relies on the honest number, and "about 4.5 before, 6 now" landed better than praise.

## 5. Plan and decisions

- **Phases**, in this order: production hotfixes, safety net (tests, CI, schema-drift guard, time zone, access), foundations, domain fixes (billing), promised extras, home and flows, polish, then a week of real use by the operator.
- **Decisions**: ask the ones that change the build with `AskUserQuestion`, once, with options. In the reference: a separate hotfix PR first? A language toggle? Which invoice a payment goes to first? A local database in Docker?
- Save the plan, the decisions and the scope (paid items and free extras) to project memory.
