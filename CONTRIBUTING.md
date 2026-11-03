# Contributing

Thanks for helping. These skills get better one real project at a time, so the most valuable contribution is evidence: what happened when you ran a skill on a real site.

## Ways to help

- **Field reports.** Open a [field report](https://github.com/vvhybe/skills/issues/new?template=field-report.yml): what you asked, what the agent did, what the owner said, and what fixed it. Owner quotes that don't map to anything in `feedback.md` are gold.
- **Gotchas.** A trap you hit, with its fix, belongs in `references/gotchas.md`.
- **Scanner rules.** A tell you keep seeing, with a fixture that shows it and a test.
- **Recipes.** A building block that shipped and that a client liked, written so it works on another brand.

## The evidence rule

Every rule, recipe and gotcha comes from something that happened on a real site, not from taste alone. Say where it came from in your PR. Taste is welcome as a hypothesis in an issue; it becomes a rule once it has held up somewhere.

## Writing style

The skills are read by agents first and people second. Write the way the existing files do:

- Plain words, short sentences, active voice, imperative mood ("Check the port", not "The port should be checked").
- Concrete over abstract: a real number, a real file, a real example.
- One idea per bullet. Tables for decisions and mappings.
- Sentence case for headings. No marketing words; no emoji in instructions (templates for team chat messages may use them).
- Keep `SKILL.md` under 500 lines. Detail goes in `references/`, one level deep, each file with a contents list when it grows past a screen.
- No client names, private URLs, tokens or internal facts. Describe what happened, not who it happened to.

## Scripts

- Zero dependencies where possible. Node 18+ for JavaScript, Bash for shell scripts (they must pass `shellcheck -S warning`).
- Playwright scripts are a single function expression with no trailing semicolon (the MCP wraps them).
- Scripts read and measure; they never change the target project.

## Before you open a PR

```bash
node scripts/validate.mjs            # frontmatter, size, links, scripts parse
node --test tests/slop-scan.test.mjs # scanner regression tests
```

Add a line to `CHANGELOG.md` under "Unreleased". Use [Conventional Commits](https://www.conventionalcommits.org/) with a lowercase subject (`feat(site-upgrade): add a booking recipe`).

## Adding a skill

A new skill lives in `skills/<name>/` with a `SKILL.md` whose `name` matches the folder. Add it to `.claude-plugin/marketplace.json` and to the README's list. Open an issue first so we can talk about scope.

By contributing you agree that your contribution is licensed under the MIT License and that you follow the [Code of Conduct](CODE_OF_CONDUCT.md).
