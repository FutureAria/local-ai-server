from pathlib import Path


README = Path("README.md")
SECURITY = Path("SECURITY.md")
RELEASE_CHECKLIST = Path("docs/RELEASE_CHECKLIST.md")


def _extract_protected_endpoints(text: str) -> list[str]:
    start = text.index("보호 endpoint:")
    end = text.index("주의:", start) if "주의:" in text[start:] else text.index("```bash", start)
    section = text[start:end]
    return [line.strip()[2:].strip("`") for line in section.splitlines() if line.startswith("- `")]


def test_readme_and_security_protected_endpoint_lists_match() -> None:
    readme = README.read_text(encoding="utf-8")
    security = SECURITY.read_text(encoding="utf-8")

    assert set(_extract_protected_endpoints(readme)) == set(_extract_protected_endpoints(security))


def test_security_docs_share_high_risk_stop_conditions() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [README, SECURITY, RELEASE_CHECKLIST]
    )

    for phrase in [
        "외부 LLM API",
        "실제 shell 실행",
        "브라우저 interaction",
        "파일 생성, 수정, 삭제",
        "운영 배포",
        "클라우드 또는 Oracle 리소스",
    ]:
        assert phrase in combined


def test_security_docs_do_not_expose_secret_shapes() -> None:
    for path in [README, SECURITY]:
        text = path.read_text(encoding="utf-8")
        assert "Authorization: Bearer <LOCAL_API_KEY>" in text or "change-me" in text

    release_text = RELEASE_CHECKLIST.read_text(encoding="utf-8")
    assert "LOCAL_API_KEY=" not in release_text
    assert "Authorization: Bearer <LOCAL_API_KEY>" in release_text
