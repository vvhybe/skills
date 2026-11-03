# Feedback: what owners say, and what to change

An operator judges a dashboard by their own day: did the payment save, did the form keep what they typed, can they find the client between two classes. Their words are short and rarely in design terms. These are real reactions from the reference epic, what they turned out to mean, and what fixed them. Read this whenever the owner reacts, and save new reactions to memory first.

## Contents

1. The decoder
2. How owners like to work
3. What owners approved

## 1. The decoder

| The owner says | It means | Do |
| --- | --- | --- |
| "Not generic." | Category defaults: KPI tiles, "Welcome back, Admin", settings nobody uses. | Back to the operator's day (discovery.md): their words, their tasks in their order, a greeting by their own name and the time of day. |
| "Something WOW." | One moment worth showing someone, not decoration everywhere. | One signature scene where the operator isn't working: sign-in, the greeting, empty and error screens (design-direction.md). |
| "It's jerky." | Motion that performs (a 3D flip) where a calm one answers. | Sheets that slide, short eased transitions, motion that shows what changed. |
| "We need icons here." | A label and value list reads as a form dump; the eye can't find a row. | One icon per row from the app's icon set, same size and tone, aligned on a column; values keep the weight. |
| "I lost what I typed." | Create or edit lives in a dialog that closes on an outside click. | The shared form sheet that asks before discarding (foundations.md § Create and edit). |
| "The button does nothing." | A dead action: a covered trigger, a swallowed error, a missing toast. | Run `covered-controls.js`; every action answers with success or a coded failure (foundations.md § Feedback and errors). |
| "Why does it say something else here?" | Two screens compute the same figure differently. | One domain module per number, used everywhere (foundations.md § Data and money). |
| "I can't use it on my phone." | The desktop table squeezed. | Phone-ready lists with row actions in a drawer; `tap-targets.js` and `overflow.js` at 390 and 320. |
| "Is it done?" | They want a status, not a wall of text. | Three lines: what's live, what's left, what needs them. |

## 2. How owners like to work

- **A plan before code.** The phased plan from discovery, with the owner's decisions asked once, with options.
- **A hotfix first when production is broken,** as its own small PR; everything else on one epic PR, verified as a whole before production.
- **Honest ratings** on five axes (design harmony, UI and UX, fluidity, functionality, practicality), each with the concrete path to 10/10.
- **Never "done" below 9/10.** The owner noticed self-ratings of 6 or 7 offered only after calling work done. Score before saying it, from screenshots at phone and desktop widths, and fix what costs points (SKILL.md rule 9).
- **"No work, just save it."** When the owner sends feedback this way, save it to memory and stop.

## 3. What owners approved

- **Forms in sheets on desktop and drawers on phones,** never dialogs. The sheets were praised by name.
- **Toasts that carry an error code** matching a server log line, and a report action the operator can send to the developer.
- **A coherent icon set** (iconsax in the reference) used at one size and stroke across the app.
- **Animated components only where they behave.** In the reference, animate-ui's DropdownMenu broke hydration and its Dialog flip was jerky; the plain versions stayed.
- **A signature scene from the brand:** a lotus pond at dawn, from the logo's own petals, on the sign-in and error screens.
- **The greeting:** the operator's Google first name and the part of the day, in the business's time zone.
