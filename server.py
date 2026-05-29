#!/usr/bin/env python3
"""
Local viewer + manifest builder for the tutorials in this directory.

This is a fully static site (no custom backend). The browser fetches
`manifest.json` to know which tutorials exist, then fetches each `.md` file
directly. That means it works identically locally and on GitHub Pages.

Two modes:

  python3 server.py            # rebuild manifest.json, then serve locally
                               # at http://localhost:8765/
  python3 server.py --build    # rebuild manifest.json only (e.g. before
                               # `git commit && git push` to GitHub Pages)
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
COURSES_DIR = SCRIPT_DIR / "courses"
MANIFEST = SCRIPT_DIR / "manifest.json"
PORT = 8765
SKIP_FILES = {"learner_profile.md", "MEMORY.md", "README.md", "CLAUDE.md"}

# Small words kept lowercase when prettifying a subject folder name.
_SMALL_WORDS = {"and", "or", "of", "the", "to", "a", "an", "in", "on", "for"}


def prettify_subject(slug: str) -> str:
    """Turn a folder slug like 'data-structures-and-algorithms' into a title."""
    words = slug.replace("_", "-").split("-")
    out = []
    for i, w in enumerate(words):
        if i != 0 and w in _SMALL_WORDS:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def extract_meta(md_path: Path) -> tuple[str, str, int | None]:
    """Return (title, date, order) for a tutorial markdown file.

    Date comes from a leading YYYY-MM-DD in the filename.
    Title is the first H1 in the body, with a filename-derived fallback.
    Order is the `order:` frontmatter field (the intended reading position),
    or None if absent.
    """
    date = ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", md_path.stem)
    if m:
        date = m.group(1)
        fallback_title = m.group(2).replace("-", " ").title()
    else:
        fallback_title = md_path.stem.replace("-", " ").title()

    title = fallback_title
    order: int | None = None
    try:
        in_frontmatter = False
        with md_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped == "---":
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and stripped.startswith("order:"):
                    try:
                        order = int(stripped.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                if not in_frontmatter and stripped.startswith("# "):
                    title = stripped[2:].strip()
                    break
    except OSError:
        pass
    return title, date, order


def collect_items(dir_path: Path) -> list[dict]:
    """Collect tutorial entries from a directory (recursively).

    Each `path` is relative to this directory so the static viewer can fetch
    it directly (e.g. "courses/data-structures-and-algorithms/2026-...md").
    """
    items: list[dict] = []
    for md in sorted(dir_path.rglob("*.md")):
        if md.name in SKIP_FILES:
            continue
        title, date, order = extract_meta(md)
        items.append({
            "filename": md.name,
            "path": md.relative_to(SCRIPT_DIR).as_posix(),
            "title": title,
            "date": date,
            "order": order,
        })
    # Intended reading order first (explicit `order:`); fall back to date/title
    # for any tutorial that hasn't been given one yet (sentinel sends them last).
    items.sort(key=lambda it: (it["order"] if it["order"] is not None else 10**9,
                               it["date"], it["title"]))
    return items


def build_manifest() -> dict:
    """Build a sectioned manifest the viewer renders as accordions.

    Shape:
        {
          "sections": [ { "id", "title", "items": [...] }, ... ],
          "about": { "path": "about.md", "title": "..." }   # optional
        }

    Sections, in order: "Extras" (complementary content under extras/), then
    one section per subject folder under courses/.
    """
    sections: list[dict] = []

    extras_dir = SCRIPT_DIR / "extras"
    if extras_dir.is_dir():
        items = collect_items(extras_dir)
        if items:
            sections.append({"id": "extras", "title": "Extras", "items": items})

    if COURSES_DIR.is_dir():
        for subject_dir in sorted(p for p in COURSES_DIR.iterdir() if p.is_dir()):
            items = collect_items(subject_dir)
            if items:
                sections.append({
                    "id": subject_dir.name,
                    "title": prettify_subject(subject_dir.name),
                    "items": items,
                })

    manifest: dict = {"sections": sections}

    # Standalone pages pinned at the bottom of the sidebar. Files in pages/ are
    # ordered by their numeric filename prefix (1-..., 2-...); CONTRIBUTING.md
    # (kept at the repo root for GitHub) is appended last.
    pages: list[dict] = []
    pages_dir = SCRIPT_DIR / "pages"
    if pages_dir.is_dir():
        for md in sorted(pages_dir.glob("*.md")):
            if md.name in SKIP_FILES:
                continue
            title, _, _ = extract_meta(md)
            pages.append({"path": md.relative_to(SCRIPT_DIR).as_posix(), "title": title})

    contributing = SCRIPT_DIR / "CONTRIBUTING.md"
    if contributing.exists():
        title, _, _ = extract_meta(contributing)
        pages.append({"path": "CONTRIBUTING.md", "title": title or "Contributing"})

    if pages:
        manifest["pages"] = pages

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def serve() -> None:
    os.chdir(SCRIPT_DIR)
    handler_cls = http.server.SimpleHTTPRequestHandler
    handler_cls.log_message = lambda *_a, **_kw: None  # type: ignore[assignment]
    print(f"📚 Serving {SCRIPT_DIR}")
    print(f"🌐 Open:  http://localhost:{PORT}/")
    print("   (Ctrl+C to stop)")
    # ThreadingHTTPServer: handle requests concurrently. The single-threaded
    # HTTPServer blocks on one (keep-alive) connection at a time, which makes
    # browsers appear to "load forever".
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler_cls) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build",
        action="store_true",
        help="only rebuild manifest.json (do not start the server)",
    )
    args = parser.parse_args()

    manifest = build_manifest()
    total = sum(len(s["items"]) for s in manifest["sections"])
    print(f"✓ manifest.json updated ({total} tutorials, {len(manifest['sections'])} sections)")

    if args.build:
        return
    serve()


if __name__ == "__main__":
    main()
