from pathlib import Path

import scripts.local_ci_check as local_ci


LOCAL_CI_DOCUMENTS = [
    Path("README.md"),
    Path("docs/OPERATIONS.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/PUBLIC_RELEASE_SUMMARY.md"),
]

LOCAL_CI_DOC_SNIPPETS = {
    "pytest": ["python -m pytest", ".venv/bin/pytest"],
    "compileall": ["python -m compileall app cli scripts", ".venv/bin/python -m compileall app cli scripts"],
    "public-release-check": [
        "python scripts/public_release_check.py --root . --json",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
    ],
    "git-diff-check": ["git diff --check"],
}


def test_operations_runbook_documents_safe_local_check_order() -> None:
    text = Path("docs/OPERATIONS.md").read_text(encoding="utf-8")

    required = [
        "## 로컬 운영 Runbook",
        "python scripts/local_ci_check.py --root .",
        "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000",
        "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server",
        "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000",
        "GET /assistant/startup",
        "GET /project/api-inventory",
        "POST /assistant/message",
        "GET /documents/stats",
        "local-ai integrity",
        "local-ai repair-preview",
    ]

    for item in required:
        assert item in text


def test_operations_runbook_keeps_risky_actions_out_of_automation() -> None:
    text = Path("docs/OPERATIONS.md").read_text(encoding="utf-8")
    runbook = text.split("## 로컬 운영 Runbook", maxsplit=1)[1].split("## 백업 기준", maxsplit=1)[0]

    assert "브라우저 클릭/입력/전송 자동화" in runbook
    assert "shell 실제 실행" in runbook
    assert "파일 생성/수정/삭제 자동화" in runbook
    assert "운영 배포" in runbook
    assert "자동 삭제는 수행하지 않는다" in runbook
    assert "실제 repair/delete/rebuild를 실행하지 말고" in runbook


def test_local_ci_docs_match_script_step_contract() -> None:
    step_names = [item["name"] for item in local_ci.build_check_commands(Path("."))]

    assert step_names == list(LOCAL_CI_DOC_SNIPPETS)
    for path in LOCAL_CI_DOCUMENTS:
        text = path.read_text(encoding="utf-8")
        assert "python scripts/local_ci_check.py --root ." in text
        for step_name, accepted_snippets in LOCAL_CI_DOC_SNIPPETS.items():
            assert any(snippet in text for snippet in accepted_snippets), f"{path} missing {step_name} command"
