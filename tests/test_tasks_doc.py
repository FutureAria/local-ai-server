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
