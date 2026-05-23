from pathlib import Path


PLAN = Path("docs/USER_DOCUMENT_E2E_PLAN.md")


def test_user_document_e2e_plan_documents_approval_and_storage_impact() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for phrase in [
        "사용자 승인",
        "SQLite",
        "Chroma",
        "`data/uploads/`",
        "127.0.0.1",
        "LOCAL_API_KEY",
        "X-API-Key",
        "ollama serve",
        "llama3.2",
        "nomic-embed-text",
    ]:
        assert phrase in text


def test_user_document_e2e_plan_keeps_paste_safe_summary_contract() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for phrase in [
        "scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-notes.md --sanitized-summary",
        "safe_to_paste=true",
        "excluded_fields",
        "질문/답변 원문",
        "request id",
        "stored path",
        "문서 원문",
    ]:
        assert phrase in text

    assert "LOCAL_API_KEY=" not in text


def test_user_document_e2e_plan_is_linked_and_task_remains_manual() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    summary = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")
    tasks = Path("docs/TASKS.md").read_text(encoding="utf-8")

    assert "docs/USER_DOCUMENT_E2E_PLAN.md" in readme
    assert "docs/USER_DOCUMENT_E2E_PLAN.md" in summary
    assert "[x] 실제 사용자 `.md` 또는 `.txt` 문서 기준 upload/search/ask-with-docs end-to-end 재검증 결과를 paste-safe summary로 기록" in tasks
    assert "승인 후 `docs/PROJECT_SUMMARY.md` 기준으로 실행했고, safe-to-paste summary를 `docs/WORKLOG.md`에 기록했다." in tasks
