from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.chat_logs import get_chat_log_service
from app.main import app
from app.services.chat_log_service import ChatLogService


class FakeChatLogService:
    def list_chat_logs(self, db, limit: int, offset: int, mode: str | None = None, query: str | None = None):
        return {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "mode": mode,
            "query": query,
            "items": [
                {
                    "id": 1,
                    "question_preview": "question",
                    "answer_preview": "answer",
                    "mode": "direct",
                    "model": "llama3.2",
                    "used_sources_count": 0,
                    "created_at": "2026-05-20T00:00:00",
                }
            ],
        }

    def get_chat_log(self, db, chat_log_id: int):
        return {
            "id": chat_log_id,
            "question": "question",
            "answer": "answer",
            "mode": "direct",
            "model": "llama3.2",
            "used_sources": [],
            "created_at": "2026-05-20T00:00:00",
        }


def test_chat_log_list_endpoint_contract() -> None:
    app.dependency_overrides[get_chat_log_service] = lambda: FakeChatLogService()
    client = TestClient(app)
    response = client.get("/chat-logs?limit=10&offset=0")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["question_preview"] == "question"


def test_chat_log_list_endpoint_accepts_filters() -> None:
    app.dependency_overrides[get_chat_log_service] = lambda: FakeChatLogService()
    client = TestClient(app)
    response = client.get("/chat-logs?limit=10&offset=0&mode=rag&query=JWT")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "rag"
    assert body["query"] == "JWT"


def test_chat_log_detail_endpoint_contract() -> None:
    app.dependency_overrides[get_chat_log_service] = lambda: FakeChatLogService()
    client = TestClient(app)
    response = client.get("/chat-logs/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["answer"] == "answer"


def test_chat_log_service_preview_truncates() -> None:
    service = ChatLogService()
    long_value = "x" * 200
    assert service._preview(long_value).endswith("...")
    assert len(service._preview(long_value)) == 160


def test_chat_log_service_sources_handles_invalid_json() -> None:
    assert ChatLogService()._sources("not-json") == []
