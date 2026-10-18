"""Application configuration module.

Centralized configuration using Pydantic Settings.
Reads environment variables from .env or system environment.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema.

    Model and dimension settings are intentionally left open (Terbuka)
    until decided by the repository owner per AGENTS.md Section 2.
    """

    # Gemini API Credentials
    gemini_api_key: str = ""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/umb_academic_rag"

    # Embedding & LLM (Status: Terbuka)
    embedding_model: Optional[str] = None
    embedding_dim: Optional[int] = None
    llm_model: Optional[str] = None

    # RAG Retrieval Hyperparameters
    top_k: int = 5
    similarity_threshold: float = 0.0

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list of strings."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
