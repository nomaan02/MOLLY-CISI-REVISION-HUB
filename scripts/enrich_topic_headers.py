#!/usr/bin/env python3
"""
Insert structured title block after YAML frontmatter in topic .md files.
Idempotent via <!-- topic-sheet v1 -->.
"""
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
TOPICS = ROOT / "knowledge-base" / "topics"
QBANK = ROOT / "knowledge-base" / "question-bank"
MARKER = "<!-- topic-sheet v1 -->"

TOPIC_SUMMARIES: dict[str, str] = {
    "fsma-regulated-activities": "FSMA 2000 as the backbone of UK regulation: statutory objectives, the FCA/PRA split, general prohibition, regulated activities, authorisation, and interfaces with market abuse and enforcement.",
    "international-regulation-us-asia": "Awareness-level survey of major non-UK regimes (e.g. US, key Asian centres) and international standard-setters — useful for Section C context and perimeter questions.",
    "pra-fca-structure-supervision": "How the PRA and FCA are structured, their statutory objectives, threshold conditions, supervision and policy tools, and solo- vs dual-regulated firms.",
    "smcr-senior-managers": "SM&CR: Senior Managers Regime, Certification Regime, conduct rules, handover, regulatory references — core individual accountability content for scenarios.",
    "aper-cocon-prin": "APER (legacy), COCON, and the Principles for Businesses — how high-level duties and conduct rules apply to firms and staff.",
    "consumer-duty": "Consumer Duty (PRIN 12): outcomes, cross-cutting rules, retail customer definition, and how it changes COBS and governance expectations.",
    "sysc-systems-controls": "SYSC 1–9: governance, risk control, compliance, audit, outsourcing, conflicts, CASS oversight — systems and controls the examiner tests often.",
    "sysc-conflicts-remuneration": "Conflicts of interest (SYSC 10), remuneration (SYSC 19A), and how they interact with COBS and ethics scenarios.",
    "threshold-conditions-fitness-tc": "Threshold Conditions, fitness and propriety, TC and competence — gatekeeping for authorisation and ongoing standing.",
    "cobs-obligations-inducements": "COBS business standards, client communications, inducements and gifts — MiFID conduct baseline for retail and professional business.",
    "cobs-client-categorisation": "Client categorisation (retail, professional, eligible counterparty), elective professional, and consequences for conduct rules.",
    "cobs-financial-promotions": "Financial promotions: s21 FSMA, COBS 4, fair clear not misleading — heavily examined with real-world media angles.",
    "cobs-information-agreements-product-governance": "Disclosure, agreements, advice vs guidance, and product governance / target market under COBS and related rules.",
    "cobs-suitability-appropriateness": "Suitability (advice) and appropriateness (non-advised) — MiFID investor protection and Consumer Duty overlay.",
    "cobs-dealing-managing": "Order handling, best execution, churning, reporting and post-trade obligations in COBS dealing and managing.",
    "cass-client-assets": "CASS: safeguarding and administration of client assets and money — rules, resolution, and breach risk.",
    "sup-supervision-perg": "SUP processes (notifications, waivers) and PERG on whether activities are regulated — perimeter and authorisation practice.",
    "depp-enforcement-penalties": "DEPP: enforcement process, statutory notices, penalty factors, settlement — how regulators sanction firms and individuals.",
    "redress-complaints-compensation": "DISP, FOS jurisdiction and process, FSCS limits — complaints and compensation end-to-end.",
    "takeover-panel-principles": "Takeover Panel, six general principles, mandatory bid rule — foundation for bid behaviour.",
    "takeover-code-rules": "Detailed Takeover Code rules, timetable, documents — application in scenarios.",
    "listing-rules-dtr": "UKLR / listing regime and DTR continuing obligations — issuers, inside information, and control transactions.",
    "aim-prospectus-rules": "AIM, prospectus regulation, Model Code — smaller listings and share-dealing codes.",
    "market-abuse-mar": "MAR: insider dealing, unlawful disclosure, market manipulation, suspicious orders and reporting — EU-derived UK regime.",
    "insider-dealing": "Criminal insider dealing (CJA 1993), defences, and overlap with MAR civil regime.",
    "money-laundering-poca-mlr": "POCA offences, MLR 2017, JMLSG, CDD, SARs — financial crime chapter staple.",
    "financial-crime-terrorism-sanctions": "Terrorist financing, sanctions lists, proliferation — firm systems and offences.",
    "bribery-act": "Bribery Act 2010: offences, adequate procedures, corporate failure to prevent — essay and scenario material.",
    "data-protection-whistleblowing": "UK GDPR/DPA 2018 essentials for firms, and whistleblowing (including SYSC 18 context).",
    "financial-benchmarks": "Benchmark regulation — awareness of manipulation risk and oversight (lower exam weight).",
    "esg-climate-cryptoassets": "ESG disclosure, climate risk, cryptoasset promotions and conduct — topical Section C angles.",
    "markets-and-exchanges": "RIE, MTF, OTF, SI and market definitions — skim-level factual recall.",
    "current-regulatory-developments": "Brexit, Edinburgh Reforms, SM&CR reviews, digital — essay background, not deep memorisation.",
    "compliance-function-principles": "BIS 10 principles and the role of the compliance function — board, independence, resourcing.",
    "ethics-integrity-cisi-code": "CISI Code of Conduct and ethics — compulsory Section B question territory.",
}


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


def qbank_link_label(rq: str) -> str:
    """Human-readable label for a question-bank path, e.g. section-a/01-uk-regulatory-structure.md."""
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


def build_header(data: dict, fp: Path, topic_titles: dict[str, str]) -> str:
    topic = data.get("topic", fp.stem)
    syllabus = data.get("syllabus_part", "")
    ch = data.get("chapter", "")
    w = data.get("chapter_exam_weight", "")
    kl = data.get("knowledge_level", "")
    pr = data.get("exam_priority", "")
    stem = fp.stem

    summary = TOPIC_SUMMARIES.get(
        stem,
        f"Workbook coverage of **{topic}** for CISI Level 6 Regulation & Compliance — see syllabus scope and linked questions below.",
    )

    lines = [
        MARKER,
        "",
        f"# {topic}",
        "",
        "> **What this note covers:** " + summary,
        "",
        "| | |",
        "|:---|:---|",
        f'| **Syllabus** | {syllabus} |',
        f"| **Chapter weight** | ≈ {w} (Chapter {ch}) |",
        f"| **Depth** | {kl} · **Priority:** {pr} |",
        "",
        "### Related topics",
        "",
    ]

    for ref in data.get("cross_references") or []:
        ref = ref.strip()
        tgt = TOPICS / ref
        label = topic_titles.get(ref, ref.replace(".md", "").replace("-", " ").title())
        href = rel_to(fp, tgt)
        lines.append(f"- [{label}]({href})")

    if not (data.get("cross_references") or []):
        lines.append("- *(none listed in frontmatter)*")

    lines.extend(["", "### Past paper practice", ""])

    for rq in data.get("related_questions") or []:
        rq = rq.strip()
        tgt = QBANK / rq
        label = qbank_link_label(rq)
        href = rel_to(fp, tgt)
        lines.append(f"- [{label}]({href})")

    if not (data.get("related_questions") or []):
        lines.append("- *(none listed in frontmatter)*")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def load_all_topic_titles() -> dict[str, str]:
    out: dict[str, str] = {}
    for fp in TOPICS.rglob("*.md"):
        rel = fp.relative_to(TOPICS).as_posix()
        raw = fp.read_text(encoding="utf-8")
        _, data, _ = split_frontmatter_raw(raw)
        if data and "topic" in data:
            out[rel] = data["topic"]
    return out


def ensure_title_line(fm_text: str, topic: str) -> str:
    if re.search(r"(?m)^title:\s", fm_text):
        return fm_text
    return "title: " + json.dumps(topic, ensure_ascii=False) + "\n" + fm_text


def process_file(fp: Path, topic_titles: dict[str, str]) -> bool:
    raw = fp.read_text(encoding="utf-8")
    if MARKER in raw:
        return False
    fm_text, data, body = split_frontmatter_raw(raw)
    if data is None:
        print(f"SKIP (no valid YAML): {fp.relative_to(ROOT)}", file=sys.stderr)
        return False

    topic = data.get("topic", fp.stem)
    if "title" not in data:
        fm_text = ensure_title_line(fm_text, topic)

    header = build_header(data, fp, topic_titles)
    new_raw = f"---\n{fm_text}\n---\n\n{header}{body}"
    fp.write_text(new_raw, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    topic_titles = load_all_topic_titles()
    n = 0
    for fp in sorted(TOPICS.rglob("*.md")):
        if process_file(fp, topic_titles):
            print("Updated:", fp.relative_to(ROOT))
            n += 1
    print(f"Done. Updated {n} file(s).")


if __name__ == "__main__":
    main()
