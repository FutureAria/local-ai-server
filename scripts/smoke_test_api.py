import argparse
import json
import os
import tempfile
from pathlib import Path

import httpx


SAMPLE_MARKDOWN_TEXT = """# Local AI smoke test

JWT 인증 흐름은 access token을 Authorization header로 전달하고,
refresh token은 재발급에 사용한다.
이 문서는 local-ai-server E2E smoke test용 임시 문서다.
"""

SAMPLE_TEXT_TEXT = """Local AI smoke test text note

Controller는 HTTP 요청과 응답 경계를 담당하고,
Service는 비즈니스 규칙과 트랜잭션 흐름을 담당한다.
이 텍스트 파일은 local-ai-server E2E smoke test용 임시 문서다.
"""

SAMPLE_DOCUMENTS = [
    ("smoke-backend-notes.md", SAMPLE_MARKDOWN_TEXT, "text/markdown"),
    ("smoke-architecture-notes.txt", SAMPLE_TEXT_TEXT, "text/plain"),
]

SUPPORTED_USER_DOCUMENT_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".htm": "text/html",
    ".html": "text/html",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}

DOCUMENT_RAG_SMOKE_FLOW = [
    "health",
    "upload",
    "search",
    "ask-with-docs",
    "feedback",
    "stats",
]

ASSISTANT_BRIDGE_PREFLIGHT_FLOW = [
    "health",
    "assistant-startup",
    "api-inventory",
]

ASSISTANT_BRIDGE_SMOKE_FLOW = [
    "assistant-startup",
    "api-inventory",
    "assistant-bootstrap",
    "assistant-action-preview",
    "assistant-read-only-result-wrapper",
    "assistant-message",
    "assistant-sessions",
    "assistant-messages",
]

SANITIZED_SUMMARY_EXCLUDED_FIELDS = [
    "question",
    "answer",
    "content",
    "headers",
    "note",
    "api_key",
    "project_root",
    "request_id",
    "stored_path",
    "document_id",
    "chunk_id",
]


def _headers() -> dict[str, str]:
    api_key = os.getenv("LOCAL_API_KEY")
    return {"X-API-Key": api_key} if api_key else {}


def _raise_for_status(step: str, response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"{step} failed: HTTP {response.status_code} {response.text}") from exc


def _write_sample_documents(temp_dir: str) -> list[tuple[Path, str]]:
    sample_files = []
    for filename, content, media_type in SAMPLE_DOCUMENTS:
        sample_file = Path(temp_dir) / filename
        sample_file.write_text(content, encoding="utf-8")
        sample_files.append((sample_file, media_type))
    return sample_files


def _prepare_user_documents(document_paths: list[str]) -> list[tuple[Path, str]]:
    prepared_documents = []
    for raw_path in document_paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            raise RuntimeError(f"document does not exist: {path}")
        if not path.is_file():
            raise RuntimeError(f"document is not a file: {path}")
        media_type = SUPPORTED_USER_DOCUMENT_TYPES.get(path.suffix.lower())
        if media_type is None:
            supported = ", ".join(sorted(SUPPORTED_USER_DOCUMENT_TYPES))
            raise RuntimeError(f"unsupported document type: {path.suffix or '(none)'}; supported: {supported}")
        prepared_documents.append((path, media_type))
    return prepared_documents


def run_assistant_bridge_preflight(base_url: str, timeout: float = 30.0) -> dict:
    base_url = base_url.rstrip("/")
    headers = _headers()
    summary: dict = {"base_url": base_url, "mode": "assistant-bridge-preflight", "steps": []}

    with httpx.Client(timeout=timeout) as client:
        for step, method, path, request_headers in [
            ("health", "GET", "/health", {}),
            ("assistant-startup", "GET", "/assistant/startup", headers),
            ("api-inventory", "GET", "/project/api-inventory", {}),
        ]:
            response = client.get(f"{base_url}{path}", headers=request_headers)
            step_result = {"step": step, "method": method, "path": path, "status": response.status_code}
            if response.status_code == 404 and step == "assistant-startup":
                step_result["hint"] = (
                    "/health responded but /assistant/startup returned 404. "
                    "Another server may be using this base URL."
                )
            summary["steps"].append(step_result)

    statuses = {step["step"]: step["status"] for step in summary["steps"]}
    summary["ok"] = (
        statuses.get("health") == 200
        and statuses.get("assistant-startup") == 200
        and statuses.get("api-inventory") == 200
    )
    if not summary["ok"]:
        summary["hint"] = (
            "Start local-ai-server on this base URL, or pass a different --base-url "
            "such as http://127.0.0.1:8010."
        )
    return summary


def _upload_and_run_rag_flow(
    client: httpx.Client,
    base_url: str,
    headers: dict[str, str],
    documents: list[tuple[Path, str]],
    summary: dict,
) -> None:
    uploaded_documents = []
    for document_path, media_type in documents:
        with document_path.open("rb") as file:
            upload = client.post(
                f"{base_url}/documents/upload",
                files={"file": (document_path.name, file, media_type)},
                headers=headers,
            )
        _raise_for_status(f"upload {document_path.name}", upload)
        upload_body = upload.json()
        uploaded_documents.append(
            {
                "filename": upload_body.get("filename", document_path.name),
                "document_id": upload_body["document_id"],
                "chunks_created": upload_body["chunks_created"],
            }
        )
    summary["steps"].append(
        {
            "step": "upload",
            "status": 200,
            "documents_count": len(uploaded_documents),
            "chunks_count": sum(item["chunks_created"] for item in uploaded_documents),
            "documents": uploaded_documents,
        }
    )

    search = client.post(
        f"{base_url}/search",
        json={"query": "Authorization header access token", "top_k": 3},
        headers=headers,
    )
    _raise_for_status("search", search)
    search_body = search.json()
    summary["steps"].append(
        {
            "step": "search",
            "status": search.status_code,
            "results_count": len(search_body.get("results", [])),
        }
    )

    ask_docs = client.post(
        f"{base_url}/ask-with-docs",
        json={"question": "내 문서 기준으로 access token은 어디로 전달해?", "top_k": 3},
        headers=headers,
    )
    _raise_for_status("ask-with-docs", ask_docs)
    ask_body = ask_docs.json()
    summary["steps"].append(
        {
            "step": "ask-with-docs",
            "status": ask_docs.status_code,
            "request_id": ask_body["request_id"],
            "sources_count": len(ask_body.get("sources", [])),
        }
    )

    feedback = client.post(
        f"{base_url}/feedback",
        json={"request_id": ask_body["request_id"], "rating": "good", "note": "smoke test"},
        headers=headers,
    )
    _raise_for_status("feedback", feedback)
    feedback_body = feedback.json()
    summary["steps"].append(
        {
            "step": "feedback",
            "status": feedback.status_code,
            "feedback_id": feedback_body["feedback_id"],
        }
    )

    stats = client.get(f"{base_url}/documents/stats")
    _raise_for_status("stats", stats)
    stats_body = stats.json()
    summary["steps"].append(
        {
            "step": "stats",
            "status": stats.status_code,
            "documents_count": stats_body["documents_count"],
            "chunks_count": stats_body["chunks_count"],
        }
    )


def run_smoke_test(base_url: str, timeout: float = 120.0, document_paths: list[str] | None = None) -> dict:
    base_url = base_url.rstrip("/")
    headers = _headers()
    summary: dict = {"base_url": base_url, "steps": []}

    if document_paths:
        documents = _prepare_user_documents(document_paths)
        summary["document_source"] = "user-provided"
        summary["user_documents_count"] = len(documents)
    else:
        summary["document_source"] = "sample"
        summary["sample_documents"] = [item[0] for item in SAMPLE_DOCUMENTS]

    with tempfile.TemporaryDirectory(prefix="local-ai-smoke-") as temp_dir:
        if not document_paths:
            documents = _write_sample_documents(temp_dir)

        with httpx.Client(timeout=timeout) as client:
            health = client.get(f"{base_url}/health")
            _raise_for_status("health", health)
            summary["steps"].append({"step": "health", "status": health.status_code})

            _upload_and_run_rag_flow(client, base_url, headers, documents, summary)

    summary["ok"] = True
    return summary


def run_assistant_bridge_smoke_test(base_url: str, project_root: str | None = None, timeout: float = 120.0) -> dict:
    base_url = base_url.rstrip("/")
    headers = _headers()
    project_root = project_root or os.getcwd()
    summary: dict = {"base_url": base_url, "project_root": project_root, "steps": []}

    with httpx.Client(timeout=timeout) as client:
        startup = client.get(f"{base_url}/assistant/startup", headers=headers)
        _raise_for_status("assistant-startup", startup)
        startup_body = startup.json()
        summary["steps"].append(
            {
                "step": "assistant-startup",
                "status": startup.status_code,
                "ui_ready": startup_body.get("ui", {}).get("ready"),
                "protected": startup_body.get("protected"),
            }
        )

        inventory = client.get(f"{base_url}/project/api-inventory")
        _raise_for_status("api-inventory", inventory)
        inventory_body = inventory.json()
        summary["steps"].append(
            {
                "step": "api-inventory",
                "status": inventory.status_code,
                "endpoints_count": inventory_body.get("endpoints_count"),
                "protected_endpoints_count": inventory_body.get("protected_endpoints_count"),
            }
        )

        bootstrap = client.post(
            f"{base_url}/assistant/bootstrap",
            json={"project_root": project_root, "include_sessions": True, "sessions_limit": 5},
            headers=headers,
        )
        _raise_for_status("assistant-bootstrap", bootstrap)
        bootstrap_body = bootstrap.json()
        summary["steps"].append(
            {
                "step": "assistant-bootstrap",
                "status": bootstrap.status_code,
                "ui_ready": bootstrap_body.get("ui", {}).get("ready"),
                "has_project_root": bootstrap_body.get("project_root") is not None,
            }
        )

        preview = client.post(
            f"{base_url}/assistant/action-preview",
            json={"message": "현재 상태 알려줘", "project_root": project_root, "mode": "auto"},
            headers=headers,
        )
        _raise_for_status("assistant-action-preview", preview)
        preview_body = preview.json()
        summary["steps"].append(
            {
                "step": "assistant-action-preview",
                "status": preview.status_code,
                "intent": preview_body.get("intent"),
                "would_execute": preview_body.get("would_execute"),
            }
        )

        wrapper_preview = client.post(
            f"{base_url}/assistant/action-loop-read-only-dispatch-preview",
            json={
                "goal": "read-only result wrapper smoke",
                "project_root": project_root,
                "proposed_steps": [],
            },
            headers=headers,
        )
        _raise_for_status("assistant-read-only-result-wrapper", wrapper_preview)
        wrapper_body = wrapper_preview.json()
        wrapper_schema = wrapper_body.get("result_wrapper_schema", {})
        summary["steps"].append(
            {
                "step": "assistant-read-only-result-wrapper",
                "status": wrapper_preview.status_code,
                "schema": wrapper_schema.get("schema"),
                "contract_mode": wrapper_schema.get("contract_mode"),
                "raw_content_allowed": wrapper_schema.get("raw_content_allowed"),
                "approval_like_json_trusted": wrapper_schema.get("approval_like_json_trusted"),
                "can_mutate_frozen_plan": wrapper_schema.get("can_mutate_frozen_plan"),
                "would_dispatch": wrapper_body.get("would_dispatch"),
                "would_read": wrapper_body.get("would_read"),
                "would_fetch": wrapper_body.get("would_fetch"),
                "execution_enabled": wrapper_body.get("execution_enabled"),
            }
        )

        message = client.post(
            f"{base_url}/assistant/message",
            json={"message": "현재 상태 알려줘", "project_root": project_root, "mode": "auto"},
            headers=headers,
        )
        _raise_for_status("assistant-message", message)
        message_body = message.json()
        session_id = message_body["session_id"]
        summary["steps"].append(
            {
                "step": "assistant-message",
                "status": message.status_code,
                "session_id": session_id,
                "response_type": message_body.get("type"),
            }
        )

        sessions = client.get(f"{base_url}/assistant/sessions", params={"limit": 5, "offset": 0}, headers=headers)
        _raise_for_status("assistant-sessions", sessions)
        sessions_body = sessions.json()
        summary["steps"].append(
            {
                "step": "assistant-sessions",
                "status": sessions.status_code,
                "sessions_count": len(sessions_body.get("sessions", [])),
            }
        )

        messages = client.get(
            f"{base_url}/assistant/sessions/{session_id}/messages",
            params={"limit": 10, "offset": 0},
            headers=headers,
        )
        _raise_for_status("assistant-messages", messages)
        messages_body = messages.json()
        summary["steps"].append(
            {
                "step": "assistant-messages",
                "status": messages.status_code,
                "total_messages": messages_body.get("total_messages"),
            }
        )

    summary["ok"] = True
    return summary


def build_sanitized_smoke_summary(summary: dict) -> dict:
    steps = summary.get("steps", [])
    mode = summary.get("mode") or (
        "assistant-bridge" if any(step.get("step") == "assistant-message" for step in steps) else "document-rag"
    )
    sanitized: dict = {
        "ok": summary.get("ok", False),
        "mode": mode,
        "base_url": summary.get("base_url"),
        "steps": [],
        "safe_to_paste": True,
        "excluded_fields": SANITIZED_SUMMARY_EXCLUDED_FIELDS,
    }

    if "sample_documents" in summary:
        sanitized["sample_documents"] = summary["sample_documents"]
    if summary.get("document_source") == "user-provided":
        sanitized["document_source"] = "user-provided"
        sanitized["user_documents_count"] = summary.get("user_documents_count")
    if "assistant_bridge" in summary:
        sanitized["assistant_bridge"] = build_sanitized_smoke_summary(summary["assistant_bridge"])

    for step in steps:
        step_name = step.get("step")
        safe_step = {
            "step": step_name,
            "status": step.get("status"),
        }
        for key in [
            "documents_count",
            "chunks_count",
            "results_count",
            "sources_count",
            "feedback_id",
            "ui_ready",
            "protected",
            "endpoints_count",
            "protected_endpoints_count",
            "has_project_root",
            "intent",
            "would_execute",
            "schema",
            "contract_mode",
            "raw_content_allowed",
            "approval_like_json_trusted",
            "can_mutate_frozen_plan",
            "would_dispatch",
            "would_read",
            "would_fetch",
            "execution_enabled",
            "response_type",
            "sessions_count",
            "total_messages",
        ]:
            if key in step:
                safe_step[key] = step[key]
        if step_name == "upload":
            if summary.get("document_source") == "user-provided":
                safe_step["documents"] = [
                    {"chunks_created": item.get("chunks_created")} for item in step.get("documents", [])
                ]
            else:
                safe_step["documents"] = [
                    {
                        "filename": item.get("filename"),
                        "chunks_created": item.get("chunks_created"),
                    }
                    for item in step.get("documents", [])
                ]
        sanitized["steps"].append(safe_step)

    return sanitized


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local-ai-server API smoke test against a running server.")
    parser.add_argument("--base-url", default=os.getenv("LOCAL_AI_SERVER_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--project-root", default=os.getenv("LOCAL_AI_PROJECT_ROOT", os.getcwd()))
    parser.add_argument(
        "--assistant-bridge-only",
        action="store_true",
        help="Run only the assistant/project API bridge smoke flow. This avoids upload/RAG but creates an assistant session/message.",
    )
    parser.add_argument(
        "--assistant-bridge-preflight",
        action="store_true",
        help="Read-only check for /health, /assistant/startup, and /project/api-inventory before running UI smoke.",
    )
    parser.add_argument(
        "--include-assistant-bridge",
        action="store_true",
        help="Run the document RAG smoke flow and then the assistant/project API bridge smoke flow.",
    )
    parser.add_argument(
        "--sanitized-summary",
        action="store_true",
        help="Print a paste-safe summary without prompt text, answer text, request ids, headers, or local project paths.",
    )
    parser.add_argument(
        "--document",
        action="append",
        default=[],
        help=(
            "Approved real document path to upload for document/RAG smoke. "
            "Supports .md, .txt, .html, .htm, .pdf, and .docx. Can be passed multiple times."
        ),
    )
    args = parser.parse_args()
    if args.assistant_bridge_preflight:
        result = run_assistant_bridge_preflight(args.base_url)
    elif args.assistant_bridge_only:
        result = run_assistant_bridge_smoke_test(args.base_url, project_root=args.project_root)
    else:
        result = run_smoke_test(args.base_url, document_paths=args.document)
        if args.include_assistant_bridge:
            result["assistant_bridge"] = run_assistant_bridge_smoke_test(args.base_url, project_root=args.project_root)
    if args.sanitized_summary:
        result = build_sanitized_smoke_summary(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
