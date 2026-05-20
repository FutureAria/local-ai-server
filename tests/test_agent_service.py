from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.db.database import Base
from app.db.models import AgentRun
from app.services.agent_service import AgentService


def test_agent_service_creates_high_risk_preview_plan_for_browser_and_file(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=False))

    with TestingSessionLocal() as db:
        run = service.create_plan(db, "github 웹 페이지 열고 내 폴더도 열어줘")

        assert run.id is not None
        assert run.risk_level == "high"
        assert run.execution_enabled == 0
        response = service.to_response(run)
        assert response["status"] == "planned"
        assert response["execution_enabled"] is False
        assert {action["tool"] for action in response["actions"]} == {"browser", "file"}
        assert all(action["requires_approval"] for action in response["actions"])
        assert db.scalar(select(AgentRun.id)) == run.id


def test_agent_service_creates_low_risk_rag_plan_for_plain_question(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings())

    with TestingSessionLocal() as db:
        run = service.create_plan(db, "JWT 인증 흐름 설명해줘")
        response = service.to_response(run)

        assert response["risk_level"] == "low"
        assert response["actions"][0]["tool"] == "rag"
        assert response["actions"][0]["requires_approval"] is False


def test_agent_service_approve_and_reject_state_transitions(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings())

    with TestingSessionLocal() as db:
        approve_run = service.create_plan(db, "웹 열어줘")
        reject_run = service.create_plan(db, "파일 열어줘")

        approved = service.approve_run(db, approve_run.id)
        rejected = service.reject_run(db, reject_run.id)

        assert approved is not None
        assert approved.status == "approved_pending_execution"
        assert approved.execution_enabled == 0
        assert rejected is not None
        assert rejected.status == "rejected"
