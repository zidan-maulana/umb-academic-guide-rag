"""Modul routing API terpusat untuk melayani request HTTP (docs/api-contract.md)."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.pipeline import run_rag_pipeline

logger = logging.getLogger("umb_rag.api")

api_router = APIRouter()


@api_router.post("/v1/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(request: ChatRequest) -> ChatResponse | JSONResponse:
    """Endpoint tanya jawab berbasis RAG untuk Panduan Akademik UMB."""
    logger.info("Pertanyaan masuk: %s", request.question[:80])

    try:
        response = run_rag_pipeline(request)
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Database/network error: %s", exc)
        return JSONResponse(
            status_code=504,
            content={"error": {"code": "timeout", "message": "Proses melebihi batas waktu, coba lagi."}},
        )
    except Exception as exc:
        error_type = type(exc).__name__
        if "google" in type(exc).__module__.lower() if hasattr(type(exc), "__module__") else False:
            logger.error("Gemini API error: %s — %s", error_type, exc)
            return JSONResponse(
                status_code=502,
                content={"error": {"code": "llm_error", "message": "Layanan AI sedang tidak tersedia, coba lagi."}},
            )
        logger.error("Unexpected error: %s — %s", error_type, exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Terjadi kesalahan internal."}},
        )

    logger.info("Respons: status=%s, jumlah_sumber=%d", response.status, len(response.sources))
    return response


@api_router.get("/v1/health", tags=["System"])
def health_check() -> dict:
    """Cek kesehatan layanan untuk pemantauan sistem."""
    return {"status": "healthy"}