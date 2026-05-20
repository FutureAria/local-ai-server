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


def test_local_ui_cors_preflight() -> None:
    client = TestClient(app)
    response = client.options(
        "/assistant/message",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
