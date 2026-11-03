# Read mode: help centers, docs and changelogs

The visitor came to understand something. The page is first a document of its kind; the brand frames it. Distilled from a consumer app's help center built from scratch: around three dozen guides across six sections, grounded screen by screen in the shipped app.

## Contents

1. The rule: the brand owns the frame, not the column
2. Where it lives
3. Information architecture
4. Writing guides that are true
5. Components readers need
6. AI-ready docs
7. Getting the app
8. Feeding the app the same content
9. Versions, changelog and languages

## 1. The rule: the brand owns the frame, not the column

The frame is the header, the sidebar, the ground, the title and section openers, and the way callouts, tables and code are set. There the brand's palette, type and signature commit fully, so the help center could belong to no other product. The reading column inside stays calm: a reading face, real contrast, a 60 to 75 character measure, nothing moving behind the text.

- Bring the marketing site's color into the frame so the help center isn't plain white and grey, but keep contrast natural: tints and mid-tones, not a saturated color slammed against white.
- Icons per topic come from the **product's own icon library, in the product's own tones**, each topic with the icon the app uses for the same screen. A single indigo chip on every topic reads as "the average purple AI style".
- The 404 sits inside the docs chrome (with the sidebar) without stacking a second navbar. It can still be a signature: the product's own artifact saying "not found".
- A favicon that differs slightly from the main site's (an inverted or badged version) tells readers which tab is help.

## 2. Where it lives

- **Name.** A consumer product's help lives at `help.` (or `support.`); `docs.` reads as developer documentation. If you move hosts, redirect every old path to the same path on the new host (308).
- **Repo.** Its own repository when the docs framework needs different framework versions than the marketing site (a docs framework on the next major Next.js while the site is on the previous one).
- **Stack.** A docs framework (Fumadocs, Starlight, Nextra, Docusaurus) on a static export, hosted where the main site is, so it gets the same headers, previews and redirects. Preview hosts get `noindex`.
- **Links between them.** The marketing site links to guides through one helper that builds the URL and the UTM tags (`helpLink(path, campaign)`), from the navbar, the footer, the contact page and under FAQ answers ("Read the guide").

## 3. Information architecture

- Organize by what the reader is trying to do and by the app's own screens, not by feature list.
- Start "Getting started" the way large consumer apps do: how to download, install, update and uninstall the app.
- When both phone platforms share the same layout, write one set of guides ("your phone") rather than two.
- Every guide answers one question. Its title is that question's answer in a few words.
- Enforce front-matter limits at build time with a schema (zod): a title of at most about 40 characters, so it fits 60 with the site suffix; a description of 140 to 160.

## 4. Writing guides that are true

- **Know the app, not the feel.** Read the app's code at the release tag for every guide; relate each guide to a real screen. Use the real screenshots, named by screen.
- **Write what ships.** When a button only toasts "coming soon", or a tour or policy promises more than the app does, the guide describes what the app does. Raise the mismatch with the product team privately.
- Keep a style guide in the repo (CONTRIBUTING.md) so new guides match.

## 5. Components readers need

- **Inline glossary.** Hard or required terms (tax ID, unit price, unit of measure) become inline citations that open a short definition on hover or tap, with a link to the full entry, instead of a separate glossary page readers never visit.
- **"Was this helpful?"** on every guide, stored in a small database (a serverless SQL binding is enough). Add its retention to the privacy policy.
- **Callouts, steps and tables** in the framework's standard forms, styled by the brand.
- **Search** that indexes headings and body text.
- **Next and previous** at the end of every guide.

## 6. AI-ready docs

Readers increasingly ask an assistant first. Large docs sites expose:

- a Markdown version of every page (`/guide.md` or `?format=md`)
- `/llms.txt` listing the guides
- an MCP endpoint that serves search and pages to assistants
- an "Ask AI" entry point that answers from these pages

## 7. Getting the app

- Store badges styled like the marketing site's (real logos from the brand CDN, a store that isn't live yet greyed out as "Coming soon"), placed in the footer and the sidebar card rather than in every guide.
- In the download guide, a **QR code that is the link**, large, with the store's logo inside the code (media.md § 6), and platform tabs that open on the reader's own phone and remember the choice.

## 8. Feeding the app the same content

When the app wants in-app help ("Help & feedback" in settings), serve the same guides as a versioned JSON contract (`/api/app/v1/help.json`) generated from the docs content at build time. Treat its types as a contract: it only grows; a breaking change is a new version. The feedback endpoint must accept requests without an `Origin` header if native HTTP clients call it.

## 9. Versions, changelog and languages

- **Latest only** when the app nudges or forces updates: one set of guides, a line saying which version they describe, and an update guide. A version switcher is for products whose users stay on old versions.
- **The changelog** stays on the marketing site (building-blocks.md § Inner pages); the help center links to it.
- **Languages:** plan the folder structure for translation from the start, even if only one language ships.
