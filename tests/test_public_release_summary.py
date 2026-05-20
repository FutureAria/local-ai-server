from pathlib import Path


SUMMARY = Path("docs/PUBLIC_RELEASE_SUMMARY.md")


def test_public_release_summary_declares_public_boundaries() -> None:
    text = SUMMARY.read_text(encoding="utf-8")

    required_phrases = [
        "Ollama local API only",
        "외부 LLM API: 사용하지 않음",
        "운영 배포: 하지 않음",
        "클라우드/Oracle 리소스: 연결 또는 생성하지 않음",
        "## 기능 경계 요약",
        "Agent read-only execution v1",
        "조건부 기능",
        "허용 root 폴더 목록 조회",
        "텍스트 파일 preview",
        "명시 URL 단건 read-only fetch",
        "dry-run only",
        "폴더 UI 열기",
        "브라우저 클릭/입력/전송 자동화",
        "실제 shell 실행",
        "파일 생성/수정/삭제 자동화",
        "repair-preview",
        "다중 사용자 auth/RBAC",
        "HTTPS termination",
    ]

    assert SUMMARY.exists()
    for phrase in required_phrases:
        assert phrase in text

    assert "배포 완료" not in text
    assert "LOCAL_API_KEY=" not in text


def test_public_release_summary_keeps_private_data_and_verification_visible() -> None:
    text = SUMMARY.read_text(encoding="utf-8")

    private_paths = [
        ".env",
        "data/local_ai.sqlite3",
        "data/chroma/",
        "data/uploads/",
        "data/logs/",
        "data/*.jsonl",
    ]
    verification_commands = [
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
    ]

    for item in private_paths + verification_commands:
        assert item in text

    assert "passed" in text


def test_release_checklist_requires_capability_boundary_self_check() -> None:
    text = Path("docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")

    for phrase in [
        "Agent execution v1은 조건부 read-only 기능",
        "허용 root 폴더 목록 조회",
        "텍스트 파일 preview",
        "명시 URL 단건 read-only fetch",
        "폴더 UI 열기",
        "shell은 dry-run 정책 판단만",
    ]:
        assert phrase in text
