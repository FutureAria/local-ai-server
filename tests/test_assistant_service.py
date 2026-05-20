from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.db import models  # noqa: F401
from app.db.database import Base
from app.db.models import AssistantMessage
from app.services.assistant_service import AssistantService


class DummyService:
    pass


def test_list_sessions_returns_last_message_preview(tmp_path) -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = session_local()
    service = AssistantService(
        settings=Settings(
            CHROMA_PATH=str(tmp_path / "chroma"),
            UPLOAD_DIR=str(tmp_path / "uploads"),
            LOCAL_API_KEY=None,
        ),
        rag_service=DummyService(),
        search_service=DummyService(),
        document_service=DummyService(),
        agent_service=DummyService(),
    )

    try:
        assistant_session = service.create_session(
            db,
            title="Demo",
            project_root=str(tmp_path),
        )
        db.add(
            AssistantMessage(
                session_id=assistant_session.id,
                role="user",
                content="  첫번째   줄\n두번째 줄  ",
                message_type="input",
            )
        )
        db.commit()

        result = service.list_sessions(db, limit=5, offset=0)

        assert result["sessions"][0]["session_id"] == assistant_session.id
        assert result["sessions"][0]["messages_count"] == 1
        assert result["sessions"][0]["last_message_preview"] == "첫번째 줄 두번째 줄"
    finally:
        db.close()
