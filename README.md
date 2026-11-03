<p align="center">
  <img src="docs/banner.png" alt="tebzira: agent skills, blended in Marrakech. The recipes I use to ship real work." width="100%">
</p>

<p align="center">
  <a href="https://github.com/vvhybe/tebzira/actions/workflows/check.yml"><img src="https://github.com/vvhybe/tebzira/actions/workflows/check.yml/badge.svg" alt="Check"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-0b0b0b?style=flat" alt="MIT license"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-0b0b0b?style=flat" alt="Agent Skills compatible"></a>
  <a href="#install"><img src="https://img.shields.io/badge/Claude%20Code-plugin-0b0b0b?style=flat" alt="Claude Code plugin"></a>
  <a href="#the-recipes"><img src="https://img.shields.io/badge/recipes-3-c0392b?style=flat" alt="3 recipes"></a>
</p>

# tebzira

> *Tebzira* is Marrakchi Darija for spices, and for the blend a cook keeps ready by the stove. This is mine.

These are the agent skills I use in my own work. Each one started as a private skill on a real project, got rewritten every time an owner said "not quite", and is shared here once it held up. They're not prompt collections: each is a recipe, with its ingredients (what it needs), its method (how it works), the scripts that taste it as it cooks, and everything that burned along the way.

## The recipes

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="skills/site-upgrade/README.md"><img src="docs/site-upgrade/banner.png" alt="site-upgrade" width="100%"></a>
      <h3><a href="skills/site-upgrade/README.md">site-upgrade</a></h3>
      <p>Turns a website into one its owner is proud to show: true claims, a design from the brand's own material, signature moments, a contact form that really delivers, SEO and security headers, a scored critique in a real browser, and PRs the team can review.</p>
      <p><sub>Built on an app's marketing site, its help center and a B2B company site taken through two directions.</sub></p>
      <p><code>npx skills add vvhybe/tebzira --skill site-upgrade</code></p>
    </td>
    <td width="50%" valign="top">
      <a href="skills/dashboard-upgrade/README.md"><img src="docs/dashboard-upgrade/banner.png" alt="dashboard-upgrade" width="100%"></a>
      <h3><a href="skills/dashboard-upgrade/README.md">dashboard-upgrade</a></h3>
      <p>Turns a dashboard that fails its operator into a calm tool they trust: money and action bugs fixed first with tests, forms that never lose input, errors they can report, screens shaped around their real day, one signature moment, all checked in a real browser against a local database.</p>
      <p><sub>Built on a yoga studio's command center in Marrakech, run from one instructor's phone. <a href="https://github.com/jnaninyoga/dashboard">Its source is public.</a></sub></p>
      <p><code>npx skills add vvhybe/tebzira --skill dashboard-upgrade</code></p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="skills/dev-guide/README.md"><img src="docs/dev-guide/banner.png" alt="dev-guide" width="100%"></a>
      <h3><a href="skills/dev-guide/README.md">dev-guide</a></h3>
      <p>Writes a developer guide for any repository as a learning book, every fact checked against the code, then typesets it as a PDF and a Word file with a publisher-grade cover: a public-domain engraving, one colour per volume, sibling repos as a series.</p>
      <p><sub>Built on three related production repositories, now Volumes I to III of one set.</sub></p>
      <p><code>npx skills add vvhybe/tebzira --skill dev-guide</code></p>
    </td>
    <td width="50%" valign="top">
      <h3>Take the whole blend</h3>
      <p>Each recipe works alone. Together they cover what a small team ships for a client: the website, the app's back office, and the book the next developer learns from.</p>
      <p><code>npx skills add vvhybe/tebzira</code></p>
      <p><sub>Pick from the list, or <a href="#install">install them as Claude Code plugins</a>.</sub></p>
    </td>
  </tr>
</table>

Each recipe's own page has its showcase, its method, its tools and what's inside.

## What every recipe shares

- **Evidence over taste.** Every claim on a website, every figure on a dashboard and every fact in a guide traces to a source. Rules in these skills come from things that happened on real projects.
- **Real material over decoration.** The product itself, real outputs, a real engraving, never stock illustration or a fake dashboard.
- **Look before you say "done".** Real browsers, every page, at every width that matters, with scripts for what can be measured and a written critique for what can't.
- **Safe on input you don't control.** The scripts read and measure; they never change the project they inspect, never leak a local file into an output, and never need an API key.
- **Small in context.** Each `SKILL.md` is a map. The detail lives in `references/`, read one file at a time, when the agent reaches that step.

## Install

**Any agent that reads [Agent Skills](https://agentskills.io)** (Claude Code, Codex, Cursor, Gemini CLI and others), with the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add vvhybe/tebzira                        # choose from the list
npx skills add vvhybe/tebzira --skill site-upgrade   # or name one
```

<details>
<summary><b>Claude Code plugin</b></summary>

```
/plugin marketplace add vvhybe/tebzira
/plugin install site-upgrade@tebzira
/plugin install dev-guide@tebzira
/plugin install dashboard-upgrade@tebzira
```

</details>

<details>
<summary><b>From a clone, linked so <code>git pull</code> updates them</b></summary>

```bash
git clone https://github.com/vvhybe/tebzira.git ~/src/tebzira
ln -s ~/src/tebzira/skills/site-upgrade ~/.claude/skills/site-upgrade
ln -s ~/src/tebzira/skills/dev-guide ~/.claude/skills/dev-guide
ln -s ~/src/tebzira/skills/dashboard-upgrade ~/.claude/skills/dashboard-upgrade
```

</details>

## What's here

```text
skills/
├── site-upgrade/       SKILL.md, references, scripts, assets, evals, and its README
├── dev-guide/          SKILL.md, references, scripts, assets, evals, and its README
└── dashboard-upgrade/  SKILL.md, references, scripts, assets, evals, and its README
docs/                  each skill's banner, showcase and case studies
tests/                 regression tests for the scripts, run in CI
scripts/validate.mjs   checks every skill: frontmatter, size, links, scripts parse
```

`npm run check` runs the validator and every test.

## Contributing

The most useful contribution is a [field report](https://github.com/vvhybe/tebzira/issues/new?template=field-report.yml): you ran a skill on a real project, and here's what happened. Rules here come from shipped work, so evidence beats opinion. See [CONTRIBUTING.md](CONTRIBUTING.md) for the writing style and the checks.

## License

[MIT](LICENSE) © [vvhybe](https://github.com/vvhybe)
