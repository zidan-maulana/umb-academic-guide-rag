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
        from backend.app.services.generate import generate_answer
        answer = generate_answer(question=request.question, chunks=chunks)
    except (ImportError, AttributeError, NotImplementedError):
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
