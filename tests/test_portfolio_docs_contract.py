from pathlib import Path


def test_readme_includes_portfolio_story_without_overclaiming() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

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
    text = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")

    assert "## 포트폴리오 포인트" in text
    for phrase in [
        "담당 범위",
        "설계 포인트",
        "안정성 포인트",
        "검증 포인트",
        "한계 명시",
        "외부 LLM API",
        "운영 배포",
    ]:
        assert phrase in text
