from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_assistant_service, require_api_key
from app.db.database import get_db
from app.schemas.assistant import (
    AssistantCapabilitiesResponse,
    AssistantActionPreviewRequest,
    AssistantActionPreviewResponse,
    AssistantBootstrapRequest,
    AssistantBootstrapResponse,
    AssistantConfigResponse,
    AssistantDashboardResponse,
    AssistantMessageListResponse,
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantPingResponse,
    AssistantSessionCreateRequest,
    AssistantSessionListResponse,
    AssistantSessionResponse,
    AssistantStatusResponse,
    AssistantUiContractResponse,
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


@router.post("/action-preview", response_model=AssistantActionPreviewResponse)
def assistant_action_preview(
    request: AssistantActionPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_preview(request)


@router.get("/ui-contract", response_model=AssistantUiContractResponse)
def assistant_ui_contract(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.ui_contract()


@router.get("/ping", response_model=AssistantPingResponse)
def assistant_ping(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.ping()


@router.get("/config", response_model=AssistantConfigResponse)
def assistant_config(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.config()


@router.get("/status", response_model=AssistantStatusResponse)
def assistant_status(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.status(db)


@router.get("/dashboard", response_model=AssistantDashboardResponse)
def assistant_dashboard(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.dashboard(db)


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


@router.get("/sessions/{session_id}/messages", response_model=AssistantMessageListResponse)
def list_assistant_session_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    messages = assistant_service.list_session_messages(db, session_id, limit=limit, offset=offset)
    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assistant session을 찾을 수 없습니다.")
    return messages


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
