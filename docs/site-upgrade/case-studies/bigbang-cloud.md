# BigBang Cloud: one company, two complete directions

**bigbang.cloud** · a private cloud for companies' ERP systems (Sage, Odoo, SAP and others) · Persuade mode, B2B, French first

> Screenshots will be added here once the new site is live on its domain.

## The brief

After the InvoiceStamp upgrade, the same team asked for the company's own site: B2B, written for decision makers, about one promise. Companies shouldn't have to deal with servers, patches and backups; the company deals with that pain so they can focus on their business. The owner's starting thought: the logo is an astronaut, so play on that, and lose the yellow accent.

## The first pass was rejected

A light refresh came back with:

> "That's not the kind of spice I'm looking for. I want a full renovation, something creative. The colors are out of balance; we need color theory."

That reaction is now in the skill's feedback decoder: "full renovation" means a new direction from discovery onward, and "colors out of balance" is about proportion and temperature, not one hex value.

## Direction one: ground control

- **The idea.** *On this site, the astronaut in the logo becomes ground control: you fly the mission, we run ground control.*
- **Color theory.** A complementary pair taken from the logo: the helmet's warm cream against deep-space navy, in roughly 60/30/10 proportions, with each accent given one job. The yellow turned out to come from the template, not the brand.
- **A mascot from the logo.** Hand-built 3D approximations were rejected ("a cheap replica with a wide head"). The owner supplied their own Blender model of the helmet; the site renders that exact model, exported headless to glTF, with inward-facing faces fixed and only two soft eyes added on the visor.
- **A story.** The business as a rocket held down by chores, lifted to orbit by ground control; onboarding as a countdown.

## Direction two: corporate, with spices from the first

The owner then asked for something "more serious and corporate", inspired mostly by large infrastructure companies' sites, with the same content. It was built on its own branch so the two could be compared fairly. The owner kept two things from the first direction (the navy and the floating pill navbar) and later asked for the corporate theme "with spices from the old one". The first theme is archived on a branch, never deleted.

What the corporate direction added:

- **Problem-to-answer illustrations.** The owner found the first corporate pass "poor in illustrations of our clients' problems". The answer: the visitor's problems drift as noise over a jagged warning-colored line, cross into the brand's navy panel, and the line runs flat with a pill naming the fix. Blueprint frames and micro-labels as one system; the warning color only on problems; no figures inside the art.
- **A benefit you can picture:** "you get `yourcompany.bigbang.cloud`, and that's it".
- **A countdown you walk through.** T-3 to T-0 as a scroll, not tabs you can skip.
- **An honest comparison** with the hyperscalers: a variable bill as `$`, `$$`, `$$$` against one flat `$`; ticks against attention triangles.
- **Lead qualification.** The catalog of hosted systems uses real brand logos and leads to the contact form already filled with the chosen system. Booking a call happens in the site's own interface, over the scheduler's API, instead of an iframe.
- **A 404 that is a game.** A canvas singularity whose black hole is the 0 of "404"; hold the button and you fall in, ending in a big bang.

## Truth in B2B

Every figure on the new site had to trace to a source. Figures nobody could source yet stayed off, with components ready to show them later, and a fact-check form went to the people who could answer. Counts come from data (the catalog's length), and the company's name, address and phone match its public business profile everywhere.

## What it taught the skill

- Two directions, compared on branches, then merged and archived → [`direction.md`](../../../skills/site-upgrade/references/direction.md) § 7
- Color theory as a relationship, not a list → [`direction.md`](../../../skills/site-upgrade/references/direction.md) § 3
- When 3D earns its place, and why the owner's own model beats any approximation → [`three-d.md`](../../../skills/site-upgrade/references/three-d.md)
- B2B blocks: problem-to-answer art, honest comparison, catalog to prefilled lead, own booking UI → [`building-blocks.md`](../../../skills/site-upgrade/references/building-blocks.md)
- Static export plus a few Functions on Cloudflare Pages, a new hosting project with the old one kept for rollback → [`seo-standards.md`](../../../skills/site-upgrade/references/seo-standards.md) § 7
