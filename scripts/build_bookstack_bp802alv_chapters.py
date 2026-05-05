#!/usr/bin/env python3
"""Build a clean, per-page BookStack import for the BP802ALV manual."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


MANUAL_FILE = "DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf"
SECTION_STARTS = [
    (7, "01", "1 Marking And Labelling"),
    (9, "02", "2 General Information"),
    (11, "03", "3 Description Of Machine"),
    (21, "04", "4 Manual Structure"),
    (25, "05", "5 Data And Technical Features"),
    (27, "06", "6 Machine Installation"),
    (39, "07", "7 Use Of The Machine"),
    (53, "08", "8 Preparing The Machine For Use"),
    (69, "09", "9 Operation And Use"),
    (95, "10", "10 Cleaning And Maintenance"),
    (113, "11", "11 Anomalies And Faults - Solutions"),
]


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\.{4,}", " ", text)
    text = re.sub(r"(?:\s*\.\s*){3,}", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_toc_page_numbers(line: str) -> str:
    """Remove right-side page numbers from table-of-contents style lines."""
    stripped = line.strip()
    match = re.match(r"^(\d{1,2}(?:\.\d+){0,4}\s+.+?)\s+\d{1,3}$", stripped)
    if match:
        return match.group(1).strip()
    match = re.match(r"^(\d{1,2}\s+-\s+.+?)\s+\d{1,3}$", stripped)
    if match:
        return match.group(1).strip()
    return line


def format_numbered_headings(text: str) -> str:
    formatted = []
    top_level = re.compile(r"^(\d{1,2})\s+-\s+(.+?)(?:\s+\d{1,3})?$")
    nested = re.compile(r"^(\d{1,2}(?:\.\d+){1,4})\s+(.+?)(?:\s+\d{1,3})?$")

    for line in text.splitlines():
        line = strip_toc_page_numbers(line)
        stripped = line.strip()
        match = top_level.match(stripped) or nested.match(stripped)
        if match:
            number, title = match.groups()
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) >= 3 and not title.lower().startswith(("fig.", "tab.")):
                level = min(2 + number.count("."), 6)
                formatted.append(f"{'#' * level} {number} {title}")
                continue
        formatted.append(line)
    return "\n".join(formatted)


def section_for_page(page_num: int) -> tuple[str, str]:
    current = SECTION_STARTS[0]
    for section in SECTION_STARTS:
        if page_num >= section[0]:
            current = section
        else:
            break
    _, key, name = current
    return key, name


def page_title(section_name: str, page_num: int, text: str) -> str:
    first_heading = None
    for line in text.splitlines():
        if line.startswith("## "):
            first_heading = line[3:].strip()
            break
        if line.startswith("### "):
            first_heading = line[4:].strip()
            break
    suffix = first_heading or section_name
    suffix = re.sub(r"\s+", " ", suffix)[:70]
    return f"BP802ALV p{page_num:03d} - {suffix}"


def build(pdf_dir: Path) -> dict:
    reader = PdfReader(str(pdf_dir / MANUAL_FILE))
    chapters: dict[str, dict] = {}
    for page_num in range(7, len(reader.pages) + 1):
        raw = reader.pages[page_num - 1].extract_text() or ""
        text = format_numbered_headings(clean_text(raw))
        current_key, current_name = section_for_page(page_num)
        chapter = chapters.setdefault(
            current_key,
            {
                "name": f"BP802ALV {current_name}",
                "description": "Clean per-page import from the BP802ALV 600R use and maintenance manual.",
                "pages": [],
            },
        )
        chapter["pages"].append(
            {
                "name": page_title(current_name, page_num, text),
                "markdown": (
                    f"# BP802ALV Manual - PDF Page {page_num}\n\n"
                    f"Source PDF: `{MANUAL_FILE}`\n\n"
                    f"Manual section: `{current_name}`\n\n"
                    f"{text}"
                ),
            }
        )
    return {"chapters": list(chapters.values())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", default="docs/vendor-documents/smipack")
    parser.add_argument("--out", default="build/bookstack_bp802alv_chapters.json")
    args = parser.parse_args()

    payload = build(Path(args.pdf_dir))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    page_count = sum(len(chapter["pages"]) for chapter in payload["chapters"])
    print(f"wrote {len(payload['chapters'])} chapters and {page_count} pages to {out}")


if __name__ == "__main__":
    main()
