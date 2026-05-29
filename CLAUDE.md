# CLAUDE.md

## What this repo is

A personal **coding-tutorial library** plus a tiny **static viewer** for reading it.
The tutorials are written by the `coding-tutor` Claude Code skill (one Markdown
file per lesson); this repo stores them, organizes them, and renders them as a
website that works locally and on any static host (no backend).

This repo is the **library + viewer**. It is *not* where teaching happens — the
pedagogy/tutor rules live in the learner's `study/` project. Here, the job is
keeping the library tidy and the viewer working.

## Layout

```
index.html          # the viewer (vanilla JS, CDN deps only — no build step)
server.py           # rebuilds manifest.json + serves locally
manifest.json       # GENERATED — never hand-edit
pages/              # standalone guide pages (no frontmatter): 1-who-am-i, 2-the-project
CONTRIBUTING.md     # how to contribute a tutorial
LICENSE.md          # MIT
learner_profile.md  # PRIVATE — gitignored, never commit
extras/             # complementary material (theory, references)
courses/<subject>/  # the curriculum, one folder per subject
```

The sidebar, top to bottom: **guide pages** first (the `pages/*.md` files in
numeric-prefix order, then `CONTRIBUTING.md`), a divider, then one collapsible
**accordion per section** — `Extras` (from `extras/`), then one per folder under
`courses/`. Section titles are the folder name prettified
(`data-structures-and-algorithms` → "Data Structures and Algorithms"). Guide
pages carry **no frontmatter** (so the `coding-tutor` skill ignores them); their
order comes from the numeric filename prefix, and the site lands on the first
one (Who am I).

## How to work here

**Build + serve:**
```bash
python3 server.py            # rebuild manifest.json, serve at http://localhost:8765/
python3 server.py --build    # rebuild manifest.json only (do this before committing)
```

**Add a tutorial:** drop a `YYYY-MM-DD-slug.md` file into `extras/` or a subject
folder under `courses/` (make a new folder to start a new subject), then run
`python3 server.py --build`. The section/entry appears automatically — no
`index.html` edits.

**Reading order:** within a section, tutorials sort by the `order:` integer in
their frontmatter (`order: 1`, `2`, …) — the intended sequence, independent of
date or filename. Always set `order:` on new tutorials so they land in the right
place; unordered ones fall back to date/title and sort last.

**Regenerate, don't edit:** `manifest.json` is built from the files. Change the
files (or add an `order:`), then `--build`. Never edit `manifest.json` by hand.

## Non-obvious things (read before changing)

- **The viewer is intentionally dependency-free.** `index.html` uses vanilla JS
  and CDN scripts (marked, highlight.js). Keep it that way — no bundler, no
  framework, no backend. It must run as plain static files.
- **The `coding-tutor` skill globs recursively.** Its scripts were patched from
  `glob("*.md")` → `rglob("*.md")` so they still find tutorials now nested under
  `courses/` and `extras/`. If the skill is reinstalled, that patch is lost and
  must be reapplied, or the skill goes blind to the library.
- **`manifest.json` paths are repo-relative** (e.g.
  `courses/data-structures-and-algorithms/2026-...md`) so the static viewer
  fetches each file directly. Don't reintroduce flat/basename-only paths.
- **`SKIP_FILES` in `server.py`** lists files that must never appear in the
  sidebar (`learner_profile.md`, `README.md`, `CLAUDE.md`, …). Add to it rather
  than special-casing elsewhere.

## Conventions

- Commit messages: English, Conventional Commits (`feat`, `fix`, `docs`,
  `refactor`, `chore`), one concern per commit.
- Never commit `learner_profile.md` (it's private and gitignored).
