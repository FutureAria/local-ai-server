from pathlib import Path

from typer.main import get_command

import cli.main as cli_main
from app.main import app
from app.services.project_status_service import build_api_inventory
from scripts import smoke_test_api as smoke


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


def test_public_release_summary_separates_done_preview_and_out_of_scope() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    snapshot = text.split("## 공개용 상태 스냅샷", 1)[1].split("## 기능 경계 요약", 1)[0]

    for phrase in [
        "로컬 API 서버",
        "구현됨",
        "문서 기반 RAG",
        "PDF OCR fallback",
        "PyPDF image XObject",
        "CLI 로컬 비서",
        "Agent 실행 엔진",
        "preview-only",
        "배포/외부 자동화",
        "하지 않음",
        "실제 shell/file/browser 실행은 하지 않는다",
        "운영 배포",
        "외부 LLM API",
    ]:
        assert phrase in snapshot


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

    assert "313 passed" in text


def test_public_release_summary_contract_snapshot_matches_runtime() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    runtime = build_api_inventory(app.routes)
    commands = get_command(cli_main.app).commands

    expected_rows = {
        "FastAPI endpoints": runtime["endpoints_count"],
        "Protected endpoints": runtime["protected_endpoints_count"],
        "Public endpoints": runtime["public_endpoints_count"],
        "Typer CLI commands": len(commands),
        "Document/RAG smoke steps": len(smoke.DOCUMENT_RAG_SMOKE_FLOW),
        "Assistant bridge smoke steps": len(smoke.ASSISTANT_BRIDGE_SMOKE_FLOW),
        "Assistant bridge preflight steps": len(smoke.ASSISTANT_BRIDGE_PREFLIGHT_FLOW),
    }

    assert "## Release Contract Snapshot" in text
    for label, value in expected_rows.items():
        assert f"| {label} | {value} |" in text


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


def test_public_release_docs_share_next_improvement_boundaries() -> None:
    docs = {
        "docs/RELEASE_CHECKLIST.md": Path("docs/RELEASE_CHECKLIST.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": SUMMARY.read_text(encoding="utf-8"),
    }

    required_phrases = [
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
        for phrase in required_phrases:
            assert phrase in text, f"{path} missing next improvement boundary: {phrase}"
