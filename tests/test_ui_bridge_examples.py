from pathlib import Path


def test_ui_bridge_examples_document_core_contracts() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    assert "GET /assistant/startup" in text
    assert "GET /assistant/ui-contract" in text
    assert "POST /assistant/message" in text
    assert '"path": "/assistant/startup"' in text
    assert '"refresh_endpoints"' in text
    assert '"display": "startup_snapshot"' in text
    assert '"external_llm_api": "not-used"' in text


def test_ui_bridge_examples_do_not_include_real_secret_shape() -> None:
    text = Path("docs/UI_BRIDGE_EXAMPLES.md").read_text(encoding="utf-8")

    assert "LOCAL_API_KEY=" not in text
    assert '"secret_returned": false' in text
    assert "Authorization: Bearer <LOCAL_API_KEY>" in text
