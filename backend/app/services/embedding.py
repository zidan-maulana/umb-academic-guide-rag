"""Layanan pembuatan representasi vektor teks menggunakan Gemini API (docs/sdd.md)."""

import logging
import re
import time
from typing import List, Optional, Tuple
from google import genai
from google.genai import types

from backend.app.config import settings

logger = logging.getLogger(__name__)

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
    max_retries: int = 6,
    initial_delay: float = 15.0,
) -> List[List[float]]:
    """Hasilkan vektor dense untuk sekumpulan chunk dokumen dalam satu panggilan API batch dengan retry backoff.

    PENTING: pada gemini-embedding-2, list string yang dikirim langsung ke `contents`
    diperlakukan sebagai SATU Content dengan banyak part, sehingga hasilnya hanya
    satu embedding gabungan. Agar tiap teks mendapat embedding sendiri, setiap teks
    dibungkus dalam objek `types.Content` terpisah.
    """
    if not items:
        return []

    client = get_embedding_client()
    formatted_contents = [
        format_document_content(text=text, title=title)
        for text, title in items
    ]
    # Satu Content per teks -> satu embedding per teks (urutan sama dengan input)
    content_objects = [
        types.Content(parts=[types.Part(text=t)]) for t in formatted_contents
    ]
    model = settings.embedding_model or "gemini-embedding-2"
    dim = settings.embedding_dim or 768

    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.embed_content(
                model=model,
                contents=content_objects,
                config=types.EmbedContentConfig(output_dimensionality=dim),
            )
            embeddings = response.embeddings or []
            vectors = [list(emb.values) for emb in embeddings if emb.values]

            # Validasi kardinalitas: jangan pernah diam-diam kehilangan chunk
            if len(vectors) != len(formatted_contents):
                raise ValueError(
                    f"Embedding mengembalikan {len(vectors)} vektor "
                    f"untuk {len(formatted_contents)} input "
                    f"(model={model}). Periksa format contents."
                )
            return vectors
        except ValueError:
            # Error validasi/logika: retry tidak akan membantu, gagal cepat
            raise
        except Exception as exc:
            err_msg = str(exc)
            is_rate_limit = (
                "429" in err_msg
                or "RESOURCE_EXHAUSTED" in err_msg
                or "rate" in err_msg.lower()
            )
            if is_rate_limit and attempt < max_retries:
                # Cek jika Google memberikan rekomendasi retryDelay spesifik
                suggested_delay = delay
                retry_match = re.search(r"retryDelay':\s*'(\d+)s'", err_msg)
                if retry_match:
                    recom = float(retry_match.group(1))
                    if recom > 120.0:
                        raise RuntimeError(
                            f"Batas kuota harian (Daily Quota 1.000 request/hari) Google AI Studio untuk API key ini telah habis. "
                            f"Google meminta waktu tunggu {recom / 3600:.1f} jam. "
                            f"Silakan gunakan API key dari akun Google lain di file .env untuk melanjutkan sisa chunk."
                        )
                    suggested_delay = max(delay, recom + 2.0)

                logger.warning(
                    "Rate limit terdeteksi pada panggilan batch. Menunggu %.1f detik sebelum mencoba ulang (percobaan %d/%d)...",
                    suggested_delay,
                    attempt,
                    max_retries,
                )
                time.sleep(suggested_delay)
                delay *= 1.5
            elif attempt < max_retries:
                logger.warning(
                    "Error transient API: %s. Mencoba ulang dalam %.1f detik (percobaan %d/%d)...",
                    err_msg,
                    delay,
                    attempt,
                    max_retries,
                )
                time.sleep(delay)
                delay *= 1.5
            else:
                logger.error(
                    "Gagal melakukan batch embedding setelah %d percobaan: %s",
                    max_retries,
                    err_msg,
                )
                raise