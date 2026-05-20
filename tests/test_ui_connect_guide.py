from pathlib import Path


GUIDE = Path("docs/UI_CONNECT_GUIDE.md")


def test_ui_connect_guide_documents_connection_values() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    for phrase in [
        "http://127.0.0.1:8000",
        "Authorization: Bearer <LOCAL_API_KEY>",
        "X-API-Key: <LOCAL_API_KEY>",
        "/Users/juyoung/local-ai-server",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]:
        assert phrase in text


def test_ui_connect_guide_documents_startup_flow() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    for endpoint in [
        "GET /assistant/startup",
        "POST /assistant/bootstrap",
        "POST /assistant/action-preview",
        "POST /assistant/message",
        "GET /assistant/sessions/{session_id}/messages",
        "GET /project/api-inventory",
    ]:
        assert endpoint in text


def test_ui_connect_guide_keeps_safety_boundaries_visible() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    for phrase in [
        "shell_execution`: `disabled",
        "browser_interaction`: `blocked",
        "file_write_delete`: `blocked",
        "external_llm_api`: `not-used",
        "브라우저 클릭/입력/전송 자동화",
        "실제 shell 실행",
        "파일 생성/수정/삭제 자동화",
        "외부 LLM API 호출",
        "운영 배포 또는 클라우드/Oracle 리소스 변경",
    ]:
        assert phrase in text

    assert "LOCAL_API_KEY=" not in text
