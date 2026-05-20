from fastapi.testclient import TestClient

from app.api.health import _model_ready
from app.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "local-ai-server",
        "ollama_base_url": "http://localhost:11434",
        "llm_model": "llama3.2",
        "embedding_model": "nomic-embed-text",
    }


def test_model_ready_accepts_latest_tag() -> None:
    assert _model_ready("llama3.2", ["llama3.2:latest"]) is True
    assert _model_ready("nomic-embed-text", ["llama3.2:latest"]) is False
