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

### Files

| File | Purpose |
|------|---------|
| `index.html` | The viewer (sidebar + rendered markdown). |
| `server.py` | Rebuilds `manifest.json` and optionally serves locally. |
| `manifest.json` | Auto-generated. Lists every tutorial for the sidebar. |
| `*.md` | The tutorials. |
| `learner_profile.md` | **Private.** Listed in `.gitignore`, won't be pushed. |
