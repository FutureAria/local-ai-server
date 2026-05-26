from pathlib import Path

from app.schemas.assistant import AssistantMessageListResponse, AssistantSessionListResponse
from app.services.assistant_service import AssistantService


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
    contract = AssistantService().ui_contract()

    for response_type in contract["response_types"]:
        assert f"| `{response_type}` |" in text


def test_ui_contract_cheatsheet_lists_runtime_refresh_endpoints() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")
    contract = AssistantService().ui_contract()

    assert "## Refresh endpoints" in text
    for item in contract["refresh_endpoints"]:
        assert f"| `{item['method']}` | `{item['path']}` |" in text


def test_ui_contract_cheatsheet_keeps_safety_and_error_contracts_visible() -> None:
    text = CHEATSHEET.read_text(encoding="utf-8")
    contract = AssistantService().ui_contract()

    for phrase in [
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

    for key, value in contract["safety"].items():
        assert f"safety.{key}" in text
        assert value in text

    for blocked_action in contract["blocked_actions"]:
        assert blocked_action in text

    assert "LOCAL_API_KEY=" not in text
