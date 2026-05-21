from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_document_service, get_rag_service, get_search_service
from app.main import app
from app.services.assistant_service import AssistantService
from app.services.project_status_service import build_api_inventory


class FakeRagService:
    async def ask(self, db, question: str, system_prompt: str | None, temperature: float):
        return SimpleNamespace(id=123, answer=f"answer: {question}", model="llama3.2")

    async def ask_with_docs(self, db, question: str, top_k: int, temperature: float):
        return SimpleNamespace(
            id=124,
            answer=f"docs answer: {question}",
            model="llama3.2",
            used_sources_json='[{"document_id":1,"filename":"note.md","chunk_index":0,"chunk_id":10}]',
        )


class FakeSearchService:
    async def search(self, query: str, top_k: int = 5):
        return [
            {
                "chunk_id": 10,
                "document_id": 1,
                "filename": "note.md",
                "chunk_index": 0,
                "content": "JWT authentication content",
                "score": 0.1,
            }
        ]


class FakeDocumentService:
    async def save_upload(self, db, filename: str, file):
        return SimpleNamespace(id=1, original_filename=filename), 1

    async def index_folder(self, db, folder_path: str, recursive: bool = True):
        return {
            "indexed_documents": 1,
            "skipped_files": 1,
            "chunks_created": 2,
            "document_ids": [10],
            "indexed_files": [
                {
                    "path": f"{folder_path}/note.html",
                    "document_id": 10,
                    "filename": "note.html",
                    "file_type": "html",
                    "chunks_created": 2,
                }
            ],
            "skipped_file_details": [
                {
                    "path": f"{folder_path}/empty.md",
                    "filename": "empty.md",
                    "reason": "빈 chunk는 생성하지 않습니다.",
                }
            ],
        }

    def preview_index_folder(self, folder_path: str, recursive: bool = True):
        return {
            "folder_path": folder_path,
            "recursive": recursive,
            "files_count": 1,
            "skipped_files_count": 0,
            "chunks_estimated": 2,
            "embedding_batch_size": 8,
            "embedding_batches_estimated": 1,
            "token_estimate": 10,
            "files": [
                {
                    "path": f"{folder_path}/note.md",
                    "filename": "note.md",
                    "file_type": "md",
                    "chunks_estimated": 2,
                    "embedding_batches_estimated": 1,
                    "token_estimate": 10,
                }
            ],
            "skipped_files": [],
            "dry_run": True,
            "note": "미리보기 전용입니다.",
        }

    def list_documents(self, db, source_type: str | None = None, file_type: str | None = None, query: str | None = None):
        filename = f"{query}.md" if query else "note.md"
        return [
            {
                "id": 1,
                "original_filename": filename,
                "stored_path": f"data/uploads/{filename}",
                "file_type": file_type or "md",
                "source_type": source_type or "upload",
                "created_at": "2026-05-20T00:00:00",
                "chunks_count": 1,
            }
        ]

    def get_supported_types(self):
        return {
            "types": [
                {
                    "extension": ".txt",
                    "file_type": "txt",
                    "available": True,
                    "optional_dependency": None,
                    "install_hint": None,
                    "description": "UTF-8 plain text",
                },
                {
                    "extension": ".pdf",
                    "file_type": "pdf",
                    "available": False,
                    "optional_dependency": "pypdf",
                    "install_hint": "pip install -e '.[documents]'",
                    "description": "Text-based PDF",
                },
            ],
            "install_hint": "PDF/DOCX 지원이 unavailable이면 pip install -e '.[documents]'를 실행하세요.",
        }

    def get_document_chunks(self, db, document_id: int, limit: int, offset: int):
        return {
            "document_id": document_id,
            "total_chunks": 1,
            "limit": limit,
            "offset": offset,
            "chunks": [
                {
                    "id": 1,
                    "document_id": document_id,
                    "chunk_index": 0,
                    "content": "chunk",
                    "token_estimate": 1,
                    "created_at": "2026-05-20T00:00:00",
                }
            ],
        }


def test_ask_contract_with_mock() -> None:
    app.dependency_overrides[get_rag_service] = lambda: FakeRagService()
    client = TestClient(app)
    response = client.post("/ask", json={"question": "Spring Boot가 뭐야?", "temperature": 0.2})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "answer: Spring Boot가 뭐야?"
    assert body["used_documents"] is False
    assert body["request_id"] == "123"


def test_ask_with_docs_contract_with_mock() -> None:
    app.dependency_overrides[get_rag_service] = lambda: FakeRagService()
    client = TestClient(app)
    response = client.post("/ask-with-docs", json={"question": "JWT", "top_k": 1})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["used_documents"] is True
    assert body["sources"][0]["chunk_id"] == 10


def test_search_contract_with_mock_embedding() -> None:
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    client = TestClient(app)
    response = client.post("/search", json={"query": "JWT", "top_k": 1})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["results"][0]["filename"] == "note.md"


def test_upload_endpoint_contract_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.post(
        "/documents/upload",
        files={"file": ("note.md", b"# Title\ncontent", "text/markdown")},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"document_id": 1, "filename": "note.md", "chunks_created": 1}


def test_index_folder_preview_endpoint_contract_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.post("/documents/index-folder-preview", json={"folder_path": "/tmp/notes", "recursive": True})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["files_count"] == 1
    assert body["chunks_estimated"] == 2
    assert body["embedding_batch_size"] == 8
    assert body["embedding_batches_estimated"] == 1


def test_index_folder_job_preview_endpoint_contract_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.post("/documents/index-folder-job-preview", json={"folder_path": "/tmp/notes", "recursive": True})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "preview-only"
    assert body["status"] == "planned"
    assert body["dry_run"] is True
    assert body["would_enqueue"] is False
    assert body["status_endpoint"] == "/documents/index-jobs/{job_id}"
    assert body["progress"] == {
        "total_files": 1,
        "processed_files": 0,
        "indexed_documents": 0,
        "skipped_files": 0,
        "chunks_created": 0,
        "embedding_batches_total": 1,
        "embedding_batches_completed": 0,
        "percent": 0.0,
    }


def test_index_folder_endpoint_contract_includes_file_details_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.post("/documents/index-folder", json={"folder_path": "/tmp/notes", "recursive": True})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["indexed_documents"] == 1
    assert body["skipped_files"] == 1
    assert body["indexed_files"][0]["file_type"] == "html"
    assert body["skipped_file_details"][0]["filename"] == "empty.md"


def test_documents_list_endpoint_accepts_filters_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.get("/documents?source_type=upload&file_type=md&query=note")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body[0]["original_filename"] == "note.md"
    assert body[0]["source_type"] == "upload"
    assert body[0]["file_type"] == "md"


def test_supported_document_types_endpoint_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.get("/documents/supported-types")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["types"][0]["extension"] == ".txt"
    assert body["types"][1]["optional_dependency"] == "pypdf"


def test_document_chunks_endpoint_contract_with_mock() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    client = TestClient(app)
    response = client.get("/documents/1/chunks?limit=10&offset=0")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["chunks"][0]["content"] == "chunk"


def test_project_status_contract() -> None:
    client = TestClient(app)

    status_response = client.get("/project/status")
    next_response = client.get("/project/next")
    inventory_response = client.get("/project/api-inventory")
    shell_policy_response = client.get("/project/shell-policy")
    shell_dry_run_response = client.post("/project/shell-dry-run", json={"command": "pwd"})
    blocked_shell_response = client.post("/project/shell-dry-run", json={"command": "rm -rf data"})

    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["project"] == "local-ai-server"
    assert status_body["current_phase"]["phase"] == 15
    assert status_body["recommended_next_model"]["recommended_ai"] == "Codex"
    assert next_response.status_code == 200
    assert next_response.json()["recommended_next_model"]["recommended_model"] == "Codex GPT-5.5"
    assert inventory_response.status_code == 200
    inventory_body = inventory_response.json()
    assert inventory_body["mode"] == "read-only"
    assert inventory_body["local_only"] is True
    assert inventory_body["endpoints_count"] >= 1
    assert any(
        endpoint["path"] == "/project/api-inventory" and endpoint["requires_api_key"] is False
        for endpoint in inventory_body["endpoints"]
    )
    assert any(
        endpoint["path"] == "/assistant/message" and endpoint["requires_api_key"] is True
        for endpoint in inventory_body["endpoints"]
    )
    assert shell_policy_response.status_code == 200
    assert shell_policy_response.json()["mode"] == "dry-run-only"
    assert shell_dry_run_response.status_code == 200
    assert shell_dry_run_response.json()["status"] == "allowed_preview"
    assert shell_dry_run_response.json()["would_execute"] is False
    assert blocked_shell_response.status_code == 200
    assert blocked_shell_response.json()["status"] == "blocked"


def test_assistant_ui_contract_paths_match_api_inventory() -> None:
    contract = AssistantService().ui_contract()
    inventory = build_api_inventory(app.routes)
    endpoints = {(endpoint["path"], method): endpoint for endpoint in inventory["endpoints"] for method in endpoint["methods"]}

    contract_calls = (
        contract["startup_sequence"]
        + contract["refresh_endpoints"]
        + contract["message_flow"]
    )

    for call in contract_calls:
        endpoint = endpoints.get((call["path"], call["method"]))
        assert endpoint is not None, f"{call['method']} {call['path']} is missing from API inventory"
        if call["path"].startswith("/assistant/"):
            assert endpoint["requires_api_key"] is True

    project_inventory = endpoints[("/project/api-inventory", "GET")]
    assert project_inventory["requires_api_key"] is False

    blocked_actions = set(contract["blocked_actions"])
    assert {"browser_interaction", "file_write_delete", "shell_execution"} <= blocked_actions
