#!/usr/bin/env python3
"""Add readable title blocks to Section A & B question bank files."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Install PyYAML: pip install pyyaml", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
QBANK = ROOT / "knowledge-base" / "question-bank"
TOPICS = ROOT / "knowledge-base" / "topics"
MARKER = "<!-- question-bank-sheet v1 -->"


def split_frontmatter_raw(raw: str) -> tuple[str, dict, str] | tuple[None, None, None]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", raw, re.DOTALL)
    if not m:
        return None, None, None
    fm_text, body = m.group(1), m.group(2)
    try:
        data = yaml.safe_load(fm_text)
        if not isinstance(data, dict):
            return None, None, None
        return fm_text, data, body
    except yaml.YAMLError:
        return None, None, None


def rel_to(from_file: Path, to_file: Path) -> str:
    return os.path.relpath(to_file, from_file.parent).replace("\\", "/")


def load_topic_titles() -> dict[str, str]:
    out: dict[str, str] = {}
    for fp in TOPICS.rglob("*.md"):
        rel = fp.relative_to(TOPICS).as_posix()
        raw = fp.read_text(encoding="utf-8")
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", raw, re.DOTALL)
        if not m:
            continue
        try:
            data = yaml.safe_load(m.group(1))
            if isinstance(data, dict) and "topic" in data:
                out[rel] = data["topic"]
        except yaml.YAMLError:
            continue
    return out


def build_header(fp: Path, data: dict, titles: dict[str, str]) -> str:
    sec = data.get("section", "?")
    if sec == "A":
        name = data.get("topic_category", "Section A")
        qrange = data.get("question_range", "")
        qcount = data.get("question_count", "")
        freq = data.get("frequency_note", "")
        title = f"Section A — {name}"
        meta_rows = [
            "| **Paper section** | A |",
            f"| **Topic category** | {name} |",
            f"| **Question range** | {qrange} |",
            f"| **Count** | {qcount} questions |",
        ]
    elif sec == "B":
        name = data.get("topic_cluster", "Section B")
        qs = data.get("questions_included", [])
        qcount = data.get("question_count", len(qs))
        comp = data.get("compulsory_questions", [])
        title = f"Section B — {name}"
        comp_note = f"{len(comp)} listed as compulsory practice" if comp else "See file for compulsory markers"
        meta_rows = [
            "| **Paper section** | B (scenarios) |",
            f"| **Topic cluster** | {name} |",
            f"| **Questions** | {qcount} scenarios |",
            f"| **Compulsory set** | {comp_note} |",
        ]
    else:
        return ""

    lines = [
        MARKER,
        "",
        f"# {title}",
        "",
        "> **About this file:** Past paper questions with **model answers** for self-marking. Section A: short factual answers; Section B: apply IRAC / ethics and use the CISI Code where relevant.",
    ]
    if sec == "A" and freq:
        lines.append(f"> {freq}")
    lines.extend(
        [
            "",
            "| | |",
            "|:---|:---|",
        ]
    )
    lines.extend(meta_rows)
    lines.extend(["", "### Study notes (topic files)", ""])

    maps = data.get("maps_to") or []
    for mpath in maps:
        mpath = mpath.strip().replace("\\", "/")
        if mpath.startswith("topics/"):
            rel = mpath[len("topics/") :]
        else:
            rel = mpath
        tgt = TOPICS / rel
        if tgt.exists():
            label = titles.get(rel, rel.replace(".md", "").replace("-", " ").title())
            href = rel_to(fp, tgt)
            lines.append(f"- [{label}]({href})")
        else:
            lines.append(f"- *({rel} — path not found in vault; update frontmatter if needed)*")

    if not maps:
        lines.append("- *(no maps_to in frontmatter)*")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def process_file(fp: Path, titles: dict[str, str]) -> bool:
    raw = fp.read_text(encoding="utf-8")
    if MARKER in raw:
        return False
    fm_text, data, body = split_frontmatter_raw(raw)
    if data is None:
        return False
    sec = data.get("section")
    if sec not in ("A", "B"):
        return False

    topic = data.get("topic_category") or data.get("topic_cluster") or "Question bank"
    if "title" not in data:
        fm_text = "title: " + json.dumps(f"{sec} — {topic}", ensure_ascii=False) + "\n" + fm_text

    header = build_header(fp, data, titles)
    if not header:
        return False
    new_raw = f"---\n{fm_text}\n---\n\n{header}{body}"
    fp.write_text(new_raw, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    titles = load_topic_titles()
    n = 0
    for fp in sorted(QBANK.rglob("*.md")):
        if process_file(fp, titles):
            print("Updated:", fp.relative_to(ROOT))
            n += 1
    print(f"Done. Updated {n} question bank file(s).")


if __name__ == "__main__":
    main()
