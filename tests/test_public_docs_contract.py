import re
from pathlib import Path

from typer.main import get_command

import cli.main as cli_main
from app.main import app
from app.services.project_status_service import build_api_inventory


DOCS = {
    "readme": Path("README.md"),
    "api": Path("docs/API.md"),
    "summary": Path("docs/PROJECT_SUMMARY.md"),
}

CORE_ENDPOINTS = [
    "GET /assistant/startup",
    "POST /assistant/bootstrap",
    "POST /assistant/action-preview",
    "POST /assistant/message",
    "GET /assistant/sessions/{session_id}/messages",
    "POST /ask-with-docs",
    "POST /documents/index-folder-preview",
    "GET /documents/vector-rebuild-preview",
    "GET /documents/integrity",
    "POST /agent/plan",
    "POST /project/shell-dry-run",
]

CORE_CLI_COMMANDS = [
    "local-ai assistant-startup",
    "local-ai assistant-bootstrap",
    "local-ai assistant-action-preview",
    "local-ai assistant-message",
    "local-ai assistant-messages",
    "local-ai ask-docs",
    "local-ai index-preview",
    "local-ai integrity",
    "local-ai vector-rebuild-preview",
    "local-ai agent-plan",
    "local-ai shell-dry-run",
]

ASSISTANT_ENDPOINTS = [
    "GET /assistant/capabilities",
    "POST /assistant/action-preview",
    "GET /assistant/ping",
    "GET /assistant/config",
    "GET /assistant/ui-contract",
    "GET /assistant/startup",
    "GET /assistant/status",
    "GET /assistant/dashboard",
    "POST /assistant/bootstrap",
    "POST /assistant/sessions",
    "GET /assistant/sessions",
    "GET /assistant/sessions/{session_id}",
    "GET /assistant/sessions/{session_id}/messages",
    "POST /assistant/message",
    "POST /assistant/project-root/validate",
]

ASSISTANT_CLI_COMMANDS = [
    "local-ai assistant-capabilities",
    "local-ai assistant-action-preview",
    "local-ai assistant-ping",
    "local-ai assistant-config",
    "local-ai assistant-ui-contract",
    "local-ai assistant-startup",
    "local-ai assistant-status",
    "local-ai assistant-dashboard",
    "local-ai assistant-bootstrap",
    "local-ai assistant-session",
    "local-ai assistant-sessions",
    "local-ai assistant-messages",
    "local-ai assistant-message",
    "local-ai assistant-root",
]

PROJECT_ENDPOINTS = [
    "GET /project/status",
    "GET /project/next",
    "GET /project/api-inventory",
    "GET /project/shell-policy",
    "POST /project/shell-dry-run",
]

PROJECT_CLI_COMMANDS = [
    "local-ai status",
    "local-ai next",
    "local-ai api-inventory",
    "local-ai shell-policy",
    "local-ai shell-dry-run",
]

PUBLIC_DOC_LINKS = [
    "docs/API.md",
    "docs/OPERATIONS.md",
    "docs/UI_CONNECT_GUIDE.md",
    "docs/UI_CONTRACT_CHEATSHEET.md",
    "docs/UI_BRIDGE_EXAMPLES.md",
    "docs/UI_QA_CHECKLIST.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/PUBLIC_RELEASE_SUMMARY.md",
    "docs/PROJECT_SUMMARY.md",
    "docs/CLAUDE_REVIEW_HANDOFF.md",
    "docs/WORKLOG.md",
    "docs/NEXT_CHAT_HANDOFF.md",
    "SECURITY.md",
]

PUBLIC_MARKDOWN_FILES = [
    Path("README.md"),
    Path("SECURITY.md"),
    Path("docs/API.md"),
    Path("docs/PROJECT_SUMMARY.md"),
    Path("docs/OPERATIONS.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/PUBLIC_RELEASE_SUMMARY.md"),
    Path("docs/UI_CONNECT_GUIDE.md"),
    Path("docs/UI_CONTRACT_CHEATSHEET.md"),
    Path("docs/UI_BRIDGE_EXAMPLES.md"),
    Path("docs/UI_QA_CHECKLIST.md"),
    Path("docs/CLAUDE_REVIEW_HANDOFF.md"),
    Path("docs/WORKLOG.md"),
    Path("docs/NEXT_CHAT_HANDOFF.md"),
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INTERNAL_FASTAPI_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


def _link_target_exists(source: Path, raw_target: str) -> bool:
    target = raw_target.strip()
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return True
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]

    target = target.split("#", 1)[0]
    if not target:
        return True

    target_path = Path(target)
    resolved = target_path if target_path.is_absolute() else source.parent / target_path
    return resolved.exists()


def test_public_doc_links_exist_and_are_referenced() -> None:
    readme = DOCS["readme"].read_text(encoding="utf-8")
    summary = DOCS["summary"].read_text(encoding="utf-8")

    for link in PUBLIC_DOC_LINKS:
        assert Path(link).exists(), f"{link} should exist"
        assert link in readme or link in summary, f"{link} should be referenced in public docs"


def test_public_markdown_links_resolve_to_files() -> None:
    broken_links = []

    for source in PUBLIC_MARKDOWN_FILES:
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = match.group(1)
            if not _link_target_exists(source, raw_target):
                line_no = text[: match.start()].count("\n") + 1
                broken_links.append(f"{source}:{line_no} -> {raw_target}")

    assert not broken_links


def test_core_endpoints_are_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}

    for endpoint in CORE_ENDPOINTS:
        assert endpoint in texts["readme"], f"{endpoint} missing from README"
        assert endpoint in texts["api"], f"{endpoint} missing from API docs"
        assert endpoint in texts["summary"], f"{endpoint} missing from project summary"


def test_core_cli_commands_are_documented_in_public_docs() -> None:
    readme = DOCS["readme"].read_text(encoding="utf-8")
    api = DOCS["api"].read_text(encoding="utf-8")
    summary = DOCS["summary"].read_text(encoding="utf-8")

    for command in CORE_CLI_COMMANDS:
        assert command in readme, f"{command} missing from README"
        assert command in api, f"{command} missing from API docs"
        assert command in summary, f"{command} missing from project summary"


def test_assistant_endpoints_are_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}

    for endpoint in ASSISTANT_ENDPOINTS:
        assert endpoint in texts["readme"], f"{endpoint} missing from README"
        assert endpoint in texts["api"], f"{endpoint} missing from API docs"
        assert endpoint in texts["summary"], f"{endpoint} missing from project summary"


def test_assistant_cli_commands_are_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}

    for command in ASSISTANT_CLI_COMMANDS:
        assert command in texts["readme"], f"{command} missing from README"
        assert command in texts["api"], f"{command} missing from API docs"
        assert command in texts["summary"], f"{command} missing from project summary"


def test_project_continuation_contract_is_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}

    for endpoint in PROJECT_ENDPOINTS:
        assert endpoint in texts["readme"], f"{endpoint} missing from README"
        assert endpoint in texts["api"], f"{endpoint} missing from API docs"
        assert endpoint in texts["summary"], f"{endpoint} missing from project summary"

    for command in PROJECT_CLI_COMMANDS:
        assert command in texts["readme"], f"{command} missing from README"
        assert command in texts["api"], f"{command} missing from API docs"
        assert command in texts["summary"], f"{command} missing from project summary"


def test_runtime_api_inventory_is_documented_in_api_reference() -> None:
    api_text = DOCS["api"].read_text(encoding="utf-8")
    runtime_endpoints = {
        f"{method} {endpoint['path']}"
        for endpoint in build_api_inventory(app.routes)["endpoints"]
        for method in endpoint["methods"]
    }

    missing = sorted(endpoint for endpoint in runtime_endpoints if f"`{endpoint}`" not in api_text)
    assert not missing


def test_runtime_cli_commands_are_documented_in_readme_and_api_reference() -> None:
    readme = DOCS["readme"].read_text(encoding="utf-8")
    api_text = DOCS["api"].read_text(encoding="utf-8")
    command = get_command(cli_main.app)
    runtime_commands = {f"local-ai {name}" for name in command.commands}

    missing_from_readme = sorted(cli_command for cli_command in runtime_commands if cli_command not in readme)
    missing_from_api = sorted(cli_command for cli_command in runtime_commands if cli_command not in api_text)

    assert not missing_from_readme
    assert not missing_from_api


def test_public_docs_keep_safety_boundaries_visible() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS.values())

    assert "외부 LLM API" in combined
    assert "Ollama local" in combined
    assert "read-only" in combined
    assert "브라우저 클릭" in combined or "browser interaction" in combined
    assert "파일 수정" in combined or "file_write_delete" in combined


def test_release_checklist_covers_publication_gates() -> None:
    checklist = Path("docs/RELEASE_CHECKLIST.md")
    text = checklist.read_text(encoding="utf-8")

    required_commands = [
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
    ]
    sensitive_paths = [
        ".env",
        "data/local_ai.sqlite3",
        "data/chroma/",
        "data/uploads/",
        "data/logs/",
        "data/*.jsonl",
    ]
    stop_conditions = [
        "실제 외부 LLM API 활성화",
        "실제 shell 실행 활성화",
        "브라우저 interaction 자동화",
        "파일 생성, 수정, 삭제 자동화",
        "운영 배포",
        "클라우드 또는 Oracle 리소스",
    ]
    regression_gates = [
        "tests/test_smoke_script.py",
        "sanitized smoke summary 계약",
        "tests/test_ui_bridge_examples.py",
        "runtime endpoint count drift check",
        "tests/test_public_docs_contract.py",
        "tests/test_security_docs_contract.py",
        "최종 공개 판단",
        "preview-only 기능",
    ]

    assert checklist.exists()
    for item in required_commands + sensitive_paths + stop_conditions + regression_gates:
        assert item in text
    assert "LOCAL_API_KEY=" not in text


def test_all_fastapi_routes_are_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}
    endpoints = []

    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set())
        if path in INTERNAL_FASTAPI_PATHS:
            continue
        for method in sorted(methods - {"HEAD", "OPTIONS"}):
            endpoints.append(f"{method} {path}")

    assert endpoints
    for endpoint in endpoints:
        assert endpoint in texts["readme"], f"{endpoint} missing from README"
        assert endpoint in texts["api"], f"{endpoint} missing from API docs"
        assert endpoint in texts["summary"], f"{endpoint} missing from project summary"


def test_all_typer_commands_are_documented_in_public_docs() -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}
    commands = [f"local-ai {name}" for name in sorted(get_command(cli_main.app).commands)]

    assert commands
    for command in commands:
        assert command in texts["readme"], f"{command} missing from README"
        assert command in texts["api"], f"{command} missing from API docs"
        assert command in texts["summary"], f"{command} missing from project summary"
