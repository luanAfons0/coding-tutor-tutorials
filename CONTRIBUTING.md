# Contributing

Thanks for wanting to add to this library! It started as one person's learning
trail, but extra tutorials, study notes, and references are welcome — as long as
they follow the same pattern so the viewer picks them up automatically.

This is a **static site** (plain HTML + vanilla JS, no backend, no build step).
Contributions are Markdown files plus a regenerated manifest — that's it.

## What you can contribute

- **A new tutorial in an existing subject** → add a file under that subject's
  folder, e.g. `courses/data-structures-and-algorithms/`.
- **A whole new subject** → create a new folder under `courses/`, e.g.
  `courses/rust-basics/`, and add your tutorial(s) there. It becomes its own
  section in the sidebar automatically.
- **Complementary material** (theory, references, cheatsheets — anything that
  isn't a build-it-yourself project) → add it to `extras/`.

## File naming

```
courses/<subject-slug>/YYYY-MM-DD-topic-slug.md
extras/YYYY-MM-DD-topic-slug.md
```

- `<subject-slug>` and `topic-slug` are lowercase, kebab-case
  (`data-structures-and-algorithms`, `build-a-hash-map`).
- The leading `YYYY-MM-DD` is the date; the viewer reads it for display.
- The section title in the sidebar is the **folder name**, prettified
  (`rust-basics` → "Rust Basics").

## Required frontmatter

Every tutorial starts with a YAML frontmatter block:

```yaml
---
concepts: hash_map,hashing,collisions          # comma-separated, no spaces
order: 1                                        # reading position within the section
description: One-paragraph summary of what this tutorial covers.
prerequisites: []                               # or paths to earlier tutorials
understanding_score: null                       # leave null
last_quizzed: null                              # leave null
created: DD-MM-YYYY
last_updated: DD-MM-YYYY
---

# Tutorial Title

...content...
```

- **`order:`** sets the reading sequence within the section. Pick the next free
  number for that subject (existing tutorials are `1`, `2`, …). Files without an
  `order:` fall back to date/title and sort last.
- **`understanding_score` / `last_quizzed`** are personal spaced-repetition
  fields — always submit them as `null`.
- A first-level heading (`# Title`) is the displayed title.

## Writing style

Teach one idea deeply, the way a great educator would: start with **why** the
concept matters, use concrete examples, build a mental model, and end with a
small exercise the reader can try. Fewer concepts explained well beats many
mentioned briefly.

## Before you open the PR

1. **Rebuild the manifest** and commit it:
   ```bash
   python3 server.py --build
   git add manifest.json <your-new-file>.md
   ```
   `manifest.json` is generated — never hand-edit it; just rebuild.
2. **Preview locally** to check it renders and sits in the right section:
   ```bash
   python3 server.py     # http://localhost:8765/
   ```
3. **Keep it static.** Don't add a backend, a bundler, or new dependencies, and
   don't edit `index.html` to wire up your file — the manifest does that.
4. **Don't commit personal files.** `learner_profile.md` is private and
   gitignored; never add it.

## PR checklist

- [ ] File is in `courses/<subject>/` or `extras/`, named `YYYY-MM-DD-slug.md`
- [ ] Frontmatter present, with `order:` set and quiz fields `null`
- [ ] `python3 server.py --build` run and `manifest.json` committed
- [ ] Renders correctly in the local preview
- [ ] No backend/dependency changes, no `index.html` edits, no personal files

Open the PR with a short note on what you're adding and why it's a good fit.
Thanks for contributing! 🚀
