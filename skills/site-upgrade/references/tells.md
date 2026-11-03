# Tells: what makes a site read as generated

A tell is a device that makes a site read as assembled by default. Most began as good ideas on good sites and became tells by being produced everywhere without a reason. This registry is dated (2023 to 2026) and names replacements as procedures, never as a font, a color or a component, because every published "use this instead" list became the next wave of tells.

`scripts/slop-scan.mjs` finds the ones the source shows. `scripts/playwright/page-audit.js` measures some of the rest. The critique (critique.md) catches what only a screenshot shows.

## The exception rule

Here a tell is a default to refuse, not a law. It is **earned** when the brand's own material or the owner's explicit choice puts it on the page, and the direction contract names it with the reason. Examples from shipped sites:

- An italic serif accent word in headlines, because the product's own reel used one.
- A floating pill navbar, because the owner kept it as a signature from the previous theme.
- Hairline blueprint frames, corner marks and mono micro-labels, as one system for an infrastructure company, used where they carry structure.
- T-3, T-2, T-1, T-0 numbering, because the countdown is the content.

To name an earned tell for the scanner, put `site-upgrade-allow: <rule> <reason>` in a comment; it covers its own line and the lines after it up to the next blank line. For a repo-wide exception, add `<rule> <reason>` to a `.site-upgrade-allow` file at the root. Rule ids (`node <skill>/scripts/slop-scan.mjs --list-rules`): `gradient-text`, `violet-gradient`, `glow`, `glass`, `eyebrow`, `numbered-sections`, `emoji-icon`, `decorative-pulse`, `transition-all`, `layout-tween`, `bounce-ease`, `invented-proof`, `fake-people`, `unsourced-uptime`, `placeholder`, `genre-copy`, `vague-cta`, `not-just`, `middot-meta`, `dead-link`, `img-no-alt`, `clarity-id`, `search-params-layout`, `boolean-env`, `secret`, `env-committed`, `reduced-motion`.

## Palette and surface

| Tell | Instead |
| --- | --- |
| Indigo or violet gradients on the hero, buttons and glows | The brand's sampled palette, mostly flat |
| Gradient-filled headline text | Solid ink; emphasis from size or weight |
| Glowing or gradient "Get started" button | A flat button named for its action |
| Cream ground with a terracotta, rust or clay accent and a serif display face (the "warm editorial" fix that became the look) | Warmth from the brand's own material, a photograph or a full field of color |
| Near-black ground with one neon accent and a glow | A dark palette from the brand, no glow |
| Glass panels and backdrop blur as decoration | Opaque surfaces one tone step from the ground; blur only for a specific effect |
| Soft grey shadow under every card | A tone step between surfaces; shadows only on what floats |
| One hue on every icon chip | The product's own icon set and tones |
| Browser defaults untouched (selection, scrollbar, caret, focus ring, underline offset) | Themed from the palette |

## Structure

| Tell | Instead |
| --- | --- |
| Hero, logo wall, three features, testimonial, pricing, call to action, in that order | The order of the argument: claims and their proof |
| Three identical feature cards, each with an icon in a rounded square | Working micro-UI, a composed section, the real artifact |
| A bento of identical rounded tiles | Tiles that vary in span and ground, each a live piece of the product |
| A fake dashboard of grey bars and donut charts | A real interface fragment built in HTML, or nothing |
| The hero-metric template: big number, small label, three stats | Numbers inside the content they describe, with a source |
| Tiny tracked uppercase eyebrow above every heading | Fold it into the heading or delete it |
| Pill badge above the headline ("New", "Introducing") | Say it in the supporting sentence |
| 01 / 02 / 03 section numbering | Order shown by position, scale or the words; a real `<ol>` when it is a list |
| Every section centered | Left-anchored by default, one centered moment |
| Every section the same layout family | A different composition from each neighbor |
| A distinctive first screen followed by stock blocks | The idea carried into pricing, FAQ, footer and 404 |
| Emoji or Unicode glyphs as icons | One drawn icon library, one stroke and weight |
| Colored side-stripe borders on cards and alerts | A tone step or nothing |
| A modal for a task that needs no interruption | Inline, a sheet or its own page |

## Motion

| Tell | Instead |
| --- | --- |
| The same fade-up on every section | One choreographed intro and state-driven moments |
| A dozen staggered hero entrances | One timeline with a clear peak |
| Hover lift on every card | Feedback where it means something |
| Ambient loops everywhere | One moving picture with a purpose and a pause control |
| A reveal that fails and leaves a blank band | Content visible by default; motion enhances |
| Bounce easing | Exponential ease-out |

## Copy and proof

| Tell | Instead |
| --- | --- |
| "Join thousands of happy customers", star rows, "Trusted by" logo walls, "#1", "10,000+ teams" | Real proof with a source, or none |
| Invented testimonials (John Doe, Acme Inc.) | None until real ones exist |
| Unsourced uptime, SLA or data-center counts | Removed until signed off; the component accepts an empty value |
| Free trials or plans that don't exist | What billing actually sells |
| Genre verbs: unlock, supercharge, seamless, elevate, effortless, cutting-edge, all-in-one | Plain verbs about what happens |
| "Not just X, it's Y"; tricolon headlines | One concrete claim |
| "Get started" and "Learn more" | The action's real name |
| Middle-dot meta strings ("Fast · Secure · Simple") | A sentence |
| Lorem ipsum, "Image here", grey placeholder boxes | Real content, or the section waits |

## Why removing tells is not enough

A page with every tell removed and nothing in their place is empty with good manners, and that reads as generated too: anyone could guess it from the category plus the list of things to avoid. The tells were filling the gap where an idea should have been. Fill it first, with the idea, the product, the real content, scale, and a field of color. Then remove what's left.
