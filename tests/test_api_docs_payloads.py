import json
import re
from pathlib import Path
from typing import Any, get_args, get_origin

from pydantic import BaseModel

from app.main import app
from app.schemas.agent import AgentPlanRequest
from app.schemas.ask import AskRequest, AskWithDocsRequest
from app.schemas.assistant import (
    AssistantActionPreviewRequest,
    AssistantBootstrapRequest,
    AssistantMessageRequest,
    AssistantSessionCreateRequest,
    ProjectRootValidateRequest,
)
from app.schemas.documents import (
    DocumentIntegrityResponse,
    DocumentRepairPreviewResponse,
    DocumentStatsResponse,
    DocumentUploadResponse,
    DocumentVectorRebuildPreviewResponse,
    IndexFolderResponse,
    IndexFolderJobPreviewResponse,
    IndexFolderPreviewResponse,
    IndexFolderRequest,
    SupportedDocumentTypesResponse,
)
from app.schemas.feedback import FeedbackRequest
from app.schemas.project import ShellDryRunRequest
from app.schemas.search import SearchRequest


REQUEST_SCHEMAS: dict[str, type[BaseModel]] = {
    "/assistant/action-preview": AssistantActionPreviewRequest,
    "/assistant/bootstrap": AssistantBootstrapRequest,
    "/assistant/sessions": AssistantSessionCreateRequest,
    "/assistant/message": AssistantMessageRequest,
    "/assistant/project-root/validate": ProjectRootValidateRequest,
    "/ask": AskRequest,
    "/ask-with-docs": AskWithDocsRequest,
    "/documents/index-folder-preview": IndexFolderRequest,
    "/documents/index-folder-job-preview": IndexFolderRequest,
    "/documents/index-folder": IndexFolderRequest,
    "/search": SearchRequest,
    "/feedback": FeedbackRequest,
    "/agent/plan": AgentPlanRequest,
    "/project/shell-dry-run": ShellDryRunRequest,
}


def _response_model_fields(response_model: Any) -> set[str]:
    origin = get_origin(response_model)
    if origin is list:
        args = get_args(response_model)
        response_model = args[0] if args else None
    if isinstance(response_model, type) and issubclass(response_model, BaseModel):
        return set(response_model.model_fields)
    return set()


def _runtime_response_fields_by_endpoint() -> dict[str, set[str]]:
    fields_by_endpoint: dict[str, set[str]] = {}
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) - {"HEAD", "OPTIONS"}
        response_fields = _response_model_fields(getattr(route, "response_model", None))
        if not path or not methods or not response_fields:
            continue
        for method in methods:
            fields_by_endpoint[f"{method} {path}"] = response_fields
    return fields_by_endpoint


def _extract_documented_response_fields(text: str) -> dict[str, set[str]]:
    headings = list(re.finditer(r"^### `(?P<method>[A-Z]+) (?P<path>[^`]+)`", text, flags=re.M))
    documented: dict[str, set[str]] = {}
    for index, heading in enumerate(headings):
        section_start = heading.end()
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[section_start:section_end]
        marker = "응답 핵심 필드:"
        if marker not in section:
            continue

        fields: set[str] = set()
        for line in section.split(marker, 1)[1].splitlines():
            if not line.strip():
                continue
            if not line.startswith("- `"):
                if fields:
                    break
                continue
            raw_field = line.strip()[2:].strip("`")
            fields.add(_top_level_response_field(raw_field))

        if fields:
            endpoint = f"{heading.group('method')} {heading.group('path')}"
            documented[endpoint] = fields
    return documented


def _top_level_response_field(raw_field: str) -> str:
    field = raw_field.split("=", 1)[0]
    field = field.split(".", 1)[0]
    field = field.split("[]", 1)[0]
    return field


def _extract_post_payload_examples(text: str) -> list[tuple[str, dict[str, Any]]]:
    examples: list[tuple[str, dict[str, Any]]] = []
    for block in re.findall(r"```bash\n(.*?)\n```", text, flags=re.S):
        if "-d '" not in block:
            continue
        path_match = re.search(r"http://127\.0\.0\.1:8000(?P<path>/[^\s\"']+)", block)
        payload_match = re.search(r"-d '(?P<payload>\{.*?\})'", block, flags=re.S)
        if not path_match or not payload_match:
            continue
        payload = json.loads(payload_match.group("payload"))
        examples.append((path_match.group("path"), payload))
    return examples


def _json_block_after_endpoint_heading(text: str, endpoint: str) -> dict[str, Any]:
    pattern = rf"### `{re.escape(endpoint)}`.*?```json\n(.*?)\n```"
    match = re.search(pattern, text, flags=re.S)
    assert match, f"JSON block for {endpoint} not found"
    return json.loads(match.group(1))


def test_api_docs_post_payload_examples_match_request_schemas() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    examples = _extract_post_payload_examples(text)

    assert examples, "docs/API.md should include POST payload examples"
    seen_paths = {path for path, _ in examples}

    for path, payload in examples:
        schema = REQUEST_SCHEMAS.get(path)
        if schema is None:
            continue
        schema.model_validate(payload)

    documented_schema_paths = set(REQUEST_SCHEMAS)
    assert documented_schema_paths <= seen_paths


def test_api_docs_index_job_preview_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "POST /documents/index-folder-job-preview")
    validated = IndexFolderJobPreviewResponse.model_validate(example)

    assert validated.job_id == "preview-only"
    assert validated.status == "planned"
    assert validated.dry_run is True
    assert validated.would_enqueue is False
    assert validated.progress.processed_files == 0
    assert validated.progress.embedding_batches_completed == 0
    assert validated.progress.percent == 0
    assert "queue 생성" in validated.note


def test_api_docs_document_upload_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "POST /documents/upload")
    validated = DocumentUploadResponse.model_validate(example)

    assert validated.document_id == 1
    assert validated.filename == "backend.md"
    assert validated.chunks_created == 3


def test_api_docs_index_folder_preview_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "POST /documents/index-folder-preview")
    validated = IndexFolderPreviewResponse.model_validate(example)

    assert validated.folder_path == "/Users/example/notes"
    assert validated.recursive is True
    assert validated.files_count == 2
    assert validated.skipped_files_count == 1
    assert validated.chunks_estimated == 5
    assert validated.embedding_batches_estimated == 1
    assert validated.dry_run is True
    assert {file.file_type for file in validated.files} == {"md", "txt"}
    assert validated.skipped_files[0].path.endswith("broken.pdf")
    assert "embedding 생성" in validated.note


def test_api_docs_index_folder_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "POST /documents/index-folder")
    validated = IndexFolderResponse.model_validate(example)

    assert validated.indexed_documents == 2
    assert validated.skipped_files == 1
    assert validated.chunks_created == 5
    assert validated.document_ids == [10, 11]
    assert {file.file_type for file in validated.indexed_files} == {"md", "txt"}
    assert validated.indexed_files[0].filename == "backend.md"
    assert validated.skipped_file_details[0].filename == "empty.md"


def test_api_docs_supported_types_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "GET /documents/supported-types")
    validated = SupportedDocumentTypesResponse.model_validate(example)

    extensions = {item.extension for item in validated.types}
    assert {".txt", ".md", ".html", ".pdf", ".docx"} <= extensions
    assert any(item.extension == ".pdf" and "OCR fallback" in item.description for item in validated.types)
    assert any(item.optional_dependency == "python-docx" and not item.available for item in validated.types)
    assert validated.pdf_ocr is False
    assert validated.pdf_ocr_install_hint is not None
    assert "tesseract" in validated.pdf_ocr_install_hint


def test_api_docs_document_stats_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "GET /documents/stats")
    validated = DocumentStatsResponse.model_validate(example)

    assert validated.documents_count == 3
    assert validated.chunks_count == 12
    assert validated.chroma_vectors_count == 12
    assert validated.missing_stored_files_count == 0
    assert validated.missing_stored_files == []


def test_api_docs_document_integrity_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "GET /documents/integrity")
    validated = DocumentIntegrityResponse.model_validate(example)

    assert validated.status == "needs_attention"
    assert validated.sqlite_chunks_count == 12
    assert validated.chroma_vectors_count == 11
    assert validated.missing_stored_files_count == 1
    assert validated.chunks_missing_vectors_count == 1
    assert validated.orphan_vectors_count == 1
    assert validated.repair_available is False
    assert "read-only dry-run" in validated.repair_note


def test_api_docs_vector_rebuild_preview_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "GET /documents/vector-rebuild-preview")
    validated = DocumentVectorRebuildPreviewResponse.model_validate(example)

    assert validated.status == "needs_rebuild"
    assert validated.dry_run is True
    assert validated.chunks_missing_vectors_count == 2
    assert validated.embedding_batches_estimated == 1
    assert validated.actions_count == 2
    assert all(action.action == "rebuild_vector" for action in validated.actions)
    assert all(action.requires_user_approval for action in validated.actions)
    assert "실제 Ollama embedding 생성" in validated.note


def test_api_docs_repair_preview_response_example_matches_schema() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    example = _json_block_after_endpoint_heading(text, "GET /documents/repair-preview")
    validated = DocumentRepairPreviewResponse.model_validate(example)

    assert validated.status == "needs_repair"
    assert validated.dry_run is True
    assert validated.actions_count == 3
    assert {action.action for action in validated.actions} == {
        "review_missing_file",
        "rebuild_vector",
        "review_orphan_vector",
    }
    assert all(action.requires_user_approval for action in validated.actions)
    assert "실제 파일 삭제" in validated.note


def test_api_docs_response_core_fields_match_response_models() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    runtime_fields = _runtime_response_fields_by_endpoint()
    documented_fields = _extract_documented_response_fields(text)

    assert documented_fields, "docs/API.md should include response field summaries"
    checked_endpoints = 0
    for endpoint, fields in documented_fields.items():
        if endpoint not in runtime_fields:
            continue
        checked_endpoints += 1
        invalid_fields = fields - runtime_fields[endpoint]
        assert not invalid_fields, f"{endpoint} documents fields not present in response model: {sorted(invalid_fields)}"

    assert checked_endpoints >= 10


def test_api_docs_top_level_sections_have_expected_order() -> None:
    text = Path("docs/API.md").read_text(encoding="utf-8")
    headings = [match.group(1) for match in re.finditer(r"^## (.+)$", text, flags=re.M)]

    expected_order = [
        "인증",
        "Rate Limit",
        "CORS",
        "Health",
        "Project Status",
        "Assistant",
        "Ask",
        "Documents",
        "Search",
        "Chat Logs",
        "Feedback",
        "Agent",
        "CLI 대응",
        "Smoke Script",
        "Local CI Check",
    ]
    positions = {heading: headings.index(heading) for heading in expected_order}

    assert len(headings) == len(set(headings))
    assert [positions[heading] for heading in expected_order] == sorted(positions.values())
    assert positions["Assistant"] < positions["Ask"] < positions["Documents"]
    ask_section = text.split("## Ask", 1)[1].split("## Documents", 1)[0]
    assert "### `POST /ask`" in ask_section
    assert "### `POST /ask-with-docs`" in ask_section
