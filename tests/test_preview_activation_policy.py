from pathlib import Path


POLICY = Path("docs/PREVIEW_ACTIVATION_POLICY.md")


def test_preview_activation_policy_documents_current_preview_only_contracts() -> None:
    text = POLICY.read_text(encoding="utf-8")

    for phrase in [
        "POST /documents/index-folder-job-preview",
        "GET /documents/vector-rebuild-preview",
        "GET /documents/repair-preview",
        "local-ai index-job-preview",
        "local-ai vector-rebuild-preview",
        "local-ai repair-preview",
        "dry_run=true",
        "would_enqueue=false",
        "job_id=preview-only",
        "progress.percent=0",
        "embedding_batches_estimated",
        "실제 repair/delete/rebuild는 수행하지 않음",
    ]:
        assert phrase in text


def test_preview_activation_policy_lists_activation_gates_and_stop_conditions() -> None:
    text = POLICY.read_text(encoding="utf-8")

    for heading in [
        "## 실제 Queue 활성화 전 조건",
        "## 실제 Rebuild 활성화 전 조건",
        "## 실제 Repair/Delete 활성화 전 조건",
        "## Stop Conditions",
    ]:
        assert heading in text

    for phrase in [
        "preview endpoint와 실제 실행 endpoint를 분리",
        "LOCAL_API_KEY",
        "SQLite를 source of truth",
        "Ollama local API",
        "orphan vector delete는 rebuild와 분리",
        "사용자 승인 또는 보안 리뷰",
        "실제 queue worker",
        "실제 Chroma write/delete 자동화",
        "workspace 밖 파일 접근",
        "외부 LLM API",
        "클라우드/Oracle 리소스 변경",
    ]:
        assert phrase in text

    assert "OpenAI" not in text or "외부 LLM API" in text
    assert "LOCAL_API_KEY=" not in text


def test_preview_activation_policy_is_linked_from_public_docs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    summary = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")

    assert "docs/PREVIEW_ACTIVATION_POLICY.md" in readme
    assert "docs/PREVIEW_ACTIVATION_POLICY.md" in summary
