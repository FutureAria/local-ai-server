from pathlib import Path

import scripts.local_ci_check as local_ci


LOCAL_CI_DOCUMENTS = [
    Path("README.md"),
    Path("docs/OPERATIONS.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/PUBLIC_RELEASE_SUMMARY.md"),
]

LOCAL_CI_DOC_SNIPPETS = {
    "pytest": [".venv/bin/python -m pytest", ".venv/bin/pytest"],
    "compileall": [".venv/bin/python -m compileall app cli scripts"],
    "public-release-check": [".venv/bin/python scripts/public_release_check.py --root . --json"],
    "git-diff-check": ["git diff --check"],
}


def _documented_command_positions(text: str) -> list[int]:
    snippets_by_step = [
        LOCAL_CI_DOC_SNIPPETS[item["name"]]
        for item in local_ci.build_check_commands(Path("."))
    ]
    positions = []
    for snippets in snippets_by_step:
        matches = [text.find(snippet) for snippet in snippets if snippet in text]
        assert matches, f"missing command snippet from {snippets}"
        positions.append(min(matches))
    return positions


def _local_ci_order_section(path: Path, text: str) -> str:
    if path == Path("README.md"):
        return text.split("이 명령은 아래 순서", maxsplit=1)[1].split("서버 실행 후", maxsplit=1)[0]
    if path == Path("docs/OPERATIONS.md"):
        return text.split("내부 실행 단계:", maxsplit=1)[1].split("### 2. 서버 시작", maxsplit=1)[0]
    if path == Path("docs/RELEASE_CHECKLIST.md"):
        return text.split("## 2. 자동 검증", maxsplit=1)[1].split("통과 기준:", maxsplit=1)[0]
    if path == Path("docs/PUBLIC_RELEASE_SUMMARY.md"):
        return text.split("공개 전 아래 명령이 통과해야 한다.", maxsplit=1)[1].split("현재 검증 상태:", maxsplit=1)[0]
    return text


def test_operations_runbook_documents_safe_local_check_order() -> None:
    text = Path("docs/OPERATIONS.md").read_text(encoding="utf-8")

    required = [
        "## 로컬 운영 Runbook",
        ".venv/bin/python scripts/local_ci_check.py --root .",
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


def test_operations_runbook_documents_verification_storage_impact() -> None:
    text = Path("docs/OPERATIONS.md").read_text(encoding="utf-8")
    runbook = text.split("## 로컬 운영 Runbook", maxsplit=1)[1].split("### 1. 빠른 정적 검증", maxsplit=1)[0]

    for phrase in [
        "검증 명령 저장 영향 요약",
        "서버 필요",
        "Ollama 필요",
        "read-only 검증. 파일/DB 수정 없음",
        "assistant 세션/메시지 기록만 SQLite에 추가될 수 있음",
        "SQLite, Chroma, `data/uploads/`에 테스트 데이터 추가",
    ]:
        assert phrase in runbook


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
        assert ".venv/bin/python scripts/local_ci_check.py --root ." in text
        for step_name, accepted_snippets in LOCAL_CI_DOC_SNIPPETS.items():
            assert any(snippet in text for snippet in accepted_snippets), f"{path} missing {step_name} command"


def test_local_ci_docs_keep_script_step_order() -> None:
    for path in LOCAL_CI_DOCUMENTS:
        text = path.read_text(encoding="utf-8")
        positions = _documented_command_positions(_local_ci_order_section(path, text))
        assert positions == sorted(positions), f"{path} local CI command order drifted"
