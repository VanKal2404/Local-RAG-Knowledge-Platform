from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Local RAG Knowledge Platform"
    app_version: str = "1.0.0"
    environment: str = "local"
    upload_dir: str = "app/storage/documents"
    chroma_dir: str = "app/storage/chroma"
    collection_name: str = "documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    chunk_size: int = 900
    chunk_overlap: int = 180
    retrieval_top_k: int = 5
    max_upload_mb: int = 25
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
