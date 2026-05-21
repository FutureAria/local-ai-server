from fastapi.testclient import TestClient

from app.api.dependencies import get_document_service
from app.main import app


class FakeDocumentStatsService:
    def get_stats(self, db):
        return {
            "documents_count": 1,
            "chunks_count": 2,
            "chat_logs_count": 3,
            "feedback_count": 4,
            "chroma_vectors_count": 2,
            "missing_stored_files_count": 0,
            "missing_stored_files": [],
        }

    def get_integrity_report(self, db):
        return {
            "status": "ok",
            "sqlite_chunks_count": 2,
            "chroma_vectors_count": 2,
            "missing_stored_files_count": 0,
            "missing_stored_files": [],
            "chunks_missing_vectors_count": 0,
            "chunks_missing_vectors": [],
            "orphan_vectors_count": 0,
            "orphan_vector_chunk_ids": [],
            "repair_available": False,
            "repair_note": "read-only",
        }

    def get_repair_preview(self, db):
        return {
            "status": "ok",
            "dry_run": True,
            "actions_count": 0,
            "actions": [],
            "note": "preview only",
        }

    def get_vector_rebuild_preview(self, db):
        return {
            "status": "ok",
            "dry_run": True,
            "chunks_missing_vectors_count": 0,
            "embedding_batch_size": 8,
            "embedding_batches_estimated": 0,
            "actions_count": 0,
            "actions": [],
            "note": "preview only",
        }


def test_document_stats_endpoint_contract() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentStatsService()
    client = TestClient(app)
    response = client.get("/documents/stats")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["documents_count"] == 1
    assert response.json()["chroma_vectors_count"] == 2


def test_document_integrity_endpoint_contract() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentStatsService()
    client = TestClient(app)
    response = client.get("/documents/integrity")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["repair_available"] is False


def test_document_repair_preview_endpoint_contract() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentStatsService()
    client = TestClient(app)
    response = client.get("/documents/repair-preview")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dry_run"] is True
    assert response.json()["actions_count"] == 0


def test_document_vector_rebuild_preview_endpoint_contract() -> None:
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentStatsService()
    client = TestClient(app)
    response = client.get("/documents/vector-rebuild-preview")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["chunks_missing_vectors_count"] == 0
    assert body["embedding_batches_estimated"] == 0
