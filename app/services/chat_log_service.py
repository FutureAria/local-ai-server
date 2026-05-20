import json

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import ChatLog


class ChatLogService:
    def list_chat_logs(
        self,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        mode: str | None = None,
        query: str | None = None,
    ) -> dict:
        filters = []
        if mode:
            filters.append(ChatLog.mode == mode)
        if query:
            pattern = f"%{query}%"
            filters.append(or_(ChatLog.question.ilike(pattern), ChatLog.answer.ilike(pattern)))

        total_stmt = select(func.count(ChatLog.id))
        rows_stmt = select(ChatLog).order_by(ChatLog.created_at.desc()).limit(limit).offset(offset)
        if filters:
            total_stmt = total_stmt.where(*filters)
            rows_stmt = rows_stmt.where(*filters)

        total = db.scalar(total_stmt) or 0
        rows = db.execute(rows_stmt).scalars().all()
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "mode": mode,
            "query": query,
            "items": [self._summary(row) for row in rows],
        }

    def get_chat_log(self, db: Session, chat_log_id: int) -> dict | None:
        row = db.get(ChatLog, chat_log_id)
        if row is None:
            return None
        return {
            "id": row.id,
            "question": row.question,
            "answer": row.answer,
            "mode": row.mode,
            "model": row.model,
            "used_sources": self._sources(row.used_sources_json),
            "created_at": row.created_at,
        }

    def _summary(self, row: ChatLog) -> dict:
        sources = self._sources(row.used_sources_json)
        return {
            "id": row.id,
            "question_preview": self._preview(row.question),
            "answer_preview": self._preview(row.answer),
            "mode": row.mode,
            "model": row.model,
            "used_sources_count": len(sources),
            "created_at": row.created_at,
        }

    def _sources(self, raw_sources: str | None) -> list[dict]:
        if not raw_sources:
            return []
        try:
            parsed = json.loads(raw_sources)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []

    def _preview(self, value: str, max_length: int = 160) -> str:
        normalized = " ".join(value.split())
        if len(normalized) <= max_length:
            return normalized
        return normalized[: max_length - 3] + "..."
