import argparse
import json
import os
import tempfile
from pathlib import Path

import httpx


SAMPLE_TEXT = """# Local AI smoke test

JWT 인증 흐름은 access token을 Authorization header로 전달하고,
refresh token은 재발급에 사용한다.
이 문서는 local-ai-server E2E smoke test용 임시 문서다.
"""


def _headers() -> dict[str, str]:
    api_key = os.getenv("LOCAL_API_KEY")
    return {"X-API-Key": api_key} if api_key else {}


def _raise_for_status(step: str, response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"{step} failed: HTTP {response.status_code} {response.text}") from exc


def run_smoke_test(base_url: str, timeout: float = 120.0) -> dict:
    base_url = base_url.rstrip("/")
    headers = _headers()
    summary: dict = {"base_url": base_url, "steps": []}

    with tempfile.TemporaryDirectory(prefix="local-ai-smoke-") as temp_dir:
        sample_file = Path(temp_dir) / "smoke-backend-notes.md"
        sample_file.write_text(SAMPLE_TEXT, encoding="utf-8")

        with httpx.Client(timeout=timeout) as client:
            health = client.get(f"{base_url}/health")
            _raise_for_status("health", health)
            summary["steps"].append({"step": "health", "status": health.status_code})

            with sample_file.open("rb") as file:
                upload = client.post(
                    f"{base_url}/documents/upload",
                    files={"file": (sample_file.name, file, "text/markdown")},
                    headers=headers,
                )
            _raise_for_status("upload", upload)
            upload_body = upload.json()
            summary["steps"].append(
                {
                    "step": "upload",
                    "status": upload.status_code,
                    "document_id": upload_body["document_id"],
                    "chunks_created": upload_body["chunks_created"],
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

        message = client.post(
            f"{base_url}/assistant/message",
            json={"message": "현재 상태 알려줘", "project_root": project_root, "mode": "status"},
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
        "--include-assistant-bridge",
        action="store_true",
        help="Run the document RAG smoke flow and then the assistant/project API bridge smoke flow.",
    )
    args = parser.parse_args()
    if args.assistant_bridge_only:
        result = run_assistant_bridge_smoke_test(args.base_url, project_root=args.project_root)
    else:
        result = run_smoke_test(args.base_url)
        if args.include_assistant_bridge:
            result["assistant_bridge"] = run_assistant_bridge_smoke_test(args.base_url, project_root=args.project_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
