PROJECT_PHASES = [
    {
        "phase": 1,
        "title": "FastAPI local RAG server",
        "status": "done",
        "summary": "Ollama, SQLite, Chroma, document upload/index/search/RAG, feedback, SFT export.",
    },
    {
        "phase": 2,
        "title": "CLI and document assistant",
        "status": "done",
        "summary": "local-ai assist, assistant REPL, API-backed CLI commands, document/folder workflows.",
    },
    {
        "phase": 3,
        "title": "Agent safety and read-only execution",
        "status": "done",
        "summary": "Agent plan, dry-run, approval, action status, read-only file/folder/URL execution.",
    },
    {
        "phase": 4,
        "title": "Safer automation loop",
        "status": "next",
        "summary": "Continue security, API, CLI, and assistant polish without enabling dangerous execution by default.",
    },
]

SAFE_NEXT_TASKS = [
    "Add assistant session summaries and better command help.",
    "Add local folder onboarding checklist for allowed roots and indexing.",
    "Add read-only shell dry-run policy before any shell execution is enabled.",
    "Add more tests for assistant REPL flows and error messages.",
    "Keep documentation and SECURITY.md aligned with actual behavior.",
]

BLOCKED_UNTIL_REVIEW = [
    "Unrestricted shell execution",
    "File write/delete/patch apply",
    "Browser click/fill/submit/login interaction",
    "Deployment or cloud resource changes",
    "Automatic fine-tuning runs",
]


def get_project_status() -> dict:
    completed = [phase for phase in PROJECT_PHASES if phase["status"] == "done"]
    current = next((phase for phase in PROJECT_PHASES if phase["status"] == "next"), PROJECT_PHASES[-1])
    return {
        "project": "local-ai-server",
        "current_phase": current,
        "completed_phases": completed,
        "safe_next_tasks": SAFE_NEXT_TASKS,
        "blocked_until_review": BLOCKED_UNTIL_REVIEW,
        "recommended_next_model": {
            "recommended_ai": "Codex",
            "recommended_model": "Codex GPT-5.5",
            "reason": "남은 안전 작업은 API/CLI/문서/테스트 중심이라 Codex가 직접 구현 가능.",
            "next_task": SAFE_NEXT_TASKS[0],
            "user_action_required": "없음. 단, shell/file-write/browser-interaction/deploy/fine-tuning 실행은 별도 승인 필요.",
        },
    }
