# AGENTS.md

Instructions for coding agents working on this repository (the skills themselves, not a project that uses them).

## What this repo is

A collection of agent skills. Each skill is a folder in `skills/` with a `SKILL.md` (frontmatter `name` and `description`, then the method), `references/` read on demand, `scripts/` for deterministic checks and `assets/` to copy into projects.

## Rules

- Follow the evidence rule and the writing style in `CONTRIBUTING.md`.
- Keep `SKILL.md` under 500 lines and every reference one level deep from it.
- Never add client names, private URLs, tokens, account IDs or personal contact details. Case studies in `docs/case-studies/` describe public sites at product level only.
- Scripts have no dependencies unless there is no other way, and they never modify the project they inspect.
- After any change, run `node scripts/validate.mjs` and `node --test tests/slop-scan.test.mjs`.
- Conventional Commits with a lowercase subject. Update `CHANGELOG.md` under "Unreleased".
