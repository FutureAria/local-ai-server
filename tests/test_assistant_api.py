from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_assistant_service
from app.main import app


NOW = datetime(2026, 5, 20, tzinfo=UTC)


class FakeAssistantService:
    def capabilities(self) -> dict:
        return {
            "service": "local-ai-server",
            "modes": ["auto", "ask_with_docs", "search"],
            "protected": True,
            "local_only": True,
            "llm_provider": "ollama-local",
            "vector_store": "chroma-local",
            "storage": "sqlite-local",
            "safe_defaults": {"shell_execution": "disabled"},
            "endpoints": {"message": "POST /assistant/message"},
        }

    def status(self, db):
        return {
            "service": "local-ai-server",
            "current_phase": {"phase": 7, "title": "Live browser UI QA", "status": "next", "summary": "qa"},
            "documents": {
                "documents_count": 1,
                "chunks_count": 2,
                "chroma_vectors_count": 2,
                "missing_stored_files_count": 0,
            },
            "integrity": {
                "status": "ok",
                "chunks_missing_vectors_count": 0,
                "orphan_vectors_count": 0,
                "repair_available": False,
            },
            "sessions": {"sessions_count": 1, "messages_count": 2},
            "safety": {"shell_execution": "disabled"},
        }

    def create_session(self, db, title=None, project_root=None):
        return SimpleNamespace(
            id="session-1",
            title=title or "New local assistant session",
            project_root=project_root,
            created_at=NOW,
            updated_at=NOW,
            messages=[],
        )

    def list_sessions(self, db, limit: int = 20, offset: int = 0):
        return {
            "sessions": [
                {
                    "session_id": "session-1",
                    "title": "Demo",
                    "project_root": "/tmp/project",
                    "created_at": NOW,
                    "updated_at": NOW,
                    "messages_count": 1,
                    "last_message_preview": "JWT",
                }
            ],
            "limit": limit,
            "offset": offset,
        }

    def get_session(self, db, session_id: str):
        if session_id != "session-1":
            return None
        return SimpleNamespace(
            id="session-1",
            title="Demo",
            project_root="/tmp/project",
            created_at=NOW,
            updated_at=NOW,
            messages=[
                SimpleNamespace(
                    id=1,
                    role="user",
                    content="JWT",
                    message_type="input",
                    payload_json=None,
                    created_at=NOW,
                )
            ],
        )

    async def handle_message(self, db, request):
        return {
            "session_id": request.session_id or "session-1",
            "type": "answer",
            "answer": f"assistant: {request.message}",
            "used_documents": True,
            "sources": [{"document_id": 1, "filename": "note.md", "chunk_index": 0, "chunk_id": 3}],
            "request_id": "123",
            "safety": {
                "shell_execution": "disabled",
                "browser_interaction": "blocked",
                "file_write_delete": "blocked",
            },
        }

    def validate_project_root(self, request):
        return {
            "project_root": request.project_root,
            "resolved_path": request.project_root,
            "exists": True,
            "is_dir": True,
            "inside_allowed_roots": True,
            "allowed_roots": [request.project_root],
            "safe_for_read_only_agent": True,
            "message": "read-only agent root로 사용할 수 있습니다.",
        }


def test_assistant_capabilities_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/capabilities")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["llm_provider"] == "ollama-local"
    assert response.json()["safe_defaults"]["shell_execution"] == "disabled"


def test_assistant_status_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/status")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["documents"]["documents_count"] == 1
    assert body["sessions"]["messages_count"] == 2


def test_assistant_session_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    create_response = client.post(
        "/assistant/sessions",
        json={"title": "Demo", "project_root": "/tmp/project"},
    )
    list_response = client.get("/assistant/sessions?limit=5&offset=0")
    get_response = client.get("/assistant/sessions/session-1")
    missing_response = client.get("/assistant/sessions/missing")

    app.dependency_overrides.clear()
    assert create_response.status_code == 200
    assert create_response.json()["session_id"] == "session-1"
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["messages_count"] == 1
    assert get_response.status_code == 200
    assert get_response.json()["messages"][0]["content"] == "JWT"
    assert missing_response.status_code == 404


def test_assistant_message_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/message",
        json={"message": "JWT 설명해줘", "session_id": "session-1", "mode": "auto"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "answer"
    assert body["used_documents"] is True
    assert body["sources"][0]["chunk_id"] == 3
    assert body["safety"]["shell_execution"] == "disabled"


def test_assistant_project_root_validate_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/project-root/validate", json={"project_root": "/tmp/project"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["safe_for_read_only_agent"] is True
