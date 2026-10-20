"""Layanan pembuatan representasi vektor teks menggunakan Gemini API (docs/sdd.md)."""

from typing import List, Optional, Tuple
from google import genai
from google.genai import types

from backend.app.config import settings

# Client singleton untuk menghemat alokasi memori
_client: Optional[genai.Client] = None


def get_embedding_client() -> genai.Client:
    """Inisialisasi atau kembalikan client Gemini API singleton."""
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY belum disetel pada environment (.env)")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def format_query_content(query: str) -> str:
    """Format teks kueri pencarian sesuai konvensi prefiks gemini-embedding-2."""
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("Teks kueri tidak boleh kosong")
    return f"task: question answering | query: {clean_query}"


def format_document_content(text: str, title: Optional[str] = None) -> str:
    """Format teks chunk dokumen sesuai konvensi prefiks gemini-embedding-2."""
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Teks dokumen tidak boleh kosong")
    clean_title = (title or "none").strip() or "none"
    return f"title: {clean_title} | text: {clean_text}"


def embed_query(query: str) -> List[float]:
    """Hasilkan vektor dense untuk pertanyaan pengguna (kueri pencarian)."""
    client = get_embedding_client()
    formatted = format_query_content(query)
    model = settings.embedding_model or "gemini-embedding-2"
    dim = settings.embedding_dim or 768

    response = client.models.embed_content(
        model=model,
        contents=formatted,
        config=types.EmbedContentConfig(output_dimensionality=dim),
    )
    return list(response.embeddings[0].values)


def embed_document(text: str, title: Optional[str] = None) -> List[float]:
    """Hasilkan vektor dense untuk satu potongan teks panduan (chunk)."""
    client = get_embedding_client()
    formatted = format_document_content(text=text, title=title)
    model = settings.embedding_model or "gemini-embedding-2"
    dim = settings.embedding_dim or 768

    response = client.models.embed_content(
        model=model,
        contents=formatted,
        config=types.EmbedContentConfig(output_dimensionality=dim),
    )
    return list(response.embeddings[0].values)


def embed_documents_batch(
    items: List[Tuple[str, Optional[str]]],
) -> List[List[float]]:
    """Hasilkan vektor untuk sekumpulan chunk dokumen (dipakai saat ingest)."""
    results: List[List[float]] = []
    for text, title in items:
        vector = embed_document(text=text, title=title)
        results.append(vector)
    return results
