# Phase 8: Ship

## Contents

1. Branches and commits
2. Pull requests
3. The team update
4. The before/after report
5. DESIGN.md
6. Repo hygiene
7. Memory

## 1. Branches and commits

- Never work on the default branch. Name branches the way the repo does (`feat/site-upgrade`, `feat/seo-standards`).
- Read the repo's commitlint config and follow it exactly; some repos add rules of their own (a lowercase subject, a trailing period).
- End commit messages with the attribution line the session's instructions give.
- Let the hooks run; never pass `--no-verify`. lint-staged also formats Markdown and JSON.
- One squash-friendly commit per PR is fine; put the detail in the body. Several atomic commits are better when the PR is large.
- If you started on a branch whose PR has since been squash-merged, rebase onto the default branch to drop the stale commit, after confirming with `git diff <old-commit> origin/main --stat` that its content is there.
- To update an open PR's branch with the default branch, merge it in rather than rebasing and force-pushing, unless the owner prefers otherwise.

## 2. Pull requests

- Follow `.github/PULL_REQUEST_TEMPLATE.md` if there is one. Otherwise:
  1. Summary, with grouped bullets, outcome first
  2. Type of change
  3. Deploying: the env vars to set and where
  4. To confirm before merging: the owner decisions still open
  5. Verified: what you actually tested, at which widths and on which build
  6. Checklist
- Don't list the commits in the description; the Commits tab does that.
- Link issues and PRs as real links (`#12` or full URLs), not bare numbers in prose.
- End the description with the attribution line the session's instructions give.
- **Stacked PRs** (the redesign, then SEO and standards): `gh pr create --base feat/<redesign> --head feat/<seo>`, with a first line reading "Stacked on #N; retargets to main after #N merges."
- When a PR changes user-facing pages and the team has a designer who reviews them, mention them on the PR with the surfaces that changed.
- Run `gh pr checks <n>` and wait for the deploy preview before reporting.
- Merging, production settings, domains and DNS are the owner's steps unless they have said otherwise.

## 3. The team update

Short, Markdown, ready to paste into the team chat (Slack, Mattermost, Discord). Written for teammates, not reviewers. Use `assets/templates/team-update.md`:

```markdown
### 🚀 <Site>: <what> ready for review
**PR:** <link>

**What's new**
- **<Area>:** <one line, outcome first>
- ...

**Before going live**
- <env vars / owner decisions>

Feedback welcome on the PR 🙏
```

When a stacked PR follows, update the same message: number the PRs, add **Merge order**, and add the post-deploy steps (run IndexNow, submit nothing twice).

## 4. The before/after report

When the owner shares progress with a team or a boss, a report beats PR descriptions. Keep one living page (a shareable artifact or a doc) and add to it at every step:

- Start from the first question the owner asked, and keep the story in order.
- **Before/after pairs** at the same viewports (1440×900 and 390×844), captured with analytics blocked and the consent card dismissed (verification.md § 1).
- **One shape for every element:** every block in one column width; screenshots in fixed frames (desktop 16:10 cropped from the top, phone 9:19.5); pairs side by side; and a lightbox so any screenshot opens full size.
- Every PR and issue as a link; every "section N" as an anchor.
- A log of updates with dates, and a status for each item (shipped, in review, waiting on the owner).
- Decisions the owner or another team must take, each with options, pros and cons, so they can decide without a meeting.
- Republish to the same address so the link the team already has keeps working.

## 5. DESIGN.md

At the end, document the built world in a `DESIGN.md` at the repo root, so the next agent or designer stays on brand without reverse-engineering the CSS. Write it from the build, not from the plan: a rulebook written before the build gets defended against reality.

Use `assets/templates/DESIGN.md`. It follows the DESIGN.md format popularized by Google Stitch and collected in awesome-design-md: YAML front matter with the tokens (colors, typography, spacing, radii), then prose sections (overview, colors, typography, layout, elevation, shapes, components, signature moments, do's and don'ts, responsive behavior). Include the brand exceptions and why they are earned. Validate it with `npx @google/design.md lint DESIGN.md` when that tool is available.

## 6. Repo hygiene

The codebase is part of what the owner shows. When the upgrade is done, or when they ask for it:

- A README that says what the site is, how to run it, the env vars (with `.env.example`) and how it deploys.
- CONTRIBUTING.md (with the writing style for content), a code of conduct, SECURITY.md, issue and PR templates, and an AGENTS.md so coding agents follow the house rules.
- Unused template pages, components and images deleted. Assets in one place, mirrored between `public/` and source.
- Only `.env.example` committed; `.env*` git-ignored.

## 7. Memory

Save what will matter next time, not what the repo already records:

- shipped and unshipped facts, and launch and pricing decisions
- the direction chosen, what was rejected and why, and which branch holds an archived theme
- owner preferences and corrections, as feedback memories with *Why* and *How to apply*
- deployment facts: which hosting project holds which domain, how to roll back

When the owner gives live feedback, save it first. If they say "no work, just save it", stop after saving.
