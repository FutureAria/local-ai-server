from pathlib import Path


def test_ui_qa_checklist_documents_required_flows() -> None:
    text = Path("docs/UI_QA_CHECKLIST.md").read_text(encoding="utf-8")

    assert "GET /assistant/startup" in text
    assert "GET /project/api-inventory" in text
    assert "POST /assistant/bootstrap" in text
    assert "POST /assistant/action-preview" in text
    assert "POST /assistant/message" in text
    assert "GET /assistant/sessions/{session_id}/messages" in text
    assert "routes" in text
    assert "protected" in text
    assert "type=agent_plan" in text
    assert "type=shell_dry_run" in text


def test_ui_qa_checklist_documents_safety_stop_conditions() -> None:
    text = Path("docs/UI_QA_CHECKLIST.md").read_text(encoding="utf-8")

    assert "LOCAL_API_KEY=" not in text
    assert "실제 shell 실행 활성화" in text
    assert "파일 생성, 수정, 삭제 자동화" in text
    assert "외부 LLM API 연결" in text
    assert "운영 배포 또는 클라우드 리소스 변경" in text
    assert "실제 repair/delete/rebuild 실행" in text
