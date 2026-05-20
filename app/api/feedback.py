from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_feedback_service, require_api_key
from app.db.database import get_db
from app.schemas.feedback import FeedbackListResponse, FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(tags=["feedback"])


@router.get("/feedback", response_model=FeedbackListResponse)
def list_feedback(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    rating: Literal["good", "bad", "neutral"] | None = None,
    chat_log_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    feedback_service: FeedbackService = Depends(get_feedback_service),
) -> dict:
    return feedback_service.list_feedback(
        db=db,
        limit=limit,
        offset=offset,
        rating=rating,
        chat_log_id=chat_log_id,
    )


@router.post("/feedback", response_model=FeedbackResponse, dependencies=[Depends(require_api_key)])
def create_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    feedback_service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackResponse:
    try:
        feedback = feedback_service.create_feedback(
            db=db,
            request_id=request.request_id,
            rating=request.rating,
            corrected_answer=request.corrected_answer,
            note=request.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FeedbackResponse(
        feedback_id=feedback.id,
        chat_log_id=feedback.chat_log_id,
        rating=feedback.rating,
    )
