from datetime import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    chunks_created: int


class DocumentSummary(BaseModel):
    id: int
    original_filename: str
    stored_path: str
    file_type: str
    source_type: str
    created_at: datetime
    chunks_count: int = 0


class SupportedDocumentType(BaseModel):
    extension: str
    file_type: str
    available: bool
    optional_dependency: str | None
    install_hint: str | None
    description: str


class SupportedDocumentTypesResponse(BaseModel):
    types: list[SupportedDocumentType]
    install_hint: str
    pdf_ocr: bool = False
    pdf_ocr_install_hint: str | None = None


class DocumentDetail(DocumentSummary):
    chunks: list[dict]


class DocumentChunkItem(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_estimate: int
    created_at: datetime


class DocumentChunksResponse(BaseModel):
    document_id: int
    total_chunks: int
    limit: int
    offset: int
    chunks: list[DocumentChunkItem]


class IndexFolderRequest(BaseModel):
    folder_path: str = Field(min_length=1)
    recursive: bool = True


class IndexFolderResponse(BaseModel):
    indexed_documents: int
    skipped_files: int
    chunks_created: int
    document_ids: list[int]
    indexed_files: list["IndexFolderIndexedFile"] = Field(default_factory=list)
    skipped_file_details: list["IndexFolderSkippedFile"] = Field(default_factory=list)


class IndexFolderIndexedFile(BaseModel):
    path: str
    document_id: int
    filename: str
    file_type: str
    chunks_created: int


class IndexFolderSkippedFile(BaseModel):
    path: str
    filename: str
    reason: str


class IndexFolderPreviewFile(BaseModel):
    path: str
    filename: str
    file_type: str
    chunks_estimated: int
    embedding_batches_estimated: int
    token_estimate: int


class IndexFolderPreviewSkippedFile(BaseModel):
    path: str
    reason: str


class IndexFolderPreviewResponse(BaseModel):
    folder_path: str
    recursive: bool
    files_count: int
    skipped_files_count: int
    chunks_estimated: int
    embedding_batch_size: int
    embedding_batches_estimated: int
    token_estimate: int
    files: list[IndexFolderPreviewFile]
    skipped_files: list[IndexFolderPreviewSkippedFile]
    dry_run: bool = True
    note: str


class IndexJobProgress(BaseModel):
    total_files: int
    processed_files: int
    indexed_documents: int
    skipped_files: int
    chunks_created: int
    embedding_batches_total: int
    embedding_batches_completed: int
    percent: float = Field(ge=0, le=100)


class IndexFolderJobPreviewResponse(BaseModel):
    job_id: str
    status: str
    folder_path: str
    recursive: bool
    dry_run: bool = True
    would_enqueue: bool = False
    progress: IndexJobProgress
    status_endpoint: str
    note: str


class DocumentStatsResponse(BaseModel):
    documents_count: int
    chunks_count: int
    chat_logs_count: int
    feedback_count: int
    chroma_vectors_count: int
    missing_stored_files_count: int
    missing_stored_files: list[dict]


class DocumentIntegrityResponse(BaseModel):
    status: str
    sqlite_chunks_count: int
    chroma_vectors_count: int
    missing_stored_files_count: int
    missing_stored_files: list[dict]
    chunks_missing_vectors_count: int
    chunks_missing_vectors: list[dict]
    orphan_vectors_count: int
    orphan_vector_chunk_ids: list[int]
    repair_available: bool
    repair_note: str


class RepairPreviewAction(BaseModel):
    action: str
    target_type: str
    target_id: int | str
    reason: str
    requires_user_approval: bool = True


class DocumentRepairPreviewResponse(BaseModel):
    status: str
    dry_run: bool
    actions_count: int
    actions: list[RepairPreviewAction]
    note: str


class DocumentVectorRebuildPreviewResponse(BaseModel):
    status: str
    dry_run: bool
    chunks_missing_vectors_count: int
    embedding_batch_size: int
    embedding_batches_estimated: int
    actions_count: int
    actions: list[RepairPreviewAction]
    note: str
