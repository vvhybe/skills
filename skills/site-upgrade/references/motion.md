# Phase 4: Motion and the signature

Motion goes on after the site works still. It answers the visitor or tells the story; it never decorates for its own sake, and it never holds content hostage.

## Contents

1. The motion budget
2. Rules
3. The toolkit
4. Recipes
5. Reduced motion
6. Performance

## 1. The motion budget

- **One choreographed intro**, run once: masked line reveals, layered entrances, then the signature moment (a seal slamming with `power4.in`, a page jolt, an ink ring).
- **User-driven:** pointer depth on hero layers, hover sheen, magnetic calls to action, drag and keyboard on galleries.
- **State-driven:** live demos, tiles that play once when scrolled into view (with a replay), stories that follow scroll and advance on their own after the visitor lingers.
- **Scroll-linked:** a scene that lifts or opens as you scroll (`scrub`), a trajectory that fills.
- **One or two signature moments** (direction.md § 6). Never several competing ones.

Avoid identical fade-ups on every block, ambient loops everywhere, hover lift on every card, bounce easing, and any reveal that could fail to fire.

## 2. Rules

- Content is visible by default. Motion starts from an already-visible state, or it hides things only under a class an inline script sets, inside `@media (prefers-reduced-motion: no-preference)`, with a timeout that shows everything if the timeline never runs (building-blocks.md § Cinematic hero).
- Animate `transform` and `opacity` first. `clip-path`, `filter`, `mask` and `backdrop-filter` are fine when they stay smooth on a mid-range phone. Never animate `top`, `left`, `width` or `height`.
- Exponential ease-out for entrances; `power4.in` for impacts; no bounce.
- Calm beats clever. A 3D-flip dialog was rejected as "jerky"; a sheet that slides was praised.
- Keep the footer, the closing call to action and anything near the bottom free of scroll reveals. Short screens may never scroll far enough to trigger them.
- Every moving thing that lasts more than five seconds can be paused.

## 3. The toolkit

- **GSAP + ScrollTrigger** for timelines, scrubbed scroll and pinned scenes. Wrap everything in `gsap.matchMedia()` with `'(prefers-reduced-motion: no-preference)'`, and clean up with `ctx.revert()` on unmount.
- **Lenis** for smooth scroll when the site is a story; drive ScrollTrigger from it, and use `lenis.scrollTo` for in-page links.
- **IntersectionObserver** for "play once when seen" and for reading lines.
- **`requestAnimationFrame`** writing straight to the DOM for anything tied to video time or pointer position, so React doesn't re-render 60 times a second.
- **CSS scroll-driven animations** (`animation-timeline: view()` / `scroll()`) for simple scroll-linked effects, inside `@supports (animation-timeline: scroll())` with a static fallback.
- **View Transitions** for state changes that should morph (a card into its detail), and `@starting-style` to animate elements in from `display: none`.
- **Canvas 2D or WebGL** when the signature needs it (a particle singularity on the 404, a 3D mascot: three-d.md). Lazy-start near the viewport, pause off screen.

## 4. Recipes

- **Masked headline lines.** Each line in an `overflow-hidden` wrapper, the text rising from `yPercent: 110`. Add bottom padding and an equal negative margin to the mask so descenders aren't clipped, and check the accent face's descenders at the largest size.
- **Pointer depth.** `gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3' })` per layer, scaled by `data-depth`; fine pointers only (`matchMedia('(pointer: fine)')`).
- **Scroll lift.** One ScrollTrigger with `scrub: true` on the hero scene: it rises and fades a little as the next section arrives.
- **Play once on view.** A tile's state machine starts when it enters, cleans up its timers on leave or unmount, and exposes a replay. Under reduced motion it renders the end state.
- **Auto-advance stories.** Track the active chapter; when the visitor has lingered for the chapter's length, glide to the next step (`lenis.scrollTo(next, { duration: 1.2 })`). Treat a landing that doesn't arrive (the visitor scrolled away) as a cancel, and fall back to looping the chapter.
- **Count-up numbers.** Render the final value in HTML; on view, tween from zero with `requestAnimationFrame` and an ease-out; with reduced motion, do nothing.
- **Re-keyed rise-ins.** Changing a React `key` remounts an element and replays its CSS animation: the cheapest way to animate a caption change or a "changed" flash.
- **Magnetic call to action.** Use the CSS `translate` property (not `transform`) so it composes with other transforms; fine pointers only; release with a spring-like ease.
- **Refresh after layout changes.** Scroll triggers measure once. Accordions, tabs, fonts and late images move things. Mount `assets/ScrollTriggerRefresh.tsx` once in the layout.

## 5. Reduced motion

With `prefers-reduced-motion: reduce`: no intro, no autoplay, no parallax, no auto-advance; tiles and counters show their final state; videos show their poster with a play button; transitions use `motion-reduce:` variants or none. Test it (verification.md): every intro target visible, nothing playing.

## 6. Performance

- Keep main-thread work out of scroll handlers; read layout once, write in rAF.
- Pause video, canvas and WebGL when off screen or when the tab is hidden (`document.visibilityState`).
- Hero video: `playsInline muted loop preload="metadata"`, a poster, WebM first then MP4; play only while visible.
- Check a mid-range phone profile in DevTools (4× CPU slowdown). If a moment drops below about 50 fps, simplify it before you polish it.
