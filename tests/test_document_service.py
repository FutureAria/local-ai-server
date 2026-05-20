import asyncio

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.db.database import Base
from app.db.models import Document, DocumentChunk
from app.services.document_service import DocumentIndexingError, DocumentService


class FakeEmbeddingService:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 2.0, 3.0] for _ in texts]


class FailingVectorStore:
    def add_chunks(self, records, embeddings) -> None:
        raise RuntimeError("vector store failed")


class RecordingVectorStore:
    def __init__(self) -> None:
        self.records = []

    def add_chunks(self, records, embeddings) -> None:
        self.records.extend(records)


def test_document_service_rolls_back_sqlite_when_vector_store_fails(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    source = tmp_path / "note.md"
    source.write_text("# Note\nJWT content", encoding="utf-8")
    settings = Settings(UPLOAD_DIR=str(tmp_path / "uploads"), CHROMA_PATH=str(tmp_path / "chroma"))
    service = DocumentService(
        settings=settings,
        embedding_service=FakeEmbeddingService(),
        vector_store=FailingVectorStore(),
    )

    with TestingSessionLocal() as db:
        with pytest.raises(DocumentIndexingError, match="rollback"):
            asyncio.run(service._index_file(db, source, original_filename="note.md", source_type="upload"))

        assert db.scalar(select(func.count(Document.id))) == 0
        assert db.scalar(select(func.count(DocumentChunk.id))) == 0


def test_document_service_preview_index_folder_is_read_only(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "first.md").write_text("a" * 80, encoding="utf-8")
    (notes / "second.txt").write_text("b" * 20, encoding="utf-8")
    (notes / "ignored.png").write_text("not indexed", encoding="utf-8")
    settings = Settings(
        UPLOAD_DIR=str(tmp_path / "uploads"),
        CHROMA_PATH=str(tmp_path / "chroma"),
        CHUNK_SIZE=30,
        CHUNK_OVERLAP=5,
        EMBEDDING_BATCH_SIZE=2,
    )
    service = DocumentService(
        settings=settings,
        embedding_service=FakeEmbeddingService(),
        vector_store=FailingVectorStore(),
    )

    preview = service.preview_index_folder(str(notes), recursive=True)

    assert preview["dry_run"] is True
    assert preview["files_count"] == 2
    assert preview["skipped_files_count"] == 0
    assert preview["chunks_estimated"] > 2
    assert preview["embedding_batch_size"] == 2
    assert preview["embedding_batches_estimated"] == 3
    assert preview["files"][0]["embedding_batches_estimated"] >= 1
    with TestingSessionLocal() as db:
        assert db.scalar(select(func.count(Document.id))) == 0
        assert db.scalar(select(func.count(DocumentChunk.id))) == 0


def test_document_service_index_folder_returns_file_details(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.sqlite3'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "first.html").write_text("<h1>JWT</h1><p>Authorization header</p>", encoding="utf-8")
    (notes / "bad.txt").write_bytes(b"\xff\xfe\x00")
    vector_store = RecordingVectorStore()
    settings = Settings(
        UPLOAD_DIR=str(tmp_path / "uploads"),
        CHROMA_PATH=str(tmp_path / "chroma"),
        CHUNK_SIZE=100,
        CHUNK_OVERLAP=10,
    )
    service = DocumentService(
        settings=settings,
        embedding_service=FakeEmbeddingService(),
        vector_store=vector_store,
    )

    with TestingSessionLocal() as db:
        result = asyncio.run(service.index_folder(db, str(notes), recursive=True))

        assert result["indexed_documents"] == 1
        assert result["skipped_files"] == 1
        assert result["indexed_files"][0]["filename"] == "first.html"
        assert result["indexed_files"][0]["file_type"] == "html"
        assert result["skipped_file_details"][0]["filename"] == "bad.txt"
        assert db.scalar(select(func.count(Document.id))) == 1
        assert db.scalar(select(func.count(DocumentChunk.id))) == 1
        assert len(vector_store.records) == 1
