"""Main FastAPI application entrypoint (docs/sdd.md)."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.config import settings
from backend.app.db import close_db_pool, init_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Kelola daur hidup aplikasi: buka pool koneksi saat mulai, tutup saat selesai."""
    init_db_pool()
    yield
    close_db_pool()


app = FastAPI(
    title="UMB Academic Guide RAG API",
    description="Backend API for UMB Academic Guide 2025/2026 Question Answering Chatbot",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Info"])
def root_info() -> dict:
    """Service status information endpoint for verification."""
    return {
        "service": "UMB Academic Guide RAG API",
        "status": "ready",
        "version": "0.1.0",
    }
