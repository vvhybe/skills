# Phase 1: Discovery

Goal: know what the company or product really is before designing anything. End the phase with a short findings report to the owner (problems, opportunities, truth gaps, the direction you propose), then continue unless they redirect.

## Contents

1. Audit the current site
2. Find the truth sources
3. Write the claims ledger
4. Build the subject inventory
5. Collect brand material
6. Report

## 1. Audit the current site

- Start the dev server and note the actual port (`pnpm dev`, `yarn dev`, `npm run dev`). If 3000 is taken, Next picks 3001; the owner often has their own server running, so leave it alone.
- Capture the **before** set as verification.md § 1 describes (reveal-scroll first: template reveals leave content invisible until scrolled).
- Run `scripts/playwright/overflow.js` and `scripts/playwright/page-audit.js` on each page. Fanned or rotated cards in fixed-width boxes are the usual cause of horizontal scroll on phones.
- Run `node <skill>/scripts/slop-scan.mjs src` for a baseline of tells, dead links and invented proof.
- Build for production and run `scripts/ssr-audit.sh` against the production server. Template layouts often wrap everything in `<Suspense>` around `useSearchParams()`, so every page ships "Loading..." HTML (see gotchas.md).
- List what is wrong:
  - dead links left over from the template (`/features-01`, `href="#"`)
  - placeholder or fabricated social proof ("Join thousands…", fake ratings, a logo wall, "#1 private cloud")
  - free trials, newsletters and plans that don't exist
  - forms that post nowhere
  - stock gradients, 3D blobs, icon-card grids
  - the old accent color: check whether it came from the brand or from the template it was built on. A template's yellow is not a brand color.
  - unused template pages, components and images

## 2. Find the truth sources

Ask the owner where these live if they aren't obvious.

- **Product source code.** Launch a read-only exploration agent in the background with a concrete brief and a word limit, asking for file paths with every answer:
  - stack and platforms; what the product does (for an app: the document types and what converts into what)
  - customization options and the brand palette and fonts
  - calculations, limits and counts, with the data file each count comes from
  - sharing and export; data model entities; payments and status tracking
  - monetization tiers and what is gated
  - languages, offline support and sign-in
  - reusable visual assets with paths and dimensions; distinctive delights
  - and, explicitly: **what is unfinished, behind a flag or unreachable, and where the product's own copy overpromises**
- **Release history.** Git tags, the CHANGELOG and milestones give a truthful changelog page. Check the live store listing for versions and dates (for the App Store: `https://itunes.apple.com/lookup?id=<id>`).
- **Legal documents** (privacy policy, terms): legal entity, address, emails, data practices, retention, subscription, refund and cancellation rules. They are the authority for FAQ answers. Note where they conflict with what the product does; flag it, don't paper over it.
- **Pricing** comes from the billing system at build time (RevenueCat, Stripe, Paddle), never typed into the page. Quote the base price the owner sets, not one storefront's localized price, and say that the store shows the visitor's own price.
- **Name, address and phone.** A public business profile (Google Business Profile) is usually the authority. Keep them identical in the contact data, the JSON-LD and the profile.
- **Launch status and availability.** Confirm with the owner and the live listing, not with env flags. A store button for a store that isn't live is greyed out as "Coming soon".
- **No product code?** A services company, a studio or a shop has no repo to read. Then the truth sources are the owner's written answers, contracts and brochures, the legal documents, the public business profile, real invoices or menus, and photographs of the real place and work. The fact-check form (§ 3) becomes the main tool rather than the fallback.
- **Proprietary assets** (templates, designs, datasets): find out what may be published and at what size before you put any of it on a public site (media.md § Protecting proprietary assets).

## 3. Write the claims ledger

Copy `assets/templates/claims-ledger.md` into the scratchpad and fill it as you read. Four lists:

- **Shipped**: what you may market, each with its source file or document.
- **Not shipped**: never market. Features behind flags; screens nothing links to; buttons that only toast "coming soon"; roadmap items; the paywall's promises the code doesn't keep.
- **Unknown**: claims the old site made that nobody can source (SLA, uptime, data-center count, customer numbers). Take them off the site. Build their components so the figure is optional and can return later without a redesign.
- **Numbers**: each figure with the file it comes from. Import counts from data ("17 systems" is `systems.length`), never type them.

When the owner doesn't know the answers, someone else in the company does. Build them a **fact-check form**: one question per claim, with the current wording, a few answer options and a free-text field, plus a sign-off. A shared doc or a small form page works; collect the answers before publishing those claims. Save durable facts to memory: what's shipped, what isn't, launch status, and decisions such as "paid only, never say free".

## 4. Build the subject inventory

List eight to twelve things that belong to this company and no competitor. The idea for the design comes from this list (direction.md), and so do the picture searches and the copy.

- **The name** and what it means. A stamp, a big bang, a lighthouse.
- **The logo's shape.** An astronaut helmet is a character waiting to happen.
- **The output.** What the product produces, as a real artifact: an A4 invoice, a rendered PDF template, a deployed subdomain address.
- **The ritual.** A sequence the visitor can walk through: an onboarding countdown, a provisioning flow, the steps from quote to paid.
- **The place.** City, street, light, materials, the time zone the team works in.
- **The customers' pain in their words.** Servers, patches, backups; chasing invoices on a phone.
- **The numbers** from the ledger.
- **The constraint** it lives with: by appointment only, one batch a month, a single platform at launch.
- **The printed things of its world:** a receipt, a ticket, a stamp, a mission patch.

## 5. Collect brand material

- **Videos.** Run `scripts/video-prep.sh`. Study the contact sheet for palette, typography (an italic serif accent word in a product reel can become the site's accent face), story structure and scene cuts.
- **Brand colors.** Sample frames and logos with PIL (`Image.getpixel` at a few points per frame); name 4 to 6 candidates.
- **Rendered product artifacts.** Real exports, real templates, mockups. These usually make the strongest pictures on the site.
- **App screenshots.** When a release brings a new set of captures, map each file to its screen name by downscaled pixel difference against an already-named set instead of guessing; a difference of 0 to 1 is the match.
- **Logo layers.** Foreground and background PNGs make a proper maskable icon; an SVG logo serves BIMI and favicons.
- **3D and character sources.** Before building a mascot or a 3D object, ask whether the owner has a source model (`.blend`, `.glb`, `.fbx`). Owners reject approximations of their own brand (three-d.md).
- **Inspiration the owner names.** Study what those sites do well (an illustration language, a frame system, density, tone), not their look. Write down what transfers.

## 6. Report

Before the big build, tell the owner in a few lines:

- what's broken on the site now
- what's inaccurate, and what you will remove until it is sourced
- which assets you found, and which you still need
- your proposed direction, in one or two sentences and a rough sketch of the home page's acts

Then proceed unless they redirect. Questions that block nothing ride along with options; they don't stop the build.
