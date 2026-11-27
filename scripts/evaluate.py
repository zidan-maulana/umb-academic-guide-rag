"""Skrip evaluasi kuantitatif pipeline RAG Panduan Akademik UMB (docs/evaluation-plan.md).

Metrik yang dihitung:
1. Hit Rate@K: Persentase pertanyaan dalam cakupan yang menemukan minimal satu halaman kunci pada chunk retrieval.
2. Citation Accuracy: Persentase jawaban yang seluruh sitasi halamannya tepat ada di halaman kunci.
3. Correct Rejection Rate: Persentase pertanyaan di luar cakupan yang berhasil ditolak dengan status not_found.
4. Rata-rata Latensi: Waktu eksekusi rata-rata per kueri.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

# Tambahkan direktori root proyek ke sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.generate import parse_cited_pages

logger = logging.getLogger("umb_rag.eval")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_dataset(dataset_path: str | Path) -> list[dict[str, Any]]:
    """Muat dataset evaluasi berformat JSON Lines atau JSON array."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Berkas dataset tidak ditemukan: {path}")

    items: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content.startswith("["):
            items = json.loads(content)
        else:
            for line_no, line in enumerate(content.splitlines(), start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    logger.warning("Gagal mem-parsing baris %d: %s", line_no, exc)

    logger.info("Berhasil memuat %d item evaluasi dari %s", len(items), path)
    return items


def evaluate_single_query(
    item: dict[str, Any],
    query_fn: Callable[[ChatRequest], ChatResponse],
) -> dict[str, Any]:
    """Jalankan satu pertanyaan uji dan hitung skor evaluasinya."""
    qid = item.get("id", "unknown")
    question = item.get("pertanyaan", "")
    jenis = item.get("jenis", "dalam_cakupan")
    halaman_kunci = [int(p) for p in item.get("halaman_kunci", [])]
    jawaban_kunci = item.get("jawaban_kunci", "")

    req = ChatRequest(question=question)

    start_time = time.perf_counter()
    resp = query_fn(req)
    latency_sec = time.perf_counter() - start_time

    is_rejected = (
        resp.status == "not_found"
        or resp.answer.strip() == "Informasi tidak ditemukan di panduan."
    )

    retrieved_pages = sorted({s.halaman for s in resp.sources if s.halaman is not None})
    cited_pages = parse_cited_pages(resp.answer)
    effective_cited_pages = cited_pages if cited_pages else retrieved_pages

    # 1. Evaluasi Penolakan (Rejection)
    correct_rejection: bool | None = None
    if jenis == "di_luar_cakupan":
        correct_rejection = is_rejected

    # 2. Evaluasi Temu Balik (Retrieval Hit@K)
    hit_at_k: bool | None = None
    if jenis == "dalam_cakupan":
        if halaman_kunci:
            hit_at_k = any(p in retrieved_pages for p in halaman_kunci)
        else:
            hit_at_k = len(retrieved_pages) > 0

    # 3. Evaluasi Ketepatan Sitasi (Citation Accuracy)
    citation_correct: bool | None = None
    if jenis == "dalam_cakupan" and not is_rejected:
        if halaman_kunci:
            if effective_cited_pages:
                all_cited_in_key = all(p in halaman_kunci for p in effective_cited_pages)
                any_key_cited = any(p in effective_cited_pages for p in halaman_kunci)
                citation_correct = all_cited_in_key and any_key_cited
            else:
                citation_correct = False
        else:
            citation_correct = True

    return {
        "id": qid,
        "kategori": item.get("kategori", "-"),
        "jenis": jenis,
        "pertanyaan": question,
        "jawaban_kunci": jawaban_kunci,
        "halaman_kunci": halaman_kunci,
        "status": resp.status,
        "jawaban": resp.answer,
        "retrieved_pages": retrieved_pages,
        "cited_pages": effective_cited_pages,
        "is_rejected": is_rejected,
        "hit_at_k": hit_at_k,
        "citation_correct": citation_correct,
        "correct_rejection": correct_rejection,
        "latency_sec": round(latency_sec, 3),
    }


def compute_metrics(eval_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Agregasi hasil per pertanyaan menjadi ringkasan metrik kuantitatif."""
    total = len(eval_results)
    if total == 0:
        return {}

    in_scope = [r for r in eval_results if r["jenis"] == "dalam_cakupan"]
    out_scope = [r for r in eval_results if r["jenis"] == "di_luar_cakupan"]

    # Hit Rate@K
    hits = [r["hit_at_k"] for r in in_scope if r["hit_at_k"] is not None]
    hit_rate = (sum(hits) / len(hits) * 100) if hits else 0.0

    # Citation Accuracy
    citations = [r["citation_correct"] for r in in_scope if r["citation_correct"] is not None]
    citation_accuracy = (sum(citations) / len(citations) * 100) if citations else 0.0

    # Correct Rejection Rate
    rejections = [r["correct_rejection"] for r in out_scope if r["correct_rejection"] is not None]
    rejection_rate = (sum(rejections) / len(rejections) * 100) if rejections else 0.0

    # Latensi
    latencies = [r["latency_sec"] for r in eval_results]
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

    return {
        "total_pertanyaan": total,
        "jumlah_dalam_cakupan": len(in_scope),
        "jumlah_di_luar_cakupan": len(out_scope),
        "hit_rate_at_k": round(hit_rate, 2),
        "citation_accuracy": round(citation_accuracy, 2),
        "correct_rejection_rate": round(rejection_rate, 2),
        "avg_latency_sec": round(avg_latency, 3),
    }


def render_markdown_report(metrics: dict[str, Any], results: list[dict[str, Any]]) -> str:
    """Format hasil evaluasi menjadi laporan Markdown terstruktur."""
    lines: list[str] = [
        "# Laporan Evaluasi Kuantitatif RAG Panduan Akademik UMB",
        f"Tanggal Evaluasi: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Ringkasan Metrik Kinerja",
        "",
        "| Metrik | Skor | Keterangan |",
        "|---|---|---|",
        f"| **Total Pertanyaan** | {metrics.get('total_pertanyaan', 0)} | Seluruh set pertanyaan evaluasi |",
        f"| **Retrieval Hit Rate** | {metrics.get('hit_rate_at_k', 0.0)}% | Minimal 1 halaman kunci ditemukan di chunk |",
        f"| **Citation Accuracy** | {metrics.get('citation_accuracy', 0.0)}% | Nomor halaman sitasi tepat sesuai kunci jawaban |",
        f"| **Correct Rejection Rate** | {metrics.get('correct_rejection_rate', 0.0)}% | Pertanyaan di luar cakupan berhasil ditolak |",
        f"| **Rata-rata Latensi** | {metrics.get('avg_latency_sec', 0.0)} dtk | Waktu respons per pertanyaan |",
        "",
        "## 2. Rincian Hasil per Pertanyaan Uji",
        "",
        "| ID | Kategori | Jenis | Status | Halaman Kunci | Sitasi Model | Hasil Evaluasi |",
        "|---|---|---|---|---|---|---|",
    ]

    for r in results:
        status = r["status"]
        key_pages = str(r["halaman_kunci"]) if r["halaman_kunci"] else "-"
        model_pages = str(r["cited_pages"]) if r["cited_pages"] else "-"

        if r["jenis"] == "di_luar_cakupan":
            eval_tag = "Lolos (Ditolak)" if r["correct_rejection"] else "Gagal (Menjawab)"
        else:
            hit_str = "Hit: Ya" if r["hit_at_k"] else "Hit: Tidak"
            cite_str = "Sitasi: Tepat" if r["citation_correct"] else "Sitasi: Meleset"
            eval_tag = f"{hit_str}, {cite_str}"

        lines.append(
            f"| {r['id']} | {r['kategori']} | {r['jenis']} | {status} | {key_pages} | {model_pages} | {eval_tag} |"
        )

    lines.append("")
    return "\n".join(lines)


def get_mock_pipeline() -> Callable[[ChatRequest], ChatResponse]:
    """Pipeline simulasi untuk pengujian evaluasi saat database / API offline."""
    from backend.app.schemas.chat import ChatFilter, CitationSource

    logger.info("Menjalankan pipeline simulasi offline (mock).")

    def mock_query(req: ChatRequest) -> ChatResponse:
        q_lower = req.question.lower()
        if "akreditasi" in q_lower and "informatika" in q_lower:
            return ChatResponse(
                status="answered",
                answer="Program Studi Teknik Informatika (Program Sarjana) berstatus Terakreditasi dengan peringkat Unggul (hal. 11).",
                sources=[
                    CitationSource(
                        id="akreditasi-11-01",
                        halaman=11,
                        bagian="Akreditasi",
                        kutipan="Program Studi Teknik Informatika berstatus Terakreditasi dengan peringkat Unggul.",
                    )
                ],
                mode=ChatFilter(),
            )
        elif "akreditasi" in q_lower and "akuntansi" in q_lower:
            return ChatResponse(
                status="answered",
                answer="Program Studi Akuntansi (Sarjana) berstatus Terakreditasi dengan peringkat Unggul (hal. 11).",
                sources=[
                    CitationSource(
                        id="akreditasi-11-05",
                        halaman=11,
                        bagian="Akreditasi",
                        kutipan="Program Studi Akuntansi (Sarjana) berstatus Terakreditasi dengan peringkat Unggul.",
                    )
                ],
                mode=ChatFilter(),
            )
        elif "visi" in q_lower and "fasilkom" in q_lower:
            return ChatResponse(
                status="answered",
                answer="Visi Fakultas Ilmu Komputer adalah menjadi fakultas yang unggul pada tahun 2030 (hal. 65).",
                sources=[
                    CitationSource(
                        id="visi-65-01",
                        halaman=65,
                        bagian="Profil",
                        kutipan="Visi Fasilkom adalah unggul nasional dan internasional 2030.",
                    )
                ],
                mode=ChatFilter(),
            )
        elif "masa studi" in q_lower or ("batas" in q_lower and "studi" in q_lower):
            return ChatResponse(
                status="answered",
                answer="Masa studi program sarjana dirancang untuk 8 semester dan paling lama 14 semester (hal. 17).",
                sources=[
                    CitationSource(
                        id="aturan-17-01",
                        halaman=17,
                        bagian="Regulasi",
                        kutipan="Masa studi program sarjana dirancang untuk 8 semester dan paling lama 14 semester.",
                    )
                ],
                mode=ChatFilter(),
            )
        elif "kehadiran" in q_lower or "uas" in q_lower or "ujian" in q_lower:
            return ChatResponse(
                status="answered",
                answer="Mahasiswa wajib hadir minimal 75 persen dan sanksi pelanggaran adalah pembatalan nilai mata kuliah E (hal. 18).",
                sources=[
                    CitationSource(
                        id="aturan-18-01",
                        halaman=18,
                        bagian="Regulasi",
                        kutipan="Peserta ujian yang melanggar tata tertib ujian dikenakan sanksi berupa nilai E.",
                    )
                ],
                mode=ChatFilter(),
            )
        else:
            return ChatResponse(
                status="not_found",
                answer="Informasi tidak ditemukan di panduan.",
                sources=[],
                mode=ChatFilter(),
            )

    return mock_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluasi Kuantitatif RAG Panduan Akademik UMB.")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval/test_qa.jsonl",
        help="Path ke berkas JSONL dataset evaluasi",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/eval/evaluation_report.md",
        help="Path untuk menyimpan laporan hasil evaluasi (Markdown)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Pakai pipeline mock jika database/API belum aktif",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = PROJECT_ROOT / dataset_path

    items = load_dataset(dataset_path)

    # Tentukan fungsi query pipeline
    pipeline_fn: Callable[[ChatRequest], ChatResponse]
    if args.mock:
        pipeline_fn = get_mock_pipeline()
    else:
        try:
            from backend.app.services.pipeline import run_rag_pipeline

            pipeline_fn = run_rag_pipeline
        except Exception as exc:
            logger.warning(
                "Tidak dapat memuat pipeline live (%s). Menggunakan mock pipeline untuk evaluasi.",
                exc,
            )
            pipeline_fn = get_mock_pipeline()

    eval_results: list[dict[str, Any]] = []
    print(f"\nMemulai evaluasi terhadap {len(items)} pertanyaan...")
    for idx, item in enumerate(items, start=1):
        print(f"[{idx}/{len(items)}] Menguji: {item.get('pertanyaan', '')[:60]}...")
        result = evaluate_single_query(item, pipeline_fn)
        eval_results.append(result)

    metrics = compute_metrics(eval_results)
    report_text = render_markdown_report(metrics, eval_results)

    # Cetak laporan ke layar
    print("\n" + report_text)

    # Simpan laporan ke berkas
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = PROJECT_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Laporan evaluasi berhasil disimpan ke: {out_path}")


if __name__ == "__main__":
    main()
