"""
CISI Diploma Revision Hub
Level 6 Regulation & Compliance — Streamlit Study Interface
Built by NakoLabs
"""

import streamlit as st
from pathlib import Path
import re

# ─── CONFIG ───────────────────────────────────────────────────────────────────

KB_ROOT = Path(__file__).parent / "knowledge-base"

PART_ORDER = [
    "part-1-regulatory-framework",
    "part-2-fca-handbook",
    "part-3-other-regulatory",
    "part-4-markets-exchanges",
    "part-5-current-developments",
    "risk-in-financial-services",
]

PART_LABELS = {
    "part-1-regulatory-framework": "Part 1 — Regulatory Framework",
    "part-2-fca-handbook": "Part 2 — FCA Handbook",
    "part-3-other-regulatory": "Part 3 — Other Regulatory",
    "part-4-markets-exchanges": "Part 4 — Markets & Exchanges",
    "part-5-current-developments": "Part 5 — Current Developments",
    "risk-in-financial-services": "Part 6 — Risk in Financial Services",
}

SECTION_LABELS = {
    "section-a": "Section A",
    "section-b": "Section B",
    "section-c": "Section C",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────


def slug_to_title(slug: str) -> str:
    """Convert kebab-case slug to readable title."""
    # Strip leading number prefix like '01-' from section-a files
    slug = re.sub(r"^\d{1,2}-", "", slug)
    # Remove .md extension
    slug = slug.removesuffix(".md")
    # Known acronyms to uppercase
    acronyms = {
        "fca", "pra", "cobs", "sysc", "cass", "depp", "sup", "aper",
        "smcr", "mar", "dtr", "tc", "aml", "mifid", "emir", "uk",
        "eu", "esma", "hmrc", "fsma", "eba", "bis", "iosco",
    }
    words = slug.split("-")
    titled = []
    for w in words:
        if w.lower() in acronyms:
            titled.append(w.upper())
        else:
            titled.append(w.capitalize())
    return " ".join(titled)


def collect_md_files(directory: Path) -> list[Path]:
    """Return sorted .md files in a directory (non-recursive)."""
    if not directory.exists():
        return []
    files = sorted(directory.glob("*.md"))
    # Exclude index.md from listings
    return [f for f in files if f.name != "index.md"]


def read_file(path: Path) -> str:
    """Read file content with fallback."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"⚠️ Could not read file: {e}"


def search_files(query: str, root: Path) -> list[tuple[str, Path]]:
    """Search all .md files for a query string. Returns (context_label, path)."""
    results = []
    query_lower = query.lower()
    for md_file in sorted(root.rglob("*.md")):
        if md_file.name == "index.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8").lower()
            if query_lower in content or query_lower in md_file.stem:
                # Build a human label from the path
                rel = md_file.relative_to(root)
                label = " → ".join(
                    slug_to_title(p) for p in [*rel.parent.parts, rel.stem]
                )
                results.append((label, md_file))
        except Exception:
            continue
    return results


# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CISI Revision Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM STYLING ──────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Clean, readable study interface */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fc;
        border-right: 1px solid #e2e4eb;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.9rem;
        padding: 4px 0;
    }

    /* Main content area */
    .main .block-container {
        max-width: 860px;
        padding-top: 2rem;
    }

    /* Markdown content styling for readability */
    .stMarkdown h1 { font-size: 1.7rem; font-weight: 700; margin-top: 1.5rem; }
    .stMarkdown h2 { font-size: 1.35rem; font-weight: 600; margin-top: 1.3rem; color: #1a1a2e; }
    .stMarkdown h3 { font-size: 1.15rem; font-weight: 600; margin-top: 1rem; color: #2d2d44; }
    .stMarkdown p  { font-size: 1rem; line-height: 1.75; color: #333; }
    .stMarkdown li { font-size: 1rem; line-height: 1.7; }
    .stMarkdown code { background: #f0f2f6; padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; }
    .stMarkdown blockquote {
        border-left: 4px solid #4a6cf7;
        padding-left: 1rem;
        color: #555;
        background: #f8f9ff;
        margin: 1rem 0;
        padding: 0.8rem 1rem;
        border-radius: 0 6px 6px 0;
    }

    /* Progress chip */
    .progress-chip {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Topic card in sidebar */
    .sidebar-section-header {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #888;
        margin: 1.2rem 0 0.4rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── SESSION STATE ────────────────────────────────────────────────────────────

if "visited" not in st.session_state:
    st.session_state.visited = set()


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📚 CISI Revision Hub")
    st.caption("Level 6 · Regulation & Compliance")
    st.markdown("---")

    # Search
    search_query = st.text_input("🔍 Search topics", placeholder="e.g. SMCR, market abuse")

    # If searching, show results instead of normal nav
    if search_query and search_query.strip():
        results = search_files(search_query.strip(), KB_ROOT)
        if results:
            st.markdown(f"**{len(results)} result{'s' if len(results) != 1 else ''}**")
            selection_labels = [r[0] for r in results]
            chosen = st.radio(
                "Results",
                selection_labels,
                label_visibility="collapsed",
            )
            chosen_path = results[selection_labels.index(chosen)][1]
            nav_mode = "search"
        else:
            st.info("No results found.")
            nav_mode = "none"
            chosen_path = None
    else:
        nav_mode = "browse"
        chosen_path = None

        # Section selector
        view = st.radio(
            "Section",
            ["📖 Study Topics", "❓ Question Bank", "📋 Reference"],
            label_visibility="collapsed",
        )

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

if nav_mode == "search" and chosen_path:
    # Render search result
    st.markdown(f"### {slug_to_title(chosen_path.stem)}")
    content = read_file(chosen_path)
    st.session_state.visited.add(str(chosen_path))
    st.markdown(content)

elif nav_mode == "browse":

    # ── STUDY TOPICS ──────────────────────────────────────────────────────
    if view == "📖 Study Topics":
        topics_dir = KB_ROOT / "topics"

        if not topics_dir.exists():
            st.warning(
                f"Topics directory not found at `{topics_dir}`. "
                "Make sure the `knowledge-base/topics/` folder is in the same directory as this app."
            )
        else:
            # Build part selector
            available_parts = []
            for p in PART_ORDER:
                if (topics_dir / p).exists():
                    available_parts.append(p)

            if not available_parts:
                st.info("No topic folders found yet.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    part_choice = st.radio(
                        "Part",
                        available_parts,
                        format_func=lambda x: PART_LABELS.get(x, slug_to_title(x)),
                    )

                    # List topics in chosen part
                    part_files = collect_md_files(topics_dir / part_choice)
                    if part_files:
                        topic_choice = st.radio(
                            "Topic",
                            part_files,
                            format_func=lambda f: (
                                ("✅ " if str(f) in st.session_state.visited else "")
                                + slug_to_title(f.stem)
                            ),
                        )
                    else:
                        topic_choice = None

                # Main area
                if topic_choice:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"### {slug_to_title(topic_choice.stem)}")
                    with col2:
                        visited_in_part = sum(
                            1 for f in part_files if str(f) in st.session_state.visited
                        )
                        st.markdown(
                            f'<span class="progress-chip">{visited_in_part}/{len(part_files)}</span>',
                            unsafe_allow_html=True,
                        )

                    st.caption(
                        f"{PART_LABELS.get(part_choice, part_choice)} · "
                        f"`{topic_choice.name}`"
                    )
                    st.markdown("---")

                    content = read_file(topic_choice)
                    st.session_state.visited.add(str(topic_choice))
                    st.markdown(content)
                else:
                    st.info("No topics in this section yet.")

    # ── QUESTION BANK ─────────────────────────────────────────────────────
    elif view == "❓ Question Bank":
        qb_dir = KB_ROOT / "question-bank"

        if not qb_dir.exists():
            st.warning(f"Question bank not found at `{qb_dir}`.")
        else:
            sections = sorted(
                [d for d in qb_dir.iterdir() if d.is_dir()],
                key=lambda d: d.name,
            )

            if not sections:
                st.info("No question bank sections found yet.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    sec_choice = st.radio(
                        "Exam Section",
                        sections,
                        format_func=lambda d: SECTION_LABELS.get(d.name, d.name),
                    )

                    sec_files = collect_md_files(sec_choice)
                    if sec_files:
                        q_choice = st.radio(
                            "Questions",
                            sec_files,
                            format_func=lambda f: slug_to_title(f.stem),
                        )
                    else:
                        q_choice = None

                if q_choice:
                    st.markdown(f"### {slug_to_title(q_choice.stem)}")
                    st.caption(
                        f"{SECTION_LABELS.get(sec_choice.name, sec_choice.name)} · "
                        f"`{q_choice.name}`"
                    )
                    st.markdown("---")
                    content = read_file(q_choice)
                    st.session_state.visited.add(str(q_choice))
                    st.markdown(content)
                else:
                    st.info("No questions in this section yet.")

    # ── REFERENCE ─────────────────────────────────────────────────────────
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
                    ref_choice = st.radio(
                        "Reference",
                        ref_files,
                        format_func=lambda f: slug_to_title(f.stem),
                    )

                if ref_choice:
                    st.markdown(f"### {slug_to_title(ref_choice.stem)}")
                    st.caption(f"`{ref_choice.name}`")
                    st.markdown("---")
                    content = read_file(ref_choice)
                    st.session_state.visited.add(str(ref_choice))
                    st.markdown(content)

else:
    # Default landing
    st.markdown("## 📚 CISI Diploma Revision Hub")
    st.markdown("**Level 6 · Regulation & Compliance**")
    st.markdown("---")
    st.markdown(
        """
        Use the sidebar to navigate through your study materials:

        - **📖 Study Topics** — Browse summarised notes by syllabus part
        - **❓ Question Bank** — Practice questions by exam section
        - **📋 Reference** — Syllabus, glossary, exam technique & more
        - **🔍 Search** — Find any topic across the entire knowledge base

        Topics you've viewed this session are marked with ✅ in the sidebar.
        """
    )

    # Quick stats
    if KB_ROOT.exists():
        total_md = len(list(KB_ROOT.rglob("*.md")))
        visited_count = len(st.session_state.visited)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Notes", total_md)
        c2.metric("Viewed This Session", visited_count)
        c3.metric("Remaining", max(0, total_md - visited_count))
