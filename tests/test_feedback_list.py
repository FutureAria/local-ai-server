from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.dependencies import get_feedback_service
from app.main import app
from app.services.feedback_service import FeedbackService


class FakeFeedbackService:
    def list_feedback(self, db, limit: int, offset: int, rating=None, chat_log_id=None):
        return {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "rating": rating,
            "chat_log_id": chat_log_id,
            "items": [
                {
                    "id": 1,
                    "chat_log_id": 9,
                    "rating": rating or "good",
                    "corrected_answer_preview": "corrected",
                    "note_preview": "note",
                    "created_at": "2026-05-20T00:00:00",
                }
            ],
        }


def test_feedback_list_endpoint_contract() -> None:
    app.dependency_overrides[get_feedback_service] = lambda: FakeFeedbackService()
    client = TestClient(app)
    response = client.get("/feedback?limit=10&offset=0&rating=good&chat_log_id=9")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["rating"] == "good"
    assert body["chat_log_id"] == 9
    assert body["items"][0]["corrected_answer_preview"] == "corrected"


def test_feedback_service_preview_truncates() -> None:
    service = FeedbackService()
    value = "x" * 200
    preview = service._preview(value)
    assert preview is not None
    assert preview.endswith("...")
    assert len(preview) == 160
