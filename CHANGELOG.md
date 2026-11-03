# Changelog

All notable changes to the skills in this repository. Versions follow [Semantic Versioning](https://semver.org/) per skill.

## Unreleased

## site-upgrade 2.0.0 (2026-11-03)

The first public release. Version 1 was a private skill distilled from one marketing-site upgrade; 2.0 folds in two more projects (a B2B company site taken through two full directions, and a help center built from scratch), every piece of owner feedback from all three, and ideas from the best open design skills.

### Added

- **Surface modes:** Persuade (product and company sites), Read (help centers, docs, changelogs) and Experience (portfolios), each with its own rules. New `read-mode.md`.
- **The idea sentence and the competitor test** in `direction.md`, with examples from shipped sites; a single "live thing" per site; palette by color theory (temperature contrast, 60/30/10, accents with one job).
- **The direction contract** template, written before code and audited in the critique.
- **The 9/10 rule** and a scored critique with caps and a written round format (`critique.md`, `assets/templates/critique-round.md`).
- **`tells.md`:** a dated registry of what reads as generated, with an explicit rule for earned exceptions that come from the brand.
- **`feedback.md`:** a decoder from what owners say ("not enough spice", "colors out of balance", "cheap replica") to what to change.
- **`three-d.md`:** when 3D earns its place, the source ladder (owner's model, procedural reconstruction, generators), the exactness gate, a headless Blender to glTF pipeline and runtime rules.
- **`slop-scan.mjs`:** a zero-dependency source scanner for tells, invented proof, genre copy, dead links, secrets and known traps, with named exceptions.
- **`page-audit.js`:** an in-browser frame check (one h1, heading length, small text, tap targets, unnamed controls, untitled sections, browser surfaces).
- **Templates:** claims ledger, direction contract, critique round, DESIGN.md, team update.
- B2B building blocks: catalog with real logos and lead prefill, problem-to-answer illustrations, honest comparison, own booking UI. Pricing presentation, changelog page, Experience mode notes.
- Media: device-frame compositing, brand-logo CDN gotchas, QR codes with a logo done properly, protecting proprietary assets.
- SEO: 2026 updates (FAQ rich results retired, real per-page lastmod, preview noindex), static exports on Cloudflare Pages, after-launch steps.
- Delivery: the before/after report, DESIGN.md at the end, repo hygiene.
- Evals, a repo validator, regression tests and CI.

### Changed

- The skill is self-contained: every recipe it needs is in its references, with original snippets, instead of pointers into a private reference repo.
- `ssr-audit.sh` also checks the canonical link and `og:image` per page.
- `ScrollTriggerRefresh.tsx` rewritten without template-specific references.
