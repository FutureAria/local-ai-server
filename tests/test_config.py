from app.config import Settings


def test_config_defaults() -> None:
    settings = Settings()
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_llm_model == "llama3.2"
    assert settings.ollama_embed_model == "nomic-embed-text"
    assert settings.database_url == "sqlite:///data/local_ai.sqlite3"
    assert settings.embedding_batch_size == 8
    assert settings.embedding_max_retries == 2
    assert settings.local_rate_limit_per_minute == 120
    assert settings.agent_execution_enabled is False
    assert settings.agent_allowed_roots == "."
    assert settings.agent_web_fetch_enabled is False
    assert settings.agent_web_fetch_max_bytes == 100_000
