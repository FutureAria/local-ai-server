import json
import re
from pathlib import Path

from app.main import app
from app.services.project_status_service import build_api_inventory
from scripts import smoke_test_api as smoke


DOC = Path("docs/SMOKE_SUMMARY_EXAMPLES.md")
TOP_LEVEL_KEYS_BY_MODE = {
    "document-rag": {"ok", "mode", "base_url", "safe_to_paste", "sample_documents", "steps", "excluded_fields"},
    "assistant-bridge": {"ok", "mode", "base_url", "safe_to_paste", "steps", "excluded_fields"},
}
STEP_KEYS = {
    "health": {"step", "status"},
    "upload": {"step", "status", "documents_count", "chunks_count", "documents"},
    "search": {"step", "status", "results_count"},
    "ask-with-docs": {"step", "status", "sources_count"},
    "feedback": {"step", "status", "feedback_id"},
    "stats": {"step", "status", "documents_count", "chunks_count"},
    "assistant-startup": {"step", "status", "ui_ready", "protected"},
    "api-inventory": {"step", "status", "endpoints_count", "protected_endpoints_count"},
    "assistant-bootstrap": {"step", "status", "ui_ready", "has_project_root"},
    "assistant-action-preview": {"step", "status", "intent", "would_execute"},
    "assistant-message": {"step", "status", "response_type"},
    "assistant-sessions": {"step", "status", "sessions_count"},
    "assistant-messages": {"step", "status", "total_messages"},
}


def _json_blocks() -> list[dict]:
    text = DOC.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)\n```", text, flags=re.S)
    assert len(blocks) == 2
    return [json.loads(block) for block in blocks]


def test_smoke_summary_examples_are_paste_safe() -> None:
    examples = _json_blocks()

    for example in examples:
        assert example["ok"] is True
        assert example["safe_to_paste"] is True
        assert example["base_url"] == "http://127.0.0.1:8000"
        assert example["steps"]
        for field in ["request_id", "headers", "api_key", "project_root", "stored_path"]:
            assert field in example["excluded_fields"]

    forbidden_fragments = [
        "LOCAL_API_KEY=",
        "Bearer secret",
        "/Users/juyoung",
        "\"question\"",
        "\"answer\"",
        "\"content\"",
        "\"stored_path\"",
    ]
    examples_without_excluded = []
    for example in examples:
        copy = dict(example)
        copy.pop("excluded_fields", None)
        examples_without_excluded.append(copy)
    body_without_excluded_list = json.dumps(examples_without_excluded, ensure_ascii=False)
    for fragment in forbidden_fragments:
        assert fragment not in body_without_excluded_list


def test_smoke_summary_examples_cover_document_and_assistant_modes() -> None:
    document, assistant = _json_blocks()

    assert document["mode"] == "document-rag"
    assert document["sample_documents"] == [
        "smoke-backend-notes.md",
        "smoke-architecture-notes.txt",
    ]
    assert [step["step"] for step in document["steps"]] == smoke.DOCUMENT_RAG_SMOKE_FLOW

    assert assistant["mode"] == "assistant-bridge"
    assert [step["step"] for step in assistant["steps"]] == smoke.ASSISTANT_BRIDGE_SMOKE_FLOW
    assert any(step.get("response_type") == "status" for step in assistant["steps"])


def test_smoke_summary_examples_match_sanitized_summary_shape() -> None:
    for example in _json_blocks():
        mode = example["mode"]
        assert set(example) == TOP_LEVEL_KEYS_BY_MODE[mode]
        assert example["excluded_fields"] == smoke.SANITIZED_SUMMARY_EXCLUDED_FIELDS
        for step in example["steps"]:
            step_name = step["step"]
            assert step_name in STEP_KEYS
            assert set(step) == STEP_KEYS[step_name]

    generated_document = smoke.build_sanitized_smoke_summary(
        {
            "ok": True,
            "base_url": "http://127.0.0.1:8000",
            "sample_documents": ["smoke-backend-notes.md", "smoke-architecture-notes.txt"],
            "steps": [
                {"step": "health", "status": 200},
                {
                    "step": "upload",
                    "status": 200,
                    "documents_count": 2,
                    "chunks_count": 2,
                    "documents": [
                        {"filename": "smoke-backend-notes.md", "document_id": 1, "chunks_created": 1},
                        {"filename": "smoke-architecture-notes.txt", "document_id": 2, "chunks_created": 1},
                    ],
                },
                {"step": "search", "status": 200, "results_count": 2},
                {"step": "ask-with-docs", "status": 200, "request_id": "1", "sources_count": 2},
                {"step": "feedback", "status": 200, "feedback_id": 1},
                {"step": "stats", "status": 200, "documents_count": 2, "chunks_count": 2},
            ],
        }
    )
    generated_assistant = smoke.build_sanitized_smoke_summary(
        {
            "ok": True,
            "base_url": "http://127.0.0.1:8000",
            "project_root": "/Users/juyoung/local-ai-server",
            "steps": [
                {"step": "assistant-startup", "status": 200, "ui_ready": True, "protected": True},
                {
                    "step": "api-inventory",
                    "status": 200,
                    "endpoints_count": build_api_inventory(app.routes)["endpoints_count"],
                    "protected_endpoints_count": build_api_inventory(app.routes)["protected_endpoints_count"],
                },
                {"step": "assistant-bootstrap", "status": 200, "ui_ready": True, "has_project_root": True},
                {"step": "assistant-action-preview", "status": 200, "intent": "status", "would_execute": False},
                {
                    "step": "assistant-message",
                    "status": 200,
                    "session_id": "session-1",
                    "response_type": "status",
                },
                {"step": "assistant-sessions", "status": 200, "sessions_count": 1},
                {"step": "assistant-messages", "status": 200, "total_messages": 2},
            ],
        }
    )

    examples = {example["mode"]: example for example in _json_blocks()}
    assert generated_document == examples["document-rag"]
    assert generated_assistant == examples["assistant-bridge"]


def test_smoke_summary_usage_rules_document_all_excluded_fields() -> None:
    text = DOC.read_text(encoding="utf-8")
    usage_rules = text.split("## 사용 규칙", 1)[1]

    assert "SANITIZED_SUMMARY_EXCLUDED_FIELDS" in usage_rules
    for field in smoke.SANITIZED_SUMMARY_EXCLUDED_FIELDS:
        assert f"`{field}`" in usage_rules


def test_assistant_smoke_summary_api_inventory_counts_match_runtime() -> None:
    _, assistant = _json_blocks()
    runtime = build_api_inventory(app.routes)
    inventory_step = next(step for step in assistant["steps"] if step["step"] == "api-inventory")

    assert inventory_step["endpoints_count"] == runtime["endpoints_count"]
    assert inventory_step["protected_endpoints_count"] == runtime["protected_endpoints_count"]
