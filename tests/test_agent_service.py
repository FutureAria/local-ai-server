from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.db.database import Base
from app.db.models import AgentRun
import app.services.agent_service as agent_service_module
from app.services.agent_service import AgentService, _extract_html_summary


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


def test_agent_service_execute_blocks_when_execution_disabled(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=False))

    with TestingSessionLocal() as db:
        run = service.create_plan(db, "폴더 './' 열어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "blocked"
        assert detail["execution_results"][0]["status"] == "blocked"
        assert "AGENT_EXECUTION_ENABLED=false" in detail["execution_results"][0]["message"]


def test_agent_service_execute_lists_allowed_folder_read_only(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    (allowed / "note.md").write_text("# Note", encoding="utf-8")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"폴더 '{allowed}' 열어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "completed"
        assert detail["execution_results"][0]["status"] == "completed"
        assert detail["execution_results"][0]["items"] == [{"name": "note.md", "type": "file", "sensitive": False}]


def test_agent_service_execute_previews_allowed_text_file_read_only(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    note = allowed / "note.md"
    note.write_text("# Note\nJWT memo", encoding="utf-8")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"파일 '{note}' 읽어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        result = detail["execution_results"][0]
        assert executed.status == "completed"
        assert result["status"] == "completed"
        assert result["content_preview"] == "# Note\nJWT memo"
        assert result["line_count"] == 2


def test_agent_service_blocks_sensitive_file_preview(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    env_file = allowed / ".env"
    env_file.write_text("TOKEN=secret", encoding="utf-8")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"파일 '{env_file}' 읽어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "blocked"
        assert "민감 파일" in detail["execution_results"][0]["message"]


def test_agent_service_blocks_large_file_preview(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    large_file = allowed / "large.md"
    large_file.write_text("x" * 20, encoding="utf-8")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
            AGENT_FILE_PREVIEW_MAX_BYTES=10,
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"파일 '{large_file}' 읽어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "blocked"
        assert "AGENT_FILE_PREVIEW_MAX_BYTES" in detail["execution_results"][0]["message"]


def test_agent_service_execute_blocks_file_outside_allowed_root(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"폴더 '{outside}' 열어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "blocked"
        assert "허용된 root 밖" in detail["execution_results"][0]["message"]


def test_agent_service_execute_blocks_web_fetch_by_default(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=True, AGENT_WEB_FETCH_ENABLED=False))

    with TestingSessionLocal() as db:
        run = service.create_plan(db, "https://example.com 웹 페이지 열어줘")
        service.approve_run(db, run.id)
        executed = service.execute_run(db, run.id)
        detail = service.to_detail(executed)

        assert executed.status == "blocked"
        assert "AGENT_WEB_FETCH_ENABLED=false" in detail["execution_results"][0]["message"]


def test_agent_service_dry_run_records_policy_without_execution(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    note = allowed / "note.md"
    note.write_text("# Note\nsecret-looking text is not read in dry-run", encoding="utf-8")
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(
        settings=Settings(
            AGENT_EXECUTION_ENABLED=True,
            AGENT_ALLOWED_ROOTS=str(allowed),
        )
    )

    with TestingSessionLocal() as db:
        run = service.create_plan(db, f"파일 '{note}' 읽어줘")
        dry_run = service.dry_run(db, run.id)
        detail = service.to_detail(dry_run)
        actions = service.get_actions(db, run.id)

        result = detail["execution_results"]
        assert result == []
        assert actions[0]["status"] == "dry_run_allowed"
        assert actions[0]["dry_run_result"]["operation"] == "preview_file"
        assert actions[0]["dry_run_result"]["would_execute"] is False
        assert actions[0]["dry_run_result"]["execute_phase_would_run"] is True
        assert "content_preview" not in actions[0]["dry_run_result"]


def test_agent_service_dry_run_marks_shell_disabled(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=True))

    with TestingSessionLocal() as db:
        run = service.create_plan(db, "터미널 명령 실행해줘")
        dry_run = service.dry_run(db, run.id)
        actions = service.get_actions(db, dry_run.id)

        assert actions[0]["tool"] == "shell"
        assert actions[0]["status"] == "dry_run_disabled"
        assert actions[0]["dry_run_result"]["would_execute"] is False


def test_agent_html_summary_extracts_title_text_and_links() -> None:
    summary = _extract_html_summary(
        """
        <html>
          <head><title>Local Docs</title><script>ignore()</script></head>
          <body><h1>JWT</h1><p>Authentication flow</p><a href="/next">Next</a></body>
        </html>
        """,
        "https://example.com/base",
    )

    assert summary["title"] == "Local Docs"
    assert "JWT" in summary["text_preview"]
    assert "Authentication flow" in summary["text_preview"]
    assert summary["links"] == [{"url": "https://example.com/next", "text": ""}]


def test_agent_service_execute_blocks_private_web_fetch_host() -> None:
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=True, AGENT_WEB_FETCH_ENABLED=True))

    result = service._execute_web_action(
        {"tool": "web_search", "action": "fetch_url_preview", "target": "http://127.0.0.1:8000/private"}
    )

    assert result["status"] == "blocked"
    assert "private, loopback, link-local IP" in result["message"]


def test_agent_service_execute_blocks_redirect_to_private_host(monkeypatch) -> None:
    class FakeStreamResponse:
        status_code = 302
        headers = {"location": "http://127.0.0.1:8000/private"}
        url = "https://example.test/start"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def iter_bytes(self):
            return iter(())

    def fake_stream(*args, **kwargs) -> FakeStreamResponse:
        assert kwargs["follow_redirects"] is False
        return FakeStreamResponse()

    monkeypatch.setattr(
        agent_service_module,
        "_resolve_host_ips",
        lambda hostname: {"127.0.0.1"} if hostname == "127.0.0.1" else {"93.184.216.34"},
    )
    monkeypatch.setattr(agent_service_module.httpx, "stream", fake_stream)
    service = AgentService(settings=Settings(AGENT_EXECUTION_ENABLED=True, AGENT_WEB_FETCH_ENABLED=True))

    result = service._execute_web_action(
        {"tool": "web_search", "action": "fetch_url_preview", "target": "https://example.test/start"}
    )

    assert result["status"] == "blocked"
    assert "redirect target blocked" in result["message"]
    assert "private, loopback, link-local IP" in result["message"]
