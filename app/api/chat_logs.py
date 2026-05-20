from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat_logs import ChatLogDetail, ChatLogListResponse
from app.services.chat_log_service import ChatLogService

router = APIRouter(prefix="/chat-logs", tags=["chat-logs"])


def get_chat_log_service() -> ChatLogService:
    return ChatLogService()


@router.get("", response_model=ChatLogListResponse)
def list_chat_logs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    mode: str | None = Query(default=None, pattern="^(direct|rag)$"),
    query: str | None = Query(default=None, min_length=1, max_length=200),
    db: Session = Depends(get_db),
    chat_log_service: ChatLogService = Depends(get_chat_log_service),
) -> dict:
    return chat_log_service.list_chat_logs(db, limit=limit, offset=offset, mode=mode, query=query)


@router.get("/{chat_log_id}", response_model=ChatLogDetail)
def get_chat_log(
    chat_log_id: int,
    db: Session = Depends(get_db),
    chat_log_service: ChatLogService = Depends(get_chat_log_service),
) -> dict:
    chat_log = chat_log_service.get_chat_log(db, chat_log_id)
    if chat_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="채팅 로그를 찾을 수 없습니다.")
    return chat_log
