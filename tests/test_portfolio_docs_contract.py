from pathlib import Path


README = Path("README.md")
PROJECT_SUMMARY = Path("docs/PROJECT_SUMMARY.md")
FINAL_REPORT = Path("docs/FINAL_REPORT.md")
SECURITY = Path("SECURITY.md")
CLAUDE_REVIEW_HANDOFF = Path("docs/CLAUDE_REVIEW_HANDOFF.md")


def test_readme_includes_portfolio_story_without_overclaiming() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## 포트폴리오 포인트" in text
    for phrase in [
        "백엔드 API 설계",
        "로컬 RAG 파이프라인 구현",
        "SQLite/Chroma 저장소 분리",
        "Typer CLI",
        "테스트/문서/보안 기준",
        "외부 LLM API 없이",
        "preview, dry-run, approval",
    ]:
        assert phrase in text

    assert "배포 완료" not in text
    assert "브라우저 클릭" in text


def test_project_summary_includes_portfolio_points_and_limits() -> None:
    text = PROJECT_SUMMARY.read_text(encoding="utf-8")

    assert "## 포트폴리오 포인트" in text
    assert "## 실행 가능 기능과 금지 기능" in text
    for phrase in [
        "담당 범위",
        "설계 포인트",
        "안정성 포인트",
        "검증 포인트",
        "한계 명시",
        "외부 LLM API",
        "운영 배포",
        "Agent execution v1",
        "조건부 read-only",
        "허용 root 폴더 목록 조회",
        "텍스트 preview",
        "명시 URL 단건 read-only fetch",
        "dry-run only",
        "브라우저 클릭/입력",
        "파일 생성/수정/삭제",
    ]:
        assert phrase in text


def test_project_summary_and_final_report_show_current_pytest_count() -> None:
    for path in [PROJECT_SUMMARY, FINAL_REPORT, CLAUDE_REVIEW_HANDOFF]:
        text = path.read_text(encoding="utf-8")
        assert "541 passed" in text
        assert "276 passed" not in text
        assert "298 passed" not in text


def test_summary_and_final_report_test_commands_match_baseline() -> None:
    required_commands = [
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
        ".venv/bin/python scripts/local_ci_check.py --root .",
    ]

    for path in [PROJECT_SUMMARY, FINAL_REPORT]:
        text = path.read_text(encoding="utf-8")
        marker = "## 테스트 실행 방법" if path == PROJECT_SUMMARY else "## 5. 테스트 실행 방법"
        test_section = text.split(marker, 1)[1].split("현재 검증 상태:", 1)[0]
        for command in required_commands:
            assert command in test_section, f"{path} missing verification command: {command}"


def test_public_docs_use_json_public_release_check_command() -> None:
    for path in [README, PROJECT_SUMMARY, FINAL_REPORT, SECURITY, CLAUDE_REVIEW_HANDOFF]:
        text = path.read_text(encoding="utf-8")
        assert ".venv/bin/python scripts/public_release_check.py --root . --json" in text
        assert ".venv/bin/python scripts/public_release_check.py --root .`" not in text
        assert ".venv/bin/python scripts/public_release_check.py --root .:" not in text


def test_final_report_matches_required_completion_report_shape() -> None:
    text = FINAL_REPORT.read_text(encoding="utf-8")

    for heading in [
        "## 1. 무엇을 만들었는지",
        "## 2. 생성된 endpoint 목록",
        "## 3. CLI 명령어 목록",
        "## 4. 서버 실행 방법",
        "## 5. 테스트 실행 방법",
        "## 6. 현재 한계",
        "## 7. 다음 추천 개선 사항",
    ]:
        assert heading in text

    for phrase in [
        "외부 GPT API, Claude API, Gemini API 없이",
        "Ollama local API",
        "FastAPI 기반 로컬 HTTP API",
        "SQLite 기반",
        "Chroma 기반 vector search",
        "Typer 기반 `local-ai` CLI",
        "POST /ask-with-docs",
        "GET /project/api-inventory",
        "local-ai assistant",
        "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000",
        ".venv/bin/pytest",
        "541 passed",
        "프론트엔드는 포함하지 않는다",
        "실제 shell 실행은 지원하지 않는다",
        "운영 배포",
        "Codex가 바로 이어서 할 수 있는 안전한 개선",
        "별도 승인 또는 보안 리뷰가 필요한 개선",
    ]:
        assert phrase in text

    assert "배포 완료" not in text
    assert "LOCAL_API_KEY=" not in text


def test_public_docs_share_current_limit_boundaries() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
    }
    required_boundary_terms = [
        "외부 LLM API",
        "cloud vector DB",
        "브라우저 클릭",
        "파일 수정",
        "shell 실행",
        "운영 배포",
        "Oracle",
        "OCR",
        "HTTPS",
        "rate limit",
        "다중 사용자",
    ]

    for path, text in docs.items():
        for term in required_boundary_terms:
            assert term in text, f"{path} missing shared limit boundary: {term}"

    assert "배포 완료" not in README.read_text(encoding="utf-8")
    assert "배포 완료" not in PROJECT_SUMMARY.read_text(encoding="utf-8")


def test_readme_and_project_summary_share_next_improvement_boundaries() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
    }

    required_terms = [
        "## 다음 추천 개선",
        "Codex가 바로 이어서 할 수 있는 안전한 개선",
        "별도 승인 또는 보안 리뷰가 필요한 개선",
        "endpoint/response field 계약 테스트",
        "runtime endpoint count drift check",
        "README/Project Summary Runtime Contract Snapshot",
        "API/CLI/smoke flow inventory",
        "승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary",
        "민감 정보 없이 유지",
        "대용량 색인 job/status API",
        "progress response schema",
        "preview-only",
        "실제 queue 활성화 조건",
        "실제 rebuild 활성화 조건",
        "assistant bridge smoke expected output",
        "UI 수동 QA 체크리스트",
        "최신 preview endpoint 표시 기준",
        "실제 repair/delete/rebuild",
        "브라우저 click/fill/submit 자동화",
        "shell 실행",
        "파일 생성/수정/삭제 자동화",
        "PDF OCR fallback",
        "JavaScript 렌더링",
        "외부 URL 크롤링",
        "pdf2image/poppler",
        "운영 배포",
        "HTTPS termination",
        "다중 사용자 권한 관리",
        "분산 rate limit",
    ]

    for path, text in docs.items():
        for term in required_terms:
            assert term in text, f"{path} missing next improvement boundary: {term}"
