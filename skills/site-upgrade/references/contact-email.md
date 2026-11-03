# Phase 5: Contact, booking and the team email

A contact form that doesn't deliver is worse than none. This phase makes the form truthful, bot-resistant and pleasant for the team that receives it.

## Contents

1. Shared data and validation
2. The form
3. The route
4. Sending (Cloudflare Email Service by default)
5. The designed notification email
6. Bot protection
7. Booking and lead qualification
8. Verify

## 1. Shared data and validation

One module holds:

- the contact details, exactly as published in the privacy policy and the business profile
- the topics
- **one fixed subject per topic**, all starting with `Website:` (for example `Website: Billing & plans`), so inbox filters work
- one `validateContact()` that both the form and the route call (or one schema, if the repo uses zod)
- the allowed values for anything prefilled from the URL (catalog slugs)

## 2. The form

- Topic chips (radio inputs), name, email, and a message with a counter. A field prefilled from the page the visitor came from (`?system=<slug>`, `?topic=quote`) shows what was prefilled and can be changed.
- Errors appear after the first submit, then update live as the visitor types; focus moves to the first invalid field; each error is tied to its field with `aria-describedby`.
- A honeypot field off screen (`aria-hidden`, `tabIndex={-1}`, `autocomplete="off"`) and a timestamp taken when the form mounts.
- States:
  - **sending:** a spinner in the button, the form locked
  - **sent:** a branded success screen; the brand's signature device fits here (an invoicing app stamped "SENT")
  - **503 not configured:** open `mailto:` with the message prefilled, so the site works before email is set up
  - **failed:** a "send it from your email app" link with the message prefilled
- A one-line privacy note linking to the policy. No consent checkbox for a contact form.
- Mask the form in session-replay analytics (`data-clarity-mask` for Microsoft Clarity, or the tool's equivalent).

## 3. The route

- An edge or serverless route (`/api/contact`), or a Pages Function on a static export.
- **Bots:** honeypot filled, or submitted less than about 2.5 s after the form mounted, gets `200 { ok: true }`, so bots learn nothing.
- **Invalid input:** `422` with field errors.
- **Not configured:** `503 { error: 'not_configured' }`.
- **Turnstile** (or the bot check in use) is verified server-side before sending; the route fails closed (503) when its secret is missing.
- Escape every visitor value that goes into HTML. Never put visitor input into `dangerouslySetInnerHTML`.

## 4. Sending (Cloudflare Email Service by default)

Use Cloudflare Email Service when the domain is on Cloudflare DNS. Otherwise ask the owner which provider to use: it is a new data processor and belongs in the privacy policy. If a `cloudflare-email-service` skill is installed, load it for the current API.

- **Endpoint:** `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/email/sending/send` with `Authorization: Bearer <token>`.
- **Body:**
  - `from: { address, name }`: the REST API takes `address`, not `email`
  - `reply_to` (snake case): the visitor, so a plain Reply reaches them
  - `subject`, `html`, `text`
  - `attachments` for inline images
  - `headers: { 'X-Entity-Ref-ID': <unique> }`; fixed subjects otherwise make Gmail thread every message into one conversation
- **Environment variables** (values, not switches): `CF_EMAIL_ACCOUNT_ID`, `CF_EMAIL_API_TOKEN` (a secret), `CONTACT_FROM_EMAIL` (an address on the onboarded domain), `CONTACT_TO_EMAIL` (optional; point it at an inbox the owner can read while testing).
- **Owner setup:**
  1. `npx wrangler email sending enable <domain>`; Cloudflare adds the SPF, DKIM, DMARC and bounce records.
  2. Create an API token: My Profile → API Tokens → Create Custom Token → **Account › Email Sending › Edit** (not the zone-level "Email Routing Rules").
  3. Add the variables to the hosting project and redeploy.
- A `success: true` response with the recipient under `queued` is normal: accepted and on its way.

## 5. The designed notification email

- **Components:** install the individual `@react-email/*` component packages (html, head, body, container, section, row, column, text, heading, button, link, img, hr, preview). Not `@react-email/components` and not `@react-email/render`: render's edge build imports prettier and html-to-text, which bloats the worker.
- **Rendering:** Next route handlers run on React's server build, where `react-dom/server` crashes ("Cannot set properties of undefined (setting 'recentlyCreatedOwnerStacks')"). Render with `assets/render-email.ts`, a small static renderer; the React Email components are plain `forwardRef`s with no hooks.
- **Layout:**
  - a header band in the brand's colors, with the app icon, a topic pill and "New message from *First name*"
  - a sender card with initials and the signature-device image
  - the message in a quote block, keeping line breaks
  - a primary "Reply to First name" button (a `mailto:` with a friendly subject)
  - a triage panel: topic, the prefilled choice, time in the team's time zone, country (from the `cf-ipcountry` header through `Intl.DisplayNames`), browser language, a rough device guess and a reference like `WEB-XXXXXXXX`
  - a footer that explains the subject convention
- **Head:** `<meta name="color-scheme" content="light only">`; web fonts in a `<link>` (Apple Mail loads them) with web-safe fallbacks.
- **Images:** inline CID attachments (`content` as base64, `disposition: 'inline'`, `content_id`), each under about 12 KB (media.md § 7). They show before the site is deployed, and Outlook doesn't block them.
- **Always** send a plain-text alternative.
- **A dev-only preview route** (`/api/contact/preview?topic=…`) renders sample data with images as normal URLs and returns 404 in production.
- **BIMI:** publish an SVG Tiny PS logo (`/bimi/logo.svg`) so the brand mark can show next to the sender. The DNS record and DMARC enforcement are the owner's steps; tell them.

## 6. Bot protection

Cloudflare Turnstile (managed, invisible) fits most sites. Widget domains include production, previews and localhost. The site key is a public env value; the secret is a secret. The server checks the token and the hostname. Headless browsers never get a token on production hosts, so end-to-end tests there need a real browser; on localhost tokens are issued. If a `turnstile-spin` skill is installed, use it.

## 7. Booking and lead qualification

- **Lead prefill.** Catalog and pricing actions link to the contact page with the choice in the URL (`/contact?system=sage-x3`). The form validates the value against the catalog, preselects the topic and shows it. The email's triage panel repeats it.
- **Contact or call.** Let the visitor choose between writing and booking a call on the same page.
- **Own booking UI.** Proxy the scheduler's public API through your route and build the picker in the site's design (building-blocks.md § Own booking UI). Show the time zone; derive offsets with `Intl` from an IANA zone.

## 8. Verify

- Call the route directly for every branch: 422, too fast, honeypot, missing bot token, 503.
- Fake 200, 502 and 503 responses with Playwright `page.route` to see the success, failure and fallback screens.
- Send **one** real, clearly labeled test to an inbox the owner can read, only when they've asked for it.
