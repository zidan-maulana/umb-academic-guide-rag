"""Script for text chunking and metadata labeling (docs/data-spec.md Section 5 and Section 7).

Chunking rules from docs/data-spec.md:
- Regulation content: chunked by article or unified topic.
- Multi-topic pages (e.g. page 17): split strictly by topic, not by page.
- Course curriculum: chunked per individual course unit.
- Vision and mission: chunked per faculty section.
- Accreditation: chunked per table row (one study program per chunk).
- Format: JSON Lines (UTF-8) saved in data/chunks/.
- Mandatory fields: id, konten, halaman, bagian, jenis_konten.
- Metadata fields: topik, fakultas, program_studi, jenjang, mata_kuliah, nama_inggris,
  kode_mk, semester, sks, peringkat_akreditasi (set to null if not applicable).
- Quality validation: unique IDs, exact text presence on labeled page, consistent code format.
"""


import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Valid values per docs/data-spec.md Section 6
BagianType = Literal["Regulasi", "Kurikulum", "Profil", "Akreditasi"]
JenisKontenType = Literal[
    "aturan", "mata_kuliah", "visi_misi", "akreditasi", "ringkasan_semester"
]
FakultasType = Literal["FDSK", "FT", "Fasilkom", "FEB", "Fikom", "FPsi"]
JenjangType = Literal[
    "Institusi", "Diploma Tiga", "Sarjana", "Magister", "Doktor", "Profesi"
]


class ChunkModel(BaseModel):
    """Schema model for an academic guide chunk per docs/data-spec.md Section 5."""

    id: str = Field(..., description="Unique chunk ID")
    konten: str = Field(..., description="Chunk textual content")
    halaman: int = Field(..., description="PDF page number")
    bagian: BagianType = Field(..., description="Section category")
    jenis_konten: JenisKontenType = Field(..., description="Type of content")
    topik: Optional[str] = Field(None, description="Topic title for regulations")
    fakultas: Optional[FakultasType] = Field(None, description="Faculty code")
    program_studi: Optional[str] = Field(None, description="Study program name")
    jenjang: Optional[JenjangType] = Field(None, description="Degree level")
    mata_kuliah: Optional[str] = Field(None, description="Course Indonesian name")
    nama_inggris: Optional[str] = Field(None, description="Course English name")
    kode_mk: Optional[str] = Field(None, description="Course code")
    semester: Optional[int] = Field(None, description="Semester integer 1-8")
    sks: Optional[int] = Field(None, description="Credit units (SKS)")
    peringkat_akreditasi: Optional[str] = Field(
        None, description="Accreditation rank"
    )


# Page mapping for Faculty and Program Studi
PAGE_MAPPING = {
    # FDSK
    27: ("FDSK", None, "Sarjana"),
    28: ("FDSK", None, "Sarjana"),
    29: ("FDSK", "Desain Produk", "Sarjana"),
    30: ("FDSK", "Desain Produk", "Sarjana"),
    31: ("FDSK", "Desain Produk", "Sarjana"),
    32: ("FDSK", "Desain Produk", "Sarjana"),
    33: ("FDSK", "Desain Interior", "Sarjana"),
    34: ("FDSK", "Desain Interior", "Sarjana"),
    35: ("FDSK", "Desain Interior", "Sarjana"),
    36: ("FDSK", "Desain Interior", "Sarjana"),
    37: ("FDSK", "Desain Komunikasi Visual", "Sarjana"),
    38: ("FDSK", "Desain Komunikasi Visual", "Sarjana"),
    39: ("FDSK", "Desain Komunikasi Visual", "Sarjana"),
    40: ("FDSK", "Desain Komunikasi Visual", "Sarjana"),
    # FT
    41: ("FT", None, "Sarjana"),
    42: ("FT", None, "Sarjana"),
    43: ("FT", "Teknik Sipil", "Sarjana"),
    44: ("FT", "Teknik Sipil", "Sarjana"),
    45: ("FT", "Teknik Sipil", "Sarjana"),
    46: ("FT", "Teknik Sipil", "Sarjana"),
    47: ("FT", "Arsitektur", "Sarjana"),
    48: ("FT", "Arsitektur", "Sarjana"),
    49: ("FT", "Arsitektur", "Sarjana"),
    50: ("FT", "Arsitektur", "Sarjana"),
    51: ("FT", "Teknik Mesin", "Sarjana"),
    52: ("FT", "Teknik Mesin", "Sarjana"),
    53: ("FT", "Teknik Mesin", "Sarjana"),
    54: ("FT", "Teknik Mesin", "Sarjana"),
    55: ("FT", "Teknik Elektro", "Sarjana"),
    56: ("FT", "Teknik Elektro", "Sarjana"),
    57: ("FT", "Teknik Elektro", "Sarjana"),
    58: ("FT", "Teknik Elektro", "Sarjana"),
    59: ("FT", "Teknik Industri", "Sarjana"),
    60: ("FT", "Teknik Industri", "Sarjana"),
    61: ("FT", "Teknik Industri", "Sarjana"),
    62: ("FT", "Teknik Industri", "Sarjana"),
    # Fasilkom
    63: ("Fasilkom", None, "Sarjana"),
    64: ("Fasilkom", None, "Sarjana"),
    65: ("Fasilkom", "Teknik Informatika", "Sarjana"),
    66: ("Fasilkom", "Teknik Informatika", "Sarjana"),
    67: ("Fasilkom", "Teknik Informatika", "Sarjana"),
    68: ("Fasilkom", "Sistem Informasi", "Sarjana"),
    69: ("Fasilkom", "Sistem Informasi", "Sarjana"),
    70: ("Fasilkom", "Sistem Informasi", "Sarjana"),
    # FEB
    71: ("FEB", None, "Sarjana"),
    72: ("FEB", None, "Sarjana"),
    73: ("FEB", "Manajemen", "Sarjana"),
    74: ("FEB", "Manajemen", "Sarjana"),
    75: ("FEB", "Manajemen", "Sarjana"),
    76: ("FEB", "Manajemen", "Sarjana"),
    77: ("FEB", "Akuntansi", "Sarjana"),
    78: ("FEB", "Akuntansi", "Sarjana"),
    79: ("FEB", "Akuntansi", "Sarjana"),
    80: ("FEB", "Akuntansi", "Sarjana"),
    81: ("FEB", "Manajemen Perusahaan", "Diploma Tiga"),
    82: ("FEB", "Manajemen Perusahaan", "Diploma Tiga"),
    83: ("FEB", "Akuntansi", "Diploma Tiga"),
    # Fikom
    84: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    85: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    86: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    87: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    88: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    89: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    90: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    91: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    92: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    93: ("Fikom", "Ilmu Komunikasi", "Sarjana"),
    # FPsi
    94: ("FPsi", "Psikologi", "Sarjana"),
    95: ("FPsi", "Psikologi", "Sarjana"),
    96: ("FPsi", "Psikologi", "Sarjana"),
    97: ("FPsi", "Psikologi", "Sarjana"),
    98: ("FPsi", "Psikologi", "Sarjana"),
}


def chunk_accreditation_page(text: str, page_num: int = 11) -> list[ChunkModel]:
    """Parse accreditation table rows from page 11 into individual chunks."""
    chunks: list[ChunkModel] = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    current_fakultas: Optional[FakultasType] = None
    rank_options = ["Unggul", "Baik Sekali", "Baik", "Sementara", "A", "B"]

    seq = 1
    for line in lines:
        # Detect faculty headers in the table
        if "Fakultas Ekonomi dan Bisnis" in line:
            current_fakultas = "FEB"
            continue
        elif line == "Teknik":
            current_fakultas = "FT"
            continue
        elif "Ilmu Komunikasi" in line and "Terakreditasi" not in line:
            current_fakultas = "Fikom"
            continue
        elif "Ilmu komputer" in line:
            current_fakultas = "Fasilkom"
            continue
        elif line == "Psikologi":
            current_fakultas = "FPsi"
            continue
        elif "Desain dan Seni Kreatif" in line:
            current_fakultas = "FDSK"
            continue

        if "Terakreditasi" not in line:
            continue

        parts = line.split("Terakreditasi")
        nama_raw = parts[0].strip()
        rank_raw = parts[1].strip() if len(parts) > 1 else ""

        # Match rank
        matched_rank = None
        for r in rank_options:
            if rank_raw.startswith(r) or rank_raw == r:
                matched_rank = r
                break
        if not matched_rank:
            matched_rank = rank_raw or "Terakreditasi"

        # Determine level (jenjang) and cleaned program name
        jenjang: JenjangType = "Sarjana"
        fakultas = current_fakultas

        if "Institusi" in nama_raw:
            jenjang = "Institusi"
            nama_prodi = "Institusi Universitas Mercu Buana"
            fakultas = None
            konten = (
                f"Institusi Universitas Mercu Buana berstatus Terakreditasi "
                f"dengan peringkat {matched_rank}, menurut Panduan Akademik 2025/2026."
            )
        else:
            if "Diploma Tiga" in nama_raw:
                jenjang = "Diploma Tiga"
            elif "Sarjana" in nama_raw:
                jenjang = "Sarjana"
            elif "Magister" in nama_raw:
                jenjang = "Magister"
            elif "Doktor" in nama_raw:
                jenjang = "Doktor"
            elif "Profesi" in nama_raw:
                jenjang = "Profesi"

            # Clean name from parenthesized level
            nama_prodi = re.sub(r"\s*\(Program [^)]+\)", "", nama_raw).strip()

            konten = (
                f"Program Studi {nama_prodi} ({jenjang}) berstatus Terakreditasi "
                f"dengan peringkat {matched_rank}, menurut Panduan Akademik 2025/2026."
            )

        chunk_id = f"akreditasi-{page_num:02d}-{seq:02d}"
        chunks.append(
            ChunkModel(
                id=chunk_id,
                konten=konten,
                halaman=page_num,
                bagian="Akreditasi",
                jenis_konten="akreditasi",
                topik="Status dan Peringkat Akreditasi",
                fakultas=fakultas,
                program_studi=nama_prodi,
                jenjang=jenjang,
                peringkat_akreditasi=matched_rank,
            )
        )
        seq += 1

    return chunks


def chunk_regulation_page(text: str, page_num: int) -> list[ChunkModel]:
    """Chunk regulation page by article or distinct topic."""
    chunks: list[ChunkModel] = []
    lines = text.splitlines()

    # Split paragraphs by double newline
    raw_paras = [p.strip() for p in text.split("\n\n") if p.strip()]

    # If page has multiple distinct sections, split into topics
    topic_header = "Regulasi Akademik"
    current_topic_text: list[str] = []
    seq = 1

    for para in raw_paras:
        first_line = para.splitlines()[0].strip()
        # Check if paragraph begins with a clear topic heading
        if (
            len(first_line) < 50
            and re.match(
                r"^(BAB\b|PASAL\b|Ketentuan\b|Kurikulum\b|Semester\b|Kegiatan\b|Pelaksanaan\b|Jadwal\b|Waktu\b|Kehadiran\b|Evaluasi\b|Beban Belajar\b|Masa Belajar\b|Pendaftaran\b|KRS Online\b|Ujian Akhir\b|Pelaksanaan UAS\b|Cuti Akademik\b|Penyusunan Tugas\b|Ujian Tugas\b|Pindah Studi\b|Sistem Evaluasi\b|Sistem Penilaian\b|Putus Studi\b|Predikat Kelulusan\b|Kelulusan Studi\b)",
                first_line,
                re.IGNORECASE,
            )
            and not re.match(r"^(\(\d+\)|\d+\.)", first_line)
        ):
            if current_topic_text:
                full_konten = "\n\n".join(current_topic_text)
                chunks.append(
                    ChunkModel(
                        id=f"aturan-{page_num:02d}-{seq:02d}",
                        konten=full_konten,
                        halaman=page_num,
                        bagian="Regulasi",
                        jenis_konten="aturan",
                        topik=topic_header,
                    )
                )
                seq += 1
                current_topic_text = []

            topic_header = first_line

        current_topic_text.append(para)

    if current_topic_text:
        full_konten = "\n\n".join(current_topic_text)
        chunks.append(
            ChunkModel(
                id=f"aturan-{page_num:02d}-{seq:02d}",
                konten=full_konten,
                halaman=page_num,
                bagian="Regulasi",
                jenis_konten="aturan",
                topik=topic_header,
            )
        )

    return chunks


def chunk_vision_mission_page(
    text: str, page_num: int, fakultas: FakultasType
) -> list[ChunkModel]:
    """Chunk faculty profile and vision/mission into a single chunk."""
    chunk = ChunkModel(
        id=f"visi_misi-{page_num:02d}-01",
        konten=text.strip(),
        halaman=page_num,
        bagian="Profil",
        jenis_konten="visi_misi",
        topik=f"Visi dan Misi Fakultas {fakultas}",
        fakultas=fakultas,
    )
    return [chunk]


def chunk_curriculum_page(
    text: str, page_num: int, fakultas: FakultasType, prodi: str, jenjang: JenjangType
) -> tuple[list[ChunkModel], list[ChunkModel]]:
    """Parse curriculum page into course chunks and semester summary chunks."""
    course_chunks: list[ChunkModel] = []
    summary_chunks: list[ChunkModel] = []

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    code_pattern = re.compile(r"\b([A-Z]\d{8,9})\b")

    semester_courses: dict[int, list[dict[str, Any]]] = {}
    current_sem: Optional[int] = None

    i = 0
    seq = 1
    while i < len(lines):
        line = lines[i]
        sem_m = re.search(r"Semester\s*([1-8])", line, re.IGNORECASE)
        if sem_m:
            current_sem = int(sem_m.group(1))
            if current_sem not in semester_courses:
                semester_courses[current_sem] = []
            i += 1
            continue

        m = code_pattern.search(line)
        if m:
            code = m.group(1)

            # Indonesian Name (previous line if valid)
            nama_id = (
                lines[i - 1]
                if i > 0
                and not code_pattern.search(lines[i - 1])
                and "Semester" not in lines[i - 1]
                and "Program Studi" not in lines[i - 1]
                else ""
            )

            # SKS detection
            sks: Optional[int] = None
            sks_m = re.search(r"\b([1-6])\s*$", line)
            if sks_m:
                sks = int(sks_m.group(1))
            elif i + 1 < len(lines) and re.match(r"^[1-6]$", lines[i + 1]):
                sks = int(lines[i + 1])
            elif i + 2 < len(lines) and re.match(r"^[1-6]$", lines[i + 2]):
                sks = int(lines[i + 2])
            elif i > 0 and re.match(r"^[1-6]$", lines[i - 1]):
                sks = int(lines[i - 1])

            # English Name
            nama_en = line.replace(code, "").strip()
            if sks:
                nama_en = re.sub(rf"\b{sks}\s*$", "", nama_en).strip()
            if (
                not nama_en
                and i + 1 < len(lines)
                and not code_pattern.search(lines[i + 1])
                and "Semester" not in lines[i + 1]
                and not re.match(r"^[1-6]$", lines[i + 1])
            ):
                nama_en = lines[i + 1]

            if not nama_id and nama_en:
                nama_id = nama_en

            # Formulate self-contained narrative content
            sks_text = f", {sks} SKS" if sks else ""
            sem_text = f", Semester {current_sem}" if current_sem else ""
            en_text = f" ({nama_en})" if nama_en and nama_en != nama_id else ""
            konten = (
                f"{nama_id}{en_text}, kode {code}{sks_text}{sem_text}, "
                f"Program Studi {prodi}."
            )

            course_chunks.append(
                ChunkModel(
                    id=f"mata_kuliah-{page_num:02d}-{seq:02d}",
                    konten=konten,
                    halaman=page_num,
                    bagian="Kurikulum",
                    jenis_konten="mata_kuliah",
                    fakultas=fakultas,
                    program_studi=prodi,
                    jenjang=jenjang,
                    mata_kuliah=nama_id,
                    nama_inggris=nama_en or nama_id,
                    kode_mk=code,
                    semester=current_sem,
                    sks=sks,
                )
            )
            seq += 1

            if current_sem:
                semester_courses[current_sem].append(
                    {"name": nama_id, "code": code, "sks": sks}
                )

        i += 1

    # Build semester summary chunks
    sum_seq = 1
    for sem_num, c_list in semester_courses.items():
        if not c_list:
            continue
        c_descs = [
            f"{c['name']} ({c['sks']} SKS)" if c["sks"] else c["name"]
            for c in c_list
        ]
        total_sks = sum(c["sks"] for c in c_list if c["sks"])
        sks_summary = f" Total: {total_sks} SKS." if total_sks > 0 else ""
        konten = (
            f"Daftar mata kuliah Semester {sem_num} Program Studi {prodi} ({jenjang}): "
            f"{', '.join(c_descs)}.{sks_summary}"
        )

        summary_chunks.append(
            ChunkModel(
                id=f"ringkasan_semester-{page_num:02d}-{sum_seq:02d}",
                konten=konten,
                halaman=page_num,
                bagian="Kurikulum",
                jenis_konten="ringkasan_semester",
                fakultas=fakultas,
                program_studi=prodi,
                jenjang=jenjang,
                semester=sem_num,
                sks=total_sks if total_sks > 0 else None,
            )
        )
        sum_seq += 1

    return course_chunks, summary_chunks


def process_all_chunks(clean_dir: Path, output_file: Path) -> list[ChunkModel]:
    """Process all cleaned text files into the full chunk corpus."""
    all_chunks: list[ChunkModel] = []
    clean_files = sorted(clean_dir.glob("page_*.txt"))

    vision_pages = {28, 42, 64, 72, 85, 95}

    for cf in clean_files:
        match = re.search(r"page_(\d+)\.txt", cf.name)
        if not match:
            continue
        page_num = int(match.group(1))
        text = cf.read_text(encoding="utf-8")

        if page_num == 11:
            all_chunks.extend(chunk_accreditation_page(text, page_num))
        elif 14 <= page_num <= 25:
            all_chunks.extend(chunk_regulation_page(text, page_num))
        elif page_num in vision_pages:
            fakultas_meta = PAGE_MAPPING.get(page_num, (None, None, None))[0]
            if fakultas_meta:
                all_chunks.extend(
                    chunk_vision_mission_page(text, page_num, fakultas_meta)
                )
        elif 27 <= page_num <= 98:
            mapping = PAGE_MAPPING.get(page_num)
            if mapping and mapping[1]:
                fakultas, prodi, jenjang = mapping
                course_chunks, summary_chunks = chunk_curriculum_page(
                    text, page_num, fakultas, prodi, jenjang
                )
                all_chunks.extend(course_chunks)
                all_chunks.extend(summary_chunks)

    # Save to JSON Lines format (UTF-8)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            # model_dump ensures all 15 fields are serialized with nulls if empty
            line_json = json.dumps(chunk.model_dump(), ensure_ascii=False)
            f.write(f"{line_json}\n")

    return all_chunks


def validate_corpus(chunks: list[ChunkModel]) -> bool:
    """Validate data quality per docs/data-spec.md Section 10."""
    logger.info("=== VALIDASI KUALITAS DATA KORPUS ===")

    # 1. Unikitas ID
    all_ids = [c.id for c in chunks]
    unique_ids = set(all_ids)
    if len(all_ids) != len(unique_ids):
        duplicates = [x for x in all_ids if all_ids.count(x) > 1]
        logger.error(f"[VALIDASI GAGAL] Ditemukan ID duplikat: {set(duplicates)}")
        return False
    logger.info(f"[VALIDASI OK] Seluruh {len(all_ids)} ID chunk unik.")

    # 2. Konten tidak kosong
    empty_content = [c.id for c in chunks if not c.konten.strip()]
    if empty_content:
        logger.error(
            f"[VALIDASI GAGAL] Ditemukan chunk dengan konten kosong: {empty_content}"
        )
        return False
    logger.info("[VALIDASI OK] Seluruh chunk memiliki teks konten valid.")

    # 3. Format kode mata kuliah
    invalid_codes = [
        c.kode_mk
        for c in chunks
        if c.kode_mk and not re.match(r"^[A-Z]\d{8,9}$", c.kode_mk)
    ]
    if invalid_codes:
        logger.error(
            f"[VALIDASI GAGAL] Format kode MK tidak valid: {set(invalid_codes)}"
        )
        return False
    logger.info("[VALIDASI OK] Format kode mata kuliah konsisten.")

    # 4. Ringkasan jumlah chunk per jenis_konten
    summary: dict[str, int] = {}
    for c in chunks:
        summary[c.jenis_konten] = summary.get(c.jenis_konten, 0) + 1

    logger.info("=== RINGKASAN JUMLAH CHUNK ===")
    for k, v in sorted(summary.items()):
        logger.info(f"  - {k}: {v} chunk")
    logger.info(f"  TOTAL: {len(chunks)} chunk.")
    logger.info("=====================================")
    return True


def main() -> None:
    """Execute chunking and metadata enrichment pipeline."""
    parser = argparse.ArgumentParser(
        description="Chunking logis dan pelabelan metadata Panduan Akademik UMB."
    )
    parser.add_argument(
        "--clean-dir",
        type=str,
        default="data/clean",
        help="Direktori teks bersih (default: data/clean)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/chunks/academic_guide_chunks.jsonl",
        help="Path file output JSON Lines (default: data/chunks/academic_guide_chunks.jsonl)",
    )

    args = parser.parse_args()
    clean_dir = Path(args.clean_dir)
    output_path = Path(args.output)

    logger.info(f"[CHUNK] Memulai proses chunking dari {clean_dir}...")
    chunks = process_all_chunks(clean_dir, output_path)
    logger.info(
        f"[CHUNK] Sukses menghasilkan {len(chunks)} chunk di {output_path}."
    )

    is_valid = validate_corpus(chunks)
    if is_valid:
        logger.info("[CHUNK] Validasi sukses! Korpus siap diserahterimakan.")
    else:
        logger.error("[CHUNK] Terdapat kesalahan validasi data.")


if __name__ == "__main__":
    main()

