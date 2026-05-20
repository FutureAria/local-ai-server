import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

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
