from pathlib import Path

from app.schemas.assistant import AssistantMessageListResponse, AssistantSessionListResponse


CHEATSHEET = Path("docs/UI_CONTRACT_CHEATSHEET.md")


def test_ui_contract_cheatsheet_lists_core_endpoints_and_fields() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")

    required_items = [
        "GET /assistant/startup",
        "POST /assistant/bootstrap",
        "POST /assistant/action-preview",
        "POST /assistant/message",
        "GET /assistant/sessions",
        "GET /assistant/sessions/{session_id}/messages",
        "GET /project/api-inventory",
        "POST /documents/index-folder-job-preview",
        "GET /documents/repair-preview",
        "GET /documents/vector-rebuild-preview",
        "ping.status",
        "config.protected",
        "dashboard.cards.connection.status",
        "ui.response_type",
        "endpoints[].requires_api_key",
        "job_id",
        "status",
        "progress.total_files",
        "progress.embedding_batches_total",
        "progress.percent",
        "chunks_missing_vectors_count",
        "actions_count",
        "actions[].requires_user_approval",
        "embedding_batches_estimated",
        "sessions[].messages_count",
        "sessions[].last_message_preview",
        "total_messages",
    ]
    for item in required_items:
        assert item in text


def test_ui_contract_cheatsheet_matches_session_schema_field_names() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")
    session_fields = set(AssistantSessionListResponse.model_fields)
    message_fields = set(AssistantMessageListResponse.model_fields)

    assert {"sessions", "limit", "offset"} <= session_fields
    assert {"messages", "limit", "offset", "total_messages"} <= message_fields
    assert "`GET /assistant/sessions` | 세션 목록 | `sessions`, `limit`, `offset`" in text
    assert "`GET /assistant/sessions/{session_id}/messages` | 메시지 기록 | `messages`, `limit`, `offset`, `total_messages`" in text
    assert "`GET /assistant/sessions` | 세션 목록 | `sessions`, `total`" not in text
    assert "`GET /assistant/sessions/{session_id}/messages` | 메시지 기록 | `messages`, `limit`, `offset`, `total`" not in text


def test_ui_contract_cheatsheet_lists_response_type_mapping() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")

    for response_type in [
        "answer",
        "search_results",
        "index_preview",
        "needs_project_root",
        "shell_dry_run",
        "agent_plan",
        "status",
        "action_preview",
    ]:
        assert f"| `{response_type}` |" in text


def test_ui_contract_cheatsheet_keeps_safety_and_error_contracts_visible() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")

    for phrase in [
        "safety.shell_execution",
        "disabled",
        "safety.browser_interaction",
        "blocked",
        "safety.file_write_delete",
        "safety.external_llm_api",
        "not-used",
        "`401`",
        "`404`",
        "`422`",
        "`429`",
        "`500`",
        "브라우저 클릭/입력/전송 자동화",
        "실제 shell 실행",
        "파일 생성/수정/삭제 자동화",
        "외부 LLM API 호출",
    ]:
        assert phrase in text

    assert "LOCAL_API_KEY=" not in text
