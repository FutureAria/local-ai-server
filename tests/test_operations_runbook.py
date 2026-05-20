from pathlib import Path


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
