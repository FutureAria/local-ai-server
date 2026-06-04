from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AssistantMode = Literal[
    "auto",
    "ask",
    "ask_with_docs",
    "search",
    "index_preview",
    "agent_plan",
    "shell_dry_run",
    "automation_plan",
]


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


class AssistantStartupResponse(BaseModel):
    service: str
    protected: bool
    local_only: bool
    ping: dict
    config: dict
    dashboard: dict
    ui_contract: dict
    recommended_calls: list[dict]
    safety: dict
    ui: dict


class AssistantUiContractResponse(BaseModel):
    service: str
    version: str
    protected: bool
    auth: dict
    startup_sequence: list[dict]
    refresh_endpoints: list[dict]
    message_flow: list[dict]
    response_types: dict
    safety: dict
    blocked_actions: list[str]
    notes: list[str]


class AssistantAutomationPlanRequest(BaseModel):
    goal: str = Field(default="personal API automation", min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)


class AssistantAutomationPlanResponse(BaseModel):
    service: str
    goal: str
    local_only: bool
    would_execute: bool
    current_capabilities: list[dict]
    automation_stages: list[dict]
    codex_safe_now: list[str]
    blocked_until_review: list[str]
    required_user_decisions: list[str]
    safety: dict
    ui: dict
    recommended_next_model: dict


class AssistantWorkflowPresetListResponse(BaseModel):
    service: str
    mode: str
    presets: list[dict]
    would_dispatch: bool
    execution_enabled: bool
    safety: dict
    ui: dict


class AssistantWorkflowPresetDetailResponse(BaseModel):
    service: str
    mode: str
    preset_id: str
    status: str
    preset: dict | None = None
    would_dispatch: bool
    execution_enabled: bool
    safety: dict
    ui: dict


class AssistantWorkflowPresetPreviewRequest(BaseModel):
    params: dict = Field(default_factory=dict)


class AssistantWorkflowPresetPreviewResponse(BaseModel):
    service: str
    mode: str
    preset_id: str
    status: str
    preset: dict | None = None
    frozen_proposed_steps: list[dict]
    would_dispatch: bool
    execution_enabled: bool
    blocked_reasons: list[str]
    unsafe_policy: dict
    audit: dict
    safety: dict
    ui: dict


AssistantTaskQueueStatus = Literal["queued", "running", "completed", "blocked", "cancelled"]


class AssistantTaskQueueCreateRequest(BaseModel):
    task_type: str = Field(min_length=1, max_length=120)
    params: dict = Field(default_factory=dict)
    ttl_seconds: int = Field(default=300, ge=1, le=3600)


class AssistantTaskQueueCreateResponse(BaseModel):
    service: str
    mode: str
    status: AssistantTaskQueueStatus
    task: dict | None = None
    blocked_reasons: list[str]
    allowed_task_types: list[str]
    would_enqueue: bool
    worker_enabled: bool
    execution_enabled: bool
    audit: dict
    cleanup_policy: dict
    safety: dict
    ui: dict


class AssistantTaskQueueListResponse(BaseModel):
    service: str
    mode: str
    tasks: list[dict]
    statuses: list[str]
    would_execute: bool
    worker_enabled: bool
    execution_enabled: bool
    cleanup_policy: dict
    safety: dict
    ui: dict


class AssistantTaskQueueDetailResponse(BaseModel):
    service: str
    mode: str
    task_id: str
    status: AssistantTaskQueueStatus
    task: dict | None = None
    would_execute: bool
    worker_enabled: bool
    execution_enabled: bool
    audit: dict
    safety: dict
    ui: dict


class AssistantTaskQueueCancelPreviewResponse(BaseModel):
    service: str
    mode: str
    task_id: str
    status: AssistantTaskQueueStatus
    task: dict | None = None
    cancellation: dict
    would_cancel_worker: bool
    worker_enabled: bool
    execution_enabled: bool
    audit: dict
    safety: dict
    ui: dict


class AssistantTaskQueueDrainRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)


class AssistantTaskQueueDrainResponse(BaseModel):
    service: str
    mode: str
    status: str
    worker_enabled: bool
    execution_enabled: bool
    would_execute: bool
    drained_count: int
    tasks: list[dict]
    results: list[dict]
    blocked_reasons: list[str]
    allowed_task_types: list[str]
    worker: dict
    audit: dict
    cleanup_policy: dict
    safety: dict
    ui: dict


AssistantFailureTool = Literal["patch", "shell", "browser"]


class AssistantFailureRecoveryPreviewRequest(BaseModel):
    tool: AssistantFailureTool
    failure_reason: str = Field(default="unknown_failure", min_length=1, max_length=200)
    params: dict = Field(default_factory=dict)
    original_sha256: str | None = Field(default=None, max_length=128)
    summary: str | None = Field(default=None, max_length=1000)


class AssistantFailureRecoveryPreviewResponse(BaseModel):
    service: str
    mode: str
    tool: str
    status: str
    failure: dict
    rollback_plan: dict
    manual_instructions: list[str]
    paste_safe_summary: str
    would_execute: bool
    would_apply: bool
    would_interact: bool
    rollback_enabled: bool
    execution_enabled: bool
    audit: dict
    safety: dict
    ui: dict


class AssistantRollbackApprovalPreviewRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    restored_content: str = Field(min_length=1, max_length=50000)
    project_root: str | None = Field(default=None, max_length=1024)
    current_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    original_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    params: dict = Field(default_factory=dict)
    reason: str | None = Field(default=None, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantRollbackApprovalPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    approval_required: bool
    rollback_enabled: bool
    would_apply: bool
    binding: dict
    preview: dict
    blocked_reasons: list[str]
    safety: dict
    ui: dict


class AssistantRollbackExecuteRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    restored_content: str = Field(min_length=1, max_length=50000)
    project_root: str | None = Field(default=None, max_length=1024)
    current_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    original_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)
    reason: str | None = Field(default=None, max_length=500)


class AssistantRollbackExecuteResponse(BaseModel):
    service: str
    mode: str
    status: str
    rollback_enabled: bool
    execution_enabled: bool
    would_apply: bool
    reason: str
    preview: dict
    blocked_reasons: list[str]
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    rollback_result: dict | None = None
    result_wrapper: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantReadOnlyScanRequest(BaseModel):
    project_root: str = Field(min_length=1, max_length=1024)
    max_items: int = Field(default=120, ge=1, le=500)


class AssistantReadOnlyScanResponse(BaseModel):
    service: str
    project_root: str
    resolved_path: str
    mode: str
    would_execute: bool
    summary: dict
    important_files: list[dict]
    top_level_items: list[dict]
    extension_counts: dict
    safety: dict
    ui: dict


class AssistantFilePreviewRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    project_root: str | None = Field(default=None, max_length=1024)
    max_bytes: int = Field(default=8000, ge=1, le=50000)


class AssistantFilePreviewResponse(BaseModel):
    service: str
    path: str
    resolved_path: str
    mode: str
    status: str
    would_execute: bool
    metadata: dict
    content_preview: str | None = None
    truncated: bool
    masked: bool
    safety: dict
    ui: dict


class AssistantUrlPreviewRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class AssistantUrlPreviewResponse(BaseModel):
    service: str
    url: str
    mode: str
    status: str
    would_fetch: bool
    reason: str
    safety: dict
    ui: dict


AssistantReadOnlyAdapterType = Literal["read_only_scan", "file_preview", "url_fetch"]


class AssistantReadOnlyAdapterExecuteRequest(BaseModel):
    adapter_type: AssistantReadOnlyAdapterType
    project_root: str | None = Field(default=None, max_length=1024)
    path: str | None = Field(default=None, max_length=1024)
    url: str | None = Field(default=None, max_length=2048)
    max_items: int = Field(default=120, ge=1, le=500)
    max_bytes: int = Field(default=8000, ge=1, le=50000)
    result_wrapper: dict = Field(default_factory=dict)


class AssistantReadOnlyAdapterExecuteResponse(BaseModel):
    service: str
    mode: str
    adapter_type: str
    status: str
    execution_enabled: bool
    would_read: bool
    would_fetch: bool
    adapter_executed: bool
    action_loop_dispatch_connected: bool
    result_wrapper: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantWebSearchProviderPreviewRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    provider: str | None = Field(default=None, max_length=80)
    result_wrapper: dict | None = None


class AssistantWebSearchProviderPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    provider: str | None = None
    query_preview: str
    would_search: bool
    would_fetch: bool
    external_api_enabled: bool
    provider_config: dict
    gate: dict
    result_wrapper: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantWebSearchProviderSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    provider: str | None = Field(default=None, max_length=80)
    result_wrapper: dict = Field(default_factory=lambda: {"untrusted": True})


class AssistantWebSearchProviderSearchResponse(BaseModel):
    service: str
    mode: str
    status: str
    provider: str | None = None
    query_preview: str
    would_search: bool
    would_fetch: bool
    external_api_enabled: bool
    reason: str
    provider_config: dict
    gate: dict
    search_result: dict | None = None
    result_wrapper: dict | None = None
    audit: dict
    safety: dict
    ui: dict


class AssistantAppOsInteractionPreviewRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    app_name: str | None = Field(default=None, max_length=120)
    window_title: str | None = Field(default=None, max_length=200)
    target_path: str | None = Field(default=None, max_length=1024)
    input_preview: str | None = Field(default=None, max_length=1000)
    reason: str | None = Field(default=None, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantAppOsInteractionPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    action: str
    app_name: str | None = None
    window_title: str | None = None
    target_path: str | None = None
    allowed: bool
    observe_plan_candidate: bool
    would_control_app: bool
    os_action_executed: bool
    reason: str
    taxonomy: dict
    permission_model: dict
    approval_binding: dict
    gate: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantWorkspaceBriefRequest(BaseModel):
    project_root: str = Field(min_length=1, max_length=1024)
    include_previews: bool = True


class AssistantWorkspaceBriefResponse(BaseModel):
    service: str
    project_root: str
    mode: str
    would_execute: bool
    scan: dict
    previews: list[dict]
    next_safe_actions: list[str]
    safety: dict
    ui: dict


class AssistantShellPreviewRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1000)
    cwd: str = Field(min_length=1, max_length=1024)
    timeout_seconds: int = Field(default=30, ge=1, le=120)


class AssistantShellPreviewResponse(BaseModel):
    service: str
    mode: str
    command_preview: str
    cwd: str
    resolved_cwd: str
    status: str
    would_execute: bool
    allowed: bool
    reason: str
    timeout_seconds: int
    policy: dict
    audit: dict
    output_preview: dict
    safety: dict
    ui: dict


class AssistantShellApprovalPreviewRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1000)
    cwd: str = Field(min_length=1, max_length=1024)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    reason: str | None = Field(default=None, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantShellApprovalPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    approval_required: bool
    would_execute: bool
    binding: dict
    preview: dict
    safety: dict
    ui: dict


class AssistantApprovalConsolePendingResponse(BaseModel):
    service: str
    mode: str
    status: str
    approvals: list[dict]
    count: int
    read_only: bool
    would_execute: bool
    approval_consumed: bool
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantApprovalConsoleDetailResponse(BaseModel):
    service: str
    mode: str
    status: str
    approval: dict | None = None
    read_only: bool
    would_execute: bool
    approval_consumed: bool
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantApprovalConsoleCleanupExpiredResponse(BaseModel):
    service: str
    mode: str
    status: str
    cleanup: dict
    read_only: bool
    would_execute: bool
    approval_consumed: bool
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantShellRunRequest(BaseModel):
    command: str = Field(min_length=1, max_length=1000)
    cwd: str = Field(min_length=1, max_length=1024)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantShellRunResponse(BaseModel):
    service: str
    mode: str
    status: str
    would_execute: bool
    execution_enabled: bool
    reason: str
    preview: dict
    output: dict | None = None
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    audit: dict | None = None
    safety: dict
    ui: dict


class AssistantPatchPreviewRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    proposed_content: str = Field(min_length=1, max_length=50000)
    project_root: str | None = Field(default=None, max_length=1024)
    reason: str | None = Field(default=None, max_length=500)


class AssistantPatchPreviewResponse(BaseModel):
    service: str
    mode: str
    path: str
    resolved_path: str
    status: str
    would_apply: bool
    allowed: bool
    reason: str
    diff_preview: str | None = None
    truncated: bool
    secret_scan: dict
    rollback: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantPatchApprovalPreviewRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    proposed_content: str = Field(min_length=1, max_length=50000)
    project_root: str | None = Field(default=None, max_length=1024)
    reason: str | None = Field(default=None, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantPatchApprovalPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    approval_required: bool
    would_apply: bool
    binding: dict
    preview: dict
    safety: dict
    ui: dict


class AssistantPatchApplyRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)
    proposed_content: str = Field(min_length=1, max_length=50000)
    project_root: str | None = Field(default=None, max_length=1024)
    original_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantPatchApplyResponse(BaseModel):
    service: str
    mode: str
    status: str
    would_apply: bool
    execution_enabled: bool
    reason: str
    preview: dict
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    apply_result: dict | None = None
    rollback: dict | None = None
    audit: dict | None = None
    safety: dict
    ui: dict


class AssistantBrowserPreviewRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_url: str | None = Field(default=None, max_length=2048)
    app_name: str | None = Field(default=None, max_length=120)
    selector: str | None = Field(default=None, max_length=500)
    input_preview: str | None = Field(default=None, max_length=1000)
    reason: str | None = Field(default=None, max_length=500)


class AssistantBrowserPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    action: str
    target_url: str | None = None
    app_name: str | None = None
    would_interact: bool
    allowed: bool
    reason: str
    risk: str
    required_manual_confirmation: bool
    taxonomy: dict
    gate: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantBrowserApprovalPreviewRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_url: str | None = Field(default=None, max_length=2048)
    app_name: str | None = Field(default=None, max_length=120)
    selector: str | None = Field(default=None, max_length=500)
    input_preview: str | None = Field(default=None, max_length=1000)
    reason: str | None = Field(default=None, max_length=500)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantBrowserApprovalPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    approval_required: bool
    would_interact: bool
    binding: dict
    preview: dict
    safety: dict
    ui: dict


class AssistantBrowserInteractRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_url: str | None = Field(default=None, max_length=2048)
    app_name: str | None = Field(default=None, max_length=120)
    selector: str | None = Field(default=None, max_length=500)
    input_preview: str | None = Field(default=None, max_length=1000)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantBrowserInteractResponse(BaseModel):
    service: str
    mode: str
    status: str
    would_interact: bool
    execution_enabled: bool
    reason: str
    preview: dict
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    safety: dict
    ui: dict


class AssistantBrowserObserveRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_url: str = Field(min_length=1, max_length=2048)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantBrowserObserveResponse(BaseModel):
    service: str
    mode: str
    status: str
    action: str
    target_url: str
    would_observe: bool
    execution_enabled: bool
    reason: str
    preview: dict
    observe_result: dict | None = None
    result_wrapper: dict | None = None
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    audit: dict | None = None
    safety: dict
    ui: dict


class AssistantBrowserLimitedInteractRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_url: str = Field(min_length=1, max_length=2048)
    selector: str = Field(min_length=1, max_length=500)
    field_name: str | None = Field(default=None, max_length=120)
    input_preview: str | None = Field(default=None, max_length=1000)
    approval_id: str | None = Field(default=None, max_length=64)
    approval_payload_hash: str | None = Field(default=None, max_length=128)
    session_id: str | None = Field(default=None, max_length=64)


class AssistantBrowserLimitedInteractResponse(BaseModel):
    service: str
    mode: str
    status: str
    action: str
    target_url: str
    selector: str
    would_interact: bool
    execution_enabled: bool
    reason: str
    policy: dict
    interaction_result: dict | None = None
    result_wrapper: dict | None = None
    required_approval_hash: str | None = None
    provided_approval_id: str | None = None
    provided_approval_hash: str | None = None
    approval_check: dict | None = None
    audit: dict | None = None
    safety: dict
    ui: dict


class AssistantActionLoopPreflightRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=20)
    require_wrappers: Literal[True] = True
    require_approval_bindings: Literal[True] = True


class AssistantActionLoopPreflightResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    would_dispatch: bool
    execution_enabled: bool
    fail_closed: bool
    frozen_plan: dict
    step_previews: list[dict]
    gates: dict
    required_user_decisions: list[str]
    safety: dict
    ui: dict


class AssistantActionLoopNoopDispatchRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=20)
    require_wrappers: Literal[True] = True
    require_approval_bindings: Literal[True] = True


class AssistantActionLoopNoopDispatchResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    would_dispatch: bool
    would_dispatch_noop_only: bool
    execution_enabled: bool
    fail_closed: bool
    approval_consume_mode: str
    route_plan: list[dict]
    noop_audit: dict
    preflight: dict
    gates: dict
    required_user_decisions: list[str]
    safety: dict
    ui: dict


class AssistantActionLoopReadOnlyDispatchPreviewRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=20)
    require_wrappers: Literal[True] = True


class AssistantActionLoopReadOnlyDispatchPreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    would_dispatch: bool
    would_read: bool
    would_fetch: bool
    execution_enabled: bool
    fail_closed: bool
    boundary_mode: str
    route_plan: list[dict]
    result_wrapper_schema: dict
    boundary_audit: dict
    gates: dict
    safety: dict
    ui: dict


class AssistantActionLoopReadOnlyDispatchResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    dispatched: bool
    execution_enabled: bool
    fail_closed: bool
    would_read: bool
    would_fetch: bool
    shell_execution_connected: bool
    patch_apply_connected: bool
    browser_interaction_connected: bool
    adapter_results: list[dict]
    boundary_preview: dict
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantActionLoopShellDispatchRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=20)
    require_wrappers: Literal[True] = True


class AssistantActionLoopShellDispatchResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    dispatched: bool
    execution_enabled: bool
    fail_closed: bool
    shell_execution_connected: bool
    patch_apply_connected: bool
    browser_interaction_connected: bool
    route_plan: list[dict]
    shell_results: list[dict]
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantActionLoopPatchDispatchRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=20)
    require_wrappers: Literal[True] = True


class AssistantActionLoopPatchDispatchResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    dispatched: bool
    execution_enabled: bool
    fail_closed: bool
    shell_execution_connected: bool
    patch_apply_connected: bool
    browser_interaction_connected: bool
    route_plan: list[dict]
    patch_results: list[dict]
    gates: dict
    audit: dict
    safety: dict
    ui: dict


class AssistantFullAutomationPreflightRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=40)
    session_id: str | None = Field(default=None, max_length=64)
    require_wrappers: Literal[True] = True
    require_approval_bindings: Literal[True] = True


class AssistantFullAutomationPreflightResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    would_dispatch: bool
    execution_enabled: bool
    fail_closed: bool
    full_automation_enabled: bool
    frozen_plan: dict
    route_plan: list[dict]
    tool_matrix: dict
    gates: dict
    blocked_reasons: list[str]
    result_wrapper_schema: dict
    audit: dict
    required_user_decisions: list[str]
    safety: dict
    ui: dict


class AssistantFullAutomationDispatchRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=40)
    session_id: str | None = Field(default=None, max_length=64)
    require_wrappers: Literal[True] = True
    require_approval_bindings: Literal[True] = True


class AssistantFullAutomationDispatchResponse(BaseModel):
    service: str
    mode: str
    status: str
    goal: str
    dispatched: bool
    would_dispatch: bool
    execution_enabled: bool
    fail_closed: bool
    approval_consume_mode: str
    approval_consumed: bool
    route_plan: list[dict]
    tool_results: list[dict]
    step_result_wrappers: list[dict]
    orchestrator_plan: dict
    dependency_graph: dict
    failure_strategy: dict
    rollback_strategy: dict
    preflight: dict
    gates: dict
    audit: dict
    blocked_reasons: list[str]
    safety: dict
    ui: dict


class AssistantDurableStatePreviewRequest(BaseModel):
    goal: str = Field(default="durable state preview", min_length=1, max_length=1000)
    project_root: str | None = Field(default=None, max_length=1024)
    proposed_steps: list[dict] = Field(default_factory=list, max_length=40)
    session_id: str | None = Field(default=None, max_length=64)
    request_id: str | None = Field(default=None, max_length=128)
    metadata: dict = Field(default_factory=dict)
    require_schema_only: Literal[True] = True
    require_read_only: Literal[True] = True
    require_no_persistence: Literal[True] = True


class AssistantDurableStatePreviewResponse(BaseModel):
    service: str
    mode: str
    status: str
    preview_state: dict
    candidate_steps: list[dict]
    read_only: bool
    schema_only: bool
    response_only: bool
    would_execute: bool
    would_persist: bool
    would_dispatch: bool
    approval_consumed: bool
    gates: dict
    audit: dict
    blocked_reasons: list[str]
    required_user_decisions: list[str]
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


class AssistantActionPreviewRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    project_root: str | None = Field(default=None, max_length=1024)
    mode: AssistantMode = "auto"


class AssistantActionPreviewResponse(BaseModel):
    intent: str
    recommended_endpoint: str
    would_execute: bool
    requires_approval: bool
    risk_level: str
    needs: list[str]
    safety: dict
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
