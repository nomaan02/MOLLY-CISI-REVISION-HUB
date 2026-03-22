import os
import sys
import re
import pymupdf4llm
from pathlib import Path


def sanitize_filename(name: str) -> str:
    stem = Path(name).stem
    slug = stem.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug + ".md"


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    md_text = pymupdf4llm.to_markdown(str(pdf_path))

    out_name = sanitize_filename(pdf_path.name)
    out_path = output_dir / out_name

    frontmatter = (
        "---\n"
        f"source: \"{pdf_path.name}\"\n"
        "---\n\n"
    )

    out_path.write_text(frontmatter + md_text, encoding="utf-8")
    return out_path


def main():
    pdf_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./pdfs")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("./knowledge-base/raw-markdown")

    if not pdf_dir.is_dir():
        print(f"Error: PDF directory not found: {pdf_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in {pdf_dir}")
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF(s) in {pdf_dir}")
    print(f"Output directory: {output_dir}\n")

    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Converting: {pdf.name} ... ", end="", flush=True)
        try:
            out = convert_pdf(pdf, output_dir)
            size = out.stat().st_size
            print(f"OK -> {out.name} ({size:,} bytes)")
        except Exception as e:
            print(f"FAILED: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
