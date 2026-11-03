# Phase 2: Direction

This file is what worked on shipped sites. If a design-direction skill is installed, load it too for range; this one stands on its own.

## Contents

1. Find the idea
2. One live thing
3. Palette by color theory
4. Type
5. Structure the page in acts
6. Signature moments
7. Two directions, when the owner is unsure
8. The direction contract
9. Copy

## 1. Find the idea

Write one sentence, and don't build until both blanks come from the subject inventory (discovery.md § 4):

> On this site, **[something only this company has]** becomes **[the device the site is built around]**.

From shipped work:

- **An invoicing app called InvoiceStamp:** the stamp in the name becomes an ink seal that slams onto a real A4 invoice in the hero, and stamps "SENT" on the contact form's success screen.
- **A private cloud company whose logo is an astronaut:** the astronaut becomes ground control. "You fly the mission; we run ground control." The helmet becomes a mascot that carries a prop for each service, and onboarding becomes a countdown from T-3 to liftoff.
- **That app's help center:** the app's own invoice becomes the 404 page (INV-0404 with a NOT FOUND stamp), and each topic wears the icon and tone the app itself uses for that screen.

**The competitor test.** Put the nearest competitor's name in the sentence. If it still works ("our cloud is fast and secure"), the idea belongs to the category, not the company: go back to the inventory. "Clean and modern" is not an idea.

## 2. One live thing

Give the site one thing the visitor can do with the real content, made from the idea:

- edit an invoice and watch the real A4 document change, totals tweening
- pick a system in the catalog and land on a contact form already filled in with it
- walk the onboarding countdown by scrolling, station by station

Rules: it uses real content, works with a thumb on a phone, never blocks reading, has a plain fallback, and it is one thing, not a playground.

## 3. Palette by color theory

- **Sample, then relate.** Sample the brand's own material and name 4 to 6 tokens. Then build a relationship between them rather than a list: one temperature contrast (a warm helmet cream against deep space navy is a complementary pair), and proportions near **60/30/10** (ground, support, accent).
- **Give accents jobs.** Reserve each accent for one meaning: an earth blue only for data, a flare red only for problems, the brand color on the primary action. An accent used in ten places means nothing.
- **"Colors out of balance"** from an owner is about proportion and temperature, not one hex value. Re-balance the fields before you swap colors.
- **Drop inherited colors.** A color that came from the template or an old wordmark PNG is not the brand.
- **Light or dark** comes from the brand material and the scene (who looks, where, in what light), not from the category. Alternate dark and light sections on purpose; a navbar that adapts to the section behind it makes the switches feel designed (building-blocks.md).
- **Contrast without forcing it.** Body text 4.5:1, large text 3:1. A deep brand color against pure white reads harsh and "forced": add tints and mid-tones between them.
- **Avoid the generated defaults** unless the brand owns them: indigo-to-violet gradients, cream with terracotta, near-black with a neon glow, single-hue icon chips everywhere ("the average purple AI style"). See tells.md.

Define the tokens once: `@theme` in Tailwind 4, `theme.extend.colors` in Tailwind 3, or CSS custom properties.

## 4. Type

- Keep the site's body face unless it is the problem. Add at most one accent face, and find it in the brand material (the reel's titles, the logo's lettering, the product UI).
- Check the face at display sizes before committing: a font whose "g" looks squashed and clipped at a tight line-height, or descenders cut off by a masked reveal, shows up only when rendered.
- Training-data default faces (Inter as a display face, Space Grotesk, Playfair Display, Fraunces, Instrument Sans, DM Sans, Outfit, Plus Jakarta Sans) need a reason beyond "it looks modern".
- Two or three sizes do the visible work: one very large, one small. Headlines stay within two lines at every width; do the arithmetic (about 32 characters is safe at a confident size) before falling in love with a sentence.
- Theme the browser surfaces from the palette: `::selection`, `caret-color`, `accent-color`, `scrollbar-color`, focus rings, `text-underline-offset`, and `font-variant-numeric: tabular-nums` wherever numbers align. It is the cheapest signal that a site was built rather than assembled.

## 5. Structure the page in acts

**Persuade (a product or marketing site):**

1. **Opening, cinematic.** The hero shows the product itself, real UI and real artifacts, with depth and one orchestrated intro. Make the seam into the next section invisible.
2. **Middle, hands-on.** Features as working micro-UI, an interactive demo of the core job, a gallery of real outputs, plans from the billing system.
3. **Finale.** One line in the brand's own voice, the store or sign-up actions, then a stable footer.

**Persuade (a company or B2B site):** speak to the visitor directly about their pain, then show the relief.

- Illustrate problem → answer, not features. A language that worked: the visitor's problems drift as noise over a jagged red line, cross into the brand's panel, and the line runs flat with a pill naming the fix. Blueprint frames with dashed outlines and corner marks, mono micro-labels, the warning color only on problems. No numbers, prices or SLAs inside the art.
- Comparisons stay honest and visual: a variable bill as `$`, `$$`, `$$$` against one flat `$`; green ticks against attention triangles; no invented figures.
- Make the benefit concrete: "you get `yourcompany.bigbang.cloud`, and that's it" lands harder than a list of services.
- The catalog's call to action carries what the visitor chose into the contact form (lead qualification).

**Read and Experience:** see read-mode.md and building-blocks.md § Experience.

Every section's composition differs from its neighbor's. Carry the idea into the pricing, the FAQ, the footer and the 404; the commonest failure is a distinctive first screen followed by stock blocks.

## 6. Signature moments

Spend boldness on one or two moments and keep the rest disciplined. Good places:

- the hero intro (a seal slam with a page jolt and an ink ring)
- the live thing
- the 404: a canvas singularity whose black hole is the 0 of "404", with the mascot orbiting it and a press-and-hold that ends in a big bang; or a NOT FOUND stamp landing on an invoice
- the contact form's success screen
- a console easter egg for the curious

Delight lives where people aren't working. Motion that answers the visitor beats motion that performs.

## 7. Two directions, when the owner is unsure

Owners sometimes ask for "something different" after a direction has shipped to a branch ("try something more serious and corporate, inspired by these sites"). Then:

- Build the alternative on its own branch from the same content, so the two compare fairly. Keep both previewable.
- From inspiration sites, take their discipline (an illustration language, a frame system, density, restraint), never their clothes.
- Keep what the owner says must stay. On the cloud company's corporate pass the owner kept the navy and the floating pill navbar from the first theme, and rejected a brighter blue.
- Expect a merge: "the corporate theme, with spices from the old one". List the old theme's best moments and port them deliberately.
- The chosen direction becomes the default branch. Archive the other on a named branch (`archive/<theme>`) with its own preview; never delete it.

## 8. The direction contract

Before code, fill `assets/templates/direction-contract.md` (about 150 words) in the scratchpad: thesis, idea sentence, own world, first viewport, signature moments, brand exceptions, and which ledger claims each section carries. Sketch the acts as ASCII wireframes. Show the owner the contract and the sketch, not a mood board.

Never copy the contract into shipped source, comments or data attributes. The critique (phase 7) audits the build against it.

Ask of every part of the plan: would this appear on any similar site? If yes, replace it with something specific to this brand, then build.

## 9. Copy

- Plain, specific and verifiable. Sentence case. Active verbs. A call to action says what happens ("Download on the App Store", "Book a 30-minute call"), never "Get started" or "Learn more".
- Use the brand's own lines (reel captions, taglines) where they fit.
- B2B: speak to the reader about their situation in their words, and build trust with specifics, not badges.
- When the audience is everyone, link hard terms to an explanation: a customer-facing changelog links "Liquid Glass" to Apple's page; a help center explains "tax ID" inline.
- No genre verbs (unlock, supercharge, seamless, elevate, effortless, cutting-edge, all-in-one), no "not just X, it's Y", no middle-dot meta strings, no tiny uppercase eyebrow above every heading, no `→` tacked onto link text.
- Keywords stay platform-neutral when the product is on several platforms ("invoice maker app", not "invoice app for iPhone") until each platform is live.
