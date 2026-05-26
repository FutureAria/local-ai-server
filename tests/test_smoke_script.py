from pathlib import Path

import scripts.smoke_test_api as smoke

SMOKE_DOCS = ["README.md", "docs/OPERATIONS.md"]


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
            filename = kwargs["files"]["file"][0]
            document_id = 1 if filename.endswith(".md") else 2
            return FakeResponse(200, {"document_id": document_id, "filename": filename, "chunks_created": 1})
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
    assert [step["step"] for step in summary["steps"]] == smoke.DOCUMENT_RAG_SMOKE_FLOW
    assert summary["sample_documents"] == ["smoke-backend-notes.md", "smoke-architecture-notes.txt"]
    assert summary["steps"][1]["documents_count"] == 2
    assert [item["filename"] for item in summary["steps"][1]["documents"]] == [
        "smoke-backend-notes.md",
        "smoke-architecture-notes.txt",
    ]
    assert calls[1]["headers"] == {"X-API-Key": "secret"}
    assert calls[1]["files"]["file"][0] == "smoke-backend-notes.md"
    assert calls[1]["files"]["file"][2] == "text/markdown"
    assert calls[2]["files"]["file"][0] == "smoke-architecture-notes.txt"
    assert calls[2]["files"]["file"][2] == "text/plain"
    assert calls[4]["json"]["question"] == "내 문서 기준으로 access token은 어디로 전달해?"


def test_smoke_script_accepts_approved_user_document(monkeypatch, tmp_path) -> None:
    calls: list[dict] = []
    approved_doc = tmp_path / "approved-notes.md"
    approved_doc.write_text("# Approved notes\n\naccess token은 header로 전달한다.", encoding="utf-8")

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)

    summary = smoke.run_smoke_test("http://server.test/", document_paths=[str(approved_doc)])
    safe = smoke.build_sanitized_smoke_summary(summary)

    assert summary["document_source"] == "user-provided"
    assert summary["user_documents_count"] == 1
    assert calls[1]["files"]["file"][0] == "approved-notes.md"
    assert calls[1]["files"]["file"][2] == "text/markdown"
    assert safe["document_source"] == "user-provided"
    assert safe["user_documents_count"] == 1
    assert safe["steps"][1]["documents"] == [{"chunks_created": 1}]
    assert "approved-notes.md" not in str(safe)


def test_smoke_script_accepts_approved_pdf_user_document(monkeypatch, tmp_path) -> None:
    calls: list[dict] = []
    approved_doc = tmp_path / "approved-scan.pdf"
    approved_doc.write_bytes(b"%PDF approved")

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)

    summary = smoke.run_smoke_test("http://server.test/", document_paths=[str(approved_doc)])
    safe = smoke.build_sanitized_smoke_summary(summary)

    assert summary["document_source"] == "user-provided"
    assert calls[1]["files"]["file"][0] == "approved-scan.pdf"
    assert calls[1]["files"]["file"][2] == "application/pdf"
    assert safe["steps"][1]["documents"] == [{"chunks_created": 1}]
    assert "approved-scan.pdf" not in str(safe)


def test_smoke_script_rejects_unsupported_user_document(tmp_path) -> None:
    unsupported_doc = tmp_path / "notes.png"
    unsupported_doc.write_bytes(b"png")

    try:
        smoke.run_smoke_test("http://server.test/", document_paths=[str(unsupported_doc)])
    except RuntimeError as exc:
        assert "unsupported document type" in str(exc)
        assert ".pdf" in str(exc)
        assert ".txt" in str(exc)
    else:
        raise AssertionError("unsupported document should fail before any HTTP call")


def test_assistant_bridge_smoke_calls_ui_contract_flow(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    summary = smoke.run_assistant_bridge_smoke_test("http://server.test/", project_root="/tmp/project")

    assert summary["ok"] is True
    assert [step["step"] for step in summary["steps"]] == smoke.ASSISTANT_BRIDGE_SMOKE_FLOW
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
            "json": {"message": "현재 상태 알려줘", "project_root": "/tmp/project", "mode": "auto"},
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
    assert summary["steps"][1]["endpoints_count"] == 3
    assert summary["steps"][1]["protected_endpoints_count"] == 2
    assert summary["steps"][5]["sessions_count"] == 1
    assert summary["steps"][6]["total_messages"] == 2


def test_sanitized_smoke_summary_omits_sensitive_or_noisy_fields(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    summary = smoke.run_smoke_test("http://server.test/")
    safe = smoke.build_sanitized_smoke_summary(summary)
    safe_without_excluded = dict(safe)
    safe_without_excluded.pop("excluded_fields", None)
    encoded = str(safe_without_excluded)

    assert safe["safe_to_paste"] is True
    assert safe["mode"] == "document-rag"
    assert safe["steps"][1]["documents"] == [
        {"filename": "smoke-backend-notes.md", "chunks_created": 1},
        {"filename": "smoke-architecture-notes.txt", "chunks_created": 1},
    ]
    assert "request_id" in safe["excluded_fields"]
    assert "request_id" not in str(safe["steps"])
    assert "document_id" not in encoded
    assert "Authorization header access token" not in encoded
    assert "secret" not in encoded


def test_sanitized_assistant_summary_omits_project_root(monkeypatch) -> None:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(smoke.httpx, "Client", client_factory)

    summary = smoke.run_assistant_bridge_smoke_test("http://server.test/", project_root="/Users/juyoung/local-ai-server")
    safe = smoke.build_sanitized_smoke_summary(summary)
    encoded = str(safe)

    assert safe["mode"] == "assistant-bridge"
    assert safe["steps"][2]["has_project_root"] is True
    assert "/Users/juyoung/local-ai-server" not in encoded
    assert "project_root" in safe["excluded_fields"]


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
    assert [step["step"] for step in summary["steps"]] == smoke.ASSISTANT_BRIDGE_PREFLIGHT_FLOW
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


def test_smoke_flow_docs_match_script_contract() -> None:
    document_flow = " → ".join(smoke.DOCUMENT_RAG_SMOKE_FLOW)
    assistant_readme_flow = (
        "assistant-startup → api-inventory → assistant-bootstrap → action-preview → "
        "assistant-message(auto/status intent) → sessions → messages"
    )
    assistant_endpoint_tokens = [
        "GET /assistant/startup",
        "GET /project/api-inventory",
        "POST /assistant/bootstrap",
        "POST /assistant/action-preview",
        "POST /assistant/message",
        "GET /assistant/sessions",
        "GET /assistant/sessions/{session_id}/messages",
    ]

    readme = Path("README.md").read_text(encoding="utf-8")
    assert document_flow in readme
    assert assistant_readme_flow in readme
    assert "임시 Markdown/Text 문서" in readme
    assert "smoke-backend-notes.md" in readme
    assert "smoke-architecture-notes.txt" in readme
    assert "--sanitized-summary" in readme
    assert "safe_to_paste=true" in readme

    for path in SMOKE_DOCS:
        text = Path(path).read_text(encoding="utf-8")
        assert document_flow in text, f"{path} missing document smoke flow"
        assert "smoke-backend-notes.md" in text, f"{path} missing Markdown smoke sample"
        assert "smoke-architecture-notes.txt" in text, f"{path} missing text smoke sample"
        assert "--sanitized-summary" in text, f"{path} missing sanitized smoke summary command"
        assert "excluded_fields" in text, f"{path} missing sanitized excluded fields"
        for token in assistant_endpoint_tokens:
            assert token in text, f"{path} missing {token}"


def test_api_and_release_docs_include_sanitized_smoke_summary_contract() -> None:
    for path in ["docs/API.md", "docs/RELEASE_CHECKLIST.md"]:
        text = Path(path).read_text(encoding="utf-8")
        assert "--sanitized-summary" in text
        assert "safe_to_paste=true" in text
        assert "질문/답변 원문" in text
        assert "request id" in text
        assert "stored path" in text


def test_ui_connect_guide_documents_assistant_smoke_expected_output() -> None:
    text = Path("docs/UI_CONNECT_GUIDE.md").read_text(encoding="utf-8")

    for step in smoke.ASSISTANT_BRIDGE_PREFLIGHT_FLOW + smoke.ASSISTANT_BRIDGE_SMOKE_FLOW:
        assert f"`{step}" in text or f"`{step}.status`" in text

    for field in [
        "ok=true",
        "health.status",
        "assistant-startup.status",
        "api-inventory.status",
        "ui_ready",
        "protected",
        "endpoints_count",
        "protected_endpoints_count",
        "has_project_root",
        "intent=status",
        "would_execute=false",
        "session_id",
        "response_type=status",
        "sessions_count",
        "total_messages",
        "/documents/index-folder-job-preview",
        "/documents/vector-rebuild-preview",
        "dry_run=true",
        "would_enqueue=false",
        "embedding_batches_estimated",
        "actions",
    ]:
        assert field in text

    assert "업로드, RAG, Ollama 답변 생성" in text
    assert "SQLite에 assistant session/message 기록" in text
    assert "Chroma write" in text
