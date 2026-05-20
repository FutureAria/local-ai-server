from fastapi import APIRouter

from app.services.project_status_service import get_project_status

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
