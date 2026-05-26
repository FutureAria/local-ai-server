from pathlib import Path

from app.services.assistant_service import AssistantService


def test_ui_qa_checklist_documents_required_flows() -> None:
    text = Path("docs/UI_QA_CHECKLIST.md").read_text(encoding="utf-8")

    assert "GET /assistant/startup" in text
    assert "GET /health" in text
    assert "GET /project/api-inventory" in text
    assert "/documents/index-folder-job-preview" in text
    assert "/documents/vector-rebuild-preview" in text
    assert "POST /assistant/bootstrap" in text
    assert "POST /assistant/action-preview" in text
    assert "POST /assistant/message" in text
    assert "GET /assistant/sessions/{session_id}/messages" in text
    assert "endpoints" in text
    assert "requires_api_key" in text
    assert "endpoints_count" in text
    assert "protected_endpoints_count" in text
    assert "public_endpoints_count" in text
    assert "sessions_count" in text
    assert "total_messages" in text
    assert "response_type=status" in text
    assert "GET /assistant/ui-contract" in text
    assert "startup_sequence" in text
    assert "refresh_endpoints" in text
    assert "message_flow" in text
    assert "response_types" in text
    assert "blocked_actions" in text
    assert "action_preview" in text
    assert "auth.secret_returned=false" in text
    assert "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server" in text
    assert "python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-preflight" in text
    assert "다른 서버가 사용 중" in text
    assert "type=agent_plan" in text
    assert "dry_run=true" in text
    assert "would_enqueue=false" in text
    assert "progress.percent=0" in text
    assert "embedding_batches_estimated" in text
    assert "type=shell_dry_run" in text
    assert "routes` 목록" not in text
    assert "`protected` 값" not in text


def test_ui_qa_checklist_covers_ui_contract_runtime_shape() -> None:
    text = Path("docs/UI_QA_CHECKLIST.md").read_text(encoding="utf-8")
    contract = AssistantService().ui_contract()

    runtime_paths = [
        item["path"]
        for group in ["startup_sequence", "refresh_endpoints", "message_flow"]
        for item in contract[group]
    ]
    for endpoint in runtime_paths + [
        "/documents/index-folder-job-preview",
        "/documents/vector-rebuild-preview",
    ]:
        assert endpoint in text

    for response_type in contract["response_types"]:
        assert response_type in text

    for blocked_action in contract["blocked_actions"]:
        assert blocked_action in text

    for key, value in contract["safety"].items():
        assert key in text
        assert value in text


def test_ui_qa_checklist_documents_safety_stop_conditions() -> None:
    text = Path("docs/UI_QA_CHECKLIST.md").read_text(encoding="utf-8")

    assert "LOCAL_API_KEY=" not in text
    assert "실제 shell 실행 활성화" in text
    assert "파일 생성, 수정, 삭제 자동화" in text
    assert "외부 LLM API 연결" in text
    assert "운영 배포 또는 클라우드 리소스 변경" in text
    assert "실제 repair/delete/rebuild 실행" in text
    assert "Chroma write 버튼" in text
