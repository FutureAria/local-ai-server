from fastapi.testclient import TestClient
import pytest

from app.api.dependencies import get_search_service, reset_rate_limiter
from app.config import get_settings
from app.main import app


class FakeSearchService:
    async def search(self, query: str, top_k: int = 5):
        return []


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("post", "/ask", {"json": {"question": "hello"}}),
        ("post", "/ask-with-docs", {"json": {"question": "hello"}}),
        ("post", "/search", {"json": {"query": "hello"}}),
        (
            "post",
            "/documents/upload",
            {"files": {"file": ("note.md", b"# Note", "text/markdown")}},
        ),
        ("post", "/documents/index-folder-preview", {"json": {"folder_path": "/tmp/notes", "recursive": True}}),
        ("post", "/documents/index-folder", {"json": {"folder_path": "/tmp/notes", "recursive": True}}),
        ("delete", "/documents/1", {}),
        ("post", "/feedback", {"json": {"request_id": "1", "rating": "good"}}),
        ("post", "/agent/plan", {"json": {"instruction": "웹 열어줘"}}),
        ("get", "/agent/runs", {}),
        ("get", "/agent/runs/1", {}),
        ("get", "/agent/runs/1/results", {}),
        ("get", "/agent/runs/1/actions", {}),
        ("post", "/agent/runs/1/dry-run", {}),
        ("post", "/agent/runs/1/approve", {}),
        ("post", "/agent/runs/1/reject", {}),
        ("post", "/agent/runs/1/execute", {}),
        ("get", "/project/shell-policy", {}),
        ("post", "/project/shell-dry-run", {"json": {"command": "pwd"}}),
        ("get", "/assistant/capabilities", {}),
        ("get", "/assistant/status", {}),
        ("post", "/assistant/sessions", {"json": {"title": "Demo"}}),
        ("get", "/assistant/sessions", {}),
        ("get", "/assistant/sessions/session-1", {}),
        ("post", "/assistant/message", {"json": {"message": "hello"}}),
        ("post", "/assistant/project-root/validate", {"json": {"project_root": "/tmp/project"}}),
    ],
)
def test_local_api_key_protects_all_mutating_endpoints(monkeypatch, method: str, path: str, kwargs: dict) -> None:
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    client = TestClient(app)

    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 401
    assert response.json()["detail"] == "LOCAL_API_KEY가 설정되어 있어 X-API-Key 또는 Authorization: Bearer 헤더가 필요합니다."

    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)


def test_local_rate_limit_blocks_protected_endpoint_after_limit(monkeypatch) -> None:
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    monkeypatch.setenv("LOCAL_RATE_LIMIT_PER_MINUTE", "2")
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    client = TestClient(app)

    headers = {"X-API-Key": "secret"}
    assert client.post("/search", json={"query": "first"}, headers=headers).status_code == 200
    assert client.post("/search", json={"query": "second"}, headers=headers).status_code == 200
    response = client.post("/search", json={"query": "third"}, headers=headers)

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_RATE_LIMIT_PER_MINUTE", raising=False)

    assert response.status_code == 429
    assert response.json()["detail"] == "요청이 너무 많습니다. 잠시 후 다시 시도하세요."
    assert int(response.headers["retry-after"]) > 0


def test_local_api_key_accepts_authorization_bearer(monkeypatch) -> None:
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    client = TestClient(app)

    response = client.post("/search", json={"query": "hello"}, headers={"Authorization": "Bearer secret"})

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)

    assert response.status_code == 200
