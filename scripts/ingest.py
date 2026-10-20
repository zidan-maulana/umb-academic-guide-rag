"""Skrip ingest dan vektorisasi korpus chunks ke PostgreSQL + pgvector (docs/sdd.md)."""

import argparse
import json
import os
from typing import Any, Dict, List

from backend.app.db import close_db_pool, get_db_connection
from backend.app.services.embedding import embed_document


UPSERT_CHUNK_SQL = """
INSERT INTO chunks (
    id, konten, halaman, bagian, jenis_konten, topik,
    fakultas, program_studi, jenjang, mata_kuliah, nama_inggris,
    kode_mk, semester, sks, peringkat_akreditasi, embedding
) VALUES (
    %(id)s, %(konten)s, %(halaman)s, %(bagian)s, %(jenis_konten)s, %(topik)s,
    %(fakultas)s, %(program_studi)s, %(jenjang)s, %(mata_kuliah)s, %(nama_inggris)s,
    %(kode_mk)s, %(semester)s, %(sks)s, %(peringkat_akreditasi)s, %(embedding)s
)
ON CONFLICT (id) DO UPDATE SET
    konten = EXCLUDED.konten,
    halaman = EXCLUDED.halaman,
    bagian = EXCLUDED.bagian,
    jenis_konten = EXCLUDED.jenis_konten,
    topik = EXCLUDED.topik,
    fakultas = EXCLUDED.fakultas,
    program_studi = EXCLUDED.program_studi,
    jenjang = EXCLUDED.jenjang,
    mata_kuliah = EXCLUDED.mata_kuliah,
    nama_inggris = EXCLUDED.nama_inggris,
    kode_mk = EXCLUDED.kode_mk,
    semester = EXCLUDED.semester,
    sks = EXCLUDED.sks,
    peringkat_akreditasi = EXCLUDED.peringkat_akreditasi,
    embedding = EXCLUDED.embedding,
    created_at = CURRENT_TIMESTAMP;
"""


def load_chunks_from_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Muat dan validasi record chunk dari berkas JSON Lines."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Berkas chunk tidak ditemukan: {filepath}")

    chunks: List[Dict[str, Any]] = []
    required_keys = {"id", "konten", "halaman", "bagian", "jenis_konten"}

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue

            item = json.loads(line_str)
            missing = required_keys - set(item.keys())
            if missing:
                raise ValueError(f"Baris {line_num} kurang field wajib: {missing}")

            chunks.append(item)

    return chunks


def ingest_chunks(filepath: str) -> int:
    """Proses embedding dan simpan seluruh chunk ke database secara idempotent."""
    chunks = load_chunks_from_jsonl(filepath)
    total = len(chunks)
    print(f"Memulai ingest {total} chunk dari: {filepath}")

    success_count = 0
    failed: list[str] = []

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for idx, item in enumerate(chunks, start=1):
                chunk_id = item["id"]
                konten = item["konten"]
                title = item.get("topik") or item.get("mata_kuliah") or item.get("bagian")

                print(f"[{idx}/{total}] Vektorisasi chunk: {chunk_id}...", end=" ", flush=True)

                try:
                    vector = embed_document(text=konten, title=title)

                    params = {
                        "id": chunk_id,
                        "konten": konten,
                        "halaman": item["halaman"],
                        "bagian": item["bagian"],
                        "jenis_konten": item["jenis_konten"],
                        "topik": item.get("topik"),
                        "fakultas": item.get("fakultas"),
                        "program_studi": item.get("program_studi"),
                        "jenjang": item.get("jenjang"),
                        "mata_kuliah": item.get("mata_kuliah"),
                        "nama_inggris": item.get("nama_inggris"),
                        "kode_mk": item.get("kode_mk"),
                        "semester": item.get("semester"),
                        "sks": item.get("sks"),
                        "peringkat_akreditasi": item.get("peringkat_akreditasi"),
                        "embedding": vector,
                    }

                    cur.execute(UPSERT_CHUNK_SQL, params)
                    success_count += 1
                    print("Tersimpan!")
                except Exception as exc:
                    failed.append(chunk_id)
                    print(f"GAGAL — {exc}")

            conn.commit()

    if failed:
        print(f"\n⚠ {len(failed)} chunk gagal: {failed}")

    return success_count


def main() -> None:
    """Entry point CLI untuk eksekusi proses ingest."""
    parser = argparse.ArgumentParser(description="Ingest chunk teks ke PostgreSQL + pgvector")
    parser.add_argument(
        "--file",
        type=str,
        default="data/chunks/mock_chunks.jsonl",
        help="Jalur file JSON Lines chunk (default: data/chunks/mock_chunks.jsonl)",
    )
    args = parser.parse_args()

    try:
        count = ingest_chunks(args.file)
        print(f"\nProses selesai! Total {count} chunk berhasil di-ingest ke pgvector.")
    finally:
        close_db_pool()


if __name__ == "__main__":
    main()
