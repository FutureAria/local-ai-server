import re
from pathlib import Path

from typer.main import get_command

import cli.main as cli_main
from app.main import app
from app.schemas.assistant import AssistantDurableStatePreviewResponse
from app.services.project_status_service import build_api_inventory
from scripts import smoke_test_api as smoke


DOCS = {
    "readme": Path("README.md"),
    "api": Path("docs/API.md"),
    "summary": Path("docs/PROJECT_SUMMARY.md"),
}
CLI_EXAMPLE_DOCS = {
    **DOCS,
    "handoff": Path("docs/NEXT_CHAT_HANDOFF.md"),
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
    "local-ai index-job-preview",
    "local-ai integrity",
    "local-ai vector-rebuild-preview",
    "local-ai agent-plan",
    "local-ai shell-dry-run",
]

ASSISTANT_ENDPOINTS = [
    "GET /assistant/capabilities",
    "POST /assistant/action-preview",
    "POST /assistant/action-loop-read-only-dispatch",
    "POST /assistant/automation-plan",
    "POST /assistant/read-only-scan",
    "POST /assistant/file-preview",
    "POST /assistant/url-preview",
    "POST /assistant/read-only-adapter/execute",
    "POST /assistant/workspace-brief",
    "POST /assistant/shell-preview",
    "POST /assistant/shell-approval-preview",
    "POST /assistant/shell-run",
    "POST /assistant/durable-state-preview/preview",
    "GET /assistant/approval-console/pending",
    "GET /assistant/approval-console/{approval_id}",
    "POST /assistant/approval-console/cleanup-expired",
    "POST /assistant/patch-preview",
    "POST /assistant/patch-approval-preview",
    "POST /assistant/patch-apply",
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
    "local-ai assistant-automation-plan",
    "local-ai assistant-read-only-scan",
    "local-ai assistant-file-preview",
    "local-ai assistant-url-preview",
    "local-ai assistant-workspace-brief",
    "local-ai assistant-shell-preview",
    "local-ai assistant-shell-approval-preview",
    "local-ai assistant-shell-run",
    "local-ai assistant-patch-preview",
    "local-ai assistant-patch-approval-preview",
    "local-ai assistant-patch-apply",
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
    "docs/FINAL_REPORT.md",
    "docs/TASKS.md",
    "docs/OCR_INTEGRATION_PLAN.md",
    "docs/USER_DOCUMENT_E2E_PLAN.md",
    "docs/SMOKE_SUMMARY_EXAMPLES.md",
    "docs/PREVIEW_ACTIVATION_POLICY.md",
    "docs/OPERATIONS.md",
    "docs/UI_CONNECT_GUIDE.md",
    "docs/UI_CONTRACT_CHEATSHEET.md",
    "docs/UI_BRIDGE_EXAMPLES.md",
    "docs/UI_QA_CHECKLIST.md",
    "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
    "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md",
    "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md",
    "docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md",
    "docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md",
    "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md",
    "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md",
    "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
    "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/PUBLIC_RELEASE_SUMMARY.md",
    "docs/PROJECT_SUMMARY.md",
    "docs/CLAUDE_REVIEW_HANDOFF.md",
    "docs/CODEX_IMPLEMENTATION_NOTES.md",
    "docs/WORKLOG.md",
    "docs/NEXT_CHAT_HANDOFF.md",
    "SECURITY.md",
]

PUBLIC_MARKDOWN_FILES = [
    Path("README.md"),
    Path("SECURITY.md"),
    Path("docs/API.md"),
    Path("docs/FINAL_REPORT.md"),
    Path("docs/TASKS.md"),
    Path("docs/OCR_INTEGRATION_PLAN.md"),
    Path("docs/USER_DOCUMENT_E2E_PLAN.md"),
    Path("docs/SMOKE_SUMMARY_EXAMPLES.md"),
    Path("docs/PREVIEW_ACTIVATION_POLICY.md"),
    Path("docs/PROJECT_SUMMARY.md"),
    Path("docs/OPERATIONS.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/PUBLIC_RELEASE_SUMMARY.md"),
    Path("docs/UI_CONNECT_GUIDE.md"),
    Path("docs/UI_CONTRACT_CHEATSHEET.md"),
    Path("docs/UI_BRIDGE_EXAMPLES.md"),
    Path("docs/UI_QA_CHECKLIST.md"),
    Path("docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md"),
    Path("docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md"),
    Path("docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"),
    Path("docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md"),
    Path("docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md"),
    Path("docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"),
    Path("docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md"),
    Path("docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md"),
    Path("docs/CLAUDE_REVIEW_HANDOFF.md"),
    Path("docs/CODEX_IMPLEMENTATION_NOTES.md"),
    Path("docs/WORKLOG.md"),
    Path("docs/NEXT_CHAT_HANDOFF.md"),
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INTERNAL_FASTAPI_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
LOCAL_AI_COMMAND_RE = re.compile(r"(?<![\w-])local-ai\s+([a-z][a-z0-9-]*)")
ENDPOINT_TOKEN_RE = re.compile(r"`(GET|POST|DELETE|PUT|PATCH) ([^`]+)`")


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
    inventory = build_api_inventory(app.routes)
    runtime_endpoints = {
        f"{method} {endpoint['path']}"
        for endpoint in inventory["endpoints"]
        for method in endpoint["methods"]
    }
    public_read_only_section = api_text.split("현재 API key 없이 읽을 수 있는 public read-only endpoint는", 1)[1].split(
        "이다.",
        1,
    )[0]

    missing = sorted(endpoint for endpoint in runtime_endpoints if f"`{endpoint}`" not in api_text)
    assert not missing
    public_endpoints = {
        f"{method} {endpoint['path']}"
        for endpoint in inventory["endpoints"]
        if endpoint["requires_api_key"] is False
        for method in endpoint["methods"]
    }
    assert all(f"`{endpoint}`" in public_read_only_section for endpoint in public_endpoints)
    documented_public_endpoints = {
        f"{method} {path}" for method, path in ENDPOINT_TOKEN_RE.findall(public_read_only_section)
    }
    assert documented_public_endpoints == public_endpoints


def test_stage76_durable_state_preview_docs_api_drift_guard_matches_schema_and_route_surface() -> None:
    api_text = DOCS["api"].read_text(encoding="utf-8")
    docs_text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS.values())
    inventory = build_api_inventory(app.routes)
    durable_endpoints = [
        endpoint for endpoint in inventory["endpoints"] if endpoint["path"].startswith("/assistant/durable-state-preview")
    ]
    section = api_text.split("### `POST /assistant/durable-state-preview/preview`", 1)[1].split(
        "### Approval Console Read-only API",
        1,
    )[0]

    assert durable_endpoints == [
        {
            "path": "/assistant/durable-state-preview/preview",
            "methods": ["POST"],
            "tags": ["assistant"],
            "name": "assistant_durable_state_preview",
            "requires_api_key": True,
        }
    ]
    for field in AssistantDurableStatePreviewResponse.model_fields:
        assert f"`{field}`" in section

    for phrase in [
        "POST /assistant/durable-state-preview/preview",
        "response-only/read-only/schema-only",
        "stored preview lookup/list/cleanup remain Decision Required",
        "GET /assistant/durable-state-preview/{preview_state_id} remains absent",
        "GET /assistant/durable-state-preview remains absent",
        "POST /assistant/durable-state-preview/cleanup-expired remains absent",
        "no persistence mutation",
        "no approval consume",
        "no queue mutation",
    ]:
        assert phrase in docs_text


def test_runtime_cli_commands_are_documented_in_readme_and_api_reference() -> None:
    readme = DOCS["readme"].read_text(encoding="utf-8")
    api_text = DOCS["api"].read_text(encoding="utf-8")
    command = get_command(cli_main.app)
    runtime_commands = {f"local-ai {name}" for name in command.commands}

    missing_from_readme = sorted(cli_command for cli_command in runtime_commands if cli_command not in readme)
    missing_from_api = sorted(cli_command for cli_command in runtime_commands if cli_command not in api_text)

    assert not missing_from_readme
    assert not missing_from_api


def test_api_reference_cli_block_matches_typer_commands() -> None:
    api_text = DOCS["api"].read_text(encoding="utf-8")
    cli_section = api_text.split("## CLI 대응", 1)[1]
    block_match = re.search(r"```bash\n(.*?)\n```", cli_section, flags=re.S)
    assert block_match is not None

    documented_commands = {
        match.group(1)
        for match in re.finditer(r"(?m)^local-ai\s+([a-z][a-z0-9-]*)", block_match.group(1))
    }
    runtime_commands = set(get_command(cli_main.app).commands)

    assert documented_commands == runtime_commands


def test_readme_and_project_summary_contract_snapshots_match_runtime() -> None:
    runtime = build_api_inventory(app.routes)
    commands = get_command(cli_main.app).commands
    expected_rows = {
        "FastAPI endpoints": runtime["endpoints_count"],
        "Protected endpoints": runtime["protected_endpoints_count"],
        "Public endpoints": runtime["public_endpoints_count"],
        "Typer CLI commands": len(commands),
        "Document/RAG smoke steps": len(smoke.DOCUMENT_RAG_SMOKE_FLOW),
        "Assistant bridge smoke steps": len(smoke.ASSISTANT_BRIDGE_SMOKE_FLOW),
        "Assistant bridge preflight steps": len(smoke.ASSISTANT_BRIDGE_PREFLIGHT_FLOW),
    }

    for path in [DOCS["readme"], DOCS["summary"]]:
        text = path.read_text(encoding="utf-8")
        assert "## Runtime Contract Snapshot" in text
        for label, value in expected_rows.items():
            assert f"| {label} | {value} |" in text

    api_text = DOCS["api"].read_text(encoding="utf-8")
    public_read_only_section = api_text.split("현재 API key 없이 읽을 수 있는 public read-only endpoint는", 1)[1].split(
        "이다.",
        1,
    )[0]
    documented_public_count = len(ENDPOINT_TOKEN_RE.findall(public_read_only_section))
    assert documented_public_count == expected_rows["Public endpoints"]


def test_public_docs_keep_safety_boundaries_visible() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOCS.values())
    api_text = DOCS["api"].read_text(encoding="utf-8")
    inventory_safety = build_api_inventory(app.routes)["safety"]

    assert "외부 LLM API" in combined
    assert "Ollama local" in combined
    assert "read-only" in combined
    assert "브라우저 클릭" in combined or "browser interaction" in combined
    assert "파일 수정" in combined or "file_write_delete" in combined
    for key, value in inventory_safety.items():
        assert f"safety.{key}={value}" in api_text


def test_public_docs_surface_decision_required_link_set() -> None:
    texts = {path: path.read_text(encoding="utf-8") for path in PUBLIC_MARKDOWN_FILES}
    public_combined = "\n".join(
        texts[path] for path in [Path("README.md"), Path("docs/PROJECT_SUMMARY.md"), Path("docs/API.md")]
    )
    required_links = [
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md",
        "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md",
        "docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md",
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md",
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
    ]

    for link in required_links:
        assert Path(link).exists(), f"{link} should exist"
        assert link in public_combined, f"{link} should be visible from public docs"
        assert any(link in text for text in texts.values()), f"{link} should stay linked in markdown docs"

    for phrase in [
        "실제 dispatch",
        "read-only adapter execution",
        "raw content",
        "approval-like JSON",
        "execution_enabled=false",
        "Local Jarvis",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
    ]:
        assert phrase in public_combined


def test_stage48_full_automation_action_loop_decision_required_is_publicly_locked() -> None:
    decision_docs = {
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md": Path(
            "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md": Path(
            "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
    }
    public_docs = {
        "README.md": Path("README.md").read_text(encoding="utf-8"),
        "SECURITY.md": Path("SECURITY.md").read_text(encoding="utf-8"),
        "docs/API.md": Path("docs/API.md").read_text(encoding="utf-8"),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8"),
    }

    for path, text in decision_docs.items():
        for phrase in [
            "48차",
            "Full Automation Action-loop Dispatch Decision Required",
            "실제 action-loop full dispatch는 계속 금지",
            "사용자 최종 승인",
            "Opus 리뷰",
            "connector별 approval consume",
            "rollback/failure strategy",
            "browser actual interaction",
            "app-os actual action",
        ]:
            assert phrase in text, f"{path} missing stage48 decision phrase: {phrase}"

    combined_public = "\n".join(public_docs.values())
    for phrase in [
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "사용자 최종 승인",
        "Opus 리뷰",
        "실제 action-loop full dispatch는 계속 금지",
    ]:
        assert phrase in combined_public


def test_release_checklist_covers_publication_gates() -> None:
    checklist = Path("docs/RELEASE_CHECKLIST.md")
    text = checklist.read_text(encoding="utf-8")

    required_commands = [
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        ".venv/bin/python scripts/local_ci_check.py --root .",
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
        "README/Project Summary Runtime Contract Snapshot",
        "API/CLI/smoke flow inventory",
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


def test_documented_local_ai_commands_exist_in_typer_app() -> None:
    known_commands = set(get_command(cli_main.app).commands)
    invalid_examples = []

    for name, path in CLI_EXAMPLE_DOCS.items():
        text = path.read_text(encoding="utf-8")
        for match in LOCAL_AI_COMMAND_RE.finditer(text):
            command_name = match.group(1)
            if command_name not in known_commands:
                line_no = text[: match.start()].count("\n") + 1
                invalid_examples.append(f"{name}:{line_no} local-ai {command_name}")

    assert not invalid_examples
