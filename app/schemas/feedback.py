from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    request_id: str
    rating: Literal["good", "bad", "neutral"]
    corrected_answer: str | None = None
    note: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: int
    chat_log_id: int
    rating: str


class FeedbackSummary(BaseModel):
    id: int
    chat_log_id: int
    rating: str
    corrected_answer_preview: str | None
    note_preview: str | None
    created_at: str


class FeedbackListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    rating: str | None = None
    chat_log_id: int | None = None
    items: list[FeedbackSummary]
