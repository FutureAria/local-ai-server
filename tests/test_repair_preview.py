from app.services.document_service import DocumentService


class FakeRepairPreviewService(DocumentService):
    def __init__(self):
        pass

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
