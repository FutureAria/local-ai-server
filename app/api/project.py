from fastapi import APIRouter, Depends

from app.api.dependencies import require_api_key
from app.schemas.project import ShellDryRunRequest
from app.services.project_status_service import dry_run_shell_command, get_project_status, get_shell_policy

router = APIRouter(prefix="/project", tags=["project"])


@router.get("/status")
def project_status() -> dict:
    return get_project_status()


@router.get("/next")
def project_next() -> dict:
    status = get_project_status()
    return {
        "current_phase": status["current_phase"],
        "safe_next_tasks": status["safe_next_tasks"],
        "blocked_until_review": status["blocked_until_review"],
        "recommended_next_model": status["recommended_next_model"],
    }


@router.get("/shell-policy", dependencies=[Depends(require_api_key)])
def shell_policy() -> dict:
    return get_shell_policy()


@router.post("/shell-dry-run", dependencies=[Depends(require_api_key)])
def shell_dry_run(request: ShellDryRunRequest) -> dict:
    return dry_run_shell_command(request.command)
