#!/usr/bin/env python3
"""Render BP802ALV manual pages to images for BookStack import."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz


MANUAL_FILE = "DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf"


def render(pdf_dir: Path, out_dir: Path, start_page: int, end_page: int, dpi: int) -> None:
    pdf_path = pdf_dir / MANUAL_FILE
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    for page_num in range(start_page, end_page + 1):
        page = doc[page_num - 1]
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image_path = out_dir / f"bp802alv-p{page_num:03d}.jpg"
        pixmap.save(image_path, jpg_quality=82)
        print(image_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir", default="docs/vendor-documents/smipack")
    parser.add_argument("--out-dir", default="build/bookstack_bp802alv_page_images")
    parser.add_argument("--start-page", type=int, default=7)
    parser.add_argument("--end-page", type=int, default=124)
    parser.add_argument("--dpi", type=int, default=140)
    args = parser.parse_args()
    render(Path(args.pdf_dir), Path(args.out_dir), args.start_page, args.end_page, args.dpi)


if __name__ == "__main__":
    main()
