# Phase 6: SEO, social cards and web standards

Ship this as its own PR, stacked on the redesign, so each can be reviewed on its own. Search guidance changes; facts below were current in late 2026. If an SEO skill is installed (for example claude-seo), run its audit too and prefer its newer guidance where they differ.

## Contents

0. Server rendering first
1. Metadata
2. Social cards
3. Structured data
4. Crawler and app files
5. Headers
6. Accessibility that also helps search
7. Static exports on Cloudflare Pages
8. After launch
9. Verify

## 0. Server rendering first (the biggest win)

Run `scripts/ssr-audit.sh` on a production build. If any page shows `BAILOUT_TO_CLIENT_SIDE_RENDERING`, a "Loading..." shell or no `<h1>`, fix that before anything else. The usual culprit is a provider in the root layout calling `useSearchParams()` inside `<Suspense>`: remove the hook if it isn't needed, or move it into a leaf component.

## 1. Metadata

- **Root layout:** `metadataBase`, a title template, description, keywords, `applicationName`, `creator`, `publisher` (the legal entity), `category`, `referrer`, `formatDetection`; full `robots.googleBot` (`max-image-preview: large`, `max-snippet: -1`, `max-video-preview: -1`); `verification` from env values, only when a meta-tag token exists (a Search Console Domain property verified by DNS has none); `itunes` (Smart App Banner) and `appLinks` only when the store URL env values are set.
- **`viewport`** (its own export since Next 14): `themeColor` (the color at the top of the page) and `colorScheme`. On iPhone Safari since iOS 26 the status bar takes its tint from the page canvas instead, so set the `<html>` background to the theme color too (gotchas.md).
- **Every inner page** uses a `pageMetadata({ title, description, path })` helper that returns the canonical URL, Open Graph (`siteName`, `locale`, `url`, title, description) and the Twitter card. Without it, inner pages inherit the home page's Open Graph title.
- **Keywords** target what people search, platform-neutral when the product is on several platforms; a title near 60 characters and a description of 140 to 160.
- **Multilingual sites:** `alternates.languages` with `hreflang` for every locale plus `x-default`.

## 2. Social cards

- One `opengraph-image.tsx` per route, **with no runtime export**, so it is prerendered once at build (static `○`) and can read fonts and art with `node:fs`. Next adds `twitter:image` from it; delete old `twitter-image` files.
- **One shared renderer:** a brand stage, logo and wordmark, two title lines with the accent face, a subtitle, a URL pill and per-page art (the product scene on home, real outputs or the mascot on inner pages). Derive counts in subtitles from data.
- **What the renderer can't do:** every element with more than one child needs `display: flex`; no `inset` (use top, left, width, height); no `closest-side` in radial gradients; `backgroundSize` patterns don't render; images go in as data URIs with explicit width and height; TTF, OTF or WOFF fonts only (media.md § 8).
- Inside a route group the image route gets a hashed URL (`/fr/opengraph-image-k0kfef`); never hard-code it. A Node-only image route in a group is inherited by edge-runtime child pages and breaks their build: give it its own group.
- Test it: `/opengraph-image` with a query string returns 404 in dev, so fetch it without one, and check the served `og:image` URL and its `Content-Type`.

## 3. Structured data

Use `assets/JsonLd.tsx`, which escapes `<`.

- **The layout** emits one `@graph`, linked by `@id`:
  - `Organization` (name, `legalName`, logo, email, telephone, `PostalAddress`, `ContactPoint`, `sameAs` with the store listings and business profile that exist)
  - `WebSite`
  - `SoftwareApplication`, `MobileApplication` or `Service` (category, operating system, offers from the real billing data, `featureList` from the claims ledger)

  Never invent `aggregateRating` or reviews.
- **`BreadcrumbList`** from the page hero.
- **`FAQPage`** built from the FAQ data, and `ContactPage`, each joined to the site graph with `isPartOf`. Google retired FAQ rich results in May 2026; the markup still helps AI search read the answers, so keep it, but don't promise rich results.
- **Blog posts:** `BlogPosting` with real dates, the author or organization, the cover image, and `mentions` for products the post names.

## 4. Crawler and app files

- **`robots.ts`:** allow `/`, disallow `/api/`; `sitemap` and `host`.
- **`sitemap.ts`:** every page, with `images: ['<page>/opengraph-image']`. Give each page its **real** last-modified date (from content front matter or the source file's last commit); a build-time date stamped on every page is ignored.
- **`manifest.ts`:** `id`, `scope`, `lang`, `dir`, `categories`, theme and background colors, icons with purpose `any` plus a **maskable** 512.
- **`/.well-known/security.txt`** (RFC 9116), a static route: Contact, Expires (11 months after the build), Preferred-Languages, Canonical. Link GitHub advisories or `SECURITY.md` only when the repo is public.
- **`/llms.txt`**, static: summary, pages and FAQ, generated from the same data. It helps AI assistants; don't expect it to move Google rankings.
- **App links:** `/.well-known/apple-app-site-association` (and `assetlinks.json` for Android) when the app supports universal links.
- **IndexNow:** a random 32-hex key in `public/<key>.txt` and a script that reads `<loc>` entries from the live sitemap and POSTs them to `api.indexnow.org`. Run it after each production deploy.

## 5. Headers

- `poweredByHeader: false`.
- **On every path:**
  - `Strict-Transport-Security: max-age=31536000`; add `includeSubDomains` and `preload` only after the owner confirms every subdomain is HTTPS
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `X-Frame-Options: DENY`
  - `Cross-Origin-Opener-Policy: same-origin`
  - a `Permissions-Policy` that switches off what the site doesn't use
- **CSP in production only** (dev needs eval and websockets): `default-src 'self'`; `script-src 'self' 'unsafe-inline'` (Next's inline bootstrap and JSON-LD) plus analytics hosts actually used; `style-src 'self' 'unsafe-inline'`; `img-src 'self' data: blob:` plus the logo CDN; `font-src 'self' data:`; `media-src 'self'`; `connect-src 'self'` plus analytics endpoints; `frame-ancestors 'none'`; `base-uri 'self'`; `form-action 'self'`; `object-src 'none'`; `upgrade-insecure-requests`. Add `'wasm-unsafe-eval'` only when a WebAssembly decoder needs it (three-d.md). List every third party during discovery; each needs entries.
- **Preview deployments:** `X-Robots-Tag: noindex` on preview and `*.pages.dev` hosts, with canonical and Open Graph URLs pointing at their own host.
- **Media caching:** `Cache-Control: public, max-age=604800, stale-while-revalidate=86400` on `/videos` and `/images`. File names don't change when contents do, so don't mark them `immutable` unless they are hashed.

## 6. Accessibility that also helps search

- A skip link to `#main`, with `id="main" tabIndex={-1}` on every `<main>`.
- One `<h1>` per page and a heading on every section.
- A branded 404 with `robots: { index: false }` and useful exits.

## 7. Static exports on Cloudflare Pages

A Next.js static export (`output: 'export'`) with Pages Functions for the few dynamic routes deploys more reliably than full-stack adapters. On that setup:

- Middleware in `functions/_middleware.ts` handles locale redirects, retired-page redirects, security headers and the localized 404.
- Extensionless files (`/opengraph-image`) need their `Content-Type` set there (or in `_headers`).
- Every dynamic segment needs `generateStaticParams`, and `dynamicParams = false` makes unknown segments 404.
- With a `[lang]` segment owning `<html>`, the root `not-found.tsx` must render its own `<html>` and `<body>` (gotchas.md).

## 8. After launch

- Submit the sitemap once in Search Console and Bing Webmaster Tools (Bing can import from Search Console). Then run IndexNow after each deploy.
- Tag links between the company's own properties with UTM parameters (`utm_source=<site>&utm_medium=referral&utm_campaign=<placement>`), but not redirects or `llms.txt`.
- Lighthouse's simulated mobile LCP on a framework site can sit far above the observed LCP; check the observed value before chasing it.
- Analytics that set third-party cookies lower Lighthouse Best Practices. That is a trade-off the owner chooses knowingly, with the privacy policy and any consent banner updated to match; record it so later audits don't "fix" it.
- For a team that needs to see progress, keep a before/after report (delivery.md § Progress report).

## 9. Verify

On a production server:

- `scripts/ssr-audit.sh`: every page has its one `<h1>`, a canonical, a social image and no bailout; the headers are present.
- `scripts/playwright/console-scan.js`: zero CSP violations, page errors or hydration errors.
- Parse the served `<head>` for `og:*`, `twitter:*`, canonical and theme color on home and one inner page.
- Paste the home URL into a social-card debugger once the domain is live.
