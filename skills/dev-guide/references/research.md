# Research: the fact sheet

A developer guide is only as good as its facts. Before planning a single chapter, build a fact sheet in the scratchpad: what the repository is, how it works, and every number the guide will print, each with its source.

## Contents

1. The rule
2. What to collect
3. Counting things
4. Using background agents
5. What not to document here
6. Before a number goes on a page

## 1. The rule

- Every claim has a `path:line` (or a document and section).
- Every number has the command that produced it, and the commit it ran against.
- Anything you can't source is marked unknown and asked about, never guessed.
- Record the commit and date the guide is written against; they become `as_of` and `colophon` in the config.

## 2. What to collect

Read the README, docs, AGENTS.md and CONTRIBUTING.md first, then the code. For each item, note the files:

- **Purpose:** what the project does, for whom, and what it deliberately does not do.
- **Shape:** languages, frameworks, entry points, the top-level folders and what each holds.
- **The main flow:** one request, job or command followed end to end, from input to output, with the files it passes through. This becomes the "life of a …" chapter.
- **Contracts:** public APIs, schemas, CLI flags, config files, environment variables, error codes, and where each is defined.
- **Internals:** the layers or services, how they are wired, the extension points.
- **Running it:** install, configure, run, test, deploy; the commands that actually work today.
- **Quality and safety:** tests by suite, CI, security controls, known gaps.
- **History and decisions:** why it is built this way; ADRs, issues and commit messages that explain trade-offs.
- **Unfinished:** features behind flags, TODOs on the main path, docs that disagree with code. The guide says what the code does.
- **Vocabulary:** the project's own terms, for the glossary.

## 3. Counting things

Numbers make a guide concrete (the home page's stat tiles, charts), and they're where guides go stale first. Count with commands you can re-run, and store the command next to the number:

```bash
git ls-files | wc -l                                   # files
git ls-files '*.py' | xargs wc -l | tail -1            # lines of a language
grep -rn "^def test_" tests | wc -l                     # tests (adapt to the framework)
grep -rhoE "@(app|router)\.(get|post|put|patch|delete)" src | wc -l   # endpoints (adapt)
```

Prefer counts a reader can verify. Don't print a number whose meaning needs a paragraph.

## 4. Using background agents

For repositories over ~50 files, give read-only exploration agents concrete briefs while you plan, one area each (the main flow, the contracts, running and deploying, tests and CI). Ask for file paths with every answer and a word limit. Then re-verify every number they report yourself: agents round, and code moves.

## 5. What not to document here

- Anything a sibling repository owns and documents. Check how this repo already links to it, and cross-reference.
- Secrets, keys, hostnames and internal infrastructure details, unless the guide is explicitly internal and the owner agrees.
- Plans and roadmaps. The guide describes what is in the repository on `as_of`.

## 6. Before a number goes on a page

Re-run its command. If it changed, change the number everywhere it appears (the home page's stats, charts, chapters). Charts are generated from these numbers by a small script in the repo, so a re-count is a re-run.
