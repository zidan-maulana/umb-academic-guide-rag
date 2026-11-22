"""Pemanggilan Gemini LLM dan ekstraksi sitasi halaman dari chunk retrieval."""

from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger("umb_rag.generate")

FALLBACK_MESSAGE = "Informasi tidak ditemukan di panduan."
DEFAULT_MODEL = "gemini-2.5-flash"

_client: genai.Client | None = None


class GenerationError(Exception):
    """Gagal memanggil Gemini atau memproses jawaban model."""


def _get_client() -> genai.Client:
    """Kembalikan klien Gemini tunggal. Raise jika API key belum di-set."""
    global _client
    if _client is not None:
        return _client

    load_dotenv()
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum di-set")

    _client = genai.Client(api_key=api_key)
    return _client


def _halaman_from_chunk(chunk: Any) -> int | None:
    """Ambil nomor halaman dari dict, objek, atau metadata bersarang."""
    raw: Any = None
    if isinstance(chunk, dict):
        raw = chunk.get("halaman")
        if raw is None:
            metadata = chunk.get("metadata")
            if isinstance(metadata, dict):
                raw = metadata.get("halaman")
    else:
        raw = getattr(chunk, "halaman", None)
        if raw is None:
            metadata = getattr(chunk, "metadata", None)
            if isinstance(metadata, dict):
                raw = metadata.get("halaman")
            elif metadata is not None:
                raw = getattr(metadata, "halaman", None)

    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def extract_pages(chunks: list[Any]) -> list[int]:
    """Kumpulkan nomor halaman unik dari chunk, lalu urutkan naik."""
    pages: set[int] = set()
    for chunk in chunks:
        halaman = _halaman_from_chunk(chunk)
        if halaman is None:
            continue
        pages.add(halaman)
    return sorted(pages)


def generate_answer(prompt: str, chunks: list[Any]) -> dict[str, Any]:
    """Kirim prompt ke Gemini dan kembalikan jawaban beserta sitasi halaman."""
    model_name = (os.getenv("GEMINI_MODEL") or DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2),
        )
        raw_text = getattr(response, "text", None)
    except Exception as exc:
        logger.exception("Gagal memanggil Gemini (%s)", type(exc).__name__)
        raise GenerationError("Gagal menghasilkan jawaban dari layanan AI") from exc

    if raw_text is None or not str(raw_text).strip():
        logger.warning("Jawaban Gemini kosong; memakai pesan fallback")
        return {
            "answer": FALLBACK_MESSAGE,
            "pages": [],
            "is_fallback": True,
        }

    answer = str(raw_text).strip()
    is_fallback = answer == FALLBACK_MESSAGE
    pages = [] if is_fallback else extract_pages(chunks)
    return {
        "answer": answer,
        "pages": pages,
        "is_fallback": is_fallback,
    }
