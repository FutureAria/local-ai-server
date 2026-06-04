import hashlib
import difflib
import ipaddress
import json
import re
import shlex
import socket
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import httpx
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db.models import AssistantMessage, AssistantSession
from app.schemas.assistant import (
    AssistantActionPreviewRequest,
    AssistantActionLoopNoopDispatchRequest,
    AssistantActionLoopPatchDispatchRequest,
    AssistantActionLoopPreflightRequest,
    AssistantActionLoopReadOnlyDispatchPreviewRequest,
    AssistantActionLoopShellDispatchRequest,
    AssistantAppOsInteractionPreviewRequest,
    AssistantAutomationPlanRequest,
    AssistantBrowserApprovalPreviewRequest,
    AssistantBrowserInteractRequest,
    AssistantBrowserLimitedInteractRequest,
    AssistantBrowserObserveRequest,
    AssistantBrowserPreviewRequest,
    AssistantDurableStatePreviewRequest,
    AssistantFailureRecoveryPreviewRequest,
    AssistantFilePreviewRequest,
    AssistantFullAutomationDispatchRequest,
    AssistantFullAutomationPreflightRequest,
    AssistantMessageRequest,
    AssistantPatchApplyRequest,
    AssistantPatchApprovalPreviewRequest,
    AssistantPatchPreviewRequest,
    AssistantReadOnlyScanRequest,
    AssistantReadOnlyAdapterExecuteRequest,
    AssistantRollbackApprovalPreviewRequest,
    AssistantRollbackExecuteRequest,
    AssistantShellApprovalPreviewRequest,
    AssistantShellPreviewRequest,
    AssistantShellRunRequest,
    AssistantTaskQueueCreateRequest,
    AssistantTaskQueueDrainRequest,
    AssistantUrlPreviewRequest,
    AssistantWebSearchProviderPreviewRequest,
    AssistantWebSearchProviderSearchRequest,
    AssistantWorkflowPresetPreviewRequest,
    AssistantWorkspaceBriefRequest,
    ProjectRootValidateRequest,
)
from app.services.agent_service import AgentService
from app.services.document_service import DocumentService
from app.services.project_status_service import dry_run_shell_command, get_project_status, get_shell_policy
from app.services.rag_service import RagService
from app.services.search_service import SearchService


APPROVAL_TTL_SECONDS = 300
APPROVAL_SESSIONLESS_CONTEXT = "request-context:assistant-locked-preview"


class InMemoryApprovalStore:
    def __init__(self) -> None:
        self._records: dict[str, dict] = {}

    def issue(
        self,
        *,
        tool_name: str,
        payload_hash: str,
        session_id: str | None,
        scope: str,
        ttl_seconds: int = APPROVAL_TTL_SECONDS,
    ) -> dict:
        now = _utc_now()
        approval_id = uuid4().hex
        record = {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "payload_hash": payload_hash,
            "session_context": _approval_session_context(session_id),
            "session_id": session_id,
            "scope": scope,
            "issued_at": now,
            "expires_at": now + timedelta(seconds=ttl_seconds),
            "ttl_seconds": ttl_seconds,
            "used": False,
            "used_at": None,
            "console_state": "pending",
            "console_reason": None,
            "console_updated_at": None,
            "console_execution_triggered": False,
        }
        self._records[approval_id] = record
        return _approval_public_record(record)

    def list(self) -> list[dict]:
        self.cleanup_expired()
        return [_approval_public_record(record) for record in self._records.values()]

    def get(self, approval_id: str | None) -> dict | None:
        self.cleanup_expired()
        if not approval_id:
            return None
        record = self._records.get(approval_id)
        return _approval_public_record(record) if record else None

    def set_console_state(self, approval_id: str | None, *, state: str, reason: str | None = None) -> dict:
        self.cleanup_expired()
        normalized = state.strip().lower()
        if normalized not in {"pending", "approved", "rejected"}:
            return _approval_check_result(
                "invalid_console_state",
                "approval console state는 pending/approved/rejected만 허용합니다.",
            )
        if not approval_id:
            return _approval_check_result("missing_approval_id", "서버 발급 approval_id가 필요합니다.")
        record = self._records.get(approval_id)
        if record is None:
            return _approval_check_result("unknown_approval", "서버 approval store에 없는 approval_id입니다.")
        reason_text = reason or ""
        masked_reason = (
            "[REDACTED_APPROVAL_LIKE_JSON]"
            if _contains_approval_like_json(reason_text)
            or re.search(r"\b(approval_id|approval_payload_hash|approval_hash|next_action)\b", reason_text, flags=re.IGNORECASE)
            else _mask_secret_like_values(reason_text)
        )
        record["console_state"] = normalized
        record["console_reason"] = masked_reason
        record["console_updated_at"] = _utc_now()
        record["console_execution_triggered"] = False
        public = _approval_public_record(record)
        return {
            "valid": True,
            "status": f"console_{normalized}",
            "reason": "approval console state-only transition completed; no execution was triggered.",
            "approval": public,
            "used": bool(record["used"]),
            "execution_triggered": False,
        }

    def consume(
        self,
        *,
        approval_id: str | None,
        payload_hash: str | None,
        session_id: str | None,
        tool_name: str,
    ) -> dict:
        result = self.validate(
            approval_id=approval_id,
            payload_hash=payload_hash,
            session_id=session_id,
            tool_name=tool_name,
        )
        if result["valid"]:
            record = self._records[approval_id or ""]
            record["used"] = True
            record["used_at"] = _utc_now()
            return {**result, "status": "valid_consumed", "used": True}
        return result

    def validate(
        self,
        *,
        approval_id: str | None,
        payload_hash: str | None,
        session_id: str | None,
        tool_name: str,
    ) -> dict:
        if not approval_id:
            return _approval_check_result("missing_approval_id", "서버 발급 approval_id가 필요합니다.")
        record = self._records.get(approval_id)
        if record is None:
            return _approval_check_result("unknown_approval", "서버 approval store에 없는 approval_id입니다.")
        public = _approval_public_record(record)
        now = _utc_now()
        if record["tool_name"] != tool_name:
            return _approval_check_result("tool_mismatch", "approval tool binding이 일치하지 않습니다.", public)
        if record["session_context"] != _approval_session_context(session_id):
            return _approval_check_result("session_mismatch", "approval session/request context가 일치하지 않습니다.", public)
        if record["payload_hash"] != payload_hash:
            return _approval_check_result("payload_hash_mismatch", "approval payload_hash가 일치하지 않습니다.", public)
        if record["expires_at"] <= now:
            return _approval_check_result("expired", "approval TTL이 만료되었습니다.", public)
        if record["used"]:
            return _approval_check_result("already_used", "approval은 single-use라 재사용할 수 없습니다.", public)
        return {
            "valid": True,
            "status": "valid",
            "reason": "server-issued approval binding이 유효합니다.",
            "approval": public,
            "used": False,
        }

    def cleanup_expired(self) -> int:
        now = _utc_now()
        expired_ids = self._expired_approval_ids(now)
        for approval_id in expired_ids:
            self._records.pop(approval_id, None)
        return len(expired_ids)

    def cleanup_expired_summary(self) -> dict:
        now = _utc_now()
        expired_ids = self._expired_approval_ids(now)
        expired_count = len(expired_ids)
        for approval_id in expired_ids:
            self._records.pop(approval_id, None)
        audit_payload = {
            "operation": "approval-store-expiry-cleanup",
            "expired_count": expired_count,
            "records_removed": expired_count,
            "state_only": True,
            "execution_triggered": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
        }
        return {
            "schema": "assistant.approval_store.expiry_cleanup.v1",
            "status": "cleaned" if expired_count else "no_expired_records",
            "expired_count": expired_count,
            "records_removed": expired_count,
            "state_only": True,
            "execution_triggered": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
            "paste_safe_summary": (
                "approval-store-expiry-cleanup completed: "
                f"expired_count={expired_count}, records_removed={expired_count}, "
                "raw approval id not included, payload_hash not included, no execution triggered."
            ),
            "audit": {
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
            },
        }

    def _expired_approval_ids(self, now: datetime) -> list[str]:
        return [
            approval_id
            for approval_id, record in self._records.items()
            if record["expires_at"] <= now
        ]


TASK_QUEUE_TTL_SECONDS = 300
TASK_QUEUE_STATUSES = ["queued", "running", "completed", "blocked", "cancelled"]


class InMemoryTaskQueuePreviewStore:
    def __init__(self) -> None:
        self._records: dict[str, dict] = {}

    def create(self, task: dict, ttl_seconds: int = TASK_QUEUE_TTL_SECONDS) -> dict:
        now = _utc_now()
        task_id = uuid4().hex
        record = {
            **task,
            "task_id": task_id,
            "status": "queued",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat(),
            "ttl_seconds": ttl_seconds,
            "cancellation": {"requested": False, "cancelled_at": None, "reason": None},
            "worker": {
                "worker_enabled": False,
                "worker_started": False,
                "background_loop_created": False,
                "execution_enabled": False,
            },
        }
        self._records[task_id] = record
        return _freeze_steps([record])[0]

    def list(self) -> list[dict]:
        self.cleanup_expired()
        return [_freeze_steps([record])[0] for record in self._records.values()]

    def get(self, task_id: str) -> dict | None:
        self.cleanup_expired()
        record = self._records.get(task_id)
        return _freeze_steps([record])[0] if record else None

    def cancel(self, task_id: str) -> dict | None:
        self.cleanup_expired()
        record = self._records.get(task_id)
        if not record:
            return None
        now = _utc_now().isoformat()
        record["status"] = "cancelled"
        record["updated_at"] = now
        record["cancellation"] = {
            "requested": True,
            "cancelled_at": now,
            "reason": "preview cancellation state only; no worker was running",
        }
        return _freeze_steps([record])[0]

    def update_execution(self, task_id: str, *, status: str, result: dict, worker: dict) -> dict | None:
        self.cleanup_expired()
        record = self._records.get(task_id)
        if not record:
            return None
        now = _utc_now().isoformat()
        record["status"] = status
        record["updated_at"] = now
        record["result"] = result
        record["worker"] = {
            **record.get("worker", {}),
            **worker,
            "worker_enabled": True,
            "worker_started": True,
            "background_loop_created": False,
            "execution_enabled": True,
            "updated_at": now,
        }
        record["execution"] = {
            **record.get("execution", {}),
            "would_execute": False,
            "would_dispatch": False,
            "would_apply": False,
            "would_interact": False,
            "worker_enabled": True,
            "background_execution_started": False,
            "execution_enabled": True,
            "status": status,
        }
        return _freeze_steps([record])[0]

    def cleanup_expired(self) -> int:
        now = _utc_now()
        expired_ids = [
            task_id
            for task_id, record in self._records.items()
            if datetime.fromisoformat(record["expires_at"]) <= now
        ]
        for task_id in expired_ids:
            self._records.pop(task_id, None)
        return len(expired_ids)


class AssistantService:
    def __init__(
        self,
        settings: Settings | None = None,
        rag_service: RagService | None = None,
        search_service: SearchService | None = None,
        document_service: DocumentService | None = None,
        agent_service: AgentService | None = None,
        approval_store: InMemoryApprovalStore | None = None,
        task_queue_store: InMemoryTaskQueuePreviewStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.rag_service = rag_service or RagService()
        self.search_service = search_service or SearchService()
        self.document_service = document_service or DocumentService()
        self.agent_service = agent_service or AgentService(self.settings)
        self.approval_store = approval_store or InMemoryApprovalStore()
        self.task_queue_store = task_queue_store or InMemoryTaskQueuePreviewStore()

    def capabilities(self) -> dict:
        return {
            "service": self.settings.service_name,
            "modes": [
                "auto",
                "ask",
                "ask_with_docs",
                "search",
                "index_preview",
                "agent_plan",
                "shell_dry_run",
                "shell_preview",
                "patch_preview",
                "browser_preview",
                "browser_observe",
                "browser_limited_interact",
                "web_search_provider_preview",
                "web_search_provider_search",
                "app_os_interaction_preview",
                "workflow_presets",
                "task_queue_preview",
                "task_queue_drain",
                "failure_recovery_preview",
                "rollback_approval_preview",
                "rollback_execute",
                "action_loop_preflight",
                "action_loop_noop_dispatch",
                "action_loop_read_only_dispatch_preview",
                "action_loop_read_only_dispatch",
                "action_loop_shell_dispatch",
                "action_loop_patch_dispatch",
                "full_automation_preflight",
                "full_automation_dispatch",
                "automation_plan",
            ],
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "llm_provider": "ollama-local",
            "vector_store": "chroma-local",
            "storage": "sqlite-local",
            "safe_defaults": {
                "shell_execution": "enabled-allowlist" if self.settings.shell_execution_enabled else "disabled",
                "shell_dry_run": "enabled",
                "shell_sandbox_execution": "enabled-allowlist" if self.settings.shell_execution_enabled else "locked",
                "patch_apply": "enabled-single-file" if self.settings.patch_apply_enabled else "locked",
                "browser_interaction": "blocked",
                "browser_interaction_preview": "locked",
                "browser_observe": "enabled-read-only" if self.settings.browser_observe_enabled else "disabled",
                "browser_limited_interaction": (
                    "enabled-candidate-validation"
                    if self.settings.browser_limited_interaction_enabled
                    else "disabled"
                ),
                "external_web_search": (
                    "enabled-provider" if self.settings.external_web_search_enabled else "disabled"
                ),
                "external_web_search_provider": (
                    self.settings.external_web_search_provider or "not-configured"
                ),
                "app_os_control": "disabled",
                "action_loop_dispatch": "disabled",
                "full_automation_dispatch": (
                    "enabled-safe-connectors"
                    if self.settings.full_automation_dispatch_enabled
                    else "disabled"
                ),
                "action_loop_noop_dispatch": "available_preview_only",
                "read_only_dispatch": "boundary-preview-only",
                "read_only_adapter_execution": (
                    "enabled-read-only" if self.settings.read_only_adapter_execution_enabled else "disabled"
                ),
                "read_only_action_loop_dispatch": (
                    "enabled-read-only" if self.settings.read_only_action_loop_dispatch_enabled else "disabled"
                ),
                "shell_action_loop_dispatch": (
                    "enabled-allowlist" if self.settings.shell_action_loop_dispatch_enabled else "disabled"
                ),
                "patch_action_loop_dispatch": (
                    "enabled-single-file" if self.settings.patch_action_loop_dispatch_enabled else "disabled"
                ),
                "long_running_task_queue": "locked-preview-only",
                "task_queue_worker": "enabled-one-shot-drain" if self.settings.task_queue_worker_enabled else "disabled",
                "background_worker": "one-shot-drain-enabled" if self.settings.task_queue_worker_enabled else "disabled",
                "rollback_executor": "enabled-single-file" if self.settings.rollback_executor_enabled else "disabled",
                "automatic_rollback": "single-file-env-opt-in" if self.settings.rollback_executor_enabled else "disabled",
                "file_write_delete": "single-file-patch-only" if self.settings.patch_apply_enabled else "blocked",
                "folder_index_from_assistant": "preview-only",
                "agent_execution_enabled": self.settings.agent_execution_enabled,
                "web_fetch_enabled": self.settings.agent_web_fetch_enabled,
            },
            "endpoints": {
                "ping": "GET /assistant/ping",
                "config": "GET /assistant/config",
                "dashboard": "GET /assistant/dashboard",
                "startup": "GET /assistant/startup",
                "ui_contract": "GET /assistant/ui-contract",
                "action_preview": "POST /assistant/action-preview",
                "action_loop_preflight": "POST /assistant/action-loop-preflight",
                "action_loop_noop_dispatch": "POST /assistant/action-loop-noop-dispatch",
                "action_loop_read_only_dispatch_preview": "POST /assistant/action-loop-read-only-dispatch-preview",
                "action_loop_read_only_dispatch": "POST /assistant/action-loop-read-only-dispatch",
                "action_loop_shell_dispatch": "POST /assistant/action-loop-shell-dispatch",
                "action_loop_patch_dispatch": "POST /assistant/action-loop-patch-dispatch",
                "full_automation_preflight": "POST /assistant/full-automation-preflight",
                "full_automation_dispatch": "POST /assistant/full-automation-dispatch",
                "automation_plan": "POST /assistant/automation-plan",
                "workflow_presets": "GET /assistant/workflow-presets",
                "workflow_preset_detail": "GET /assistant/workflow-presets/{preset_id}",
                "workflow_preset_preview": "POST /assistant/workflow-presets/{preset_id}/preview",
                "task_queue_preview": "POST /assistant/task-queue/preview",
                "task_queue": "GET /assistant/task-queue",
                "task_queue_drain": "POST /assistant/task-queue/drain",
                "task_queue_detail": "GET /assistant/task-queue/{task_id}",
                "task_queue_cancel_preview": "POST /assistant/task-queue/{task_id}/cancel-preview",
                "failure_recovery_preview": "POST /assistant/failure-recovery-preview",
                "rollback_approval_preview": "POST /assistant/rollback-approval-preview",
                "rollback_execute": "POST /assistant/rollback-execute",
                "read_only_scan": "POST /assistant/read-only-scan",
                "file_preview": "POST /assistant/file-preview",
                "url_preview": "POST /assistant/url-preview",
                "read_only_adapter_execute": "POST /assistant/read-only-adapter/execute",
                "app_os_interaction_preview": "POST /assistant/app-os-interaction-preview",
                "workspace_brief": "POST /assistant/workspace-brief",
                "shell_preview": "POST /assistant/shell-preview",
                "shell_approval_preview": "POST /assistant/shell-approval-preview",
                "shell_run": "POST /assistant/shell-run",
                "durable_state_preview": "POST /assistant/durable-state-preview/preview",
                "approval_console_pending": "GET /assistant/approval-console/pending",
                "approval_console_detail": "GET /assistant/approval-console/{approval_id}",
                "approval_console_cleanup_expired": "POST /assistant/approval-console/cleanup-expired",
                "patch_preview": "POST /assistant/patch-preview",
                "patch_approval_preview": "POST /assistant/patch-approval-preview",
                "patch_apply": "POST /assistant/patch-apply",
                "browser_preview": "POST /assistant/browser-preview",
                "browser_approval_preview": "POST /assistant/browser-approval-preview",
                "browser_interact": "POST /assistant/browser-interact",
                "browser_observe": "POST /assistant/browser-observe",
                "browser_limited_interact": "POST /assistant/browser-limited-interact",
                "web_search_provider_preview": "POST /assistant/web-search-provider-preview",
                "web_search_provider_search": "POST /assistant/web-search-provider/search",
                "bootstrap": "POST /assistant/bootstrap",
                "status": "GET /assistant/status",
                "message": "POST /assistant/message",
                "create_session": "POST /assistant/sessions",
                "list_sessions": "GET /assistant/sessions",
                "get_session": "GET /assistant/sessions/{session_id}",
                "list_session_messages": "GET /assistant/sessions/{session_id}/messages",
                "validate_project_root": "POST /assistant/project-root/validate",
                "shell_policy": "GET /project/shell-policy",
                "shell_dry_run": "POST /project/shell-dry-run",
            },
        }

    def ui_contract(self) -> dict:
        return {
            "service": self.settings.service_name,
            "version": "1",
            "protected": bool(self.settings.local_api_key),
            "auth": {
                "supported_headers": ["X-API-Key", "Authorization: Bearer <LOCAL_API_KEY>"],
                "secret_returned": False,
                "note": "LOCAL_API_KEY 값은 API 응답에 포함하지 않습니다.",
            },
            "startup_sequence": [
                {"step": 1, "method": "GET", "path": "/assistant/startup", "purpose": "one-call UI hydration"},
                {"step": 2, "method": "POST", "path": "/assistant/bootstrap", "purpose": "sessions and project root state"},
                {"step": 3, "method": "POST", "path": "/assistant/action-preview", "purpose": "pre-send intent/risk check"},
                {
                    "step": 4,
                    "method": "POST",
                    "path": "/assistant/automation-plan",
                    "purpose": "safe personal automation roadmap",
                },
                {"step": 5, "method": "POST", "path": "/assistant/message", "purpose": "send confirmed message"},
            ],
            "refresh_endpoints": [
                {"method": "GET", "path": "/assistant/ping", "purpose": "server/auth quick check"},
                {"method": "GET", "path": "/assistant/config", "purpose": "safe local settings"},
                {"method": "GET", "path": "/assistant/dashboard", "purpose": "dashboard cards"},
                {"method": "GET", "path": "/assistant/sessions", "purpose": "session sidebar refresh"},
                {
                    "method": "GET",
                    "path": "/project/api-inventory",
                    "purpose": "read-only endpoint inventory for developer/debug UI",
                },
            ],
            "message_flow": [
                {"step": 1, "method": "POST", "path": "/assistant/action-preview", "purpose": "intent/risk preview"},
                {"step": 2, "method": "POST", "path": "/assistant/message", "purpose": "safe routed answer"},
                {"step": 3, "method": "GET", "path": "/assistant/sessions/{session_id}/messages", "purpose": "paged history"},
            ],
            "response_types": {
                "answer": "assistant answer bubble",
                "search_results": "search result panel",
                "index_preview": "folder index preview panel",
                "needs_project_root": "project root required warning",
                "shell_dry_run": "shell dry-run policy panel",
                "agent_plan": "high-risk plan preview panel",
                "status": "project phase/status panel",
                "action_preview": "pre-send intent preview panel",
                "automation_plan": "personal automation readiness panel",
                "workflow_presets": "personal workflow preset list panel",
                "workflow_preset_detail": "personal workflow preset detail panel",
                "workflow_preset_preview": "personal workflow preset preview panel",
                "task_queue_preview": "locked long-running task queue create preview panel",
                "task_queue": "locked long-running task queue list panel",
                "task_queue_drain": "one-shot task queue worker drain panel",
                "task_queue_detail": "locked long-running task queue detail panel",
                "task_queue_cancel_preview": "locked long-running task cancellation preview panel",
                "failure_recovery_preview": "locked failure recovery and rollback plan panel",
                "rollback_approval_preview": "rollback approval binding preview panel",
                "rollback_execute": "single-file rollback execution panel",
                "read_only_scan": "workspace read-only scan panel",
                "file_preview": "masked file preview panel",
                "url_preview": "URL fetch preflight panel",
                "workspace_brief": "workspace brief panel",
                "shell_preview": "locked shell sandbox preview panel",
                "shell_approval_preview": "approval binding preview panel",
                "shell_run_locked": "shell run locked response panel",
                "patch_preview": "locked patch diff preview panel",
                "patch_approval_preview": "patch approval binding preview panel",
                "patch_apply_locked": "patch apply locked response panel",
                "patch_apply": "single-file patch apply result panel",
                "browser_preview": "locked browser/app interaction preview panel",
                "browser_approval_preview": "browser/app approval binding preview panel",
                "browser_interact_locked": "browser/app interact locked response panel",
                "browser_observe": "browser observe read-only result panel",
                "browser_limited_interact": "browser limited interaction candidate panel",
                "web_search_provider_preview": "locked external web search provider gate panel",
                "web_search_provider_search": "external web search provider result panel",
                "app_os_interaction_preview": "locked app/OS interaction gate panel",
                "action_loop_preflight": "locked action-loop dispatch preflight panel",
                "action_loop_noop_dispatch": "no-op action-loop route plan panel",
                "action_loop_read_only_dispatch_preview": "read-only dispatch boundary preview panel",
                "action_loop_shell_dispatch": "shell action-loop allowlist dispatch panel",
                "action_loop_patch_dispatch": "patch action-loop single-file dispatch panel",
                "full_automation_preflight": "full personal automation route preflight panel",
                "full_automation_dispatch": "full personal automation dispatch gate panel",
            },
            "safety": _safety(),
            "blocked_actions": [
                "shell_execution",
                "browser_interaction",
                "file_write_delete",
                "external_llm_api",
                "external_web_search",
                "app_os_control",
            ],
            "notes": [
                "이 계약은 UI 렌더링용 read-only 안내입니다.",
                "실제 shell 실행은 SHELL_EXECUTION_ENABLED=true, allowlist, cwd, approval binding을 모두 통과한 경우에만 제한적으로 수행합니다.",
                "런타임 LLM과 embedding은 Ollama local API만 사용합니다.",
            ],
        }

    def startup(self, db: Session) -> dict:
        ping = self.ping()
        config = self.config()
        dashboard = self.dashboard(db)
        ui_contract = self.ui_contract()
        return {
            "service": self.settings.service_name,
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "ping": ping,
            "config": config,
            "dashboard": dashboard,
            "ui_contract": ui_contract,
            "recommended_calls": [
                {"method": "POST", "path": "/assistant/bootstrap", "when": "project_root is available"},
                {"method": "POST", "path": "/assistant/action-preview", "when": "before sending user text"},
                {"method": "POST", "path": "/assistant/automation-plan", "when": "planning tool/API automation"},
                {"method": "POST", "path": "/assistant/workspace-brief", "when": "project_root is ready"},
                {"method": "POST", "path": "/assistant/message", "when": "user confirms message send"},
                {"method": "GET", "path": "/assistant/sessions/{session_id}/messages", "when": "open chat history"},
            ],
            "safety": _safety(),
            "ui": {
                "ready": True,
                "badge": "STARTUP SNAPSHOT READY",
                "message": "UI 초기 렌더링에 필요한 read-only snapshot입니다.",
                "display": "startup_snapshot",
            },
        }

    def action_preview(self, request: AssistantActionPreviewRequest) -> dict:
        intent = request.mode if request.mode != "auto" else self._detect_intent(request.message)
        needs = _intent_needs(intent, request.project_root)
        risk_level = _intent_risk(intent)
        return {
            "intent": intent,
            "recommended_endpoint": _intent_endpoint(intent),
            "would_execute": False,
            "requires_approval": intent in {"agent_plan", "shell_dry_run"},
            "risk_level": risk_level,
            "needs": needs,
            "safety": _safety(),
            "ui": {
                "response_type": "action_preview",
                "severity": "warning" if risk_level in {"medium", "high"} else "info",
                "primary_text": f"{intent} preview",
                "display": "panel",
            },
        }

    def action_loop_preflight(self, request: AssistantActionLoopPreflightRequest) -> dict:
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_frozen_steps = _mask_secret_like_structure(frozen_steps)
        step_previews = [
            self._action_loop_step_preview(index=index, step=step)
            for index, step in enumerate(frozen_steps, start=1)
        ]
        violations = []
        for preview in step_previews:
            violations.extend(preview["violations"])
        if not frozen_steps:
            violations.append("plan_empty")
        wrapper_missing = any("missing_untrusted_wrapper" in preview["violations"] for preview in step_previews)
        approval_missing = any("missing_approval_binding" in preview["violations"] for preview in step_previews)
        payload_mismatch = any("payload_hash_mismatch" in preview["violations"] for preview in step_previews)
        unsafe_action = any(preview["status"] != "allowed_preview" for preview in step_previews)
        status = "blocked" if violations else "ready_preview"
        frozen_plan = {
            "goal": _mask_secret_like_values(request.goal),
            "project_root": request.project_root,
            "steps": masked_frozen_steps,
            "steps_count": len(frozen_steps),
            "plan_hash": _stable_hash({"goal": request.goal, "project_root": request.project_root, "steps": frozen_steps}),
            "mutable": False,
            "note": "frozen plan은 dispatch 입력이 아니라 실행 전 검토용 snapshot입니다.",
        }
        gates = {
            "single_dispatch_boundary": "required_before_activation",
            "wrapper_required": True,
            "wrapper_enforced": not wrapper_missing,
            "approval_binding_required": True,
            "approval_binding_present": not approval_missing,
            "payload_hash_verified": not payload_mismatch,
            "unsafe_action_blocked": unsafe_action,
            "missing_wrapper_fail_closed": wrapper_missing,
            "missing_approval_fail_closed": approval_missing,
            "payload_hash_mismatch_fail_closed": payload_mismatch,
            "dispatch_connected": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "action-loop-dispatch-preflight-locked",
            "status": status,
            "goal": _mask_secret_like_values(request.goal),
            "would_dispatch": False,
            "execution_enabled": False,
            "fail_closed": bool(violations),
            "frozen_plan": frozen_plan,
            "step_previews": step_previews,
            "gates": gates,
            "required_user_decisions": [
                "실제 dispatch 연결 전 단일 feedback boundary 설계 확정",
                "wrapper 누락 fail-closed 테스트와 approval binding 저장 방식 리뷰",
                "shell/patch/browser 실제 실행 활성화는 별도 보안 리뷰와 사용자 최종 승인 후 진행",
            ],
            "safety": _safety(action_loop_status=status),
            "ui": _ui("action_loop_preflight", "warning", status),
        }

    def action_loop_noop_dispatch(self, request: AssistantActionLoopNoopDispatchRequest) -> dict:
        preflight = self.action_loop_preflight(
            AssistantActionLoopPreflightRequest(
                goal=request.goal,
                project_root=request.project_root,
                proposed_steps=request.proposed_steps,
                require_wrappers=request.require_wrappers,
                require_approval_bindings=request.require_approval_bindings,
            )
        )
        route_plan = [
            _noop_route_step(preview)
            for preview in preflight["step_previews"]
        ]
        noop_audit_payload = {
            "goal": preflight["goal"],
            "preflight_status": preflight["status"],
            "plan_hash": preflight["frozen_plan"]["plan_hash"],
            "routes_count": len(route_plan),
            "would_dispatch": False,
            "would_dispatch_noop_only": preflight["status"] == "ready_preview",
            "execution_enabled": False,
            "approval_consume_mode": "validate-only",
            "route_plan": route_plan,
        }
        status = "noop_ready" if preflight["status"] == "ready_preview" else "blocked"
        gates = {
            **preflight["gates"],
            "noop_dispatcher": True,
            "real_dispatch_connected": False,
            "tool_execution_connected": False,
            "approval_consume_mode": "validate-only",
            "approval_consumed": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "action-loop-noop-dispatch-preview",
            "status": status,
            "goal": preflight["goal"],
            "would_dispatch": False,
            "would_dispatch_noop_only": status == "noop_ready",
            "execution_enabled": False,
            "fail_closed": preflight["fail_closed"],
            "approval_consume_mode": "validate-only",
            "route_plan": route_plan,
            "noop_audit": {
                "schema": "assistant.action_loop.noop_dispatch.v1",
                "payload": noop_audit_payload,
                "payload_hash": _stable_hash(noop_audit_payload),
                "note": "No-op dispatcher는 routing audit만 만들고 어떤 tool도 실행하지 않습니다.",
            },
            "preflight": preflight,
            "gates": gates,
            "required_user_decisions": [
                "no-op dispatcher 이후 실제 dispatch 연결은 별도 보안 리뷰와 사용자 최종 승인 필요",
                "approval validate-only와 consume mode 전환 조건 별도 결정",
                "shell/patch/browser 실제 실행 연결 금지 상태 유지",
            ],
            "safety": _safety(action_loop_status=status),
            "ui": _ui("action_loop_noop_dispatch", "warning", status),
        }

    def action_loop_read_only_dispatch_preview(
        self,
        request: AssistantActionLoopReadOnlyDispatchPreviewRequest,
    ) -> dict:
        result_wrapper_schema = _read_only_result_wrapper_schema()
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_frozen_steps = _mask_secret_like_structure(frozen_steps)
        route_plan = [
            _read_only_boundary_step_preview(
                index=index,
                step=step,
                allowed_roots=self.settings.agent_allowed_roots,
            )
            for index, step in enumerate(frozen_steps, start=1)
        ]
        violations = [violation for route in route_plan for violation in route["violations"]]
        if not route_plan:
            violations.append("plan_empty")
        status = "ready_preview" if not violations else "blocked"
        boundary_payload = {
            "goal": _mask_secret_like_values(request.goal),
            "project_root": request.project_root,
            "steps": masked_frozen_steps,
            "routes_count": len(route_plan),
            "would_dispatch": False,
            "would_read": False,
            "would_fetch": False,
            "execution_enabled": False,
            "boundary_mode": "classification-only",
            "route_plan": route_plan,
            "result_wrapper_schema": result_wrapper_schema,
        }
        return {
            "service": self.settings.service_name,
            "mode": "action-loop-read-only-dispatch-boundary-preview",
            "status": status,
            "goal": _mask_secret_like_values(request.goal),
            "would_dispatch": False,
            "would_read": False,
            "would_fetch": False,
            "execution_enabled": False,
            "fail_closed": bool(violations),
            "boundary_mode": "classification-only",
            "route_plan": route_plan,
            "result_wrapper_schema": result_wrapper_schema,
            "boundary_audit": {
                "schema": "assistant.action_loop.read_only_boundary_preview.v1",
                "payload": boundary_payload,
                "payload_hash": _stable_hash(boundary_payload),
                "note": "Read-only dispatch boundary preview는 adapter routing을 분류하지만 파일 읽기, 폴더 스캔, URL fetch를 수행하지 않습니다.",
            },
            "gates": {
                "read_only_tools_only": not any("unsupported_tool" in route["violations"] for route in route_plan),
                "wrapper_required": True,
                "wrapper_enforced": not any("missing_untrusted_wrapper" in route["violations"] for route in route_plan),
                "real_dispatch_connected": False,
                "adapter_execution_connected": False,
                "result_wrapper_required": True,
                "raw_result_content_allowed": False,
                "approval_like_json_trusted": False,
                "result_can_mutate_frozen_plan": False,
                "file_content_read": False,
                "folder_scan_performed": False,
                "url_fetch_performed": False,
            },
            "safety": _safety(action_loop_status=status),
            "ui": _ui("action_loop_read_only_dispatch_preview", "warning", status),
        }

    def action_loop_read_only_dispatch(
        self,
        request: AssistantActionLoopReadOnlyDispatchPreviewRequest,
    ) -> dict:
        boundary = self.action_loop_read_only_dispatch_preview(request)
        safety = {
            **_safety(action_loop_status=boundary["status"]),
            "read_only_adapter_execution": (
                "enabled-read-only" if self.settings.read_only_adapter_execution_enabled else "disabled"
            ),
            "read_only_action_loop_dispatch": (
                "enabled-read-only" if self.settings.read_only_action_loop_dispatch_enabled else "disabled"
            ),
        }
        base_gates = {
            **boundary["gates"],
            "real_dispatch_connected": True,
            "read_only_dispatch_only": True,
            "adapter_execution_connected": self.settings.read_only_adapter_execution_enabled,
            "read_only_action_loop_dispatch_enabled": self.settings.read_only_action_loop_dispatch_enabled,
            "shell_execution_connected": False,
            "patch_apply_connected": False,
            "browser_interaction_connected": False,
        }
        if not self.settings.read_only_action_loop_dispatch_enabled:
            return _read_only_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=boundary["goal"],
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                adapter_results=[],
                boundary=boundary,
                gates=base_gates,
                safety=safety,
                reason="READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=false 상태라 read-only dispatch가 차단됩니다.",
            )
        if not self.settings.read_only_adapter_execution_enabled:
            return _read_only_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=boundary["goal"],
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                adapter_results=[],
                boundary=boundary,
                gates=base_gates,
                safety=safety,
                reason="READ_ONLY_ADAPTER_EXECUTION_ENABLED=false 상태라 adapter 실행이 차단됩니다.",
            )
        if boundary["status"] != "ready_preview":
            return _read_only_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=boundary["goal"],
                status="blocked",
                dispatched=False,
                execution_enabled=True,
                fail_closed=True,
                adapter_results=[],
                boundary=boundary,
                gates=base_gates,
                safety=safety,
                reason="read-only boundary preview가 blocked라 dispatch를 수행하지 않습니다.",
            )

        frozen_steps = _freeze_steps(request.proposed_steps)
        adapter_results = []
        for step in frozen_steps:
            adapter_request = _read_only_adapter_request_from_step(step, request.project_root)
            if adapter_request is None:
                adapter_results.append(
                    {
                        "status": "blocked",
                        "adapter_type": str(step.get("tool") or "unknown"),
                        "reason": "read-only dispatch에서 지원하지 않는 adapter입니다.",
                        "adapter_executed": False,
                    }
                )
                continue
            adapter_results.append(self.read_only_adapter_execute(adapter_request))
        status = "completed" if adapter_results and all(result["status"] == "completed" for result in adapter_results) else "blocked"
        return _read_only_action_loop_dispatch_response(
            service=self.settings.service_name,
            goal=boundary["goal"],
            status=status,
            dispatched=status == "completed",
            execution_enabled=True,
            fail_closed=status != "completed",
            adapter_results=adapter_results,
            boundary=boundary,
            gates=base_gates,
            safety=safety,
            reason=None if status == "completed" else "하나 이상의 read-only adapter 실행이 차단되었습니다.",
        )

    def action_loop_shell_dispatch(self, request: AssistantActionLoopShellDispatchRequest) -> dict:
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_steps = _durable_state_preview_redact_sensitive_keys(_mask_secret_like_structure(frozen_steps))
        route_plan = [
            self._action_loop_shell_step_preview(index=index, step=step)
            for index, step in enumerate(frozen_steps, start=1)
        ]
        violations = [violation for route in route_plan for violation in route["violations"]]
        if not route_plan:
            violations.append("plan_empty")
        gates = {
            "shell_action_loop_dispatch_enabled": self.settings.shell_action_loop_dispatch_enabled,
            "shell_execution_enabled": self.settings.shell_execution_enabled,
            "shell_execution_connected": (
                self.settings.shell_action_loop_dispatch_enabled and self.settings.shell_execution_enabled
            ),
            "shell_tools_only": not any("unsupported_tool" in route["violations"] for route in route_plan),
            "wrapper_required": True,
            "wrapper_enforced": not any("missing_untrusted_wrapper" in route["violations"] for route in route_plan),
            "approval_binding_required": True,
            "approval_like_json_trusted": False,
            "result_wrapper_required": True,
            "result_can_mutate_frozen_plan": False,
            "patch_apply_connected": False,
            "browser_interaction_connected": False,
            "external_api_connected": False,
            "task_worker_connected": False,
            "rollback_connected": False,
            "app_os_control_connected": False,
        }
        safety = {
            **_safety(
                shell_status=(
                    "enabled-allowlist"
                    if self.settings.shell_action_loop_dispatch_enabled and self.settings.shell_execution_enabled
                    else "disabled"
                ),
                action_loop_status="shell-dispatch-enabled" if self.settings.shell_action_loop_dispatch_enabled else "disabled",
            ),
            "shell_action_loop_dispatch": (
                "enabled-allowlist" if self.settings.shell_action_loop_dispatch_enabled else "disabled"
            ),
        }
        if not self.settings.shell_action_loop_dispatch_enabled:
            return _shell_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                route_plan=route_plan,
                shell_results=[],
                gates=gates,
                safety=safety,
                reason="SHELL_ACTION_LOOP_DISPATCH_ENABLED=false 상태라 shell action-loop dispatch가 차단됩니다.",
                masked_steps=masked_steps,
            )
        if not self.settings.shell_execution_enabled:
            return _shell_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                route_plan=route_plan,
                shell_results=[],
                gates=gates,
                safety=safety,
                reason="SHELL_EXECUTION_ENABLED=false 상태라 action-loop shell 실행이 차단됩니다.",
                masked_steps=masked_steps,
            )
        if violations:
            return _shell_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="blocked",
                dispatched=False,
                execution_enabled=True,
                fail_closed=True,
                route_plan=route_plan,
                shell_results=[],
                gates=gates,
                safety=safety,
                reason="shell action-loop route plan이 fail-closed로 차단되었습니다.",
                masked_steps=masked_steps,
            )

        shell_results = []
        for step in frozen_steps:
            params = step.get("params") if isinstance(step.get("params"), dict) else {}
            approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
            shell_results.append(
                self.shell_run(
                    AssistantShellRunRequest(
                        command=str(params.get("command") or ""),
                        cwd=str(params.get("cwd") or "."),
                        timeout_seconds=int(params.get("timeout_seconds") or 30),
                        approval_id=approval_binding.get("approval_id"),
                        approval_payload_hash=approval_binding.get("payload_hash"),
                        session_id=approval_binding.get("session_id"),
                    )
                )
            )
        status = "completed" if shell_results and all(result["status"] == "completed" for result in shell_results) else "blocked"
        return _shell_action_loop_dispatch_response(
            service=self.settings.service_name,
            goal=request.goal,
            status=status,
            dispatched=status == "completed",
            execution_enabled=True,
            fail_closed=status != "completed",
            route_plan=route_plan,
            shell_results=shell_results,
            gates=gates,
            safety=_safety(shell_status=status, action_loop_status=status) | {
                "shell_action_loop_dispatch": "enabled-allowlist"
            },
            reason=None if status == "completed" else "하나 이상의 shell action-loop step이 completed 상태가 아닙니다.",
            masked_steps=masked_steps,
        )

    def action_loop_patch_dispatch(self, request: AssistantActionLoopPatchDispatchRequest) -> dict:
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_steps = _mask_secret_like_structure(frozen_steps)
        route_plan = [
            self._action_loop_patch_step_preview(index=index, step=step)
            for index, step in enumerate(frozen_steps, start=1)
        ]
        violations = [violation for route in route_plan for violation in route["violations"]]
        if not route_plan:
            violations.append("plan_empty")
        gates = {
            "patch_action_loop_dispatch_enabled": self.settings.patch_action_loop_dispatch_enabled,
            "patch_apply_enabled": self.settings.patch_apply_enabled,
            "patch_apply_connected": (
                self.settings.patch_action_loop_dispatch_enabled and self.settings.patch_apply_enabled
            ),
            "patch_tools_only": not any("unsupported_tool" in route["violations"] for route in route_plan),
            "wrapper_required": True,
            "wrapper_enforced": not any("missing_untrusted_wrapper" in route["violations"] for route in route_plan),
            "approval_binding_required": True,
            "approval_like_json_trusted": False,
            "result_wrapper_required": True,
            "result_can_mutate_frozen_plan": False,
            "shell_execution_connected": False,
            "browser_interaction_connected": False,
            "external_api_connected": False,
            "task_worker_connected": False,
            "rollback_connected": False,
            "app_os_control_connected": False,
        }
        safety = {
            **_safety(
                patch_status=(
                    "enabled-single-file"
                    if self.settings.patch_action_loop_dispatch_enabled and self.settings.patch_apply_enabled
                    else "disabled"
                ),
                action_loop_status="patch-dispatch-enabled"
                if self.settings.patch_action_loop_dispatch_enabled
                else "disabled",
            ),
            "patch_action_loop_dispatch": (
                "enabled-single-file" if self.settings.patch_action_loop_dispatch_enabled else "disabled"
            ),
        }
        if not self.settings.patch_action_loop_dispatch_enabled:
            return _patch_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                route_plan=route_plan,
                patch_results=[],
                gates=gates,
                safety=safety,
                reason="PATCH_ACTION_LOOP_DISPATCH_ENABLED=false 상태라 patch action-loop dispatch가 차단됩니다.",
                masked_steps=masked_steps,
            )
        if not self.settings.patch_apply_enabled:
            return _patch_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="disabled",
                dispatched=False,
                execution_enabled=False,
                fail_closed=False,
                route_plan=route_plan,
                patch_results=[],
                gates=gates,
                safety=safety,
                reason="PATCH_APPLY_ENABLED=false 상태라 action-loop patch apply가 차단됩니다.",
                masked_steps=masked_steps,
            )
        if violations:
            return _patch_action_loop_dispatch_response(
                service=self.settings.service_name,
                goal=request.goal,
                status="blocked",
                dispatched=False,
                execution_enabled=True,
                fail_closed=True,
                route_plan=route_plan,
                patch_results=[],
                gates=gates,
                safety=safety,
                reason="patch action-loop route plan이 fail-closed로 차단되었습니다.",
                masked_steps=masked_steps,
            )

        patch_results = []
        for step in frozen_steps:
            params = step.get("params") if isinstance(step.get("params"), dict) else {}
            approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
            patch_results.append(
                self.patch_apply(
                    AssistantPatchApplyRequest(
                        path=str(params.get("path") or ""),
                        proposed_content=str(params.get("proposed_content") or ""),
                        project_root=params.get("project_root"),
                        original_sha256=params.get("original_sha256"),
                        approval_id=approval_binding.get("approval_id"),
                        approval_payload_hash=approval_binding.get("payload_hash"),
                        session_id=approval_binding.get("session_id"),
                    )
                )
            )
        status = "completed" if patch_results and all(result["status"] == "applied" for result in patch_results) else "blocked"
        return _patch_action_loop_dispatch_response(
            service=self.settings.service_name,
            goal=request.goal,
            status=status,
            dispatched=status == "completed",
            execution_enabled=True,
            fail_closed=status != "completed",
            route_plan=route_plan,
            patch_results=patch_results,
            gates=gates,
            safety=_safety(patch_status=status, action_loop_status=status) | {
                "patch_action_loop_dispatch": "enabled-single-file"
            },
            reason=None if status == "completed" else "하나 이상의 patch action-loop step이 applied 상태가 아닙니다.",
            masked_steps=masked_steps,
        )

    def full_automation_preflight(self, request: AssistantFullAutomationPreflightRequest) -> dict:
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_steps = _mask_secret_like_structure(frozen_steps)
        route_plan = [
            self._full_automation_step_preflight(index=index, step=step, project_root=request.project_root)
            for index, step in enumerate(frozen_steps, start=1)
        ]
        blocked_reasons = sorted(
            {
                reason
                for route in route_plan
                for reason in route.get("blocked_reasons", [])
            }
        )
        if not route_plan:
            blocked_reasons.append("plan_empty")
        status = "ready_preflight" if not blocked_reasons else "blocked"
        frozen_plan = {
            "goal": _mask_secret_like_values(request.goal),
            "project_root": request.project_root,
            "steps": masked_steps,
            "steps_count": len(frozen_steps),
            "plan_hash": _stable_hash(
                {
                    "goal": request.goal,
                    "project_root": request.project_root,
                    "steps": frozen_steps,
                    "session_id": request.session_id,
                }
            ),
            "mutable": False,
            "can_be_mutated_by_tool_result": False,
        }
        tool_matrix = _full_automation_tool_matrix(self.settings)
        gates = {
            "full_automation_dispatch_enabled": self.settings.full_automation_dispatch_enabled,
            "dispatch_connected": False,
            "preflight_only": True,
            "approval_consume_mode": "validate-only",
            "approval_consumed": False,
            "wrapper_required": True,
            "approval_binding_required": True,
            "result_wrapper_required": True,
            "raw_result_content_allowed": False,
            "approval_like_json_trusted": False,
            "result_can_mutate_frozen_plan": False,
            "shell_connected": False,
            "patch_connected": False,
            "rollback_connected": False,
            "task_worker_connected": False,
            "browser_actual_interaction_connected": False,
            "external_api_connected": False,
            "app_os_control_connected": False,
            "daemon_or_service_connected": False,
            "git_reset_or_bulk_restore_connected": False,
        }
        audit_payload = {
            "goal": _mask_secret_like_values(request.goal),
            "status": status,
            "plan_hash": frozen_plan["plan_hash"],
            "routes_count": len(route_plan),
            "blocked_reasons": blocked_reasons,
            "would_dispatch": False,
            "execution_enabled": False,
            "full_automation_enabled": self.settings.full_automation_dispatch_enabled,
            "approval_consume_mode": "validate-only",
        }
        return {
            "service": self.settings.service_name,
            "mode": "full-personal-automation-preflight",
            "status": status,
            "goal": _mask_secret_like_values(request.goal),
            "would_dispatch": False,
            "execution_enabled": False,
            "fail_closed": bool(blocked_reasons),
            "full_automation_enabled": self.settings.full_automation_dispatch_enabled,
            "frozen_plan": frozen_plan,
            "route_plan": route_plan,
            "tool_matrix": tool_matrix,
            "gates": gates,
            "blocked_reasons": blocked_reasons,
            "result_wrapper_schema": _full_automation_result_wrapper_schema(),
            "audit": {
                "schema": "assistant.full_automation.preflight.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "36차 full automation preflight는 통합 route plan만 만들고 어떤 tool도 실행하지 않습니다.",
            },
            "required_user_decisions": [
                "실제 full automation dispatch는 37차 이후 별도 connector별 테스트로만 확장",
                "browser actual interaction, app-os, daemon/service, git reset/bulk restore는 별도 단계 전까지 미연결",
                "tool result는 untrusted wrapper로만 취급하고 frozen plan mutation을 금지",
            ],
            "safety": _safety(action_loop_status=status) | {
                "full_automation_dispatch": "disabled",
                "browser_actual_interaction": "disabled",
                "app_os_control": "disabled",
                "daemon_service": "disabled",
            },
            "ui": _ui("full_automation_preflight", "warning" if blocked_reasons else "info", status),
        }

    def full_automation_dispatch(self, request: AssistantFullAutomationDispatchRequest) -> dict:
        preflight = self.full_automation_preflight(
            AssistantFullAutomationPreflightRequest(
                goal=request.goal,
                project_root=request.project_root,
                proposed_steps=request.proposed_steps,
                session_id=request.session_id,
                require_wrappers=request.require_wrappers,
                require_approval_bindings=request.require_approval_bindings,
            )
        )
        blocked_reasons = list(preflight["blocked_reasons"])
        read_only_adapter_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.read_only_adapter_execution_enabled
        )
        shell_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.shell_execution_enabled
        )
        patch_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.patch_apply_enabled
        )
        rollback_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.rollback_executor_enabled
        )
        task_queue_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.task_queue_worker_enabled
        )
        browser_observe_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.browser_observe_enabled
        )
        browser_limited_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.browser_limited_interaction_enabled
        )
        external_web_search_connected = (
            self.settings.full_automation_dispatch_enabled
            and self.settings.external_web_search_enabled
        )
        app_os_preview_connected = self.settings.full_automation_dispatch_enabled
        if not self.settings.full_automation_dispatch_enabled:
            blocked_reasons = sorted({*blocked_reasons, "full_automation_dispatch_disabled"})
            status = "disabled"
            reason = "FULL_AUTOMATION_DISPATCH_ENABLED=false 상태라 통합 dispatch가 차단됩니다."
        elif preflight["status"] != "ready_preflight":
            status = "blocked"
            reason = "full automation preflight가 fail-closed 상태라 dispatch를 수행하지 않습니다."
        else:
            status = "noop_ready"
            reason = "37차 full automation은 실제 connector 실행 없이 route order와 step wrapper aggregation만 반환합니다."
        frozen_steps = _freeze_steps(request.proposed_steps)
        tool_results: list[dict] = []
        if status == "noop_ready" and (
            read_only_adapter_connected
            or shell_connected
            or patch_connected
            or rollback_connected
            or task_queue_connected
            or browser_observe_connected
            or browser_limited_connected
            or external_web_search_connected
            or app_os_preview_connected
        ):
            step_result_wrappers = []
            for index, route in enumerate(preflight["route_plan"], start=1):
                adapter_result = None
                shell_result = None
                patch_result = None
                rollback_result = None
                task_queue_result = None
                browser_observe_result = None
                browser_limited_result = None
                external_web_search_result = None
                app_os_preview_result = None
                if route.get("category") == "read_only":
                    if read_only_adapter_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        adapter_request = _read_only_adapter_request_from_step(step, request.project_root)
                        if adapter_request is None:
                            adapter_result = {
                                "status": "blocked",
                                "adapter_type": str(route.get("tool") or "unknown"),
                                "reason": "full automation read-only dispatch에서 지원하지 않는 adapter입니다.",
                                "adapter_executed": False,
                            }
                        else:
                            adapter_result = self.read_only_adapter_execute(adapter_request)
                        tool_results.append(adapter_result)
                elif route.get("category") == "shell":
                    if shell_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        approval_binding = (
                            step.get("approval_binding")
                            if isinstance(step.get("approval_binding"), dict)
                            else {}
                        )
                        shell_result = self.shell_run(
                            AssistantShellRunRequest(
                                command=str(params.get("command") or ""),
                                cwd=str(params.get("cwd") or "."),
                                timeout_seconds=int(params.get("timeout_seconds") or 30),
                                approval_id=approval_binding.get("approval_id"),
                                approval_payload_hash=approval_binding.get("payload_hash"),
                                session_id=approval_binding.get("session_id"),
                            )
                        )
                        tool_results.append(shell_result)
                elif route.get("category") == "patch":
                    if patch_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        approval_binding = (
                            step.get("approval_binding")
                            if isinstance(step.get("approval_binding"), dict)
                            else {}
                        )
                        patch_result = self.patch_apply(
                            AssistantPatchApplyRequest(
                                path=str(params.get("path") or ""),
                                proposed_content=str(params.get("proposed_content") or ""),
                                project_root=params.get("project_root"),
                                original_sha256=params.get("original_sha256"),
                                approval_id=approval_binding.get("approval_id"),
                                approval_payload_hash=approval_binding.get("payload_hash"),
                                session_id=approval_binding.get("session_id"),
                            )
                        )
                        tool_results.append(patch_result)
                elif route.get("category") == "rollback":
                    if rollback_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        approval_binding = (
                            step.get("approval_binding")
                            if isinstance(step.get("approval_binding"), dict)
                            else {}
                        )
                        rollback_result = self.rollback_execute(
                            AssistantRollbackExecuteRequest(
                                path=str(params.get("path") or ""),
                                restored_content=str(params.get("restored_content") or ""),
                                project_root=params.get("project_root"),
                                current_sha256=params.get("current_sha256"),
                                original_sha256=params.get("original_sha256"),
                                approval_id=approval_binding.get("approval_id"),
                                approval_payload_hash=approval_binding.get("payload_hash"),
                                session_id=approval_binding.get("session_id"),
                                reason=params.get("reason"),
                            )
                        )
                        tool_results.append(rollback_result)
                elif route.get("category") == "task_queue":
                    if task_queue_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        task = _full_automation_task_queue_task(
                            index=index,
                            tool=str(route.get("tool") or ""),
                            params=params,
                            project_root=request.project_root,
                        )
                        task_queue_result = self._task_queue_execute_one_shot(task)
                        tool_results.append(task_queue_result)
                elif route.get("category") == "browser_observe":
                    if browser_observe_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        approval_binding = (
                            step.get("approval_binding")
                            if isinstance(step.get("approval_binding"), dict)
                            else {}
                        )
                        browser_observe_result = self.browser_observe(
                            AssistantBrowserObserveRequest(
                                action=str(params.get("action") or _browser_observe_action_from_tool(str(route.get("tool") or ""))),
                                target_url=str(params.get("target_url") or params.get("url") or ""),
                                approval_id=approval_binding.get("approval_id"),
                                approval_payload_hash=approval_binding.get("payload_hash"),
                                session_id=approval_binding.get("session_id"),
                            )
                        )
                        tool_results.append(browser_observe_result)
                elif route.get("category") == "browser_limited_interaction":
                    if browser_limited_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        approval_binding = (
                            step.get("approval_binding")
                            if isinstance(step.get("approval_binding"), dict)
                            else {}
                        )
                        browser_limited_result = self.browser_limited_interact(
                            AssistantBrowserLimitedInteractRequest(
                                action=str(params.get("action") or _browser_limited_action_from_tool(str(route.get("tool") or ""))),
                                target_url=str(params.get("target_url") or params.get("url") or ""),
                                selector=str(params.get("selector") or ""),
                                field_name=params.get("field_name"),
                                input_preview=params.get("input_preview"),
                                approval_id=approval_binding.get("approval_id"),
                                approval_payload_hash=approval_binding.get("payload_hash"),
                                session_id=approval_binding.get("session_id"),
                            )
                        )
                        tool_results.append(browser_limited_result)
                elif route.get("category") == "external_web_search":
                    if external_web_search_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
                        external_web_search_result = self.web_search_provider_search(
                            AssistantWebSearchProviderSearchRequest(
                                query=str(params.get("query") or ""),
                                provider=params.get("provider"),
                                result_wrapper=wrapper,
                            )
                        )
                        tool_results.append(external_web_search_result)
                elif route.get("category") == "app_os":
                    if app_os_preview_connected:
                        step = frozen_steps[index - 1] if index - 1 < len(frozen_steps) else {}
                        params = step.get("params") if isinstance(step.get("params"), dict) else {}
                        app_os_preview_result = self.app_os_interaction_preview(
                            AssistantAppOsInteractionPreviewRequest(
                                action=str(params.get("action") or "observe"),
                                app_name=params.get("app_name"),
                                window_title=params.get("window_title"),
                                target_path=params.get("target_path"),
                                input_preview=params.get("input_preview"),
                                reason=params.get("reason"),
                                session_id=request.session_id,
                            )
                        )
                        tool_results.append(app_os_preview_result)
                step_result_wrappers.append(
                    _full_automation_step_wrapper(
                        route=route,
                        execution_order=index,
                        read_only_adapter_result=adapter_result,
                        shell_result=shell_result,
                        patch_result=patch_result,
                        rollback_result=rollback_result,
                        task_queue_result=task_queue_result,
                        browser_observe_result=browser_observe_result,
                        browser_limited_result=browser_limited_result,
                        external_web_search_result=external_web_search_result,
                        app_os_preview_result=app_os_preview_result,
                    )
                )
            if tool_results:
                execution_completed = all(
                    result.get("status") in {"completed", "timeout", "applied", "validated", "observe_plan_candidate"} for result in tool_results
                )
                status = "full_automation_completed" if execution_completed else "blocked"
                reason = (
                    "46차 full automation은 read-only/shell/patch/rollback/task-queue/browser-observe/browser-limited/external-search step과 app-os preview step만 기존 안전 boundary로 처리했습니다."
                    if execution_completed
                    else "하나 이상의 full automation read-only/shell/patch/rollback/task-queue/browser-observe/browser-limited/external-search/app-os-preview step이 차단되었습니다."
                )
                blocked_reasons = sorted(
                    {
                        *blocked_reasons,
                        *[
                            f"full_automation_step_{result.get('status')}"
                            for result in tool_results
                            if result.get("status") not in {"completed", "timeout", "applied", "validated", "observe_plan_candidate"}
                        ],
                    }
                )
        else:
            step_result_wrappers = [
                _full_automation_step_wrapper(route=route, execution_order=index)
                for index, route in enumerate(preflight["route_plan"], start=1)
            ] if self.settings.full_automation_dispatch_enabled else []
        orchestrator_plan = _full_automation_orchestrator_plan(
            goal=preflight["goal"],
            frozen_plan=preflight["frozen_plan"],
            route_plan=preflight["route_plan"],
            enabled=self.settings.full_automation_dispatch_enabled,
            status=status,
        )
        dependency_graph = _full_automation_dependency_graph(preflight["route_plan"])
        failure_strategy = _full_automation_failure_strategy(status=status, blocked_reasons=blocked_reasons)
        rollback_strategy = _full_automation_rollback_strategy()
        any_adapter_executed = any(result.get("adapter_executed") is True for result in tool_results)
        any_shell_executed = any(
            result.get("mode") == "shell-sandbox-v1" and result.get("would_execute") is True
            for result in tool_results
        )
        any_patch_applied = any(result.get("mode") == "patch-apply-v1" and result.get("would_apply") is True for result in tool_results)
        any_rollback_applied = any(
            result.get("mode") == "rollback-executor-v1" and result.get("would_apply") is True
            for result in tool_results
        )
        any_task_queue_completed = any(
            result.get("schema") == "assistant.task_queue.worker_result.v1"
            and result.get("status") == "completed"
            for result in tool_results
        )
        any_browser_observed = any(
            result.get("mode") == "browser-observe-v1" and result.get("would_observe") is True
            for result in tool_results
        )
        any_browser_limited_validated = any(
            result.get("mode") == "browser-limited-interact-v1"
            and result.get("status") == "validated"
            and result.get("would_interact") is False
            for result in tool_results
        )
        any_external_web_search_completed = any(
            result.get("mode") == "external-web-search-provider-v1"
            and result.get("status") == "completed"
            and result.get("would_search") is True
            for result in tool_results
        )
        any_app_os_preview_completed = any(
            result.get("mode") == "app-os-interaction-gate-preview"
            and result.get("status") == "observe_plan_candidate"
            and result.get("os_action_executed") is False
            for result in tool_results
        )
        any_tool_executed = (
            any_adapter_executed
            or any_shell_executed
            or any_patch_applied
            or any_rollback_applied
            or any_task_queue_completed
            or any_browser_observed
            or any_browser_limited_validated
            or any_external_web_search_completed
            or any_app_os_preview_completed
        )
        any_preview_connector_completed = (
            any_browser_limited_validated
            or any_app_os_preview_completed
        )
        any_mutating_connector_executed = any_patch_applied or any_rollback_applied
        shell_approval_consumed = any(
            (result.get("approval_check") or {}).get("used") is True
            for result in tool_results
            if result.get("mode") == "shell-sandbox-v1"
        )
        patch_approval_consumed = any(
            (result.get("approval_check") or {}).get("used") is True
            for result in tool_results
            if result.get("mode") == "patch-apply-v1"
        )
        rollback_approval_consumed = any(
            (result.get("approval_check") or {}).get("used") is True
            for result in tool_results
            if result.get("mode") == "rollback-executor-v1"
        )
        browser_observe_approval_consumed = any(
            (result.get("approval_check") or {}).get("used") is True
            for result in tool_results
            if result.get("mode") == "browser-observe-v1"
        )
        browser_limited_approval_consumed = any(
            (result.get("approval_check") or {}).get("used") is True
            for result in tool_results
            if result.get("mode") == "browser-limited-interact-v1"
        )
        approval_consume_mode = (
            "safe-connectors-existing-boundary"
            if (
                shell_approval_consumed
                or patch_approval_consumed
                or rollback_approval_consumed
                or browser_observe_approval_consumed
                or browser_limited_approval_consumed
            )
            else "validate-only"
        )
        audit_payload = {
            "goal": preflight["goal"],
            "status": status,
            "preflight_status": preflight["status"],
            "preflight_audit_hash": preflight["audit"]["payload_hash"],
            "blocked_reasons": blocked_reasons,
            "dispatched": any_tool_executed,
            "would_dispatch": any_tool_executed,
            "execution_enabled": self.settings.full_automation_dispatch_enabled,
            "approval_consume_mode": approval_consume_mode,
            "approval_consumed": (
                shell_approval_consumed
                or patch_approval_consumed
                or rollback_approval_consumed
                or browser_observe_approval_consumed
                or browser_limited_approval_consumed
            ),
            "reason": _mask_secret_like_values(reason),
            "orchestrator_plan_hash": orchestrator_plan["plan_hash"],
            "step_result_wrappers_count": len(step_result_wrappers),
            "dependency_graph_hash": dependency_graph["graph_hash"],
            "read_only_adapter_connected": read_only_adapter_connected,
            "read_only_adapter_results_count": sum(1 for result in tool_results if "adapter_executed" in result),
            "shell_connected": shell_connected,
            "shell_results_count": sum(1 for result in tool_results if result.get("mode") == "shell-sandbox-v1"),
            "patch_connected": patch_connected,
            "patch_results_count": sum(1 for result in tool_results if result.get("mode") == "patch-apply-v1"),
            "rollback_connected": rollback_connected,
            "rollback_results_count": sum(1 for result in tool_results if result.get("mode") == "rollback-executor-v1"),
            "task_queue_connected": task_queue_connected,
            "task_queue_results_count": sum(
                1 for result in tool_results if result.get("schema") == "assistant.task_queue.worker_result.v1"
            ),
            "browser_observe_connected": browser_observe_connected,
            "browser_observe_results_count": sum(1 for result in tool_results if result.get("mode") == "browser-observe-v1"),
            "browser_limited_interaction_connected": browser_limited_connected,
            "browser_limited_results_count": sum(
                1 for result in tool_results if result.get("mode") == "browser-limited-interact-v1"
            ),
            "external_web_search_connected": external_web_search_connected,
            "external_web_search_results_count": sum(
                1 for result in tool_results if result.get("mode") == "external-web-search-provider-v1"
            ),
            "app_os_preview_connected": app_os_preview_connected,
            "app_os_preview_results_count": sum(
                1 for result in tool_results if result.get("mode") == "app-os-interaction-gate-preview"
            ),
            "safe_connector_execution_connected": any_tool_executed,
            "preview_connector_execution_connected": any_preview_connector_completed,
            "mutating_connector_execution_connected": any_mutating_connector_executed,
            "browser_actual_interaction_connected": False,
            "app_os_actual_action_connected": False,
            "action_loop_full_dispatch_connected": False,
            "daemon_or_service_connected": False,
            "git_reset_or_bulk_restore_connected": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "full-personal-automation-safe-orchestrator",
            "status": status,
            "goal": preflight["goal"],
            "dispatched": any_tool_executed,
            "would_dispatch": any_tool_executed,
            "execution_enabled": self.settings.full_automation_dispatch_enabled,
            "fail_closed": status not in {"disabled", "noop_ready", "full_automation_completed"},
            "approval_consume_mode": approval_consume_mode,
            "approval_consumed": (
                shell_approval_consumed
                or patch_approval_consumed
                or rollback_approval_consumed
                or browser_observe_approval_consumed
                or browser_limited_approval_consumed
            ),
            "route_plan": preflight["route_plan"],
            "tool_results": tool_results,
            "step_result_wrappers": step_result_wrappers,
            "orchestrator_plan": orchestrator_plan,
            "dependency_graph": dependency_graph,
            "failure_strategy": failure_strategy,
            "rollback_strategy": rollback_strategy,
            "preflight": preflight,
            "gates": {
                **preflight["gates"],
                "full_automation_dispatch_enabled": self.settings.full_automation_dispatch_enabled,
                "dispatch_connected": False,
                "tool_execution_connected": False,
                "approval_consumed": (
                    shell_approval_consumed
                    or patch_approval_consumed
                    or rollback_approval_consumed
                    or browser_observe_approval_consumed
                    or browser_limited_approval_consumed
                ),
                "noop_orchestrator_connected": self.settings.full_automation_dispatch_enabled,
                "step_result_aggregation_connected": self.settings.full_automation_dispatch_enabled,
                "read_only_adapter_execution_connected": read_only_adapter_connected,
                "read_only_steps_executed": any_adapter_executed,
                "shell_execution_connected": shell_connected,
                "shell_steps_executed": any_shell_executed,
                "patch_apply_connected": patch_connected,
                "patch_steps_applied": any_patch_applied,
                "rollback_executor_connected": rollback_connected,
                "rollback_steps_applied": any_rollback_applied,
                "task_queue_worker_connected": task_queue_connected,
                "task_queue_steps_completed": any_task_queue_completed,
                "browser_observe_connected": browser_observe_connected,
                "browser_observe_steps_completed": any_browser_observed,
                "browser_limited_interaction_connected": browser_limited_connected,
                "browser_limited_interaction_steps_validated": any_browser_limited_validated,
                "external_web_search_connected": external_web_search_connected,
                "external_web_search_steps_completed": any_external_web_search_completed,
                "app_os_preview_connected": app_os_preview_connected,
                "app_os_preview_steps_completed": any_app_os_preview_completed,
                "app_os_actual_action_connected": False,
                "browser_actual_interaction_connected": False,
                "safe_connector_execution_connected": any_tool_executed,
                "preview_connector_execution_connected": any_preview_connector_completed,
                "action_loop_full_dispatch_connected": False,
                "actual_connector_execution_connected": any_tool_executed,
                "mutating_connector_execution_connected": any_mutating_connector_executed,
            },
            "audit": {
                "schema": "assistant.full_automation.read_only_orchestrator.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "46차 orchestrator는 read-only adapter, allowlist shell, approved single-file patch/rollback, read-only task queue, browser observe, browser limited candidate, external web search, app-os preview step만 기존 boundary로 제한 처리하고 browser actual interaction/app-os actual action dispatch를 수행하지 않습니다.",
            },
            "blocked_reasons": blocked_reasons,
            "safety": preflight["safety"] | {
                "full_automation_dispatch": (
                    "enabled-safe-connectors"
                    if self.settings.full_automation_dispatch_enabled
                    else "disabled"
                ),
                "read_only_adapter_execution": (
                    "enabled-read-only" if read_only_adapter_connected else "disabled"
                ),
                "shell_execution": (
                    "enabled-allowlist" if shell_connected else "disabled"
                ),
                "patch_apply": (
                    "enabled-single-file" if patch_connected else "disabled"
                ),
                "rollback_executor": (
                    "enabled-single-file" if rollback_connected else "disabled"
                ),
                "task_queue_worker": (
                    "enabled-one-shot-step" if task_queue_connected else "disabled"
                ),
                "browser_observe": (
                    "enabled-read-only" if browser_observe_connected else "disabled"
                ),
                "browser_limited_interaction": (
                    "enabled-candidate-validation" if browser_limited_connected else "disabled"
                ),
                "external_web_search": (
                    "enabled-provider" if external_web_search_connected else "disabled"
                ),
                "app_os_preview": (
                    "enabled-preview-only" if app_os_preview_connected else "disabled"
                ),
                "app_os_actual_action": "disabled",
                "browser_actual_interaction": "disabled",
                "action_loop_full_dispatch": "disabled",
                "daemon_or_service": "disabled",
                "git_reset_or_bulk_restore": "disabled",
                "external_provider_extension": "disabled",
                "mutating_connector_execution": (
                    "enabled-single-file-patch-or-rollback-only"
                    if any_mutating_connector_executed
                    else "disabled"
                ),
                "approval_consume": approval_consume_mode,
            },
            "ui": _ui(
                "full_automation_dispatch",
                "info" if status in {"noop_ready", "full_automation_completed"} else "warning",
                status,
            ),
        }

    def _full_automation_step_preflight(self, index: int, step: dict, project_root: str | None) -> dict:
        tool = str(step.get("tool") or "").strip().lower().replace("-", "_")
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
        approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
        blocked_reasons: list[str] = []
        if wrapper.get("untrusted") is not True:
            blocked_reasons.append("missing_untrusted_wrapper")
        if _contains_approval_like_json(params):
            blocked_reasons.append("approval_like_json_injection_blocked")
        category = _full_automation_tool_category(tool)
        route = f"blocked://{tool or 'unknown'}"
        preview: dict | None = None
        required_payload_hash = None
        approval_check = None
        dispatch_supported = False
        if category == "read_only":
            preview = _read_only_boundary_step_preview(index, {**step, "tool": tool}, self.settings.agent_allowed_roots)
            blocked_reasons.extend(preview["violations"])
            route = f"read-only://{tool}"
        elif category == "shell":
            preview = self._action_loop_shell_step_preview(index=index, step={**step, "tool": "shell"})
            blocked_reasons.extend(preview["violations"])
            route = "shell://allowlist"
            required_payload_hash = preview.get("required_payload_hash")
            approval_check = preview.get("approval_check")
        elif category == "patch":
            preview = self._action_loop_patch_step_preview(index=index, step={**step, "tool": "patch"})
            blocked_reasons.extend(preview["violations"])
            route = "patch://single-file"
            required_payload_hash = preview.get("required_payload_hash")
            approval_check = preview.get("approval_check")
        elif category == "rollback":
            preview = _rollback_single_file_preview(
                path=str(params.get("path") or ""),
                restored_content=str(params.get("restored_content") or ""),
                project_root=params.get("project_root") or project_root,
                allowed_roots=self.settings.agent_allowed_roots,
                current_sha256=params.get("current_sha256"),
                original_sha256=params.get("original_sha256"),
                params=params,
                reason=params.get("reason"),
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "rollback://single-file"
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
            if required_payload_hash:
                approval_check = self.approval_store.validate(
                    approval_id=approval_binding.get("approval_id"),
                    payload_hash=approval_binding.get("payload_hash"),
                    session_id=approval_binding.get("session_id"),
                    tool_name="rollback",
                )
                if not approval_binding.get("approval_id") or not approval_binding.get("payload_hash"):
                    blocked_reasons.append("missing_approval_binding")
                elif approval_binding.get("payload_hash") != required_payload_hash:
                    blocked_reasons.append("payload_hash_mismatch")
                elif not approval_check["valid"]:
                    blocked_reasons.append(f"approval_{approval_check['status']}")
        elif category == "task_queue":
            preview = _full_automation_task_queue_step_preview(
                index=index,
                tool=tool,
                params=params,
                project_root=project_root,
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "task-queue://one-shot"
        elif category == "browser_observe":
            preview = self._full_automation_browser_observe_step_preview(
                index=index,
                tool=tool,
                params=params,
                approval_binding=approval_binding,
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "browser-observe://read-only"
            required_payload_hash = preview.get("required_payload_hash")
            approval_check = preview.get("approval_check")
        elif category == "browser_limited_interaction":
            preview = self._full_automation_browser_limited_step_preview(
                index=index,
                tool=tool,
                params=params,
                approval_binding=approval_binding,
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "browser-limited://candidate-validation"
            required_payload_hash = preview.get("required_payload_hash")
            approval_check = preview.get("approval_check")
        elif category == "external_web_search":
            preview = self._full_automation_external_web_search_step_preview(
                index=index,
                tool=tool,
                params=params,
                wrapper=wrapper,
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "external-web-search://provider"
        elif category == "app_os":
            preview = self._full_automation_app_os_step_preview(
                index=index,
                tool=tool,
                params=params,
                session_id=None,
            )
            blocked_reasons.extend(preview["blocked_reasons"])
            route = "app-os://preview-only"
        else:
            blocked_reasons.append(f"{category}_blocked")
        status = "routable_preflight" if not blocked_reasons else "blocked"
        return {
            "index": index,
            "tool": tool or "unknown",
            "category": category,
            "route": route,
            "status": status,
            "dispatch_supported": dispatch_supported,
            "would_dispatch": False,
            "execution_enabled": False,
            "approval_consume_mode": "validate-only",
            "approval_consumed": False,
            "required_payload_hash": required_payload_hash,
            "provided_approval_id": approval_binding.get("approval_id"),
            "provided_payload_hash": approval_binding.get("payload_hash"),
            "approval_check": approval_check,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "preview_summary": _full_automation_preview_summary(category, preview),
        }

    def _full_automation_browser_observe_step_preview(
        self,
        *,
        index: int,
        tool: str,
        params: dict,
        approval_binding: dict,
    ) -> dict:
        action = str(params.get("action") or _browser_observe_action_from_tool(tool))
        target_url = str(params.get("target_url") or params.get("url") or "")
        preview = self.browser_preview(
            AssistantBrowserPreviewRequest(action=action, target_url=target_url)
        )
        policy_reason = _browser_observe_policy_reason(
            action=preview["action"],
            target_url=target_url,
            allowed_origins=self.settings.browser_observe_allowed_origins,
        )
        blocked_reasons: list[str] = []
        if not preview["allowed"]:
            blocked_reasons.append("unsafe_browser_observe_action")
        if policy_reason:
            blocked_reasons.append("browser_observe_target_blocked")
        if _contains_approval_like_json(params):
            blocked_reasons.append("approval_like_json_injection_blocked")
        required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] and not policy_reason else None
        approval_check = None
        if required_payload_hash:
            approval_check = self.approval_store.validate(
                approval_id=approval_binding.get("approval_id"),
                payload_hash=approval_binding.get("payload_hash"),
                session_id=approval_binding.get("session_id"),
                tool_name="browser",
            )
            if not approval_binding.get("approval_id") or not approval_binding.get("payload_hash"):
                blocked_reasons.append("missing_approval_binding")
            elif approval_binding.get("payload_hash") != required_payload_hash:
                blocked_reasons.append("payload_hash_mismatch")
            elif not approval_check["valid"]:
                blocked_reasons.append(f"approval_{approval_check['status']}")
        status = "allowed_preview" if not blocked_reasons else "blocked"
        payload = {
            "index": index,
            "tool": tool,
            "action": preview["action"],
            "target_url": _mask_secret_like_values(target_url),
            "status": status,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "required_payload_hash": required_payload_hash,
            "browser_actual_interaction": False,
        }
        return {
            "schema": "assistant.full_automation.browser_observe.preview.v1",
            "status": status,
            "allowed": not blocked_reasons,
            "action": preview["action"],
            "target_url": _mask_secret_like_values(target_url),
            "required_payload_hash": required_payload_hash,
            "approval_check": approval_check,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "preview": preview,
            "policy_reason": policy_reason,
            "audit": {
                "schema": "assistant.full_automation.browser_observe.preview.audit.v1",
                "payload": payload,
                "payload_hash": _stable_hash(payload),
            },
        }

    def _full_automation_browser_limited_step_preview(
        self,
        *,
        index: int,
        tool: str,
        params: dict,
        approval_binding: dict,
    ) -> dict:
        action = str(params.get("action") or _browser_limited_action_from_tool(tool))
        target_url = str(params.get("target_url") or params.get("url") or "")
        selector = str(params.get("selector") or "")
        policy = _browser_limited_interaction_policy(
            action=action,
            target_url=target_url,
            selector=selector,
            field_name=params.get("field_name"),
            input_preview=params.get("input_preview"),
            allowed_origins=self.settings.browser_limited_interaction_allowed_origins,
            allowed_selectors=self.settings.browser_limited_interaction_allowed_selectors,
            allowed_fill_fields=self.settings.browser_limited_interaction_allowed_fill_fields,
        )
        blocked_reasons: list[str] = []
        if not policy["allowed"]:
            reason = str(policy.get("reason") or "")
            if "origin" in reason or "target_url" in reason or "private/LAN/metadata" in reason:
                blocked_reasons.append("browser_limited_interaction_target_blocked")
            else:
                blocked_reasons.append("unsafe_browser_limited_interaction")
            if not self.settings.browser_limited_interaction_enabled:
                blocked_reasons.append("browser_limited_interaction_not_connected_to_full_automation")
        if _contains_approval_like_json(params):
            blocked_reasons.append("approval_like_json_injection_blocked")
        approval_check = None
        required_payload_hash = approval_binding.get("payload_hash") if policy["allowed"] else None
        if policy["allowed"]:
            approval_check = self.approval_store.validate(
                approval_id=approval_binding.get("approval_id"),
                payload_hash=approval_binding.get("payload_hash"),
                session_id=approval_binding.get("session_id"),
                tool_name="browser",
            )
            if not approval_binding.get("approval_id") or not approval_binding.get("payload_hash"):
                blocked_reasons.append("missing_approval_binding")
            elif not approval_check["valid"]:
                blocked_reasons.append(f"approval_{approval_check['status']}")
        status = "allowed_preview" if not blocked_reasons else "blocked"
        payload = {
            "index": index,
            "tool": tool,
            "action": policy["action"],
            "target_url": policy["target_url"],
            "selector": policy["selector"],
            "field_name": policy["field_name"],
            "status": status,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "required_payload_hash": required_payload_hash,
            "policy_payload_hash": policy["payload_hash"],
            "browser_actual_interaction": False,
        }
        return {
            "schema": "assistant.full_automation.browser_limited.preview.v1",
            "status": status,
            "allowed": not blocked_reasons,
            "action": policy["action"],
            "target_url": policy["target_url"],
            "selector": policy["selector"],
            "field_name": policy["field_name"],
            "required_payload_hash": required_payload_hash,
            "policy_payload_hash": policy["payload_hash"],
            "approval_check": approval_check,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "policy": policy,
            "audit": {
                "schema": "assistant.full_automation.browser_limited.preview.audit.v1",
                "payload": payload,
                "payload_hash": _stable_hash(payload),
            },
        }

    def _full_automation_external_web_search_step_preview(
        self,
        *,
        index: int,
        tool: str,
        params: dict,
        wrapper: dict,
    ) -> dict:
        query = str(params.get("query") or "")
        provider = params.get("provider")
        policy = _evaluate_web_search_provider_search_policy(
            query=query,
            requested_provider=provider,
            configured_provider=self.settings.external_web_search_provider,
            api_key_configured=bool(self.settings.external_web_search_api_key),
            external_api_enabled=self.settings.external_web_search_enabled,
            rate_limit_per_minute=self.settings.external_web_search_rate_limit_per_minute,
            result_wrapper=wrapper,
        )
        blocked_reasons: list[str] = []
        reason = str(policy.get("reason") or "")
        if not policy["allowed"]:
            if "private/LAN/metadata" in reason or "secret-like query" in reason:
                blocked_reasons.append("external_web_search_query_blocked")
            elif "allowlist" in reason or "provider" in reason:
                blocked_reasons.append("external_web_search_provider_blocked")
            elif "untrusted=true" in reason:
                blocked_reasons.append("missing_untrusted_wrapper")
            else:
                blocked_reasons.append("external_web_search_not_connected_to_full_automation")
        if not self.settings.external_web_search_enabled:
            blocked_reasons.append("external_web_search_not_connected_to_full_automation")
        if _contains_approval_like_json(params):
            blocked_reasons.append("approval_like_json_injection_blocked")
        status = "allowed_preview" if not blocked_reasons else "blocked"
        payload = {
            "index": index,
            "tool": tool,
            "provider": policy["provider"],
            "query_preview": policy["query_preview"],
            "status": status,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "external_api_enabled": self.settings.external_web_search_enabled,
            "would_search": False,
        }
        return {
            "schema": "assistant.full_automation.external_web_search.preview.v1",
            "status": status,
            "allowed": not blocked_reasons,
            "provider": policy["provider"],
            "query_preview": policy["query_preview"],
            "blocked_reasons": sorted(set(blocked_reasons)),
            "policy": policy,
            "audit": {
                "schema": "assistant.full_automation.external_web_search.preview.audit.v1",
                "payload": payload,
                "payload_hash": _stable_hash(payload),
            },
        }

    def _full_automation_app_os_step_preview(
        self,
        *,
        index: int,
        tool: str,
        params: dict,
        session_id: str | None,
    ) -> dict:
        action = str(params.get("action") or _app_os_action_from_tool(tool))
        preview = self.app_os_interaction_preview(
            AssistantAppOsInteractionPreviewRequest(
                action=action,
                app_name=params.get("app_name"),
                window_title=params.get("window_title"),
                target_path=params.get("target_path"),
                input_preview=params.get("input_preview"),
                reason=params.get("reason"),
                session_id=session_id,
            )
        )
        blocked_reasons: list[str] = []
        if preview["status"] != "observe_plan_candidate":
            blocked_reasons.append("app_os_blocked")
            blocked_reasons.append("app_os_actual_action_blocked")
        if preview.get("os_action_executed") is True or preview.get("would_control_app") is True:
            blocked_reasons.append("app_os_blocked")
            blocked_reasons.append("app_os_actual_action_blocked")
        if _contains_approval_like_json(params):
            blocked_reasons.append("approval_like_json_injection_blocked")
        status = "allowed_preview" if not blocked_reasons else "blocked"
        payload = {
            "index": index,
            "tool": tool,
            "action": preview["action"],
            "app_name": preview["app_name"],
            "window_title": preview["window_title"],
            "target_path": preview["target_path"],
            "status": status,
            "blocked_reasons": sorted(set(blocked_reasons)),
            "observe_plan_candidate": preview["observe_plan_candidate"],
            "would_control_app": False,
            "os_action_executed": False,
        }
        return {
            "schema": "assistant.full_automation.app_os.preview.v1",
            "status": status,
            "allowed": not blocked_reasons,
            "action": preview["action"],
            "app_name": preview["app_name"],
            "window_title": preview["window_title"],
            "target_path": preview["target_path"],
            "observe_plan_candidate": preview["observe_plan_candidate"],
            "blocked_reasons": sorted(set(blocked_reasons)),
            "preview": preview,
            "audit": {
                "schema": "assistant.full_automation.app_os.preview.audit.v1",
                "payload": payload,
                "payload_hash": _stable_hash(payload),
            },
        }

    def ping(self) -> dict:
        return {
            "status": "ok",
            "service": self.settings.service_name,
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "ui_ready": True,
        }

    def config(self) -> dict:
        return {
            "service": self.settings.service_name,
            "protected": bool(self.settings.local_api_key),
            "local_only": True,
            "cors_origins": _csv_values(self.settings.local_cors_origins),
            "allowed_roots": _root_summaries(self.settings.agent_allowed_roots),
            "models": {
                "llm_provider": "ollama-local",
                "llm_model": self.settings.ollama_llm_model,
                "embedding_model": self.settings.ollama_embed_model,
            },
            "storage": {
                "database": "sqlite-local",
                "vector_store": "chroma-local",
                "upload_dir": self.settings.upload_dir,
                "chroma_path": self.settings.chroma_path,
            },
            "safety": _safety(),
            "rate_limit": {
                "enabled": self.settings.local_rate_limit_per_minute > 0,
                "per_minute": self.settings.local_rate_limit_per_minute,
            },
        }

    def status(self, db: Session) -> dict:
        project_status = get_project_status()
        document_stats = self.document_service.get_stats(db)
        integrity = self.document_service.get_integrity_report(db)
        sessions_count = db.scalar(select(func.count(AssistantSession.id))) or 0
        messages_count = db.scalar(select(func.count(AssistantMessage.id))) or 0
        return {
            "service": self.settings.service_name,
            "current_phase": project_status["current_phase"],
            "documents": {
                "documents_count": document_stats["documents_count"],
                "chunks_count": document_stats["chunks_count"],
                "chroma_vectors_count": document_stats["chroma_vectors_count"],
                "missing_stored_files_count": document_stats["missing_stored_files_count"],
            },
            "integrity": {
                "status": integrity["status"],
                "chunks_missing_vectors_count": integrity["chunks_missing_vectors_count"],
                "orphan_vectors_count": integrity["orphan_vectors_count"],
                "repair_available": integrity["repair_available"],
            },
            "sessions": {
                "sessions_count": sessions_count,
                "messages_count": messages_count,
            },
            "safety": _safety(),
        }

    def dashboard(self, db: Session) -> dict:
        status = self.status(db)
        recent_sessions = self.list_sessions(db, limit=5, offset=0)["sessions"]
        return {
            "service": self.settings.service_name,
            "current_phase": status["current_phase"],
            "cards": {
                "documents": status["documents"],
                "integrity": status["integrity"],
                "sessions": status["sessions"],
                "connection": {
                    "status": "ready",
                    "protected": bool(self.settings.local_api_key),
                    "local_only": True,
                },
            },
            "recent_sessions": recent_sessions,
            "safety": status["safety"],
            "ui": {
                "ready": True,
                "badge": "DASHBOARD READY",
                "message": "대시보드 상태를 조회했습니다.",
                "recommended_refresh_seconds": 30,
            },
        }

    def bootstrap(
        self,
        db: Session,
        project_root: str | None = None,
        include_sessions: bool = True,
        sessions_limit: int = 10,
    ) -> dict:
        root_status = None
        if project_root:
            root_status = self.validate_project_root(ProjectRootValidateRequest(project_root=project_root))
        sessions = self.list_sessions(db, limit=sessions_limit, offset=0) if include_sessions else None
        return {
            "service": self.settings.service_name,
            "capabilities": self.capabilities(),
            "status": self.status(db),
            "project_root": root_status,
            "sessions": sessions,
            "recommended_calls": [
                {"method": "POST", "path": "/assistant/project-root/validate", "when": "project_root input changes"},
                {"method": "POST", "path": "/assistant/automation-plan", "when": "사용자 자동화 목표를 단계화할 때"},
                {"method": "POST", "path": "/assistant/workspace-brief", "when": "read-only 프로젝트 요약이 필요할 때"},
                {"method": "POST", "path": "/assistant/sessions", "when": "new chat starts"},
                {"method": "POST", "path": "/assistant/message", "when": "user sends a message"},
                {"method": "GET", "path": "/assistant/sessions", "when": "refresh session sidebar"},
            ],
            "ui": {
                "ready": True,
                "badge": "LOCAL API READY",
                "message": "로컬 assistant API가 준비되었습니다.",
                "blocked_actions": ["shell_execution", "browser_interaction", "file_write_delete"],
            },
        }

    def read_only_scan(self, request: AssistantReadOnlyScanRequest) -> dict:
        root = _resolve_path(request.project_root)
        root_status = self.validate_project_root(ProjectRootValidateRequest(project_root=request.project_root))
        if not root_status["safe_for_read_only_agent"]:
            return {
                "service": self.settings.service_name,
                "project_root": request.project_root,
                "resolved_path": str(root),
                "mode": "read-only",
                "would_execute": False,
                "summary": {
                    "status": "blocked",
                    "reason": root_status["message"],
                    "files_count": 0,
                    "dirs_count": 0,
                },
                "important_files": [],
                "top_level_items": [],
                "extension_counts": {},
                "safety": _safety(),
                "ui": _ui("read_only_scan", "warning", "project root blocked"),
            }

        files_count = 0
        dirs_count = 0
        skipped_count = 0
        extension_counts: dict[str, int] = {}
        top_level_items = []
        for child in sorted(root.iterdir(), key=lambda item: item.name.lower())[: request.max_items]:
            if _is_sensitive_path(child):
                skipped_count += 1
                continue
            item_type = "dir" if child.is_dir() else "file"
            top_level_items.append(
                {
                    "name": child.name,
                    "type": item_type,
                    "extension": child.suffix.lower() if child.is_file() else None,
                }
            )
        for item in root.rglob("*"):
            if _is_skipped_tree_item(item) or _is_sensitive_path(item):
                skipped_count += 1
                continue
            if item.is_dir():
                dirs_count += 1
                continue
            if item.is_file():
                files_count += 1
                extension = item.suffix.lower() or "(none)"
                extension_counts[extension] = extension_counts.get(extension, 0) + 1
        important_files = [
            {
                "path": str(root / name),
                "name": name,
                "exists": (root / name).exists(),
                "type": "file",
            }
            for name in [
                "README.md",
                "AGENTS.md",
                "SECURITY.md",
                "pyproject.toml",
                "package.json",
                "docs/TASKS.md",
                "docs/WORKLOG.md",
                "docs/NEXT_CHAT_HANDOFF.md",
            ]
        ]
        return {
            "service": self.settings.service_name,
            "project_root": request.project_root,
            "resolved_path": str(root),
            "mode": "read-only",
            "would_execute": False,
            "summary": {
                "status": "completed",
                "files_count": files_count,
                "dirs_count": dirs_count,
                "skipped_count": skipped_count,
                "top_level_items_count": len(top_level_items),
            },
            "important_files": important_files,
            "top_level_items": top_level_items,
            "extension_counts": dict(sorted(extension_counts.items())),
            "safety": _safety(),
            "ui": _ui("read_only_scan", "info", "read-only scan completed"),
        }

    def file_preview(self, request: AssistantFilePreviewRequest) -> dict:
        resolved_path = _resolve_path(request.path)
        project_root = None
        if request.project_root:
            root_status = self.validate_project_root(ProjectRootValidateRequest(project_root=request.project_root))
            if not root_status["safe_for_read_only_agent"]:
                return {
                    "service": self.settings.service_name,
                    "path": request.path,
                    "resolved_path": str(resolved_path),
                    "mode": "read-only",
                    "status": "blocked",
                    "would_execute": False,
                    "metadata": {"reason": root_status["message"]},
                    "content_preview": None,
                    "truncated": False,
                    "masked": False,
                    "safety": _safety(),
                    "ui": _ui("file_preview", "warning", "project root blocked"),
                }
            project_root = Path(root_status["resolved_path"])
        allowed_roots = [project_root] if project_root else _allowed_roots(self.settings.agent_allowed_roots)
        base = {
            "service": self.settings.service_name,
            "path": request.path,
            "resolved_path": str(resolved_path),
            "mode": "read-only",
            "would_execute": False,
            "content_preview": None,
            "truncated": False,
            "masked": False,
            "safety": _safety(),
        }
        if not any(_is_relative_to(resolved_path, root) for root in allowed_roots):
            return {
                **base,
                "status": "blocked",
                "metadata": {"reason": "허용된 root 밖의 파일 preview는 차단됩니다."},
                "ui": _ui("file_preview", "warning", "outside allowed root"),
            }
        if not resolved_path.exists() or not resolved_path.is_file():
            return {
                **base,
                "status": "blocked",
                "metadata": {"reason": "존재하는 파일만 preview할 수 있습니다."},
                "ui": _ui("file_preview", "warning", "file not found"),
            }
        if _is_sensitive_path(resolved_path):
            return {
                **base,
                "status": "blocked",
                "metadata": {"reason": "민감 파일 또는 credential 후보는 preview하지 않습니다."},
                "ui": _ui("file_preview", "warning", "sensitive file blocked"),
            }
        size_bytes = resolved_path.stat().st_size
        if size_bytes > self.settings.agent_file_preview_max_bytes:
            return {
                **base,
                "status": "blocked",
                "metadata": {
                    "reason": "파일이 AGENT_FILE_PREVIEW_MAX_BYTES보다 큽니다.",
                    "size_bytes": size_bytes,
                },
                "ui": _ui("file_preview", "warning", "file too large"),
            }
        raw = resolved_path.read_bytes()
        if _looks_binary(raw):
            return {
                **base,
                "status": "blocked",
                "metadata": {"reason": "binary 파일은 preview하지 않습니다.", "size_bytes": size_bytes},
                "ui": _ui("file_preview", "warning", "binary file blocked"),
            }
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            return {
                **base,
                "status": "blocked",
                "metadata": {"reason": "UTF-8 텍스트 파일만 preview할 수 있습니다.", "size_bytes": size_bytes},
                "ui": _ui("file_preview", "warning", "non utf-8 file blocked"),
            }
        preview = content[: request.max_bytes]
        masked_preview = _mask_secret_like_values(preview)
        return {
            **base,
            "status": "completed",
            "metadata": {
                "filename": resolved_path.name,
                "extension": resolved_path.suffix.lower(),
                "size_bytes": size_bytes,
                "line_count": content.count("\n") + (1 if content else 0),
            },
            "content_preview": masked_preview,
            "truncated": len(content) > len(preview),
            "masked": masked_preview != preview,
            "ui": _ui("file_preview", "info", "file preview completed"),
        }

    def url_preview(self, request: AssistantUrlPreviewRequest) -> dict:
        url = request.url.strip()
        if not re.match(r"^https?://", url):
            status = "blocked"
            reason = "http/https URL만 read-only preview 후보가 될 수 있습니다."
        elif not (self.settings.agent_execution_enabled and self.settings.agent_web_fetch_enabled):
            status = "disabled"
            reason = "AGENT_EXECUTION_ENABLED와 AGENT_WEB_FETCH_ENABLED가 모두 true일 때만 명시 URL 단건 fetch 후보가 됩니다."
        else:
            status = "allowed_preview"
            reason = "명시 URL 단건 read-only fetch 후보입니다. 브라우저 클릭/로그인/입력은 수행하지 않습니다."
        return {
            "service": self.settings.service_name,
            "url": url,
            "mode": "read-only-url-preflight",
            "status": status,
            "would_fetch": False,
            "reason": reason,
            "safety": _safety(),
            "ui": _ui("url_preview", "warning" if status != "allowed_preview" else "info", status),
        }

    def read_only_adapter_execute(self, request: AssistantReadOnlyAdapterExecuteRequest) -> dict:
        wrapper_valid = request.result_wrapper.get("untrusted") is True
        base_payload = {
            "adapter_type": request.adapter_type,
            "project_root": request.project_root,
            "path": request.path,
            "url": request.url,
            "max_items": request.max_items,
            "max_bytes": request.max_bytes,
            "wrapper_valid": wrapper_valid,
            "execution_enabled": self.settings.read_only_adapter_execution_enabled,
            "action_loop_dispatch_connected": False,
        }
        safety = {**_safety(), "read_only_adapter_execution": "enabled-read-only" if self.settings.read_only_adapter_execution_enabled else "disabled"}
        if not wrapper_valid:
            return _read_only_adapter_response(
                service=self.settings.service_name,
                adapter_type=request.adapter_type,
                status="blocked",
                execution_enabled=self.settings.read_only_adapter_execution_enabled,
                would_read=False,
                would_fetch=False,
                adapter_executed=False,
                result=None,
                reason="read-only adapter result는 untrusted wrapper가 필요합니다.",
                audit_payload=base_payload,
                safety=safety,
            )
        if not self.settings.read_only_adapter_execution_enabled:
            return _read_only_adapter_response(
                service=self.settings.service_name,
                adapter_type=request.adapter_type,
                status="disabled",
                execution_enabled=False,
                would_read=False,
                would_fetch=False,
                adapter_executed=False,
                result=None,
                reason="READ_ONLY_ADAPTER_EXECUTION_ENABLED=false 상태라 adapter 실행이 차단됩니다.",
                audit_payload=base_payload,
                safety=safety,
            )

        if request.adapter_type == "read_only_scan":
            if not request.project_root:
                status = "blocked"
                result = {"reason": "read_only_scan adapter에는 project_root가 필요합니다."}
            else:
                result = self.read_only_scan(
                    AssistantReadOnlyScanRequest(project_root=request.project_root, max_items=request.max_items)
                )
                status = "completed" if result["summary"]["status"] == "completed" else "blocked"
            return _read_only_adapter_response(
                service=self.settings.service_name,
                adapter_type=request.adapter_type,
                status=status,
                execution_enabled=True,
                would_read=status == "completed",
                would_fetch=False,
                adapter_executed=status == "completed",
                result=result,
                reason=None if status == "completed" else result.get("reason") or result.get("summary", {}).get("reason"),
                audit_payload={**base_payload, "status": status},
                safety=safety,
            )

        if request.adapter_type == "file_preview":
            if not request.path:
                status = "blocked"
                result = {"reason": "file_preview adapter에는 path가 필요합니다."}
            else:
                result = self.file_preview(
                    AssistantFilePreviewRequest(
                        path=request.path,
                        project_root=request.project_root,
                        max_bytes=request.max_bytes,
                    )
                )
                status = "completed" if result["status"] == "completed" else "blocked"
            return _read_only_adapter_response(
                service=self.settings.service_name,
                adapter_type=request.adapter_type,
                status=status,
                execution_enabled=True,
                would_read=status == "completed",
                would_fetch=False,
                adapter_executed=status == "completed",
                result=result,
                reason=None if status == "completed" else result.get("reason") or result.get("metadata", {}).get("reason"),
                audit_payload={**base_payload, "status": status},
                safety=safety,
            )

        result = _execute_read_only_url_fetch(
            url=request.url or "",
            max_bytes=min(request.max_bytes, self.settings.agent_web_fetch_max_bytes),
            web_fetch_enabled=self.settings.agent_web_fetch_enabled,
        )
        status = "completed" if result["status"] == "completed" else "blocked"
        return _read_only_adapter_response(
            service=self.settings.service_name,
            adapter_type=request.adapter_type,
            status=status,
            execution_enabled=True,
            would_read=False,
            would_fetch=status == "completed",
            adapter_executed=status == "completed",
            result=result,
            reason=None if status == "completed" else result.get("reason"),
            audit_payload={**base_payload, "status": status},
            safety=safety,
        )

    def web_search_provider_preview(self, request: AssistantWebSearchProviderPreviewRequest) -> dict:
        policy = _evaluate_web_search_provider_policy(
            query=request.query,
            requested_provider=request.provider,
            configured_provider=self.settings.external_web_search_provider,
            external_api_enabled=self.settings.external_web_search_enabled,
            rate_limit_per_minute=self.settings.external_web_search_rate_limit_per_minute,
            result_wrapper=request.result_wrapper,
        )
        return {
            "service": self.settings.service_name,
            "mode": "external-web-search-provider-gate-preview",
            "status": policy["status"],
            "provider": policy["provider"],
            "query_preview": policy["query_preview"],
            "would_search": False,
            "would_fetch": False,
            "external_api_enabled": False,
            "provider_config": policy["provider_config"],
            "gate": policy["gate"],
            "result_wrapper": policy["result_wrapper"],
            "audit": policy["audit"],
            "safety": _safety(external_web_search_status=policy["status"]),
            "ui": _ui("web_search_provider_preview", "warning", policy["status"]),
        }

    def web_search_provider_search(self, request: AssistantWebSearchProviderSearchRequest) -> dict:
        policy = _evaluate_web_search_provider_search_policy(
            query=request.query,
            requested_provider=request.provider,
            configured_provider=self.settings.external_web_search_provider,
            api_key_configured=bool(self.settings.external_web_search_api_key),
            external_api_enabled=self.settings.external_web_search_enabled,
            rate_limit_per_minute=self.settings.external_web_search_rate_limit_per_minute,
            result_wrapper=request.result_wrapper,
        )
        search_result = None
        result_wrapper = None
        if not self.settings.external_web_search_enabled:
            status = "disabled"
            reason = "EXTERNAL_WEB_SEARCH_ENABLED=false 상태라 external web search 실행이 차단됩니다."
        elif not policy["allowed"]:
            status = "blocked"
            reason = policy["reason"]
        else:
            search_result = _execute_external_web_search(
                provider=policy["provider"] or "",
                query=request.query,
                api_key=self.settings.external_web_search_api_key or "",
            )
            status = search_result["status"]
            reason = search_result["paste_safe_summary"]
            result_wrapper = _external_web_search_result_wrapper(search_result)
        audit_payload = {
            "query_preview": policy["query_preview"],
            "provider": policy["provider"],
            "status": status,
            "would_search": status == "completed",
            "external_api_enabled": self.settings.external_web_search_enabled,
            "external_call_performed": bool(search_result and search_result.get("external_call_performed")),
            "result_hash": _stable_hash(search_result or {}),
        }
        return {
            "service": self.settings.service_name,
            "mode": "external-web-search-provider-v1",
            "status": status,
            "provider": policy["provider"],
            "query_preview": policy["query_preview"],
            "would_search": status == "completed",
            "would_fetch": status == "completed",
            "external_api_enabled": self.settings.external_web_search_enabled,
            "reason": _mask_secret_like_values(reason),
            "provider_config": policy["provider_config"],
            "gate": policy["gate"],
            "search_result": search_result,
            "result_wrapper": result_wrapper,
            "audit": {
                "schema": "assistant.external_web_search.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "33차 external web search는 provider/key/rate/query/wrapper gate 통과 시에만 단건 provider 호출을 수행합니다.",
            },
            "safety": _safety(external_web_search_status=status),
            "ui": _ui("web_search_provider_search", "info" if status == "completed" else "warning", status),
        }

    def app_os_interaction_preview(self, request: AssistantAppOsInteractionPreviewRequest) -> dict:
        policy = _evaluate_app_os_interaction_policy(
            action=request.action,
            app_name=request.app_name,
            window_title=request.window_title,
            target_path=request.target_path,
            input_preview=request.input_preview,
            reason=request.reason,
            os_control_enabled=self.settings.app_os_control_enabled,
            session_id=request.session_id,
        )
        return {
            "service": self.settings.service_name,
            "mode": "app-os-interaction-gate-preview",
            "status": policy["status"],
            "action": policy["action"],
            "app_name": policy["app_name"],
            "window_title": policy["window_title"],
            "target_path": policy["target_path"],
            "allowed": False,
            "observe_plan_candidate": policy["observe_plan_candidate"],
            "would_control_app": False,
            "os_action_executed": False,
            "reason": policy["reason"],
            "taxonomy": policy["taxonomy"],
            "permission_model": policy["permission_model"],
            "approval_binding": policy["approval_binding"],
            "gate": policy["gate"],
            "audit": policy["audit"],
            "safety": _safety(app_os_status=policy["status"]),
            "ui": _ui("app_os_interaction_preview", "warning", policy["status"]),
        }

    def workspace_brief(self, request: AssistantWorkspaceBriefRequest) -> dict:
        scan = self.read_only_scan(AssistantReadOnlyScanRequest(project_root=request.project_root, max_items=80))
        previews = []
        if request.include_previews and scan["summary"]["status"] == "completed":
            root = Path(scan["resolved_path"])
            for relative_path in ["README.md", "AGENTS.md", "SECURITY.md", "docs/TASKS.md", "docs/WORKLOG.md"]:
                candidate = root / relative_path
                if candidate.exists():
                    preview = self.file_preview(
                        AssistantFilePreviewRequest(
                            path=str(candidate),
                            project_root=request.project_root,
                            max_bytes=1200,
                        )
                    )
                    previews.append(
                        {
                            "path": relative_path,
                            "status": preview["status"],
                            "metadata": preview["metadata"],
                            "content_preview": preview["content_preview"],
                            "truncated": preview["truncated"],
                            "masked": preview["masked"],
                        }
                    )
        return {
            "service": self.settings.service_name,
            "project_root": request.project_root,
            "mode": "read-only-workspace-brief",
            "would_execute": False,
            "scan": scan,
            "previews": previews,
            "next_safe_actions": [
                "필요 파일을 더 좁혀 /assistant/file-preview로 확인",
                "명령 실행 전 /assistant/shell-preview로 allowlist와 cwd 정책만 확인",
                "문서 색인은 /documents/index-folder-preview로 먼저 확인",
                "실제 shell/browser/file-write는 5차 이후 별도 안전장치에서 처리",
            ],
            "safety": _safety(),
            "ui": _ui("workspace_brief", "info", "workspace brief completed"),
        }

    def shell_preview(self, request: AssistantShellPreviewRequest) -> dict:
        policy = _evaluate_shell_policy(
            command=request.command,
            cwd=request.cwd,
            timeout_seconds=request.timeout_seconds,
            allowed_roots=self.settings.agent_allowed_roots,
        )
        output_preview = {
            "stdout": _mask_secret_like_values(""),
            "stderr": _mask_secret_like_values(""),
            "truncated": False,
            "note": "preview 단계에서는 subprocess를 실행하지 않아 stdout/stderr가 비어 있습니다.",
        }
        audit = _shell_audit_payload(policy, output_preview)
        return {
            "service": self.settings.service_name,
            "mode": "shell-sandbox-preview",
            "command_preview": policy["command_preview"],
            "cwd": request.cwd,
            "resolved_cwd": policy["resolved_cwd"],
            "status": policy["status"],
            "would_execute": False,
            "allowed": policy["allowed"],
            "reason": policy["reason"],
            "timeout_seconds": policy["timeout_seconds"],
            "policy": policy,
            "audit": audit,
            "output_preview": output_preview,
            "safety": _safety(shell_status=policy["status"]),
            "ui": _ui("shell_preview", "info" if policy["allowed"] else "warning", policy["status"]),
        }

    def shell_approval_preview(self, request: AssistantShellApprovalPreviewRequest) -> dict:
        preview = self.shell_preview(
            AssistantShellPreviewRequest(
                command=request.command,
                cwd=request.cwd,
                timeout_seconds=request.timeout_seconds,
            )
        )
        binding = {
            "command_preview": preview["command_preview"],
            "resolved_cwd": preview["resolved_cwd"],
            "timeout_seconds": preview["timeout_seconds"],
            "audit_payload_hash": preview["audit"]["payload_hash"],
            "reason": _mask_secret_like_values(request.reason or ""),
            "status": preview["status"],
            "approval_scope": "single-command-preview-only",
            "payload_hash": preview["audit"]["payload_hash"],
            "expires_in_seconds": 300,
            "store": "not-created",
            "manual_review_required": True,
            "server_issued": False,
            "single_use": True,
            "session_context": _approval_session_context(request.session_id),
        }
        if preview["allowed"]:
            approval = self.approval_store.issue(
                tool_name="shell",
                payload_hash=preview["audit"]["payload_hash"],
                session_id=request.session_id,
                scope="single-command-preview-only",
            )
            binding = {**binding, **approval, "expires_in_seconds": approval["ttl_seconds"]}
        return {
            "service": self.settings.service_name,
            "mode": "shell-approval-binding-preview",
            "status": "blocked" if not preview["allowed"] else "approval_required",
            "approval_required": True,
            "would_execute": False,
            "binding": binding,
            "preview": preview,
            "safety": _safety(shell_status=preview["status"]),
            "ui": _ui("shell_approval_preview", "warning", "approval preview only"),
        }

    def approval_console_pending(self) -> dict:
        approvals = [_approval_console_safe_record(record) for record in self.approval_store.list()]
        audit_payload = {
            "operation": "approval-console-read-only-pending",
            "approval_count": len(approvals),
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "approval-console-read-only",
            "status": "completed",
            "approvals": approvals,
            "count": len(approvals),
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": _approval_console_gates(),
            "audit": _approval_console_audit(audit_payload),
            "safety": _safety(action_loop_status="disabled", browser_status="disabled", app_os_status="disabled"),
            "ui": _ui("approval_console_pending", "info", "read-only approval console"),
        }

    def approval_console_detail(self, approval_id: str) -> dict:
        approval = self.approval_store.get(approval_id)
        safe_approval = _approval_console_safe_record(approval) if approval else None
        status = "completed" if safe_approval else "not_found_or_expired"
        audit_payload = {
            "operation": "approval-console-read-only-detail",
            "approval_found": safe_approval is not None,
            "lookup_ref": _approval_console_ref(approval_id),
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "approval-console-read-only",
            "status": status,
            "approval": safe_approval,
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": _approval_console_gates(),
            "audit": _approval_console_audit(audit_payload),
            "safety": _safety(action_loop_status="disabled", browser_status="disabled", app_os_status="disabled"),
            "ui": _ui("approval_console_detail", "info" if safe_approval else "warning", status),
        }

    def approval_console_cleanup_expired(self) -> dict:
        cleanup = self.approval_store.cleanup_expired_summary()
        safe_cleanup = _approval_console_safe_cleanup(cleanup)
        audit_payload = {
            "operation": "approval-console-read-only-cleanup-expired",
            "expired_count": safe_cleanup["expired_count"],
            "records_removed": safe_cleanup["records_removed"],
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "approval-console-read-only",
            "status": safe_cleanup["status"],
            "cleanup": safe_cleanup,
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": _approval_console_gates(),
            "audit": _approval_console_audit(audit_payload),
            "safety": _safety(action_loop_status="disabled", browser_status="disabled", app_os_status="disabled"),
            "ui": _ui("approval_console_cleanup_expired", "info", safe_cleanup["status"]),
        }

    def durable_state_preview(self, request: AssistantDurableStatePreviewRequest) -> dict:
        frozen_steps = _freeze_steps(request.proposed_steps)
        masked_steps = _durable_state_preview_redact_sensitive_keys(
            _mask_secret_like_structure(frozen_steps)
        )
        safe_metadata = _durable_state_preview_safe_metadata(request.metadata)
        context_payload = {
            "goal": request.goal,
            "project_root": request.project_root,
            "steps": frozen_steps,
            "session_id": request.session_id,
            "request_id": request.request_id,
            "metadata": request.metadata,
        }
        context_hash = _stable_hash(context_payload)
        preview_state = {
            "state_schema_version": "durable_state_preview.v1",
            "preview_state_id": f"preview-state:{context_hash[:16]}",
            "state_status": "candidate-preview",
            "owner_session_ref": _durable_state_preview_ref("session", request.session_id),
            "request_context_ref": _durable_state_preview_ref("request", request.request_id),
            "plan_ref": f"plan-ref:{context_hash[16:32]}",
            "payload_hash_ref": f"payload-hash-ref:{context_hash[32:48]}",
            "masked_params": {
                "goal": _mask_secret_like_values(request.goal),
                "project_root": _mask_secret_like_values(request.project_root or ""),
                "metadata": safe_metadata,
            },
            "candidate_steps_count": len(masked_steps),
            "recovery_boundary": {
                "recovery_metadata_only": True,
                "auto_recovery": False,
                "auto_retry": False,
                "rollback_available": False,
                "rollback_unavailable": True,
            },
            "replay_boundary": {
                "replay_preview_only": True,
                "automatic_replay": False,
                "queued_replay_worker": False,
                "replay_does_not_dispatch_connector": True,
            },
            "approval_boundary": {
                "approval_consumed": False,
                "server_issued_approval_required_for_execution": True,
                "client_supplied_approval_like_json_trusted": False,
                "approval_console_state_can_override_payload_hash": False,
            },
            "manual_review_required": True,
            "stop_on_first_blocked": True,
        }
        audit_payload = {
            "operation": "durable-state-preview-read-only",
            "state_schema_version": preview_state["state_schema_version"],
            "preview_state_id": preview_state["preview_state_id"],
            "state_status": preview_state["state_status"],
            "candidate_steps_count": len(masked_steps),
            "read_only": True,
            "schema_only": True,
            "response_only": True,
            "would_execute": False,
            "would_persist": False,
            "would_dispatch": False,
            "approval_consumed": False,
            "raw_approval_id_included": False,
            "payload_hash_included": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "durable-state-preview-read-only",
            "status": "completed",
            "preview_state": preview_state,
            "candidate_steps": masked_steps,
            "read_only": True,
            "schema_only": True,
            "response_only": True,
            "would_execute": False,
            "would_persist": False,
            "would_dispatch": False,
            "approval_consumed": False,
            "gates": _durable_state_preview_gates(),
            "audit": _durable_state_preview_audit(audit_payload),
            "blocked_reasons": [],
            "required_user_decisions": [
                "stored preview lookup/list/cleanup endpoints remain Decision Required",
                "durable storage migration remains blocked",
                "queue worker, scheduler, daemon/service/background loop remain blocked",
            ],
            "safety": _safety(action_loop_status="disabled", browser_status="disabled", app_os_status="disabled") | {
                "durable_state_preview": "read-only-schema-only",
                "durable_storage": "not_connected",
                "queue_worker": "not_started",
            },
            "ui": _ui("durable_state_preview", "info", "read-only durable state preview"),
        }

    def shell_run(self, request: AssistantShellRunRequest) -> dict:
        preview = self.shell_preview(
            AssistantShellPreviewRequest(
                command=request.command,
                cwd=request.cwd,
                timeout_seconds=request.timeout_seconds,
            )
        )
        approval_check = None
        execution_enabled = self.settings.shell_execution_enabled
        safety = _safety(shell_status="enabled-allowlist" if execution_enabled else "disabled")
        if _shell_run_has_approval_injection(request):
            return _shell_run_response(
                service=self.settings.service_name,
                status="blocked",
                would_execute=False,
                execution_enabled=execution_enabled,
                reason="approval-like JSON injection 후보가 포함되어 shell 실행이 차단됩니다.",
                preview=preview,
                required_approval_hash=preview["audit"]["payload_hash"] if preview["allowed"] else None,
                request=request,
                approval_check=None,
                output=None,
                safety=safety,
            )
        if not preview["allowed"]:
            status = "blocked"
            reason = preview["reason"]
            return _shell_run_response(
                service=self.settings.service_name,
                status=status,
                would_execute=False,
                execution_enabled=execution_enabled,
                reason=reason,
                preview=preview,
                required_approval_hash=None,
                request=request,
                approval_check=None,
                output=None,
                safety=safety,
            )
        if not execution_enabled:
            approval_check = self.approval_store.validate(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="shell",
            )
            if not approval_check["valid"]:
                return _shell_run_response(
                    service=self.settings.service_name,
                    status="blocked",
                    would_execute=False,
                    execution_enabled=False,
                    reason=approval_check["reason"],
                    preview=preview,
                    required_approval_hash=preview["audit"]["payload_hash"],
                    request=request,
                    approval_check=approval_check,
                    output=None,
                    safety=safety,
                )
            return _shell_run_response(
                service=self.settings.service_name,
                status="disabled",
                would_execute=False,
                execution_enabled=False,
                reason="SHELL_EXECUTION_ENABLED=false 상태라 실제 subprocess 실행이 차단됩니다.",
                preview=preview,
                required_approval_hash=preview["audit"]["payload_hash"],
                request=request,
                approval_check=approval_check,
                output=None,
                safety=safety,
            )

        approval_check = self.approval_store.consume(
            approval_id=request.approval_id,
            payload_hash=request.approval_payload_hash,
            session_id=request.session_id,
            tool_name="shell",
        )
        if not approval_check["valid"]:
            return _shell_run_response(
                service=self.settings.service_name,
                status="blocked",
                would_execute=False,
                execution_enabled=True,
                reason=approval_check["reason"],
                preview=preview,
                required_approval_hash=preview["audit"]["payload_hash"],
                request=request,
                approval_check=approval_check,
                output=None,
                safety=safety,
            )
        output = _execute_shell_allowlist_command(
            command=request.command,
            cwd=preview["resolved_cwd"],
            timeout_seconds=preview["timeout_seconds"],
        )
        status = output["status"]
        return _shell_run_response(
            service=self.settings.service_name,
            status=status,
            would_execute=True,
            execution_enabled=True,
            reason=output["paste_safe_summary"],
            preview=preview,
            required_approval_hash=preview["audit"]["payload_hash"],
            request=request,
            approval_check=approval_check,
            output=output,
            safety=_safety(shell_status=status),
        )

    def patch_preview(self, request: AssistantPatchPreviewRequest) -> dict:
        policy = _evaluate_patch_policy(
            path=request.path,
            proposed_content=request.proposed_content,
            project_root=request.project_root,
            allowed_roots=self.settings.agent_allowed_roots,
        )
        audit = _patch_audit_payload(policy, request.reason)
        return {
            "service": self.settings.service_name,
            "mode": "patch-preview-locked",
            "path": request.path,
            "resolved_path": policy["resolved_path"],
            "status": policy["status"],
            "would_apply": False,
            "allowed": policy["allowed"],
            "reason": policy["reason"],
            "diff_preview": policy["diff_preview"],
            "truncated": policy["truncated"],
            "secret_scan": policy["secret_scan"],
            "rollback": policy["rollback"],
            "audit": audit,
            "safety": _safety(patch_status=policy["status"]),
            "ui": _ui("patch_preview", "info" if policy["allowed"] else "warning", policy["status"]),
        }

    def patch_approval_preview(self, request: AssistantPatchApprovalPreviewRequest) -> dict:
        preview = self.patch_preview(
            AssistantPatchPreviewRequest(
                path=request.path,
                proposed_content=request.proposed_content,
                project_root=request.project_root,
                reason=request.reason,
            )
        )
        binding = {
            "resolved_path": preview["resolved_path"],
            "audit_payload_hash": preview["audit"]["payload_hash"],
            "reason": _mask_secret_like_values(request.reason or ""),
            "status": preview["status"],
            "approval_scope": "single-file-patch-preview-only",
            "payload_hash": preview["audit"]["payload_hash"],
            "expires_in_seconds": 300,
            "store": "not-created",
            "manual_review_required": True,
            "server_issued": False,
            "single_use": True,
            "session_context": _approval_session_context(request.session_id),
        }
        if preview["allowed"]:
            approval = self.approval_store.issue(
                tool_name="patch",
                payload_hash=preview["audit"]["payload_hash"],
                session_id=request.session_id,
                scope="single-file-patch-preview-only",
            )
            binding = {**binding, **approval, "expires_in_seconds": approval["ttl_seconds"]}
        return {
            "service": self.settings.service_name,
            "mode": "patch-approval-binding-preview",
            "status": "blocked" if not preview["allowed"] else "approval_required",
            "approval_required": True,
            "would_apply": False,
            "binding": binding,
            "preview": preview,
            "safety": _safety(patch_status=preview["status"]),
            "ui": _ui("patch_approval_preview", "warning", "patch approval preview only"),
        }

    def patch_apply(self, request: AssistantPatchApplyRequest) -> dict:
        preview = self.patch_preview(
            AssistantPatchPreviewRequest(
                path=request.path,
                proposed_content=request.proposed_content,
                project_root=request.project_root,
            )
        )
        apply_result = None
        rollback = {
            **preview.get("rollback", {}),
            "automatic_rollback_enabled": False,
            "backup_file_created": False,
            "note": "29차 patch apply는 단일 파일 write만 수행하며 자동 rollback/restore는 수행하지 않습니다.",
        }
        audit_payload = {
            "resolved_path": preview["resolved_path"],
            "preview_payload_hash": preview["audit"]["payload_hash"],
            "provided_original_sha256": request.original_sha256,
            "would_apply": False,
            "execution_enabled": self.settings.patch_apply_enabled,
            "status": "pending",
        }
        if not preview["allowed"]:
            status = "blocked"
            reason = preview["reason"]
            approval_check = None
        else:
            approval_check = self.approval_store.consume(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="patch",
            )
            if not approval_check["valid"]:
                status = "blocked"
                reason = approval_check["reason"]
            elif not self.settings.patch_apply_enabled:
                status = "disabled"
                reason = "server approval은 검증/소비됐지만 PATCH_APPLY_ENABLED=false 상태라 실제 파일 write는 차단됩니다."
            elif request.original_sha256 != preview["rollback"].get("original_sha256"):
                status = "blocked"
                reason = "original_sha256이 patch preview의 원본 hash와 일치하지 않아 apply가 차단됩니다."
            else:
                resolved_path = Path(preview["resolved_path"])
                current_raw = resolved_path.read_bytes()
                current_sha = hashlib.sha256(current_raw).hexdigest()
                if current_sha != request.original_sha256:
                    status = "blocked"
                    reason = "apply 직전 디스크 original_sha256이 요청 hash와 달라 파일 write를 수행하지 않았습니다."
                else:
                    proposed_bytes = request.proposed_content.encode("utf-8")
                    resolved_path.write_text(request.proposed_content, encoding="utf-8")
                    new_sha = hashlib.sha256(proposed_bytes).hexdigest()
                    status = "applied"
                    reason = "승인된 단일 UTF-8 텍스트 파일 patch apply를 완료했습니다."
                    apply_result = {
                        "resolved_path": preview["resolved_path"],
                        "bytes_written": len(proposed_bytes),
                        "original_sha256": current_sha,
                        "new_sha256": new_sha,
                        "paste_safe_summary": (
                            f"patch_apply status=applied bytes_written={len(proposed_bytes)} "
                            f"original_sha256={current_sha} new_sha256={new_sha}"
                        ),
                    }
                    rollback = {
                        **rollback,
                        "available": True,
                        "original_sha256": current_sha,
                        "new_sha256": new_sha,
                        "manual_restore_required": True,
                        "automatic_rollback_enabled": False,
                        "backup_file_created": False,
                    }
        audit_payload = {
            **audit_payload,
            "status": status,
            "would_apply": status == "applied",
            "approval_status": approval_check.get("status") if approval_check else None,
            "apply_result_hash": _stable_hash(apply_result or {}),
            "rollback": rollback,
        }
        return {
            "service": self.settings.service_name,
            "mode": "patch-apply-v1" if self.settings.patch_apply_enabled else "patch-apply-locked",
            "status": status,
            "would_apply": status == "applied",
            "execution_enabled": self.settings.patch_apply_enabled,
            "reason": reason,
            "preview": preview,
            "required_approval_hash": preview["audit"]["payload_hash"] if preview["allowed"] else None,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": approval_check if preview["allowed"] else None,
            "apply_result": apply_result,
            "rollback": rollback,
            "audit": {
                "schema": "assistant.patch_apply.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "29차 patch apply는 env opt-in 단일 파일 write이며 action-loop/rollback executor와 연결하지 않습니다.",
            },
            "safety": _safety(patch_status=status),
            "ui": _ui(
                "patch_apply" if status == "applied" else "patch_apply_locked",
                "info" if status == "applied" else "warning",
                status,
            ),
        }

    def browser_preview(self, request: AssistantBrowserPreviewRequest) -> dict:
        policy = _evaluate_browser_policy(
            action=request.action,
            target_url=request.target_url,
            app_name=request.app_name,
            selector=request.selector,
            input_preview=request.input_preview,
            reason=request.reason,
        )
        audit = _browser_audit_payload(policy)
        return {
            "service": self.settings.service_name,
            "mode": "browser-interaction-preview-locked",
            "status": policy["status"],
            "action": policy["action"],
            "target_url": policy["target_url"],
            "app_name": policy["app_name"],
            "would_interact": False,
            "allowed": policy["allowed"],
            "reason": policy["reason"],
            "risk": policy["risk"],
            "required_manual_confirmation": True,
            "taxonomy": policy["taxonomy"],
            "gate": _browser_gate_payload(policy),
            "audit": audit,
            "safety": _safety(browser_status=policy["status"]),
            "ui": _ui("browser_preview", "info" if policy["allowed"] else "warning", policy["status"]),
        }

    def browser_approval_preview(self, request: AssistantBrowserApprovalPreviewRequest) -> dict:
        preview = self.browser_preview(
            AssistantBrowserPreviewRequest(
                action=request.action,
                target_url=request.target_url,
                app_name=request.app_name,
                selector=request.selector,
                input_preview=request.input_preview,
                reason=request.reason,
            )
        )
        binding = {
            "action": preview["action"],
            "target_url": preview["target_url"],
            "app_name": preview["app_name"],
            "audit_payload_hash": preview["audit"]["payload_hash"],
            "reason": _mask_secret_like_values(request.reason or ""),
            "status": preview["status"],
            "approval_scope": "single-browser-preview-only",
            "payload_hash": preview["audit"]["payload_hash"],
            "expires_in_seconds": 300,
            "store": "not-created",
            "manual_review_required": True,
            "server_issued": False,
            "single_use": True,
            "session_context": _approval_session_context(request.session_id),
        }
        if preview["allowed"]:
            approval = self.approval_store.issue(
                tool_name="browser",
                payload_hash=preview["audit"]["payload_hash"],
                session_id=request.session_id,
                scope="single-browser-preview-only",
            )
            binding = {**binding, **approval, "expires_in_seconds": approval["ttl_seconds"]}
        return {
            "service": self.settings.service_name,
            "mode": "browser-approval-binding-preview",
            "status": "blocked" if not preview["allowed"] else "approval_required",
            "approval_required": True,
            "would_interact": False,
            "binding": binding,
            "preview": preview,
            "safety": _safety(browser_status=preview["status"]),
            "ui": _ui("browser_approval_preview", "warning", "browser approval preview only"),
        }

    def browser_interact(self, request: AssistantBrowserInteractRequest) -> dict:
        preview = self.browser_preview(
            AssistantBrowserPreviewRequest(
                action=request.action,
                target_url=request.target_url,
                app_name=request.app_name,
                selector=request.selector,
                input_preview=request.input_preview,
            )
        )
        if not preview["allowed"]:
            status = "blocked"
            reason = preview["reason"]
        else:
            approval_check = self.approval_store.consume(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="browser",
            )
            if approval_check["valid"]:
                status = "locked"
                reason = "server approval은 검증/소비됐지만 7차 browser/app interaction은 기본값 locked/disabled입니다. 실제 click/fill/submit/login/payment/delete 또는 OS app control은 연결하지 않았습니다."
            else:
                status = "blocked"
                reason = approval_check["reason"]
        return {
            "service": self.settings.service_name,
            "mode": "browser-interact-locked",
            "status": status,
            "would_interact": False,
            "execution_enabled": False,
            "reason": reason,
            "preview": preview,
            "required_approval_hash": preview["audit"]["payload_hash"] if preview["allowed"] else None,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": approval_check if preview["allowed"] else None,
            "safety": _safety(browser_status=status),
            "ui": _ui("browser_interact_locked", "warning", status),
        }

    def browser_observe(self, request: AssistantBrowserObserveRequest) -> dict:
        preview = self.browser_preview(
            AssistantBrowserPreviewRequest(
                action=request.action,
                target_url=request.target_url,
            )
        )
        policy_reason = _browser_observe_policy_reason(
            action=preview["action"],
            target_url=request.target_url,
            allowed_origins=self.settings.browser_observe_allowed_origins,
        )
        observe_result = None
        result_wrapper = None
        approval_check = None
        if not preview["allowed"]:
            status = "blocked"
            reason = preview["reason"]
        elif policy_reason:
            status = "blocked"
            reason = policy_reason
        elif not self.settings.browser_observe_enabled:
            status = "disabled"
            reason = "BROWSER_OBSERVE_ENABLED=false 상태라 browser observe 실행이 차단됩니다."
        else:
            approval_check = self.approval_store.consume(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="browser",
            )
            if not approval_check["valid"]:
                status = "blocked"
                reason = approval_check["reason"]
            else:
                observe_result = _execute_browser_observe(
                    action=preview["action"],
                    target_url=request.target_url,
                )
                status = observe_result["status"]
                reason = observe_result["paste_safe_summary"]
                result_wrapper = _browser_observe_result_wrapper(observe_result)
        audit_payload = {
            "action": preview["action"],
            "target_url": request.target_url,
            "status": status,
            "would_observe": status == "completed",
            "execution_enabled": self.settings.browser_observe_enabled,
            "observe_result_hash": _stable_hash(observe_result or {}),
            "approval_status": approval_check.get("status") if approval_check else None,
        }
        return {
            "service": self.settings.service_name,
            "mode": "browser-observe-v1" if self.settings.browser_observe_enabled else "browser-observe-locked",
            "status": status,
            "action": preview["action"],
            "target_url": _mask_secret_like_values(request.target_url),
            "would_observe": status == "completed",
            "execution_enabled": self.settings.browser_observe_enabled,
            "reason": _mask_secret_like_values(reason),
            "preview": preview,
            "observe_result": observe_result,
            "result_wrapper": result_wrapper,
            "required_approval_hash": preview["audit"]["payload_hash"] if preview["allowed"] and not policy_reason else None,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": approval_check,
            "audit": {
                "schema": "assistant.browser_observe.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "31차 browser observe는 loopback URL read-only observation만 수행하며 click/fill/submit/login/payment/delete를 수행하지 않습니다.",
            },
            "safety": {
                **_safety(browser_status=status),
                "browser_observe": "enabled-read-only" if self.settings.browser_observe_enabled else "disabled",
                "browser_interaction": "blocked",
            },
            "ui": _ui("browser_observe", "info" if status == "completed" else "warning", status),
        }

    def browser_limited_interact(self, request: AssistantBrowserLimitedInteractRequest) -> dict:
        policy = _browser_limited_interaction_policy(
            action=request.action,
            target_url=request.target_url,
            selector=request.selector,
            field_name=request.field_name,
            input_preview=request.input_preview,
            allowed_origins=self.settings.browser_limited_interaction_allowed_origins,
            allowed_selectors=self.settings.browser_limited_interaction_allowed_selectors,
            allowed_fill_fields=self.settings.browser_limited_interaction_allowed_fill_fields,
        )
        interaction_result = None
        result_wrapper = None
        approval_check = None
        if not policy["allowed"]:
            status = "blocked"
            reason = policy["reason"]
        elif not self.settings.browser_limited_interaction_enabled:
            status = "disabled"
            reason = "BROWSER_LIMITED_INTERACTION_ENABLED=false 상태라 browser limited interaction이 차단됩니다."
        else:
            approval_check = self.approval_store.consume(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="browser",
            )
            if not approval_check["valid"]:
                status = "blocked"
                reason = approval_check["reason"]
            else:
                interaction_result = _browser_limited_interaction_candidate_result(policy)
                result_wrapper = _browser_limited_interaction_result_wrapper(interaction_result)
                status = interaction_result["status"]
                reason = interaction_result["paste_safe_summary"]
        audit_payload = {
            "action": policy["action"],
            "target_url": policy["target_url"],
            "selector": policy["selector"],
            "field_name": policy["field_name"],
            "status": status,
            "would_interact": False,
            "execution_enabled": self.settings.browser_limited_interaction_enabled,
            "interaction_result_hash": _stable_hash(interaction_result or {}),
            "approval_status": approval_check.get("status") if approval_check else None,
        }
        return {
            "service": self.settings.service_name,
            "mode": (
                "browser-limited-interact-v1"
                if self.settings.browser_limited_interaction_enabled
                else "browser-limited-interact-locked"
            ),
            "status": status,
            "action": policy["action"],
            "target_url": _mask_secret_like_values(request.target_url),
            "selector": _mask_secret_like_values(request.selector),
            "would_interact": False,
            "execution_enabled": self.settings.browser_limited_interaction_enabled,
            "reason": _mask_secret_like_values(reason),
            "policy": policy,
            "interaction_result": interaction_result,
            "result_wrapper": result_wrapper,
            "required_approval_hash": policy["payload_hash"] if policy["allowed"] else None,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": approval_check,
            "audit": {
                "schema": "assistant.browser_limited_interact.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "32차 limited interaction은 candidate validation만 수행하며 browser launch/click/fill/profile mutation을 수행하지 않습니다.",
            },
            "safety": {
                **_safety(browser_status=status),
                "browser_limited_interaction": (
                    "enabled-candidate-validation"
                    if self.settings.browser_limited_interaction_enabled
                    else "disabled"
                ),
                "browser_interaction": "blocked",
                "browser_launch": "not_performed",
            },
            "ui": _ui("browser_limited_interact", "info" if status == "validated" else "warning", status),
        }

    def _action_loop_step_preview(self, index: int, step: dict) -> dict:
        tool = str(step.get("tool") or "").strip().lower()
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
        approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
        violations = []
        preview: dict | None = None
        required_payload_hash = None
        if wrapper.get("untrusted") is not True:
            violations.append("missing_untrusted_wrapper")
        if tool == "shell":
            preview = self.shell_preview(
                AssistantShellPreviewRequest(
                    command=str(params.get("command") or ""),
                    cwd=str(params.get("cwd") or "."),
                    timeout_seconds=int(params.get("timeout_seconds") or 30),
                )
            )
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
        elif tool == "patch":
            preview = self.patch_preview(
                AssistantPatchPreviewRequest(
                    path=str(params.get("path") or ""),
                    proposed_content=str(params.get("proposed_content") or ""),
                    project_root=params.get("project_root"),
                    reason="action-loop preflight",
                )
            )
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
        elif tool == "browser":
            preview = self.browser_preview(
                AssistantBrowserPreviewRequest(
                    action=str(params.get("action") or ""),
                    target_url=params.get("target_url"),
                    app_name=params.get("app_name"),
                    selector=params.get("selector"),
                    input_preview=params.get("input_preview"),
                    reason="action-loop preflight",
                )
            )
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
        else:
            violations.append("unsupported_tool")
        if preview is not None and not preview.get("allowed"):
            violations.append("unsafe_action")
        provided_payload_hash = approval_binding.get("payload_hash")
        provided_approval_id = approval_binding.get("approval_id")
        provided_session_id = approval_binding.get("session_id")
        approval_check = None
        if required_payload_hash and not provided_payload_hash:
            violations.append("missing_approval_binding")
        elif required_payload_hash and provided_payload_hash != required_payload_hash:
            violations.append("payload_hash_mismatch")
        if required_payload_hash:
            approval_check = self.approval_store.validate(
                approval_id=provided_approval_id,
                payload_hash=provided_payload_hash,
                session_id=provided_session_id,
                tool_name=tool,
            )
            if not provided_approval_id and "missing_approval_binding" not in violations:
                violations.append("missing_approval_binding")
            elif not approval_check["valid"] and approval_check["status"] not in {
                "missing_approval_id",
                "payload_hash_mismatch",
            }:
                violations.append(f"approval_{approval_check['status']}")
            elif not approval_check["valid"] and approval_check["status"] == "missing_approval_id":
                violations.append("missing_approval_binding")
        status = "allowed_preview" if preview is not None and not violations else "blocked"
        return {
            "index": index,
            "tool": tool or "unknown",
            "status": status,
            "would_dispatch": False,
            "execution_enabled": False,
            "required_payload_hash": required_payload_hash,
            "provided_approval_id": provided_approval_id,
            "provided_payload_hash": provided_payload_hash,
            "approval_check": approval_check,
            "violations": violations,
            "preview_summary": _action_loop_preview_summary(tool, preview),
        }

    def _action_loop_shell_step_preview(self, index: int, step: dict) -> dict:
        tool = str(step.get("tool") or "").strip().lower()
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
        approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
        violations: list[str] = []
        preview: dict | None = None
        required_payload_hash = None
        approval_check = None
        if wrapper.get("untrusted") is not True:
            violations.append("missing_untrusted_wrapper")
        if tool != "shell":
            violations.append("unsupported_tool")
        else:
            preview = self.shell_preview(
                AssistantShellPreviewRequest(
                    command=str(params.get("command") or ""),
                    cwd=str(params.get("cwd") or "."),
                    timeout_seconds=int(params.get("timeout_seconds") or 30),
                )
            )
            if not preview["allowed"]:
                violations.append("unsafe_shell_action")
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
        provided_payload_hash = approval_binding.get("payload_hash")
        provided_approval_id = approval_binding.get("approval_id")
        provided_session_id = approval_binding.get("session_id")
        if _contains_approval_like_json(params):
            violations.append("approval_like_json_injection_blocked")
        if required_payload_hash:
            approval_check = self.approval_store.validate(
                approval_id=provided_approval_id,
                payload_hash=provided_payload_hash,
                session_id=provided_session_id,
                tool_name="shell",
            )
            if not provided_approval_id or not provided_payload_hash:
                violations.append("missing_approval_binding")
            elif provided_payload_hash != required_payload_hash:
                violations.append("payload_hash_mismatch")
            elif not approval_check["valid"]:
                violations.append(f"approval_{approval_check['status']}")
        status = "allowed_preview" if preview is not None and not violations else "blocked"
        return {
            "index": index,
            "tool": tool or "unknown",
            "route": "shell://allowlist" if tool == "shell" else "blocked://unsupported",
            "status": status,
            "would_execute": False,
            "execution_enabled": False,
            "required_payload_hash": required_payload_hash,
            "provided_approval_id": provided_approval_id,
            "provided_payload_hash": provided_payload_hash,
            "approval_check": approval_check,
            "violations": violations,
            "preview_summary": _action_loop_preview_summary(tool, preview),
        }

    def _action_loop_patch_step_preview(self, index: int, step: dict) -> dict:
        tool = str(step.get("tool") or "").strip().lower()
        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
        approval_binding = step.get("approval_binding") if isinstance(step.get("approval_binding"), dict) else {}
        violations: list[str] = []
        preview: dict | None = None
        required_payload_hash = None
        approval_check = None
        provided_original_sha256 = params.get("original_sha256")
        required_original_sha256 = None
        if wrapper.get("untrusted") is not True:
            violations.append("missing_untrusted_wrapper")
        if tool != "patch":
            violations.append("unsupported_tool")
        else:
            preview = self.patch_preview(
                AssistantPatchPreviewRequest(
                    path=str(params.get("path") or ""),
                    proposed_content=str(params.get("proposed_content") or ""),
                    project_root=params.get("project_root"),
                )
            )
            if not preview["allowed"]:
                violations.append("unsafe_patch_action")
            required_payload_hash = preview["audit"]["payload_hash"] if preview["allowed"] else None
            required_original_sha256 = preview["rollback"].get("original_sha256") if preview["allowed"] else None
            if required_original_sha256 and provided_original_sha256 != required_original_sha256:
                violations.append("original_sha256_mismatch")
        provided_payload_hash = approval_binding.get("payload_hash")
        provided_approval_id = approval_binding.get("approval_id")
        provided_session_id = approval_binding.get("session_id")
        if _contains_approval_like_json(params):
            violations.append("approval_like_json_injection_blocked")
        if required_payload_hash:
            approval_check = self.approval_store.validate(
                approval_id=provided_approval_id,
                payload_hash=provided_payload_hash,
                session_id=provided_session_id,
                tool_name="patch",
            )
            if not provided_approval_id or not provided_payload_hash:
                violations.append("missing_approval_binding")
            elif provided_payload_hash != required_payload_hash:
                violations.append("payload_hash_mismatch")
            elif not approval_check["valid"]:
                violations.append(f"approval_{approval_check['status']}")
        status = "allowed_preview" if preview is not None and not violations else "blocked"
        return {
            "index": index,
            "tool": tool or "unknown",
            "route": "patch://single-file" if tool == "patch" else "blocked://unsupported",
            "status": status,
            "would_apply": False,
            "execution_enabled": False,
            "required_payload_hash": required_payload_hash,
            "provided_approval_id": provided_approval_id,
            "provided_payload_hash": provided_payload_hash,
            "required_original_sha256": required_original_sha256,
            "provided_original_sha256": provided_original_sha256,
            "approval_check": approval_check,
            "violations": violations,
            "preview_summary": _action_loop_preview_summary(tool, preview),
        }

    def automation_plan(self, request: AssistantAutomationPlanRequest) -> dict:
        root_status = None
        if request.project_root:
            root_status = self.validate_project_root(ProjectRootValidateRequest(project_root=request.project_root))
        allowed_root_ready = bool(root_status and root_status["safe_for_read_only_agent"])
        current_capabilities = [
            {
                "capability": "local_rag",
                "status": "ready",
                "execution": "ollama_local_only",
                "notes": "문서 업로드, 검색, ask-with-docs는 현재 지원됩니다.",
            },
            {
                "capability": "folder_index_preview",
                "status": "ready",
                "execution": "read_only_preview",
                "notes": "색인 전 파일 수, 예상 chunk, embedding batch를 확인할 수 있습니다.",
            },
            {
                "capability": "file_preview",
                "status": "conditional",
                "execution": "read_only_agent_v1",
                "notes": "AGENT_EXECUTION_ENABLED=true와 허용 root 안에서만 텍스트 preview가 가능합니다.",
                "project_root_ready": allowed_root_ready,
            },
            {
                "capability": "web_fetch",
                "status": "conditional",
                "execution": "explicit_url_read_only_fetch",
                "notes": "브라우저 조작이 아니라 명시 URL 단건 fetch만 별도 flag에서 가능합니다.",
            },
            {
                "capability": "shell",
                "status": "locked_preview",
                "execution": "allowlist_preview_and_locked_run_only",
                "notes": "shell-preview, approval-preview, locked shell-run 계약만 제공하며 실제 subprocess 실행은 하지 않습니다.",
            },
            {
                "capability": "browser_interaction",
                "status": "locked_preview",
                "execution": "taxonomy_preview_and_locked_interact_only",
                "notes": "browser-preview, approval-preview, locked browser-interact 계약만 제공하며 실제 click/fill/submit/login/payment/delete 또는 OS app control은 하지 않습니다.",
            },
            {
                "capability": "file_write_delete",
                "status": "locked_preview",
                "execution": "diff_preview_and_locked_apply_only",
                "notes": "patch-preview, approval-preview, locked patch-apply 계약만 제공하며 실제 파일 수정은 하지 않습니다.",
            },
            {
                "capability": "external_llm_api",
                "status": "blocked",
                "execution": "not_used",
                "notes": "OpenAI/Claude/Gemini API는 이 프로젝트 런타임에 사용하지 않습니다.",
            },
        ]
        automation_stages = [
            {
                "stage": 1,
                "name": "Local knowledge API",
                "status": "implemented",
                "codex_can_continue": True,
                "activation": "already safe local API",
            },
            {
                "stage": 2,
                "name": "Assistant UI bridge",
                "status": "implemented",
                "codex_can_continue": True,
                "activation": "read-only/status/message contract",
            },
            {
                "stage": 3,
                "name": "Automation preflight",
                "status": "implemented_by_this_endpoint",
                "codex_can_continue": True,
                "activation": "plan-only; no tool execution",
            },
            {
                "stage": 4,
                "name": "Read-only file and URL adapters",
                "status": "conditional",
                "codex_can_continue": True,
                "activation": "only within existing agent read-only v1 gates",
            },
            {
                "stage": 5,
                "name": "Shell sandbox",
                "status": "implemented_locked_preview",
                "codex_can_continue": True,
                "activation": "allowlist preview, approval binding preview, locked run; no subprocess",
            },
            {
                "stage": 6,
                "name": "File patch automation",
                "status": "implemented_locked_preview",
                "codex_can_continue": True,
                "activation": "diff preview, approval binding preview, locked apply; no file write/delete",
            },
            {
                "stage": 7,
                "name": "Browser interaction",
                "status": "implemented_locked_preview",
                "codex_can_continue": True,
                "activation": "taxonomy preview, approval binding preview, locked interact; no browser/app control",
            },
            {
                "stage": 8,
                "name": "External provider/API expansion",
                "status": "review_required",
                "codex_can_continue": False,
                "activation": "blocked; no external LLM/API provider by default",
            },
        ]
        return {
            "service": self.settings.service_name,
            "goal": request.goal,
            "local_only": True,
            "would_execute": False,
            "current_capabilities": current_capabilities,
            "automation_stages": automation_stages,
            "codex_safe_now": [
                "문서/RAG API 계약과 테스트 보강",
                "assistant UI bridge 응답 필드 보강",
                "folder index preview와 read-only agent v1 회귀 테스트 보강",
                "safe capability honesty 문서와 API inventory 정합성 유지",
            ],
            "blocked_until_review": [
                "실제 shell 실행",
                "브라우저 click/fill/submit/login/payment/delete 자동화",
                "원본 파일 생성/수정/삭제 자동화",
                "외부 LLM/API provider 활성화",
                "운영 배포, cloud/Oracle 리소스 변경, 비용 영향 작업",
            ],
            "required_user_decisions": [
                "자동화 1차 target을 read-only file preview, explicit URL fetch, UI bridge 중 하나로 선택",
                "허용할 project root와 private data 제외 범위 확정",
                "실제 실행 기능은 별도 보안 리뷰와 최종 승인 후 stage별로 활성화",
            ],
            "safety": _safety(),
            "ui": {
                "response_type": "automation_plan",
                "severity": "warning",
                "primary_text": "개인 API 자동화는 plan-only로 정리했습니다.",
                "display": "panel",
            },
            "recommended_next_model": {
                "recommended_ai": "Codex",
                "recommended_model": "Codex GPT-5.5",
                "reason": "현재 단계는 read-only API 계약, 테스트, 문서 보강이므로 Codex가 안전하게 계속 처리 가능합니다.",
                "next_task": "자동화 target을 하나 고른 뒤 preview/read-only 범위에서 API와 테스트를 확장",
                "user_action_required": "실제 shell/browser/file-write/external API 활성화는 별도 최종 승인 전 진행 불가",
            },
        }

    def workflow_presets(self) -> dict:
        presets = [_workflow_preset_public(preset) for preset in WORKFLOW_PRESETS.values()]
        return {
            "service": self.settings.service_name,
            "mode": "workflow-preset-list-preview",
            "presets": presets,
            "would_dispatch": False,
            "execution_enabled": False,
            "safety": _safety(),
            "ui": _ui("workflow_presets", "info", "workflow presets preview"),
        }

    def workflow_preset_detail(self, preset_id: str) -> dict:
        normalized_id = _normalize_preset_id(preset_id)
        preset = WORKFLOW_PRESETS.get(normalized_id)
        status = "available" if preset else "blocked"
        return {
            "service": self.settings.service_name,
            "mode": "workflow-preset-detail-preview",
            "preset_id": normalized_id,
            "status": status,
            "preset": _workflow_preset_public(preset) if preset else None,
            "would_dispatch": False,
            "execution_enabled": False,
            "safety": _safety(),
            "ui": _ui("workflow_preset_detail", "info" if preset else "warning", status),
        }

    def workflow_preset_preview(self, preset_id: str, request: AssistantWorkflowPresetPreviewRequest) -> dict:
        normalized_id = _normalize_preset_id(preset_id)
        raw_params = request.params if isinstance(request.params, dict) else {}
        masked_params = _mask_secret_like_structure(raw_params)
        preset = WORKFLOW_PRESETS.get(normalized_id)
        blocked_reasons: list[str] = []
        if normalized_id in UNSAFE_WORKFLOW_PRESETS:
            blocked_reasons.append("unsafe_preset_blocked")
        elif preset is None:
            blocked_reasons.append("unknown_or_unsafe_preset")
        elif preset.get("unsafe"):
            blocked_reasons.append("unsafe_preset_blocked")
        blocked_reasons.extend(_workflow_param_violations(raw_params))
        steps = []
        if preset is not None and not blocked_reasons:
            steps = _freeze_steps(_workflow_preset_steps(preset, masked_params))
        audit_payload = {
            "preset_id": normalized_id,
            "params": masked_params,
            "steps": steps,
            "steps_count": len(steps),
            "would_dispatch": False,
            "execution_enabled": False,
            "blocked_reasons": blocked_reasons,
        }
        status = "blocked" if blocked_reasons else "proposed_steps_preview"
        return {
            "service": self.settings.service_name,
            "mode": "workflow-preset-proposed-steps-preview",
            "preset_id": normalized_id,
            "status": status,
            "preset": _workflow_preset_public(preset) if preset and not preset.get("unsafe") else None,
            "frozen_proposed_steps": steps,
            "would_dispatch": False,
            "execution_enabled": False,
            "blocked_reasons": blocked_reasons,
            "unsafe_policy": {
                "schema": "assistant.workflow_preset.unsafe_policy.v1",
                "dispatch_connected": False,
                "shell_execution_connected": False,
                "patch_apply_connected": False,
                "browser_interaction_connected": False,
                "external_api_connected": False,
                "approval_like_json_trusted": False,
                "masking_required": True,
                "unsafe_presets_blocked": True,
            },
            "audit": {
                "schema": "assistant.workflow_preset.preview.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "workflow preset preview는 proposed_steps 생성 계약이며 action-loop dispatch를 수행하지 않습니다.",
            },
            "safety": _safety(action_loop_status=status),
            "ui": _ui("workflow_preset_preview", "warning" if blocked_reasons else "info", status),
        }

    def task_queue_preview(self, request: AssistantTaskQueueCreateRequest) -> dict:
        task_type = _normalize_task_type(request.task_type)
        raw_params = request.params if isinstance(request.params, dict) else {}
        masked_params = _mask_secret_like_structure(raw_params)
        blocked_reasons = _task_queue_blocked_reasons(task_type, raw_params)
        task = None
        if not blocked_reasons:
            task_payload = {
                "schema": "assistant.long_running_task.locked_preview.v1",
                "task_type": task_type,
                "status": "queued",
                "params": masked_params,
                "allowed_scope": "noop/read-only preview only",
                "execution": {
                    "would_enqueue": False,
                    "would_execute": False,
                    "would_dispatch": False,
                    "would_apply": False,
                    "would_interact": False,
                    "worker_enabled": False,
                    "background_execution_started": False,
                    "execution_enabled": False,
                },
                "audit_link": {
                    "schema": "assistant.long_running_task.audit_link.v1",
                    "source": "task_queue_preview",
                    "task_type": task_type,
                },
            }
            task = self.task_queue_store.create(task_payload, ttl_seconds=request.ttl_seconds)
            task["audit_link"]["task_id"] = task["task_id"]
            task["audit_link"]["payload_hash"] = _stable_hash(_task_audit_payload(task))
        audit_payload = {
            "task_type": task_type,
            "params": masked_params,
            "blocked_reasons": blocked_reasons,
            "task_id": task["task_id"] if task else None,
            "would_enqueue": False,
            "worker_enabled": False,
            "execution_enabled": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "long-running-queue-locked-preview",
            "status": "blocked" if blocked_reasons else "queued",
            "task": task,
            "blocked_reasons": blocked_reasons,
            "allowed_task_types": sorted(ALLOWED_TASK_QUEUE_TYPES),
            "would_enqueue": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": _task_audit(audit_payload),
            "cleanup_policy": _task_cleanup_policy(),
            "safety": _safety(action_loop_status="locked"),
            "ui": _ui("task_queue_preview", "warning" if blocked_reasons else "info", "task queue locked preview"),
        }

    def task_queue(self) -> dict:
        tasks = self.task_queue_store.list()
        return {
            "service": self.settings.service_name,
            "mode": "long-running-queue-list-read-only",
            "tasks": tasks,
            "statuses": TASK_QUEUE_STATUSES,
            "would_execute": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "cleanup_policy": _task_cleanup_policy(),
            "safety": _safety(action_loop_status="locked"),
            "ui": _ui("task_queue", "info", "task queue status read-only"),
        }

    def task_queue_drain(self, request: AssistantTaskQueueDrainRequest) -> dict:
        tasks = self.task_queue_store.list()
        worker = _task_queue_worker_policy(
            enabled=self.settings.task_queue_worker_enabled,
            requested_limit=request.limit,
            configured_limit=self.settings.task_queue_worker_max_drain,
        )
        if not self.settings.task_queue_worker_enabled:
            audit_payload = {
                "worker_enabled": False,
                "requested_limit": request.limit,
                "available_tasks": len(tasks),
                "drained_count": 0,
            }
            return {
                "service": self.settings.service_name,
                "mode": "task_queue_worker_disabled",
                "status": "disabled",
                "worker_enabled": False,
                "execution_enabled": False,
                "would_execute": False,
                "drained_count": 0,
                "tasks": tasks,
                "results": [],
                "blocked_reasons": ["task_queue_worker_disabled"],
                "allowed_task_types": sorted(TASK_QUEUE_WORKER_ALLOWED_TYPES),
                "worker": worker,
                "audit": _task_worker_audit(audit_payload),
                "cleanup_policy": _task_cleanup_policy(),
                "safety": _safety(action_loop_status="locked") | {"task_queue_worker": "disabled"},
                "ui": _ui("task_queue_drain", "warning", "disabled"),
            }

        results: list[dict] = []
        updated_tasks: list[dict] = []
        limit = worker["effective_limit"]
        for task in tasks:
            if len(results) >= limit:
                break
            if task.get("status") != "queued":
                continue
            result = self._task_queue_execute_one_shot(task)
            updated = self.task_queue_store.update_execution(
                task["task_id"],
                status=result["status"],
                result=result,
                worker={
                    "one_shot_drain": True,
                    "daemon_started": False,
                    "service_installed": False,
                    "task_type": task.get("task_type"),
                },
            )
            results.append(result)
            if updated:
                updated_tasks.append(updated)

        status = "completed" if results and all(item["status"] == "completed" for item in results) else "blocked"
        if not results:
            status = "idle"
        blocked_reasons = sorted(
            {
                reason
                for result in results
                for reason in result.get("blocked_reasons", [])
            }
        )
        audit_payload = {
            "worker_enabled": True,
            "requested_limit": request.limit,
            "effective_limit": limit,
            "available_tasks": len(tasks),
            "drained_count": len(results),
            "result_statuses": [result["status"] for result in results],
            "blocked_reasons": blocked_reasons,
        }
        return {
            "service": self.settings.service_name,
            "mode": "task_queue_worker_one_shot_drain",
            "status": status,
            "worker_enabled": True,
            "execution_enabled": True,
            "would_execute": False,
            "drained_count": len(results),
            "tasks": updated_tasks,
            "results": results,
            "blocked_reasons": blocked_reasons,
            "allowed_task_types": sorted(TASK_QUEUE_WORKER_ALLOWED_TYPES),
            "worker": worker,
            "audit": _task_worker_audit(audit_payload),
            "cleanup_policy": _task_cleanup_policy(),
            "safety": _safety(action_loop_status="locked") | {"task_queue_worker": "enabled-one-shot-drain"},
            "ui": _ui("task_queue_drain", "info" if status == "completed" else "warning", status),
        }

    def _task_queue_execute_one_shot(self, task: dict) -> dict:
        task_type = _normalize_task_type(task.get("task_type", ""))
        params = task.get("params") if isinstance(task.get("params"), dict) else {}
        blocked_reasons = _task_queue_worker_blocked_reasons(task_type, params)
        if blocked_reasons:
            result = {
                "schema": "assistant.task_queue.worker_result.v1",
                "task_id": task.get("task_id"),
                "task_type": task_type,
                "status": "blocked",
                "blocked_reasons": blocked_reasons,
                "result": None,
            }
            return _task_queue_worker_result_wrapper(result)
        if task_type == "noop":
            result = {
                "schema": "assistant.task_queue.worker_result.v1",
                "task_id": task.get("task_id"),
                "task_type": task_type,
                "status": "completed",
                "blocked_reasons": [],
                "result": {"noop": True, "summary": "no-op task completed by one-shot worker"},
            }
            return _task_queue_worker_result_wrapper(result)

        adapter_request = _task_queue_adapter_request(task_type, params)
        adapter_result = self.read_only_adapter_execute(adapter_request)
        status = "completed" if adapter_result["status"] == "completed" else "blocked"
        blocked = [] if status == "completed" else [adapter_result["status"]]
        result = {
            "schema": "assistant.task_queue.worker_result.v1",
            "task_id": task.get("task_id"),
            "task_type": task_type,
            "status": status,
            "blocked_reasons": blocked,
            "result": adapter_result,
        }
        return _task_queue_worker_result_wrapper(result)

    def task_queue_detail(self, task_id: str) -> dict:
        task = self.task_queue_store.get(task_id)
        status = task["status"] if task else "blocked"
        audit_payload = {
            "task_id": task_id,
            "task_found": task is not None,
            "status": status,
            "would_execute": False,
            "worker_enabled": False,
            "execution_enabled": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "long-running-queue-detail-read-only",
            "task_id": task_id,
            "status": status,
            "task": task,
            "would_execute": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": _task_audit(audit_payload),
            "safety": _safety(action_loop_status="locked"),
            "ui": _ui("task_queue_detail", "info" if task else "warning", status),
        }

    def task_queue_cancel_preview(self, task_id: str) -> dict:
        task = self.task_queue_store.cancel(task_id)
        status = task["status"] if task else "blocked"
        cancellation = task["cancellation"] if task else {
            "requested": False,
            "cancelled_at": None,
            "reason": "unknown task id; no worker cancellation performed",
        }
        audit_payload = {
            "task_id": task_id,
            "task_found": task is not None,
            "status": status,
            "cancellation": cancellation,
            "would_cancel_worker": False,
            "worker_enabled": False,
            "execution_enabled": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "long-running-cancel-locked-preview",
            "task_id": task_id,
            "status": status,
            "task": task,
            "cancellation": cancellation,
            "would_cancel_worker": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": _task_audit(audit_payload),
            "safety": _safety(action_loop_status="locked"),
            "ui": _ui("task_queue_cancel_preview", "info" if task else "warning", status),
        }

    def failure_recovery_preview(self, request: AssistantFailureRecoveryPreviewRequest) -> dict:
        tool = str(request.tool)
        raw_params = request.params if isinstance(request.params, dict) else {}
        masked_params = _mask_secret_like_structure(raw_params)
        failure = _failure_summary(tool, request.failure_reason, request.summary, masked_params)
        rollback_plan = _rollback_plan_for_failure(tool, failure, masked_params, request.original_sha256)
        manual_instructions = _manual_recovery_instructions(tool, rollback_plan)
        paste_safe_summary = _failure_paste_safe_summary(failure, rollback_plan)
        audit_payload = {
            "tool": tool,
            "failure": failure,
            "rollback_plan": rollback_plan,
            "would_execute": False,
            "would_apply": False,
            "would_interact": False,
            "rollback_enabled": False,
            "execution_enabled": False,
        }
        return {
            "service": self.settings.service_name,
            "mode": "failure-recovery-rollback-locked-preview",
            "tool": tool,
            "status": "rollback_preview" if tool == "patch" else "manual_instruction_only",
            "failure": failure,
            "rollback_plan": rollback_plan,
            "manual_instructions": manual_instructions,
            "paste_safe_summary": paste_safe_summary,
            "would_execute": False,
            "would_apply": False,
            "would_interact": False,
            "rollback_enabled": False,
            "execution_enabled": False,
            "audit": {
                "schema": "assistant.failure_recovery.preview.v1",
                "payload": audit_payload,
                "payload_hash": _stable_hash(audit_payload),
                "note": "failure recovery는 rollback plan preview이며 자동 rollback을 수행하지 않습니다.",
            },
            "safety": _safety(action_loop_status="locked"),
            "ui": _ui("failure_recovery_preview", "warning", "failure recovery preview only"),
        }

    def rollback_approval_preview(self, request: AssistantRollbackApprovalPreviewRequest) -> dict:
        preview = _rollback_single_file_preview(
            path=request.path,
            restored_content=request.restored_content,
            project_root=request.project_root,
            allowed_roots=self.settings.agent_allowed_roots,
            current_sha256=request.current_sha256,
            original_sha256=request.original_sha256,
            params=request.params,
            reason=request.reason,
        )
        binding = {
            "resolved_path": preview["resolved_path"],
            "audit_payload_hash": preview["audit"]["payload_hash"],
            "reason": _mask_secret_like_values(request.reason or ""),
            "status": preview["status"],
            "approval_scope": "single-file-rollback-preview-only",
            "payload_hash": preview["audit"]["payload_hash"],
            "expires_in_seconds": 300,
            "store": "not-created",
            "manual_review_required": True,
            "server_issued": False,
            "single_use": True,
            "session_context": _approval_session_context(request.session_id),
        }
        if preview["allowed"]:
            approval = self.approval_store.issue(
                tool_name="rollback",
                payload_hash=preview["audit"]["payload_hash"],
                session_id=request.session_id,
                scope="single-file-rollback-preview-only",
            )
            binding = {**binding, **approval, "expires_in_seconds": approval["ttl_seconds"]}
        return {
            "service": self.settings.service_name,
            "mode": "rollback-approval-binding-preview",
            "status": "approval_required" if preview["allowed"] else "blocked",
            "approval_required": True,
            "rollback_enabled": False,
            "would_apply": False,
            "binding": binding,
            "preview": preview,
            "blocked_reasons": preview["blocked_reasons"],
            "safety": _safety(action_loop_status="locked") | {
                "rollback_executor": "enabled-single-file" if self.settings.rollback_executor_enabled else "disabled"
            },
            "ui": _ui("rollback_approval_preview", "warning", "rollback approval preview only"),
        }

    def rollback_execute(self, request: AssistantRollbackExecuteRequest) -> dict:
        preview = _rollback_single_file_preview(
            path=request.path,
            restored_content=request.restored_content,
            project_root=request.project_root,
            allowed_roots=self.settings.agent_allowed_roots,
            current_sha256=request.current_sha256,
            original_sha256=request.original_sha256,
            params={},
            reason=request.reason,
        )
        rollback_result = None
        approval_check = None
        status = "blocked"
        reason = preview["reason"]
        if preview["allowed"]:
            approval_check = self.approval_store.consume(
                approval_id=request.approval_id,
                payload_hash=request.approval_payload_hash,
                session_id=request.session_id,
                tool_name="rollback",
            )
            if not approval_check["valid"]:
                status = "blocked"
                reason = approval_check["reason"]
            elif not self.settings.rollback_executor_enabled:
                status = "disabled"
                reason = "server approval은 검증/소비됐지만 ROLLBACK_EXECUTOR_ENABLED=false 상태라 rollback write는 차단됩니다."
            else:
                resolved_path = Path(preview["resolved_path"])
                current_raw = resolved_path.read_bytes()
                current_sha = hashlib.sha256(current_raw).hexdigest()
                if current_sha != request.current_sha256:
                    status = "blocked"
                    reason = "rollback 직전 디스크 current_sha256이 요청 hash와 달라 파일 write를 수행하지 않았습니다."
                else:
                    restored_bytes = request.restored_content.encode("utf-8")
                    resolved_path.write_text(request.restored_content, encoding="utf-8")
                    restored_sha = hashlib.sha256(restored_bytes).hexdigest()
                    status = "applied"
                    reason = "승인된 단일 UTF-8 텍스트 파일 rollback restore를 완료했습니다."
                    rollback_result = {
                        "resolved_path": preview["resolved_path"],
                        "bytes_written": len(restored_bytes),
                        "previous_sha256": current_sha,
                        "restored_sha256": restored_sha,
                        "paste_safe_summary": (
                            f"rollback_execute status=applied bytes_written={len(restored_bytes)} "
                            f"previous_sha256={current_sha} restored_sha256={restored_sha}"
                        ),
                    }
        result_wrapper = _rollback_result_wrapper(
            {
                "status": status,
                "rollback_result": rollback_result,
                "blocked_reasons": preview["blocked_reasons"],
                "approval_status": approval_check.get("status") if approval_check else None,
            }
        )
        audit_payload = {
            "resolved_path": preview["resolved_path"],
            "preview_payload_hash": preview["audit"]["payload_hash"],
            "provided_current_sha256": request.current_sha256,
            "provided_original_sha256": request.original_sha256,
            "status": status,
            "would_apply": status == "applied",
            "execution_enabled": self.settings.rollback_executor_enabled,
            "approval_status": approval_check.get("status") if approval_check else None,
            "rollback_result_hash": _stable_hash(rollback_result or {}),
        }
        return {
            "service": self.settings.service_name,
            "mode": "rollback-executor-v1" if self.settings.rollback_executor_enabled else "rollback-executor-locked",
            "status": status,
            "rollback_enabled": self.settings.rollback_executor_enabled,
            "execution_enabled": self.settings.rollback_executor_enabled,
            "would_apply": status == "applied",
            "reason": _mask_secret_like_values(reason),
            "preview": preview,
            "blocked_reasons": preview["blocked_reasons"],
            "required_approval_hash": preview["audit"]["payload_hash"] if preview["allowed"] else None,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": approval_check,
            "rollback_result": rollback_result,
            "result_wrapper": result_wrapper,
            "audit": {
                "schema": "assistant.rollback_execute.v1",
                "payload": _mask_secret_like_structure(audit_payload),
                "payload_hash": _stable_hash(audit_payload),
                "note": "35차 rollback executor는 env opt-in 단일 파일 restore이며 git/shell/browser/task/app-os rollback과 연결하지 않습니다.",
            },
            "safety": _safety(action_loop_status="locked") | {
                "rollback_executor": "enabled-single-file" if self.settings.rollback_executor_enabled else "disabled"
            },
            "ui": _ui("rollback_execute", "info" if status == "applied" else "warning", status),
        }

    def create_session(self, db: Session, title: str | None = None, project_root: str | None = None) -> AssistantSession:
        session = AssistantSession(
            id=uuid4().hex,
            title=title or "New local assistant session",
            project_root=project_root,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session, limit: int = 20, offset: int = 0) -> dict:
        message_counts = (
            select(
                AssistantMessage.session_id,
                func.count(AssistantMessage.id).label("messages_count"),
                func.max(AssistantMessage.id).label("last_message_id"),
            )
            .group_by(AssistantMessage.session_id)
            .subquery()
        )
        last_messages = (
            select(AssistantMessage.id, AssistantMessage.content)
        ).subquery()
        stmt = (
            select(
                AssistantSession,
                func.coalesce(message_counts.c.messages_count, 0),
                last_messages.c.content,
            )
            .outerjoin(message_counts, message_counts.c.session_id == AssistantSession.id)
            .outerjoin(last_messages, last_messages.c.id == message_counts.c.last_message_id)
            .order_by(desc(AssistantSession.updated_at))
            .limit(limit)
            .offset(offset)
        )
        sessions = []
        for session, messages_count, last_message in db.execute(stmt).all():
            sessions.append(
                {
                    "session_id": session.id,
                    "title": session.title,
                    "project_root": session.project_root,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "messages_count": messages_count,
                    "last_message_preview": _preview(last_message) if last_message else None,
                }
            )
        return {"sessions": sessions, "limit": limit, "offset": offset}

    def get_session(self, db: Session, session_id: str) -> AssistantSession | None:
        stmt = (
            select(AssistantSession)
            .where(AssistantSession.id == session_id)
            .options(selectinload(AssistantSession.messages))
        )
        return db.scalars(stmt).first()

    def list_session_messages(self, db: Session, session_id: str, limit: int = 50, offset: int = 0) -> dict | None:
        session_exists = db.scalar(select(func.count(AssistantSession.id)).where(AssistantSession.id == session_id)) or 0
        if session_exists == 0:
            return None
        total = db.scalar(select(func.count(AssistantMessage.id)).where(AssistantMessage.session_id == session_id)) or 0
        stmt = (
            select(AssistantMessage)
            .where(AssistantMessage.session_id == session_id)
            .order_by(AssistantMessage.created_at, AssistantMessage.id)
            .limit(limit)
            .offset(offset)
        )
        return {
            "session_id": session_id,
            "total_messages": total,
            "limit": limit,
            "offset": offset,
            "messages": [_message_to_item(message) for message in db.scalars(stmt).all()],
        }

    async def handle_message(self, db: Session, request: AssistantMessageRequest) -> dict:
        session = self._get_or_create_session(db, request)
        intent = request.mode if request.mode != "auto" else self._detect_intent(request.message)
        self._record_message(db, session, "user", request.message, "input", None)

        if intent == "ask":
            chat_log = await self.rag_service.ask(db, request.message, system_prompt=None, temperature=request.temperature)
            response = {
                "session_id": session.id,
                "type": "answer",
                "answer": chat_log.answer,
                "used_documents": False,
                "sources": [],
                "request_id": str(chat_log.id),
                "safety": _safety(),
                "ui": _ui("answer", "info", chat_log.answer),
            }
        elif intent == "ask_with_docs":
            chat_log = await self.rag_service.ask_with_docs(
                db,
                request.message,
                top_k=request.top_k,
                temperature=request.temperature,
            )
            sources = json.loads(chat_log.used_sources_json or "[]")
            response = {
                "session_id": session.id,
                "type": "answer",
                "answer": chat_log.answer,
                "used_documents": True,
                "sources": sources,
                "request_id": str(chat_log.id),
                "safety": _safety(),
                "ui": _ui("answer", "info", chat_log.answer),
            }
        elif intent == "search":
            results = await self.search_service.search(_clean_search_query(request.message), top_k=request.top_k)
            response = {
                "session_id": session.id,
                "type": "search_results",
                "answer": f"{len(results)}개 검색 결과를 찾았습니다.",
                "data": {"query": _clean_search_query(request.message), "results": results},
                "used_documents": True,
                "sources": _sources_from_results(results),
                "safety": _safety(),
                "ui": _ui("search_results", "info", f"{len(results)}개 검색 결과"),
            }
        elif intent == "index_preview":
            folder_path = request.project_root or session.project_root or _extract_path(request.message)
            if not folder_path:
                response = {
                    "session_id": session.id,
                    "type": "needs_project_root",
                    "answer": "폴더 색인 미리보기를 하려면 project_root가 필요합니다.",
                    "data": {"required_field": "project_root"},
                    "safety": _safety(),
                    "ui": _ui("needs_project_root", "warning", "project root 필요"),
                }
            else:
                preview = self.document_service.preview_index_folder(folder_path, recursive=True)
                response = {
                    "session_id": session.id,
                    "type": "index_preview",
                    "answer": f"색인 미리보기 완료: 파일 {preview['files_count']}개, 예상 chunk {preview['chunks_estimated']}개입니다.",
                    "data": preview,
                    "safety": _safety(),
                    "ui": _ui("index_preview", "info", "색인 미리보기 완료"),
                }
        elif intent == "shell_dry_run":
            command = _extract_shell_command(request.message)
            result = dry_run_shell_command(command)
            response = {
                "session_id": session.id,
                "type": "shell_dry_run",
                "answer": result["reason"],
                "data": result,
                "safety": _safety(shell_status=result["status"]),
                "ui": _ui("shell_dry_run", "warning" if result["status"] == "blocked" else "info", result["status"]),
            }
        elif intent == "agent_plan":
            run = self.agent_service.create_plan(db, request.message)
            response = {
                "session_id": session.id,
                "type": "agent_plan",
                "answer": "실행형 요청은 안전한 agent plan으로만 기록했습니다. 실제 shell/browser/file-write 실행은 하지 않았습니다.",
                "data": self.agent_service.to_response(run),
                "safety": _safety(),
                "ui": _ui("agent_plan", "warning", "실행 대신 계획만 생성"),
            }
        elif intent == "automation_plan":
            plan = self.automation_plan(
                AssistantAutomationPlanRequest(goal=request.message, project_root=request.project_root or session.project_root)
            )
            response = {
                "session_id": session.id,
                "type": "automation_plan",
                "answer": "개인 API 자동화 목표를 안전한 단계별 plan-only 계약으로 정리했습니다.",
                "data": plan,
                "safety": _safety(),
                "ui": _ui("automation_plan", "warning", "자동화 plan-only"),
            }
        else:
            status = get_project_status()
            response = {
                "session_id": session.id,
                "type": "status",
                "answer": f"현재 차수는 {status['current_phase']['phase']}차입니다.",
                "data": status,
                "safety": _safety(),
                "ui": _ui("status", "info", f"{status['current_phase']['phase']}차"),
            }

        self._record_message(db, session, "assistant", response.get("answer") or "", response["type"], response)
        return response

    def validate_project_root(self, request: ProjectRootValidateRequest) -> dict:
        raw = request.project_root
        try:
            resolved = Path(raw).expanduser().resolve()
        except RuntimeError:
            resolved = Path(raw).expanduser()
        allowed_roots = _allowed_roots(self.settings.agent_allowed_roots)
        inside_allowed = any(_is_relative_to(resolved, root) for root in allowed_roots)
        exists = resolved.exists()
        is_dir = resolved.is_dir()
        safe = exists and is_dir and inside_allowed
        return {
            "project_root": raw,
            "resolved_path": str(resolved),
            "exists": exists,
            "is_dir": is_dir,
            "inside_allowed_roots": inside_allowed,
            "allowed_roots": [str(root) for root in allowed_roots],
            "safe_for_read_only_agent": safe,
            "message": "read-only agent root로 사용할 수 있습니다." if safe else "존재하는 폴더이고 AGENT_ALLOWED_ROOTS 안에 있어야 합니다.",
        }

    def shell_policy(self) -> dict:
        return get_shell_policy()

    def _get_or_create_session(self, db: Session, request: AssistantMessageRequest) -> AssistantSession:
        if request.session_id:
            session = self.get_session(db, request.session_id)
            if session is not None:
                return session
        return self.create_session(db, title=_title_from_message(request.message), project_root=request.project_root)

    def _record_message(
        self,
        db: Session,
        session: AssistantSession,
        role: str,
        content: str,
        message_type: str,
        payload: dict | None,
    ) -> None:
        message = AssistantMessage(
            session_id=session.id,
            role=role,
            content=content,
            message_type=message_type,
            payload_json=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
        )
        db.add(message)
        db.commit()

    def _detect_intent(self, message: str) -> str:
        lowered = message.lower()
        if any(keyword in lowered for keyword in ["상태", "status", "다음", "next", "차수"]):
            return "status"
        if any(keyword in lowered for keyword in ["shell", "터미널", "명령", "command", "실행"]):
            return "shell_dry_run"
        if any(keyword in lowered for keyword in ["자동화", "automation", "개인 api", "personal api", "api 자동"]):
            return "automation_plan"
        if any(keyword in lowered for keyword in ["색인", "index", "폴더", "folder"]):
            return "index_preview"
        if any(keyword in lowered for keyword in ["검색", "search", "찾아줘", "찾아"]):
            return "search"
        if any(keyword in lowered for keyword in ["브라우저", "browser", "웹 열", "클릭", "삭제", "수정", "저장"]):
            return "agent_plan"
        return "ask_with_docs"


def session_to_response(session: AssistantSession) -> dict:
    messages = sorted(session.messages, key=lambda item: item.created_at)
    return {
        "session_id": session.id,
        "title": session.title,
        "project_root": session.project_root,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "message_type": message.message_type,
                "payload": json.loads(message.payload_json) if message.payload_json else None,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


def _message_to_item(message: AssistantMessage) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "message_type": message.message_type,
        "payload": json.loads(message.payload_json) if message.payload_json else None,
        "created_at": message.created_at,
    }


def _safety(
    shell_status: str = "blocked",
    patch_status: str = "locked",
    browser_status: str = "locked",
    action_loop_status: str = "locked",
    external_web_search_status: str = "disabled",
    app_os_status: str = "disabled",
) -> dict:
    return {
        "shell_execution": "enabled-allowlist" if shell_status in {"completed", "failed", "timeout", "enabled-allowlist"} else "disabled",
        "shell_dry_run": shell_status,
        "shell_sandbox_execution": "enabled-allowlist" if shell_status in {"completed", "failed", "timeout", "enabled-allowlist"} else "locked",
        "patch_apply": patch_status,
        "browser_interaction": "blocked",
        "browser_interaction_preview": browser_status,
        "action_loop_dispatch": "disabled",
        "action_loop_preflight": action_loop_status,
        "file_write_delete": "blocked",
        "folder_index": "preview-only via assistant",
        "external_llm_api": "not-used",
        "external_web_search": external_web_search_status,
        "external_api_enabled": "false",
        "app_os_control": app_os_status,
        "os_action_execution": "disabled",
    }


def _preview(content: str, limit: int = 80) -> str:
    compact = " ".join(content.split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


def _ui(response_type: str, severity: str, primary_text: str) -> dict:
    return {
        "response_type": response_type,
        "severity": severity,
        "primary_text": primary_text[:160],
        "display": "message" if response_type == "answer" else "panel",
    }


def _read_only_adapter_response(
    *,
    service: str,
    adapter_type: str,
    status: str,
    execution_enabled: bool,
    would_read: bool,
    would_fetch: bool,
    adapter_executed: bool,
    result: dict | None,
    reason: str | None,
    audit_payload: dict,
    safety: dict,
) -> dict:
    masked_result = _mask_secret_like_structure(result or {})
    wrapper = {
        "schema": "assistant.read_only_adapter.result_wrapper.v1",
        "untrusted": True,
        "adapter_type": adapter_type,
        "status": status,
        "result": masked_result,
        "reason": _mask_secret_like_values(reason or ""),
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
    }
    payload = {
        **_mask_secret_like_structure(audit_payload),
        "status": status,
        "would_read": would_read,
        "would_fetch": would_fetch,
        "adapter_executed": adapter_executed,
        "action_loop_dispatch_connected": False,
        "wrapper_schema": wrapper["schema"],
    }
    return {
        "service": service,
        "mode": "read-only-adapter-execution",
        "adapter_type": adapter_type,
        "status": status,
        "execution_enabled": execution_enabled,
        "would_read": would_read,
        "would_fetch": would_fetch,
        "adapter_executed": adapter_executed,
        "action_loop_dispatch_connected": False,
        "result_wrapper": wrapper,
        "audit": {
            "schema": "assistant.read_only_adapter.execution_audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "25차 read-only adapter execution은 action-loop dispatch와 연결하지 않습니다.",
        },
        "safety": safety,
        "ui": _ui("read_only_adapter_execute", "info" if status == "completed" else "warning", status),
    }


def _read_only_action_loop_dispatch_response(
    *,
    service: str,
    goal: str,
    status: str,
    dispatched: bool,
    execution_enabled: bool,
    fail_closed: bool,
    adapter_results: list[dict],
    boundary: dict,
    gates: dict,
    safety: dict,
    reason: str | None,
) -> dict:
    payload = {
        "goal": goal,
        "status": status,
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "adapter_results_count": len(adapter_results),
        "adapter_result_hashes": [
            result.get("audit", {}).get("payload_hash")
            for result in adapter_results
            if isinstance(result, dict)
        ],
        "boundary_audit_hash": boundary.get("boundary_audit", {}).get("payload_hash"),
        "shell_execution_connected": False,
        "patch_apply_connected": False,
        "browser_interaction_connected": False,
        "reason": _mask_secret_like_values(reason or ""),
    }
    would_read = any(result.get("would_read") is True for result in adapter_results if isinstance(result, dict))
    would_fetch = any(result.get("would_fetch") is True for result in adapter_results if isinstance(result, dict))
    return {
        "service": service,
        "mode": "action-loop-read-only-dispatch",
        "status": status,
        "goal": goal,
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "fail_closed": fail_closed,
        "would_read": would_read,
        "would_fetch": would_fetch,
        "shell_execution_connected": False,
        "patch_apply_connected": False,
        "browser_interaction_connected": False,
        "adapter_results": _mask_secret_like_structure(adapter_results),
        "boundary_preview": boundary,
        "gates": gates,
        "audit": {
            "schema": "assistant.action_loop.read_only_dispatch.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "26차 read-only dispatch는 shell/patch/browser dispatch와 연결하지 않습니다.",
        },
        "safety": safety,
        "ui": _ui("action_loop_read_only_dispatch", "info" if status == "completed" else "warning", status),
    }


def _shell_action_loop_dispatch_response(
    *,
    service: str,
    goal: str,
    status: str,
    dispatched: bool,
    execution_enabled: bool,
    fail_closed: bool,
    route_plan: list[dict],
    shell_results: list[dict],
    gates: dict,
    safety: dict,
    reason: str | None,
    masked_steps: list[dict],
) -> dict:
    wrapped_results = [
        _shell_action_loop_result_wrapper(result)
        for result in shell_results
        if isinstance(result, dict)
    ]
    payload = {
        "goal": _mask_secret_like_values(goal),
        "status": status,
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "fail_closed": fail_closed,
        "route_plan_count": len(route_plan),
        "shell_results_count": len(wrapped_results),
        "shell_result_hashes": [wrapper["audit"]["payload_hash"] for wrapper in wrapped_results],
        "steps": masked_steps,
        "shell_execution_connected": gates.get("shell_execution_connected") is True,
        "patch_apply_connected": False,
        "browser_interaction_connected": False,
        "reason": _mask_secret_like_values(reason or ""),
    }
    return {
        "service": service,
        "mode": "action-loop-shell-dispatch",
        "status": status,
        "goal": _mask_secret_like_values(goal),
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "fail_closed": fail_closed,
        "shell_execution_connected": gates.get("shell_execution_connected") is True,
        "patch_apply_connected": False,
        "browser_interaction_connected": False,
        "route_plan": _mask_secret_like_structure(route_plan),
        "shell_results": wrapped_results,
        "gates": gates,
        "audit": {
            "schema": "assistant.action_loop.shell_dispatch.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "28차 shell action-loop dispatch는 27차 shell allowlist endpoint만 호출하며 patch/browser/external/task/rollback/app-os에는 연결하지 않습니다.",
        },
        "safety": safety,
        "ui": _ui("action_loop_shell_dispatch", "info" if status == "completed" else "warning", status),
    }


def _shell_action_loop_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    payload = {
        "status": safe_result.get("status"),
        "would_execute": safe_result.get("would_execute"),
        "execution_enabled": safe_result.get("execution_enabled"),
        "reason": safe_result.get("reason"),
        "output_status": safe_result.get("output", {}).get("status") if isinstance(safe_result.get("output"), dict) else None,
        "stdout_truncated": safe_result.get("output", {}).get("stdout_truncated") if isinstance(safe_result.get("output"), dict) else None,
        "stderr_truncated": safe_result.get("output", {}).get("stderr_truncated") if isinstance(safe_result.get("output"), dict) else None,
    }
    return {
        "schema": "assistant.action_loop.shell_result_wrapper.v1",
        "untrusted": True,
        "source_adapter": "shell_run",
        "status": safe_result.get("status"),
        "result": safe_result,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.action_loop.shell_result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _patch_action_loop_dispatch_response(
    *,
    service: str,
    goal: str,
    status: str,
    dispatched: bool,
    execution_enabled: bool,
    fail_closed: bool,
    route_plan: list[dict],
    patch_results: list[dict],
    gates: dict,
    safety: dict,
    reason: str | None,
    masked_steps: list[dict],
) -> dict:
    wrapped_results = [
        _patch_action_loop_result_wrapper(result)
        for result in patch_results
        if isinstance(result, dict)
    ]
    payload = {
        "goal": _mask_secret_like_values(goal),
        "status": status,
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "fail_closed": fail_closed,
        "route_plan_count": len(route_plan),
        "patch_results_count": len(wrapped_results),
        "patch_result_hashes": [wrapper["audit"]["payload_hash"] for wrapper in wrapped_results],
        "steps": masked_steps,
        "shell_execution_connected": False,
        "patch_apply_connected": gates.get("patch_apply_connected") is True,
        "browser_interaction_connected": False,
        "reason": _mask_secret_like_values(reason or ""),
    }
    return {
        "service": service,
        "mode": "action-loop-patch-dispatch",
        "status": status,
        "goal": _mask_secret_like_values(goal),
        "dispatched": dispatched,
        "execution_enabled": execution_enabled,
        "fail_closed": fail_closed,
        "shell_execution_connected": False,
        "patch_apply_connected": gates.get("patch_apply_connected") is True,
        "browser_interaction_connected": False,
        "route_plan": _mask_secret_like_structure(route_plan),
        "patch_results": wrapped_results,
        "gates": gates,
        "audit": {
            "schema": "assistant.action_loop.patch_dispatch.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "30차 patch action-loop dispatch는 29차 single-file patch apply endpoint만 호출하며 shell/browser/external/task/rollback/app-os에는 연결하지 않습니다.",
        },
        "safety": safety,
        "ui": _ui("action_loop_patch_dispatch", "info" if status == "completed" else "warning", status),
    }


def _patch_action_loop_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    payload = {
        "status": safe_result.get("status"),
        "would_apply": safe_result.get("would_apply"),
        "execution_enabled": safe_result.get("execution_enabled"),
        "reason": safe_result.get("reason"),
        "bytes_written": safe_result.get("apply_result", {}).get("bytes_written")
        if isinstance(safe_result.get("apply_result"), dict)
        else None,
        "original_sha256": safe_result.get("apply_result", {}).get("original_sha256")
        if isinstance(safe_result.get("apply_result"), dict)
        else None,
        "new_sha256": safe_result.get("apply_result", {}).get("new_sha256")
        if isinstance(safe_result.get("apply_result"), dict)
        else None,
    }
    return {
        "schema": "assistant.action_loop.patch_result_wrapper.v1",
        "untrusted": True,
        "source_adapter": "patch_apply",
        "status": safe_result.get("status"),
        "result": safe_result,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.action_loop.patch_result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


FULL_AUTOMATION_READ_ONLY_TOOLS = {"read_only_scan", "file_preview", "url_preview", "workspace_brief"}
FULL_AUTOMATION_SHELL_TOOLS = {"shell", "shell_run"}
FULL_AUTOMATION_PATCH_TOOLS = {"patch", "patch_apply"}
FULL_AUTOMATION_ROLLBACK_TOOLS = {"rollback", "rollback_execute"}
FULL_AUTOMATION_TASK_QUEUE_TOOLS = {"task_queue", "task_queue_drain", "task_queue_worker"}
FULL_AUTOMATION_BROWSER_OBSERVE_TOOLS = {"browser_observe", "browser_screenshot", "browser_page_title"}
FULL_AUTOMATION_BROWSER_LIMITED_TOOLS = {"browser_limited_interact", "browser_click", "browser_fill"}
FULL_AUTOMATION_EXTERNAL_SEARCH_TOOLS = {"web_search_provider_search", "external_web_search", "web_search"}
FULL_AUTOMATION_APP_OS_TOOLS = {"app_os", "app_os_control", "os_control", "open_app", "hotkey"}
FULL_AUTOMATION_ALWAYS_BLOCKED_TOOLS = {
    "git_reset",
    "git_clean",
    "git_checkout",
    "bulk_restore",
    "file_delete",
    "file_create",
    "daemon",
    "service",
    "deploy",
    "browser_login",
    "browser_payment",
    "browser_delete",
}


def _full_automation_tool_category(tool: str) -> str:
    normalized = tool.strip().lower().replace("-", "_")
    if normalized in FULL_AUTOMATION_READ_ONLY_TOOLS:
        return "read_only"
    if normalized in FULL_AUTOMATION_SHELL_TOOLS:
        return "shell"
    if normalized in FULL_AUTOMATION_PATCH_TOOLS:
        return "patch"
    if normalized in FULL_AUTOMATION_ROLLBACK_TOOLS:
        return "rollback"
    if normalized in FULL_AUTOMATION_TASK_QUEUE_TOOLS:
        return "task_queue"
    if normalized in FULL_AUTOMATION_BROWSER_OBSERVE_TOOLS:
        return "browser_observe"
    if normalized in FULL_AUTOMATION_BROWSER_LIMITED_TOOLS:
        return "browser_limited_interaction"
    if normalized in FULL_AUTOMATION_EXTERNAL_SEARCH_TOOLS:
        return "external_web_search"
    if normalized in FULL_AUTOMATION_APP_OS_TOOLS:
        return "app_os"
    if normalized in FULL_AUTOMATION_ALWAYS_BLOCKED_TOOLS:
        return "always_blocked"
    if not normalized:
        return "unknown"
    return "unsupported"


def _app_os_action_from_tool(tool: str) -> str:
    normalized = tool.strip().lower().replace("-", "_")
    if normalized in {"open_app", "app_os_control", "os_control"}:
        return "open"
    if normalized == "hotkey":
        return "hotkey"
    return "observe"


def _full_automation_result_wrapper_schema() -> dict:
    return {
        "schema": "assistant.full_automation.result_wrapper.v1",
        "contract_mode": "preflight-noop-and-read-only-aggregation",
        "wrapper_required": True,
        "wrapper_untrusted_required": True,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "allowed_summary_fields": ["status", "tool", "category", "masked_summary", "audit"],
        "prohibited_fields": [
            "raw_content",
            "approval_id",
            "approval_hash",
            "next_step",
            "shell_command",
            "patch_payload",
            "rollback_payload",
            "browser_action",
            "os_action",
            "external_api",
        ],
    }


def _full_automation_orchestrator_plan(
    goal: str,
    frozen_plan: dict,
    route_plan: list[dict],
    enabled: bool,
    status: str,
) -> dict:
    ordered_routes = [
        {
            "execution_order": index,
            "source_index": route.get("index"),
            "tool": route.get("tool"),
            "category": route.get("category"),
            "route": route.get("route"),
            "route_status": route.get("status"),
            "dispatch_supported": False,
            "would_execute": False,
        }
        for index, route in enumerate(route_plan, start=1)
    ]
    payload = {
        "goal": goal,
        "frozen_plan_hash": frozen_plan.get("plan_hash"),
        "status": status,
        "enabled": enabled,
        "ordered_routes": ordered_routes,
        "steps_count": len(ordered_routes),
        "no_op": status != "full_automation_completed",
        "approval_consume_mode": "validate-only",
    }
    return {
        "schema": "assistant.full_automation.orchestrator_plan.v1",
        "status": "ready" if enabled and status == "noop_ready" else status,
        "no_op": status != "full_automation_completed",
        "ordered_routes": ordered_routes,
        "steps_count": len(ordered_routes),
        "plan_hash": _stable_hash(payload),
        "can_be_mutated_by_tool_result": False,
        "actual_connector_execution": status == "full_automation_completed",
    }


def _full_automation_dependency_graph(route_plan: list[dict]) -> dict:
    nodes = [
        {
            "id": f"step-{route.get('index')}",
            "execution_order": index,
            "tool": route.get("tool"),
            "category": route.get("category"),
            "status": route.get("status"),
        }
        for index, route in enumerate(route_plan, start=1)
    ]
    edges = [
        {
            "from": f"step-{route_plan[index - 1].get('index')}",
            "to": f"step-{route_plan[index].get('index')}",
            "type": "sequential_noop_order",
        }
        for index in range(1, len(route_plan))
    ]
    payload = {"nodes": nodes, "edges": edges, "can_execute_parallel": False, "no_op": True}
    return {
        "schema": "assistant.full_automation.dependency_graph.v1",
        "nodes": nodes,
        "edges": edges,
        "can_execute_parallel": False,
        "graph_hash": _stable_hash(payload),
    }


def _full_automation_step_wrapper(
    route: dict,
    execution_order: int,
    read_only_adapter_result: dict | None = None,
    shell_result: dict | None = None,
    patch_result: dict | None = None,
    rollback_result: dict | None = None,
    task_queue_result: dict | None = None,
    browser_observe_result: dict | None = None,
    browser_limited_result: dict | None = None,
    external_web_search_result: dict | None = None,
    app_os_preview_result: dict | None = None,
) -> dict:
    if read_only_adapter_result is not None:
        status = (
            "full_automation_completed"
            if read_only_adapter_result.get("status") == "completed"
            else "blocked"
        )
    elif shell_result is not None:
        status = (
            "full_automation_completed"
            if shell_result.get("status") in {"completed", "timeout"}
            else "blocked"
        )
    elif patch_result is not None:
        status = (
            "full_automation_completed"
            if patch_result.get("status") == "applied"
            else "blocked"
        )
    elif rollback_result is not None:
        status = (
            "full_automation_completed"
            if rollback_result.get("status") == "applied"
            else "blocked"
        )
    elif task_queue_result is not None:
        status = (
            "full_automation_completed"
            if task_queue_result.get("status") == "completed"
            else "blocked"
        )
    elif browser_observe_result is not None:
        status = (
            "full_automation_completed"
            if browser_observe_result.get("status") == "completed"
            else "blocked"
        )
    elif browser_limited_result is not None:
        status = (
            "full_automation_completed"
            if browser_limited_result.get("status") == "validated"
            else "blocked"
        )
    elif external_web_search_result is not None:
        status = (
            "full_automation_completed"
            if external_web_search_result.get("status") == "completed"
            else "blocked"
        )
    elif app_os_preview_result is not None:
        status = (
            "full_automation_completed"
            if app_os_preview_result.get("status") == "observe_plan_candidate"
            and app_os_preview_result.get("os_action_executed") is False
            else "blocked"
        )
    else:
        status = "noop_ready" if route.get("status") == "routable_preflight" else "blocked"
    executed = (
        read_only_adapter_result is not None
        or shell_result is not None
        or patch_result is not None
        or rollback_result is not None
        or task_queue_result is not None
        or browser_observe_result is not None
        or browser_limited_result is not None
        or external_web_search_result is not None
        or app_os_preview_result is not None
    )
    payload = {
        "execution_order": execution_order,
        "source_index": route.get("index"),
        "tool": route.get("tool"),
        "category": route.get("category"),
        "route_status": route.get("status"),
        "status": status,
        "blocked_reasons": route.get("blocked_reasons") or [],
        "no_op": not executed,
        "read_only_adapter_executed": (
            read_only_adapter_result.get("adapter_executed") is True
            if read_only_adapter_result is not None
            else False
        ),
        "shell_executed": (
            shell_result.get("would_execute") is True
            if shell_result is not None
            else False
        ),
        "patch_applied": (
            patch_result.get("would_apply") is True
            if patch_result is not None
            else False
        ),
        "rollback_applied": (
            rollback_result.get("would_apply") is True
            if rollback_result is not None
            else False
        ),
        "task_queue_completed": (
            task_queue_result.get("status") == "completed"
            if task_queue_result is not None
            else False
        ),
        "browser_observed": (
            browser_observe_result.get("would_observe") is True
            if browser_observe_result is not None
            else False
        ),
        "browser_limited_candidate_validated": (
            browser_limited_result.get("status") == "validated"
            if browser_limited_result is not None
            else False
        ),
        "external_web_search_completed": (
            external_web_search_result.get("status") == "completed"
            if external_web_search_result is not None
            else False
        ),
        "app_os_preview_candidate": (
            app_os_preview_result.get("status") == "observe_plan_candidate"
            if app_os_preview_result is not None
            else False
        ),
        "app_os_actual_action_executed": (
            app_os_preview_result.get("os_action_executed") is True
            if app_os_preview_result is not None
            else False
        ),
    }
    masked_adapter_result = (
        _mask_secret_like_structure(read_only_adapter_result)
        if read_only_adapter_result is not None
        else None
    )
    masked_shell_result = (
        _mask_secret_like_structure(shell_result)
        if shell_result is not None
        else None
    )
    masked_patch_result = (
        _mask_secret_like_structure(patch_result)
        if patch_result is not None
        else None
    )
    masked_rollback_result = (
        _mask_secret_like_structure(rollback_result)
        if rollback_result is not None
        else None
    )
    masked_task_queue_result = (
        _mask_secret_like_structure(task_queue_result)
        if task_queue_result is not None
        else None
    )
    masked_browser_observe_result = (
        _mask_secret_like_structure(browser_observe_result)
        if browser_observe_result is not None
        else None
    )
    masked_browser_limited_result = (
        _mask_secret_like_structure(browser_limited_result)
        if browser_limited_result is not None
        else None
    )
    masked_external_web_search_result = (
        _mask_secret_like_structure(external_web_search_result)
        if external_web_search_result is not None
        else None
    )
    masked_app_os_preview_result = (
        _mask_secret_like_structure(app_os_preview_result)
        if app_os_preview_result is not None
        else None
    )
    shell_approval_consumed = (
        (shell_result.get("approval_check") or {}).get("used") is True
        if shell_result is not None
        else False
    )
    patch_approval_consumed = (
        (patch_result.get("approval_check") or {}).get("used") is True
        if patch_result is not None
        else False
    )
    rollback_approval_consumed = (
        (rollback_result.get("approval_check") or {}).get("used") is True
        if rollback_result is not None
        else False
    )
    browser_observe_approval_consumed = (
        (browser_observe_result.get("approval_check") or {}).get("used") is True
        if browser_observe_result is not None
        else False
    )
    browser_limited_approval_consumed = (
        (browser_limited_result.get("approval_check") or {}).get("used") is True
        if browser_limited_result is not None
        else False
    )
    return {
        "schema": "assistant.full_automation.step_result_wrapper.v1",
        "execution_order": execution_order,
        "source_index": route.get("index"),
        "tool": route.get("tool"),
        "category": route.get("category"),
        "status": status,
        "masked_summary": {
            "route": route.get("route"),
            "route_status": route.get("status"),
            "blocked_reasons": route.get("blocked_reasons") or [],
            "would_execute": executed,
            "read_only_adapter_executed": (
                read_only_adapter_result.get("adapter_executed") is True
                if read_only_adapter_result is not None
                else False
            ),
            "shell_executed": (
                shell_result.get("would_execute") is True
                if shell_result is not None
                else False
            ),
            "patch_applied": (
                patch_result.get("would_apply") is True
                if patch_result is not None
                else False
            ),
            "rollback_applied": (
                rollback_result.get("would_apply") is True
                if rollback_result is not None
                else False
            ),
            "task_queue_completed": (
                task_queue_result.get("status") == "completed"
                if task_queue_result is not None
                else False
            ),
            "browser_observed": (
                browser_observe_result.get("would_observe") is True
                if browser_observe_result is not None
                else False
            ),
            "browser_limited_candidate_validated": (
                browser_limited_result.get("status") == "validated"
                if browser_limited_result is not None
                else False
            ),
            "external_web_search_completed": (
                external_web_search_result.get("status") == "completed"
                if external_web_search_result is not None
                else False
            ),
            "app_os_preview_candidate": (
                app_os_preview_result.get("status") == "observe_plan_candidate"
                if app_os_preview_result is not None
                else False
            ),
            "app_os_actual_action_executed": (
                app_os_preview_result.get("os_action_executed") is True
                if app_os_preview_result is not None
                else False
            ),
            "approval_consumed": (
                shell_approval_consumed
                or patch_approval_consumed
                or rollback_approval_consumed
                or browser_observe_approval_consumed
                or browser_limited_approval_consumed
            ),
        },
        "read_only_adapter_result": masked_adapter_result,
        "shell_result": masked_shell_result,
        "patch_result": masked_patch_result,
        "rollback_result": masked_rollback_result,
        "task_queue_result": masked_task_queue_result,
        "browser_observe_result": masked_browser_observe_result,
        "browser_limited_result": masked_browser_limited_result,
        "external_web_search_result": masked_external_web_search_result,
        "app_os_preview_result": masked_app_os_preview_result,
        "untrusted": True,
        "raw_content_included": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.full_automation.step_result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _full_automation_failure_strategy(status: str, blocked_reasons: list[str]) -> dict:
    return {
        "schema": "assistant.full_automation.failure_strategy.v1",
        "status": status,
        "blocked_reasons": blocked_reasons,
        "stop_on_first_blocked": True,
        "auto_retry": False,
        "auto_continue_after_blocked_step": False,
        "paste_safe_summary_required": True,
        "raw_error_content_allowed": False,
    }


def _full_automation_rollback_strategy() -> dict:
    return {
        "schema": "assistant.full_automation.rollback_strategy.v1",
        "mode": "preview_only",
        "auto_rollback": False,
        "rollback_connector_connected": False,
        "git_reset_allowed": False,
        "bulk_restore_allowed": False,
        "file_delete_allowed": False,
        "requires_new_stage_before_execution": True,
    }


def _full_automation_tool_matrix(settings: Settings) -> dict:
    return {
        "read_only_adapter_execution": {
            "status": "available_if_enabled" if settings.read_only_adapter_execution_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.read_only_adapter_execution_enabled,
            "requires_wrapper": True,
            "approval_consume_mode": "none",
        },
        "shell": {
            "status": "available_if_enabled" if settings.shell_execution_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.shell_execution_enabled,
            "requires_approval": True,
            "approval_consume_mode": "validate-only",
            "allowlist_only": True,
        },
        "patch": {
            "status": "available_if_enabled" if settings.patch_apply_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.patch_apply_enabled,
            "requires_approval": True,
            "single_file_only": True,
        },
        "rollback": {
            "status": "available_if_enabled" if settings.rollback_executor_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.rollback_executor_enabled,
            "requires_approval": True,
            "single_file_only": True,
        },
        "task_queue_worker": {
            "status": "one_shot_available_if_enabled" if settings.task_queue_worker_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.task_queue_worker_enabled,
            "daemon_or_service_allowed": False,
        },
        "browser_observe": {
            "status": "available_if_enabled" if settings.browser_observe_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.browser_observe_enabled,
            "actual_interaction_allowed": False,
        },
        "browser_limited_interaction": {
            "status": "candidate_validation_if_enabled"
            if settings.browser_limited_interaction_enabled
            else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.browser_limited_interaction_enabled,
            "browser_launch_allowed": False,
        },
        "external_web_search": {
            "status": "provider_available_if_enabled" if settings.external_web_search_enabled else "disabled",
            "full_automation_connected": settings.full_automation_dispatch_enabled
            and settings.external_web_search_enabled,
            "provider": settings.external_web_search_provider or "not-configured",
        },
        "app_os": {
            "status": "preview_only",
            "full_automation_connected": settings.full_automation_dispatch_enabled,
            "preview_only": True,
            "os_action_execution_allowed": False,
        },
    }


def _full_automation_preview_summary(category: str, preview: dict | None) -> dict:
    if preview is None:
        return {"category": category, "status": "blocked", "summary": "full automation connector not connected"}
    if category == "read_only":
        return {
            "category": category,
            "status": preview.get("status"),
            "route": preview.get("route"),
            "target": preview.get("target"),
            "would_dispatch": False,
            "execution_enabled": False,
        }
    if category in {"shell", "patch"}:
        return {
            "category": category,
            "status": preview.get("status"),
            "preview_summary": preview.get("preview_summary"),
            "would_dispatch": False,
            "execution_enabled": False,
        }
    if category == "rollback":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "resolved_path": preview.get("resolved_path"),
            "would_apply": False,
            "execution_enabled": False,
        }
    if category == "task_queue":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "task_type": preview.get("task_type"),
            "would_execute": False,
            "execution_enabled": False,
            "worker_loop_enabled": False,
        }
    if category == "browser_observe":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "action": preview.get("action"),
            "target_url": preview.get("target_url"),
            "would_observe": False,
            "execution_enabled": False,
            "browser_actual_interaction": False,
        }
    if category == "browser_limited_interaction":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "action": preview.get("action"),
            "target_url": preview.get("target_url"),
            "selector": preview.get("selector"),
            "would_interact": False,
            "execution_enabled": False,
            "browser_launch": "not_performed",
            "browser_actual_interaction": False,
        }
    if category == "external_web_search":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "provider": preview.get("provider"),
            "query_preview": preview.get("query_preview"),
            "would_search": False,
            "execution_enabled": False,
            "external_api_call": False,
        }
    if category == "app_os":
        return {
            "category": category,
            "status": preview.get("status"),
            "allowed": preview.get("allowed"),
            "action": preview.get("action"),
            "app_name": preview.get("app_name"),
            "observe_plan_candidate": preview.get("observe_plan_candidate"),
            "would_control_app": False,
            "os_action_executed": False,
            "execution_enabled": False,
            "preview_only": True,
        }
    return {"category": category, "status": preview.get("status"), "execution_enabled": False}


def _read_only_adapter_request_from_step(
    step: dict,
    project_root: str | None,
) -> AssistantReadOnlyAdapterExecuteRequest | None:
    tool = str(step.get("tool") or "").strip().lower()
    params = step.get("params") if isinstance(step.get("params"), dict) else {}
    wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
    if tool == "read_only_scan":
        root = str(params.get("project_root") or project_root or "")
        if not root:
            return None
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="read_only_scan",
            project_root=root,
            max_items=int(params.get("max_items") or 120),
            result_wrapper=wrapper,
        )
    if tool == "file_preview":
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="file_preview",
            project_root=params.get("project_root") or project_root,
            path=str(params.get("path") or ""),
            max_bytes=int(params.get("max_bytes") or 8000),
            result_wrapper=wrapper,
        )
    if tool == "url_preview":
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="url_fetch",
            url=str(params.get("url") or ""),
            max_bytes=int(params.get("max_bytes") or 8000),
            result_wrapper=wrapper,
        )
    if tool == "workspace_brief":
        root = str(params.get("project_root") or project_root or "")
        if not root:
            return None
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="read_only_scan",
            project_root=root,
            max_items=80,
            result_wrapper=wrapper,
        )
    return None


def _execute_read_only_url_fetch(url: str, max_bytes: int, web_fetch_enabled: bool) -> dict:
    normalized_url = url.strip()
    if not re.match(r"^https?://", normalized_url):
        return {"status": "blocked", "url": normalized_url, "reason": "http/https URL만 fetch할 수 있습니다."}
    if not web_fetch_enabled:
        return {
            "status": "blocked",
            "url": normalized_url,
            "reason": "AGENT_WEB_FETCH_ENABLED=false 상태라 URL fetch를 차단했습니다.",
        }
    block_reason = _read_only_url_block_reason(normalized_url)
    if block_reason:
        return {"status": "blocked", "url": normalized_url, "reason": block_reason}
    try:
        with httpx.stream("GET", normalized_url, timeout=10.0, follow_redirects=False) as response:
            final_url = str(response.url)
            final_block_reason = _read_only_url_block_reason(final_url)
            if final_block_reason:
                return {"status": "blocked", "url": normalized_url, "reason": final_block_reason}
            if 300 <= response.status_code < 400:
                redirect_target = response.headers.get("location")
                if redirect_target:
                    redirect_url = urljoin(final_url, redirect_target)
                    redirect_block_reason = _read_only_url_block_reason(redirect_url)
                    if redirect_block_reason:
                        return {
                            "status": "blocked",
                            "url": normalized_url,
                            "reason": f"redirect target blocked: {redirect_block_reason}",
                        }
                return {
                    "status": "blocked",
                    "url": normalized_url,
                    "reason": "redirect 응답은 자동으로 따라가지 않습니다.",
                }
            chunks: list[bytes] = []
            bytes_read = 0
            truncated = False
            for chunk in response.iter_bytes():
                bytes_read += len(chunk)
                if bytes_read > max_bytes:
                    remaining = max_bytes - sum(len(item) for item in chunks)
                    if remaining > 0:
                        chunks.append(chunk[:remaining])
                    truncated = True
                    break
                chunks.append(chunk)
            body = b"".join(chunks)
            content_type = response.headers.get("content-type", "")
            text_preview = ""
            if "text" in content_type or "json" in content_type or "html" in content_type:
                text_preview = _mask_secret_like_values(body.decode(response.encoding or "utf-8", errors="replace"))
            return {
                "status": "completed",
                "url": normalized_url,
                "final_url": final_url,
                "status_code": response.status_code,
                "content_type": content_type,
                "bytes_returned": len(body),
                "truncated": truncated,
                "content_preview": text_preview,
            }
    except httpx.HTTPError as exc:
        return {"status": "blocked", "url": normalized_url, "reason": f"URL fetch 실패: {exc}"}


def _read_only_url_block_reason(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "http/https URL만 fetch할 수 있습니다."
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return "URL hostname을 확인할 수 없어 fetch를 차단했습니다."
    if _is_private_lan_or_metadata_host(host):
        return "private/LAN/metadata host는 read-only URL fetch에서 차단됩니다."
    try:
        addresses = _resolve_host_ips(host)
    except OSError as exc:
        return f"URL hostname을 해석할 수 없어 fetch를 차단했습니다: {exc}"
    for address in addresses:
        if _is_private_lan_or_metadata_host(address):
            return "private/LAN/metadata IP로 해석되는 URL은 read-only URL fetch에서 차단됩니다."
    return None


def _resolve_host_ips(hostname: str) -> set[str]:
    try:
        return {str(ipaddress.ip_address(hostname))}
    except ValueError:
        pass
    return {item[4][0] for item in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)}


def _title_from_message(message: str) -> str:
    normalized = " ".join(message.split())
    return normalized[:60] or "New local assistant session"


def _clean_search_query(message: str) -> str:
    query = re.sub(r"^(검색|search)\s*[:：]?", "", message.strip(), flags=re.IGNORECASE)
    return query.strip() or message


def _sources_from_results(results: list[dict]) -> list[dict]:
    return [
        {
            "document_id": result["document_id"],
            "filename": result["filename"],
            "chunk_index": result["chunk_index"],
            "chunk_id": result["chunk_id"],
        }
        for result in results
    ]


def _extract_shell_command(message: str) -> str:
    match = re.search(r"`([^`]+)`", message)
    if match:
        return match.group(1)
    prefixes = ["shell", "터미널", "명령", "command", "실행"]
    lowered = message.lower()
    for prefix in prefixes:
        index = lowered.find(prefix)
        if index >= 0:
            return message[index + len(prefix) :].strip(" :：") or message
    return message


def _extract_path(text: str) -> str | None:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", text)
    if quoted:
        return quoted.group(1)
    path_like = re.search(r"((?:~|\.)?/[\w가-힣 ._~\-/]+|(?:\.{1,2}/[\w가-힣 ._~\-/]+))", text)
    return path_like.group(1).strip() if path_like else None


def _resolve_path(value: str | None) -> Path:
    raw = value or "."
    try:
        return Path(raw).expanduser().resolve()
    except RuntimeError:
        return Path(raw).expanduser()


SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".netrc",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".crt", ".cer"}
SENSITIVE_PATH_PARTS = {".ssh", ".gnupg", ".aws", ".config", "secrets", ".secrets"}
SKIPPED_TREE_PARTS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".pytest_cache",
    ".mypy_cache",
}


def _is_sensitive_path(path: Path) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    lowered_parts = [part.lower() for part in path.parts]
    if name in SENSITIVE_FILE_NAMES or suffix in SENSITIVE_SUFFIXES:
        return True
    if any(part in SENSITIVE_PATH_PARTS for part in lowered_parts):
        return True
    return any(keyword in name for keyword in ["secret", "token", "credential", "password", "passwd"])


def _is_skipped_tree_item(path: Path) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    return any(part in SKIPPED_TREE_PARTS for part in lowered_parts)


def _looks_binary(raw: bytes) -> bool:
    if not raw:
        return False
    sample = raw[:2048]
    if b"\x00" in sample:
        return True
    control_bytes = sum(1 for byte in sample if byte < 9 or (13 < byte < 32))
    return control_bytes / len(sample) > 0.10


SECRET_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    re.compile(r"\b[a-fA-F0-9]{32,}\b"),
]

SHELL_ALLOWED_EXACT = {
    ("pwd",),
    ("ls",),
    ("ls", "-la"),
    ("ls", "-al"),
    ("git", "status"),
    ("git", "diff", "--check"),
    (".venv/bin/pytest",),
    (".venv/bin/python", "-m", "pytest"),
    (".venv/bin/python", "-m", "compileall", "app", "cli", "scripts"),
    (".venv/bin/python", "scripts/local_ci_check.py", "--root", "."),
}
SHELL_ALLOWED_PREFIXES: set[tuple[str, ...]] = set()
SHELL_BLOCKED_TOKENS = {
    "sudo",
    "rm",
    "rmdir",
    "mv",
    "cp",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    "scp",
    "rsync",
    "bash",
    "sh",
    "zsh",
    "fish",
    "python",
    "python3",
    "pip",
    "pip3",
    "brew",
    "npm",
    "npx",
    "pnpm",
    "yarn",
}
SHELL_BLOCKED_PHRASES = {
    "rm -rf",
    "git reset",
    "git clean",
    "git push",
    "curl |",
    "curl -fs",
    "wget |",
    "pip install",
    "brew install",
    "npm install",
    "chmod -r",
}
SHELL_CONTROL_TOKENS = {"|", "||", "&&", ";", ">", ">>", "<", "<<", "$(", "`"}
SHELL_OUTPUT_MAX_BYTES = 12_000


def _mask_secret_like_values(value: str) -> str:
    masked = value
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub("[REDACTED]", masked)
    return masked


def _mask_secret_like_structure(value):
    if isinstance(value, str):
        return _mask_secret_like_values(value)
    if isinstance(value, list):
        return [_mask_secret_like_structure(item) for item in value]
    if isinstance(value, dict):
        return {key: _mask_secret_like_structure(item) for key, item in value.items()}
    return value


def _looks_secret_like(value: str) -> bool:
    return _secret_scan(value)["has_secret_like_value"]


def _evaluate_shell_policy(command: str, cwd: str, timeout_seconds: int, allowed_roots: str) -> dict:
    raw_command = command.strip()
    command_preview = _mask_secret_like_values(" ".join(raw_command.split()))
    resolved_cwd = _resolve_path(cwd)
    roots = _allowed_roots(allowed_roots)
    base = {
        "command_preview": command_preview,
        "resolved_cwd": str(resolved_cwd),
        "timeout_seconds": timeout_seconds,
        "allowed_roots": [str(root) for root in roots],
        "allowlist": {
            "exact": [" ".join(item) for item in sorted(SHELL_ALLOWED_EXACT)],
            "prefixes": [" ".join(item) for item in sorted(SHELL_ALLOWED_PREFIXES)],
        },
        "blocked_tokens": sorted(SHELL_BLOCKED_TOKENS),
        "blocked_phrases": sorted(SHELL_BLOCKED_PHRASES),
    }
    if not raw_command:
        return {**base, "status": "blocked", "allowed": False, "reason": "빈 shell command는 차단됩니다."}
    if not resolved_cwd.exists() or not resolved_cwd.is_dir():
        return {**base, "status": "blocked", "allowed": False, "reason": "cwd는 존재하는 디렉터리여야 합니다."}
    if not any(_is_relative_to(resolved_cwd, root) for root in roots):
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "reason": "cwd가 AGENT_ALLOWED_ROOTS 밖이므로 차단됩니다.",
        }
    lowered = raw_command.lower()
    for phrase in SHELL_BLOCKED_PHRASES:
        if phrase in lowered:
            return {
                **base,
                "status": "blocked",
                "allowed": False,
                "reason": f"고위험 shell phrase가 포함되어 차단됩니다: {phrase}",
            }
    if any(token in raw_command for token in SHELL_CONTROL_TOKENS):
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "reason": "pipe, redirect, command substitution, command chaining은 차단됩니다.",
        }
    try:
        parts = shlex.split(raw_command)
    except ValueError:
        return {**base, "status": "blocked", "allowed": False, "reason": "shell command를 안전하게 parsing할 수 없습니다."}
    if not parts:
        return {**base, "status": "blocked", "allowed": False, "reason": "빈 shell command는 차단됩니다."}
    normalized_parts = tuple(part.lower() for part in parts)
    command_name = normalized_parts[0]
    if command_name in SHELL_BLOCKED_TOKENS and not _matches_shell_allowlist(normalized_parts):
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "reason": f"고위험 shell command가 차단됩니다: {command_name}",
        }
    if not _matches_shell_allowlist(normalized_parts):
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "reason": "5차 shell sandbox allowlist에 없는 명령입니다.",
        }
    return {
        **base,
        "status": "allowed_preview",
        "allowed": True,
        "reason": "allowlist 명령이지만 현재 단계에서는 실제 실행하지 않고 preview/audit만 제공합니다.",
    }


def _matches_shell_allowlist(parts: tuple[str, ...]) -> bool:
    if parts in SHELL_ALLOWED_EXACT:
        return True
    return any(parts[: len(prefix)] == prefix for prefix in SHELL_ALLOWED_PREFIXES)


def _shell_audit_payload(policy: dict, output_preview: dict) -> dict:
    payload = {
        "command_preview": policy["command_preview"],
        "resolved_cwd": policy["resolved_cwd"],
        "status": policy["status"],
        "timeout_seconds": policy["timeout_seconds"],
        "would_execute": False,
        "output_preview": output_preview,
    }
    return {
        "schema": "assistant.shell_sandbox.preview.v1",
        "payload": payload,
        "payload_hash": _stable_hash(payload),
        "note": "audit payload는 실행 증거가 아니라 locked preview 계약입니다.",
    }


def _shell_run_has_approval_injection(request: AssistantShellRunRequest) -> bool:
    values = [
        request.command,
        request.cwd,
        request.approval_id or "",
        request.approval_payload_hash or "",
        request.session_id or "",
    ]
    return any(_contains_approval_like_json(value) for value in values) or any(
        re.search(r"\bapproval_(id|payload_hash|hash)\b", value, flags=re.IGNORECASE)
        for value in values
    )


def _execute_shell_allowlist_command(command: str, cwd: str, timeout_seconds: int) -> dict:
    started_at = _utc_now()
    parts = shlex.split(command.strip())
    try:
        completed = subprocess.run(
            parts,
            cwd=cwd,
            shell=False,
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = _mask_and_cap_output(completed.stdout)
        stderr = _mask_and_cap_output(completed.stderr)
        status = "completed" if completed.returncode == 0 else "failed"
        summary = (
            f"shell command {status}: exit_code={completed.returncode}, "
            f"stdout_bytes={stdout['raw_bytes']}, stderr_bytes={stderr['raw_bytes']}"
        )
        return {
            "status": status,
            "exit_code": completed.returncode,
            "timeout": False,
            "timeout_seconds": timeout_seconds,
            "stdout": stdout["text"],
            "stderr": stderr["text"],
            "stdout_bytes": stdout["raw_bytes"],
            "stderr_bytes": stderr["raw_bytes"],
            "stdout_truncated": stdout["truncated"],
            "stderr_truncated": stderr["truncated"],
            "stdout_masked": stdout["masked"],
            "stderr_masked": stderr["masked"],
            "paste_safe_summary": summary,
            "started_at": started_at.isoformat(),
            "completed_at": _utc_now().isoformat(),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = _mask_and_cap_output(exc.stdout or b"")
        stderr = _mask_and_cap_output(exc.stderr or b"")
        return {
            "status": "timeout",
            "exit_code": None,
            "timeout": True,
            "timeout_seconds": timeout_seconds,
            "stdout": stdout["text"],
            "stderr": stderr["text"],
            "stdout_bytes": stdout["raw_bytes"],
            "stderr_bytes": stderr["raw_bytes"],
            "stdout_truncated": stdout["truncated"],
            "stderr_truncated": stderr["truncated"],
            "stdout_masked": stdout["masked"],
            "stderr_masked": stderr["masked"],
            "paste_safe_summary": f"shell command timeout: timeout_seconds={timeout_seconds}",
            "started_at": started_at.isoformat(),
            "completed_at": _utc_now().isoformat(),
        }


def _mask_and_cap_output(raw: bytes | str) -> dict:
    raw_bytes = raw.encode("utf-8", errors="replace") if isinstance(raw, str) else raw
    capped = raw_bytes[:SHELL_OUTPUT_MAX_BYTES]
    text = capped.decode("utf-8", errors="replace")
    masked = _mask_secret_like_values(text)
    return {
        "text": masked,
        "raw_bytes": len(raw_bytes),
        "truncated": len(raw_bytes) > SHELL_OUTPUT_MAX_BYTES,
        "masked": masked != text,
    }


def _shell_run_response(
    *,
    service: str,
    status: str,
    would_execute: bool,
    execution_enabled: bool,
    reason: str,
    preview: dict,
    required_approval_hash: str | None,
    request: AssistantShellRunRequest,
    approval_check: dict | None,
    output: dict | None,
    safety: dict,
) -> dict:
    audit_payload = {
        "command_preview": preview["command_preview"],
        "resolved_cwd": preview["resolved_cwd"],
        "status": status,
        "would_execute": would_execute,
        "execution_enabled": execution_enabled,
        "required_approval_hash": required_approval_hash,
        "provided_approval_id": request.approval_id,
        "provided_approval_hash": request.approval_payload_hash,
        "approval_status": approval_check.get("status") if approval_check else None,
        "output_status": output.get("status") if output else None,
        "stdout_truncated": output.get("stdout_truncated") if output else False,
        "stderr_truncated": output.get("stderr_truncated") if output else False,
    }
    return {
        "service": service,
        "mode": "shell-sandbox-v1" if execution_enabled else "shell-run-locked",
        "status": status,
        "would_execute": would_execute,
        "execution_enabled": execution_enabled,
        "reason": _mask_secret_like_values(reason),
        "preview": preview,
        "output": output,
        "required_approval_hash": required_approval_hash,
        "provided_approval_id": request.approval_id,
        "provided_approval_hash": request.approval_payload_hash,
        "approval_check": approval_check,
        "audit": {
            "schema": "assistant.shell_sandbox.run.v1",
            "payload": _mask_secret_like_structure(audit_payload),
            "payload_hash": _stable_hash(audit_payload),
            "note": "27차 Shell Sandbox v1은 env opt-in, allowlist, cwd, approval binding을 모두 통과한 단건 subprocess만 실행합니다.",
        },
        "safety": safety,
        "ui": _ui("shell_run_locked", "info" if status == "completed" else "warning", status),
    }
def _evaluate_patch_policy(
    path: str,
    proposed_content: str,
    project_root: str | None,
    allowed_roots: str,
) -> dict:
    resolved_path = _resolve_path(path)
    configured_roots = _allowed_roots(allowed_roots)
    requested_root = Path(project_root).expanduser().resolve() if project_root else None
    requested_root_allowed = (
        requested_root is None or any(_is_relative_to(requested_root, root) for root in configured_roots)
    )
    roots = [requested_root] if requested_root_allowed and requested_root is not None else configured_roots
    base = {
        "resolved_path": str(resolved_path),
        "allowed_roots": [str(root) for root in roots],
        "configured_allowed_roots": [str(root) for root in configured_roots],
        "requested_project_root": str(requested_root) if requested_root else None,
        "diff_preview": None,
        "truncated": False,
        "secret_scan": _secret_scan(proposed_content),
        "rollback": {
            "available": False,
            "note": "preview-only 단계에서는 파일을 수정하지 않으므로 rollback artifact를 생성하지 않습니다.",
        },
    }
    if not requested_root_allowed:
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "reason": "project_root가 AGENT_ALLOWED_ROOTS 밖이므로 차단됩니다.",
        }
    if not any(_is_relative_to(resolved_path, root) for root in roots):
        return {**base, "status": "blocked", "allowed": False, "reason": "path가 AGENT_ALLOWED_ROOTS 밖이므로 차단됩니다."}
    if not resolved_path.exists() or not resolved_path.is_file():
        return {**base, "status": "blocked", "allowed": False, "reason": "기존 파일만 patch preview할 수 있습니다."}
    if _is_sensitive_path(resolved_path):
        return {**base, "status": "blocked", "allowed": False, "reason": "민감 파일 또는 credential 후보는 patch preview하지 않습니다."}
    if base["secret_scan"]["has_secret_like_value"]:
        return {**base, "status": "blocked", "allowed": False, "reason": "proposed_content에 secret-like 값이 포함되어 차단됩니다."}
    size_bytes = resolved_path.stat().st_size
    if size_bytes > 50000:
        return {**base, "status": "blocked", "allowed": False, "reason": "대용량 파일은 patch preview하지 않습니다."}
    raw = resolved_path.read_bytes()
    if _looks_binary(raw):
        return {**base, "status": "blocked", "allowed": False, "reason": "binary 파일은 patch preview하지 않습니다."}
    try:
        original = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {**base, "status": "blocked", "allowed": False, "reason": "UTF-8 텍스트 파일만 patch preview할 수 있습니다."}
    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            proposed_content.splitlines(keepends=True),
            fromfile=f"a/{resolved_path.name}",
            tofile=f"b/{resolved_path.name}",
        )
    )
    masked_diff = _mask_secret_like_values(diff)
    truncated = len(masked_diff) > 12000
    diff_preview = masked_diff[:12000]
    rollback = {
        "available": True,
        "note": "실제 apply 전에는 현재 파일 snapshot hash와 manual backup/rollback 계획을 별도로 확인해야 합니다.",
        "original_sha256": hashlib.sha256(raw).hexdigest(),
    }
    return {
        **base,
        "status": "allowed_preview",
        "allowed": True,
        "reason": "허용 root 안의 안전한 텍스트 파일 diff preview입니다. 실제 파일 수정은 수행하지 않습니다.",
        "diff_preview": diff_preview,
        "truncated": truncated,
        "rollback": rollback,
    }


def _secret_scan(value: str) -> dict:
    findings = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            findings.append(pattern.pattern)
    return {
        "has_secret_like_value": bool(findings),
        "findings_count": len(findings),
        "patterns": findings,
        "masked_preview": _mask_secret_like_values(value[:1000]),
    }


def _patch_audit_payload(policy: dict, reason: str | None) -> dict:
    payload = {
        "resolved_path": policy["resolved_path"],
        "status": policy["status"],
        "would_apply": False,
        "diff_preview_hash": _stable_hash({"diff_preview": policy["diff_preview"] or ""}),
        "secret_scan": {
            "has_secret_like_value": policy["secret_scan"]["has_secret_like_value"],
            "findings_count": policy["secret_scan"]["findings_count"],
        },
        "rollback": policy["rollback"],
        "reason": _mask_secret_like_values(reason or ""),
    }
    return {
        "schema": "assistant.patch_preview.v1",
        "payload": payload,
        "payload_hash": _stable_hash(payload),
        "note": "audit payload는 실행 증거가 아니라 locked patch preview 계약입니다.",
    }


def _rollback_single_file_preview(
    *,
    path: str,
    restored_content: str,
    project_root: str | None,
    allowed_roots: str,
    current_sha256: str | None,
    original_sha256: str | None,
    params: dict,
    reason: str | None,
) -> dict:
    resolved_path = _resolve_path(path)
    configured_roots = _allowed_roots(allowed_roots)
    requested_root = Path(project_root).expanduser().resolve() if project_root else None
    requested_root_allowed = (
        requested_root is None or any(_is_relative_to(requested_root, root) for root in configured_roots)
    )
    roots = [requested_root] if requested_root_allowed and requested_root is not None else configured_roots
    restored_bytes = restored_content.encode("utf-8")
    restored_sha = hashlib.sha256(restored_bytes).hexdigest()
    blocked_reasons: list[str] = []
    current_disk_sha = None
    diff_preview = None
    truncated = False
    secret_scan = _secret_scan(restored_content)
    if not requested_root_allowed:
        blocked_reasons.append("project_root_outside_allowed_roots")
    if not any(_is_relative_to(resolved_path, root) for root in roots):
        blocked_reasons.append("path_outside_allowed_roots")
    if _contains_approval_like_json(params):
        blocked_reasons.append("approval_like_json_injection_blocked")
    if _task_params_reference_unsafe_action(params):
        blocked_reasons.append("unsafe_action_reference_blocked")
    if original_sha256 != restored_sha:
        blocked_reasons.append("original_sha256_mismatch")
    if secret_scan["has_secret_like_value"]:
        blocked_reasons.append("secret_like_restored_content_blocked")
    if not resolved_path.exists() or not resolved_path.is_file():
        blocked_reasons.append("existing_file_required")
    elif _is_sensitive_path(resolved_path):
        blocked_reasons.append("sensitive_path_blocked")
    else:
        size_bytes = resolved_path.stat().st_size
        if size_bytes > 50000:
            blocked_reasons.append("file_too_large")
        raw = resolved_path.read_bytes()
        current_disk_sha = hashlib.sha256(raw).hexdigest()
        if current_sha256 != current_disk_sha:
            blocked_reasons.append("current_sha256_mismatch")
        if _looks_binary(raw):
            blocked_reasons.append("binary_file_blocked")
        else:
            try:
                current_text = raw.decode("utf-8")
            except UnicodeDecodeError:
                blocked_reasons.append("non_utf8_file_blocked")
            else:
                diff = "".join(
                    difflib.unified_diff(
                        current_text.splitlines(keepends=True),
                        restored_content.splitlines(keepends=True),
                        fromfile=f"current/{resolved_path.name}",
                        tofile=f"restored/{resolved_path.name}",
                    )
                )
                masked_diff = _mask_secret_like_values(diff)
                truncated = len(masked_diff) > 12000
                diff_preview = masked_diff[:12000]
    status = "allowed_preview" if not blocked_reasons else "blocked"
    payload = {
        "resolved_path": str(resolved_path),
        "status": status,
        "blocked_reasons": blocked_reasons,
        "current_disk_sha256": current_disk_sha,
        "provided_current_sha256": current_sha256,
        "provided_original_sha256": original_sha256,
        "restored_sha256": restored_sha,
        "diff_preview_hash": _stable_hash({"diff_preview": diff_preview or ""}),
        "reason": _mask_secret_like_values(reason or ""),
    }
    return {
        "schema": "assistant.rollback.single_file.preview.v1",
        "resolved_path": str(resolved_path),
        "allowed_roots": [str(root) for root in roots],
        "configured_allowed_roots": [str(root) for root in configured_roots],
        "requested_project_root": str(requested_root) if requested_root else None,
        "status": status,
        "allowed": not blocked_reasons,
        "blocked_reasons": sorted(set(blocked_reasons)),
        "reason": "rollback single-file restore preview is allowed" if not blocked_reasons else "rollback single-file restore preview blocked",
        "diff_preview": diff_preview,
        "truncated": truncated,
        "secret_scan": secret_scan,
        "current_disk_sha256": current_disk_sha,
        "provided_current_sha256": current_sha256,
        "provided_original_sha256": original_sha256,
        "restored_sha256": restored_sha,
        "would_apply": False,
        "rollback_scope": {
            "single_file_only": True,
            "git_reset_allowed": False,
            "bulk_restore_allowed": False,
            "delete_create_allowed": False,
            "shell_browser_app_os_allowed": False,
            "task_worker_connected": False,
            "action_loop_connected": False,
        },
        "audit": {
            "schema": "assistant.rollback.single_file.preview.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "rollback preview는 approval binding용 hash를 만들며 실행은 수행하지 않습니다.",
        },
    }


def _rollback_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    return {
        "schema": "assistant.rollback_execute.result_wrapper.v1",
        "untrusted": True,
        "paste_safe": True,
        "masked": safe_result != result,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "approval_like_json_trusted": False,
        "result_hash": _stable_hash(safe_result),
    }


WORKFLOW_PRESETS = {
    "project_review": {
        "id": "project_review",
        "title": "Project Review",
        "category": "coding",
        "description": "프로젝트 루트 구조와 핵심 문서를 read-only로 검토하는 preset입니다.",
        "params_schema": {"project_root": "string"},
        "step_templates": [
            {"tool": "read_only_scan", "params": {"project_root": "{project_root}", "max_items": 120}},
            {"tool": "file_preview", "params": {"path": "{project_root}/README.md", "project_root": "{project_root}"}},
            {"tool": "file_preview", "params": {"path": "{project_root}/AGENTS.md", "project_root": "{project_root}"}},
        ],
    },
    "docs_check": {
        "id": "docs_check",
        "title": "Docs Check",
        "category": "docs",
        "description": "TASKS/WORKLOG/SECURITY 문서 상태를 preview하는 preset입니다.",
        "params_schema": {"project_root": "string"},
        "step_templates": [
            {"tool": "file_preview", "params": {"path": "{project_root}/docs/TASKS.md", "project_root": "{project_root}"}},
            {"tool": "file_preview", "params": {"path": "{project_root}/docs/WORKLOG.md", "project_root": "{project_root}"}},
            {"tool": "file_preview", "params": {"path": "{project_root}/SECURITY.md", "project_root": "{project_root}"}},
        ],
    },
    "ci_preview": {
        "id": "ci_preview",
        "title": "CI Preview",
        "category": "local-server-maintenance",
        "description": "local CI 명령 후보를 shell locked preview로만 제안하는 preset입니다.",
        "params_schema": {"project_root": "string"},
        "step_templates": [
            {
                "tool": "shell",
                "params": {
                    "command": ".venv/bin/python scripts/local_ci_check.py --root .",
                    "cwd": "{project_root}",
                    "timeout_seconds": 120,
                },
            }
        ],
    },
    "patch_review": {
        "id": "patch_review",
        "title": "Patch Review",
        "category": "coding",
        "description": "patch 후보를 diff preview로만 검토하는 preset입니다.",
        "params_schema": {"path": "string", "proposed_content": "string", "project_root": "string"},
        "step_templates": [
            {
                "tool": "patch",
                "params": {
                    "path": "{path}",
                    "proposed_content": "{proposed_content}",
                    "project_root": "{project_root}",
                },
            }
        ],
    },
    "browser_review_plan": {
        "id": "browser_review_plan",
        "title": "Browser Review Plan",
        "category": "portfolio",
        "description": "브라우저 관찰 계획을 browser locked preview로만 제안하는 preset입니다.",
        "params_schema": {"target_url": "string"},
        "step_templates": [
            {"tool": "browser", "params": {"action": "observe", "target_url": "{target_url}"}}
        ],
    },
}

UNSAFE_WORKFLOW_PRESETS = {
    "unsafe_direct_shell",
    "unsafe_browser_click",
    "unsafe_external_api",
}

ALLOWED_TASK_QUEUE_TYPES = {
    "noop",
    "read_only_scan",
    "file_preview",
    "url_preview",
    "workflow_preset_preview",
}

TASK_QUEUE_WORKER_ALLOWED_TYPES = {
    "noop",
    "read_only_scan",
    "file_preview",
    "url_preview",
}

FULL_AUTOMATION_TASK_QUEUE_ALLOWED_TYPES = {
    "noop",
    "read_only_scan",
    "file_preview",
}

MUTATING_TASK_QUEUE_TYPES = {
    "shell",
    "shell_run",
    "patch",
    "patch_apply",
    "browser",
    "browser_interact",
    "app_os",
    "app_os_interaction",
    "external_api",
    "external_web_search",
    "rollback",
    "rollback_execute",
    "failure_recovery_execute",
    "action_loop",
    "action_loop_dispatch",
}

FAILURE_REASON_TAXONOMY = {
    "patch": ["diff_rejected", "hash_mismatch", "path_blocked", "content_blocked", "apply_failed"],
    "shell": ["command_blocked", "timeout", "nonzero_exit", "cwd_blocked", "policy_denied"],
    "browser": ["navigation_blocked", "selector_missing", "interaction_blocked", "login_required", "unsafe_action"],
}


def _normalize_preset_id(preset_id: str) -> str:
    return str(preset_id or "").strip().lower().replace(" ", "_")


def _workflow_preset_public(preset: dict | None) -> dict:
    if not preset:
        return {}
    return {
        "id": preset["id"],
        "title": preset["title"],
        "category": preset["category"],
        "description": preset["description"],
        "params_schema": preset["params_schema"],
        "steps_count": len(preset["step_templates"]),
        "would_dispatch": False,
        "execution_enabled": False,
    }


def _workflow_param_violations(params: dict) -> list[str]:
    violations: list[str] = []
    if _contains_approval_like_json(params):
        violations.append("approval_like_json_injection_blocked")
    if str(params.get("preset_id") or "").strip().lower() in UNSAFE_WORKFLOW_PRESETS:
        violations.append("unsafe_preset_reference_blocked")
    return violations


def _contains_approval_like_json(value) -> bool:
    if isinstance(value, dict):
        keys = {str(key).lower() for key in value}
        if {"approval_id", "approval_payload_hash"} & keys or {"approval", "approval_hash"} & keys:
            return True
        return any(_contains_approval_like_json(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_approval_like_json(item) for item in value)
    return False


def _workflow_preset_steps(preset: dict, params: dict) -> list[dict]:
    return [
        {
            "tool": template["tool"],
            "params": _workflow_render_params(template.get("params", {}), params),
            "wrapper": {
                "untrusted": True,
                "source": "workflow_preset",
                "preset_id": preset["id"],
            },
            "preview_only": True,
        }
        for template in preset["step_templates"]
    ]


def _workflow_render_params(template_params: dict, params: dict) -> dict:
    rendered = {}
    for key, value in template_params.items():
        if isinstance(value, str):
            rendered[key] = _workflow_render_string(value, params)
        else:
            rendered[key] = value
    return rendered


def _workflow_render_string(value: str, params: dict) -> str:
    rendered = value
    for key, param_value in params.items():
        if isinstance(param_value, (str, int, float, bool)):
            rendered = rendered.replace("{" + str(key) + "}", str(param_value))
    return rendered


def _normalize_task_type(task_type: str) -> str:
    return str(task_type or "").strip().lower().replace("-", "_").replace(" ", "_")


def _task_queue_blocked_reasons(task_type: str, params: dict) -> list[str]:
    reasons: list[str] = []
    if task_type in MUTATING_TASK_QUEUE_TYPES:
        reasons.append("mutating_task_blocked")
    if task_type not in ALLOWED_TASK_QUEUE_TYPES:
        reasons.append("unsupported_task_type")
    if _contains_approval_like_json(params):
        reasons.append("approval_like_json_injection_blocked")
    if _task_params_reference_unsafe_action(params):
        reasons.append("unsafe_action_reference_blocked")
    return reasons


def _task_queue_worker_blocked_reasons(task_type: str, params: dict) -> list[str]:
    reasons = _task_queue_blocked_reasons(task_type, params)
    if task_type not in TASK_QUEUE_WORKER_ALLOWED_TYPES:
        reasons.append("worker_task_type_not_allowed")
    if task_type in {"shell", "shell_run"}:
        reasons.append("shell_worker_not_connected")
    if task_type in {"url_preview", "url_fetch"}:
        reasons.append("network_fetch_worker_not_connected")
    return sorted(set(reasons))


def _full_automation_task_queue_step_preview(
    *,
    index: int,
    tool: str,
    params: dict,
    project_root: str | None,
) -> dict:
    task_type = _normalize_task_type(str(params.get("task_type") or params.get("type") or ""))
    task_params = _full_automation_task_queue_params(params=params, project_root=project_root)
    blocked_reasons = _task_queue_worker_blocked_reasons(task_type, task_params)
    if task_type not in FULL_AUTOMATION_TASK_QUEUE_ALLOWED_TYPES:
        blocked_reasons.append("full_automation_task_queue_type_not_allowed")
    status = "allowed_preview" if not blocked_reasons else "blocked"
    payload = {
        "index": index,
        "tool": tool,
        "task_type": task_type,
        "status": status,
        "blocked_reasons": sorted(set(blocked_reasons)),
        "params_hash": _stable_hash(_mask_secret_like_structure(task_params)),
        "worker_loop_enabled": False,
        "daemon_or_service_allowed": False,
    }
    return {
        "schema": "assistant.full_automation.task_queue.preview.v1",
        "status": status,
        "allowed": not blocked_reasons,
        "task_type": task_type,
        "blocked_reasons": sorted(set(blocked_reasons)),
        "allowed_task_types": sorted(FULL_AUTOMATION_TASK_QUEUE_ALLOWED_TYPES),
        "worker": {
            "one_shot_step": True,
            "background_loop_created": False,
            "daemon_started": False,
            "service_installed": False,
        },
        "audit": {
            "schema": "assistant.full_automation.task_queue.preview.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _full_automation_task_queue_task(
    *,
    index: int,
    tool: str,
    params: dict,
    project_root: str | None,
) -> dict:
    task_type = _normalize_task_type(str(params.get("task_type") or params.get("type") or ""))
    task_params = _full_automation_task_queue_params(params=params, project_root=project_root)
    task_id = str(params.get("task_id") or f"full-automation-step-{index}")
    return {
        "task_id": task_id,
        "task_type": task_type,
        "params": task_params,
        "status": "queued",
        "source": "full_automation_dispatch",
        "tool": tool,
    }


def _full_automation_task_queue_params(*, params: dict, project_root: str | None) -> dict:
    task_params = {
        key: value
        for key, value in params.items()
        if key not in {"task_type", "type", "task_id", "limit"}
    }
    if project_root and "project_root" not in task_params:
        task_params["project_root"] = project_root
    return task_params


def _task_queue_adapter_request(task_type: str, params: dict) -> AssistantReadOnlyAdapterExecuteRequest:
    if task_type == "read_only_scan":
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="read_only_scan",
            project_root=params.get("project_root"),
            max_items=_coerce_int(params.get("max_items"), default=120, minimum=1, maximum=500),
            result_wrapper={"untrusted": True},
        )
    if task_type == "file_preview":
        return AssistantReadOnlyAdapterExecuteRequest(
            adapter_type="file_preview",
            project_root=params.get("project_root"),
            path=params.get("path"),
            max_bytes=_coerce_int(params.get("max_bytes"), default=8000, minimum=1, maximum=50000),
            result_wrapper={"untrusted": True},
        )
    return AssistantReadOnlyAdapterExecuteRequest(
        adapter_type="url_fetch",
        url=params.get("url"),
        max_bytes=_coerce_int(params.get("max_bytes"), default=8000, minimum=1, maximum=50000),
        result_wrapper={"untrusted": True},
    )


def _coerce_int(value, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _task_params_reference_unsafe_action(value) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"command", "patch", "browser_action", "os_action", "external_api", "next_step"}:
                return True
            if _task_params_reference_unsafe_action(item):
                return True
        return False
    if isinstance(value, list):
        return any(_task_params_reference_unsafe_action(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in ["osascript", "open -a ", "rm -rf", "curl http", "browser.click"])
    return False


def _task_cleanup_policy() -> dict:
    return {
        "schema": "assistant.long_running_task.cleanup_policy.v1",
        "storage": "process-local in-memory preview store",
        "ttl_seconds_default": TASK_QUEUE_TTL_SECONDS,
        "cleanup_trigger": "list/detail/cancel-preview calls remove expired preview records",
        "durability": "not durable; no SQLite table and no daemon worker",
        "worker_loop_enabled": False,
    }


def _task_queue_worker_policy(*, enabled: bool, requested_limit: int, configured_limit: int) -> dict:
    effective_limit = max(1, min(int(requested_limit), int(configured_limit), 20))
    return {
        "schema": "assistant.task_queue.worker_policy.v1",
        "worker_enabled": enabled,
        "execution_enabled": enabled,
        "one_shot_drain": True,
        "background_loop_created": False,
        "daemon_started": False,
        "service_installed": False,
        "infinite_loop_allowed": False,
        "durable_queue_enabled": False,
        "max_drain": configured_limit,
        "requested_limit": requested_limit,
        "effective_limit": effective_limit,
        "allowed_task_types": sorted(TASK_QUEUE_WORKER_ALLOWED_TYPES),
        "mutating_tasks_allowed": False,
        "shell_task_connected": False,
        "browser_task_connected": False,
        "external_api_task_connected": False,
        "rollback_task_connected": False,
        "app_os_task_connected": False,
    }


def _task_worker_audit(payload: dict) -> dict:
    return {
        "schema": "assistant.task_queue.worker_audit.v1",
        "payload": payload,
        "payload_hash": _stable_hash(payload),
        "note": "task queue worker는 env opt-in one-shot drain만 수행하며 daemon/service/background loop를 시작하지 않습니다.",
    }


def _task_queue_worker_result_wrapper(result: dict) -> dict:
    masked = _mask_secret_like_structure(result)
    return {
        **masked,
        "result_wrapper": {
            "schema": "assistant.task_queue.worker_result_wrapper.v1",
            "untrusted": True,
            "paste_safe": True,
            "masked": masked != result,
            "source": "task_queue_worker",
            "task_id": result.get("task_id"),
        },
        "audit": {
            "schema": "assistant.task_queue.worker_result_wrapper.audit.v1",
            "payload_hash": _stable_hash(masked),
        },
    }


def _task_audit_payload(task: dict) -> dict:
    return {
        "task_id": task.get("task_id"),
        "task_type": task.get("task_type"),
        "status": task.get("status"),
        "params": task.get("params"),
        "worker": task.get("worker"),
        "execution": task.get("execution"),
    }


def _task_audit(payload: dict) -> dict:
    return {
        "schema": "assistant.long_running_task.audit.v1",
        "payload": payload,
        "payload_hash": _stable_hash(payload),
        "note": "long-running task queue는 locked preview 상태이며 background worker를 시작하지 않습니다.",
    }


def _failure_summary(tool: str, reason: str, summary: str | None, params: dict) -> dict:
    normalized_reason = str(reason or "unknown_failure").strip().lower().replace("-", "_").replace(" ", "_")
    taxonomy = FAILURE_REASON_TAXONOMY.get(tool, [])
    if normalized_reason not in taxonomy:
        normalized_reason = "unknown_failure"
    return {
        "schema": "assistant.failure_reason.taxonomy.v1",
        "tool": tool,
        "reason": normalized_reason,
        "known_reasons": taxonomy,
        "summary": _mask_secret_like_values(summary or ""),
        "params": params,
    }


def _rollback_plan_for_failure(tool: str, failure: dict, params: dict, original_sha256: str | None) -> dict:
    if tool == "patch":
        original_hash = _safe_original_sha256(original_sha256, params)
        return {
            "schema": "assistant.rollback_plan.patch.v1",
            "type": "patch_rollback_preview",
            "original_sha256": original_hash,
            "preconditions": [
                "사용자가 원본 파일과 original_sha256을 직접 비교해야 합니다.",
                "자동 file restore, git reset, patch apply는 수행하지 않습니다.",
            ],
            "steps": [
                "diff preview와 original_sha256을 수동 검토합니다.",
                "필요하면 사용자가 별도 승인 후 직접 백업본을 복원합니다.",
            ],
            "would_apply": False,
            "rollback_enabled": False,
            "automatic_execution": False,
        }
    if tool == "shell":
        return {
            "schema": "assistant.rollback_plan.shell.v1",
            "type": "manual_instruction_only",
            "preconditions": ["실패한 command를 서버가 재실행하거나 되돌리지 않습니다."],
            "steps": ["명령 출력과 cwd를 사용자가 직접 확인합니다.", "필요하면 별도 승인 후 수동 명령을 새로 검토합니다."],
            "would_execute": False,
            "rollback_enabled": False,
            "automatic_execution": False,
        }
    return {
        "schema": "assistant.rollback_plan.browser.v1",
        "type": "manual_instruction_only",
        "preconditions": ["브라우저 session, click, fill, submit을 서버가 조작하지 않습니다."],
        "steps": ["대상 URL과 selector를 사용자가 직접 확인합니다.", "로그인/결제/삭제/전송 흐름은 별도 승인 전 자동화하지 않습니다."],
        "would_interact": False,
        "rollback_enabled": False,
        "automatic_execution": False,
    }


def _safe_original_sha256(original_sha256: str | None, params: dict) -> str:
    candidate = str(original_sha256 or params.get("original_sha256") or "").strip().lower()
    if re.fullmatch(r"[0-9a-f]{64}", candidate):
        return candidate
    return "missing_original_sha256"


def _manual_recovery_instructions(tool: str, rollback_plan: dict) -> list[str]:
    common = [
        "자동 rollback 실행은 비활성입니다.",
        "git reset, file restore, shell execution, browser interaction은 수행하지 않습니다.",
    ]
    return [*common, *rollback_plan.get("steps", [])]


def _failure_paste_safe_summary(failure: dict, rollback_plan: dict) -> str:
    text = (
        f"Failure recovery preview: tool={failure['tool']}, reason={failure['reason']}, "
        f"rollback_type={rollback_plan['type']}, automatic_execution=false."
    )
    if rollback_plan.get("original_sha256"):
        text += f" original_sha256={rollback_plan['original_sha256']}."
    return _mask_secret_like_values(text)


def _freeze_steps(steps: list[dict]) -> list[dict]:
    return json.loads(json.dumps(steps, ensure_ascii=False, sort_keys=True))


def _action_loop_preview_summary(tool: str, preview: dict | None) -> dict:
    if preview is None:
        return {"status": "blocked", "reason": "unsupported tool"}
    summary = {
        "mode": preview.get("mode"),
        "status": preview.get("status"),
        "allowed": preview.get("allowed", False),
        "reason": preview.get("reason"),
    }
    if tool == "shell":
        summary["command_preview"] = preview.get("command_preview")
        summary["would_execute"] = preview.get("would_execute")
    elif tool == "patch":
        summary["resolved_path"] = preview.get("resolved_path")
        summary["would_apply"] = preview.get("would_apply")
    elif tool == "browser":
        summary["action"] = preview.get("action")
        summary["would_interact"] = preview.get("would_interact")
    return summary


def _noop_route_step(preview: dict) -> dict:
    return {
        "index": preview["index"],
        "tool": preview["tool"],
        "route": f"noop://{preview['tool']}",
        "status": "routable_noop" if preview["status"] == "allowed_preview" else "blocked",
        "would_execute": False,
        "would_apply": False,
        "would_interact": False,
        "would_dispatch": False,
        "execution_enabled": False,
        "approval_validation_status": (
            preview.get("approval_check", {}) or {}
        ).get("status"),
        "violations": preview["violations"],
        "preview_summary": preview["preview_summary"],
    }


READ_ONLY_BOUNDARY_TOOLS = {"read_only_scan", "file_preview", "url_preview", "workspace_brief"}


def _read_only_result_wrapper_schema() -> dict:
    return {
        "schema": "assistant.action_loop.read_only_result_wrapper.v1",
        "contract_mode": "preview-only",
        "wrapper_required": True,
        "wrapper_untrusted_required": True,
        "raw_content_allowed": False,
        "masked_summary_only": True,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "required_fields": [
            "schema",
            "source_adapter",
            "wrapper",
            "masked_summary",
            "metadata",
            "safety",
            "audit",
        ],
        "prohibited_fields": [
            "raw_content",
            "raw_file_bytes",
            "raw_url_response",
            "approval",
            "approval_id",
            "approval_hash",
            "next_step",
            "shell_command",
            "patch_payload",
            "browser_action",
            "unwrapped_tool_result",
        ],
        "safety_fields": {
            "would_dispatch": False,
            "would_read": False,
            "would_fetch": False,
            "execution_enabled": False,
            "masking_required": True,
        },
    }


def _read_only_result_wrapper_preview(tool: str) -> dict:
    schema = _read_only_result_wrapper_schema()
    return {
        "schema": schema["schema"],
        "source_adapter": tool or "unknown",
        "contract_mode": schema["contract_mode"],
        "wrapper_required": True,
        "wrapper_untrusted_required": True,
        "would_include_raw_content": False,
        "would_trust_approval_like_json": False,
        "would_allow_next_step_mutation": False,
        "would_dispatch": False,
        "would_read": False,
        "would_fetch": False,
        "execution_enabled": False,
        "prohibited_fields": schema["prohibited_fields"],
    }


def _read_only_boundary_step_preview(index: int, step: dict, allowed_roots: str) -> dict:
    tool = str(step.get("tool") or "").strip().lower()
    params = step.get("params") if isinstance(step.get("params"), dict) else {}
    wrapper = step.get("wrapper") if isinstance(step.get("wrapper"), dict) else {}
    violations = []
    if wrapper.get("untrusted") is not True:
        violations.append("missing_untrusted_wrapper")
    if tool not in READ_ONLY_BOUNDARY_TOOLS:
        violations.append("unsupported_tool")
    target = _read_only_boundary_target(tool, params, allowed_roots)
    violations.extend(target["violations"])
    status = "routable_read_only_preview" if not violations else "blocked"
    return {
        "index": index,
        "tool": tool or "unknown",
        "route": f"read-only-boundary://{tool or 'unknown'}",
        "status": status,
        "boundary_only": True,
        "would_dispatch": False,
        "would_read": False,
        "would_fetch": False,
        "execution_enabled": False,
        "target": target["target"],
        "result_wrapper_preview": _read_only_result_wrapper_preview(tool or "unknown"),
        "violations": violations,
    }


def _read_only_boundary_target(tool: str, params: dict, allowed_roots: str) -> dict:
    roots = _allowed_roots(allowed_roots)
    violations: list[str] = []
    if tool in {"read_only_scan", "workspace_brief"}:
        raw_root = str(params.get("project_root") or "")
        resolved_root = _resolve_path(raw_root) if raw_root else None
        if not raw_root:
            violations.append("missing_project_root")
        elif not any(_is_relative_to(resolved_root, root) for root in roots):
            violations.append("project_root_outside_allowed_roots")
        return {
            "target": {
                "project_root": raw_root or None,
                "resolved_project_root": str(resolved_root) if resolved_root else None,
                "allowed_roots": [str(root) for root in roots],
            },
            "violations": violations,
        }
    if tool == "file_preview":
        raw_path = str(params.get("path") or "")
        resolved_path = _resolve_path(raw_path) if raw_path else None
        if not raw_path:
            violations.append("missing_path")
        elif not any(_is_relative_to(resolved_path, root) for root in roots):
            violations.append("path_outside_allowed_roots")
        elif _is_sensitive_path(resolved_path):
            violations.append("sensitive_path")
        return {
            "target": {
                "path": raw_path or None,
                "resolved_path": str(resolved_path) if resolved_path else None,
                "allowed_roots": [str(root) for root in roots],
            },
            "violations": violations,
        }
    if tool == "url_preview":
        url = str(params.get("url") or "").strip()
        if not url:
            violations.append("missing_url")
        else:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                violations.append("invalid_url")
        return {"target": {"url": url or None}, "violations": violations}
    return {"target": {}, "violations": violations}


WEB_SEARCH_PROVIDER_CANDIDATES = {"disabled", "none", "tavily", "serpapi", "brave", "bing", "google_cse"}
WEB_SEARCH_EXECUTION_PROVIDERS = {"brave"}
METADATA_HOSTS = {
    "169.254.169.254",
    "metadata.google.internal",
    "metadata",
}


def _evaluate_web_search_provider_policy(
    *,
    query: str,
    requested_provider: str | None,
    configured_provider: str | None,
    external_api_enabled: bool,
    rate_limit_per_minute: int,
    result_wrapper: dict | None,
) -> dict:
    raw_query = query.strip()
    query_preview = _mask_secret_like_values(raw_query)
    provider = (requested_provider or configured_provider or "").strip().lower() or None
    provider_configured = bool(configured_provider)
    wrapper_status = _web_search_result_wrapper_status(result_wrapper)
    url_scan = _scan_query_for_private_or_metadata_urls(raw_query)

    if url_scan["blocked"]:
        status = "blocked"
        reason = "private/LAN/metadata URL 후보가 query에 포함되어 external web search provider gate에서 차단됩니다."
    elif result_wrapper is not None and not wrapper_status["valid"]:
        status = "blocked"
        reason = "external web search result wrapper는 untrusted=true를 포함해야 합니다."
    elif not external_api_enabled or not provider_configured:
        status = "provider_not_configured"
        reason = "외부 web search provider가 설정되지 않았거나 EXTERNAL_WEB_SEARCH_ENABLED=false입니다."
    else:
        status = "blocked"
        reason = "외부 web search provider 실제 호출은 Decision Required 전까지 차단됩니다."

    payload = {
        "query_preview": query_preview,
        "provider": provider,
        "status": status,
        "external_api_enabled": False,
        "would_search": False,
        "would_fetch": False,
        "blocked_urls": url_scan["blocked_hosts"],
        "wrapper_untrusted": wrapper_status["untrusted"],
    }
    return {
        "status": status,
        "provider": provider,
        "query_preview": query_preview,
        "reason": reason,
        "provider_config": {
            "schema": "assistant.web_search.provider_config.v1",
            "configured": provider_configured,
            "configured_provider": configured_provider,
            "requested_provider": requested_provider,
            "provider": provider,
            "supported_provider_candidates": sorted(WEB_SEARCH_PROVIDER_CANDIDATES),
            "external_api_enabled": False,
            "default_external_api_enabled": False,
            "api_key_configured": False,
            "paid_provider_enabled": False,
            "rate_limit_per_minute": rate_limit_per_minute,
            "cost_control": {
                "cost_budget_configured": False,
                "paid_calls_allowed": False,
                "decision_required_before_paid_provider": True,
            },
        },
        "gate": {
            "schema": "assistant.web_search.provider_gate.v1",
            "contract_mode": "locked-preview",
            "provider_not_configured": status == "provider_not_configured",
            "external_api_enabled": False,
            "would_search": False,
            "would_fetch": False,
            "external_call_performed": False,
            "network_request_performed": False,
            "private_lan_metadata_url_blocked": url_scan["blocked"],
            "blocked_hosts": url_scan["blocked_hosts"],
            "query_masking_required": True,
            "result_wrapper_untrusted_required": True,
            "decision_required": True,
        },
        "result_wrapper": wrapper_status,
        "audit": {
            "schema": "assistant.web_search.provider_gate.preview.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
            "note": "audit payload는 external web search 실행 증거가 아니라 provider gate preview 계약입니다.",
        },
    }


def _web_search_result_wrapper_status(result_wrapper: dict | None) -> dict:
    provided = isinstance(result_wrapper, dict)
    untrusted = bool(result_wrapper.get("untrusted") is True) if provided else False
    return {
        "schema": "assistant.web_search.result_wrapper.v1",
        "required": True,
        "provided": provided,
        "untrusted": untrusted,
        "valid": provided and untrusted,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "execution_enabled": False,
        "required_fields": ["schema", "source_provider", "wrapper", "masked_summary", "metadata", "safety", "audit"],
        "missing": [] if untrusted else ["untrusted=true"],
    }


def _evaluate_web_search_provider_search_policy(
    *,
    query: str,
    requested_provider: str | None,
    configured_provider: str | None,
    api_key_configured: bool,
    external_api_enabled: bool,
    rate_limit_per_minute: int,
    result_wrapper: dict | None,
) -> dict:
    preview = _evaluate_web_search_provider_policy(
        query=query,
        requested_provider=requested_provider,
        configured_provider=configured_provider,
        external_api_enabled=external_api_enabled,
        rate_limit_per_minute=rate_limit_per_minute,
        result_wrapper=result_wrapper,
    )
    provider = preview["provider"]
    wrapper = preview["result_wrapper"]
    reason = None
    if preview["gate"]["private_lan_metadata_url_blocked"]:
        reason = "private/LAN/metadata URL 후보가 query에 포함되어 external web search에서 차단됩니다."
    elif _contains_approval_like_json({"query": query}):
        reason = "approval-like JSON injection은 external web search에서 차단됩니다."
    elif _looks_secret_like(query):
        reason = "secret-like query는 external web search에서 차단됩니다."
    elif not wrapper["valid"]:
        reason = "external web search result wrapper는 untrusted=true를 포함해야 합니다."
    elif not external_api_enabled:
        reason = "EXTERNAL_WEB_SEARCH_ENABLED=false 상태라 external web search 실행이 차단됩니다."
    elif not provider or provider not in WEB_SEARCH_EXECUTION_PROVIDERS:
        reason = "external web search provider allowlist에 없는 provider입니다."
    elif not configured_provider or provider != configured_provider.strip().lower():
        reason = "요청 provider가 서버 설정 provider와 일치하지 않습니다."
    elif not api_key_configured:
        reason = "external web search provider API key가 설정되지 않았습니다."
    elif rate_limit_per_minute <= 0:
        reason = "EXTERNAL_WEB_SEARCH_RATE_LIMIT_PER_MINUTE가 1 이상이어야 합니다."
    allowed = reason is None
    provider_config = {
        **preview["provider_config"],
        "external_api_enabled": external_api_enabled,
        "api_key_configured": api_key_configured,
        "api_key_returned": False,
        "paid_provider_enabled": external_api_enabled and api_key_configured,
        "execution_provider_allowlist": sorted(WEB_SEARCH_EXECUTION_PROVIDERS),
    }
    gate = {
        **preview["gate"],
        "contract_mode": "provider-execution-v1",
        "external_api_enabled": external_api_enabled,
        "would_search": allowed,
        "would_fetch": allowed,
        "external_call_performed": False,
        "network_request_performed": False,
        "provider_allowlist_enforced": True,
        "rate_limit_required": True,
        "api_key_required": True,
        "api_key_returned": False,
        "decision_required": False if allowed else True,
    }
    payload = {
        "query_preview": preview["query_preview"],
        "provider": provider,
        "allowed": allowed,
        "external_api_enabled": external_api_enabled,
        "api_key_configured": api_key_configured,
        "rate_limit_per_minute": rate_limit_per_minute,
        "wrapper_untrusted": wrapper["untrusted"],
    }
    return {
        "allowed": allowed,
        "status": "ready" if allowed else "blocked",
        "provider": provider,
        "query_preview": preview["query_preview"],
        "reason": reason or "external web search provider gate passed.",
        "provider_config": provider_config,
        "gate": gate,
        "result_wrapper": wrapper,
        "audit": {
            "schema": "assistant.web_search.provider_search.policy.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _execute_external_web_search(provider: str, query: str, api_key: str) -> dict:
    normalized_provider = provider.strip().lower()
    try:
        if normalized_provider != "brave":
            return _external_web_search_failed_result(normalized_provider, query, "unsupported_provider")
        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": 5},
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        raw_results = ((payload.get("web") or {}).get("results") or [])[:5]
        results = [
            {
                "title": _mask_secret_like_values(str(item.get("title") or ""))[:200],
                "url": _mask_secret_like_values(str(item.get("url") or ""))[:500],
                "snippet": _mask_secret_like_values(str(item.get("description") or ""))[:500],
            }
            for item in raw_results
            if isinstance(item, dict)
        ]
        return {
            "schema": "assistant.external_web_search.result.v1",
            "status": "completed",
            "provider": normalized_provider,
            "query_preview": _mask_secret_like_values(query),
            "results": results,
            "results_count": len(results),
            "external_call_performed": True,
            "network_request_performed": True,
            "raw_content_returned": False,
            "api_key_returned": False,
            "paste_safe_summary": f"external_web_search status=completed provider={normalized_provider} results={len(results)}",
        }
    except (httpx.HTTPError, ValueError) as exc:
        return _external_web_search_failed_result(normalized_provider, query, exc.__class__.__name__)


def _external_web_search_failed_result(provider: str, query: str, error: str) -> dict:
    return {
        "schema": "assistant.external_web_search.result.v1",
        "status": "failed",
        "provider": provider,
        "query_preview": _mask_secret_like_values(query),
        "results": [],
        "results_count": 0,
        "external_call_performed": provider in WEB_SEARCH_EXECUTION_PROVIDERS,
        "network_request_performed": provider in WEB_SEARCH_EXECUTION_PROVIDERS,
        "raw_content_returned": False,
        "api_key_returned": False,
        "paste_safe_summary": f"external_web_search status=failed provider={provider} error={error}",
    }


def _external_web_search_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    payload = {
        "status": safe_result.get("status"),
        "provider": safe_result.get("provider"),
        "results_count": safe_result.get("results_count"),
        "external_call_performed": safe_result.get("external_call_performed"),
    }
    return {
        "schema": "assistant.external_web_search.result_wrapper.v1",
        "untrusted": True,
        "source_provider": safe_result.get("provider"),
        "status": safe_result.get("status"),
        "result": safe_result,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.external_web_search.result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _scan_query_for_private_or_metadata_urls(query: str) -> dict:
    blocked_hosts: list[str] = []
    for raw_url in re.findall(r"https?://[^\s\"'<>]+", query, flags=re.IGNORECASE):
        parsed = urlparse(raw_url)
        host = (parsed.hostname or "").strip().lower()
        if _is_private_lan_or_metadata_host(host):
            blocked_hosts.append(host)
    return {"blocked": bool(blocked_hosts), "blocked_hosts": sorted(set(blocked_hosts))}


def _is_private_lan_or_metadata_host(host: str) -> bool:
    if not host:
        return False
    normalized = host.strip("[]").lower().rstrip(".")
    if normalized in METADATA_HOSTS or normalized == "localhost" or normalized.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return any(
        [
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_multicast,
            ip.is_reserved,
            ip.is_unspecified,
        ]
    )


APP_OS_OBSERVE_PLAN_ACTIONS = {"observe", "observe_plan", "observe-plan", "status", "read"}
APP_OS_BLOCKED_ACTIONS = {
    "open",
    "launch",
    "click",
    "type",
    "input",
    "hotkey",
    "shortcut",
    "file_dialog",
    "file-dialog",
    "file_open",
    "file-open",
    "save",
    "delete",
    "login",
    "payment",
    "submit",
    "drag",
    "drop",
}


def _evaluate_app_os_interaction_policy(
    *,
    action: str,
    app_name: str | None,
    window_title: str | None,
    target_path: str | None,
    input_preview: str | None,
    reason: str | None,
    os_control_enabled: bool,
    session_id: str | None,
) -> dict:
    normalized_action = action.strip().lower().replace(" ", "_")
    masked_app_name = _mask_secret_like_values(app_name or "")
    masked_window_title = _mask_secret_like_values(window_title or "")
    masked_target_path = _mask_secret_like_values(target_path or "")
    masked_input = _mask_secret_like_values(input_preview or "")
    masked_reason = _mask_secret_like_values(reason or "")
    path_blocked = _app_os_target_path_blocked(target_path)
    observe_candidate = normalized_action in APP_OS_OBSERVE_PLAN_ACTIONS and not path_blocked["blocked"]

    taxonomy = {
        "observe_plan_actions": sorted(APP_OS_OBSERVE_PLAN_ACTIONS),
        "blocked_actions": sorted(APP_OS_BLOCKED_ACTIONS),
        "allowed_actions": [],
        "app_launch": "blocked",
        "click_type_hotkey": "blocked",
        "file_dialog": "blocked",
        "permission_model": "documented-only",
    }
    if path_blocked["blocked"]:
        status = "blocked"
        reason_text = path_blocked["reason"]
    elif normalized_action in APP_OS_BLOCKED_ACTIONS:
        status = "blocked"
        reason_text = f"App/OS interaction 금지 taxonomy에 포함되어 차단됩니다: {normalized_action}"
    elif not observe_candidate:
        status = "blocked"
        reason_text = "20차 App/OS gate는 observe-plan 후보 외 action을 허용하지 않습니다."
    elif os_control_enabled:
        status = "observe_plan_candidate"
        reason_text = "observe-plan 후보이지만 실제 OS app control은 연결하지 않았습니다."
    else:
        status = "observe_plan_candidate"
        reason_text = "observe-plan 후보입니다. APP_OS_CONTROL_ENABLED=false 기본값이므로 실제 app/OS action은 수행하지 않습니다."

    payload = {
        "action": normalized_action,
        "app_name": masked_app_name or None,
        "window_title": masked_window_title or None,
        "target_path": masked_target_path or None,
        "input_preview": masked_input or None,
        "reason_preview": masked_reason or None,
        "status": status,
        "observe_plan_candidate": observe_candidate,
        "would_control_app": False,
        "os_action_executed": False,
    }
    payload_hash = _stable_hash(payload)
    return {
        "status": status,
        "action": normalized_action,
        "app_name": masked_app_name or None,
        "window_title": masked_window_title or None,
        "target_path": masked_target_path or None,
        "observe_plan_candidate": observe_candidate,
        "reason": reason_text,
        "taxonomy": taxonomy,
        "permission_model": {
            "schema": "assistant.app_os.permission_model.v1",
            "contract_mode": "documented-only",
            "os_control_enabled": False,
            "requires_user_final_approval": True,
            "requires_platform_permission_review": True,
            "requires_app_allowlist": True,
            "requires_single_action_approval": True,
            "bulk_approval_allowed": False,
            "implemented_permissions": [],
            "blocked_permissions": [
                "app_open",
                "window_focus",
                "mouse_click",
                "keyboard_type",
                "hotkey",
                "file_dialog",
            ],
        },
        "approval_binding": {
            "schema": "assistant.app_os.approval_binding_design.v1",
            "designed_only": True,
            "server_issued_approval_required": True,
            "approval_store": "not-created",
            "approval_scope": "single-app-os-observe-plan-preview-only",
            "payload_hash": payload_hash,
            "single_use": True,
            "session_context": _approval_session_context(session_id),
            "note": "approval binding은 설계 계약만 노출하며 실제 OS action approval로 사용하지 않습니다.",
        },
        "gate": {
            "schema": "assistant.app_os.interaction_gate.v1",
            "contract_mode": "locked-preview",
            "allowed": False,
            "observe_plan_candidate": observe_candidate,
            "app_os_control_enabled": False,
            "would_control_app": False,
            "os_action_executed": False,
            "computer_use_connected": False,
            "applescript_connected": False,
            "osascript_connected": False,
            "open_command_connected": False,
            "permission_model_documented": True,
            "target_path_blocked": path_blocked["blocked"],
            "blocked_execution": [
                "app_open",
                "click",
                "type",
                "hotkey",
                "file_dialog",
                "file_open",
            ],
        },
        "audit": {
            "schema": "assistant.app_os.interaction_gate.preview.v1",
            "payload": payload,
            "payload_hash": payload_hash,
            "note": "audit payload는 App/OS 실행 증거가 아니라 locked preview 계약입니다.",
        },
    }


def _app_os_target_path_blocked(target_path: str | None) -> dict:
    if not target_path:
        return {"blocked": False, "reason": None}
    try:
        resolved = _resolve_path(target_path)
    except RuntimeError:
        resolved = Path(target_path).expanduser()
    if _is_sensitive_path(resolved):
        return {"blocked": True, "reason": "credential/private path 후보는 App/OS gate에서 차단됩니다."}
    return {"blocked": False, "reason": None}


BROWSER_READ_ONLY_ACTIONS = {
    "observe",
    "inspect",
    "screenshot",
    "read",
    "read_only",
    "read-only",
    "page_title",
    "current_url",
}
BROWSER_BLOCKED_ACTIONS = {
    "click",
    "fill",
    "submit",
    "login",
    "payment",
    "delete",
    "download",
    "upload",
    "navigate",
    "open",
    "install",
    "run",
}


def _evaluate_browser_policy(
    action: str,
    target_url: str | None,
    app_name: str | None,
    selector: str | None,
    input_preview: str | None,
    reason: str | None,
) -> dict:
    normalized_action = action.strip().lower().replace(" ", "_")
    masked_input = _mask_secret_like_values(input_preview or "")
    masked_reason = _mask_secret_like_values(reason or "")
    taxonomy = {
        "read_only_actions": sorted(BROWSER_READ_ONLY_ACTIONS),
        "blocked_actions": sorted(BROWSER_BLOCKED_ACTIONS),
        "os_app_control": "blocked",
        "network_fetch": "not_performed",
        "login_session_use": "blocked",
        "domain_allowlist": "candidate_design_only",
    }
    parsed_domain = None
    if target_url:
        parsed = urlparse(target_url)
        parsed_domain = parsed.netloc.lower() or None
    base = {
        "action": normalized_action,
        "target_url": target_url,
        "target_domain": parsed_domain,
        "app_name": app_name,
        "selector": _mask_secret_like_values(selector or ""),
        "input_preview": masked_input,
        "reason_preview": masked_reason,
        "taxonomy": taxonomy,
    }
    if app_name:
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "risk": "high",
            "reason": "OS app control은 7차 locked preview에서도 차단됩니다.",
        }
    if target_url:
        parsed = urlparse(target_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return {
                **base,
                "status": "blocked",
                "allowed": False,
                "risk": "medium",
                "reason": "browser target_url은 http/https URL 형식만 preview 후보가 될 수 있습니다.",
            }
    if normalized_action in BROWSER_BLOCKED_ACTIONS:
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "risk": "high",
            "reason": f"브라우저/앱 interaction 금지 taxonomy에 포함되어 차단됩니다: {normalized_action}",
        }
    if normalized_action not in BROWSER_READ_ONLY_ACTIONS:
        return {
            **base,
            "status": "blocked",
            "allowed": False,
            "risk": "medium",
            "reason": "7차 browser preview allowlist에 없는 action입니다.",
        }
    return {
        **base,
        "status": "allowed_preview",
        "allowed": True,
        "risk": "low",
        "reason": "read-only 관찰 action 후보이지만 실제 browser/app control은 수행하지 않습니다.",
    }


def _browser_audit_payload(policy: dict) -> dict:
    payload = {
        "action": policy["action"],
        "target_url": policy["target_url"],
        "app_name": policy["app_name"],
        "selector": policy["selector"],
        "input_preview": policy["input_preview"],
        "reason_preview": policy["reason_preview"],
        "status": policy["status"],
        "risk": policy["risk"],
        "would_interact": False,
    }
    return {
        "schema": "assistant.browser_interaction.preview.v1",
        "payload": payload,
        "payload_hash": _stable_hash(payload),
        "note": "audit payload는 실행 증거가 아니라 locked browser/app interaction preview 계약입니다.",
    }


def _browser_gate_payload(policy: dict) -> dict:
    return {
        "schema": "assistant.browser_interaction.gate.v1",
        "contract_mode": "locked-preview",
        "execution_enabled": False,
        "launch_enabled": False,
        "would_interact": False,
        "browser_launch": "not_performed",
        "allowed_candidate": bool(policy["allowed"]),
        "action_taxonomy": policy["taxonomy"],
        "domain_allowlist_candidate": {
            "mode": "design-only",
            "enforced": False,
            "configured_domains": [],
            "target_domain": policy.get("target_domain"),
            "note": "domain allowlist는 후보 설계만 노출하며 실제 browser/network control에 사용하지 않습니다.",
        },
        "masked_fields": ["selector", "input_preview", "reason_preview"],
        "blocked_execution": [
            "click",
            "fill",
            "submit",
            "login",
            "payment",
            "delete",
            "browser_launch",
            "os_app_control",
        ],
    }


BROWSER_OBSERVE_ACTIONS = {"observe", "inspect", "screenshot", "read", "read_only", "read-only", "page_title", "current_url"}


def _browser_observe_action_from_tool(tool: str) -> str:
    normalized = tool.strip().lower().replace("-", "_")
    if normalized == "browser_screenshot":
        return "screenshot"
    if normalized == "browser_page_title":
        return "page_title"
    return "observe"


def _browser_observe_policy_reason(action: str, target_url: str, allowed_origins: str) -> str | None:
    normalized_action = action.strip().lower().replace(" ", "_")
    if normalized_action not in BROWSER_OBSERVE_ACTIONS:
        return f"browser observe allowlist에 없는 action입니다: {normalized_action}"
    parsed = urlparse(target_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "browser observe target_url은 http/https URL이어야 합니다."
    host = parsed.hostname or ""
    if _is_private_lan_or_metadata_host(host) and not _is_loopback_browser_host(host):
        return "private/LAN/metadata URL은 browser observe에서 차단됩니다."
    allowed = _browser_observe_allowed_origins(allowed_origins)
    origin = f"{parsed.scheme}://{parsed.hostname or ''}".lower()
    if parsed.port:
        origin_with_port = f"{origin}:{parsed.port}"
    else:
        origin_with_port = origin
    if not _is_loopback_browser_host(host) and origin not in allowed and origin_with_port not in allowed:
        return "target_url origin이 browser observe allowlist에 없어 차단됩니다."
    return None


def _browser_observe_allowed_origins(raw: str) -> set[str]:
    origins = set()
    for item in raw.split(","):
        value = item.strip().rstrip("/").lower()
        if value:
            origins.add(value)
    return origins


def _is_loopback_browser_host(host: str) -> bool:
    normalized = host.strip().lower()
    if normalized in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def _execute_browser_observe(action: str, target_url: str) -> dict:
    normalized_action = action.strip().lower().replace(" ", "_")
    try:
        response = httpx.get(target_url, timeout=5.0, follow_redirects=False)
        content = response.content[:50_000]
        text = response.text[:50_000]
        title = _extract_html_title(text)
        status = "completed"
        reason = f"browser_observe status=completed http_status={response.status_code} title_present={bool(title)}"
        return {
            "schema": "assistant.browser_observe.result.v1",
            "status": status,
            "action": normalized_action,
            "target_url": _mask_secret_like_values(target_url),
            "current_url": _mask_secret_like_values(str(response.url)),
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "page_title": _mask_secret_like_values(title or ""),
            "body_bytes_sampled": len(content),
            "browser_launch": "not_performed",
            "screenshot_requested": normalized_action == "screenshot",
            "screenshot_captured": False,
            "raw_content_returned": False,
            "paste_safe_summary": reason,
        }
    except httpx.HTTPError as exc:
        reason = f"browser_observe status=failed error={exc.__class__.__name__}"
        return {
            "schema": "assistant.browser_observe.result.v1",
            "status": "failed",
            "action": normalized_action,
            "target_url": _mask_secret_like_values(target_url),
            "current_url": None,
            "http_status": None,
            "content_type": None,
            "page_title": "",
            "body_bytes_sampled": 0,
            "browser_launch": "not_performed",
            "screenshot_requested": normalized_action == "screenshot",
            "screenshot_captured": False,
            "raw_content_returned": False,
            "paste_safe_summary": reason,
        }


def _extract_html_title(text: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return title[:200]


def _browser_observe_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    payload = {
        "status": safe_result.get("status"),
        "action": safe_result.get("action"),
        "target_url": safe_result.get("target_url"),
        "current_url": safe_result.get("current_url"),
        "http_status": safe_result.get("http_status"),
        "page_title_present": bool(safe_result.get("page_title")),
        "screenshot_captured": safe_result.get("screenshot_captured"),
    }
    return {
        "schema": "assistant.browser_observe.result_wrapper.v1",
        "untrusted": True,
        "source_adapter": "browser_observe",
        "status": safe_result.get("status"),
        "result": safe_result,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.browser_observe.result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


BROWSER_LIMITED_INTERACTION_ACTIONS = {"click", "fill"}
BROWSER_LIMITED_INTERACTION_BLOCKED_ACTIONS = {
    "submit",
    "login",
    "payment",
    "delete",
    "download",
    "upload",
    "file_dialog",
    "open_file",
    "navigate",
    "type",
    "press",
}
BROWSER_CREDENTIAL_FIELD_TOKENS = {
    "password",
    "passwd",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "card",
    "cvv",
    "ssn",
}


def _browser_limited_action_from_tool(tool: str) -> str:
    normalized = tool.strip().lower().replace("-", "_")
    if normalized == "browser_fill":
        return "fill"
    return "click"


def _browser_limited_interaction_policy(
    *,
    action: str,
    target_url: str,
    selector: str,
    field_name: str | None,
    input_preview: str | None,
    allowed_origins: str,
    allowed_selectors: str,
    allowed_fill_fields: str,
) -> dict:
    normalized_action = action.strip().lower().replace(" ", "_").replace("-", "_")
    normalized_selector = selector.strip()
    normalized_field = (field_name or "").strip().lower()
    parsed = urlparse(target_url)
    origin = ""
    origin_with_port = ""
    host = parsed.hostname or ""
    if parsed.scheme and parsed.hostname:
        origin = f"{parsed.scheme}://{parsed.hostname}".lower()
        origin_with_port = f"{origin}:{parsed.port}" if parsed.port else origin
    configured_origins = _browser_observe_allowed_origins(allowed_origins)
    configured_selectors = _browser_limited_csv(allowed_selectors)
    configured_fill_fields = _browser_limited_csv(allowed_fill_fields)
    base = {
        "schema": "assistant.browser_limited_interaction.policy.v1",
        "action": normalized_action,
        "target_url": _mask_secret_like_values(target_url),
        "target_origin": origin_with_port,
        "selector": _mask_secret_like_values(normalized_selector),
        "field_name": _mask_secret_like_values(normalized_field),
        "input_preview": _mask_secret_like_values(input_preview or ""),
        "allowed": False,
        "reason": "",
        "payload_hash": "",
        "browser_launch": "not_performed",
        "interaction_execution": "not_connected",
        "allowed_actions": sorted(BROWSER_LIMITED_INTERACTION_ACTIONS),
        "blocked_actions": sorted(BROWSER_LIMITED_INTERACTION_BLOCKED_ACTIONS),
        "configured_origins": sorted(configured_origins),
        "configured_selectors": sorted(configured_selectors),
        "configured_fill_fields": sorted(configured_fill_fields),
    }
    reason = None
    if normalized_action in BROWSER_LIMITED_INTERACTION_BLOCKED_ACTIONS:
        reason = f"browser limited interaction blocked action입니다: {normalized_action}"
    elif normalized_action not in BROWSER_LIMITED_INTERACTION_ACTIONS:
        reason = f"browser limited interaction allowlist에 없는 action입니다: {normalized_action}"
    elif parsed.scheme not in {"http", "https"} or not parsed.netloc:
        reason = "browser limited interaction target_url은 http/https URL이어야 합니다."
    elif _is_private_lan_or_metadata_host(host) and not _is_loopback_browser_host(host):
        reason = "private/LAN/metadata URL은 browser limited interaction에서 차단됩니다."
    elif not _is_loopback_browser_host(host) and origin not in configured_origins and origin_with_port not in configured_origins:
        reason = "target_url origin이 browser limited interaction allowlist에 없어 차단됩니다."
    elif normalized_selector not in configured_selectors:
        reason = "selector가 browser limited interaction selector allowlist에 없어 차단됩니다."
    elif normalized_action == "fill" and normalized_field and _browser_field_is_credential_like(normalized_field):
        reason = "credential-like field는 browser limited interaction에서 차단됩니다."
    elif normalized_action == "fill" and not normalized_field:
        reason = "fill action은 field_name이 필요합니다."
    elif normalized_action == "fill" and normalized_field not in configured_fill_fields:
        reason = "fill field가 browser limited interaction field allowlist에 없어 차단됩니다."
    elif _contains_approval_like_json({"field_name": normalized_field, "input_preview": input_preview or ""}):
        reason = "approval-like JSON injection은 browser limited interaction에서 차단됩니다."
    elif _looks_secret_like(input_preview or ""):
        reason = "secret-like input은 browser limited interaction에서 차단됩니다."
    if reason:
        blocked = {**base, "reason": reason}
        return {**blocked, "payload_hash": _stable_hash(blocked)}
    allowed = {
        **base,
        "allowed": True,
        "reason": "limited interaction candidate는 검증됐지만 실제 browser launch/click/fill은 아직 연결하지 않았습니다.",
    }
    return {**allowed, "payload_hash": _stable_hash(allowed)}


def _browser_limited_csv(raw: str) -> set[str]:
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _browser_field_is_credential_like(field_name: str) -> bool:
    normalized = field_name.strip().lower().replace("-", "_")
    return any(token in normalized for token in BROWSER_CREDENTIAL_FIELD_TOKENS)


def _browser_limited_interaction_candidate_result(policy: dict) -> dict:
    return {
        "schema": "assistant.browser_limited_interact.result.v1",
        "status": "validated",
        "action": policy["action"],
        "target_url": policy["target_url"],
        "target_origin": policy["target_origin"],
        "selector": policy["selector"],
        "field_name": policy["field_name"],
        "interaction_executed": False,
        "browser_launch": "not_performed",
        "profile_used": False,
        "session_mutated": False,
        "input_submitted": False,
        "download_started": False,
        "upload_started": False,
        "raw_content_returned": False,
        "paste_safe_summary": (
            "browser limited interaction candidate validated; actual browser launch/click/fill not performed"
        ),
    }


def _browser_limited_interaction_result_wrapper(result: dict) -> dict:
    safe_result = _mask_secret_like_structure(result)
    payload = {
        "status": safe_result.get("status"),
        "action": safe_result.get("action"),
        "target_url": safe_result.get("target_url"),
        "selector": safe_result.get("selector"),
        "interaction_executed": safe_result.get("interaction_executed"),
        "browser_launch": safe_result.get("browser_launch"),
    }
    return {
        "schema": "assistant.browser_limited_interact.result_wrapper.v1",
        "untrusted": True,
        "source_adapter": "browser_limited_interact",
        "status": safe_result.get("status"),
        "result": safe_result,
        "raw_content_allowed": False,
        "approval_like_json_trusted": False,
        "can_mutate_frozen_plan": False,
        "can_set_next_action": False,
        "can_request_approval": False,
        "audit": {
            "schema": "assistant.browser_limited_interact.result_wrapper.audit.v1",
            "payload": payload,
            "payload_hash": _stable_hash(payload),
        },
    }


def _stable_hash(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _approval_session_context(session_id: str | None) -> str:
    normalized = (session_id or "").strip()
    return normalized if normalized else APPROVAL_SESSIONLESS_CONTEXT


def _approval_public_record(record: dict) -> dict:
    return {
        "approval_id": record["approval_id"],
        "tool_name": record["tool_name"],
        "payload_hash": record["payload_hash"],
        "session_context": record["session_context"],
        "session_id": record["session_id"],
        "scope": record["scope"],
        "issued_at": record["issued_at"].isoformat(),
        "expires_at": record["expires_at"].isoformat(),
        "ttl_seconds": record["ttl_seconds"],
        "used": record["used"],
        "console_state": record.get("console_state", "pending"),
        "console_reason": record.get("console_reason"),
        "console_updated_at": (
            record["console_updated_at"].isoformat()
            if isinstance(record.get("console_updated_at"), datetime)
            else record.get("console_updated_at")
        ),
        "console_execution_triggered": bool(record.get("console_execution_triggered", False)),
        "store": "server-in-memory",
        "server_issued": True,
        "single_use": True,
    }


def _approval_console_ref(approval_id: str) -> str:
    return f"approval-ref:{_stable_hash({'approval_ref_source': approval_id})[:16]}"


def _approval_console_safe_record(approval: dict) -> dict:
    return {
        "approval_ref": _approval_console_ref(str(approval.get("approval_id", ""))),
        "tool_name": approval.get("tool_name"),
        "scope": approval.get("scope"),
        "issued_at": approval.get("issued_at"),
        "expires_at": approval.get("expires_at"),
        "ttl_seconds": approval.get("ttl_seconds"),
        "used": bool(approval.get("used")),
        "console_state": approval.get("console_state", "pending"),
        "console_reason": approval.get("console_reason"),
        "console_updated_at": approval.get("console_updated_at"),
        "console_execution_triggered": bool(approval.get("console_execution_triggered", False)),
        "server_issued": bool(approval.get("server_issued", False)),
        "single_use": bool(approval.get("single_use", True)),
        "session_bound": bool(approval.get("session_context")),
        "raw_approval_id_included": False,
        "payload_hash_included": False,
        "omitted_fields": ["approval_id", "payload_hash", "session_id", "session_context"],
    }


def _approval_console_safe_cleanup(cleanup: dict) -> dict:
    return {
        "schema": cleanup.get("schema", "assistant.approval_store.expiry_cleanup.v1"),
        "status": cleanup.get("status"),
        "expired_count": int(cleanup.get("expired_count", 0)),
        "records_removed": int(cleanup.get("records_removed", 0)),
        "state_only": bool(cleanup.get("state_only", True)),
        "execution_triggered": False,
        "approval_consumed": False,
        "raw_approval_id_included": False,
        "payload_hash_included": False,
        "paste_safe_summary": cleanup.get("paste_safe_summary", ""),
        "omitted_fields": ["approval_id", "payload_hash", "session_id", "session_context"],
    }


def _approval_console_gates() -> dict:
    return {
        "endpoint_surface": "read-only",
        "protected_endpoint_only": True,
        "local_api_key_supported": True,
        "pending_list_detail_cleanup_connected": True,
        "approve_endpoint_connected": False,
        "reject_endpoint_connected": False,
        "approve_reject_is_execution": False,
        "cleanup_is_approval_consume": False,
        "approval_consumed": False,
        "would_execute": False,
        "action_loop_full_dispatch_connected": False,
        "browser_actual_interaction_connected": False,
        "app_os_actual_action_connected": False,
    }


def _approval_console_audit(payload: dict) -> dict:
    return {
        "schema": "assistant.approval_console.read_only.v1",
        "payload": payload,
        "audit_summary_hash": _stable_hash(payload),
        "raw_approval_id_included": False,
        "payload_hash_included": False,
    }


def _durable_state_preview_ref(kind: str, value: str | None) -> str:
    normalized = (value or f"{kind}:sessionless").strip()
    return f"{kind}-ref:{_stable_hash({f'{kind}_ref_source': normalized})[:16]}"


def _durable_state_preview_safe_metadata(metadata: dict) -> dict:
    safe = _mask_secret_like_structure(metadata)
    return _durable_state_preview_redact_sensitive_keys(safe)


def _durable_state_preview_redact_sensitive_keys(value):
    if isinstance(value, list):
        return [_durable_state_preview_redact_sensitive_keys(item) for item in value]
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(token in normalized for token in {"approval_id", "approval_payload_hash", "payload_hash", "token", "secret", "password"}):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = _durable_state_preview_redact_sensitive_keys(item)
        return redacted
    return value


def _durable_state_preview_gates() -> dict:
    return {
        "endpoint_surface": "response-only-read-only-schema-only",
        "protected_endpoint_only": True,
        "local_api_key_supported": True,
        "read_only": True,
        "schema_only": True,
        "response_only": True,
        "stored_preview_lookup_connected": False,
        "stored_preview_list_connected": False,
        "stored_preview_cleanup_connected": False,
        "durable_storage_migration_connected": False,
        "durable_table_created": False,
        "persistence_mutation_connected": False,
        "queue_mutation_connected": False,
        "would_execute": False,
        "would_persist": False,
        "would_dispatch": False,
        "would_start_worker": False,
        "would_schedule": False,
        "would_replay": False,
        "would_recover": False,
        "approval_consumed": False,
        "action_loop_full_dispatch_connected": False,
        "browser_actual_interaction_connected": False,
        "app_os_actual_action_connected": False,
    }


def _durable_state_preview_audit(payload: dict) -> dict:
    return {
        "schema": "assistant.durable_state_preview.read_only.v1",
        "payload": payload,
        "audit_summary_hash": _stable_hash(payload),
        "raw_approval_id_included": False,
        "payload_hash_included": False,
    }


def _approval_check_result(status: str, reason: str, approval: dict | None = None) -> dict:
    return {
        "valid": False,
        "status": status,
        "reason": reason,
        "approval": approval,
        "used": bool(approval and approval.get("used")),
    }


def _allowed_roots(value: str) -> list[Path]:
    roots = []
    for raw_root in value.split(","):
        raw_root = raw_root.strip()
        if raw_root:
            roots.append(Path(raw_root).expanduser().resolve())
    return roots or [Path(".").resolve()]


def _root_summaries(value: str) -> list[dict]:
    return [
        {
            "path": str(root),
            "exists": root.exists(),
            "is_dir": root.is_dir(),
        }
        for root in _allowed_roots(value)
    ]


def _csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _intent_endpoint(intent: str) -> str:
    if intent == "ask":
        return "POST /assistant/message"
    if intent == "ask_with_docs":
        return "POST /assistant/message"
    if intent == "search":
        return "POST /assistant/message"
    if intent == "index_preview":
        return "POST /assistant/message"
    if intent == "shell_dry_run":
        return "POST /assistant/message"
    if intent == "agent_plan":
        return "POST /assistant/message"
    return "POST /assistant/message"


def _intent_risk(intent: str) -> str:
    if intent == "agent_plan":
        return "high"
    if intent == "shell_dry_run":
        return "medium"
    if intent == "index_preview":
        return "low"
    return "low"


def _intent_needs(intent: str, project_root: str | None) -> list[str]:
    if intent == "index_preview" and not project_root:
        return ["project_root"]
    return []


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
