from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuTrust API"
    environment: str = "development"
    api_prefix: str = ""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "docutrust"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    upload_dir: str = "storage/uploads"
    chroma_dir: str = "storage/chroma"
    max_upload_size_mb: int = 25

    retrieval_top_k: int = 6
    relevance_threshold: float = 0.62
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    tavily_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
