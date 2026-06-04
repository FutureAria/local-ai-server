from pathlib import Path

from typer.testing import CliRunner

import cli.main as cli_main


DIRECT_HTTP_CLI_ROUTE_CASES = [
    (["health"], "GET", "/health"),
    (["doctor"], "GET", "/health/ollama"),
    (["status"], "GET", "/project/status"),
    (["next"], "GET", "/project/next"),
    (["api-inventory"], "GET", "/project/api-inventory"),
    (["shell-policy"], "GET", "/project/shell-policy"),
    (["shell-dry-run", "pwd"], "POST", "/project/shell-dry-run"),
    (["assistant-capabilities"], "GET", "/assistant/capabilities"),
    (["assistant-ping"], "GET", "/assistant/ping"),
    (["assistant-config"], "GET", "/assistant/config"),
    (["assistant-status"], "GET", "/assistant/status"),
    (["assistant-dashboard"], "GET", "/assistant/dashboard"),
    (["assistant-action-preview", "브라우저 열어줘"], "POST", "/assistant/action-preview"),
    (["assistant-action-loop-preflight", "개인 API dispatch"], "POST", "/assistant/action-loop-preflight"),
    (["assistant-action-loop-noop-dispatch", "개인 API dispatch"], "POST", "/assistant/action-loop-noop-dispatch"),
    (["assistant-action-loop-read-only-dispatch-preview", "read only"], "POST", "/assistant/action-loop-read-only-dispatch-preview"),
    (["assistant-automation-plan", "내 개인 API 자동화"], "POST", "/assistant/automation-plan"),
    (["assistant-read-only-scan", "/tmp/project"], "POST", "/assistant/read-only-scan"),
    (["assistant-file-preview", "/tmp/project/README.md"], "POST", "/assistant/file-preview"),
    (["assistant-url-preview", "https://example.com"], "POST", "/assistant/url-preview"),
    (["assistant-workspace-brief", "/tmp/project"], "POST", "/assistant/workspace-brief"),
    (["assistant-shell-preview", "git status"], "POST", "/assistant/shell-preview"),
    (["assistant-shell-approval-preview", "git status"], "POST", "/assistant/shell-approval-preview"),
    (["assistant-shell-run", "git status"], "POST", "/assistant/shell-run"),
    (["assistant-patch-preview", "/tmp/project/note.md", "hello"], "POST", "/assistant/patch-preview"),
    (["assistant-patch-approval-preview", "/tmp/project/note.md", "hello"], "POST", "/assistant/patch-approval-preview"),
    (["assistant-patch-apply", "/tmp/project/note.md", "hello"], "POST", "/assistant/patch-apply"),
    (["assistant-browser-preview", "observe"], "POST", "/assistant/browser-preview"),
    (["assistant-browser-approval-preview", "screenshot"], "POST", "/assistant/browser-approval-preview"),
    (["assistant-browser-interact", "observe"], "POST", "/assistant/browser-interact"),
    (["assistant-ui-contract"], "GET", "/assistant/ui-contract"),
    (["assistant-startup"], "GET", "/assistant/startup"),
    (["assistant-bootstrap"], "POST", "/assistant/bootstrap"),
    (["assistant-session"], "POST", "/assistant/sessions"),
    (["assistant-sessions"], "GET", "/assistant/sessions"),
    (["assistant-messages", "session-1"], "GET", "/assistant/sessions/session-1/messages"),
    (["assistant-message", "질문"], "POST", "/assistant/message"),
    (["assistant-root", "/tmp/project"], "POST", "/assistant/project-root/validate"),
    (["ask", "질문"], "POST", "/ask"),
    (["ask-docs", "질문"], "POST", "/ask-with-docs"),
    (["assist", "질문"], "POST", "/ask-with-docs"),
    (["search", "JWT"], "POST", "/search"),
    (["index", "/tmp/notes"], "POST", "/documents/index-folder"),
    (["index-preview", "/tmp/notes"], "POST", "/documents/index-folder-preview"),
    (["index-job-preview", "/tmp/notes"], "POST", "/documents/index-folder-job-preview"),
    (["docs"], "GET", "/documents"),
    (["document-types"], "GET", "/documents/supported-types"),
    (["chunks", "1"], "GET", "/documents/1/chunks"),
    (["stats"], "GET", "/documents/stats"),
    (["integrity"], "GET", "/documents/integrity"),
    (["repair-preview"], "GET", "/documents/repair-preview"),
    (["vector-rebuild-preview"], "GET", "/documents/vector-rebuild-preview"),
    (["logs"], "GET", "/chat-logs"),
    (["log", "1"], "GET", "/chat-logs/1"),
    (["feedbacks"], "GET", "/feedback"),
    (["agent-plan", "README 읽어줘"], "POST", "/agent/plan"),
    (["agent-runs"], "GET", "/agent/runs"),
    (["agent-run", "1"], "GET", "/agent/runs/1"),
    (["agent-results", "1"], "GET", "/agent/runs/1/results"),
    (["agent-actions", "1"], "GET", "/agent/runs/1/actions"),
    (["agent-dry-run", "1"], "POST", "/agent/runs/1/dry-run"),
    (["agent-approve", "1"], "POST", "/agent/runs/1/approve"),
    (["agent-reject", "1"], "POST", "/agent/runs/1/reject"),
    (["agent-execute", "1"], "POST", "/agent/runs/1/execute"),
]


class FakeResponse:
    status_code = 200
    text = '{"ok": true}'

    def __init__(self, payload: dict | list | None = None) -> None:
        self._payload = payload or {"ok": True}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict | list:
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
        if url.endswith("/project/status") or url.endswith("/project/next"):
            return FakeResponse(
                {
                    "current_phase": {
                        "phase": 15,
                        "title": "Live browser UI QA",
                        "status": "next",
                        "summary": "Exercise browser UI.",
                    },
                    "completed_phases": [
                        {"phase": 1, "title": "FastAPI local RAG server", "status": "done", "summary": "done"}
                    ],
                    "safe_next_tasks": ["Send a real browser UI message"],
                    "blocked_until_review": ["Unrestricted shell execution"],
                    "recommended_next_model": {
                        "recommended_ai": "Codex",
                        "recommended_model": "Codex GPT-5.5",
                        "reason": "safe implementation",
                        "next_task": "Send a real browser UI message",
                        "user_action_required": "없음",
                    },
                }
            )
        if url.endswith("/project/api-inventory"):
            return FakeResponse(
                {
                    "service": "local-ai-server",
                    "mode": "read-only",
                    "endpoints_count": 1,
                    "endpoints": [{"path": "/project/api-inventory", "methods": ["GET"]}],
                }
            )
        if url.endswith("/project/shell-policy"):
            return FakeResponse({"mode": "dry-run-only", "allowed_commands": [], "blocked_tokens": []})
        if url.endswith("/assistant/capabilities"):
            return FakeResponse({"service": "local-ai-server", "modes": ["auto"]})
        if url.endswith("/assistant/ping"):
            return FakeResponse({"status": "ok", "service": "local-ai-server", "ui_ready": True})
        if url.endswith("/assistant/config"):
            return FakeResponse({"service": "local-ai-server", "protected": True, "allowed_roots": []})
        if url.endswith("/assistant/status"):
            return FakeResponse({"service": "local-ai-server", "documents": {"documents_count": 0}})
        if url.endswith("/assistant/dashboard"):
            return FakeResponse({"service": "local-ai-server", "cards": {"connection": {"status": "ready"}}})
        if url.endswith("/assistant/ui-contract"):
            return FakeResponse({"service": "local-ai-server", "version": "1", "startup_sequence": []})
        if url.endswith("/assistant/startup"):
            return FakeResponse(
                {
                    "service": "local-ai-server",
                    "ping": {"status": "ok"},
                    "config": {"protected": True},
                    "dashboard": {"cards": {"connection": {"status": "ready"}}},
                    "ui_contract": {"version": "1"},
                    "ui": {"ready": True},
                }
            )
        if url.endswith("/assistant/sessions/session-1/messages"):
            return FakeResponse({"session_id": "session-1", "total_messages": 1, "messages": []})
        if url.endswith("/assistant/sessions"):
            return FakeResponse({"sessions": [], "limit": kwargs.get("params", {}).get("limit", 20), "offset": 0})
        if url.endswith("/documents/supported-types"):
            return FakeResponse(
                {
                    "types": [
                        {
                            "extension": ".pdf",
                            "file_type": "pdf",
                            "available": True,
                            "optional_dependency": "pypdf",
                            "install_hint": None,
                            "description": "Text-based PDF with optional OCR fallback for PyPDF image XObjects.",
                        }
                    ],
                    "install_hint": "PDF OCR은 pip install -e '.[ocr]'와 로컬 tesseract 설치가 필요합니다.",
                    "pdf_ocr": False,
                    "pdf_ocr_install_hint": "install local tesseract",
                }
            )
        return FakeResponse({"method": "GET"})

    def post(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "POST", "url": url, **kwargs})
        if url.endswith("/ask-with-docs"):
            return FakeResponse(
                {
                    "answer": "문서 기준 답변",
                    "request_id": "11",
                    "sources": [{"document_id": 1, "filename": "note.md", "chunk_index": 0, "chunk_id": 3}],
                }
            )
        if url.endswith("/project/shell-dry-run"):
            return FakeResponse({"status": "allowed_preview", "would_execute": False})
        if url.endswith("/assistant/action-preview"):
            return FakeResponse(
                {
                    "intent": "agent_plan",
                    "recommended_endpoint": "POST /assistant/message",
                    "would_execute": False,
                    "requires_approval": True,
                    "risk_level": "high",
                    "needs": [],
                }
            )
        if url.endswith("/assistant/automation-plan"):
            return FakeResponse(
                {
                    "goal": kwargs.get("json", {}).get("goal", "personal API automation"),
                    "would_execute": False,
                    "blocked_until_review": ["실제 shell 실행"],
                }
            )
        if url.endswith("/assistant/action-loop-preflight"):
            return FakeResponse(
                {
                    "mode": "action-loop-dispatch-preflight-locked",
                    "would_dispatch": False,
                    "execution_enabled": False,
                    "fail_closed": True,
                }
            )
        if url.endswith("/assistant/action-loop-noop-dispatch"):
            return FakeResponse(
                {
                    "mode": "action-loop-noop-dispatch-preview",
                    "would_dispatch": False,
                    "would_dispatch_noop_only": False,
                    "execution_enabled": False,
                    "approval_consume_mode": "validate-only",
                }
            )
        if url.endswith("/assistant/action-loop-read-only-dispatch-preview"):
            return FakeResponse(
                {
                    "mode": "action-loop-read-only-dispatch-boundary-preview",
                    "would_dispatch": False,
                    "would_read": False,
                    "would_fetch": False,
                    "execution_enabled": False,
                    "boundary_mode": "classification-only",
                }
            )
        if url.endswith("/assistant/read-only-scan"):
            return FakeResponse({"mode": "read-only", "would_execute": False})
        if url.endswith("/assistant/file-preview"):
            return FakeResponse({"mode": "read-only", "status": "completed", "would_execute": False})
        if url.endswith("/assistant/url-preview"):
            return FakeResponse({"mode": "read-only-url-preflight", "status": "disabled", "would_fetch": False})
        if url.endswith("/assistant/workspace-brief"):
            return FakeResponse({"mode": "read-only-workspace-brief", "would_execute": False})
        if url.endswith("/assistant/shell-preview"):
            return FakeResponse({"mode": "shell-sandbox-preview", "status": "allowed_preview", "would_execute": False})
        if url.endswith("/assistant/shell-approval-preview"):
            return FakeResponse(
                {"mode": "shell-approval-binding-preview", "approval_required": True, "would_execute": False}
            )
        if url.endswith("/assistant/shell-run"):
            return FakeResponse({"mode": "shell-run-locked", "status": "locked", "execution_enabled": False})
        if url.endswith("/assistant/patch-preview"):
            return FakeResponse({"mode": "patch-preview-locked", "status": "allowed_preview", "would_apply": False})
        if url.endswith("/assistant/patch-approval-preview"):
            return FakeResponse(
                {"mode": "patch-approval-binding-preview", "approval_required": True, "would_apply": False}
            )
        if url.endswith("/assistant/patch-apply"):
            return FakeResponse({"mode": "patch-apply-locked", "status": "locked", "execution_enabled": False})
        if url.endswith("/assistant/browser-preview"):
            return FakeResponse({"mode": "browser-interaction-preview-locked", "status": "allowed_preview", "would_interact": False})
        if url.endswith("/assistant/browser-approval-preview"):
            return FakeResponse(
                {"mode": "browser-approval-binding-preview", "approval_required": True, "would_interact": False}
            )
        if url.endswith("/assistant/browser-interact"):
            return FakeResponse({"mode": "browser-interact-locked", "status": "locked", "execution_enabled": False})
        if url.endswith("/assistant/bootstrap"):
            return FakeResponse(
                {
                    "service": "local-ai-server",
                    "capabilities": {"endpoints": {"message": "POST /assistant/message"}},
                    "status": {"current_phase": {"phase": 15}},
                    "project_root": {"safe_for_read_only_agent": True},
                    "sessions": {"sessions": []},
                    "recommended_calls": [],
                    "ui": {"ready": True, "badge": "LOCAL API READY"},
                }
            )
        if url.endswith("/assistant/sessions"):
            return FakeResponse({"session_id": "session-1"})
        if url.endswith("/assistant/message"):
            return FakeResponse(
                {
                    "session_id": "session-1",
                    "type": "answer",
                    "answer": "통합 assistant 답변",
                    "request_id": "55",
                    "sources": [],
                }
            )
        if url.endswith("/assistant/project-root/validate"):
            return FakeResponse({"safe_for_read_only_agent": True})
        return FakeResponse({"method": "POST"})


def _install_fake_client(monkeypatch) -> list[dict]:
    calls: list[dict] = []

    def client_factory(timeout: float) -> FakeClient:
        return FakeClient(calls)

    monkeypatch.setattr(cli_main.httpx, "Client", client_factory)
    return calls


def _path_from_url(url: str) -> str:
    return "/" + url.split("://", 1)[1].split("/", 1)[1]


def test_direct_http_cli_commands_call_expected_routes(monkeypatch) -> None:
    for args, expected_method, expected_path in DIRECT_HTTP_CLI_ROUTE_CASES:
        calls = _install_fake_client(monkeypatch)
        monkeypatch.setenv("LOCAL_API_KEY", "secret")

        result = CliRunner().invoke(cli_main.app, args)

        assert result.exit_code == 0, f"local-ai {' '.join(args)} failed: {result.output}"
        assert calls, f"local-ai {' '.join(args)} did not call the backend"
        assert calls[0]["method"] == expected_method, f"local-ai {' '.join(args)} used wrong method"
        assert _path_from_url(calls[0]["url"]) == expected_path, f"local-ai {' '.join(args)} used wrong path"


def test_cli_ask_sends_server_url_payload_and_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_AI_SERVER_URL", "http://server.test/")
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["ask", "안녕", "--temperature", "0.4"])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://server.test/ask",
            "json": {"question": "안녕", "temperature": 0.4},
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_status_and_next_show_phase(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)

    status_result = CliRunner().invoke(cli_main.app, ["status"])
    next_result = CliRunner().invoke(cli_main.app, ["next"])

    assert status_result.exit_code == 0
    assert next_result.exit_code == 0
    assert "현재 차수: 15차" in status_result.output
    assert "Recommended Next Model" in status_result.output
    assert "다음 차수: 15차" in next_result.output
    assert calls == [
        {"method": "GET", "url": "http://127.0.0.1:8000/project/status"},
        {"method": "GET", "url": "http://127.0.0.1:8000/project/next"},
    ]


def test_cli_api_inventory_calls_project_inventory(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)

    result = CliRunner().invoke(cli_main.app, ["api-inventory"])

    assert result.exit_code == 0
    assert "api-inventory" in result.output
    assert calls == [
        {"method": "GET", "url": "http://127.0.0.1:8000/project/api-inventory"},
    ]


def test_cli_document_types_preserves_pdf_ocr_fields(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)

    result = CliRunner().invoke(cli_main.app, ["document-types"])

    assert result.exit_code == 0
    assert '"pdf_ocr": false' in result.output
    assert "install local tesseract" in result.output
    assert "OCR fallback" in result.output
    assert calls == [
        {"method": "GET", "url": "http://127.0.0.1:8000/documents/supported-types"},
    ]


def test_cli_roots_and_shell_dry_run(monkeypatch, tmp_path) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    monkeypatch.setenv("AGENT_ALLOWED_ROOTS", str(tmp_path))

    roots_result = CliRunner().invoke(cli_main.app, ["roots"])
    policy_result = CliRunner().invoke(cli_main.app, ["shell-policy"])
    dry_run_result = CliRunner().invoke(cli_main.app, ["shell-dry-run", "pwd"])

    assert roots_result.exit_code == 0
    assert str(tmp_path) in roots_result.output
    assert policy_result.exit_code == 0
    assert dry_run_result.exit_code == 0
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/project/shell-policy",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/project/shell-dry-run",
            "json": {"command": "pwd"},
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_assist_uses_ask_with_docs_and_prints_answer(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["assist", "JWT 설명해줘", "--top-k", "3"])

    assert result.exit_code == 0
    assert "문서 기준 답변" in result.output
    assert "sources:" in result.output
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/ask-with-docs",
            "json": {"question": "JWT 설명해줘", "top_k": 3, "temperature": 0.2},
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_assistant_bridge_commands_send_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    capabilities_result = CliRunner().invoke(cli_main.app, ["assistant-capabilities"])
    ping_result = CliRunner().invoke(cli_main.app, ["assistant-ping"])
    config_result = CliRunner().invoke(cli_main.app, ["assistant-config"])
    status_result = CliRunner().invoke(cli_main.app, ["assistant-status"])
    dashboard_result = CliRunner().invoke(cli_main.app, ["assistant-dashboard"])
    ui_contract_result = CliRunner().invoke(cli_main.app, ["assistant-ui-contract"])
    startup_result = CliRunner().invoke(cli_main.app, ["assistant-startup"])
    action_preview_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-action-preview", "브라우저 열어줘", "--project-root", "/tmp/project"],
    )
    action_loop_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-action-loop-preflight", "개인 API dispatch", "--project-root", "/tmp/project"],
    )
    action_loop_noop_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-action-loop-noop-dispatch", "개인 API dispatch", "--project-root", "/tmp/project"],
    )
    action_loop_read_only_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-action-loop-read-only-dispatch-preview", "read only", "--project-root", "/tmp/project"],
    )
    automation_plan_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-automation-plan", "내 개인 API 자동화", "--project-root", "/tmp/project"],
    )
    shell_preview_result = CliRunner().invoke(cli_main.app, ["assistant-shell-preview", "git status", "--cwd", "/tmp/project"])
    shell_approval_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-shell-approval-preview", "git status", "--cwd", "/tmp/project", "--reason", "local CI"],
    )
    shell_run_result = CliRunner().invoke(cli_main.app, ["assistant-shell-run", "git status", "--cwd", "/tmp/project"])
    patch_preview_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-patch-preview", "/tmp/project/note.md", "hello", "--project-root", "/tmp/project"],
    )
    patch_approval_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-patch-approval-preview", "/tmp/project/note.md", "hello", "--project-root", "/tmp/project", "--reason", "docs"],
    )
    patch_apply_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-patch-apply", "/tmp/project/note.md", "hello", "--project-root", "/tmp/project"],
    )
    browser_preview_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-browser-preview", "observe", "--target-url", "https://example.com"],
    )
    browser_approval_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-browser-approval-preview", "screenshot", "--target-url", "https://example.com", "--reason", "qa"],
    )
    browser_interact_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-browser-interact", "observe", "--target-url", "https://example.com"],
    )
    bootstrap_result = CliRunner().invoke(cli_main.app, ["assistant-bootstrap", "--project-root", "/tmp/project"])
    session_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-session", "--title", "Demo", "--project-root", "/tmp/project"],
    )
    sessions_result = CliRunner().invoke(cli_main.app, ["assistant-sessions", "--limit", "5"])
    messages_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-messages", "session-1", "--limit", "10", "--offset", "1"],
    )
    message_result = CliRunner().invoke(
        cli_main.app,
        [
            "assistant-message",
            "JWT 설명해줘",
            "--session-id",
            "session-1",
            "--project-root",
            "/tmp/project",
            "--mode",
            "auto",
            "--top-k",
            "3",
        ],
    )
    root_result = CliRunner().invoke(cli_main.app, ["assistant-root", "/tmp/project"])

    assert capabilities_result.exit_code == 0
    assert ping_result.exit_code == 0
    assert config_result.exit_code == 0
    assert status_result.exit_code == 0
    assert dashboard_result.exit_code == 0
    assert ui_contract_result.exit_code == 0
    assert startup_result.exit_code == 0
    assert action_preview_result.exit_code == 0
    assert action_loop_result.exit_code == 0
    assert action_loop_noop_result.exit_code == 0
    assert action_loop_read_only_result.exit_code == 0
    assert automation_plan_result.exit_code == 0
    assert shell_preview_result.exit_code == 0
    assert shell_approval_result.exit_code == 0
    assert shell_run_result.exit_code == 0
    assert patch_preview_result.exit_code == 0
    assert patch_approval_result.exit_code == 0
    assert patch_apply_result.exit_code == 0
    assert browser_preview_result.exit_code == 0
    assert browser_approval_result.exit_code == 0
    assert browser_interact_result.exit_code == 0
    assert bootstrap_result.exit_code == 0
    assert session_result.exit_code == 0
    assert sessions_result.exit_code == 0
    assert messages_result.exit_code == 0
    assert message_result.exit_code == 0
    assert root_result.exit_code == 0
    assert "통합 assistant 답변" in message_result.output
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/capabilities",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/ping",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/config",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/status",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/dashboard",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/ui-contract",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/startup",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/action-preview",
            "json": {"message": "브라우저 열어줘", "project_root": "/tmp/project", "mode": "auto"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/action-loop-preflight",
            "json": {"goal": "개인 API dispatch", "project_root": "/tmp/project", "proposed_steps": []},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/action-loop-noop-dispatch",
            "json": {"goal": "개인 API dispatch", "project_root": "/tmp/project", "proposed_steps": []},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/action-loop-read-only-dispatch-preview",
            "json": {"goal": "read only", "project_root": "/tmp/project", "proposed_steps": []},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/automation-plan",
            "json": {"goal": "내 개인 API 자동화", "project_root": "/tmp/project"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-preview",
            "json": {"command": "git status", "cwd": "/tmp/project"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-approval-preview",
            "json": {"command": "git status", "cwd": "/tmp/project", "reason": "local CI", "session_id": None},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-run",
            "json": {
                "command": "git status",
                "cwd": "/tmp/project",
                "approval_id": None,
                "approval_payload_hash": None,
                "session_id": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-preview",
            "json": {"path": "/tmp/project/note.md", "proposed_content": "hello", "project_root": "/tmp/project"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-approval-preview",
            "json": {
                "path": "/tmp/project/note.md",
                "proposed_content": "hello",
                "project_root": "/tmp/project",
                "reason": "docs",
                "session_id": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-apply",
            "json": {
                "path": "/tmp/project/note.md",
                "proposed_content": "hello",
                "project_root": "/tmp/project",
                "approval_id": None,
                "approval_payload_hash": None,
                "session_id": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/browser-preview",
            "json": {
                "action": "observe",
                "target_url": "https://example.com",
                "app_name": None,
                "selector": None,
                "input_preview": None,
                "reason": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/browser-approval-preview",
            "json": {
                "action": "screenshot",
                "target_url": "https://example.com",
                "app_name": None,
                "selector": None,
                "input_preview": None,
                "reason": "qa",
                "session_id": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/browser-interact",
            "json": {
                "action": "observe",
                "target_url": "https://example.com",
                "app_name": None,
                "selector": None,
                "input_preview": None,
                "approval_id": None,
                "approval_payload_hash": None,
                "session_id": None,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/bootstrap",
            "json": {"project_root": "/tmp/project", "include_sessions": True, "sessions_limit": 10},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/sessions",
            "json": {"title": "Demo", "project_root": "/tmp/project"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/sessions",
            "params": {"limit": 5, "offset": 0},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/assistant/sessions/session-1/messages",
            "params": {"limit": 10, "offset": 1},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/message",
            "json": {
                "message": "JWT 설명해줘",
                "session_id": "session-1",
                "project_root": "/tmp/project",
                "mode": "auto",
                "top_k": 3,
                "temperature": 0.2,
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/project-root/validate",
            "json": {"project_root": "/tmp/project"},
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_docs_sends_filter_params_without_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)

    result = CliRunner().invoke(
        cli_main.app,
        ["docs", "--source-type", "upload", "--file-type", "md", "--query", "jwt"],
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/documents",
            "params": {"source_type": "upload", "file_type": "md", "query": "jwt"},
        }
    ]


def test_cli_index_preview_sends_api_key(monkeypatch, tmp_path) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")
    notes = tmp_path / "notes"
    notes.mkdir()

    result = CliRunner().invoke(cli_main.app, ["index-preview", str(notes)])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/documents/index-folder-preview",
            "json": {"folder_path": str(notes), "recursive": True},
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_agent_plan_sends_instruction_and_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["agent-plan", "GitHub 웹 열어줘"])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/plan",
            "json": {"instruction": "GitHub 웹 열어줘"},
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_agent_runs_sends_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["agent-runs", "--limit", "5", "--offset", "1"])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/agent/runs",
            "params": {"limit": 5, "offset": 1},
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_agent_approve_and_reject_send_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    approve_result = CliRunner().invoke(cli_main.app, ["agent-approve", "7"])
    reject_result = CliRunner().invoke(cli_main.app, ["agent-reject", "8"])

    assert approve_result.exit_code == 0
    assert reject_result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/runs/7/approve",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/runs/8/reject",
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_agent_execute_sends_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["agent-execute", "7"])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/runs/7/execute",
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_agent_results_sends_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(cli_main.app, ["agent-results", "7"])

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/agent/runs/7/results",
            "headers": {"X-API-Key": "secret"},
        }
    ]


def test_cli_agent_actions_and_dry_run_send_api_key(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    actions_result = CliRunner().invoke(cli_main.app, ["agent-actions", "7"])
    dry_run_result = CliRunner().invoke(cli_main.app, ["agent-dry-run", "7"])

    assert actions_result.exit_code == 0
    assert dry_run_result.exit_code == 0
    assert calls == [
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/agent/runs/7/actions",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/runs/7/dry-run",
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_agent_shell_creates_plan_and_runs_commands(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(
        cli_main.app,
        ["agent-shell"],
        input="README 읽어줘\n/runs\n/dry-run 3\n/results 3\n/quit\n",
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/plan",
            "json": {"instruction": "README 읽어줘"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/agent/runs",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/runs/3/dry-run",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/agent/runs/3/results",
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_assistant_repl_routes_docs_and_questions(monkeypatch) -> None:
    calls = _install_fake_client(monkeypatch)
    monkeypatch.setenv("LOCAL_API_KEY", "secret")

    result = CliRunner().invoke(
        cli_main.app,
        ["assistant", "--top-k", "4"],
        input=(
            "JWT 설명해줘\n/search JWT\n/docs\n/roots\n/status\n/next\n/shell-policy\n"
            "/shell-dry-run pwd\n/shell-preview git status\n/shell-approval-preview git status\n"
            "/shell-run git status\n/patch-preview README.md\n/patch-approval-preview README.md\n"
            "/patch-apply README.md\n/summary\n/agent README 읽어줘\n/quit\n"
        ),
    )

    assert result.exit_code == 0
    assert "통합 assistant 답변" in result.output
    assert calls == [
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/message",
            "json": {"message": "JWT 설명해줘", "mode": "auto", "top_k": 4, "temperature": 0.2},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/search",
            "json": {"query": "JWT", "top_k": 4},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/documents",
        },
        {"method": "GET", "url": "http://127.0.0.1:8000/project/status"},
        {"method": "GET", "url": "http://127.0.0.1:8000/project/next"},
        {
            "method": "GET",
            "url": "http://127.0.0.1:8000/project/shell-policy",
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/project/shell-dry-run",
            "json": {"command": "pwd"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-preview",
            "json": {"command": "git status", "cwd": "."},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-approval-preview",
            "json": {"command": "git status", "cwd": ".", "reason": "assistant repl preview"},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/shell-run",
            "json": {"command": "git status", "cwd": "."},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-preview",
            "json": {"path": "README.md", "proposed_content": Path("README.md").read_text(encoding="utf-8"), "project_root": None},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-approval-preview",
            "json": {
                "path": "README.md",
                "proposed_content": Path("README.md").read_text(encoding="utf-8"),
                "project_root": None,
                "reason": "assistant repl preview",
            },
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/patch-apply",
            "json": {"path": "README.md", "proposed_content": Path("README.md").read_text(encoding="utf-8"), "project_root": None},
            "headers": {"X-API-Key": "secret"},
        },
        {
            "method": "POST",
            "url": "http://127.0.0.1:8000/agent/plan",
            "json": {"instruction": "README 읽어줘"},
            "headers": {"X-API-Key": "secret"},
        },
    ]


def test_cli_upload_missing_file_fails_before_http_call(monkeypatch, tmp_path) -> None:
    calls = _install_fake_client(monkeypatch)
    missing_file = tmp_path / "missing.md"

    result = CliRunner().invoke(cli_main.app, ["upload", str(missing_file)])

    assert result.exit_code == 1
    assert "파일을 찾을 수 없습니다" in result.output
    assert calls == []
