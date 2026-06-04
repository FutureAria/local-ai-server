from pathlib import Path


POLICY = Path("docs/PREVIEW_ACTIVATION_POLICY.md")
READ_ONLY_ADAPTER_DECISION = Path("docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md")
READ_ONLY_RESULT_WRAPPER_SCHEMA = Path("docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md")


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


def test_read_only_adapter_execution_decision_required_policy_matrix() -> None:
    text = READ_ONLY_ADAPTER_DECISION.read_text(encoding="utf-8")

    for phrase in [
        "# Read-only Adapter Execution Decision Required",
        "## Preview-only Policy Matrix",
        "`read_only_scan`",
        "`file_preview`",
        "`url_preview`",
        "`workspace_brief`",
        "25차",
        "26차",
        "env opt-in read-only",
        "READ_ONLY_ADAPTER_EXECUTION_ENABLED=true",
        "READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true",
        "would_dispatch=false",
        "would_read=false",
        "would_fetch=false",
        "execution_enabled=false",
        "기본값은 여전히 disabled",
        "shell/patch/browser dispatch는 수행하지 않는다",
        "Decision Required",
        "approval consume mode 전환",
        "외부 LLM/API provider 연결",
    ]:
        assert phrase in text


def test_read_only_adapter_execution_decision_required_is_linked_from_public_docs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    summary = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")
    security = Path("SECURITY.md").read_text(encoding="utf-8")

    for text in [readme, summary, security]:
        assert "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md" in text


def test_read_only_result_wrapper_schema_documents_preview_only_injection_boundary() -> None:
    text = READ_ONLY_RESULT_WRAPPER_SCHEMA.read_text(encoding="utf-8")

    for phrase in [
        "# Read-only Result Wrapper Schema",
        "assistant.action_loop.read_only_result_wrapper.v1",
        "contract_mode",
        "`preview-only`",
        "raw_content_allowed",
        "`false`",
        "approval_like_json_trusted",
        "can_mutate_frozen_plan",
        "can_set_next_action",
        "raw_content",
        "approval_id",
        "next_step",
        "shell_command",
        "patch_payload",
        "browser_action",
        "would_dispatch",
        "would_read",
        "would_fetch",
        "execution_enabled",
        "실제 파일 내용 읽기",
        "실제 URL fetch",
    ]:
        assert phrase in text


def test_read_only_result_wrapper_schema_is_linked_from_public_docs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    summary = Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8")
    security = Path("SECURITY.md").read_text(encoding="utf-8")
    api = Path("docs/API.md").read_text(encoding="utf-8")

    for text in [readme, summary, security, api]:
        assert "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md" in text
