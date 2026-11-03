# Feedback: what owners say, and what to change

Owners rarely speak in design terms. They say "not enough spice" or "it looks cheap", and the fix is almost never what the words suggest at first. These are real reactions from shipped upgrades, what they turned out to mean, and what fixed them. Read this whenever the owner reacts, and save new reactions to memory.

## Contents

1. The decoder
2. How owners like to work
3. What owners approved

## 1. The decoder

| The owner says | It means | Do |
| --- | --- | --- |
| "Not enough spice. It's just 'we added a video'." | The change is an addition, not an upgrade. The site still doesn't show off the product. | More product, more interaction, more depth: a live demo, real artifacts, a story that moves. Not more decoration. |
| "It feels like PowerPoint, not a website." | Stacked centered blocks that each fade in. | Composition: pinned stories, layered depth, interactive demos, state-driven motion (motion.md). |
| "I want #upgrade, not #update." | A plain label where a crafted moment belongs. | Turn the call to action into a moment: a live preview capsule with a progress ring and chapter captions instead of "Watch in 23 seconds". |
| "Not the kind of spice I'm looking for. I want a full renovation." | A light-touch pass was offered for a request that wanted a new direction. | Start from discovery and the idea sentence again; propose a whole direction, palette to mascot. |
| "The colors are out of balance. We need color theory." | Proportion and temperature are off, not one hex. | A temperature contrast (complementary warm against cool) and 60/30/10 proportions; accents with single jobs (direction.md § 3). |
| "All indigo is boring, the average purple AI style." | One generated hue everywhere. | The product's own palette and icon tones, varied per topic. |
| "The contrast looks forced." | A saturated brand color slammed against white. | Tints and mid-tones between them; keep contrast natural. |
| "It's a cheap replica with a wide head." | An approximation of the brand's own mark. | Get the source asset (the owner's model) and pass the exactness gate (three-d.md). |
| "You used a cheap trick." | A shortcut that looks like the real thing at a glance (a logo pasted over a QR code). | Do it properly (media.md § 6), or ask for the asset you need. |
| "This is a dull, flat display." | Numbers or facts set as plain text in a row. | Make them a designed moment: floating cards that count up, with real swatches or icons. |
| "Templates aren't a background for your data; each has its own personality." | The differentiator is shown as an image gallery. | Spotlight behavior: group items by what they do, from their own descriptions (building-blocks.md § Spotlighting). |
| "That language switch hanging there is awful." | A default control in a crafted page. | A segmented `FR \| EN` control that belongs to the design. |
| "It's jerky." | Motion that performs (a 3D flip) where a calm one answers. | Sheets that slide, short eased transitions; motion that shows what changed. |
| "The illustration looks smaller on mobile; it could take the full screen." | The phone version is the desktop squeezed. | Give the phone its own composition: full-bleed art, its own crop. |
| "Poor in illustrations of our clients' problems." | The site lists services; it doesn't show the visitor's situation. | Problem-to-answer illustrations (building-blocks.md § Company and B2B). |
| "We should speak directly to them." | The copy talks about the company. | Second person, the visitor's pains in their words, then the relief. |
| "Not generic." | Category defaults. | Back to the subject inventory: the owner's words, their name, their place. |
| "I don't have those numbers now, but we can add them later." | Unknown, not zero. | Remove the figure, make the component accept an empty value, and send a fact-check form. |
| "Why add them as secrets? They're links." | Over-engineering public config. | Public values are plain env values; only real secrets are secrets. |
| "Make it an env, to make things standard." | A boolean switch or a hardcoded constant. | An env var that holds the value (a URL); empty means off (a greyed "Coming soon"). |

## 2. How owners like to work

- **Iterations, home page first.** "Let's focus on the home page for now; once we're good, you can do the other pages."
- **A plan before code** on big moves; a short status ("where are we now?") on request, without a wall of text.
- **One question at a time, with options.** Owners answer numbered questions quickly ("1: yes, 2: leave it open, 3: me").
- **A second direction on its own branch** when they want to compare, and the losing one archived, never deleted.
- **Short, paste-ready updates** for the team after each PR, and a living before/after report when a boss is watching.
- **Stacked PRs** for separable work (the redesign, then SEO), and a merge order when there are several.
- **Their consent is specific.** "Push and open PRs" is not "merge" and not "change the domain". Ask for each new kind of outward step.
- **Explanations for them only** when they ask how something works ("elaborate for me so I can follow along"): plain, short, no jargon.

## 3. What owners approved

- A real A4 invoice as the demo, instead of an abstract "math done" section.
- Story progress bars of equal length that advance on their own when the visitor lingers.
- Ambient video muted and looping.
- FAQ and Contact in the navbar; a stable footer on every page; a contact form that really delivers, with fixed `Website:` subjects and a designed email.
- The SEO and standards work as a separate stacked PR.
- A countdown the visitor walks through by scrolling, instead of tabs they can skip.
- A catalog of real brand logos that leads to a prefilled contact form.
- A 404 that is a game (a singularity, a press-and-hold big bang) or a joke in the product's own language (a NOT FOUND stamp on an invoice).
- A corporate direction inspired by large infrastructure sites, with the first direction's best moments kept.
- A help center that relates every guide to a real screen, in the app's own icons and tones.
