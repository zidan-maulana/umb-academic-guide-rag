"""Main FastAPI application entrypoint.

Initializes FastAPI app, configures CORS middleware with explicit origins,
and mounts API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.config import settings

app = FastAPI(
    title="UMB Academic Guide RAG API",
    description="Backend API for UMB Academic Guide 2025/2026 Question Answering Chatbot",
    version="0.1.0",
)

# Configure CORS with explicit origins per AGENTS.md conventions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Info"])
def root_info() -> dict:
    """Service status information endpoint for verification."""
    return {
        "service": "UMB Academic Guide RAG API",
        "status": "ready",
        "version": "0.1.0",
    }
