from pathlib import Path


README = Path("README.md")


def test_readme_has_top_level_onboarding_sections() -> None:
    text = README.read_text(encoding="utf-8")

    for heading in [
        "## Quick Start",
        "## Verification",
        "## Local Assistant Quick Flow",
        "## Safe Boundaries",
        "## Key Docs",
    ]:
        assert heading in text


def test_readme_quick_start_documents_core_commands() -> None:
    text = README.read_text(encoding="utf-8")

    for command in [
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        'pip install -e ".[dev,documents]"',
        "ollama serve",
        "ollama pull llama3.2",
        "ollama pull nomic-embed-text",
        "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000",
    ]:
        assert command in text


def test_readme_verification_documents_safe_check_commands() -> None:
    text = README.read_text(encoding="utf-8")

    for command in [
        "python scripts/local_ci_check.py --root .",
        (
            "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 "
            "--assistant-bridge-only --project-root /Users/juyoung/local-ai-server"
        ),
        "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000",
    ]:
        assert command in text


def test_readme_documents_minimal_local_assistant_flow_near_top() -> None:
    text = README.read_text(encoding="utf-8")
    quick_flow_index = text.index("## Local Assistant Quick Flow")
    safe_boundaries_index = text.index("## Safe Boundaries")

    assert quick_flow_index < safe_boundaries_index
    for command in [
        "local-ai doctor",
        "local-ai index-preview ./notes",
        "local-ai index ./notes",
        'local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름 설명해줘"',
        "local-ai assistant",
    ]:
        assert command in text

    for phrase in [
        "/search JWT",
        "/docs",
        "/status",
        "/next",
        "/summary",
        "preview 또는 dry-run",
        "브라우저 클릭",
        "파일 생성/수정/삭제",
    ]:
        assert phrase in text


def test_readme_keeps_safe_boundaries_visible_near_top() -> None:
    text = README.read_text(encoding="utf-8")

    for phrase in [
        "Ollama local API",
        "OpenAI, Claude, Gemini",
        "LangChain",
        "cloud vector DB",
        "127.0.0.1",
        "LOCAL_API_KEY",
        "브라우저 클릭/입력/전송 자동화",
        "shell dry-run",
        "파일 생성/수정/삭제 자동화",
        "운영 배포",
        "클라우드/Oracle",
        "## Capability Boundary Matrix",
        "Agent execution v1",
        "조건부 read-only",
        "dry-run only",
        "명시 URL 단건 read-only fetch",
        "크롤링/브라우저 이동이 아닙니다",
    ]:
        assert phrase in text


def test_readme_key_docs_links_public_project_docs() -> None:
    text = README.read_text(encoding="utf-8")

    for link in [
        "docs/API.md",
        "docs/PROJECT_SUMMARY.md",
        "docs/OPERATIONS.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/PUBLIC_RELEASE_SUMMARY.md",
        "docs/UI_BRIDGE_EXAMPLES.md",
        "docs/UI_QA_CHECKLIST.md",
        "docs/CLAUDE_REVIEW_HANDOFF.md",
        "docs/WORKLOG.md",
        "docs/NEXT_CHAT_HANDOFF.md",
        "SECURITY.md",
    ]:
        assert link in text
