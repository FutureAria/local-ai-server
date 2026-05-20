import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_rag_service, require_api_key
from app.db.database import get_db
from app.schemas.ask import AskRequest, AskResponse, AskWithDocsRequest, AskWithDocsResponse, SourceReference
from app.services.ollama_client import OllamaError
from app.services.rag_service import RagService

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse, dependencies=[Depends(require_api_key)])
async def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    rag_service: RagService = Depends(get_rag_service),
) -> AskResponse:
    try:
        chat_log = await rag_service.ask(
            db=db,
            question=request.question,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
        )
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return AskResponse(
        answer=chat_log.answer,
        model=chat_log.model,
        used_documents=False,
        request_id=str(chat_log.id),
    )


@router.post("/ask-with-docs", response_model=AskWithDocsResponse, dependencies=[Depends(require_api_key)])
async def ask_with_docs(
    request: AskWithDocsRequest,
    db: Session = Depends(get_db),
    rag_service: RagService = Depends(get_rag_service),
) -> AskWithDocsResponse:
    try:
        chat_log = await rag_service.ask_with_docs(
            db=db,
            question=request.question,
            top_k=request.top_k,
            temperature=request.temperature,
        )
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    sources_data = json.loads(chat_log.used_sources_json or "[]")
    return AskWithDocsResponse(
        answer=chat_log.answer,
        model=chat_log.model,
        used_documents=True,
        sources=[SourceReference(**source) for source in sources_data],
        request_id=str(chat_log.id),
    )
