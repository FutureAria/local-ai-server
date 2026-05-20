from pathlib import Path

from typer.testing import CliRunner

import cli.main as cli_main


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
                        "phase": 13,
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
        if url.endswith("/assistant/sessions/session-1/messages"):
            return FakeResponse({"session_id": "session-1", "total_messages": 1, "messages": []})
        if url.endswith("/assistant/sessions"):
            return FakeResponse({"sessions": [], "limit": kwargs.get("params", {}).get("limit", 20), "offset": 0})
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
        if url.endswith("/assistant/bootstrap"):
            return FakeResponse(
                {
                    "service": "local-ai-server",
                    "capabilities": {"endpoints": {"message": "POST /assistant/message"}},
                    "status": {"current_phase": {"phase": 13}},
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
    assert "현재 차수: 13차" in status_result.output
    assert "Recommended Next Model" in status_result.output
    assert "다음 차수: 13차" in next_result.output
    assert calls == [
        {"method": "GET", "url": "http://127.0.0.1:8000/project/status"},
        {"method": "GET", "url": "http://127.0.0.1:8000/project/next"},
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
    action_preview_result = CliRunner().invoke(
        cli_main.app,
        ["assistant-action-preview", "브라우저 열어줘", "--project-root", "/tmp/project"],
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
    assert action_preview_result.exit_code == 0
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
            "method": "POST",
            "url": "http://127.0.0.1:8000/assistant/action-preview",
            "json": {"message": "브라우저 열어줘", "project_root": "/tmp/project", "mode": "auto"},
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
        input="JWT 설명해줘\n/search JWT\n/docs\n/roots\n/status\n/next\n/shell-policy\n/shell-dry-run pwd\n/summary\n/agent README 읽어줘\n/quit\n",
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
