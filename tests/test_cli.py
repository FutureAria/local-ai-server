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


def test_cli_upload_missing_file_fails_before_http_call(monkeypatch, tmp_path) -> None:
    calls = _install_fake_client(monkeypatch)
    missing_file = tmp_path / "missing.md"

    result = CliRunner().invoke(cli_main.app, ["upload", str(missing_file)])

    assert result.exit_code == 1
    assert "파일을 찾을 수 없습니다" in result.output
    assert calls == []
