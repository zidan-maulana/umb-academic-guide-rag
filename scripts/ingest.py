"""Skrip ingest dan vektorisasi korpus chunks ke PostgreSQL + pgvector (docs/sdd.md).

Dilengkapi dengan:
- Batch embedding (mengirim 25-30 teks per API call, memangkas 96% kuota request).
- Pacing delay & auto-retry exponential backoff untuk mencegah Rate Limit HTTP 429.
- Opsi --reset untuk membersihkan tabel chunks sebelum mulai.
- Fitur resume otomatis (melewati chunk yang sudah tersimpan di database).
- Safe commit per batch ke database PostgreSQL.
"""

import argparse
import json
import os
import time
from typing import Any, Dict, List, Set

from backend.app.db import close_db_pool, get_db_connection
from backend.app.services.embedding import embed_documents_batch


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


def get_existing_chunk_ids() -> Set[str]:
    """Ambil set ID chunk yang sudah tersimpan dan memiliki vektor embedding di database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM chunks WHERE embedding IS NOT NULL;")
            rows = cur.fetchall()
            return {r[0] for r in rows}


def reset_chunks_table() -> None:
    """Kosongkan tabel chunks di database (TRUNCATE)."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            print("[RESET] Mengosongkan tabel chunks di database...", end=" ", flush=True)
            cur.execute("TRUNCATE TABLE chunks;")
            conn.commit()
            print("Selesai! Tabel telah bersih.")


def ingest_chunks_batch(
    filepath: str,
    batch_size: int = 20,
    delay: float = 12.0,
    reset: bool = False,
) -> int:
    """Proses embedding batch dan simpan seluruh chunk ke PostgreSQL + pgvector secara aman."""
    all_chunks = load_chunks_from_jsonl(filepath)
    total_file = len(all_chunks)
    print(f"\n=== PROSES INGEST KORPUS ({filepath}) ===")
    print(f"Total chunk dalam file: {total_file}")

    if reset:
        reset_chunks_table()
        chunks_to_process = all_chunks
    else:
        existing_ids = get_existing_chunk_ids()
        if existing_ids:
            print(f"[RESUME] Ditemukan {len(existing_ids)} chunk yang sudah ada di database.")
            chunks_to_process = [c for c in all_chunks if c["id"] not in existing_ids]
            print(f"[RESUME] Sisa chunk yang perlu di-vektorisasi: {len(chunks_to_process)}")
        else:
            chunks_to_process = all_chunks

    if not chunks_to_process:
        print("[INFO] Seluruh chunk sudah tersimpan di database. Tidak ada yang perlu diproses.")
        return 0

    total_process = len(chunks_to_process)
    num_batches = (total_process + batch_size - 1) // batch_size
    print(f"[BATCH CONFIG] Ukuran batch: {batch_size} chunk/request | Total batch: {num_batches} | Jeda: {delay}s")

    success_count = 0
    start_time = time.perf_counter()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for b_idx in range(num_batches):
                b_start = b_idx * batch_size
                b_end = min(b_start + batch_size, total_process)
                batch_items = chunks_to_process[b_start:b_end]

                print(
                    f"\n[Batch {b_idx + 1}/{num_batches}] Memproses chunk #{b_start + 1} - #{b_end} "
                    f"({b_end}/{total_process} - {(b_end / total_process * 100):.1f}%)...",
                    flush=True,
                )

                # Siapkan tuple (konten, title) untuk batch embedding
                embed_inputs = [
                    (
                        item["konten"],
                        item.get("topik") or item.get("mata_kuliah") or item.get("bagian"),
                    )
                    for item in batch_items
                ]

                # Panggil Gemini Embedding API sekali per batch (dengan retry backoff bawaan)
                t0_emb = time.perf_counter()
                vectors = embed_documents_batch(embed_inputs)
                elapsed_emb = time.perf_counter() - t0_emb
                print(f"  -> Vektorisasi {len(vectors)} chunk selesai dalam {elapsed_emb:.2f}s.")

                # Simpan batch ke PostgreSQL
                for item, vector in zip(batch_items, vectors):
                    params = {
                        "id": item["id"],
                        "konten": item["konten"],
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

                # Safe commit per batch
                conn.commit()
                print(f"  -> Tersimpan permanen ke PostgreSQL. Total tersimpan: {success_count}/{total_process}.")

                # Pacing sleep untuk menjaga limit RPM
                if b_idx + 1 < num_batches and delay > 0:
                    time.sleep(delay)

    total_elapsed = time.perf_counter() - start_time
    print(f"\n=======================================================")
    print(f"Proses ingest tuntas dalam {total_elapsed:.1f} detik ({total_elapsed / 60:.2f} menit)!")
    print(f"Total chunk berhasil di-vektorisasi dan disimpan: {success_count}")
    print(f"=======================================================\n")

    return success_count


def main() -> None:
    """Entry point CLI untuk eksekusi proses ingest."""
    default_file = (
        "data/chunks/academic_guide_chunks.jsonl"
        if os.path.exists("data/chunks/academic_guide_chunks.jsonl")
        else "data/chunks/mock_chunks.jsonl"
    )

    parser = argparse.ArgumentParser(
        description="Ingest batch chunk teks ke PostgreSQL + pgvector dengan anti-rate-limit"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=default_file,
        help=f"Jalur file JSON Lines chunk (default: {default_file})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Jumlah chunk per panggilan API embedding (default: 20)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=12.0,
        help="Jeda detik antar batch untuk keamanan limit RPM (default: 12.0)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Kosongkan (TRUNCATE) tabel chunks sebelum memulai ingest baru",
    )
    args = parser.parse_args()

    try:
        ingest_chunks_batch(
            filepath=args.file,
            batch_size=args.batch_size,
            delay=args.delay,
            reset=args.reset,
        )
    finally:
        close_db_pool()


if __name__ == "__main__":
    main()
