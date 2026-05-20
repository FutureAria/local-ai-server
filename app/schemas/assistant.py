from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AssistantMode = Literal["auto", "ask", "ask_with_docs", "search", "index_preview", "agent_plan", "shell_dry_run"]


class AssistantCapabilitiesResponse(BaseModel):
    service: str
    modes: list[str]
    protected: bool
    local_only: bool
    llm_provider: str
    vector_store: str
    storage: str
    safe_defaults: dict
    endpoints: dict


class AssistantSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    project_root: str | None = Field(default=None, max_length=1024)


class AssistantSessionResponse(BaseModel):
    session_id: str
    title: str
    project_root: str | None
    created_at: datetime
    updated_at: datetime
    messages: list["AssistantMessageItem"] = Field(default_factory=list)


class AssistantSessionSummary(BaseModel):
    session_id: str
    title: str
    project_root: str | None
    created_at: datetime
    updated_at: datetime
    messages_count: int
    last_message_preview: str | None = None


class AssistantSessionListResponse(BaseModel):
    sessions: list[AssistantSessionSummary]
    limit: int
    offset: int


class AssistantMessageListResponse(BaseModel):
    session_id: str
    total_messages: int
    limit: int
    offset: int
    messages: list["AssistantMessageItem"]


class AssistantStatusResponse(BaseModel):
    service: str
    current_phase: dict
    documents: dict
    integrity: dict
    sessions: dict
    safety: dict


class AssistantPingResponse(BaseModel):
    status: str
    service: str
    protected: bool
    local_only: bool
    ui_ready: bool


class AssistantConfigResponse(BaseModel):
    service: str
    protected: bool
    local_only: bool
    cors_origins: list[str]
    allowed_roots: list[dict]
    models: dict
    storage: dict
    safety: dict
    rate_limit: dict


class AssistantDashboardResponse(BaseModel):
    service: str
    current_phase: dict
    cards: dict
    recent_sessions: list[dict]
    safety: dict
    ui: dict


class AssistantBootstrapRequest(BaseModel):
    project_root: str | None = Field(default=None, max_length=1024)
    include_sessions: bool = True
    sessions_limit: int = Field(default=10, ge=1, le=50)


class AssistantBootstrapResponse(BaseModel):
    service: str
    capabilities: dict
    status: dict
    project_root: dict | None = None
    sessions: dict | None = None
    recommended_calls: list[dict]
    ui: dict


class AssistantMessageItem(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    payload: dict | None = None
    created_at: datetime


class AssistantMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=64)
    project_root: str | None = Field(default=None, max_length=1024)
    mode: AssistantMode = "auto"
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)


class AssistantMessageResponse(BaseModel):
    session_id: str
    type: str
    answer: str | None = None
    data: dict | list | None = None
    used_documents: bool = False
    sources: list[dict] = Field(default_factory=list)
    request_id: str | None = None
    safety: dict
    ui: dict = Field(default_factory=dict)


class ProjectRootValidateRequest(BaseModel):
    project_root: str = Field(min_length=1, max_length=1024)


class ProjectRootValidateResponse(BaseModel):
    project_root: str
    resolved_path: str
    exists: bool
    is_dir: bool
    inside_allowed_roots: bool
    allowed_roots: list[str]
    safe_for_read_only_agent: bool
    message: str
