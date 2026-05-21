from types import SimpleNamespace

from app.services.document_service import DocumentService


class FakeRepairPreviewService(DocumentService):
    def __init__(self):
        self.settings = SimpleNamespace(embedding_batch_size=8)

    def get_integrity_report(self, db):
        return {
            "missing_stored_files": [
                {"document_id": 1, "filename": "missing.md", "stored_path": "data/uploads/missing.md"}
            ],
            "chunks_missing_vectors": [{"chunk_id": 2, "document_id": 1, "chunk_index": 0}],
            "orphan_vector_chunk_ids": [99],
        }


def test_repair_preview_is_dry_run_and_lists_actions() -> None:
    service = FakeRepairPreviewService()
    preview = service.get_repair_preview(db=None)
    assert preview["dry_run"] is True
    assert preview["status"] == "needs_repair"
    assert preview["actions_count"] == 3
    assert {action["action"] for action in preview["actions"]} == {
        "review_missing_file",
        "rebuild_vector",
        "review_orphan_vector",
    }


def test_vector_rebuild_preview_is_dry_run_and_lists_only_rebuild_actions() -> None:
    service = FakeRepairPreviewService()
    preview = service.get_vector_rebuild_preview(db=None)
    assert preview["dry_run"] is True
    assert preview["status"] == "needs_rebuild"
    assert preview["chunks_missing_vectors_count"] == 1
    assert preview["embedding_batch_size"] == 8
    assert preview["embedding_batches_estimated"] == 1
    assert preview["actions_count"] == 1
    assert preview["actions"][0]["action"] == "rebuild_vector"
    assert preview["actions"][0]["target_id"] == 2
