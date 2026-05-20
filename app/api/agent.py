from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_agent_service, require_api_key
from app.db.database import get_db
from app.schemas.agent import AgentPlanRequest, AgentPlanResponse, AgentRunDetail, AgentRunSummary
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/plan", response_model=AgentPlanResponse, dependencies=[Depends(require_api_key)])
def create_agent_plan(
    request: AgentPlanRequest,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> dict:
    run = agent_service.create_plan(db, request.instruction)
    return agent_service.to_response(run)


@router.get("/runs", response_model=list[AgentRunSummary], dependencies=[Depends(require_api_key)])
def list_agent_runs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> list[dict]:
    return [agent_service.to_summary(run) for run in agent_service.list_runs(db, limit=limit, offset=offset)]


@router.get("/runs/{run_id}", response_model=AgentRunDetail, dependencies=[Depends(require_api_key)])
def get_agent_run(
    run_id: int,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> dict:
    run = agent_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent run을 찾을 수 없습니다.")
    return agent_service.to_detail(run)


@router.post("/runs/{run_id}/approve", response_model=AgentRunDetail, dependencies=[Depends(require_api_key)])
def approve_agent_run(
    run_id: int,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> dict:
    try:
        run = agent_service.approve_run(db, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent run을 찾을 수 없습니다.")
    return agent_service.to_detail(run)


@router.post("/runs/{run_id}/reject", response_model=AgentRunDetail, dependencies=[Depends(require_api_key)])
def reject_agent_run(
    run_id: int,
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> dict:
    try:
        run = agent_service.reject_run(db, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent run을 찾을 수 없습니다.")
    return agent_service.to_detail(run)
