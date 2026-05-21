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
from app.schemas.documents import IndexFolderRequest
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
