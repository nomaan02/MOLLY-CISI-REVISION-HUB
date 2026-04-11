"""
CISI Diploma Revision Hub
Level 6 Regulation & Compliance — Streamlit Study Interface
Built by NakoLabs
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import re
import random

# ─── CONFIG ───────────────────────────────────────────────────────────────────

KB_ROOT = Path(__file__).parent / "knowledge-base"
PROGRESS_FILE = Path(__file__).parent / "progress.json"

PART_ORDER = [
    "part-1-regulatory-framework",
    "part-2-fca-handbook",
    "part-3-other-regulatory",
    "part-4-markets-exchanges",
    "part-5-current-developments",
    "risk-in-financial-services",
]

PART_LABELS = {
    "part-1-regulatory-framework": "Part 1 — Regulatory Framework (20%)",
    "part-2-fca-handbook": "Part 2 — FCA Handbook (40%)",
    "part-3-other-regulatory": "Part 3 — Other Regulatory (20%)",
    "part-4-markets-exchanges": "Part 4 — Markets & Exchanges (2.5%)",
    "part-5-current-developments": "Part 5 — Current Developments (2.5%)",
    "risk-in-financial-services": "Part 6 — Risk in Financial Services (15%)",
}

PART_SHORT_LABELS = {
    "part-1-regulatory-framework": "Part 1 — Regulatory Framework",
    "part-2-fca-handbook": "Part 2 — FCA Handbook",
    "part-3-other-regulatory": "Part 3 — Other Regulatory",
    "part-4-markets-exchanges": "Part 4 — Markets & Exchanges",
    "part-5-current-developments": "Part 5 — Current Developments",
    "risk-in-financial-services": "Part 6 — Risk in Financial Services",
}

PART_WEIGHTS = {
    "part-1-regulatory-framework": "20%",
    "part-2-fca-handbook": "40%",
    "part-3-other-regulatory": "20%",
    "part-4-markets-exchanges": "2.5%",
    "part-5-current-developments": "2.5%",
    "risk-in-financial-services": "15%",
}

SECTION_LABELS = {
    "section-a": "Section A",
    "section-b": "Section B",
    "section-c": "Section C",
}

GIFS_DIR = Path(__file__).parent / "gifs"

CHEER_MESSAGES = [
    "wwwwwWWWWOOOOOOOOOOOO. YYYYYEEEEEAAhhhhhhhhhh",
    "Bravest button in queef ville fr",
    "the jews would hate to see you win here babe",
    "luv luv luv",
    "You're gonna absolutely smash this exam.",
    "'go molly go molly', they all cheered benevolantly",
    "hope you like da gifs bby",
    "You've got more determination than the FCA has regulations.(ai generated but kind of slaps)",
    "Keep going — future you will say thanks.",
    "SM&CR? More like SM&CRUSH IT. - lol another ai one ",
    "#mollyisthebest",
    "I'm so proud of my hardworking mummy - Polly, aged 6 months",
    "wow guys wowww, shes so smart. wtf. i wish i was smart like her wowwww",
    "love you sunshine",
    "Every page you read is a page closer to Bristol. - Malala",
    "deep breaths shorty locks, deep breaths",
    "she's my hero guys. wtf. shes my hero. omg",
    "Bristol awaits us baby!!!",
    "BS5 6HS",
    "I heard the FCA or compliance doesn't exists in bristol # fun fact",
]

# ─── PERSISTENT PROGRESS ─────────────────────────────────────────────────────


def _empty_progress() -> dict:
    return {"covered": [], "flagged": [], "notes_log": {}}


def load_progress() -> dict:
    """Load progress data from JSON file, migrating old format if needed."""
    data = _empty_progress()
    if PROGRESS_FILE.exists():
        try:
            raw = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return data

        data["covered"] = raw.get("covered", [])
        data["flagged"] = raw.get("flagged", [])
        data["notes_log"] = raw.get("notes_log", {})

        # Migrate old single-string notes into notes_log entries
        old_notes = raw.get("notes", {})
        if old_notes:
            for key, text in old_notes.items():
                if text and text.strip():
                    if key not in data["notes_log"]:
                        data["notes_log"][key] = []
                    # Only migrate if not already present
                    existing_texts = {e["text"] for e in data["notes_log"][key]}
                    if text.strip() not in existing_texts:
                        data["notes_log"][key].append({
                            "text": text.strip(),
                            "timestamp": "Migrated",
                        })
            # Save the migrated version (drops old "notes" key)
            save_progress(data)

    return data


def save_progress(data: dict):
    """Save progress data to JSON file."""
    PROGRESS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_topic_key(file_path: Path) -> str:
    """Stable key for a topic file relative to knowledge-base."""
    try:
        return str(file_path.relative_to(KB_ROOT))
    except ValueError:
        return str(file_path)


def add_note_entry(progress: dict, topic_key: str, text: str):
    """Append a timestamped note entry to the log for a topic."""
    if "notes_log" not in progress:
        progress["notes_log"] = {}
    if topic_key not in progress["notes_log"]:
        progress["notes_log"][topic_key] = []
    progress["notes_log"][topic_key].append({
        "text": text.strip(),
        "timestamp": datetime.now().strftime("%d %b %Y  %H:%M"),
    })
    save_progress(progress)


def delete_note_entry(progress: dict, topic_key: str, index: int):
    """Delete a single note entry by index."""
    entries = progress.get("notes_log", {}).get(topic_key, [])
    if 0 <= index < len(entries):
        entries.pop(index)
        if not entries:
            progress["notes_log"].pop(topic_key, None)
        save_progress(progress)


def get_notes_for_topic(progress: dict, topic_key: str) -> list[dict]:
    """Return list of {text, timestamp} entries for a topic."""
    return progress.get("notes_log", {}).get(topic_key, [])


def count_topics_with_notes(progress: dict) -> int:
    return len([k for k, v in progress.get("notes_log", {}).items() if v])


def total_note_entries(progress: dict) -> int:
    return sum(len(v) for v in progress.get("notes_log", {}).values())


# ─── HELPERS ──────────────────────────────────────────────────────────────────


def slug_to_title(slug: str) -> str:
    slug = re.sub(r"^\d{1,2}-", "", slug)
    slug = slug.removesuffix(".md")
    acronyms = {
        "fca", "pra", "cobs", "sysc", "cass", "depp", "sup", "aper",
        "smcr", "mar", "dtr", "tc", "aml", "mifid", "emir", "uk",
        "eu", "esma", "hmrc", "fsma", "eba", "bis", "iosco",
    }
    words = slug.split("-")
    return " ".join(w.upper() if w.lower() in acronyms else w.capitalize() for w in words)


def collect_md_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [f for f in sorted(directory.glob("*.md")) if f.name != "index.md"]


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Could not read file: {e}"


def search_files(query: str, root: Path) -> list[tuple[str, Path]]:
    results = []
    query_lower = query.lower()
    for md_file in sorted(root.rglob("*.md")):
        if md_file.name == "index.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8").lower()
            if query_lower in content or query_lower in md_file.stem:
                rel = md_file.relative_to(root)
                label = " > ".join(slug_to_title(p) for p in [*rel.parent.parts, rel.stem])
                results.append((label, md_file))
        except Exception:
            continue
    return results


def count_all_topic_files() -> int:
    topics_dir = KB_ROOT / "topics"
    if not topics_dir.exists():
        return 0
    return len([f for f in topics_dir.rglob("*.md") if f.name != "index.md"])


def get_part_progress(part_key: str, progress: dict) -> tuple[int, int, list[Path]]:
    files = collect_md_files(KB_ROOT / "topics" / part_key)
    covered = sum(1 for f in files if get_topic_key(f) in progress.get("covered", []))
    return covered, len(files), files


def sidebar_topic_label(f: Path, progress: dict) -> str:
    key = get_topic_key(f)
    parts = []
    if key in progress.get("covered", []):
        parts.append("✅")
    if key in progress.get("flagged", []):
        parts.append("🚩")
    parts.append(slug_to_title(f.stem))
    return " ".join(parts)


def resolve_part_key(topic_path: Path) -> str | None:
    """Get the part key from a topic file path."""
    try:
        rel = topic_path.relative_to(KB_ROOT / "topics")
        return rel.parts[0] if rel.parts else None
    except ValueError:
        return None


# ─── PARTY MODE DIALOG ────────────────────────────────────────────────────────


@st.dialog("🎉 You've got this!")
def party_mode_popup():
    gifs = list(GIFS_DIR.glob("*.gif"))
    if gifs:
        st.image(str(random.choice(gifs)), use_container_width=True)
    st.markdown(f"**{random.choice(CHEER_MESSAGES)}**")


# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CISI Revision Hub",
    page_icon="🐈‍⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM STYLING ──────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp { font-family: 'Inter', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f8f9fc;
    border-right: 1px solid #e2e4eb;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem;
    padding: 4px 0;
}

/* Widen main area to use full width for 2-column layout */
.main .block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

/* Markdown */
.stMarkdown h1 { font-size: 1.7rem; font-weight: 700; margin-top: 1.5rem; }
.stMarkdown h2 { font-size: 1.35rem; font-weight: 600; margin-top: 1.3rem; color: #1a1a2e; }
.stMarkdown h3 { font-size: 1.15rem; font-weight: 600; margin-top: 1rem; color: #2d2d44; }
.stMarkdown p  { font-size: 1rem; line-height: 1.75; color: #333; }
.stMarkdown li { font-size: 1rem; line-height: 1.7; }
.stMarkdown code { background: #f0f2f6; padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; }
.stMarkdown blockquote {
    border-left: 4px solid #4a6cf7; padding-left: 1rem; color: #555;
    background: #f8f9ff; margin: 1rem 0; padding: 0.8rem 1rem;
    border-radius: 0 6px 6px 0;
}

/* Badges */
.badge-covered {
    display: inline-block; background: #e8f5e9; color: #2e7d32;
    padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;
}
.badge-flagged {
    display: inline-block; background: #fff3e0; color: #e65100;
    padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;
}
.badge-weight {
    display: inline-block; background: #e3f2fd; color: #1565c0;
    padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;
}
.badge-notes {
    display: inline-block; background: #f3e5f5; color: #7b1fa2;
    padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;
}

/* Overall progress bar */
.overall-progress-bar {
    background: #e8eaef; border-radius: 8px; height: 12px;
    overflow: hidden; margin: 0.5rem 0;
}
.overall-progress-fill {
    height: 100%; border-radius: 8px;
    background: linear-gradient(90deg, #4a6cf7, #6dd5ed);
    transition: width 0.4s ease;
}

/* Notes panel */
.notes-panel-header {
    background: #4a6cf7;
    color: white;
    padding: 10px 14px;
    font-size: 0.88rem;
    font-weight: 600;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
}
.note-entry {
    background: #f8f9fc;
    border-left: 3px solid #4a6cf7;
    padding: 6px 8px;
    border-radius: 0 4px 4px 0;
    font-size: 0.84rem;
    line-height: 1.4;
    color: #333;
}
.note-entry .note-ts {
    display: block;
    font-size: 0.7rem;
    color: #999;
    margin-top: 2px;
}
.note-empty {
    color: #aaa;
    font-size: 0.85rem;
    font-style: italic;
    padding: 8px 0;
}

/* Notebook view */
.notebook-topic-header {
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a2e;
    padding: 8px 0 4px 0;
    border-bottom: 1px solid #eee;
    margin-top: 1rem;
}
.notebook-part-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #4a6cf7;
    margin-top: 1.5rem;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


# ─── LOAD PROGRESS + SESSION STATE ───────────────────────────────────────────

progress = load_progress()

if "visited" not in st.session_state:
    st.session_state.visited = set()
if "active_topic" not in st.session_state:
    st.session_state.active_topic = None


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📚 CISI Revision Hub")
    st.caption("Level 6 · Regulation & Compliance")
    st.markdown("---")

    st.toggle("🐾 GIFs on pages", key="party_gifs")
    st.markdown("---")

    search_query = st.text_input("🔍 Search topics", placeholder="e.g. SMCR, market abuse")

    if search_query and search_query.strip():
        results = search_files(search_query.strip(), KB_ROOT)
        if results:
            st.markdown(f"**{len(results)} result{'s' if len(results) != 1 else ''}**")
            selection_labels = [r[0] for r in results]
            chosen = st.radio("Results", selection_labels, label_visibility="collapsed")
            chosen_path = results[selection_labels.index(chosen)][1]
            nav_mode = "search"
        else:
            st.info("No results found.")
            nav_mode = "none"
            chosen_path = None

    elif st.session_state.active_topic is not None:
        # ── Persistent direct-navigation mode ──
        nav_mode = "active"
        chosen_path = None

        if st.button("← Back to menu", use_container_width=True):
            st.session_state.active_topic = None
            st.rerun()

        target = st.session_state.active_topic
        at_part_key = target.get("part")
        if at_part_key:
            st.markdown("---")
            st.info(PART_SHORT_LABELS.get(at_part_key, at_part_key))
            topics_dir = KB_ROOT / "topics"
            part_files = collect_md_files(topics_dir / at_part_key)
            if part_files:
                at_topic_path = Path(target["topic_file"])
                current_idx = next(
                    (i for i, f in enumerate(part_files) if str(f) == str(at_topic_path)), 0
                )
                topic_choice = st.radio(
                    "Other topics in this part",
                    part_files,
                    index=current_idx,
                    format_func=lambda f: sidebar_topic_label(f, progress),
                    key="active_topic_radio",
                )
                if str(topic_choice) != str(at_topic_path):
                    st.session_state.active_topic = {
                        "part": at_part_key,
                        "topic_file": str(topic_choice),
                    }
                    st.rerun()

    else:
        nav_mode = "browse"
        chosen_path = None

        view = st.radio(
            "Section",
            ["🏠 Home", "📖 Study Topics", "❓ Question Bank", "📝 Notes Notebook", "📋 Reference"],
            label_visibility="collapsed",
        )


# ─── RIGHT-SIDE NOTES PANEL ─────────────────────────────────────────────────

def render_notes_panel(topic_key: str, topic_title: str, topic_path: Path | None = None,
                       part_key: str | None = None):
    """
    Render the notes panel inside the right column.
    Input is always at the top and visible. Delete buttons are inline with notes.
    """
    entries = get_notes_for_topic(progress, topic_key)

    # ── Panel header ──
    st.markdown(
        f'<div class="notes-panel-header">📝 Notes — {topic_title}</div>',
        unsafe_allow_html=True,
    )

    # ── Compose + Send (always at top, always visible) ──
    note_text = st.text_area(
        "Write a note",
        height=80,
        key=f"compose_{topic_key}",
        label_visibility="collapsed",
        placeholder="Type a note and hit Send...",
    )

    btn_cols = st.columns([1, 1])
    with btn_cols[0]:
        if st.button("📤 Send", key=f"send_{topic_key}", use_container_width=True, type="primary"):
            if note_text and note_text.strip():
                add_note_entry(progress, topic_key, note_text)
                st.session_state.active_topic = {"part": part_key, "topic_file": str(topic_path)}
                st.rerun()
            else:
                st.warning("Write something first!")

    with btn_cols[1]:
        entry_count = len(entries)
        st.markdown(
            f'<span class="badge-notes">{entry_count} note{"s" if entry_count != 1 else ""}</span>',
            unsafe_allow_html=True,
        )

    # ── Existing notes log (newest first, delete inline) ──
    if entries:
        st.markdown("---")
        for i, entry in enumerate(reversed(entries)):
            real_idx = len(entries) - 1 - i
            ncol, dcol = st.columns([6, 1])
            with ncol:
                st.markdown(
                    f'<div class="note-entry">'
                    f'{entry["text"]}'
                    f'<span class="note-ts">{entry["timestamp"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with dcol:
                if st.button("🗑️", key=f"del_{topic_key}_{real_idx}", help="Delete this note"):
                    delete_note_entry(progress, topic_key, real_idx)
                    st.session_state.active_topic = {"part": part_key, "topic_file": str(topic_path)}
                    st.rerun()
    else:
        st.markdown('<div class="note-empty">No notes yet — start typing above.</div>',
                    unsafe_allow_html=True)

    # ── Copy to AI Chat ──
    with st.expander("🤖 Copy to AI Chat"):
        content = read_file(topic_path) if topic_path else ""
        prompt_content = content[:8000] if len(content) > 8000 else content

        prompt_lines = [
            "I'm studying for the CISI Level 6 Regulation & Compliance exam.",
            f"I'm working on the topic: **{topic_title}**.",
        ]
        if part_key:
            weight = PART_WEIGHTS.get(part_key, "")
            prompt_lines.append(f"This is in {PART_LABELS.get(part_key, part_key)} (exam weight: {weight}).")
        prompt_lines += ["", "Here is the study material for this topic:", "```", prompt_content, "```"]

        # Include all notes
        if entries:
            prompt_lines += ["", "Here are my study notes so far:"]
            for entry in entries:
                prompt_lines.append(f"- [{entry['timestamp']}] {entry['text']}")

        prompt_lines += [
            "",
            "Please give me a tiered breakdown of this topic:",
            "1. **MUST KNOW** — the 3-4 core concepts I need to memorise",
            "2. **SHOULD KNOW** — supporting detail that strengthens answers",
            "3. **AWARENESS ONLY** — background I can skip",
            "",
            "Also tell me how often this topic appears in past papers and which exam sections "
            "(A, B, or C) it shows up in. Answer from the perspective of a compliance officer.",
        ]
        st.code("\n".join(prompt_lines), language="markdown")
        st.caption("Select all and copy (Ctrl+A then Ctrl+C).")


# ─── RENDER: TOPIC DETAIL (2-column layout) ─────────────────────────────────

def render_topic_detail(topic_path: Path, part_key: str | None = None):
    """Render topic content on the left, notes panel on the right."""
    key = get_topic_key(topic_path)
    title = slug_to_title(topic_path.stem)

    # Two-column layout: content (left) | notes panel (right)
    col_content, col_notes = st.columns([3, 1])

    with col_content:
        # Header
        st.markdown(f"### {title}")
        subtitle_parts = []
        if part_key:
            subtitle_parts.append(PART_LABELS.get(part_key, part_key))
            weight = PART_WEIGHTS.get(part_key)
            if weight:
                subtitle_parts.append(f"Exam weight: {weight}")
        subtitle_parts.append(f"`{topic_path.name}`")
        st.caption(" · ".join(subtitle_parts))

        # Covered / Flagged
        cc1, cc2, cc3 = st.columns([1, 1, 3])
        is_covered = key in progress.get("covered", [])
        is_flagged = key in progress.get("flagged", [])

        with cc1:
            new_covered = st.checkbox("✅ Covered", value=is_covered, key=f"cov_{key}")
        with cc2:
            new_flagged = st.checkbox("🚩 Review later", value=is_flagged, key=f"flag_{key}")

        changed = False
        if new_covered != is_covered:
            if new_covered:
                if key not in progress["covered"]:
                    progress["covered"].append(key)
            else:
                progress["covered"] = [k for k in progress["covered"] if k != key]
            changed = True
        if new_flagged != is_flagged:
            if new_flagged:
                if key not in progress["flagged"]:
                    progress["flagged"].append(key)
            else:
                progress["flagged"] = [k for k in progress["flagged"] if k != key]
            changed = True
        if changed:
            save_progress(progress)

        st.markdown("---")

        # Main content
        content = read_file(topic_path)
        st.session_state.visited.add(str(topic_path))
        st.markdown(content)

    with col_notes:
        render_notes_panel(key, title, topic_path, part_key)

        # Party GIFs down the full length of the right column
        if st.session_state.get("party_gifs"):
            gifs = list(GIFS_DIR.glob("*.gif"))
            if gifs:
                rng = random.Random(key)
                shuffled = rng.sample(gifs, len(gifs))
                for gif in shuffled:
                    st.markdown('<div style="margin-top:3rem"></div>',
                                unsafe_allow_html=True)
                    st.image(str(gif), use_container_width=True)
                    st.caption(rng.choice(CHEER_MESSAGES))


# ─── HOME DASHBOARD ─────────────────────────────────────────────────────────

def render_home():
    st.markdown("## 📚 CISI Diploma Revision Hub")
    st.markdown("**Level 6 · Regulation & Compliance**")
    st.markdown("---")

    topics_dir = KB_ROOT / "topics"
    total_topics = count_all_topic_files()
    covered_count = len(progress.get("covered", []))
    flagged_count = len(progress.get("flagged", []))
    notes_topics = count_topics_with_notes(progress)
    notes_total = total_note_entries(progress)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Topics", total_topics)
    c2.metric("Covered", covered_count)
    c3.metric("Flagged", flagged_count)
    c4.metric("Note Entries", notes_total)

    if total_topics > 0:
        pct = covered_count / total_topics
        st.markdown(
            f'<div class="overall-progress-bar">'
            f'<div class="overall-progress-fill" style="width:{pct*100:.1f}%"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"{round(pct*100)}% complete — {covered_count} of {total_topics} topics covered")

    st.markdown("---")

    # Part-by-part collapsible cards
    for pk in PART_ORDER:
        if not (topics_dir / pk).exists():
            continue
        part_covered, part_total, part_files = get_part_progress(pk, progress)
        part_pct = part_covered / max(part_total, 1)
        weight = PART_WEIGHTS.get(pk, "")
        short_label = PART_SHORT_LABELS.get(pk, pk)

        with st.expander(f"{short_label}  —  {part_covered}/{part_total} covered", expanded=False):
            pcol1, pcol2 = st.columns([4, 1])
            with pcol1:
                st.progress(part_pct)
            with pcol2:
                st.markdown(f'<span class="badge-weight">{weight} of exam</span>', unsafe_allow_html=True)

            for f in part_files:
                fkey = get_topic_key(f)
                is_cov = fkey in progress.get("covered", [])
                is_flag = fkey in progress.get("flagged", [])
                has_notes = bool(get_notes_for_topic(progress, fkey))

                status = ""
                if is_cov:
                    status += "✅ "
                if is_flag:
                    status += "🚩 "
                if has_notes:
                    status += "📝 "
                if not is_cov and not is_flag:
                    status += "⬜ "

                if st.button(f"{status}{slug_to_title(f.stem)}", key=f"home_nav_{fkey}",
                             use_container_width=True):
                    st.session_state.active_topic = {"part": pk, "topic_file": str(f)}
                    st.rerun()

    # Flagged section
    if flagged_count > 0:
        st.markdown("---")
        st.markdown("#### 🚩 Flagged for Review")
        for fkey in progress.get("flagged", []):
            fpath = KB_ROOT / fkey
            parts = Path(fkey).parts
            pk = parts[1] if len(parts) > 1 else None
            if st.button(f"🚩 {slug_to_title(Path(fkey).stem)}", key=f"flagged_nav_{fkey}",
                         use_container_width=True):
                st.session_state.active_topic = {"part": pk, "topic_file": str(fpath)}
                st.rerun()


# ─── NOTES NOTEBOOK VIEW ────────────────────────────────────────────────────

def render_notes_notebook():
    """Browse all notes organised by part and topic."""
    st.markdown("## 📝 Notes Notebook")
    st.caption("All your study notes, organised by topic")
    st.markdown("---")

    notes_log = progress.get("notes_log", {})
    if not notes_log:
        st.info("No notes yet. Start adding notes from any Study Topic page — "
                "they'll appear here organised by topic.")
        return

    # Stats
    topics_with_notes = count_topics_with_notes(progress)
    total_entries = total_note_entries(progress)
    nc1, nc2 = st.columns(2)
    nc1.metric("Topics with Notes", topics_with_notes)
    nc2.metric("Total Note Entries", total_entries)
    st.markdown("---")

    # Group notes by part
    topics_dir = KB_ROOT / "topics"
    for pk in PART_ORDER:
        if not (topics_dir / pk).exists():
            continue

        part_files = collect_md_files(topics_dir / pk)
        # Check if any topic in this part has notes
        part_has_notes = False
        for f in part_files:
            nb_key = get_topic_key(f)
            if get_notes_for_topic(progress, nb_key):
                part_has_notes = True
                break

        if not part_has_notes:
            continue

        short_label = PART_SHORT_LABELS.get(pk, pk)
        st.markdown(f'<div class="notebook-part-header">{short_label}</div>', unsafe_allow_html=True)

        for f in part_files:
            nb_key = get_topic_key(f)
            entries = get_notes_for_topic(progress, nb_key)
            if not entries:
                continue

            title = slug_to_title(f.stem)
            with st.expander(f"{title} — {len(entries)} note{'s' if len(entries) != 1 else ''}", expanded=False):
                # Button to jump to this topic
                if st.button(f"📖 Open {title}", key=f"notebook_nav_{nb_key}", use_container_width=True):
                    st.session_state.active_topic = {"part": pk, "topic_file": str(f)}
                    st.rerun()

                for i, entry in enumerate(entries):
                    ncol, dcol = st.columns([6, 1])
                    with ncol:
                        st.markdown(
                            f'<div class="note-entry">'
                            f'{entry["text"]}'
                            f'<span class="note-ts">{entry["timestamp"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    with dcol:
                        if st.button("🗑️", key=f"nb_del_{nb_key}_{i}", help="Delete this note"):
                            delete_note_entry(progress, nb_key, i)
                            st.rerun()

    # Orphaned notes (keys that don't match any current topic file)
    all_topic_keys = set()
    for pk in PART_ORDER:
        for f in collect_md_files(KB_ROOT / "topics" / pk):
            all_topic_keys.add(get_topic_key(f))

    orphaned = {k: v for k, v in notes_log.items() if k not in all_topic_keys and v}
    if orphaned:
        st.markdown("---")
        st.markdown("#### Other Notes")
        for orph_key, entries in orphaned.items():
            title = slug_to_title(Path(orph_key).stem)
            with st.expander(f"{title} — {len(entries)} note{'s' if len(entries) != 1 else ''}"):
                for i, entry in enumerate(entries):
                    st.markdown(
                        f'<div class="note-entry">'
                        f'{entry["text"]}'
                        f'<span class="note-ts">{entry["timestamp"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

_, party_btn_col = st.columns([5, 1])
with party_btn_col:
    if st.button("🎉 Click me 2 cheer up xx"):
        party_mode_popup()

# ── Persistent direct navigation (from Home / Notebook / Notes buttons) ──
if st.session_state.active_topic is not None and nav_mode == "active":
    target = st.session_state.active_topic
    topic_path = Path(target["topic_file"])
    part_key = target.get("part")

    if topic_path.exists():
        render_topic_detail(topic_path, part_key)
    else:
        st.session_state.active_topic = None
        st.rerun()

elif nav_mode == "search" and chosen_path:
    part_key = resolve_part_key(chosen_path)
    if part_key and part_key in PART_ORDER:
        render_topic_detail(chosen_path, part_key)
    else:
        st.markdown(f"### {slug_to_title(chosen_path.stem)}")
        content = read_file(chosen_path)
        st.session_state.visited.add(str(chosen_path))
        st.markdown(content)

elif nav_mode == "browse":

    # ── HOME ──
    if view == "🏠 Home":
        render_home()

    # ── STUDY TOPICS ──
    elif view == "📖 Study Topics":
        topics_dir = KB_ROOT / "topics"
        if not topics_dir.exists():
            st.warning("Topics directory not found.")
        else:
            available_parts = [p for p in PART_ORDER if (topics_dir / p).exists()]
            if not available_parts:
                st.info("No topic folders found yet.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    total_topics = count_all_topic_files()
                    covered_count = len(progress.get("covered", []))
                    flagged_count = len(progress.get("flagged", []))
                    st.markdown(
                        f'<span class="badge-covered">✅ {covered_count} covered</span> '
                        f'<span class="badge-flagged">🚩 {flagged_count} flagged</span>',
                        unsafe_allow_html=True,
                    )
                    st.progress(min(covered_count / max(total_topics, 1), 1.0))
                    st.caption(f"{covered_count} of {total_topics} topics covered")
                    st.markdown("---")

                    part_choice = st.radio(
                        "Part", available_parts,
                        format_func=lambda x: PART_LABELS.get(x, slug_to_title(x)),
                    )

                    part_files = collect_md_files(topics_dir / part_choice)
                    if part_files:
                        topic_choice = st.radio(
                            "Topic", part_files,
                            format_func=lambda f: sidebar_topic_label(f, progress),
                        )
                    else:
                        topic_choice = None

                if topic_choice:
                    render_topic_detail(topic_choice, part_choice)
                else:
                    st.info("No topics in this section yet.")

    # ── QUESTION BANK ──
    elif view == "❓ Question Bank":
        qb_dir = KB_ROOT / "question-bank"
        if not qb_dir.exists():
            st.warning(f"Question bank not found at `{qb_dir}`.")
        else:
            sections = sorted([d for d in qb_dir.iterdir() if d.is_dir()], key=lambda d: d.name)
            if not sections:
                st.info("No question bank sections found yet.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    sec_choice = st.radio("Exam Section", sections,
                                          format_func=lambda d: SECTION_LABELS.get(d.name, d.name))
                    sec_files = collect_md_files(sec_choice)
                    q_choice = st.radio("Questions", sec_files,
                                        format_func=lambda f: slug_to_title(f.stem)) if sec_files else None

                if q_choice:
                    st.markdown(f"### {slug_to_title(q_choice.stem)}")
                    st.caption(f"{SECTION_LABELS.get(sec_choice.name, sec_choice.name)} · `{q_choice.name}`")
                    st.markdown("---")
                    content = read_file(q_choice)
                    st.session_state.visited.add(str(q_choice))
                    st.markdown(content)
                else:
                    st.info("No questions in this section yet.")

    # ── NOTES NOTEBOOK ──
    elif view == "📝 Notes Notebook":
        render_notes_notebook()

    # ── REFERENCE ──
    elif view == "📋 Reference":
        ref_dir = KB_ROOT / "reference"
        if not ref_dir.exists():
            st.warning(f"Reference directory not found at `{ref_dir}`.")
        else:
            ref_files = collect_md_files(ref_dir)
            if not ref_files:
                st.info("No reference files found yet.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    ref_choice = st.radio("Reference", ref_files,
                                          format_func=lambda f: slug_to_title(f.stem))
                if ref_choice:
                    st.markdown(f"### {slug_to_title(ref_choice.stem)}")
                    st.caption(f"`{ref_choice.name}`")
                    st.markdown("---")
                    content = read_file(ref_choice)
                    st.session_state.visited.add(str(ref_choice))
                    st.markdown(content)

else:
    render_home()
