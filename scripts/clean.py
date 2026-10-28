"""Script for cleaning extracted text without semantic distortion (docs/data-spec.md Section 4).

Cleaning rules from docs/data-spec.md Section 4:
- Clean without altering meaning. Preserve complete sentences for embedding.
- Strip repetitive headers, footers, and printed page numbers.
- Rejoin hyphenated words split across line breaks and sentences broken mid-phrase.
- Normalize irregular spacing, anomalous characters, and corrupted bullet symbols.
- DO NOT apply stopword removal, stemming, or full lowercasing.
- DO NOT alter numbers, SKS, semesters, course codes, course names, or official terms.
- DO NOT correct typographical errors from the source (e.g. 'PRINGKAT'); log them instead.
- Save cleaned text per page into data/clean/.
"""


import argparse
import logging
import re
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Constants defining document scope based on docs/data-spec.md
ACCREDITATION_PAGE = 11
REGULATION_PAGES = range(14, 26)  # 14 to 25 inclusive
FACULTY_CURRICULUM_PAGES = range(27, 99)  # 27 to 98 inclusive


def normalize_shadow_text(text: str) -> str:
    """Normalize drop-shadow font artifacts where every character in a word is doubled.
    Example: 'FFAAKKUULLTTAASS' -> 'FAKULTAS', 'DDeessaaiinn' -> 'Desain'.
    """
    def dedup_chars(match: re.Match) -> str:
        s = match.group(0)
        return "".join(s[i] for i in range(0, len(s), 2))

    # Match words of at least 3 distinct duplicated pairs: (c1)(c1)(c2)(c2)(c3)(c3)...
    pattern = re.compile(r"\b([a-zA-Z])\1([a-zA-Z])\2(?:([a-zA-Z])\3)+\b")
    return pattern.sub(dedup_chars, text)


def normalize_bullets(text: str) -> str:
    """Normalize anomalous bullet symbols (e.g., black squares, bullet glyphs) to standard dashes."""
    # Replace solid square bullet or corrupted glyphs at line starts
    text = re.sub(r"^[■•\uf0b7]\s*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"\n[■•\uf0b7]\s*", "\n- ", text)
    return text


def dehyphenate_text(text: str) -> str:
    """Rejoin words split across line breaks by a hyphen.
    Preserves hyphens for reduplicated Indonesian words (e.g. 'lain-lain', 'sekurang-kurangnya').
    Joins single words without hyphens (e.g. 'pembela- jaran' -> 'pembelajaran').
    """
    def resolve_hyphen(match: re.Match) -> str:
        word_before = match.group(1)
        word_after = match.group(2)
        # Check for Indonesian reduplication or repetition
        w1_low = word_before.lower()
        w2_low = word_after.lower()
        if w1_low == w2_low or w2_low.startswith(w1_low[:3]):
            return f"{word_before}-{word_after}"
        return f"{word_before}{word_after}"

    return re.sub(r"(\b[a-zA-Z]+)-\n\s*([a-zA-Z]+\b)", resolve_hyphen, text)


def is_heading_or_marker(line: str) -> bool:
    """Detect if a line represents a heading, list marker, or formula that should not be merged."""
    if not line:
        return True
    # List markers: (1), (a), a., 1., -, •
    if re.match(r"^(\(\d+\)|\([a-zA-Z]\)|\d+\.|\b[a-zA-Z]\.|\-|\•)\s*", line):
        return True
    # Known section or structural headings
    if re.match(
        r"^(BAB\b|PASAL\b|Semester\b|Program Studi\b|Masa Belajar\b|Pendaftaran\b|KRS Online\b|Ujian Akhir\b|Pelaksanaan\b|Penyusunan\b|Ketentuan\b|Visi\b|Misi\b|Tujuan\b)",
        line,
        re.IGNORECASE,
    ):
        return True
    # Short title case line with no punctuation at end
    if len(line) < 35 and re.match(r"^[A-Z][A-Za-z0-9\s\(\)/,]+$", line) and not line.endswith((".", ",", ";", ":")):
        return True
    # Formulas or separator lines
    if "---" in line or "∑" in line or "=" in line:
        return True
    return False


def unwrap_regulation_paragraphs(text: str) -> str:
    """Unwrap broken lines within paragraphs for regulation pages while preserving lists and headings."""
    lines = text.splitlines()
    unwrapped_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            unwrapped_lines.append("")
            i += 1
            continue

        while i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line:
                break
            # Do not merge if next line is a list item, heading, or formula
            if is_heading_or_marker(next_line):
                break
            # Do not merge if current line ends with sentence terminal punctuation or is a heading
            if re.search(r"[:.!?]$", line):
                break
            if is_heading_or_marker(line):
                break

            # Merge with space
            line = f"{line} {next_line}"
            i += 1

        unwrapped_lines.append(line)
        i += 1

    return "\n".join(unwrapped_lines)


def normalize_whitespace(text: str) -> str:
    """Normalize excessive horizontal spaces while keeping paragraph line breaks intact."""
    # Replace horizontal tabs or 3+ spaces with single space within line
    lines = [re.sub(r"[ \t]{2,}", " ", line).rstrip() for line in text.splitlines()]
    result = "\n".join(lines)
    # Collapse 3 or more consecutive newlines into 2
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip() + "\n"


def log_source_anomalies(text: str, page_num: int) -> None:
    """Log noted source anomalies without altering them, adhering to AGENTS.md rules."""
    if page_num == ACCREDITATION_PAGE and "PRINGKAT" in text:
        logger.info(
            f"[CLEAN LOG] Hal. {page_num}: Ditemukan typo sumber 'PRINGKAT' (dipertahankan sesuai aturan data-spec)."
        )


def clean_page_text(raw_text: str, page_num: int) -> str:
    """Clean and normalize raw extracted page text without semantic distortion."""
    log_source_anomalies(raw_text, page_num)

    # 1. Normalize drop shadow text artifacts
    text = normalize_shadow_text(raw_text)

    # 2. Normalize corrupted bullet glyphs
    text = normalize_bullets(text)

    # 3. De-hyphenate broken words across line breaks
    text = dehyphenate_text(text)

    # 4. Unwrap paragraph lines only for regulation pages (14-25)
    # Tables and curriculum pages preserve their strict line structure
    if page_num in REGULATION_PAGES:
        text = unwrap_regulation_paragraphs(text)

    # 5. Clean whitespace and blank lines
    text = normalize_whitespace(text)

    return text


def clean_file(raw_file: Path, clean_dir: Path) -> Path:
    """Clean a single raw text page file and save to clean directory."""
    raw_text = raw_file.read_text(encoding="utf-8")
    # Extract page number from filename page_{num:03d}.txt
    match = re.search(r"page_(\d+)\.txt", raw_file.name)
    page_num = int(match.group(1)) if match else 0

    cleaned = clean_page_text(raw_text, page_num)

    clean_dir.mkdir(parents=True, exist_ok=True)
    out_file = clean_dir / raw_file.name
    out_file.write_text(cleaned, encoding="utf-8")
    return out_file


def main() -> None:
    """Execute text cleaning pipeline CLI."""
    parser = argparse.ArgumentParser(
        description="Pembersihan dan normalisasi teks Panduan Akademik UMB."
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default="data/raw",
        help="Direktori teks mentah hasil ekstraksi (default: data/raw)",
    )
    parser.add_argument(
        "--clean-dir",
        type=str,
        default="data/clean",
        help="Direktori penyimpanan teks bersih (default: data/clean)",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=None,
        help="Bersihkan satu nomor halaman spesifik (contoh: --page 17 atau --page 11)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Bersihkan seluruh berkas teks di data/raw/",
    )

    args = parser.parse_args()
    raw_dir = Path(args.raw_dir)
    clean_dir = Path(args.clean_dir)

    if args.page is not None:
        target_name = f"page_{args.page:03d}.txt"
        target_file = raw_dir / target_name
        if not target_file.is_file():
            print(f"[CLEAN ERROR] File {target_file} tidak ditemukan. Jalankan extract.py lebih dulu.")
            return

        out_file = clean_file(target_file, clean_dir)
        print(f"[CLEAN] Sukses membersihkan {target_file.name} -> {out_file}")
        content = out_file.read_text(encoding="utf-8")
        print("-" * 50)
        print(f"Preview (300 karakter pertama):\n{content[:300]}")
        print("-" * 50)
        return

    if args.all:
        raw_files = sorted(raw_dir.glob("page_*.txt"))
        if not raw_files:
            print(f"[CLEAN ERROR] Tidak ada file page_*.txt di {raw_dir}. Jalankan extract.py dulu.")
            return

        print(f"[CLEAN] Memulai pembersihan {len(raw_files)} halaman...")
        for rf in raw_files:
            clean_file(rf, clean_dir)

        print(f"[CLEAN] Pembersihan selesai. Seluruh file tersimpan di {clean_dir}.")
        return

    print("Tentukan opsi:")
    print("  Gunakan --page <nomor> untuk membersihkan satu halaman (contoh: --page 17)")
    print("  Gunakan --all untuk membersihkan seluruh halaman di data/raw/")


if __name__ == "__main__":
    main()

