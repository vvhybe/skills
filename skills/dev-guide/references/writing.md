# Writing the guide

The guide is a learning book, not a reference dump. It takes a capable developer who has never seen this codebase and makes them productive in it, and it reads as well on GitHub as it does printed. The rules below are what the build understands and what readers need.

## Contents

1. What kind of documentation this is
2. Structure: four parts
3. The home page
4. A chapter
5. Callouts
6. Check yourself
7. Diagrams
8. Code, tables and numbers
9. The glossary
10. Style

## 1. What kind of documentation this is

Documentation comes in four kinds (the Diátaxis framework): tutorials, how-to guides, reference and explanation. A developer guide is mostly **explanation**: how the system works and why. It is shaped like a **tutorial** (a path through the material in order) and ends with a little **reference** (quick reference, glossary). Keep exhaustive reference (every endpoint's fields, every flag) in generated API docs and link to them.

Good learning books share a few habits, and the chapter template builds them in:

- **An advance organizer:** each chapter opens by saying what it covers ("In this chapter").
- **Concrete before abstract:** follow one real request or command end to end before describing the layers.
- **Why, not only what:** every rule a newcomer might break gets its reason.
- **Retrieval practice:** each chapter ends with questions that make the reader recall and apply, with answers that explain.
- **Signposting:** breadcrumbs, previous/next links, cross-references to the chapter that explains a term.

## 2. Structure: four parts

Four parts, each with a roman numeral and a colour (the edge tabs and dividers use them). A shape that works for most repositories:

| Part | Purpose | Typical chapters |
| --- | --- | --- |
| I. The big picture | What it is and how it fits together | What it is; the life of a request (or job, or command); repository tour |
| II. The contract | What the outside world sees | API or CLI; data formats; errors; configuration surface |
| III. Inside | How it works | One chapter per layer or subsystem; extension points |
| IV. Running and reference | Working on it day to day | Configuration; security; deployment; development workflow; design decisions; troubleshooting; quick reference; glossary |

Rename the parts to fit the project (a template kit's Part II might be "Building a template"). Keep chapters at 3 to 8 printed pages. Number chapters across the whole guide (1 to N), and files `NN-slug.md`. Record the parts and their file stems in `.print.json`.

## 3. The home page

`docs/guide/README.md`, from `assets/templates/home.md`:

- `# <Title> — Developer Guide` and a bold one-sentence promise
- a `> [!NOTE]` **Who this guide is for** box: the reader and what they need to know already
- a stats block: an HTML comment `<!-- stats -->` followed by a one-row table of numbers, a separator row and a row of labels (five numbers at most, each from the fact sheet)
- **The guide at a glance:** a Mermaid `mindmap` of parts and chapters
- **Contents:** one `### Part N · Title` heading per part, each followed by a table whose rows are exactly `| [N · Chapter title](NN-slug.md) | What you will learn |`. The build reads these descriptions for the part dividers, so keep the format.
- reading paths (for someone in a hurry, for a new contributor), how the pages are marked up, and where the rules really live
- a closing note linking the printable editions and showing the cover thumbnail

## 4. A chapter

From `assets/templates/chapter.md`:

1. `# N · Title` (the middle dot matters: the build splits the number from the title on it)
2. a breadcrumb line: `[Home](README.md) › Part I · The big picture`
3. a `> [!NOTE]` box whose first line is `**In this chapter**`, with three to five bullets
4. a lead paragraph that answers "what is this and why should I care?"
5. sections (`##`), each with one idea, prose first, a figure when the shape matters
6. `## Check yourself` with two to four questions
7. `<!-- nav -->`, a rule, and previous/next links

Link the first mention of another chapter's topic: `see [chapter 6](06-errors.md)`.

## 5. Callouts

GitHub's alert syntax, which renders on GitHub and becomes styled boxes in print. A leading bold line becomes the box's title.

| Syntax | Prints as | Use for |
| --- | --- | --- |
| `> [!NOTE]` | Note | background worth knowing, and the chapter's "In this chapter" box |
| `> [!TIP]` | Tip | a habit or shortcut that saves time |
| `> [!IMPORTANT]` | Why? | the reason behind a rule or design decision |
| `> [!WARNING]` | Watch out | a mistake people make often, or a sharp edge |
| `> [!CAUTION]` | Never | a hard rule; breaking it breaks production or security |

Use them sparingly: one or two per page at most. A page that is all boxes has no emphasis left.

## 6. Check yourself

```markdown
## Check yourself

**1. Why does the CLI not import `server.py`?**

<details><summary>Show answer</summary>
Because <code>server.py</code> starts the HTTP app on import … (one to three sentences that explain)
</details>
```

Write questions that need understanding, not recall of a sentence: "where would you add …", "what happens if …", "why is … and not …". The answer explains the reasoning, so a wrong guess still teaches. Answers are HTML inside `<details>`, so use `<code>` rather than backticks there.

## 7. Diagrams

- Mermaid in fenced blocks: `flowchart` for structure and data flow, `sequenceDiagram` for a request's life, `stateDiagram-v2` for lifecycles, `mindmap` for the home page.
- One idea per diagram, ten to fourteen nodes at most. Labels are short; detail goes in the prose.
- Colour with the four part colours through `classDef`, consistently (one colour means one kind of thing on every page). The printed theme is `assets/mermaid-print.json`.
- A caption on the next line, in italics: `*Figure: the runtime takes the whole plugin; the kit takes only the core.*`
- After a build, run `scripts/diagram_sizes.py <work>`: anything printing under about 6.5 pt needs reshaping (split long chains into two rows with subgraphs, use a mindmap for trees, LR for wide fans).
- Charts only from verified numbers, generated by a small script with `scripts/charts.py` into `docs/guide/assets/*.svg`, with a subtitle saying what was counted and when.

## 8. Code, tables and numbers

- Code blocks are short, real and labelled with their language. Say which file they come from in the sentence before.
- Tables for comparisons and mappings, at most five columns. Every table has a header row.
- Numbers come from the fact sheet, with the date they were counted when they could change.

## 9. The glossary

`glossary.md`, from `assets/templates/glossary.md`: a `##` heading per term, alphabetical, a one- or two-sentence definition in the project's sense, and a link to the chapter that explains it. Code terms in backticks sort by their name.

## 10. Style

- Plain words, short sentences, active voice, second person ("you send", "you'll see").
- Present tense for how the system works; past tense only for history.
- Define a term at first use, then use it the same way everywhere. One name per thing.
- Explain the reason for each rule. "Never call X from a handler" becomes useful with "because …".
- No marketing words, no "simply" or "just", no filler introductions.
- Sentence case for headings; chapter titles say what the chapter is about in three to five words.
