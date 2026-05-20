from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import ChatLog, Feedback
from scripts import export_sft_data as export_module


def test_export_sft_data_writes_corrected_answers(tmp_path: Path, monkeypatch) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        chat_log = ChatLog(
            question="JWT가 뭐야?",
            answer="old answer",
            mode="direct",
            model="llama3.2",
            used_sources_json=None,
        )
        db.add(chat_log)
        db.flush()
        db.add(
            Feedback(
                chat_log_id=chat_log.id,
                rating="bad",
                corrected_answer="JWT는 인증 토큰 형식이다.",
                note="수정",
            )
        )
        db.commit()

    monkeypatch.setattr(export_module, "init_db", lambda: None)
    monkeypatch.setattr(export_module, "SessionLocal", TestingSessionLocal)

    output = tmp_path / "sft.jsonl"
    count = export_module.export_sft_data(output)

    assert count == 1
    content = output.read_text(encoding="utf-8")
    assert "JWT는 인증 토큰 형식이다." in content
