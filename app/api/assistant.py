from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_assistant_service, require_api_key
from app.db.database import get_db
from app.schemas.assistant import (
    AssistantCapabilitiesResponse,
    AssistantActionPreviewRequest,
    AssistantActionPreviewResponse,
    AssistantActionLoopNoopDispatchRequest,
    AssistantActionLoopNoopDispatchResponse,
    AssistantActionLoopPatchDispatchRequest,
    AssistantActionLoopPatchDispatchResponse,
    AssistantActionLoopPreflightRequest,
    AssistantActionLoopPreflightResponse,
    AssistantActionLoopReadOnlyDispatchPreviewRequest,
    AssistantActionLoopReadOnlyDispatchPreviewResponse,
    AssistantActionLoopReadOnlyDispatchResponse,
    AssistantActionLoopShellDispatchRequest,
    AssistantActionLoopShellDispatchResponse,
    AssistantApprovalConsoleCleanupExpiredResponse,
    AssistantApprovalConsoleDetailResponse,
    AssistantApprovalConsolePendingResponse,
    AssistantAutomationPlanRequest,
    AssistantAutomationPlanResponse,
    AssistantAppOsInteractionPreviewRequest,
    AssistantAppOsInteractionPreviewResponse,
    AssistantBrowserApprovalPreviewRequest,
    AssistantBrowserApprovalPreviewResponse,
    AssistantBrowserInteractRequest,
    AssistantBrowserInteractResponse,
    AssistantBrowserLimitedInteractRequest,
    AssistantBrowserLimitedInteractResponse,
    AssistantBrowserObserveRequest,
    AssistantBrowserObserveResponse,
    AssistantBrowserPreviewRequest,
    AssistantBrowserPreviewResponse,
    AssistantBootstrapRequest,
    AssistantBootstrapResponse,
    AssistantConfigResponse,
    AssistantDashboardResponse,
    AssistantDurableStatePreviewRequest,
    AssistantDurableStatePreviewResponse,
    AssistantFailureRecoveryPreviewRequest,
    AssistantFailureRecoveryPreviewResponse,
    AssistantFilePreviewRequest,
    AssistantFilePreviewResponse,
    AssistantFullAutomationDispatchRequest,
    AssistantFullAutomationDispatchResponse,
    AssistantFullAutomationPreflightRequest,
    AssistantFullAutomationPreflightResponse,
    AssistantMessageListResponse,
    AssistantMessageRequest,
    AssistantMessageResponse,
    AssistantPatchApplyRequest,
    AssistantPatchApplyResponse,
    AssistantPatchApprovalPreviewRequest,
    AssistantPatchApprovalPreviewResponse,
    AssistantPatchPreviewRequest,
    AssistantPatchPreviewResponse,
    AssistantPingResponse,
    AssistantReadOnlyScanRequest,
    AssistantReadOnlyScanResponse,
    AssistantReadOnlyAdapterExecuteRequest,
    AssistantReadOnlyAdapterExecuteResponse,
    AssistantRollbackApprovalPreviewRequest,
    AssistantRollbackApprovalPreviewResponse,
    AssistantRollbackExecuteRequest,
    AssistantRollbackExecuteResponse,
    AssistantShellApprovalPreviewRequest,
    AssistantShellApprovalPreviewResponse,
    AssistantShellPreviewRequest,
    AssistantShellPreviewResponse,
    AssistantShellRunRequest,
    AssistantShellRunResponse,
    AssistantSessionCreateRequest,
    AssistantSessionListResponse,
    AssistantSessionResponse,
    AssistantStartupResponse,
    AssistantStatusResponse,
    AssistantTaskQueueCancelPreviewResponse,
    AssistantTaskQueueCreateRequest,
    AssistantTaskQueueCreateResponse,
    AssistantTaskQueueDetailResponse,
    AssistantTaskQueueDrainRequest,
    AssistantTaskQueueDrainResponse,
    AssistantTaskQueueListResponse,
    AssistantUiContractResponse,
    AssistantUrlPreviewRequest,
    AssistantUrlPreviewResponse,
    AssistantWebSearchProviderPreviewRequest,
    AssistantWebSearchProviderPreviewResponse,
    AssistantWebSearchProviderSearchRequest,
    AssistantWebSearchProviderSearchResponse,
    AssistantWorkflowPresetDetailResponse,
    AssistantWorkflowPresetListResponse,
    AssistantWorkflowPresetPreviewRequest,
    AssistantWorkflowPresetPreviewResponse,
    AssistantWorkspaceBriefRequest,
    AssistantWorkspaceBriefResponse,
    ProjectRootValidateRequest,
    ProjectRootValidateResponse,
)
from app.services.assistant_service import AssistantService, session_to_response
from app.services.document_loader import DocumentLoaderError
from app.services.ollama_client import OllamaError

router = APIRouter(prefix="/assistant", tags=["assistant"], dependencies=[Depends(require_api_key)])


@router.get("/capabilities", response_model=AssistantCapabilitiesResponse)
def assistant_capabilities(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.capabilities()


@router.post("/action-preview", response_model=AssistantActionPreviewResponse)
def assistant_action_preview(
    request: AssistantActionPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_preview(request)


@router.post("/action-loop-preflight", response_model=AssistantActionLoopPreflightResponse)
def assistant_action_loop_preflight(
    request: AssistantActionLoopPreflightRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_preflight(request)


@router.post("/action-loop-noop-dispatch", response_model=AssistantActionLoopNoopDispatchResponse)
def assistant_action_loop_noop_dispatch(
    request: AssistantActionLoopNoopDispatchRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_noop_dispatch(request)


@router.post("/action-loop-read-only-dispatch-preview", response_model=AssistantActionLoopReadOnlyDispatchPreviewResponse)
def assistant_action_loop_read_only_dispatch_preview(
    request: AssistantActionLoopReadOnlyDispatchPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_read_only_dispatch_preview(request)


@router.post("/action-loop-read-only-dispatch", response_model=AssistantActionLoopReadOnlyDispatchResponse)
def assistant_action_loop_read_only_dispatch(
    request: AssistantActionLoopReadOnlyDispatchPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_read_only_dispatch(request)


@router.post("/action-loop-shell-dispatch", response_model=AssistantActionLoopShellDispatchResponse)
def assistant_action_loop_shell_dispatch(
    request: AssistantActionLoopShellDispatchRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_shell_dispatch(request)


@router.post("/action-loop-patch-dispatch", response_model=AssistantActionLoopPatchDispatchResponse)
def assistant_action_loop_patch_dispatch(
    request: AssistantActionLoopPatchDispatchRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.action_loop_patch_dispatch(request)


@router.post("/full-automation-preflight", response_model=AssistantFullAutomationPreflightResponse)
def assistant_full_automation_preflight(
    request: AssistantFullAutomationPreflightRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.full_automation_preflight(request)


@router.post("/full-automation-dispatch", response_model=AssistantFullAutomationDispatchResponse)
def assistant_full_automation_dispatch(
    request: AssistantFullAutomationDispatchRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.full_automation_dispatch(request)


@router.post("/durable-state-preview/preview", response_model=AssistantDurableStatePreviewResponse)
def assistant_durable_state_preview(
    request: AssistantDurableStatePreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.durable_state_preview(request)


@router.post("/automation-plan", response_model=AssistantAutomationPlanResponse)
def assistant_automation_plan(
    request: AssistantAutomationPlanRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.automation_plan(request)


@router.get("/workflow-presets", response_model=AssistantWorkflowPresetListResponse)
def assistant_workflow_presets(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.workflow_presets()


@router.get("/workflow-presets/{preset_id}", response_model=AssistantWorkflowPresetDetailResponse)
def assistant_workflow_preset_detail(
    preset_id: str,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.workflow_preset_detail(preset_id)


@router.post("/workflow-presets/{preset_id}/preview", response_model=AssistantWorkflowPresetPreviewResponse)
def assistant_workflow_preset_preview(
    preset_id: str,
    request: AssistantWorkflowPresetPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.workflow_preset_preview(preset_id, request)


@router.post("/task-queue/preview", response_model=AssistantTaskQueueCreateResponse)
def assistant_task_queue_preview(
    request: AssistantTaskQueueCreateRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.task_queue_preview(request)


@router.get("/task-queue", response_model=AssistantTaskQueueListResponse)
def assistant_task_queue(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.task_queue()


@router.post("/task-queue/drain", response_model=AssistantTaskQueueDrainResponse)
def assistant_task_queue_drain(
    request: AssistantTaskQueueDrainRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.task_queue_drain(request)


@router.get("/task-queue/{task_id}", response_model=AssistantTaskQueueDetailResponse)
def assistant_task_queue_detail(
    task_id: str,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.task_queue_detail(task_id)


@router.post("/task-queue/{task_id}/cancel-preview", response_model=AssistantTaskQueueCancelPreviewResponse)
def assistant_task_queue_cancel_preview(
    task_id: str,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.task_queue_cancel_preview(task_id)


@router.post("/failure-recovery-preview", response_model=AssistantFailureRecoveryPreviewResponse)
def assistant_failure_recovery_preview(
    request: AssistantFailureRecoveryPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.failure_recovery_preview(request)


@router.post("/rollback-approval-preview", response_model=AssistantRollbackApprovalPreviewResponse)
def assistant_rollback_approval_preview(
    request: AssistantRollbackApprovalPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.rollback_approval_preview(request)


@router.post("/rollback-execute", response_model=AssistantRollbackExecuteResponse)
def assistant_rollback_execute(
    request: AssistantRollbackExecuteRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.rollback_execute(request)


@router.post("/read-only-scan", response_model=AssistantReadOnlyScanResponse)
def assistant_read_only_scan(
    request: AssistantReadOnlyScanRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.read_only_scan(request)


@router.post("/file-preview", response_model=AssistantFilePreviewResponse)
def assistant_file_preview(
    request: AssistantFilePreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.file_preview(request)


@router.post("/url-preview", response_model=AssistantUrlPreviewResponse)
def assistant_url_preview(
    request: AssistantUrlPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.url_preview(request)


@router.post("/read-only-adapter/execute", response_model=AssistantReadOnlyAdapterExecuteResponse)
def assistant_read_only_adapter_execute(
    request: AssistantReadOnlyAdapterExecuteRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.read_only_adapter_execute(request)


@router.post("/web-search-provider-preview", response_model=AssistantWebSearchProviderPreviewResponse)
def assistant_web_search_provider_preview(
    request: AssistantWebSearchProviderPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.web_search_provider_preview(request)


@router.post("/web-search-provider/search", response_model=AssistantWebSearchProviderSearchResponse)
def assistant_web_search_provider_search(
    request: AssistantWebSearchProviderSearchRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.web_search_provider_search(request)


@router.post("/app-os-interaction-preview", response_model=AssistantAppOsInteractionPreviewResponse)
def assistant_app_os_interaction_preview(
    request: AssistantAppOsInteractionPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.app_os_interaction_preview(request)


@router.post("/workspace-brief", response_model=AssistantWorkspaceBriefResponse)
def assistant_workspace_brief(
    request: AssistantWorkspaceBriefRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.workspace_brief(request)


@router.post("/shell-preview", response_model=AssistantShellPreviewResponse)
def assistant_shell_preview(
    request: AssistantShellPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.shell_preview(request)


@router.post("/shell-approval-preview", response_model=AssistantShellApprovalPreviewResponse)
def assistant_shell_approval_preview(
    request: AssistantShellApprovalPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.shell_approval_preview(request)


@router.get("/approval-console/pending", response_model=AssistantApprovalConsolePendingResponse)
def assistant_approval_console_pending(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.approval_console_pending()


@router.get("/approval-console/{approval_id}", response_model=AssistantApprovalConsoleDetailResponse)
def assistant_approval_console_detail(
    approval_id: str,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.approval_console_detail(approval_id)


@router.post("/approval-console/cleanup-expired", response_model=AssistantApprovalConsoleCleanupExpiredResponse)
def assistant_approval_console_cleanup_expired(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.approval_console_cleanup_expired()


@router.post("/shell-run", response_model=AssistantShellRunResponse)
def assistant_shell_run(
    request: AssistantShellRunRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.shell_run(request)


@router.post("/patch-preview", response_model=AssistantPatchPreviewResponse)
def assistant_patch_preview(
    request: AssistantPatchPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.patch_preview(request)


@router.post("/patch-approval-preview", response_model=AssistantPatchApprovalPreviewResponse)
def assistant_patch_approval_preview(
    request: AssistantPatchApprovalPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.patch_approval_preview(request)


@router.post("/patch-apply", response_model=AssistantPatchApplyResponse)
def assistant_patch_apply(
    request: AssistantPatchApplyRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.patch_apply(request)


@router.post("/browser-preview", response_model=AssistantBrowserPreviewResponse)
def assistant_browser_preview(
    request: AssistantBrowserPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.browser_preview(request)


@router.post("/browser-approval-preview", response_model=AssistantBrowserApprovalPreviewResponse)
def assistant_browser_approval_preview(
    request: AssistantBrowserApprovalPreviewRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.browser_approval_preview(request)


@router.post("/browser-interact", response_model=AssistantBrowserInteractResponse)
def assistant_browser_interact(
    request: AssistantBrowserInteractRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.browser_interact(request)


@router.post("/browser-observe", response_model=AssistantBrowserObserveResponse)
def assistant_browser_observe(
    request: AssistantBrowserObserveRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.browser_observe(request)


@router.post("/browser-limited-interact", response_model=AssistantBrowserLimitedInteractResponse)
def assistant_browser_limited_interact(
    request: AssistantBrowserLimitedInteractRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.browser_limited_interact(request)


@router.get("/ui-contract", response_model=AssistantUiContractResponse)
def assistant_ui_contract(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.ui_contract()


@router.get("/startup", response_model=AssistantStartupResponse)
def assistant_startup(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.startup(db)


@router.get("/ping", response_model=AssistantPingResponse)
def assistant_ping(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.ping()


@router.get("/config", response_model=AssistantConfigResponse)
def assistant_config(
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.config()


@router.get("/status", response_model=AssistantStatusResponse)
def assistant_status(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.status(db)


@router.get("/dashboard", response_model=AssistantDashboardResponse)
def assistant_dashboard(
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.dashboard(db)


@router.post("/bootstrap", response_model=AssistantBootstrapResponse)
def assistant_bootstrap(
    request: AssistantBootstrapRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.bootstrap(
        db,
        project_root=request.project_root,
        include_sessions=request.include_sessions,
        sessions_limit=request.sessions_limit,
    )


@router.post("/sessions", response_model=AssistantSessionResponse)
def create_assistant_session(
    request: AssistantSessionCreateRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    session = assistant_service.create_session(db, title=request.title, project_root=request.project_root)
    return session_to_response(session)


@router.get("/sessions", response_model=AssistantSessionListResponse)
def list_assistant_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.list_sessions(db, limit=limit, offset=offset)


@router.get("/sessions/{session_id}", response_model=AssistantSessionResponse)
def get_assistant_session(
    session_id: str,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    session = assistant_service.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assistant session을 찾을 수 없습니다.")
    return session_to_response(session)


@router.get("/sessions/{session_id}/messages", response_model=AssistantMessageListResponse)
def list_assistant_session_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    messages = assistant_service.list_session_messages(db, session_id, limit=limit, offset=offset)
    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assistant session을 찾을 수 없습니다.")
    return messages


@router.post("/message", response_model=AssistantMessageResponse)
async def assistant_message(
    request: AssistantMessageRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    try:
        return await assistant_service.handle_message(db, request)
    except DocumentLoaderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OllamaError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/project-root/validate", response_model=ProjectRootValidateResponse)
def validate_project_root(
    request: ProjectRootValidateRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> dict:
    return assistant_service.validate_project_root(request)
