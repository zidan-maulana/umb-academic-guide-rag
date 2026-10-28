"""Script for page-by-page text extraction from raw PDF (docs/data-spec.md Section 4).

Extraction rules from docs/data-spec.md Section 2 and Section 4:
- Scope: pages 14 to 98, plus the accreditation table on page 11.
- Section separators: skip pages 13, 26, and 99 during extraction.
- Two-column regulation pages (e.g. page 17): do not use pdftotext -layout.
  Extract without -layout or crop page into left and right halves.
- Accreditation table (page 11): extract via pdftotext -layout or manual CSV input.
- Curriculum pages: visual verification required for course code mapping due to inconsistent positions.
- Page numbering reference: strictly follow PDF page numbers.
- Output raw extracted text per page into data/raw/.
"""


import argparse
import glob
import os
from pathlib import Path
from typing import Optional

import pdfplumber

# Constants defining document scope based on docs/data-spec.md Section 2
ACCREDITATION_PAGE = 11
REGULATION_PAGES = range(14, 26)  # 14 to 25 inclusive
FACULTY_CURRICULUM_PAGES = range(27, 99)  # 27 to 98 inclusive
SEPARATOR_PAGES = {13, 26, 99}

# Bottom margin cutoff in points to exclude printed page numbers
FOOTER_MARGIN_PT = 45.0


def find_pdf_path(raw_dir: Path) -> Path:
    """Find the academic guide PDF file in data/raw/ directory."""
    candidates = [
        raw_dir / "3_-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf",
        raw_dir / "3.-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # Fallback to wildcard search in raw_dir
    matches = list(raw_dir.glob("*Panduan*.pdf"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        f"PDF panduan akademik tidak ditemukan di {raw_dir}. "
        "Pastikan file PDF diletakkan di folder data/raw/."
    )


def extract_two_column_page(page: pdfplumber.page.Page) -> str:
    """Extract text from a 2-column layout page by reading left column then right column."""
    width = page.width
    height = page.height
    split_x = width / 2.0
    effective_height = height - FOOTER_MARGIN_PT

    # Left column: from x=0 to middle split
    left_crop = page.crop((0, 0, split_x, effective_height))
    left_text = (left_crop.extract_text() or "").strip()

    # Right column: from middle split to right edge
    right_crop = page.crop((split_x, 0, width, effective_height))
    right_text = (right_crop.extract_text() or "").strip()

    if left_text and right_text:
        return f"{left_text}\n\n{right_text}"
    return left_text or right_text


def extract_standard_page(page: pdfplumber.page.Page) -> str:
    """Extract text from a single-column or table page, excluding footer page number."""
    width = page.width
    height = page.height
    effective_height = height - FOOTER_MARGIN_PT

    content_crop = page.crop((0, 0, width, effective_height))
    return (content_crop.extract_text() or "").strip()


def extract_page_by_number(pdf: pdfplumber.PDF, page_num: int) -> str:
    """Extract text for a given 1-indexed PDF page number according to layout rules."""
    if page_num in SEPARATOR_PAGES:
        return ""

    page_idx = page_num - 1
    if page_idx < 0 or page_idx >= len(pdf.pages):
        raise ValueError(
            f"Nomor halaman {page_num} di luar jangkauan PDF (total {len(pdf.pages)} halaman)."
        )

    page = pdf.pages[page_idx]

    if page_num in REGULATION_PAGES:
        return extract_two_column_page(page)
    elif page_num == ACCREDITATION_PAGE or page_num in FACULTY_CURRICULUM_PAGES:
        return extract_standard_page(page)
    else:
        # Pages outside scope (1-10, 12, 100-105)
        return extract_standard_page(page)


def save_raw_page(page_num: int, text: str, output_dir: Path) -> Path:
    """Save extracted raw text to a designated text file in raw directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"page_{page_num:03d}.txt"
    out_file.write_text(text, encoding="utf-8")
    return out_file


def get_all_in_scope_pages() -> list[int]:
    """Return sorted list of all in-scope page numbers, skipping section separators."""
    pages = [ACCREDITATION_PAGE]
    for p in REGULATION_PAGES:
        if p not in SEPARATOR_PAGES:
            pages.append(p)
    for p in FACULTY_CURRICULUM_PAGES:
        if p not in SEPARATOR_PAGES:
            pages.append(p)
    return sorted(pages)


def main() -> None:
    """Execute text extraction CLI."""
    parser = argparse.ArgumentParser(
        description="Ekstraksi teks per halaman dari PDF Panduan Akademik UMB."
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="Path ke file PDF (opsional, default: data/raw/*Panduan*.pdf)",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help="Ekstrak satu nomor halaman spesifik (contoh: --page 17 atau --page 11)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ekstrak seluruh halaman dalam scope (hal. 11, dan hal. 14 s/d 98)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw",
        help="Direktori penyimpanan file teks mentah (default: data/raw)",
    )

    args = parser.parse_args()
    raw_dir = Path(args.output_dir)

    pdf_file = Path(args.pdf) if args.pdf else find_pdf_path(raw_dir)
    print(f"[EXTRACT] Menggunakan file PDF: {pdf_file}")

    with pdfplumber.open(pdf_file) as pdf:
        total_pdf_pages = len(pdf.pages)
        print(f"[EXTRACT] Total halaman PDF terdeteksi: {total_pdf_pages}")

        if args.page is not None:
            target_page = args.page
            print(f"[EXTRACT] Menjalankan ekstraksi sampel untuk halaman: {target_page}")
            extracted_text = extract_page_by_number(pdf, target_page)
            out_path = save_raw_page(target_page, extracted_text, raw_dir)
            print(f"[EXTRACT] Selesai. Hasil disimpan di: {out_path}")
            print(f"[EXTRACT] Jumlah karakter: {len(extracted_text)}")
            print("-" * 50)
            preview = extracted_text[:300] if len(extracted_text) > 300 else extracted_text
            print(f"Preview 300 karakter pertama:\n{preview}")
            print("-" * 50)
            return

        if args.all:
            in_scope_pages = get_all_in_scope_pages()
            print(
                f"[EXTRACT] Menjalankan ekstraksi penuh untuk {len(in_scope_pages)} halaman scope..."
            )
            extracted_count = 0
            for page_num in in_scope_pages:
                text = extract_page_by_number(pdf, page_num)
                save_raw_page(page_num, text, raw_dir)
                extracted_count += 1
                if extracted_count % 10 == 0 or extracted_count == len(in_scope_pages):
                    print(
                        f"[EXTRACT] Progress: {extracted_count}/{len(in_scope_pages)} halaman selesai diekstrak."
                    )
            print(f"[EXTRACT] Ekstraksi penuh selesai. Seluruh file tersimpan di {raw_dir}.")
            return

        # Default info if no option provided
        print("Tentukan opsi pengerjaan:")
        print("  Gunakan --page <nomor> untuk menguji satu halaman (misal: --page 17)")
        print("  Gunakan --all untuk mengekstrak seluruh halaman scope")


if __name__ == "__main__":
    main()

