from pathlib import Path
from math import ceil
from typing import BinaryIO

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import ChatLog, Document, DocumentChunk, Feedback
from app.services.chunking_service import ChunkingService
from app.services.document_loader import DocumentLoader, DocumentLoaderError, file_type_for_path
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.utils.file_utils import iter_supported_files, safe_upload_name


class DocumentIndexingError(RuntimeError):
    pass


class DocumentService:
    def __init__(
        self,
        settings: Settings | None = None,
        loader: DocumentLoader | None = None,
        chunker: ChunkingService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.settings = settings or get_settings()
        self.loader = loader or DocumentLoader()
        self.chunker = chunker or ChunkingService(self.settings.chunk_size, self.settings.chunk_overlap)
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore(self.settings)

    async def save_upload(self, db: Session, filename: str, file: BinaryIO) -> tuple[Document, int]:
        stored_name = safe_upload_name(filename)
        upload_path = Path(self.settings.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        stored_path = upload_path / stored_name
        with stored_path.open("wb") as output:
            output.write(file.read())
        return await self._index_file(db, stored_path, original_filename=filename, source_type="upload")

    async def index_folder(self, db: Session, folder_path: str, recursive: bool = True) -> dict:
        folder = Path(folder_path).expanduser().resolve()
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"색인할 폴더를 찾을 수 없습니다: {folder}")

        indexed = 0
        skipped = 0
        total_chunks = 0
        document_ids: list[int] = []
        indexed_files: list[dict] = []
        skipped_file_details: list[dict] = []
        for path in iter_supported_files(folder, recursive=recursive):
            try:
                document, chunks_created = await self._index_file(
                    db, path, original_filename=path.name, source_type="folder"
                )
            except ValueError as exc:
                db.rollback()
                skipped += 1
                skipped_file_details.append(
                    {
                        "path": str(path),
                        "filename": path.name,
                        "reason": str(exc),
                    }
                )
                continue
            indexed += 1
            total_chunks += chunks_created
            document_ids.append(document.id)
            indexed_files.append(
                {
                    "path": str(path),
                    "document_id": document.id,
                    "filename": path.name,
                    "file_type": file_type_for_path(path),
                    "chunks_created": chunks_created,
                }
            )
        return {
            "indexed_documents": indexed,
            "skipped_files": skipped,
            "chunks_created": total_chunks,
            "document_ids": document_ids,
            "indexed_files": indexed_files,
            "skipped_file_details": skipped_file_details,
        }

    def preview_index_folder(self, folder_path: str, recursive: bool = True) -> dict:
        folder = Path(folder_path).expanduser().resolve()
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"미리보기할 폴더를 찾을 수 없습니다: {folder}")

        files: list[dict] = []
        skipped_files: list[dict] = []
        chunks_estimated = 0
        token_estimate = 0

        for path in iter_supported_files(folder, recursive=recursive):
            try:
                text = self.loader.load_text(path)
                chunks = self.chunker.split_text(
                    text,
                    metadata={"filename": path.name, "file_type": file_type_for_path(path)},
                )
            except DocumentLoaderError as exc:
                skipped_files.append({"path": str(path), "reason": str(exc)})
                continue

            file_token_estimate = sum(chunk.token_estimate for chunk in chunks)
            file_chunks_estimated = len(chunks)
            file_embedding_batches_estimated = ceil(file_chunks_estimated / self.settings.embedding_batch_size)
            chunks_estimated += file_chunks_estimated
            token_estimate += file_token_estimate
            files.append(
                {
                    "path": str(path),
                    "filename": path.name,
                    "file_type": file_type_for_path(path),
                    "chunks_estimated": file_chunks_estimated,
                    "embedding_batches_estimated": file_embedding_batches_estimated,
                    "token_estimate": file_token_estimate,
                }
            )

        return {
            "folder_path": str(folder),
            "recursive": recursive,
            "files_count": len(files),
            "skipped_files_count": len(skipped_files),
            "chunks_estimated": chunks_estimated,
            "embedding_batch_size": self.settings.embedding_batch_size,
            "embedding_batches_estimated": ceil(chunks_estimated / self.settings.embedding_batch_size)
            if chunks_estimated
            else 0,
            "token_estimate": token_estimate,
            "files": files,
            "skipped_files": skipped_files,
            "dry_run": True,
            "note": "미리보기 전용입니다. 파일 수정, DB 저장, embedding 생성, Chroma 저장은 수행하지 않습니다.",
        }

    async def _index_file(
        self, db: Session, path: Path, original_filename: str, source_type: str
    ) -> tuple[Document, int]:
        text = self.loader.load_text(path)
        file_type = file_type_for_path(path)
        chunks = self.chunker.split_text(
            text,
            metadata={"filename": original_filename, "file_type": file_type},
        )
        embeddings = []
        if chunks:
            # Keep the SQLite write transaction short by calling Ollama before DB writes.
            embeddings = await self.embedding_service.embed_texts([chunk.content for chunk in chunks])

        try:
            document = Document(
                original_filename=original_filename,
                stored_path=str(path),
                file_type=file_type,
                source_type=source_type,
            )
            db.add(document)
            db.flush()

            chunk_rows: list[DocumentChunk] = []
            for chunk in chunks:
                row = DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    token_estimate=chunk.token_estimate,
                )
                db.add(row)
                chunk_rows.append(row)
            db.flush()

            records = [
                {
                    "chunk_id": row.id,
                    "document_id": document.id,
                    "filename": original_filename,
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                }
                for row in chunk_rows
            ]
            if records:
                self.vector_store.add_chunks(records, embeddings)

            db.commit()
            db.refresh(document)
        except Exception as exc:
            db.rollback()
            raise DocumentIndexingError(
                f"문서 색인 저장 중 오류가 발생했습니다. SQLite 변경은 rollback되었습니다: {original_filename}"
            ) from exc
        return document, len(chunk_rows)

    def get_supported_types(self) -> dict:
        return {
            "types": self.loader.supported_types(),
            "install_hint": "PDF/DOCX 지원이 unavailable이면 pip install -e '.[documents]'를 실행하세요.",
        }

    def list_documents(
        self,
        db: Session,
        source_type: str | None = None,
        file_type: str | None = None,
        query: str | None = None,
    ) -> list[dict]:
        filters = []
        if source_type:
            filters.append(Document.source_type == source_type)
        if file_type:
            filters.append(Document.file_type == file_type)
        if query:
            pattern = f"%{query.strip()}%"
            filters.append(
                or_(
                    Document.original_filename.ilike(pattern),
                    Document.stored_path.ilike(pattern),
                )
            )

        stmt = (
            select(Document, func.count(DocumentChunk.id).label("chunks_count"))
            .outerjoin(DocumentChunk)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
        )
        if filters:
            stmt = stmt.where(*filters)
        return [
            {
                "id": document.id,
                "original_filename": document.original_filename,
                "stored_path": document.stored_path,
                "file_type": document.file_type,
                "source_type": document.source_type,
                "created_at": document.created_at,
                "chunks_count": chunks_count,
            }
            for document, chunks_count in db.execute(stmt).all()
        ]

    def get_document(self, db: Session, document_id: int) -> dict | None:
        document = db.get(Document, document_id)
        if document is None:
            return None
        chunks = (
            db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
            )
            .scalars()
            .all()
        )
        return {
            "id": document.id,
            "original_filename": document.original_filename,
            "stored_path": document.stored_path,
            "file_type": document.file_type,
            "source_type": document.source_type,
            "created_at": document.created_at,
            "chunks_count": len(chunks),
            "chunks": [
                {
                    "id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_estimate": chunk.token_estimate,
                }
                for chunk in chunks
            ],
        }

    def get_document_chunks(self, db: Session, document_id: int, limit: int, offset: int) -> dict | None:
        document = db.get(Document, document_id)
        if document is None:
            return None
        total_chunks = (
            db.scalar(select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)) or 0
        )
        chunks = (
            db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(limit)
                .offset(offset)
            )
            .scalars()
            .all()
        )
        return {
            "document_id": document_id,
            "total_chunks": total_chunks,
            "limit": limit,
            "offset": offset,
            "chunks": [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_estimate": chunk.token_estimate,
                    "created_at": chunk.created_at,
                }
                for chunk in chunks
            ],
        }

    def delete_document(self, db: Session, document_id: int) -> bool:
        document = db.get(Document, document_id)
        if document is None:
            return False
        self.vector_store.delete_document(document_id)
        db.delete(document)
        db.commit()
        return True

    def get_stats(self, db: Session) -> dict:
        documents = db.execute(select(Document)).scalars().all()
        missing_files = self._missing_stored_files(documents)
        return {
            "documents_count": len(documents),
            "chunks_count": db.scalar(select(func.count(DocumentChunk.id))) or 0,
            "chat_logs_count": db.scalar(select(func.count(ChatLog.id))) or 0,
            "feedback_count": db.scalar(select(func.count(Feedback.id))) or 0,
            "chroma_vectors_count": self.vector_store.count(),
            "missing_stored_files_count": len(missing_files),
            "missing_stored_files": missing_files,
        }

    def get_integrity_report(self, db: Session) -> dict:
        documents = db.execute(select(Document)).scalars().all()
        chunks = db.execute(select(DocumentChunk)).scalars().all()
        sqlite_chunk_ids = {chunk.id for chunk in chunks}
        chroma_chunk_ids = self.vector_store.list_chunk_ids()
        missing_files = self._missing_stored_files(documents)

        chunks_missing_vectors = [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
            if chunk.id not in chroma_chunk_ids
        ]
        orphan_vector_chunk_ids = sorted(chroma_chunk_ids - sqlite_chunk_ids)
        has_issues = bool(missing_files or chunks_missing_vectors or orphan_vector_chunk_ids)

        return {
            "status": "needs_attention" if has_issues else "ok",
            "sqlite_chunks_count": len(sqlite_chunk_ids),
            "chroma_vectors_count": len(chroma_chunk_ids),
            "missing_stored_files_count": len(missing_files),
            "missing_stored_files": missing_files,
            "chunks_missing_vectors_count": len(chunks_missing_vectors),
            "chunks_missing_vectors": chunks_missing_vectors,
            "orphan_vectors_count": len(orphan_vector_chunk_ids),
            "orphan_vector_chunk_ids": orphan_vector_chunk_ids,
            "repair_available": False,
            "repair_note": "현재 endpoint는 read-only dry-run입니다. 실제 repair/delete는 사용자 승인 후 별도 구현하세요.",
        }

    def get_repair_preview(self, db: Session) -> dict:
        integrity = self.get_integrity_report(db)
        actions: list[dict] = []

        for missing_file in integrity["missing_stored_files"]:
            actions.append(
                {
                    "action": "review_missing_file",
                    "target_type": "document",
                    "target_id": missing_file["document_id"],
                    "reason": f"stored_path가 존재하지 않습니다: {missing_file['stored_path']}",
                    "requires_user_approval": True,
                }
            )

        for missing_vector in integrity["chunks_missing_vectors"]:
            actions.append(
                {
                    "action": "rebuild_vector",
                    "target_type": "chunk",
                    "target_id": missing_vector["chunk_id"],
                    "reason": "SQLite chunk는 있지만 Chroma vector가 없습니다.",
                    "requires_user_approval": True,
                }
            )

        for orphan_chunk_id in integrity["orphan_vector_chunk_ids"]:
            actions.append(
                {
                    "action": "review_orphan_vector",
                    "target_type": "chroma_vector",
                    "target_id": orphan_chunk_id,
                    "reason": "Chroma vector는 있지만 SQLite chunk가 없습니다.",
                    "requires_user_approval": True,
                }
            )

        return {
            "status": "needs_repair" if actions else "ok",
            "dry_run": True,
            "actions_count": len(actions),
            "actions": actions,
            "note": "미리보기 전용입니다. 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않습니다.",
        }

    def _missing_stored_files(self, documents: list[Document]) -> list[dict]:
        return [
            {
                "document_id": document.id,
                "filename": document.original_filename,
                "stored_path": document.stored_path,
            }
            for document in documents
            if not Path(document.stored_path).exists()
        ]
