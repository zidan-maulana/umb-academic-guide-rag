"""Orkestrasi pipeline RAG menghubungkan retrieval, konteks, dan pembentukan respons (docs/sdd.md)."""

import logging
from typing import List

from backend.app.schemas.chat import (
    ChatFilter,
    ChatRequest,
    ChatResponse,
    CitationSource,
    RetrievedChunk,
)
from backend.app.services.retrieval import retrieve_chunks

logger = logging.getLogger("umb_rag.pipeline")


def format_citations(chunks: List[RetrievedChunk]) -> List[CitationSource]:
    """Ubah chunk yang relevan menjadi daftar sitasi sumber resmi untuk antarmuka pengguna."""
    citations: List[CitationSource] = []
    for c in chunks:
        quote = c.konten if len(c.konten) <= 200 else c.konten[:197] + "..."
        citations.append(
            CitationSource(
                id=c.id,
                halaman=c.halaman,
                bagian=c.bagian,
                kutipan=quote,
                jenis_konten=c.jenis_konten,
                topik=c.topik,
                fakultas=c.fakultas,
                program_studi=c.program_studi,
                similarity=c.similarity,
            )
        )
    return citations


def run_rag_pipeline(request: ChatRequest) -> ChatResponse:
    """Jalankan alur temu balik informasi (retrieval) dan susun respons akhir."""
    active_mode = request.filters or ChatFilter()

    chunks = retrieve_chunks(
        query=request.question,
        filters=request.filters,
    )

    logger.info(
        "Retrieval selesai: pertanyaan='%s', chunks=%d, skor=%s",
        request.question[:80],
        len(chunks),
        [f"{c.id}:{c.similarity}" for c in chunks],
    )

    if not chunks:
        return ChatResponse(
            status="not_found",
            answer="Informasi tidak ditemukan di panduan.",
            sources=[],
            mode=active_mode,
        )

    sources = format_citations(chunks)

    try:
        from backend.app.services.prompt import (
            ChunkData,
            RAGPromptInput,
            build_rag_prompt,
        )
        from backend.app.services.generate import generate_answer

        prompt_chunks = [
            ChunkData(
                id=c.id,
                konten=c.konten,
                halaman=c.halaman,
                bagian=c.bagian,
                jenis_konten=c.jenis_konten,
                fakultas=c.fakultas,
                program_studi=c.program_studi,
            )
            for c in chunks
        ]
        prompt = build_rag_prompt(
            RAGPromptInput(context_chunks=prompt_chunks, user_query=request.question)
        )
        gen_result = generate_answer(prompt=prompt, chunks=chunks)

        if (
            gen_result.get("is_fallback")
            or gen_result.get("answer") == "Informasi tidak ditemukan di panduan."
        ):
            return ChatResponse(
                status="not_found",
                answer="Informasi tidak ditemukan di panduan.",
                sources=[],
                mode=active_mode,
            )

        answer = gen_result.get("answer") or ""
    except Exception as exc:
        logger.warning("Gagal memanggil generate_answer, fallback ke top chunk: %s", exc)
        top_chunk = chunks[0]
        answer = (
            f"Berdasarkan Panduan Akademik UMB (Halaman {top_chunk.halaman}):\n"
            f"{top_chunk.konten}"
        )

    return ChatResponse(
        status="answered",
        answer=answer,
        sources=sources,
        mode=active_mode,
    )
