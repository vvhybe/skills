# Phase 7: Ship

## Branches and PRs

- **Production broken?** Ship a small hotfix PR first; the owner merges it and runs its migration.
- **Everything else** lands as commits on one epic branch with one PR, kept as a draft until the owner has verified it as a whole. Nothing reaches production in between.
- **Commits**: one topic each (`feat(ui): …`, `fix(billing): …`, `test: …`), with a body that says why. Follow the repo's commitlint if it has one, and end with the attribution line from the session's instructions. Never pass `--no-verify`.
- **PR description**: a summary grouped by area; what was verified and how; what the owner must confirm or run (decisions, env vars, migrations); a checklist. End with the attribution line from the session's instructions.
- **Public repo**: no client names, prices, quotation terms or unfixed security gaps in commits, PRs or issues. Describe security work generically ("access hardening") until it's fixed.
- **Owner steps, never yours**: production deploys, production migrations, publishing an OAuth app, changing production settings or provider dashboards. List them in the PR and in your update.

## Owner updates

After each push, a short note covering:

- what changed, outcome first, grouped by area
- how you checked it (and what you could only check statically)
- what's left on the path to 10/10
- what you need from them

When they ask "how would you rate it", answer on the five axes from discovery, before and now, with what keeps each from 10.

## Memory

Save what will matter next session, not what the repo already records:

- **project**: the plan, decisions, what is merged and migrated, the business rules as the owner corrected them, scope (paid items and free extras)
- **feedback**: the owner's verdicts on the UI (what worked, what felt wrong), each with *Why* and *How to apply*
- **reference**: the local database, the action harness, which test accounts are allowed
