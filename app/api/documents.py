from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_document_service, require_api_key
from app.db.database import get_db
from app.schemas.documents import (
    DocumentDetail,
    DocumentChunksResponse,
    DocumentIntegrityResponse,
    DocumentRepairPreviewResponse,
    DocumentStatsResponse,
    DocumentSummary,
    DocumentUploadResponse,
    DocumentVectorRebuildPreviewResponse,
    IndexFolderJobPreviewResponse,
    IndexFolderPreviewResponse,
    IndexFolderRequest,
    IndexFolderResponse,
    SupportedDocumentTypesResponse,
)
from app.services.document_loader import DocumentLoaderError
from app.services.document_service import DocumentIndexingError, DocumentService
from app.services.ollama_client import OllamaError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, dependencies=[Depends(require_api_key)])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    try:
        document, chunks_created = await document_service.save_upload(db, file.filename or "uploaded.txt", file.file)
    except DocumentLoaderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except DocumentIndexingError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.original_filename,
        chunks_created=chunks_created,
    )


@router.get("", response_model=list[DocumentSummary])
def list_documents(
    source_type: str | None = Query(default=None, pattern="^(upload|folder)$"),
    file_type: str | None = Query(default=None, pattern="^(txt|md|pdf|docx|html)$"),
    query: str | None = Query(default=None, min_length=1, max_length=200),
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> list[dict]:
    return document_service.list_documents(db, source_type=source_type, file_type=file_type, query=query)


@router.get("/supported-types", response_model=SupportedDocumentTypesResponse)
def supported_document_types(
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    return document_service.get_supported_types()


@router.get("/stats", response_model=DocumentStatsResponse)
def document_stats(
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    return document_service.get_stats(db)


@router.get("/integrity", response_model=DocumentIntegrityResponse)
def document_integrity(
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    return document_service.get_integrity_report(db)


@router.get("/repair-preview", response_model=DocumentRepairPreviewResponse)
def document_repair_preview(
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    return document_service.get_repair_preview(db)


@router.get("/vector-rebuild-preview", response_model=DocumentVectorRebuildPreviewResponse)
def document_vector_rebuild_preview(
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    return document_service.get_vector_rebuild_preview(db)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    document = document_service.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문서를 찾을 수 없습니다.")
    return document


@router.get("/{document_id}/chunks", response_model=DocumentChunksResponse)
def get_document_chunks(
    document_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    chunks = document_service.get_document_chunks(db, document_id, limit=limit, offset=offset)
    if chunks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문서를 찾을 수 없습니다.")
    return chunks


@router.delete("/{document_id}", dependencies=[Depends(require_api_key)])
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    deleted = document_service.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문서를 찾을 수 없습니다.")
    return {"deleted": True, "document_id": document_id}


@router.post("/index-folder", response_model=IndexFolderResponse, dependencies=[Depends(require_api_key)])
async def index_folder(
    request: IndexFolderRequest,
    db: Session = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    try:
        return await document_service.index_folder(db, request.folder_path, recursive=request.recursive)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except DocumentIndexingError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/index-folder-preview", response_model=IndexFolderPreviewResponse, dependencies=[Depends(require_api_key)])
def index_folder_preview(
    request: IndexFolderRequest,
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    try:
        return document_service.preview_index_folder(request.folder_path, recursive=request.recursive)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/index-folder-job-preview",
    response_model=IndexFolderJobPreviewResponse,
    dependencies=[Depends(require_api_key)],
)
def index_folder_job_preview(
    request: IndexFolderRequest,
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    try:
        preview = document_service.preview_index_folder(request.folder_path, recursive=request.recursive)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    total_files = preview["files_count"]
    return {
        "job_id": "preview-only",
        "status": "planned",
        "folder_path": preview["folder_path"],
        "recursive": preview["recursive"],
        "dry_run": True,
        "would_enqueue": False,
        "progress": {
            "total_files": total_files,
            "processed_files": 0,
            "indexed_documents": 0,
            "skipped_files": preview["skipped_files_count"],
            "chunks_created": 0,
            "embedding_batches_total": preview["embedding_batches_estimated"],
            "embedding_batches_completed": 0,
            "percent": 0,
        },
        "status_endpoint": "/documents/index-jobs/{job_id}",
        "note": (
            "대용량 색인 job/status API의 preview-only 응답입니다. "
            "현재 요청은 queue 생성, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않습니다."
        ),
    }
