import json
import re
from pathlib import Path

from app.main import app
from app.schemas.assistant import (
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantStartupResponse,
    AssistantUiContractResponse,
)
from app.schemas.documents import IndexFolderJobPreviewResponse
from app.services.assistant_service import AssistantService
from app.services.project_status_service import build_api_inventory


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
    assert "GET /project/api-inventory" in text
    assert "/documents/index-folder-job-preview" in text
    assert "/documents/vector-rebuild-preview" in text
    assert "POST /assistant/message" in text
    assert '"path": "/assistant/startup"' in text
    assert '"path": "/project/api-inventory"' in text
    assert '"refresh_endpoints"' in text
    assert '"display": "startup_snapshot"' in text
    assert '"external_llm_api": "not-used"' in text
    assert '"mode": "read-only"' in text
    assert '"job_id": "preview-only"' in text
    assert '"would_enqueue": false' in text
    assert '"embedding_batches_total": 2' in text


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


def test_ui_bridge_api_inventory_example_matches_runtime_field_names() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")
    example = _json_block_after_heading(text, "GET /project/api-inventory")
    runtime = build_api_inventory(app.routes)

    for field in [
        "mode",
        "local_only",
        "endpoints_count",
        "protected_endpoints_count",
        "public_endpoints_count",
        "endpoints",
        "safety",
    ]:
        assert field in example
        assert field in runtime

    assert example["endpoints_count"] == runtime["endpoints_count"]
    assert example["protected_endpoints_count"] == runtime["protected_endpoints_count"]
    assert example["public_endpoints_count"] == runtime["public_endpoints_count"]

    endpoint = example["endpoints"][0]
    assert {"path", "methods", "name", "tags", "requires_api_key"} <= set(endpoint)
    example_paths = {endpoint["path"] for endpoint in example["endpoints"]}
    assert "/documents/index-folder-job-preview" in example_paths
    assert "/documents/vector-rebuild-preview" in example_paths
    assert "routes" not in example
    assert "total_routes" not in example
    assert "protected_routes" not in example
    assert "protected" not in endpoint


def test_ui_bridge_index_job_preview_example_matches_schema() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")
    example = _json_block_after_heading(text, "POST /documents/index-folder-job-preview")
    validated = IndexFolderJobPreviewResponse.model_validate(example)

    assert validated.job_id == "preview-only"
    assert validated.status == "planned"
    assert validated.dry_run is True
    assert validated.would_enqueue is False
    assert validated.progress.total_files == 3
    assert validated.progress.embedding_batches_total == 2
    assert validated.progress.percent == 0


def test_ui_bridge_ui_contract_example_matches_runtime_contract_keys() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")
    example = _json_block_after_heading(text, "GET /assistant/ui-contract")
    runtime = AssistantService().ui_contract()

    example_refresh_paths = {endpoint["path"] for endpoint in example["refresh_endpoints"]}
    runtime_refresh_paths = {endpoint["path"] for endpoint in runtime["refresh_endpoints"]}

    assert set(example["response_types"]) == set(runtime["response_types"])
    assert example_refresh_paths == runtime_refresh_paths
    assert "/project/api-inventory" in runtime_refresh_paths
    assert example["blocked_actions"] == runtime["blocked_actions"]
