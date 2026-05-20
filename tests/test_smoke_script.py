import scripts.smoke_test_api as smoke


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeClient:
    def __init__(self, calls: list[dict]) -> None:
        self.calls = calls

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def get(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "GET", "url": url, **kwargs})
        if url.endswith("/health"):
            return FakeResponse(200, {"status": "ok"})
        if url.endswith("/assistant/startup"):
            return FakeResponse(200, {"protected": True, "ui": {"ready": True}})
        if url.endswith("/project/api-inventory"):
            return FakeResponse(200, {"endpoints_count": 3, "protected_endpoints_count": 2})
        if url.endswith("/assistant/sessions"):
            return FakeResponse(200, {"sessions": [{"session_id": "session-1"}]})
        if url.endswith("/assistant/sessions/session-1/messages"):
            return FakeResponse(200, {"total_messages": 2, "messages": []})
        return FakeResponse(200, {"documents_count": 1, "chunks_count": 1})

    def post(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "POST", "url": url, **kwargs})
        if url.endswith("/documents/upload"):
            return FakeResponse(200, {"document_id": 1, "filename": "smoke.md", "chunks_created": 1})
        if url.endswith("/search"):
            return FakeResponse(200, {"query": "JWT", "results": [{"chunk_id": 1}]})
        if url.endswith("/ask-with-docs"):
            return FakeResponse(200, {"request_id": "7", "sources": [{"chunk_id": 1}]})
        if url.endswith("/feedback"):
            return FakeResponse(200, {"feedback_id": 9})
        if url.endswith("/assistant/bootstrap"):
            return FakeResponse(200, {"ui": {"ready": True}, "project_root": {"safe_for_read_only_agent": True}})
        if url.endswith("/assistant/action-preview"):
            return FakeResponse(200, {"intent": "status", "would_execute": False})
        if url.endswith("/assistant/message"):
            return FakeResponse(200, {"session_id": "session-1", "type": "status", "answer": "현재 차수는 15차입니다."})
        return FakeResponse(200, {})


def test_smoke_script_calls_expected_api_flow(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    summary = smoke.run_smoke_test("http://server.test/")

    assert summary["ok"] is True
    assert [step["step"] for step in summary["steps"]] == [
        "health",
        "upload",
        "search",
        "ask-with-docs",
        "feedback",
        "stats",
    ]
    assert calls[1]["headers"] == {"X-API-Key": "secret"}
    assert calls[3]["json"]["question"] == "내 문서 기준으로 access token은 어디로 전달해?"


def test_assistant_bridge_smoke_calls_ui_contract_flow(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    summary = smoke.run_assistant_bridge_smoke_test("http://server.test/", project_root="/tmp/project")

    assert summary["ok"] is True
    assert [step["step"] for step in summary["steps"]] == [
        "assistant-startup",
        "api-inventory",
        "assistant-bootstrap",
        "assistant-action-preview",
        "assistant-message",
        "assistant-sessions",
        "assistant-messages",
    ]
    assert calls == [
        {"method": "GET", "url": "http://server.test/assistant/startup", "headers": {"X-API-Key": "secret"}},
        {"method": "GET", "url": "http://server.test/project/api-inventory"},
        {
            "method": "POST",
            "url": "http://server.test/assistant/bootstrap",
            "json": {"project_root": "/tmp/project", "include_sessions": True, "sessions_limit": 5},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://server.test/assistant/action-preview",
            "json": {"message": "현재 상태 알려줘", "project_root": "/tmp/project", "mode": "auto"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://server.test/assistant/message",
            "json": {"message": "현재 상태 알려줘", "project_root": "/tmp/project", "mode": "status"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://server.test/assistant/sessions",
            "params": {"limit": 5, "offset": 0},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://server.test/assistant/sessions/session-1/messages",
            "params": {"limit": 10, "offset": 0},
            "headers": {"X-API-Key": "secret"},
        },
    ]
    assert summary["steps"][4]["response_type"] == "status"


def test_assistant_bridge_preflight_detects_wrong_server(monkeypatch) -> None:
    calls: list[dict] = []

    class WrongServerClient(FakeClient):
        def get(self, url: str, **kwargs) -> FakeResponse:
            self.calls.append({"method": "GET", "url": url, **kwargs})
            if url.endswith("/health"):
                return FakeResponse(200, {"status": "ok", "agent": "other"})
            if url.endswith("/assistant/startup"):
                return FakeResponse(404, {"detail": "Not Found"})
            if url.endswith("/project/api-inventory"):
                return FakeResponse(404, {"detail": "Not Found"})
            return FakeResponse(404, {"detail": "Not Found"})

    def client_factory(timeout: float) -> WrongServerClient:
        return WrongServerClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)

    summary = smoke.run_assistant_bridge_preflight("http://server.test/")

    assert summary["ok"] is False
    assert [step["step"] for step in summary["steps"]] == [
        "health",
        "assistant-startup",
        "api-inventory",
    ]
    assert summary["steps"][1]["status"] == 404
    assert "Another server may be using this base URL" in summary["steps"][1]["hint"]
    assert "different --base-url" in summary["hint"]


def test_assistant_bridge_preflight_passes_for_expected_server(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)

    summary = smoke.run_assistant_bridge_preflight("http://server.test/")

    assert summary["ok"] is True
    assert [step["status"] for step in summary["steps"]] == [200, 200, 200]
