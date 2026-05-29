# Coding Tutor - My Learning Journey

This repository contains my personalized coding tutorials created with the [coding-tutor](https://github.com/nityeshaga/claude-code-essentials) Claude Code plugin.

## What's Here

- **Tutorials**: Markdown files with concepts learned from various codebases
- **Learner Profile**: My background, goals, and learning preferences
- **Quiz History**: Spaced repetition quiz results tracking my progress

## How It Works

Each tutorial includes:
- `source_repo`: Which codebase the examples come from
- `concepts`: What concepts are covered
- `understanding_score`: How well I've retained this (1-10, updated via quizzes)
- Real code examples from actual projects I'm learning from

This is my personal learning trail - tutorials are written specifically for me, using my vocabulary and building on my existing knowledge.

---

## Viewing the tutorials as a website

A small static site is bundled with this folder so the tutorials are nicer to read than raw markdown.

### Local

```
python3 server.py
```

Opens at <http://localhost:8765/>. Press Ctrl+C to stop. The script regenerates `manifest.json` at startup and serves the current directory.

### Publishing to GitHub Pages

The site is fully static — no backend. To publish:

1. **Rebuild the manifest** so it lists the latest tutorials:
   ```
   python3 server.py --build
   ```
2. **Commit and push:**
   ```
   git add . && git commit -m "Update tutorials" && git push
   ```
3. **Enable Pages** in the repo settings (once, on first setup):
   *Settings → Pages → Source: deploy from a branch → main / root.*

Your tutorials will be live at `https://<username>.github.io/<repo>/`.

> Tip: run `python3 server.py --build` whenever you add or rename a `.md` file so the sidebar list stays in sync before you push.

### Layout

Content lives in two places, plus an "about" page:

```
coding-tutor-tutorials/
├── index.html          # the viewer
├── server.py           # builds manifest.json + serves locally
├── manifest.json       # auto-generated, sectioned index (drives the sidebar)
├── about.md            # the "How am I" page (no frontmatter)
├── learner_profile.md  # private
├── extras/             # complementary material (theory, references)
│   └── YYYY-MM-DD-topic.md
└── courses/            # the curriculum, one folder per subject
    └── data-structures-and-algorithms/
        └── YYYY-MM-DD-topic.md
```

The sidebar renders one collapsible **accordion** per section:

- **Extras** — everything in `extras/` (complementary content like Big O notation).
- **One section per subject** — each folder under `courses/`, titled by the
  folder name prettified (`data-structures-and-algorithms` → "Data Structures
  and Algorithms").
- **How am I** — a pinned link at the bottom that loads `about.md`.

Every entry in `manifest.json` carries a `path` relative to this directory
(e.g. `courses/data-structures-and-algorithms/2026-...md`), so the static
viewer fetches each file directly — it works the same locally and on any
static host.

**To add content:** drop a `.md` file into `extras/` or into a subject folder
under `courses/` (create a new folder, e.g. `courses/javascript/`, to start a
new subject), then run `python3 server.py --build`. The new section/entry
appears automatically — no edits to `index.html` needed.

**Reading order:** within a section, tutorials are sorted by the `order:` field
in their frontmatter (`order: 1`, `order: 2`, …) — the intended sequence to read
them in, independent of filename or date. Tutorials without an `order:` fall
back to date, then title, and sort after the ordered ones.

### Files

| File | Purpose |
|------|---------|
| `index.html` | The viewer (accordion sidebar by section + rendered markdown). |
| `server.py` | Rebuilds `manifest.json` (walks `extras/` + `courses/`) and optionally serves locally. |
| `manifest.json` | Auto-generated. `{ sections: [{id, title, items:[{path, title, date, order}]}], about }`. |
| `about.md` | The "How am I" page — about the developer and the project. |
| `extras/*.md` | Complementary material (theory, references). |
| `courses/<subject>/*.md` | The curriculum tutorials, grouped by subject. |
| `learner_profile.md` | **Private.** Listed in `.gitignore`. |
