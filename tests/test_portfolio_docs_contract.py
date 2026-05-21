from pathlib import Path


README = Path("README.md")
PROJECT_SUMMARY = Path("docs/PROJECT_SUMMARY.md")
SECURITY = Path("SECURITY.md")


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
