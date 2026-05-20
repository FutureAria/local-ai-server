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
        "status": "done",
        "summary": "Assistant session summary, allowed root onboarding, shell dry-run policy, REPL status helpers, and docs alignment.",
    },
    {
        "phase": 5,
        "title": "UI Bridge Assistant API",
        "status": "done",
        "summary": "Assistant capabilities, sessions, message router, project-root validation, and CLI bridge commands.",
    },
    {
        "phase": 6,
        "title": "Browser UI integration support",
        "status": "done",
        "summary": "Local CORS defaults and assistant session list API for browser UI integration.",
    },
    {
        "phase": 7,
        "title": "UI dashboard status API",
        "status": "done",
        "summary": "Assistant status endpoint for document, integrity, session, and safety dashboard data.",
    },
    {
        "phase": 8,
        "title": "UI bootstrap contract",
        "status": "done",
        "summary": "Assistant bootstrap endpoint and CLI command for browser UI startup contract.",
    },
    {
        "phase": 9,
        "title": "UI readiness helper APIs",
        "status": "done",
        "summary": "Assistant ping, config, and dashboard endpoints for local browser UI connection checks.",
    },
    {
        "phase": 10,
        "title": "Assistant message paging",
        "status": "done",
        "summary": "Read-only paged assistant session messages endpoint and CLI command for UI history rendering.",
    },
    {
        "phase": 11,
        "title": "Assistant action preview",
        "status": "done",
        "summary": "Read-only intent preview endpoint and CLI command for UI preflight rendering.",
    },
    {
        "phase": 12,
        "title": "Assistant UI contract",
        "status": "done",
        "summary": "Read-only UI contract endpoint and CLI command for startup and message flow integration.",
    },
    {
        "phase": 13,
        "title": "Assistant startup snapshot",
        "status": "done",
        "summary": "Read-only startup snapshot endpoint and CLI command for one-call browser UI initialization.",
    },
    {
        "phase": 14,
        "title": "Project API inventory",
        "status": "done",
        "summary": "Read-only API inventory endpoint and CLI command for backend/UI integration checks.",
    },
    {
        "phase": 15,
        "title": "Live browser UI QA",
        "status": "next",
        "summary": "Exercise the connected browser UI against the local assistant API and refine rendering details.",
    },
]

SAFE_NEXT_TASKS = [
    "Call GET /assistant/startup from the browser UI to hydrate ping/config/dashboard/ui-contract in one request.",
    "Use GET /project/api-inventory to confirm endpoint groups and API-key boundaries before wiring a client.",
    "Use GET /assistant/ui-contract as the browser UI integration checklist.",
    "Use POST /assistant/action-preview before sending messages that may become agent or shell dry-run requests.",
    "Use GET /assistant/sessions/{session_id}/messages for paged chat history rendering.",
    "Call GET /assistant/ping, GET /assistant/config, and GET /assistant/dashboard from the browser UI.",
    "Call POST /assistant/bootstrap from the browser UI startup flow and confirm token/project-root/session rendering.",
    "Send a real browser UI message to POST /assistant/message and confirm CORS/auth/response rendering.",
    "Load GET /assistant/status in the UI and confirm dashboard rendering.",
    "Check GET /assistant/sessions in the UI after a few messages.",
    "Run upload/search/ask-with-docs against a real local .md or .txt note.",
    "Review SQLite/Chroma status with local-ai stats and local-ai integrity.",
    "Keep shell/file-write/browser-interaction/deploy/fine-tuning in blocked or review-required status.",
]

BLOCKED_UNTIL_REVIEW = [
    "Unrestricted shell execution",
    "File write/delete/patch apply",
    "Browser click/fill/submit/login interaction",
    "Deployment or cloud resource changes",
    "Automatic fine-tuning runs",
]

SHELL_DRY_RUN_ALLOWED_COMMANDS = {
    "pwd": "현재 작업 디렉터리 확인",
    "ls": "파일/폴더 목록 조회",
    "rg": "텍스트 검색",
    "cat": "텍스트 파일 출력",
    "pytest": "테스트 실행",
    "python -m pytest": "테스트 실행",
    "git status": "Git 상태 확인",
    "git log": "Git 로그 조회",
}

SHELL_DRY_RUN_BLOCKED_TOKENS = {
    "rm",
    "rmdir",
    "mv",
    "cp",
    "sudo",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    "scp",
    "rsync",
    "pip install",
    "brew install",
    "git reset",
    "git clean",
    "git push",
}


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


def get_shell_policy() -> dict:
    return {
        "mode": "dry-run-only",
        "allowed_commands": [
            {"command": command, "reason": reason}
            for command, reason in SHELL_DRY_RUN_ALLOWED_COMMANDS.items()
        ],
        "blocked_tokens": sorted(SHELL_DRY_RUN_BLOCKED_TOKENS),
        "note": "이 정책은 실제 shell 실행이 아니라 실행 전 판단만 제공합니다.",
    }


def build_api_inventory(routes: list) -> dict:
    endpoints = []
    for route in routes:
        path = getattr(route, "path", "")
        methods = sorted(method for method in getattr(route, "methods", set()) if method not in {"HEAD", "OPTIONS"})
        if not path.startswith("/") or not methods:
            continue
        if path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
            continue

        dependencies = getattr(getattr(route, "dependant", None), "dependencies", [])
        requires_api_key = any(getattr(dependency.call, "__name__", "") == "require_api_key" for dependency in dependencies)
        tags = list(getattr(route, "tags", []) or [])
        endpoints.append(
            {
                "path": path,
                "methods": methods,
                "tags": tags,
                "name": getattr(route, "name", ""),
                "requires_api_key": requires_api_key,
            }
        )

    endpoints.sort(key=lambda item: (item["path"], item["methods"]))
    protected_count = sum(1 for endpoint in endpoints if endpoint["requires_api_key"])
    return {
        "service": "local-ai-server",
        "mode": "read-only",
        "local_only": True,
        "endpoints_count": len(endpoints),
        "protected_endpoints_count": protected_count,
        "public_endpoints_count": len(endpoints) - protected_count,
        "endpoints": endpoints,
        "safety": {
            "external_llm_api": "disabled",
            "shell_execution": "dry-run-only",
            "browser_interaction": "disabled",
            "file_write_delete": "disabled",
        },
    }


def dry_run_shell_command(command: str) -> dict:
    normalized = " ".join(command.strip().split())
    if not normalized:
        return {
            "command": command,
            "status": "blocked",
            "would_execute": False,
            "reason": "빈 명령은 실행할 수 없습니다.",
        }

    lowered = normalized.lower()
    for token in SHELL_DRY_RUN_BLOCKED_TOKENS:
        if token in lowered:
            return {
                "command": normalized,
                "status": "blocked",
                "would_execute": False,
                "reason": f"고위험 token이 포함되어 shell dry-run 정책에서 차단됩니다: {token}",
            }

    matched = _matched_allowed_command(lowered)
    if matched is None:
        return {
            "command": normalized,
            "status": "blocked",
            "would_execute": False,
            "reason": "allowlist에 없는 명령입니다. 실제 실행 엔진 연결 전에는 허용하지 않습니다.",
        }

    return {
        "command": normalized,
        "status": "allowed_preview",
        "would_execute": False,
        "matched_policy": matched,
        "reason": "allowlist 후보입니다. 현재 단계에서는 실제 실행하지 않고 preview만 제공합니다.",
    }


def _matched_allowed_command(lowered: str) -> str | None:
    for command in sorted(SHELL_DRY_RUN_ALLOWED_COMMANDS, key=len, reverse=True):
        if lowered == command or lowered.startswith(f"{command} "):
            return command
    return None
