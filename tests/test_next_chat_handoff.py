from pathlib import Path


def test_next_chat_handoff_keeps_codex_tasks_safe() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert "브라우저 조작 없이" in text
    assert "Codex가 바로 이어서 할 수 있는 안전 작업" in text
    assert "사용자 수동 확인 또는 별도 승인 후에만 진행할 작업" in text
    assert "실제 브라우저 렌더링 확인" in text
    assert "사용자 승인 또는 수동 확인 전 진행 불가" in text


def test_next_chat_handoff_includes_current_verification_gates() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert ".venv/bin/pytest" in text
    assert "174 passed" in text
    assert ".venv/bin/python -m compileall app cli scripts" in text
    assert ".venv/bin/python scripts/public_release_check.py --root . --json" in text
    assert "git diff --check" in text


def test_next_chat_handoff_links_release_and_ui_docs() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    for doc in [
        "docs/UI_BRIDGE_EXAMPLES.md",
        "docs/UI_QA_CHECKLIST.md",
        "docs/RELEASE_CHECKLIST.md",
    ]:
        assert doc in text
