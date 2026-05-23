from pathlib import Path


TASKS = Path("docs/TASKS.md")


def test_tasks_doc_exists_and_separates_work_by_risk() -> None:
    text = TASKS.read_text(encoding="utf-8")

    for heading in [
        "# TASKS",
        "## 상태 기준",
        "## Codex가 바로 이어서 할 수 있는 안전 작업",
        "## 사용자 수동 확인 작업",
        "## 별도 승인 또는 보안 리뷰가 필요한 작업",
        "## Stop Conditions",
        "## 검증 명령",
    ]:
        assert heading in text

    for phrase in [
        "safe-next",
        "manual-check",
        "review-required",
        "외부 LLM API",
        "실제 shell 실행",
        "파일 생성, 수정, 삭제 자동화",
        "브라우저 click/fill/submit/login 자동화",
        "Oracle Cloud",
        ".venv/bin/python scripts/local_ci_check.py --root .",
    ]:
        assert phrase in text


def test_tasks_doc_is_linked_from_public_docs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    summary = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")

    assert "docs/TASKS.md" in readme
    assert "docs/TASKS.md" in summary


def test_tasks_doc_marks_safe_contracts_and_user_document_e2e_done() -> None:
    text = TASKS.read_text(encoding="utf-8")

    for item in [
        "[x] README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트 유지",
        "[x] runtime endpoint count drift check 유지",
        "[x] assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 기준으로 유지",
        "[x] `scripts/smoke_test_api.py --sanitized-summary` 결과 예시가 원문/secret/local path를 제외하는지 계속 검증",
        "[x] 실제 사용자 `.md` 또는 `.txt` 문서 기준 upload/search/ask-with-docs end-to-end 재검증 결과를 paste-safe summary로 기록",
        "[x] 대용량 색인 job/status API progress response schema를 preview-only 계약 기준으로 문서화 유지",
        "[x] Chroma 누락 vector 재생성 preview-only endpoint 기준 실제 rebuild 활성화 조건 문서 유지",
        "[x] `docs/NEXT_CHAT_HANDOFF.md`와 이 문서의 safe/manual/review 경계 정합성 유지",
    ]:
        assert item in text

    assert "승인 후 `docs/PROJECT_SUMMARY.md` 기준으로 실행했고, safe-to-paste summary를 `docs/WORKLOG.md`에 기록했다." in text
    assert "문서/RAG smoke는 SQLite, Chroma, `data/uploads/`에 테스트 데이터를 추가할 수 있다." not in text
