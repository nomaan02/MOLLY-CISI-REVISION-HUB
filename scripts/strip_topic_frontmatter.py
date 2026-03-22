#!/usr/bin/env python3
"""
Remove YAML frontmatter and <!-- topic-sheet v1 --> from topic .md files so
content starts at the # heading (human-readable sheet only).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "knowledge-base" / "topics"

MARKERS = (
    "<!-- topic-sheet v1 -->",
    "<!-- topic-sheet-v1 -->",  # tolerate variant
)


def strip_prefix(raw: str) -> tuple[str, bool]:
    for m in MARKERS:
        i = raw.find(m)
        if i != -1:
            rest = raw[i + len(m) :]
            rest = rest.lstrip("\n\r")
            return rest, True
    return raw, False


def main() -> None:
    n = 0
    for fp in sorted(TOPICS.rglob("*.md")):
        raw = fp.read_text(encoding="utf-8")
        new, changed = strip_prefix(raw)
        if not changed:
            print("SKIP (no marker):", fp.relative_to(ROOT), file=sys.stderr)
            continue
        if new == raw:
            continue
        fp.write_text(new, encoding="utf-8", newline="\n")
        print("Stripped:", fp.relative_to(ROOT))
        n += 1
    print(f"Done. Updated {n} file(s).")


if __name__ == "__main__":
    main()
