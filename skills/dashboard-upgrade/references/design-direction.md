# Phase 5: Spice

If a design-direction skill is installed, load it first; this file is what worked in a working tool. In a dashboard, most of the spice is discipline: one identity applied everywhere, plus one or two memorable moments where the operator isn't working.

## Identity

- **Palette**: take it from the brand (logo, place, existing tokens) and name 4 to 6 tokens in `@theme`, with dark-mode values. In the reference: teal from the logo text, blush from the lotus petals, warm stone backgrounds.
- **Type scale**: one scale for page title, section, body and caption, used everywhere. Remove 9 to 10 px all-caps labels: unreadable on a phone. Nothing below 12 px (`tap-targets.js` reports it).
- **Statuses**: one badge system (paid, unpaid, partly paid, overdue look the same on every screen) and one danger treatment.
- **Icons**: one set and one rule for weights. The reference uses `iconsax-reactjs`: the default style for UI, `Bold` for primary actions.

## Motion

- **Answer their actions**: a sheet slides in, a row updates, a toast changes state. Ease-out `cubic-bezier(0.16, 1, 0.3, 1)`, 150 to 300 ms, closing faster than opening.
- **Never** 3D flips, springy overshoot on dialogs, or anything that delays a tap.
- **Ambient motion only where they aren't working**: sign-in, error, not-found and empty screens, and the greeting.
- **Reduced motion**: final states and still scenes; `document.getAnimations().length` should be 0 for decorative scenes.

## Signature moments (pick one or two)

- **A greeting** with an animated time-of-day icon (rising sun, moon) drawn in the brand's style.
- **A backdrop scene** for the sign-in, error and not-found screens, taken from the brand's world. The reference's is a lotus pond at dawn: a bloom on a lily pad sending out rings, petals tumbling in 3D at three depths, light glinting on the water, breathing dawn light. It has its own light and dark palette so the lotus glows at night, a deterministic layout (no hydration mismatch), transform and opacity only, and a still, composed pond under reduced motion. Ref: `components/ui/lotus-pond.tsx` and the "Lotus pond" block in `app/globals.css`.
- **An empty state** that invites the first action.

Never reuse the lotus, the pond or the yoga palette on another brand: find that brand's own scene.

## Libraries

- **shadcn**: diff the local components against the registry before "updating"; keep local fixes. Add upstream extras only when a screen needs them.
- **animate-ui**: adopt it per component and pin the version (its licence is MIT plus Commons Clause). Back out any component that misbehaves: in the reference, DropdownMenu (hydration ids) and Dialog (jerky flip).
- **sileo toasts**: set autopilot timing so expanded toasts don't collapse after about 4.5 s, and override its title-casing. The toast is a `<button>`, so put no links inside it.
- **Bundle weight**: check for a library shipped twice (sileo pinned motion 12 while animate-ui needed 14). It's extra download on the operator's phone.
