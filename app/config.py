from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "local-ai-server"
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_llm_model: str = Field(default="llama3.2", alias="OLLAMA_LLM_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    database_url: str = Field(default="sqlite:///data/local_ai.sqlite3", alias="DATABASE_URL")
    chroma_path: str = Field(default="data/chroma", alias="CHROMA_PATH")
    upload_dir: str = Field(default="data/uploads", alias="UPLOAD_DIR")
    chunk_size: int = Field(default=1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    embedding_batch_size: int = Field(default=8, ge=1, le=128, alias="EMBEDDING_BATCH_SIZE")
    embedding_max_retries: int = Field(default=2, ge=0, le=10, alias="EMBEDDING_MAX_RETRIES")
    local_api_key: str | None = Field(default=None, alias="LOCAL_API_KEY")
    local_rate_limit_per_minute: int = Field(default=120, ge=0, alias="LOCAL_RATE_LIMIT_PER_MINUTE")
    agent_execution_enabled: bool = Field(default=False, alias="AGENT_EXECUTION_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def ensure_data_dirs(self) -> None:
        Path("data").mkdir(parents=True, exist_ok=True)
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_path).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_data_dirs()
    return settings
