from fastapi.testclient import TestClient
import pytest

from app.api.dependencies import get_search_service, reset_rate_limiter
from app.config import get_settings
from app.main import app, create_app
from app.services.project_status_service import build_api_inventory


class FakeSearchService:
    async def search(self, query: str, top_k: int = 5):
        return []


PROTECTED_ENDPOINT_CASES = [
    ("post", "/ask", {"json": {"question": "hello"}}),
    ("post", "/ask-with-docs", {"json": {"question": "hello"}}),
    ("post", "/search", {"json": {"query": "hello"}}),
    (
        "post",
        "/documents/upload",
        {"files": {"file": ("note.md", b"# Note", "text/markdown")}},
    ),
    ("post", "/documents/index-folder-preview", {"json": {"folder_path": "/tmp/notes", "recursive": True}}),
    ("post", "/documents/index-folder-job-preview", {"json": {"folder_path": "/tmp/notes", "recursive": True}}),
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
    ("post", "/assistant/action-preview", {"json": {"message": "hello"}}),
    ("post", "/assistant/action-loop-preflight", {"json": {"goal": "personal API dispatch", "proposed_steps": []}}),
    ("post", "/assistant/action-loop-noop-dispatch", {"json": {"goal": "personal API dispatch", "proposed_steps": []}}),
    ("post", "/assistant/action-loop-read-only-dispatch-preview", {"json": {"goal": "read-only dispatch", "proposed_steps": []}}),
    ("post", "/assistant/action-loop-read-only-dispatch", {"json": {"goal": "read-only dispatch", "proposed_steps": []}}),
    ("post", "/assistant/action-loop-shell-dispatch", {"json": {"goal": "shell dispatch", "proposed_steps": []}}),
    ("post", "/assistant/action-loop-patch-dispatch", {"json": {"goal": "patch dispatch", "proposed_steps": []}}),
    ("post", "/assistant/full-automation-preflight", {"json": {"goal": "full automation", "proposed_steps": []}}),
    ("post", "/assistant/full-automation-dispatch", {"json": {"goal": "full automation", "proposed_steps": []}}),
    ("post", "/assistant/automation-plan", {"json": {"goal": "personal API automation"}}),
    ("get", "/assistant/workflow-presets", {}),
    ("get", "/assistant/workflow-presets/{preset_id}", {}),
    ("post", "/assistant/workflow-presets/{preset_id}/preview", {"json": {"params": {"project_root": "/tmp/project"}}}),
    ("post", "/assistant/task-queue/preview", {"json": {"task_type": "noop", "params": {"note": "plan"}}}),
    ("get", "/assistant/task-queue", {}),
    ("post", "/assistant/task-queue/drain", {"json": {"limit": 1}}),
    ("get", "/assistant/task-queue/task-1", {}),
    ("post", "/assistant/task-queue/task-1/cancel-preview", {}),
    ("post", "/assistant/failure-recovery-preview", {"json": {"tool": "patch", "failure_reason": "hash_mismatch"}}),
    (
        "post",
        "/assistant/rollback-approval-preview",
        {"json": {"path": "/tmp/project/a.md", "restored_content": "old\n", "current_sha256": "a" * 64, "original_sha256": "b" * 64}},
    ),
    (
        "post",
        "/assistant/rollback-execute",
        {"json": {"path": "/tmp/project/a.md", "restored_content": "old\n", "current_sha256": "a" * 64, "original_sha256": "b" * 64}},
    ),
    ("post", "/assistant/read-only-scan", {"json": {"project_root": "/tmp/project"}}),
    ("post", "/assistant/file-preview", {"json": {"path": "/tmp/project/README.md"}}),
    ("post", "/assistant/url-preview", {"json": {"url": "https://example.com"}}),
    (
        "post",
        "/assistant/read-only-adapter/execute",
        {"json": {"adapter_type": "file_preview", "path": "/tmp/project/README.md", "result_wrapper": {"untrusted": True}}},
    ),
    (
        "post",
        "/assistant/web-search-provider-preview",
        {"json": {"query": "latest FastAPI release notes", "result_wrapper": {"untrusted": True}}},
    ),
    (
        "post",
        "/assistant/web-search-provider/search",
        {"json": {"query": "latest FastAPI release notes", "result_wrapper": {"untrusted": True}}},
    ),
    ("post", "/assistant/app-os-interaction-preview", {"json": {"action": "observe-plan", "app_name": "Preview"}}),
    ("post", "/assistant/workspace-brief", {"json": {"project_root": "/tmp/project"}}),
    ("post", "/assistant/shell-preview", {"json": {"command": "git status", "cwd": "/tmp/project"}}),
    ("post", "/assistant/shell-approval-preview", {"json": {"command": "git status", "cwd": "/tmp/project"}}),
    ("post", "/assistant/shell-run", {"json": {"command": "git status", "cwd": "/tmp/project"}}),
    ("get", "/assistant/approval-console/pending", {}),
    ("get", "/assistant/approval-console/approval-1", {}),
    ("post", "/assistant/approval-console/cleanup-expired", {}),
    (
        "post",
        "/assistant/durable-state-preview/preview",
        {"json": {"goal": "preview durable state", "proposed_steps": []}},
    ),
    ("post", "/assistant/patch-preview", {"json": {"path": "/tmp/project/note.md", "proposed_content": "hello"}}),
    ("post", "/assistant/patch-approval-preview", {"json": {"path": "/tmp/project/note.md", "proposed_content": "hello"}}),
    ("post", "/assistant/patch-apply", {"json": {"path": "/tmp/project/note.md", "proposed_content": "hello"}}),
    ("post", "/assistant/browser-preview", {"json": {"action": "observe", "target_url": "https://example.com"}}),
    ("post", "/assistant/browser-approval-preview", {"json": {"action": "screenshot", "target_url": "https://example.com"}}),
    ("post", "/assistant/browser-interact", {"json": {"action": "observe", "target_url": "https://example.com"}}),
    ("post", "/assistant/browser-observe", {"json": {"action": "observe", "target_url": "http://127.0.0.1:8000"}}),
    (
        "post",
        "/assistant/browser-limited-interact",
        {"json": {"action": "click", "target_url": "http://127.0.0.1:8000", "selector": "#ok"}},
    ),
    ("get", "/assistant/ping", {}),
    ("get", "/assistant/config", {}),
    ("get", "/assistant/status", {}),
    ("get", "/assistant/dashboard", {}),
    ("get", "/assistant/startup", {}),
    ("get", "/assistant/ui-contract", {}),
    ("post", "/assistant/bootstrap", {"json": {}}),
    ("post", "/assistant/sessions", {"json": {"title": "Demo"}}),
    ("get", "/assistant/sessions", {}),
    ("get", "/assistant/sessions/session-1", {}),
    ("get", "/assistant/sessions/session-1/messages", {}),
    ("post", "/assistant/message", {"json": {"message": "hello"}}),
    ("post", "/assistant/project-root/validate", {"json": {"project_root": "/tmp/project"}}),
]


def _case_path_to_template(path: str) -> str:
    if path == "/documents/1":
        return "/documents/{document_id}"
    if path.startswith("/agent/runs/1"):
        return path.replace("/agent/runs/1", "/agent/runs/{run_id}", 1)
    if path.startswith("/assistant/sessions/session-1"):
        return path.replace("/assistant/sessions/session-1", "/assistant/sessions/{session_id}", 1)
    if path.startswith("/assistant/task-queue/task-1"):
        return path.replace("/assistant/task-queue/task-1", "/assistant/task-queue/{task_id}", 1)
    if path == "/assistant/approval-console/approval-1":
        return "/assistant/approval-console/{approval_id}"
    return path


@pytest.mark.parametrize(("method", "path", "kwargs"), PROTECTED_ENDPOINT_CASES)
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


def test_protected_endpoint_cases_match_api_inventory() -> None:
    inventory = build_api_inventory(app.routes)
    inventory_protected = {
        (method.lower(), endpoint["path"])
        for endpoint in inventory["endpoints"]
        if endpoint["requires_api_key"] is True
        for method in endpoint["methods"]
    }
    tested_protected = {
        (method, _case_path_to_template(path))
        for method, path, _kwargs in PROTECTED_ENDPOINT_CASES
    }

    assert tested_protected == inventory_protected
    assert len(tested_protected) == inventory["protected_endpoints_count"]


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


def test_api_inventory_stays_public_but_marks_protected_endpoints(monkeypatch) -> None:
    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    client = TestClient(app)

    response = client.get("/project/api-inventory")

    get_settings.cache_clear()
    reset_rate_limiter()
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "read-only"
    assert any(
        endpoint["path"] == "/project/shell-policy" and endpoint["requires_api_key"] is True
        for endpoint in body["endpoints"]
    )
    assert any(
        endpoint["path"] == "/project/api-inventory" and endpoint["requires_api_key"] is False
        for endpoint in body["endpoints"]
    )


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


def test_create_app_warns_when_local_api_key_missing(monkeypatch, capsys, tmp_path) -> None:
    get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_API_KEY_WARN", raising=False)

    create_app()
    captured = capsys.readouterr()

    get_settings.cache_clear()
    assert "LOCAL_API_KEY is not set" in captured.err


def test_create_app_can_silence_missing_local_api_key_warning(monkeypatch, capsys, tmp_path) -> None:
    get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)
    monkeypatch.setenv("LOCAL_API_KEY_WARN", "false")

    create_app()
    captured = capsys.readouterr()

    get_settings.cache_clear()
    monkeypatch.delenv("LOCAL_API_KEY_WARN", raising=False)
    assert "LOCAL_API_KEY is not set" not in captured.err


def test_cors_allow_credentials_defaults_false(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.delenv("LOCAL_CORS_ALLOW_CREDENTIALS", raising=False)

    test_app = create_app()

    get_settings.cache_clear()
    cors_middleware = next(item for item in test_app.user_middleware if item.cls.__name__ == "CORSMiddleware")
    assert cors_middleware.kwargs["allow_credentials"] is False


def test_cors_allow_credentials_can_be_enabled_by_env(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("LOCAL_CORS_ALLOW_CREDENTIALS", "true")

    test_app = create_app()

    get_settings.cache_clear()
    monkeypatch.delenv("LOCAL_CORS_ALLOW_CREDENTIALS", raising=False)
    cors_middleware = next(item for item in test_app.user_middleware if item.cls.__name__ == "CORSMiddleware")
    assert cors_middleware.kwargs["allow_credentials"] is True
