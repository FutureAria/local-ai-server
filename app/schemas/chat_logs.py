from datetime import datetime

from pydantic import BaseModel


class ChatLogSummary(BaseModel):
    id: int
    question_preview: str
    answer_preview: str
    mode: str
    model: str
    used_sources_count: int
    created_at: datetime


class ChatLogListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    mode: str | None = None
    query: str | None = None
    items: list[ChatLogSummary]


class ChatLogDetail(BaseModel):
    id: int
    question: str
    answer: str
    mode: str
    model: str
    used_sources: list[dict]
    created_at: datetime
