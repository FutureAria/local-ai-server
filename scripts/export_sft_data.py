import argparse
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, init_db
from app.db.models import ChatLog, Feedback


SYSTEM_PROMPT = "You are a helpful local AI assistant."


def export_sft_data(output: Path) -> int:
    init_db()
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with SessionLocal() as db:
        rows = _corrected_rows(db)
        with output.open("w", encoding="utf-8") as file:
            for chat_log, feedback in rows:
                record = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": chat_log.question},
                        {"role": "assistant", "content": feedback.corrected_answer},
                    ]
                }
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    return count


def _corrected_rows(db: Session) -> list[tuple[ChatLog, Feedback]]:
    stmt = (
        select(ChatLog, Feedback)
        .join(Feedback, Feedback.chat_log_id == ChatLog.id)
        .where(Feedback.corrected_answer.is_not(None))
        .order_by(Feedback.created_at.asc())
    )
    return list(db.execute(stmt).all())


def main() -> None:
    parser = argparse.ArgumentParser(description="Export corrected feedback as SFT JSONL.")
    parser.add_argument("--output", default="data/sft_dataset.jsonl")
    args = parser.parse_args()
    count = export_sft_data(Path(args.output))
    print(f"exported={count} output={args.output}")


if __name__ == "__main__":
    main()
