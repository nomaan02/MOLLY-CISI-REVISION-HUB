#!/usr/bin/env python3
"""Fix link text under ### Past paper practice in topic sheets."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "knowledge-base" / "topics"


def label_for_qbank_path(rq: str) -> str:
    rq = rq.strip().replace("\\", "/")
    parts = rq.split("/")
    if len(parts) < 2:
        return rq
    sec = parts[-2]
    fname = parts[-1].replace(".md", "")
    letter = sec.replace("section-", "").upper()
    slug = fname
    if re.match(r"^\d{2}-", slug):
        slug = re.sub(r"^\d{2}-", "", slug)
    name = slug.replace("-", " ").title()
    for a, b in [
        (" Of ", " of "),
        (" And ", " and "),
        (" The ", " the "),
        ("Uk ", "UK "),
        ("Fsm ", "FSMA "),
        ("Mlr ", "MLR "),
        ("Cisi ", "CISI "),
        ("Smcr ", "SM&CR "),
        ("Mifid ", "MiFID "),
        ("Aml ", "AML "),
    ]:
        name = name.replace(a, b)
    return f"Section {letter} · {name}"


def fix_file(fp: Path) -> bool:
    raw = fp.read_text(encoding="utf-8")
    if "<!-- topic-sheet v1 -->" not in raw:
        return False

    def repl(m: re.Match[str]) -> str:
        path = m.group(1)
        return f"- [{label_for_qbank_path(path)}](../../question-bank/{path})"

    new = re.sub(
        r"- \[[^\]]+\]\(\.\./\.\./question-bank/((?:section-[abc])/[^)]+\.md)\)",
        repl,
        raw,
    )
    if new == raw:
        return False
    fp.write_text(new, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    n = 0
    for fp in TOPICS.rglob("*.md"):
        if fix_file(fp):
            n += 1
            print("Fixed labels:", fp.relative_to(ROOT))
    print(f"Done. {n} file(s) updated.")


if __name__ == "__main__":
    main()
