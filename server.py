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
MANIFEST = SCRIPT_DIR / "manifest.json"
PORT = 8765
SKIP_FILES = {"learner_profile.md", "MEMORY.md", "README.md"}


def extract_title_and_date(md_path: Path) -> tuple[str, str]:
    """Return (title, date) for a tutorial markdown file.

    Date comes from a leading YYYY-MM-DD in the filename.
    Title is the first H1 in the body, with a filename-derived fallback.
    """
    date = ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", md_path.stem)
    if m:
        date = m.group(1)
        fallback_title = m.group(2).replace("-", " ").title()
    else:
        fallback_title = md_path.stem.replace("-", " ").title()

    title = fallback_title
    try:
        in_frontmatter = False
        with md_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped == "---":
                    in_frontmatter = not in_frontmatter
                    continue
                if not in_frontmatter and stripped.startswith("# "):
                    title = stripped[2:].strip()
                    break
    except OSError:
        pass
    return title, date


def build_manifest() -> list[dict]:
    items: list[dict] = []
    for md in sorted(SCRIPT_DIR.glob("*.md")):
        if md.name in SKIP_FILES:
            continue
        title, date = extract_title_and_date(md)
        items.append({"filename": md.name, "title": title, "date": date})
    MANIFEST.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    return items


def serve() -> None:
    os.chdir(SCRIPT_DIR)
    handler_cls = http.server.SimpleHTTPRequestHandler
    handler_cls.log_message = lambda *_a, **_kw: None  # type: ignore[assignment]
    print(f"📚 Serving {SCRIPT_DIR}")
    print(f"🌐 Open:  http://localhost:{PORT}/")
    print("   (Ctrl+C to stop)")
    with http.server.HTTPServer(("127.0.0.1", PORT), handler_cls) as httpd:
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

    items = build_manifest()
    print(f"✓ manifest.json updated ({len(items)} tutorials)")

    if args.build:
        return
    serve()


if __name__ == "__main__":
    main()
