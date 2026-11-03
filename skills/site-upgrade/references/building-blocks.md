# Phase 3: Building blocks

Patterns that shipped, with the traps each one hit. Adapt every one to the new brand and to the target repo's versions: Tailwind 4 has `@theme`, `@utility`, `size-*` and `bg-linear-*`; Tailwind 3 needs `theme.extend` and plugins. The snippets are minimal sketches in React and TypeScript, not drop-in components.

Build it **still** first: tokens, the hero at desktop and phone width, then each section with real content. Motion comes in phase 4.

## Contents

- Hero and navigation: cinematic hero, adaptive navbar, phone menu, language switch
- Telling the story: scroll story with pinned film, live preview button, walk-through countdown
- Showing the product: live UI tiles, interactive product demo, coverflow gallery with floating stats, spotlighting the differentiator
- Company and B2B: catalog with real logos and lead prefill, problem-to-answer illustrations, honest comparison, own booking UI
- Plans and pricing
- Inner pages: page hero, footer, FAQ, changelog, legal pages, 404
- Experience mode: portfolios and showcases
- Utilities

## Hero and navigation

### Cinematic hero

- **Composition.** Lay out a fixed-pixel scene (say 560×620) and scale the whole box per breakpoint (`scale-[0.6] sm:scale-[0.84] lg:scale-100`) with wrapper heights set to match. Responsive layered art without hand-tuning every element.
- **Layers.** Nest three elements per layer: the outer one takes pointer parallax (`data-depth`, moved with `gsap.quickTo` on x and y), the middle one takes the intro animation, the inner one holds the static CSS `rotate`. Separate elements mean transforms never fight.
- **The product is the art.** A real device frame with a real screen (media.md § App screenshots), a real document, the real mascot.
- **No flash before the intro, and no blank hero without it.** An inline script in `<head>` adds a class to `<html>` (`document.documentElement.classList.add('intro')`). CSS hides intro targets only under `.intro` inside `@media (prefers-reduced-motion: no-preference)`; the timeline reveals them with `autoAlpha` and removes the class when it ends. A timeout in the same inline script removes the class after about 3 s if the timeline never started, so a slow or failed bundle still shows the hero. With scripts off or reduced motion, everything shows.

### Adaptive navbar

Dark sections carry `data-nav-theme="dark"` and light ones `"light"`. The bar watches a thin band where it floats and takes the theme of whatever is under it:

```tsx
useEffect(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const e of entries) if (e.isIntersecting) setTheme(e.target.getAttribute('data-nav-theme') as Theme);
    },
    { rootMargin: '-44px 0px -91% 0px' }, // a band about where the bar sits
  );
  document.querySelectorAll('[data-nav-theme]').forEach((s) => observer.observe(s));
  return () => observer.disconnect();
}, [pathname]);
```

- Section links glide with the smooth scroller (`lenis.scrollTo('#id')`) on the home page and are `/#id` elsewhere. Page links get `aria-current="page"`.
- FAQ and Contact belong in the bar when visitors look for them.

### Phone menu

- A solid panel under the bar that closes on Escape, an outside `pointerdown` and a route change. Translucent panels let the hero text ghost through.
- **Every action in the bar is also in the menu**, the primary one included. A contact button that is hidden on phones and missing from the menu is a lost lead.

### Language switch

A segmented control (`FR | EN`) with the current language marked, not a flag toggle: flags are countries, not languages, and owners notice. Keep the default locale in the URL scheme, localize the 404, and emit `hreflang` alternates (seo-standards.md).

## Telling the story

### Scroll story with a pinned film

- **Layout.** The film is pinned with `sticky top-0 h-screen` plus **`self-start`** on the grid item (grid items stretch, and a stretched item never sticks). The steps are tall list items beside it. The section uses `overflow-clip`, never `overflow-hidden`, which breaks sticky.
- **Active step.** Whichever step crosses a reading line: an IntersectionObserver band at 50% on desktop, lower on phones so it clears the media.
- **Playback.** Each chapter plays its own `[start, end)` range of one video. When the visitor lingers, the chapter hands over by gliding to the next step while the film runs on, with no seek back. If the glide never lands, loop that chapter; the last chapter loops.
- **Progress bars.** Equal length, like stories, written straight to the DOM from `requestAnimationFrame` so playback never re-renders React.
- **Encoding.** Chapter jumps need keyframes at each cut (media.md).
- **Phones.** A full-screen reel with the chapter's title and line set over the bottom like a news caption that cycles, while the steps stay in the page as invisible scroll spacers for scrolling and screen readers.

### Live preview button

A crafted call to action instead of a "Watch in 23 seconds" pill: a square silent preview clip in a circle, a progress ring driven by the clip's time, and the current chapter's caption beside it.

```ts
const C = 2 * Math.PI * radius;
let raf = 0;
const tick = () => {
  const p = video.duration ? video.currentTime / video.duration : 0;
  ring.style.strokeDashoffset = String(C * (1 - p));
  raf = requestAnimationFrame(tick);
};
// start on enter, cancelAnimationFrame(raf) and pause on leave
```

Re-key the caption on each chapter change to replay its rise-in. Add a magnetic pull (the `translate` property, fine pointers only) and a 1px gradient border drawn with a mask. Play only while on screen.

### Walk-through countdown

An onboarding sequence (T-3, T-2, T-1, T-0) is a scroll the visitor walks through, not tabs they may skip. A trajectory line fills with scroll, each station pings a ring as it is reached, and the mascot travels or reacts. On phones, check that markers and progress bars never sit on top of the mascot or the copy at any scroll position.

## Showing the product

### Live UI tiles

Each tile shows a working piece of the product instead of an icon: a color picked from a logo, a signature drawing itself (`pathLength={1}` and a dashoffset animation), a slot-roll of currencies, payments reaching a "Paid" stamp, contacts ticking in, a browser-to-phone sync.

- Each tile is a small state machine that starts when it scrolls into view (once), cleans up its timers and offers a replay where it helps. With reduced motion it shows the final state.
- One `pointermove` handler on the grid sets `--spot-x` and `--spot-y` on the hovered tile for a spotlight.
- Vary spans and grounds (one night tile) so it doesn't look like a card kit.
- A slot roll that wraps spins backwards unless you duplicate the first item at the end and snap back without a transition on `transitionend`.

### Interactive product demo

Two halves that mirror the product's workflow: an editor styled like the real app next to the real output document.

- **Fit the document like a PDF viewer.** Lay it out at a fixed width and scale it to its column. Observe the column (its width) and the paper (rows added, fonts swapped), and size a frame between them that nothing observes, so setting its height can't loop:

  ```tsx
  useLayoutEffect(() => {
    const column = columnRef.current!, frame = frameRef.current!, paper = paperRef.current!;
    const fit = () => {
      const scale = Math.min(1, column.clientWidth / PAPER_WIDTH);
      paper.style.transform = `scale(${scale})`; // transform-origin: top left; layout size unchanged
      frame.style.height = `${paper.offsetHeight * scale}px`;
    };
    const observer = new ResizeObserver(fit);
    observer.observe(column);
    observer.observe(paper);
    return () => observer.disconnect();
  }, []);
  ```

- **Highlight only real changes.** Keep the previous value as derived state and re-key a span to replay the flash, so changing the brand color doesn't flash every field:

  ```tsx
  function Changed({ value, children }: { value: unknown; children: React.ReactNode }) {
    const [seen, setSeen] = useState(value);
    const [flashes, setFlashes] = useState(0);
    if (!Object.is(value, seen)) { setSeen(value); setFlashes((n) => n + 1); }
    return <span key={flashes} className={flashes ? 'animate-flash' : undefined}>{children}</span>;
  }
  ```

- **Tween the totals** with `requestAnimationFrame`; jump straight to the value with reduced motion.
- **Seal the paper.** Give every text element inside the document an explicit size and color. The site's base styles, and their dark-mode variants, otherwise leak onto a white page.
- **Mark it as a real artifact.** Put `data-ui` on the root of any real document or app fragment built in HTML. `page-audit.js` then skips it for page-level rules (small text, tap targets, heading length), because a real invoice has 9 px line items and that's correct.

### Coverflow gallery with floating stats

- Each card's offset from the active one is the shortest way around the ring; one function turns it into a transform:

  ```ts
  const offset = (i: number, active: number, n: number) => {
    let d = (i - active) % n;
    if (d > n / 2) d -= n;
    if (d < -n / 2) d += n;
    return d;
  };
  const placement = (d: number) => ({
    transform: `translateX(${d * 62}%) translateZ(${-Math.abs(d) * 140}px) rotateY(${d * -28}deg)`,
    opacity: Math.abs(d) > 2 ? 0 : 1 - Math.abs(d) * 0.18,
    zIndex: 10 - Math.abs(d),
  });
  ```

- Side cards are buttons with `tabIndex={-1}`; the group handles arrow keys; pointer down and up handle swipes.
- Use **real rendered outputs** at the paper's own aspect ratio.
- Under the active card, show what it is for (its trades, its color variants) and a link to view it up close.
- **Numbers as a moment, not a flat row.** The library's counts float around the carousel as small cards (a count with a real swatch row or icon), count up once on view, and bob gently. Render the final number in the HTML so crawlers and reduced motion see it. Below the large breakpoint, stack them at one width.

### Spotlighting the differentiator

When one feature is the product's edge (its templates, its catalog), give it its own page and treat each item as having a personality, not as an image in a grid.

- Ground each item's description in its source (a manifest's own description), never in invented adjectives.
- Group by behavior the visitor can see ("reacts to the numbers", "changes with the document length"), and include an item only when its published preview shows that behavior.
- A catalog card opens a close-up `<dialog>` with a larger preview, what it is made for, its variants, the primary action, Copy link and previous/next. `/page#item-<id>` opens one directly.
- Publish only what may be published (licences, unreleased items) and only at preview sizes (media.md § Protecting proprietary assets).

## Company and B2B

### Catalog with real logos and lead prefill

- Third-party logos come from a brand-logo CDN (Brandfetch's Logo Link) rather than static files that go stale; read its terms, then look up each brand's real assets and render each on its real background before shipping (media.md § Brand logos).
- Logos rest in grey and take their own color on hover, only where hover exists: `@media (hover: hover) { .logo { filter: grayscale(1) } .logo:hover { filter: none } }`.
- On phones, a deliberate grid (two columns by three rows) whose last cell reads "+12 more" beats a long scroll.
- Lead it in order of the owner's priorities, not alphabetically.
- **Carry the choice into the contact form.** The catalog's action links to `/contact?system=<slug>`. The form reads the parameter in a small client component (not the layout: see gotchas.md § Rendering), accepts only slugs from the catalog, preselects the topic and adds a line to the message. The team gets qualified leads.

### Problem-to-answer illustrations

B2B visitors need to see their problem understood before they see a product. A language that worked for a cloud company, inspired by large infrastructure sites:

- Problems drift as noise over a jagged line in a warning color, cross into the brand's panel, and the line runs flat with a pill naming the fix.
- Before/after diagrams: scattered blocks, tangled wires and a variable bill against one private cloud, one contact and a flat bill.
- One system across the page: dashed blueprint frames with corner marks, mono micro-labels, the warning color only for problems, no figures, prices or SLAs inside the art.

### Honest comparison

Compare against the alternatives the visitor already considers, by name, without inventing numbers: a variable bill as `$`, `$$`, `$$$` across months against one flat `$`; ticks for what you include and attention triangles for what they must handle themselves.

### Own booking UI

An embedded scheduling iframe clashes with the design and widens the CSP. Proxy the scheduler's public API (for Cal.com: available slots, create and cancel a booking) through your own route, and build the picker in the site's language. Show the time zone explicitly and derive offsets from an IANA zone with `Intl`, never a hardcoded offset; some countries change offset during the year.

## Plans and pricing

- Fetch prices from the billing system at build time, memoized (`pending ??= load()`), with a deliberate fallback when the API or its variables are missing. Plans, the FAQ and the JSON-LD offers read the same source.
- Present value the way large companies do, without tricks: one recommended plan marked clearly; the yearly plan anchored by its monthly equivalent and the saving; the trial stated plainly and identically everywhere; renewal and cancellation terms next to the button; taxes and local prices explained ("the store shows the price for your country"). No fake strikethrough prices, countdown timers or "only 3 left".
- When the store SDK truncates the monthly equivalent ($119.99 a year → $9.99 a month), do the same so the site and the app agree.
- If the owner chooses not to publish prices, route the pricing page to a quote request and keep the builder in the code for later.

## Inner pages

- **Page hero.** One dark-stage hero for inner pages with breadcrumbs (emit `BreadcrumbList` JSON-LD from it), the heading and a CSS rise-in. No scroll triggers.
- **Footer.** Static, the same on every page, no reveal animations, so it shows even on short screens. It closes the page; it isn't a sitemap dump.
- **FAQ explorer.** Search that opens matching answers, a category rail tracked by IntersectionObserver, a grid-rows accordion and a contact fallback when nothing matches. On phones the grid needs `grid-cols-1` and `min-w-0` on the rail, or the chip row overflows the page. Link answers to the help center's guide where one exists.
- **Changelog.** Built from git tags, the CHANGELOG and release milestones, dated by the store's release days, written for customers rather than developers, with hard terms linked to an explanation. An RSS feed lets followers subscribe. Keep it on the marketing site and link it from the help center.
- **Legal pages.** A quiet closing card with ways to get help. Keep acronyms like "FAQ" intact if the button styles change case (`normal-case`).
- **404.** A signature moment, not a dead end (direction.md § 6), with real exits and `robots: noindex`.

## Experience mode: portfolios and showcases

- The work leads from the first viewport. The interface recedes.
- A cover treatment can carry the identity (a 1-bit black-and-white cover that develops into the project's native colors on hover), but on a project's own page the screens show in their native colors.
- Each project page is a case study: a short summary, chapters, each screen explained as a numbered figure with a note, and a story built only from verified facts. Dates come from git history and releases.
- Carousels of shots scroll gently and loop without a seam, holding each shot long enough to see.
- Personality lives in small, optional places: page titles written as paths (`~/name/contact`), a console easter egg, keyboard navigation for the curious. None of it blocks the work.
- Client work follows the client's disclosure rules: product-level descriptions for employer-owned products, credits to roles when names are off limits, no links to private tools, no contact details in plain HTML.

## Utilities

- `assets/ScrollTriggerRefresh.tsx`: refresh scroll triggers on any body resize.
- A `useInView` hook (once, with a threshold) and a `useReducedMotion` hook; share them instead of re-implementing per component.
- Stage backgrounds as named utilities (`stage-night`, `stage-aurora`) so dark sections stay consistent.
