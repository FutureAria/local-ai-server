from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_assistant_service, require_api_key
from app.db.database import get_db
from app.schemas.assistant import (
    AssistantCapabilitiesResponse,
    AssistantBootstrapRequest,
    AssistantBootstrapResponse,
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantSessionCreateRequest,
    AssistantSessionListResponse,
    AssistantSessionResponse,
    AssistantStatusResponse,
    ProjectRootValidateRequest,
    ProjectRootValidateResponse,
)
from app.services.assistant_service import AssistantService, session_to_response
from app.services.document_loader import DocumentLoaderError
from app.services.ollama_client import OllamaError

router = APIRouter(prefix="/assistant", tags=["assistant"], dependencies=[Depends(require_api_key)])


@router.get("/capabilities", response_model=AssistantCapabilitiesResponse)
def assistant_capabilities(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.capabilities()


@router.get("/status", response_model=AssistantStatusResponse)
def assistant_status(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.status(db)


@router.post("/bootstrap", response_model=AssistantBootstrapResponse)
def assistant_bootstrap(
    request: AssistantBootstrapRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.bootstrap(
        db,
        project_root=request.project_root,
        include_sessions=request.include_sessions,
        sessions_limit=request.sessions_limit,
    )


@router.post("/sessions", response_model=AssistantSessionResponse)
def create_assistant_session(
    request: AssistantSessionCreateRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    session = assistant_service.create_session(db, title=request.title, project_root=request.project_root)
    return session_to_response(session)


@router.get("/sessions", response_model=AssistantSessionListResponse)
def list_assistant_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.list_sessions(db, limit=limit, offset=offset)


@router.get("/sessions/{session_id}", response_model=AssistantSessionResponse)
def get_assistant_session(
    session_id: str,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    session = assistant_service.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assistant session을 찾을 수 없습니다.")
    return session_to_response(session)


@router.post("/message", response_model=AssistantMessageResponse)
async def assistant_message(
    request: AssistantMessageRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    try:
        return await assistant_service.handle_message(db, request)
    except DocumentLoaderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/project-root/validate", response_model=ProjectRootValidateResponse)
def validate_project_root(
    request: ProjectRootValidateRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.validate_project_root(request)
