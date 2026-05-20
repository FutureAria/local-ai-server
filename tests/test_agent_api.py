from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.dependencies import get_agent_service
from app.main import app


class FakeAgentService:
    def create_plan(self, db, instruction: str):
        return {"id": 1, "instruction": instruction}

    def to_response(self, run) -> dict:
        return {
            "run_id": 1,
            "status": "planned",
            "risk_level": "high",
            "execution_enabled": False,
            "actions": [
                {
                    "tool": "browser",
                    "action": "open_preview",
                    "target": run["instruction"],
                    "risk_level": "high",
                    "requires_approval": True,
                    "execution_enabled": False,
                    "reason": "preview only",
                }
            ],
            "note": "preview-only",
        }

    def list_runs(self, db, limit: int = 20, offset: int = 0):
        return [{"id": 1}]

    def to_summary(self, run) -> dict:
        return {
            "id": 1,
            "instruction_preview": "웹 열어줘",
            "status": "planned",
            "risk_level": "high",
            "execution_enabled": False,
            "created_at": datetime(2026, 5, 20, tzinfo=UTC),
        }

    def get_run(self, db, run_id: int):
        return {"id": run_id} if run_id == 1 else None

    def approve_run(self, db, run_id: int):
        return {"id": run_id, "status": "approved_pending_execution"} if run_id == 1 else None

    def reject_run(self, db, run_id: int):
        return {"id": run_id, "status": "rejected"} if run_id == 1 else None

    def execute_run(self, db, run_id: int):
        return {"id": run_id, "status": "blocked"} if run_id == 1 else None

    def to_detail(self, run) -> dict:
        return {
            **self.to_summary(run),
            "status": run.get("status", "planned"),
            "instruction": "웹 열어줘",
            "actions": [
                {
                    "tool": "browser",
                    "action": "open_preview",
                    "target": "웹 열어줘",
                    "risk_level": "high",
                    "requires_approval": True,
                    "execution_enabled": False,
                    "reason": "preview only",
                }
            ],
            "execution_results": [
                {
                    "tool": "browser",
                    "action": "open_preview",
                    "status": "blocked",
                    "message": "blocked",
                }
            ]
            if run.get("status") == "blocked"
            else [],
        }


def test_agent_plan_endpoint_returns_preview_plan_with_mock() -> None:
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()
    client = TestClient(app)

    response = client.post("/agent/plan", json={"instruction": "GitHub 웹 열어줘"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["execution_enabled"] is False
    assert body["actions"][0]["tool"] == "browser"
    assert body["actions"][0]["requires_approval"] is True


def test_agent_runs_endpoints_with_mock() -> None:
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()
    client = TestClient(app)

    list_response = client.get("/agent/runs")
    detail_response = client.get("/agent/runs/1")
    missing_response = client.get("/agent/runs/999")

    app.dependency_overrides.clear()
    assert list_response.status_code == 200
    assert list_response.json()[0]["status"] == "planned"
    assert detail_response.status_code == 200
    assert detail_response.json()["actions"][0]["action"] == "open_preview"
    assert missing_response.status_code == 404


def test_agent_approve_and_reject_endpoints_with_mock() -> None:
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()
    client = TestClient(app)

    approve_response = client.post("/agent/runs/1/approve")
    reject_response = client.post("/agent/runs/1/reject")
    missing_response = client.post("/agent/runs/999/approve")

    app.dependency_overrides.clear()
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved_pending_execution"
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"
    assert missing_response.status_code == 404


def test_agent_execute_endpoint_with_mock() -> None:
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()
    client = TestClient(app)

    response = client.post("/agent/runs/1/execute")
    missing_response = client.post("/agent/runs/999/execute")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"
    assert response.json()["execution_results"][0]["status"] == "blocked"
    assert missing_response.status_code == 404
