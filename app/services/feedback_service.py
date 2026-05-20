from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ChatLog, Feedback


class FeedbackService:
    def create_feedback(
        self,
        db: Session,
        request_id: str,
        rating: str,
        corrected_answer: str | None = None,
        note: str | None = None,
    ) -> Feedback:
        try:
            chat_log_id = int(request_id)
        except ValueError as exc:
            raise ValueError("request_id는 chat log id 문자열이어야 합니다.") from exc

        chat_log = db.get(ChatLog, chat_log_id)
        if chat_log is None:
            raise ValueError(f"request_id에 해당하는 chat log를 찾을 수 없습니다: {request_id}")

        feedback = Feedback(
            chat_log_id=chat_log.id,
            rating=rating,
            corrected_answer=corrected_answer,
            note=note,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    def list_feedback(
        self,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        rating: str | None = None,
        chat_log_id: int | None = None,
    ) -> dict:
        filters = []
        if rating:
            filters.append(Feedback.rating == rating)
        if chat_log_id is not None:
            filters.append(Feedback.chat_log_id == chat_log_id)

        total_stmt = select(func.count(Feedback.id))
        rows_stmt = select(Feedback).order_by(Feedback.created_at.desc()).limit(limit).offset(offset)
        if filters:
            total_stmt = total_stmt.where(*filters)
            rows_stmt = rows_stmt.where(*filters)

        total = db.scalar(total_stmt) or 0
        rows = db.execute(rows_stmt).scalars().all()
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "rating": rating,
            "chat_log_id": chat_log_id,
            "items": [self._summary(row) for row in rows],
        }

    def _summary(self, feedback: Feedback) -> dict:
        return {
            "id": feedback.id,
            "chat_log_id": feedback.chat_log_id,
            "rating": feedback.rating,
            "corrected_answer_preview": self._preview(feedback.corrected_answer),
            "note_preview": self._preview(feedback.note),
            "created_at": feedback.created_at.isoformat(),
        }

    def _preview(self, value: str | None, max_length: int = 160) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) <= max_length:
            return normalized
        return normalized[: max_length - 3] + "..."
