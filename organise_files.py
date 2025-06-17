#!/usr/bin/env python3
"""
organise_files.py
─────────────────
• Sorts loose video files into series / movie folders.
• Handles episode names such as:
      [SubsPlease] Series Title - 03v2 (720p) [ABCDEF12].mkv
      [SubsPlease] Aparida - 09.5 (720p) [F40254DB].mkv
• Handles movie names such as:
      I Want to Eat Your Pancreas (2018) 1080p AV1 Opus [UnAV1Chain] v2.mkv
      Nausicaä of the Valley of the Wind (1984) 1080p AV1 Opus Dual‑Audio [...].mkv
• Updates each folder’s mtime to its newest file (recursive).

Usage
-----
    python organise_files.py              # organise current directory
    python organise_files.py "/path/to/dir"
"""

import os
import re
import shutil
import sys
from pathlib import Path

# ────────────────────────── patterns ──────────────────────────────────────
PATTERNS = [
    # Fansubbed TV episodes
    re.compile(
        r"""^\s*
        \[[^\]]+\]              # leading [Group]
        \s+
        (?P<title>.*?)          # series title
        \s*-\s*
        (?:                     # episode:
            \d+(?:\.\d+)?       #   01   or  09.5
            (?:v\d+)?           #   v2   (optional)
        )
        (?:\s*\([^)]+\))?       # optional (720p)
        \s*\[[0-9A-Fa-f]+\]     # trailing hash
        \.[A-Za-z0-9]+$         # extension
    """,
        re.VERBOSE,
    ),
    # Stand‑alone movies  Title (YEAR) ...
    re.compile(
        r"""^\s*
        (?:\[[^\]]+\]\s+)?      # optional leading [Group]
        (?P<title>.+?)\s*       # movie title
        \(\d{4}\)               # (YEAR)
        .*?\.[A-Za-z0-9]+$      # rest + extension
    """,
        re.VERBOSE,
    ),
]

INVALID_CHARS = re.compile(r'[\\/:*?"<>|]')  # Win‑invalid


# ────────────────────────── helpers ───────────────────────────────────────
def sanitize(name: str) -> str:
    """Replace filesystem‑forbidden characters with underscores."""
    return INVALID_CHARS.sub("_", name).strip()


def extract_title(filename: str) -> str | None:
    """Return folder title for *filename* or None if no pattern matches."""
    for pat in PATTERNS:
        m = pat.match(filename)
        if m:
            return sanitize(m.group("title"))
    return None


def sync_folder_mtime(folder: Path) -> None:
    """Set *folder*'s mtime to the newest file it (recursively) contains."""
    mtimes = [p.stat().st_mtime for p in folder.rglob("*") if p.is_file()]
    if mtimes:
        newest = max(mtimes)
        os.utime(folder, (newest, newest))  # (atime, mtime)


# ────────────────────────── core organiser ────────────────────────────────
def organise(root: Path) -> None:
    moved = 0
    for entry in root.iterdir():
        if entry.is_dir():
            continue  # process only files

        title = extract_title(entry.name)
        if not title:
            continue

        dest_dir = root / title
        dest_dir.mkdir(exist_ok=True)

        target = dest_dir / entry.name
        if target.exists():
            print(f"⚠️  Skipped (already exists): {target}")
            continue

        shutil.move(str(entry), target)
        moved += 1
        print(f"✔︎  Moved: {entry.name} → {dest_dir.name}/")

    # Update timestamps for *all* first‑level sub‑folders
    for sub in root.iterdir():
        if sub.is_dir():
            sync_folder_mtime(sub)

    print(f"\nDone. {moved} file(s) moved; folder timestamps updated.")


# ────────────────────────── entry‑point ───────────────────────────────────
if __name__ == "__main__":
    root_arg = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root_arg.is_dir():
        sys.exit(f"Error: {root_arg} is not a directory.")
    organise(root_arg)
