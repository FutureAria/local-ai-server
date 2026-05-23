import json
import re
from pathlib import Path


DOC = Path("docs/SMOKE_SUMMARY_EXAMPLES.md")


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
    assert {step["step"] for step in document["steps"]} >= {
        "health",
        "upload",
        "search",
        "ask-with-docs",
        "feedback",
        "stats",
    }

    assert assistant["mode"] == "assistant-bridge"
    assert {step["step"] for step in assistant["steps"]} >= {
        "assistant-startup",
        "api-inventory",
        "assistant-bootstrap",
        "action-preview",
        "assistant-message",
        "assistant-sessions",
        "assistant-messages",
    }
    assert any(step.get("response_type") == "status" for step in assistant["steps"])
