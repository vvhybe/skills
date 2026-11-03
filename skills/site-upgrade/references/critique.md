# Phase 7b: Critique, scored

Passing the scripted checks means nothing broken was measured. It says nothing about whether the site is good. This file is how you find out, and the rule is simple: **you don't report the work as done until your own written critique scores it 9 or higher**, or your report says plainly what keeps it below.

Judge only screenshots, never the code. You wrote the code, so you will read your intentions into it. A problem visible in a screenshot is real, whatever the code says.

## Contents

1. How to look
2. The score
3. Caps
4. Writing a round
5. What to fix first
6. When to stop

## 1. How to look

Open the desktop screenshots first, then the phone ones. Make each pass on its own.

1. **One second, then five.** Glance and look away: what did you see? There should be one answer (an object, a word, an image). Then read the first screen for five seconds as a stranger: what is this, who is it for, what do I do next?
2. **Squint.** The page should reduce to two or three large masses with clear size differences. Many similar medium masses mean nothing leads.
3. **Cover the logo.** Could this first screen belong to a competitor? Then scroll: does the idea reach the pricing, the FAQ, the footer and the 404, or does the page turn into stock blocks after the hero?
4. **Edges.** Follow the left edge of every text block down the page. Two or three shared edges mean it was composed; six mean things were placed one at a time.
5. **Space and frame.** Related things close, unrelated things far; the gap between sections clearly larger than any gap inside one. Equal outer margins. No section with its text in one half and nothing in the other. No stretch of nothing taller than half a screen.
6. **Type.** A decisive jump from body to headline. Five sizes at most. Headlines within two lines at every width, no orphan word, no clipped descenders.
7. **Color.** Name the proportions: what holds most of the surface, what supports, where the accent is. Count the accent: on the primary action and one more thing, or everywhere?
8. **Product and pictures.** Is the product itself visible, as real UI or real output? Is every image doing a job? Any grey box, stretched image or fake screen made of bars?
9. **Sameness.** Write one word per section for its layout (split, full-bleed, list, demo, gallery, statement). The same word twice in a row is the template showing.
10. **Phone.** Its own composition with its own crops and line breaks, or the desktop squeezed? Does anything overlap (markers on the mascot, a progress bar on a heading)? Is every action reachable, the menu included?
11. **Substance.** Does each section deliver its information completely? Would a visitor leave knowing what they came to learn?
12. **Truth.** Is every claim on screen in the claims ledger as shipped? Any number without a source?
13. **Motion and states.** With reduced motion, is everything visible? Did any reveal leave a blank band? Do hover, focus, loading and error states exist and look designed?
14. **The contract.** Hold the build against the direction contract: does the first viewport match, did the signature land, are the brand exceptions the only tells?

## 2. The score

Four criteria, 1 to 10 each, weighted like an awards jury: **design 40%, usability 30%, creativity 20%, content 10%**.

- **Design:** composition, typography, color, imagery, craft. 9–10: every screen holds as a poster; nothing could be removed or moved. 7: clean and professional, little tension. 6: tidy but anonymous, reads as a kit.
- **Usability:** orientation in seconds, readable text, obvious actions, an honest phone version. 9–10: you know what it is and what to do without scrolling, flawless on a phone. 7: works, with one real problem.
- **Creativity:** an idea you can state in one sentence, carried through. 9–10: specific to this company and not seen applied this way. 7: a tasteful version of a known approach. 6 or less: the category default.
- **Content:** words and pictures that are specific, true and edited. 9–10: every line could only be about this company. 6 or less: slogans and filler.

`overall = 0.4 × design + 0.3 × usability + 0.2 × creativity + 0.1 × content`

For calibration, strong award-site winners land around 7.5 to 8.5 from a jury. A 9 from you means a stranger would call it the best site in its category. If your first score for your own work is 9, score it again as the juror who didn't build it.

## 3. Caps

These override the arithmetic.

- A claim that isn't in the ledger as shipped, or an invented number or testimonial: **overall ≤ 5**.
- A blank band where a reveal didn't fire, content clipped off screen, or horizontal scroll on a phone: **usability ≤ 5**.
- No clear title saying what this is on the first screen: **usability ≤ 6**.
- Anything covering a headline, a button or the mascot at any scroll position: **usability ≤ 6**.
- An action missing on phones (not in the bar, not in the menu): **usability ≤ 6**.
- The first screen could belong to a competitor: **creativity ≤ 6**.
- An unearned tell visible in a screenshot (tells.md): **overall ≤ 7**.
- The product never appears as real UI or real output: **design ≤ 7**.
- The same fade on every block, or a page that barely moves: **design ≤ 7**.
- Two or more mostly empty desktop screens, or running text small and grey: **design ≤ 6.5**.
- Any placeholder (grey box, lorem, "Image here"): **content ≤ 5**.

## 4. Writing a round

Write it down, in this shape (`assets/templates/critique-round.md`), so rounds compare:

```
ROUND n — <page>, <widths and themes looked at>
Seen in one second: …
Idea (one sentence): …
Live thing: …
Layout words by section: hero=… / …=… / …
Scores: design _ · usability _ · creativity _ · content _ → overall _._
Caps applied: …
Top three problems, most visible first, each with the screenshot and the fix:
1. …
2. …
3. …
```

Name problems the way a designer would to a colleague: "the supporting line starts 40 px left of the headline's edge", "the comparison is the third split layout in a row", "on the 390 shot the countdown markers sit on the mascot's visor". "Could be more polished" is not a finding.

## 5. What to fix first

Later items can't rescue earlier ones.

1. **Truth.** Anything unsourced comes off.
2. **The idea.** If the cover-the-logo pass fails, change the concept, not the details.
3. **Hierarchy.** One dominant thing per screen.
4. **Composition.** Shared edges, section spacing, variety between sections, holes.
5. **Typography.** Scale, line breaks, measure, leading.
6. **Imagery and product.** Replace weak pictures; show the real product.
7. **Color.** Proportion and accent discipline.
8. **Detail.** States, focus, small alignments, phone refinements.
9. **Motion.** Last.

When removing something leaves a gap, don't refill it with an ornament. Close the gap, enlarge what remains, or let the product or a field of color take the space.

## 6. When to stop

Up to three rounds: critique, fix the top three, re-run the checks, critique again. Stop early when a round finds nothing a stranger would notice and the score is 9 or more. If the third round still scores under 9, report the score honestly with the remaining problems and what it would take to fix them. Never round up.
