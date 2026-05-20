import json
import re
from pathlib import Path

from app.schemas.assistant import (
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantStartupResponse,
    AssistantUiContractResponse,
)


def _json_block_after_heading(text: str, heading: str) -> dict:
    pattern = rf"## `{re.escape(heading)}`.*?```json\n(.*?)\n```"
    match = re.search(pattern, text, flags=re.S)
    assert match, f"JSON block for {heading} not found"
    return json.loads(match.group(1))


def _json_block_after_label(text: str, label: str) -> dict:
    pattern = rf"{re.escape(label)}:\n\n```json\n(.*?)\n```"
    match = re.search(pattern, text, flags=re.S)
    assert match, f"JSON block for {label} not found"
    return json.loads(match.group(1))


def test_ui_bridge_examples_document_core_contracts() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    assert "GET /assistant/startup" in text
    assert "GET /assistant/ui-contract" in text
    assert "POST /assistant/message" in text
    assert '"path": "/assistant/startup"' in text
    assert '"refresh_endpoints"' in text
    assert '"display": "startup_snapshot"' in text
    assert '"external_llm_api": "not-used"' in text


def test_ui_bridge_examples_document_message_response_types() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    for response_type in [
        "answer",
        "search_results",
        "index_preview",
        "needs_project_root",
        "shell_dry_run",
        "agent_plan",
        "status",
    ]:
        assert f"type={response_type}" in text
        assert f'"response_type": "{response_type}"' in text

    assert '"would_execute": false' in text
    assert '"requires_approval": true' in text
    assert '"browser_interaction": "blocked"' in text
    assert '"file_write_delete": "blocked"' in text


def test_ui_bridge_examples_do_not_include_real_secret_shape() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    assert "LOCAL_API_KEY=" not in text
    assert '"secret_returned": false' in text
    assert "Authorization: Bearer <LOCAL_API_KEY>" in text


def test_ui_bridge_full_examples_match_assistant_schemas() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    AssistantUiContractResponse.model_validate(_json_block_after_heading(text, "GET /assistant/ui-contract"))
    AssistantStartupResponse.model_validate(_json_block_after_heading(text, "GET /assistant/startup"))
    AssistantMessageRequest.model_validate(_json_block_after_label(text, "요청"))
    AssistantMessageResponse.model_validate(_json_block_after_label(text, "응답"))
