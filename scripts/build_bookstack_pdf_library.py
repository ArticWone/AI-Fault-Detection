#!/usr/bin/env python3
"""Build BookStack page payloads from local PDF manuals.

This creates a JSON file that can be uploaded to BookStack from the node,
where the API token lives. It intentionally does not store API secrets.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


PDFS = [
    {
        "title": "BP802ALV 600R Use and Maintenance Manual",
        "file": "DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf",
        "prefix": "BP802ALV Manual",
        "chunk_pages": 8,
        "keywords": [
            "BP802ALV 600R",
            "sealing bar",
            "bar safety",
            "film finished",
            "B12 obstruction",
            "chain separator",
            "emergency door open",
            "inverter error",
        ],
    },
    {
        "title": "Industry 4.0 Ethernet and Modbus Manual",
        "file": "DM200289_D_Industry_4_0_Ethernet_Modbus.pdf",
        "prefix": "Industry 4.0 Manual",
        "chunk_pages": 4,
        "keywords": [
            "Modbus TCP",
            "VNC",
            "UltraVNC",
            "register 13300",
            "register 10142",
            "register 10112",
            "register 10161",
            "192.168.0.1",
        ],
    },
    {
        "title": "External Reel-Holder Manual",
        "file": "DM200178_A_EN_external_reel_holder.pdf",
        "prefix": "External Reel-Holder Manual",
        "chunk_pages": 4,
        "keywords": [
            "external reel-holder",
            "bottom loading",
            "tensioning bar",
            "reel end photocell",
            "50.SQ.4",
            "51.B",
            "32.M.1",
        ],
    },
]

WIRING_SCAN = {
    "title": "Wiring Diagrams Part 1 Scan",
    "file": "SMIPACK_wiring_diagrams_part_1_scan.pdf",
    "prefix": "Wiring Diagrams Part 1",
    "keywords": [
        "wiring diagram",
        "schematic",
        "terminal block",
        "wire number",
        "sensor cable",
        "FLXIO",
        "FLXMOD",
        "DIO 16",
        "B1",
        "B2",
        "B11",
        "B12",
        "SQ13",
        "50.SQ.4",
        "50.SQ.5",
        "51.B",
        "52.SQ.4",
        "52.SQ.5",
        "55.SQ.2",
        "162.KM.8",
        "162.KM.9",
        "60.KA.3",
        "32.M.1",
    ],
}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\.{4,}", " ", text)
    text = re.sub(r"(?:\s*\.\s*){3,}", " ", text)
    text = re.sub(r"[·•]{4,}", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def markdown_safe_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return format_numbered_headings(text)


def format_numbered_headings(text: str) -> str:
    """Turn extracted manual section numbers into readable Markdown headings."""
    formatted = []
    top_level = re.compile(r"^(\d{1,2})\s+-\s+(.+?)(?:\s+(\d{1,3}))?$")
    nested = re.compile(r"^(\d{1,2}(?:\.\d+){1,3})\s+(.+?)(?:\s+(\d{1,3}))?$")

    for line in text.splitlines():
        stripped = line.strip()
        match = top_level.match(stripped) or nested.match(stripped)
        if match:
            number, title, page = match.groups()
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) >= 3 and not title.lower().startswith(("fig.", "tab.")):
                level = min(3 + number.count("."), 6)
                suffix = f" _(page {page})_" if page else ""
                formatted.append(f"{'#' * level} {number} {title}{suffix}")
                continue
        formatted.append(line)
    return "\n".join(formatted)


def split_page_chunks(total_pages: int, chunk_size: int) -> list[tuple[int, int]]:
    chunks = []
    start = 1
    while start <= total_pages:
        end = min(start + chunk_size - 1, total_pages)
        chunks.append((start, end))
        start = end + 1
    return chunks


def extract_pdf_pages(pdf_dir: Path, spec: dict) -> list[dict]:
    pdf_path = pdf_dir / spec["file"]
    reader = PdfReader(str(pdf_path))
    pages = []
    for start, end in split_page_chunks(len(reader.pages), int(spec["chunk_pages"])):
        text_parts = []
        for page_num in range(start, end + 1):
            try:
                text = reader.pages[page_num - 1].extract_text() or ""
            except Exception as exc:  # pragma: no cover - defensive for damaged PDFs
                text = f"[Text extraction failed on page {page_num}: {exc}]"
            text = clean_text(text)
            if text:
                text_parts.append(f"## PDF Page {page_num}\n\n{markdown_safe_text(text)}")
        body = "\n\n".join(text_parts).strip()
        if not body:
            body = "No embedded text was found for this page range."
        pages.append(
            {
                "name": f"{spec['prefix']} - Pages {start:03d}-{end:03d}",
                "markdown": (
                    f"# {spec['title']} - Pages {start}-{end}\n\n"
                    f"Source PDF: `{spec['file']}`\n\n"
                    f"Search keywords: {', '.join(spec['keywords'])}\n\n"
                    f"{body}"
                ),
            }
        )
    return pages


def build_wiring_placeholders(pdf_dir: Path) -> list[dict]:
    pdf_path = pdf_dir / WIRING_SCAN["file"]
    reader = PdfReader(str(pdf_path))
    pages = []
    for page_num in range(1, len(reader.pages) + 1):
        pages.append(
            {
                "name": f"{WIRING_SCAN['prefix']} - Sheet {page_num:03d}",
                "markdown": (
                    f"# {WIRING_SCAN['title']} - Sheet {page_num}\n\n"
                    f"Source PDF: `{WIRING_SCAN['file']}`\n\n"
                    "This scan page is image-only. Use this page to record OCR text, "
                    "wire labels, terminal blocks, and traced device references.\n\n"
                    f"Search keywords: {', '.join(WIRING_SCAN['keywords'])}\n\n"
                    "## Trace Notes\n\n"
                    "| Wire/terminal | Device label | Machine area | Related fault/register | Status |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| unknown | unknown | unknown | unknown | needs trace |\n"
                ),
            }
        )
    return pages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", default="docs/vendor-documents/smipack")
    parser.add_argument("--out", default="build/bookstack_pdf_library_pages.json")
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir)
    pages = []
    for spec in PDFS:
        pages.extend(extract_pdf_pages(pdf_dir, spec))
    pages.extend(build_wiring_placeholders(pdf_dir))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"pages": pages}, indent=2), encoding="utf-8")
    print(f"wrote {len(pages)} pages to {out}")


if __name__ == "__main__":
    main()
