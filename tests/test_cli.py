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
        return FakeResponse({"method": "GET"})

    def post(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": "POST", "url": url, **kwargs})
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


def test_cli_upload_missing_file_fails_before_http_call(monkeypatch, tmp_path) -> None:
    calls = _install_fake_client(monkeypatch)
    missing_file = tmp_path / "missing.md"

    result = CliRunner().invoke(cli_main.app, ["upload", str(missing_file)])

    assert result.exit_code == 1
    assert "파일을 찾을 수 없습니다" in result.output
    assert calls == []
