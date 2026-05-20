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
            "endpoints": {
                "ping": "GET /assistant/ping",
                "config": "GET /assistant/config",
                "dashboard": "GET /assistant/dashboard",
                "action_preview": "POST /assistant/action-preview",
                "message": "POST /assistant/message",
            },
        }

    def action_preview(self, request):
        intent = request.mode if request.mode != "auto" else "agent_plan"
        return {
            "intent": intent,
            "recommended_endpoint": "POST /assistant/message",
            "would_execute": False,
            "requires_approval": intent == "agent_plan",
            "risk_level": "high" if intent == "agent_plan" else "low",
            "needs": [],
            "safety": {"shell_execution": "disabled"},
            "ui": {"response_type": "action_preview", "severity": "warning", "primary_text": intent, "display": "panel"},
        }

    def ping(self):
        return {
            "status": "ok",
            "service": "local-ai-server",
            "protected": True,
            "local_only": True,
            "ui_ready": True,
        }

    def config(self):
        return {
            "service": "local-ai-server",
            "protected": True,
            "local_only": True,
            "cors_origins": ["http://127.0.0.1:5173"],
            "allowed_roots": [{"path": "/tmp/project", "exists": True, "is_dir": True}],
            "models": {"llm_provider": "ollama-local", "llm_model": "llama3.2", "embedding_model": "nomic-embed-text"},
            "storage": {"database": "sqlite-local", "vector_store": "chroma-local"},
            "safety": {"shell_execution": "disabled"},
            "rate_limit": {"enabled": True, "per_minute": 120},
        }

    def status(self, db):
        return {
            "service": "local-ai-server",
            "current_phase": {"phase": 12, "title": "Live browser UI QA", "status": "next", "summary": "qa"},
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

    def dashboard(self, db):
        return {
            "service": "local-ai-server",
            "current_phase": self.status(db)["current_phase"],
            "cards": {
                "documents": self.status(db)["documents"],
                "integrity": self.status(db)["integrity"],
                "sessions": self.status(db)["sessions"],
                "connection": {"status": "ready", "protected": True, "local_only": True},
            },
            "recent_sessions": self.list_sessions(db, limit=5, offset=0)["sessions"],
            "safety": {"shell_execution": "disabled"},
            "ui": {"ready": True, "badge": "DASHBOARD READY"},
        }

    def bootstrap(self, db, project_root=None, include_sessions=True, sessions_limit=10):
        return {
            "service": "local-ai-server",
            "capabilities": self.capabilities(),
            "status": self.status(db),
            "project_root": {
                "project_root": project_root,
                "resolved_path": project_root,
                "safe_for_read_only_agent": True,
            }
            if project_root
            else None,
            "sessions": self.list_sessions(db, limit=sessions_limit, offset=0) if include_sessions else None,
            "recommended_calls": [
                {"method": "POST", "path": "/assistant/message", "when": "user sends a message"}
            ],
            "ui": {
                "ready": True,
                "badge": "LOCAL API READY",
                "message": "로컬 assistant API가 준비되었습니다.",
                "blocked_actions": ["shell_execution", "browser_interaction"],
            },
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

    def _session(self):
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

    def get_session(self, db, session_id: str):
        if session_id != "session-1":
            return None
        return self._session()

    def list_session_messages(self, db, session_id: str, limit: int = 50, offset: int = 0):
        if session_id != "session-1":
            return None
        messages = self._session().messages[offset : offset + limit]
        return {
            "session_id": session_id,
            "total_messages": 1,
            "limit": limit,
            "offset": offset,
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "message_type": message.message_type,
                    "payload": None,
                    "created_at": message.created_at,
                }
                for message in messages
            ],
        }

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
            "ui": {"response_type": "answer", "severity": "info", "primary_text": "assistant", "display": "message"},
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


def test_assistant_action_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/action-preview", json={"message": "브라우저 열어줘", "mode": "auto"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "agent_plan"
    assert body["would_execute"] is False
    assert body["requires_approval"] is True
    assert body["ui"]["response_type"] == "action_preview"


def test_assistant_ping_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/ping")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ui_ready"] is True


def test_assistant_config_endpoint_with_mock_does_not_return_secret() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/config")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["protected"] is True
    assert "local_api_key" not in body
    assert body["allowed_roots"][0]["exists"] is True


def test_assistant_status_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/status")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["documents"]["documents_count"] == 1
    assert body["sessions"]["messages_count"] == 2


def test_assistant_dashboard_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/dashboard")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["cards"]["connection"]["status"] == "ready"
    assert body["recent_sessions"][0]["session_id"] == "session-1"
    assert body["ui"]["ready"] is True


def test_assistant_bootstrap_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/bootstrap",
        json={"project_root": "/tmp/project", "include_sessions": True, "sessions_limit": 5},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["capabilities"]["endpoints"]["message"] == "POST /assistant/message"
    assert body["status"]["current_phase"]["phase"] == 12
    assert body["project_root"]["safe_for_read_only_agent"] is True
    assert body["sessions"]["limit"] == 5
    assert body["ui"]["ready"] is True


def test_assistant_session_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    create_response = client.post(
        "/assistant/sessions",
        json={"title": "Demo", "project_root": "/tmp/project"},
    )
    list_response = client.get("/assistant/sessions?limit=5&offset=0")
    get_response = client.get("/assistant/sessions/session-1")
    messages_response = client.get("/assistant/sessions/session-1/messages?limit=10&offset=0")
    missing_response = client.get("/assistant/sessions/missing")
    missing_messages_response = client.get("/assistant/sessions/missing/messages")

    app.dependency_overrides.clear()
    assert create_response.status_code == 200
    assert create_response.json()["session_id"] == "session-1"
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["messages_count"] == 1
    assert get_response.status_code == 200
    assert get_response.json()["messages"][0]["content"] == "JWT"
    assert messages_response.status_code == 200
    assert messages_response.json()["total_messages"] == 1
    assert messages_response.json()["messages"][0]["content"] == "JWT"
    assert missing_response.status_code == 404
    assert missing_messages_response.status_code == 404


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
    assert body["ui"]["response_type"] == "answer"


def test_assistant_project_root_validate_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/project-root/validate", json={"project_root": "/tmp/project"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["safe_for_read_only_agent"] is True
