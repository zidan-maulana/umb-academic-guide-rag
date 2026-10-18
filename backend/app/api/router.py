"""API routing module.

Central router coordinating API endpoints.
Chat endpoints and additional service endpoints (e.g., health check)
will be registered here once decisions and api-contract.md are finalized.
"""

from fastapi import APIRouter

api_router = APIRouter()

# Placeholder for future routers (e.g., api_router.include_router(chat_router, prefix="/chat"))
