import json
import os
from pathlib import Path

import httpx
import typer

app = typer.Typer(help="local-ai-server CLI")

UPLOAD_CONTENT_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _base_url() -> str:
    return os.getenv("LOCAL_AI_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")


def _headers() -> dict[str, str]:
    api_key = os.getenv("LOCAL_API_KEY")
    return {"X-API-Key": api_key} if api_key else {}


def _print_response(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        typer.echo(f"HTTP {exc.response.status_code}: {exc.response.text}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(response.json(), ensure_ascii=False, indent=2))


def _request_json(method: str, path: str, **kwargs) -> dict | list:
    with httpx.Client(timeout=120.0) as client:
        response = getattr(client, method)(f"{_base_url()}{path}", **kwargs)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        typer.echo(f"HTTP {exc.response.status_code}: {exc.response.text}", err=True)
        raise typer.Exit(code=1) from exc
    return response.json()


def _print_json(payload: dict | list) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_assistant_answer(payload: dict | list) -> None:
    if not isinstance(payload, dict) or "answer" not in payload:
        _print_json(payload)
        return
    typer.echo(payload["answer"])
    request_id = payload.get("request_id")
    sources = payload.get("sources") or []
    if request_id:
        typer.echo(f"\nrequest_id={request_id}")
    if sources:
        typer.echo("sources:")
        for source in sources:
            typer.echo(
                f"- document_id={source.get('document_id')} "
                f"filename={source.get('filename')} "
                f"chunk_index={source.get('chunk_index')} "
                f"chunk_id={source.get('chunk_id')}"
            )


@app.command()
def health() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/health"))


@app.command()
def doctor() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/health/ollama"))


@app.command()
def ask(question: str, temperature: float = 0.2) -> None:
    payload = {"question": question, "temperature": temperature}
    with httpx.Client(timeout=120.0) as client:
        _print_response(client.post(f"{_base_url()}/ask", json=payload, headers=_headers()))


@app.command("ask-docs")
def ask_docs(question: str, top_k: int = 5, temperature: float = 0.2) -> None:
    payload = {"question": question, "top_k": top_k, "temperature": temperature}
    with httpx.Client(timeout=120.0) as client:
        _print_response(client.post(f"{_base_url()}/ask-with-docs", json=payload, headers=_headers()))


@app.command("assist")
def assist(question: str, top_k: int = 5, temperature: float = 0.2, json_output: bool = False) -> None:
    payload = {"question": question, "top_k": top_k, "temperature": temperature}
    response = _request_json("post", "/ask-with-docs", json=payload, headers=_headers())
    if json_output:
        _print_json(response)
    else:
        _print_assistant_answer(response)


@app.command()
def search(query: str, top_k: int = 5) -> None:
    payload = {"query": query, "top_k": top_k}
    with httpx.Client(timeout=60.0) as client:
        _print_response(client.post(f"{_base_url()}/search", json=payload, headers=_headers()))


@app.command()
def upload(file_path: Path) -> None:
    if not file_path.exists():
        typer.echo(f"파일을 찾을 수 없습니다: {file_path}", err=True)
        raise typer.Exit(code=1)
    content_type = UPLOAD_CONTENT_TYPES.get(file_path.suffix.lower(), "application/octet-stream")
    with file_path.open("rb") as file:
        files = {"file": (file_path.name, file, content_type)}
        with httpx.Client(timeout=120.0) as client:
            _print_response(client.post(f"{_base_url()}/documents/upload", files=files, headers=_headers()))


@app.command("index")
def index_folder(folder_path: Path, recursive: bool = True) -> None:
    payload = {"folder_path": str(folder_path), "recursive": recursive}
    with httpx.Client(timeout=120.0) as client:
        _print_response(client.post(f"{_base_url()}/documents/index-folder", json=payload, headers=_headers()))


@app.command("index-preview")
def index_folder_preview(folder_path: Path, recursive: bool = True) -> None:
    payload = {"folder_path": str(folder_path), "recursive": recursive}
    with httpx.Client(timeout=120.0) as client:
        _print_response(
            client.post(f"{_base_url()}/documents/index-folder-preview", json=payload, headers=_headers())
        )


@app.command("docs")
def docs(
    source_type: str | None = None,
    file_type: str | None = None,
    query: str | None = None,
) -> None:
    params = {}
    if source_type:
        params["source_type"] = source_type
    if file_type:
        params["file_type"] = file_type
    if query:
        params["query"] = query
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/documents", params=params))


@app.command("document-types")
def document_types() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/documents/supported-types"))


@app.command("chunks")
def chunks(document_id: int, limit: int = 20, offset: int = 0) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(
            client.get(
                f"{_base_url()}/documents/{document_id}/chunks",
                params={"limit": limit, "offset": offset},
            )
        )


@app.command("stats")
def stats() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/documents/stats"))


@app.command("logs")
def logs(limit: int = 20, offset: int = 0, mode: str | None = None, query: str | None = None) -> None:
    params = {"limit": limit, "offset": offset}
    if mode:
        params["mode"] = mode
    if query:
        params["query"] = query
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/chat-logs", params=params))


@app.command("log")
def log(chat_log_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/chat-logs/{chat_log_id}"))


@app.command("feedbacks")
def feedbacks(
    limit: int = 20,
    offset: int = 0,
    rating: str | None = None,
    chat_log_id: int | None = None,
) -> None:
    params = {"limit": limit, "offset": offset}
    if rating:
        params["rating"] = rating
    if chat_log_id is not None:
        params["chat_log_id"] = chat_log_id
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/feedback", params=params))


@app.command("agent-plan")
def agent_plan(instruction: str) -> None:
    payload = {"instruction": instruction}
    with httpx.Client(timeout=60.0) as client:
        _print_response(client.post(f"{_base_url()}/agent/plan", json=payload, headers=_headers()))


@app.command("agent-runs")
def agent_runs(limit: int = 20, offset: int = 0) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/agent/runs", params={"limit": limit, "offset": offset}, headers=_headers()))


@app.command("agent-run")
def agent_run(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/agent/runs/{run_id}", headers=_headers()))


@app.command("agent-results")
def agent_results(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/agent/runs/{run_id}/results", headers=_headers()))


@app.command("agent-actions")
def agent_actions(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/agent/runs/{run_id}/actions", headers=_headers()))


@app.command("agent-dry-run")
def agent_dry_run(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.post(f"{_base_url()}/agent/runs/{run_id}/dry-run", headers=_headers()))


@app.command("agent-shell")
def agent_shell() -> None:
    typer.echo("local-ai agent shell. 질문을 입력하면 agent plan을 만들고, /help로 명령을 봅니다.")
    while True:
        try:
            command = typer.prompt("local-ai")
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            break

        command = command.strip()
        if not command:
            continue
        if command in {"/quit", "/exit", "quit", "exit"}:
            break
        if command == "/help":
            typer.echo(
                "\n".join(
                    [
                        "일반 문장: agent plan 생성",
                        "/runs",
                        "/run <id>",
                        "/actions <id>",
                        "/dry-run <id>",
                        "/approve <id>",
                        "/reject <id>",
                        "/execute <id>",
                        "/results <id>",
                        "/quit",
                    ]
                )
            )
            continue

        try:
            payload = _agent_shell_dispatch(command)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            continue
        _print_json(payload)


def _agent_shell_dispatch(command: str) -> dict | list:
    parts = command.split(maxsplit=1)
    name = parts[0]
    value = parts[1] if len(parts) > 1 else ""

    if name == "/runs":
        return _request_json("get", "/agent/runs", headers=_headers())
    if name in {"/run", "/actions", "/dry-run", "/approve", "/reject", "/execute", "/results"}:
        if not value.isdigit():
            raise ValueError(f"{name} 명령에는 숫자 run_id가 필요합니다.")
        run_id = int(value)
        if name == "/run":
            return _request_json("get", f"/agent/runs/{run_id}", headers=_headers())
        if name == "/actions":
            return _request_json("get", f"/agent/runs/{run_id}/actions", headers=_headers())
        if name == "/dry-run":
            return _request_json("post", f"/agent/runs/{run_id}/dry-run", headers=_headers())
        if name == "/approve":
            return _request_json("post", f"/agent/runs/{run_id}/approve", headers=_headers())
        if name == "/reject":
            return _request_json("post", f"/agent/runs/{run_id}/reject", headers=_headers())
        if name == "/execute":
            return _request_json("post", f"/agent/runs/{run_id}/execute", headers=_headers())
        if name == "/results":
            return _request_json("get", f"/agent/runs/{run_id}/results", headers=_headers())

    return _request_json("post", "/agent/plan", json={"instruction": command}, headers=_headers())


@app.command("assistant")
def assistant(top_k: int = 5, temperature: float = 0.2) -> None:
    typer.echo("local-ai assistant. 일반 질문은 내 문서 기준으로 답하고, /help로 명령을 봅니다.")
    while True:
        try:
            command = typer.prompt("assistant")
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            break

        command = command.strip()
        if not command:
            continue
        if command in {"/quit", "/exit", "quit", "exit"}:
            break
        if command == "/help":
            typer.echo(
                "\n".join(
                    [
                        "일반 문장: /ask-with-docs로 문서 기반 답변",
                        "/ask <질문>",
                        "/search <검색어>",
                        "/docs",
                        "/stats",
                        "/index-preview <folder>",
                        "/index <folder>",
                        "/agent <지시>",
                        "/runs",
                        "/run <id>",
                        "/actions <id>",
                        "/dry-run <id>",
                        "/approve <id>",
                        "/execute <id>",
                        "/results <id>",
                        "/quit",
                    ]
                )
            )
            continue

        try:
            payload = _assistant_dispatch(command, top_k=top_k, temperature=temperature)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            continue
        if isinstance(payload, dict) and "answer" in payload:
            _print_assistant_answer(payload)
        else:
            _print_json(payload)


def _assistant_dispatch(command: str, top_k: int, temperature: float) -> dict | list:
    parts = command.split(maxsplit=1)
    name = parts[0]
    value = parts[1] if len(parts) > 1 else ""

    if name == "/docs":
        return _request_json("get", "/documents")
    if name == "/stats":
        return _request_json("get", "/documents/stats")
    if name == "/runs":
        return _request_json("get", "/agent/runs", headers=_headers())
    if name == "/search":
        if not value:
            raise ValueError("/search 명령에는 검색어가 필요합니다.")
        return _request_json("post", "/search", json={"query": value, "top_k": top_k}, headers=_headers())
    if name == "/ask":
        if not value:
            raise ValueError("/ask 명령에는 질문이 필요합니다.")
        return _request_json(
            "post",
            "/ask-with-docs",
            json={"question": value, "top_k": top_k, "temperature": temperature},
            headers=_headers(),
        )
    if name in {"/index-preview", "/index"}:
        if not value:
            raise ValueError(f"{name} 명령에는 folder path가 필요합니다.")
        endpoint = "/documents/index-folder-preview" if name == "/index-preview" else "/documents/index-folder"
        return _request_json(
            "post",
            endpoint,
            json={"folder_path": value, "recursive": True},
            headers=_headers(),
        )
    if name == "/agent":
        if not value:
            raise ValueError("/agent 명령에는 지시문이 필요합니다.")
        return _request_json("post", "/agent/plan", json={"instruction": value}, headers=_headers())
    if name in {"/run", "/actions", "/dry-run", "/approve", "/execute", "/results"}:
        if not value.isdigit():
            raise ValueError(f"{name} 명령에는 숫자 run_id가 필요합니다.")
        run_id = int(value)
        if name == "/run":
            return _request_json("get", f"/agent/runs/{run_id}", headers=_headers())
        if name == "/actions":
            return _request_json("get", f"/agent/runs/{run_id}/actions", headers=_headers())
        if name == "/dry-run":
            return _request_json("post", f"/agent/runs/{run_id}/dry-run", headers=_headers())
        if name == "/approve":
            return _request_json("post", f"/agent/runs/{run_id}/approve", headers=_headers())
        if name == "/execute":
            return _request_json("post", f"/agent/runs/{run_id}/execute", headers=_headers())
        if name == "/results":
            return _request_json("get", f"/agent/runs/{run_id}/results", headers=_headers())

    return _request_json(
        "post",
        "/ask-with-docs",
        json={"question": command, "top_k": top_k, "temperature": temperature},
        headers=_headers(),
    )


@app.command("agent-approve")
def agent_approve(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.post(f"{_base_url()}/agent/runs/{run_id}/approve", headers=_headers()))


@app.command("agent-reject")
def agent_reject(run_id: int) -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.post(f"{_base_url()}/agent/runs/{run_id}/reject", headers=_headers()))


@app.command("agent-execute")
def agent_execute(run_id: int) -> None:
    with httpx.Client(timeout=60.0) as client:
        _print_response(client.post(f"{_base_url()}/agent/runs/{run_id}/execute", headers=_headers()))


@app.command("integrity")
def integrity() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/documents/integrity"))


@app.command("repair-preview")
def repair_preview() -> None:
    with httpx.Client(timeout=30.0) as client:
        _print_response(client.get(f"{_base_url()}/documents/repair-preview"))


@app.command("export-sft")
def export_sft(output: Path = Path("data/sft_dataset.jsonl")) -> None:
    from scripts.export_sft_data import export_sft_data

    count = export_sft_data(output)
    typer.echo(f"exported={count} output={output}")


if __name__ == "__main__":
    app()
