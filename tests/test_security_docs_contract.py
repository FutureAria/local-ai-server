from pathlib import Path

from app.main import app
from app.services.project_status_service import build_api_inventory


README = Path("README.md")
SECURITY = Path("SECURITY.md")
API_DOCS = Path("docs/API.md")
RELEASE_CHECKLIST = Path("docs/RELEASE_CHECKLIST.md")
PUBLIC_RELEASE_SUMMARY = Path("docs/PUBLIC_RELEASE_SUMMARY.md")
PROJECT_SUMMARY = Path("docs/PROJECT_SUMMARY.md")
HTTP_METHODS = ("GET ", "POST ", "PUT ", "PATCH ", "DELETE ")


def _extract_protected_endpoints(text: str) -> list[str]:
    start = text.index("보호 endpoint:")
    end = text.index("주의:", start) if "주의:" in text[start:] else text.index("```bash", start)
    section = text[start:end]
    endpoints = []
    for line in section.splitlines():
        if not line.startswith("- `"):
            continue
        endpoint = line.strip()[2:].strip("`")
        if endpoint.startswith(HTTP_METHODS):
            endpoints.append(endpoint)
    return endpoints


def test_readme_and_security_protected_endpoint_lists_match() -> None:
    readme = README.read_text(encoding="utf-8")
    security = SECURITY.read_text(encoding="utf-8")

    assert set(_extract_protected_endpoints(readme)) == set(_extract_protected_endpoints(security))


def test_protected_endpoint_docs_match_runtime_api_inventory() -> None:
    runtime_protected = {
        f"{method} {endpoint['path']}"
        for endpoint in build_api_inventory(app.routes)["endpoints"]
        if endpoint["requires_api_key"]
        for method in endpoint["methods"]
    }

    for path in [README, SECURITY, API_DOCS]:
        documented = set(_extract_protected_endpoints(path.read_text(encoding="utf-8")))
        assert documented == runtime_protected, f"{path} protected endpoint list is out of sync"


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


def test_public_release_docs_each_keep_high_risk_boundaries() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
        "docs/RELEASE_CHECKLIST.md": RELEASE_CHECKLIST.read_text(encoding="utf-8"),
        "docs/PUBLIC_RELEASE_SUMMARY.md": PUBLIC_RELEASE_SUMMARY.read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
    }
    required_phrases = [
        "외부 LLM API",
        "실제 shell 실행",
        "브라우저",
        "파일 생성/수정/삭제",
        "운영 배포",
        "Oracle",
        "DB migration",
        "비용",
    ]

    for path, text in docs.items():
        for phrase in required_phrases:
            assert phrase in text, f"{path} missing high-risk boundary: {phrase}"


def test_api_reference_keeps_execution_stop_boundaries_visible() -> None:
    text = API_DOCS.read_text(encoding="utf-8")

    for phrase in [
        "외부 LLM API",
        "실제 shell",
        "브라우저 클릭",
        "파일 수정",
        "운영 배포",
    ]:
        assert phrase in text


def test_security_docs_do_not_expose_secret_shapes() -> None:
    for path in [README, SECURITY]:
        text = path.read_text(encoding="utf-8")
        assert "Authorization: Bearer <LOCAL_API_KEY>" in text or "change-me" in text

    release_text = RELEASE_CHECKLIST.read_text(encoding="utf-8")
    assert "LOCAL_API_KEY=" not in release_text
    assert "Authorization: Bearer <LOCAL_API_KEY>" in release_text
