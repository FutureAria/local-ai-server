from pathlib import Path


def test_readme_documents_browser_ui_attach_sequence() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "브라우저 UI를 붙이는 기본 순서" in text
    assert "GET /assistant/startup" in text
    assert "POST /assistant/bootstrap" in text
    assert "POST /assistant/action-preview" in text
    assert "POST /assistant/message" in text
    assert "GET /assistant/sessions/{session_id}/messages" in text
    assert "docs/UI_QA_CHECKLIST.md" in text
    assert "docs/UI_BRIDGE_EXAMPLES.md" in text
