from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies import get_assistant_service
from app.main import app
from app.services.project_status_service import build_api_inventory


NOW = datetime(2026, 5, 20, tzinfo=UTC)


class FakeAssistantService:
    def capabilities(self) -> dict:
        return {
            "service": "local-ai-server",
            "modes": ["auto", "ask_with_docs", "search"],
            "protected": True,
            "local_only": True,
            "llm_provider": "ollama-local",
            "vector_store": "chroma-local",
            "storage": "sqlite-local",
            "safe_defaults": {"shell_execution": "disabled"},
            "endpoints": {
                "ping": "GET /assistant/ping",
                "config": "GET /assistant/config",
                "dashboard": "GET /assistant/dashboard",
                "startup": "GET /assistant/startup",
                "ui_contract": "GET /assistant/ui-contract",
                "action_preview": "POST /assistant/action-preview",
                "message": "POST /assistant/message",
            },
        }

    def ui_contract(self):
        return {
            "service": "local-ai-server",
            "version": "1",
            "protected": True,
            "auth": {"supported_headers": ["X-API-Key"], "secret_returned": False},
            "startup_sequence": [{"step": 1, "method": "GET", "path": "/assistant/startup", "purpose": "hydrate"}],
            "refresh_endpoints": [{"method": "GET", "path": "/assistant/ping", "purpose": "check"}],
            "message_flow": [{"step": 1, "method": "POST", "path": "/assistant/message", "purpose": "answer"}],
            "response_types": {"answer": "assistant answer bubble"},
            "safety": {"shell_execution": "disabled"},
            "blocked_actions": ["shell_execution"],
            "notes": ["read-only contract"],
        }

    def startup(self, db):
        return {
            "service": "local-ai-server",
            "protected": True,
            "local_only": True,
            "ping": self.ping(),
            "config": self.config(),
            "dashboard": self.dashboard(db),
            "ui_contract": self.ui_contract(),
            "recommended_calls": [{"method": "POST", "path": "/assistant/bootstrap", "when": "startup"}],
            "safety": {"shell_execution": "disabled"},
            "ui": {"ready": True, "badge": "STARTUP SNAPSHOT READY", "display": "startup_snapshot"},
        }

    def action_preview(self, request):
        intent = request.mode if request.mode != "auto" else "agent_plan"
        return {
            "intent": intent,
            "recommended_endpoint": "POST /assistant/message",
            "would_execute": False,
            "requires_approval": intent == "agent_plan",
            "risk_level": "high" if intent == "agent_plan" else "low",
            "needs": [],
            "safety": {"shell_execution": "disabled"},
            "ui": {"response_type": "action_preview", "severity": "warning", "primary_text": intent, "display": "panel"},
        }

    def action_loop_preflight(self, request):
        return {
            "service": "local-ai-server",
            "mode": "action-loop-dispatch-preflight-locked",
            "status": "blocked",
            "goal": request.goal,
            "would_dispatch": False,
            "execution_enabled": False,
            "fail_closed": True,
            "frozen_plan": {
                "goal": request.goal,
                "steps": request.proposed_steps,
                "mutable": False,
                "plan_hash": "g" * 64,
            },
            "step_previews": [],
            "gates": {
                "dispatch_connected": False,
                "missing_wrapper_fail_closed": False,
                "missing_approval_fail_closed": False,
                "payload_hash_mismatch_fail_closed": False,
            },
            "required_user_decisions": ["dispatch review"],
            "safety": {"action_loop_dispatch": "disabled", "action_loop_preflight": "blocked"},
            "ui": {
                "response_type": "action_loop_preflight",
                "severity": "warning",
                "primary_text": "blocked",
                "display": "panel",
            },
        }

    def action_loop_noop_dispatch(self, request):
        return {
            "service": "local-ai-server",
            "mode": "action-loop-noop-dispatch-preview",
            "status": "blocked",
            "goal": request.goal,
            "would_dispatch": False,
            "would_dispatch_noop_only": False,
            "execution_enabled": False,
            "fail_closed": True,
            "approval_consume_mode": "validate-only",
            "route_plan": [],
            "noop_audit": {
                "schema": "assistant.action_loop.noop_dispatch.v1",
                "payload": {"would_dispatch": False, "execution_enabled": False},
                "payload_hash": "n" * 64,
            },
            "preflight": self.action_loop_preflight(request),
            "gates": {
                "noop_dispatcher": True,
                "real_dispatch_connected": False,
                "tool_execution_connected": False,
                "approval_consume_mode": "validate-only",
                "approval_consumed": False,
            },
            "required_user_decisions": ["dispatch review"],
            "safety": {"action_loop_dispatch": "disabled", "action_loop_preflight": "blocked"},
            "ui": {
                "response_type": "action_loop_noop_dispatch",
                "severity": "warning",
                "primary_text": "blocked",
                "display": "panel",
            },
        }

    def action_loop_read_only_dispatch_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "action-loop-read-only-dispatch-boundary-preview",
            "status": "blocked",
            "goal": request.goal,
            "would_dispatch": False,
            "would_read": False,
            "would_fetch": False,
            "execution_enabled": False,
            "fail_closed": True,
            "boundary_mode": "classification-only",
            "route_plan": [],
            "result_wrapper_schema": {
                "schema": "assistant.action_loop.read_only_result_wrapper.v1",
                "contract_mode": "preview-only",
                "wrapper_required": True,
                "wrapper_untrusted_required": True,
                "raw_content_allowed": False,
                "approval_like_json_trusted": False,
                "can_mutate_frozen_plan": False,
                "can_set_next_action": False,
                "can_request_approval": False,
                "required_fields": ["schema", "source_adapter", "wrapper", "masked_summary"],
                "prohibited_fields": ["raw_content", "approval_id", "next_step"],
                "safety_fields": {
                    "would_dispatch": False,
                    "would_read": False,
                    "would_fetch": False,
                    "execution_enabled": False,
                    "masking_required": True,
                },
            },
            "boundary_audit": {
                "schema": "assistant.action_loop.read_only_boundary_preview.v1",
                "payload": {"would_dispatch": False, "would_read": False, "would_fetch": False},
                "payload_hash": "r" * 64,
            },
            "gates": {
                "read_only_tools_only": True,
                "wrapper_required": True,
                "real_dispatch_connected": False,
                "adapter_execution_connected": False,
                "result_wrapper_required": True,
                "raw_result_content_allowed": False,
                "approval_like_json_trusted": False,
                "file_content_read": False,
                "url_fetch_performed": False,
            },
            "safety": {"action_loop_dispatch": "disabled", "action_loop_preflight": "blocked"},
            "ui": {
                "response_type": "action_loop_read_only_dispatch_preview",
                "severity": "warning",
                "primary_text": "blocked",
                "display": "panel",
            },
        }

    def automation_plan(self, request):
        return {
            "service": "local-ai-server",
            "goal": request.goal,
            "local_only": True,
            "would_execute": False,
            "current_capabilities": [
                {"capability": "local_rag", "status": "ready"},
                {"capability": "shell", "status": "blocked"},
            ],
            "automation_stages": [
                {"stage": 1, "name": "Local knowledge API", "status": "implemented"},
                {"stage": 5, "name": "Shell execution", "status": "review_required"},
            ],
            "codex_safe_now": ["문서/RAG API 계약과 테스트 보강"],
            "blocked_until_review": ["실제 shell 실행", "브라우저 interaction"],
            "required_user_decisions": ["자동화 1차 target 선택"],
            "safety": {"shell_execution": "disabled", "browser_interaction": "blocked"},
            "ui": {
                "response_type": "automation_plan",
                "severity": "warning",
                "primary_text": "plan-only",
                "display": "panel",
            },
            "recommended_next_model": {
                "recommended_ai": "Codex",
                "recommended_model": "Codex GPT-5.5",
                "reason": "safe contract",
                "next_task": "preview/read-only API 확장",
                "user_action_required": "dangerous activation 승인 전 진행 불가",
            },
        }

    def workflow_presets(self):
        return {
            "service": "local-ai-server",
            "mode": "workflow-preset-list-preview",
            "presets": [
                {"id": "project_review", "title": "Project Review", "category": "coding", "steps_count": 2},
                {"id": "ci_preview", "title": "CI Preview", "category": "local-server-maintenance", "steps_count": 1},
            ],
            "would_dispatch": False,
            "execution_enabled": False,
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {"response_type": "workflow_presets", "severity": "info", "primary_text": "presets", "display": "panel"},
        }

    def workflow_preset_detail(self, preset_id):
        return {
            "service": "local-ai-server",
            "mode": "workflow-preset-detail-preview",
            "preset_id": preset_id,
            "status": "available",
            "preset": {"id": preset_id, "title": "Project Review", "category": "coding", "steps_count": 2},
            "would_dispatch": False,
            "execution_enabled": False,
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {
                "response_type": "workflow_preset_detail",
                "severity": "info",
                "primary_text": "available",
                "display": "panel",
            },
        }

    def workflow_preset_preview(self, preset_id, request):
        return {
            "service": "local-ai-server",
            "mode": "workflow-preset-proposed-steps-preview",
            "preset_id": preset_id,
            "status": "proposed_steps_preview",
            "preset": {"id": preset_id, "title": "Project Review", "category": "coding", "steps_count": 1},
            "frozen_proposed_steps": [
                {
                    "tool": "read_only_scan",
                    "params": {"project_root": request.params.get("project_root", "/tmp/project")},
                    "wrapper": {"untrusted": True, "source": "workflow_preset", "preset_id": preset_id},
                    "preview_only": True,
                }
            ],
            "would_dispatch": False,
            "execution_enabled": False,
            "blocked_reasons": [],
            "unsafe_policy": {
                "schema": "assistant.workflow_preset.unsafe_policy.v1",
                "dispatch_connected": False,
                "shell_execution_connected": False,
                "patch_apply_connected": False,
                "browser_interaction_connected": False,
                "external_api_connected": False,
            },
            "audit": {
                "schema": "assistant.workflow_preset.preview.v1",
                "payload_hash": "p" * 64,
                "payload": {"would_dispatch": False, "execution_enabled": False},
            },
            "safety": {"action_loop_dispatch": "proposed_steps_preview"},
            "ui": {
                "response_type": "workflow_preset_preview",
                "severity": "info",
                "primary_text": "proposed_steps_preview",
                "display": "panel",
            },
        }

    def task_queue_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "long-running-queue-locked-preview",
            "status": "queued",
            "task": {
                "task_id": "task-1",
                "task_type": request.task_type,
                "status": "queued",
                "params": request.params,
                "audit_link": {"schema": "assistant.long_running_task.audit_link.v1", "task_id": "task-1"},
                "worker": {
                    "worker_enabled": False,
                    "worker_started": False,
                    "background_loop_created": False,
                    "execution_enabled": False,
                },
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
            },
            "blocked_reasons": [],
            "allowed_task_types": ["noop", "read_only_scan"],
            "would_enqueue": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": {
                "schema": "assistant.long_running_task.audit.v1",
                "payload": {"task_id": "task-1", "would_enqueue": False},
                "payload_hash": "t" * 64,
            },
            "cleanup_policy": {"worker_loop_enabled": False, "ttl_seconds_default": 300},
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {"response_type": "task_queue_preview", "severity": "info", "primary_text": "queued", "display": "panel"},
        }

    def task_queue(self):
        return {
            "service": "local-ai-server",
            "mode": "long-running-queue-list-read-only",
            "tasks": [],
            "statuses": ["queued", "running", "completed", "blocked", "cancelled"],
            "would_execute": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "cleanup_policy": {"worker_loop_enabled": False, "ttl_seconds_default": 300},
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {"response_type": "task_queue", "severity": "info", "primary_text": "list", "display": "panel"},
        }

    def task_queue_drain(self, request):
        return {
            "service": "local-ai-server",
            "mode": "task_queue_worker_disabled",
            "status": "disabled",
            "worker_enabled": False,
            "execution_enabled": False,
            "would_execute": False,
            "drained_count": 0,
            "tasks": [],
            "results": [],
            "blocked_reasons": ["task_queue_worker_disabled"],
            "allowed_task_types": ["noop", "read_only_scan"],
            "worker": {
                "worker_enabled": False,
                "one_shot_drain": True,
                "background_loop_created": False,
                "daemon_started": False,
                "service_installed": False,
            },
            "audit": {
                "schema": "assistant.task_queue.worker_audit.v1",
                "payload": {"requested_limit": request.limit},
                "payload_hash": "w" * 64,
            },
            "cleanup_policy": {"worker_loop_enabled": False, "ttl_seconds_default": 300},
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {"response_type": "task_queue_drain", "severity": "warning", "primary_text": "disabled", "display": "panel"},
        }

    def task_queue_detail(self, task_id):
        return {
            "service": "local-ai-server",
            "mode": "long-running-queue-detail-read-only",
            "task_id": task_id,
            "status": "queued",
            "task": {"task_id": task_id, "status": "queued"},
            "would_execute": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": {
                "schema": "assistant.long_running_task.audit.v1",
                "payload": {"task_id": task_id},
                "payload_hash": "d" * 64,
            },
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {"response_type": "task_queue_detail", "severity": "info", "primary_text": "queued", "display": "panel"},
        }

    def task_queue_cancel_preview(self, task_id):
        return {
            "service": "local-ai-server",
            "mode": "long-running-cancel-locked-preview",
            "task_id": task_id,
            "status": "cancelled",
            "task": {"task_id": task_id, "status": "cancelled"},
            "cancellation": {"requested": True, "cancelled_at": "2026-06-02T00:00:00+00:00", "reason": "preview"},
            "would_cancel_worker": False,
            "worker_enabled": False,
            "execution_enabled": False,
            "audit": {
                "schema": "assistant.long_running_task.audit.v1",
                "payload": {"task_id": task_id},
                "payload_hash": "c" * 64,
            },
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {
                "response_type": "task_queue_cancel_preview",
                "severity": "info",
                "primary_text": "cancelled",
                "display": "panel",
            },
        }

    def failure_recovery_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "failure-recovery-rollback-locked-preview",
            "tool": request.tool,
            "status": "rollback_preview" if request.tool == "patch" else "manual_instruction_only",
            "failure": {
                "schema": "assistant.failure_reason.taxonomy.v1",
                "tool": request.tool,
                "reason": request.failure_reason,
                "known_reasons": ["hash_mismatch"],
                "summary": request.summary or "",
                "params": request.params,
            },
            "rollback_plan": {
                "schema": f"assistant.rollback_plan.{request.tool}.v1",
                "type": "patch_rollback_preview" if request.tool == "patch" else "manual_instruction_only",
                "original_sha256": request.original_sha256 or "missing_original_sha256",
                "would_apply": False,
                "rollback_enabled": False,
                "automatic_execution": False,
            },
            "manual_instructions": ["자동 rollback 실행은 비활성입니다."],
            "paste_safe_summary": "Failure recovery preview: automatic_execution=false.",
            "would_execute": False,
            "would_apply": False,
            "would_interact": False,
            "rollback_enabled": False,
            "execution_enabled": False,
            "audit": {
                "schema": "assistant.failure_recovery.preview.v1",
                "payload": {"would_execute": False, "would_apply": False, "would_interact": False},
                "payload_hash": "r" * 64,
            },
            "safety": {"action_loop_dispatch": "disabled"},
            "ui": {
                "response_type": "failure_recovery_preview",
                "severity": "warning",
                "primary_text": "failure recovery preview only",
                "display": "panel",
            },
        }

    def rollback_approval_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "rollback-approval-binding-preview",
            "status": "approval_required",
            "approval_required": True,
            "rollback_enabled": False,
            "would_apply": False,
            "binding": {
                "approval_id": "approval-1",
                "payload_hash": "k" * 64,
                "approval_scope": "single-file-rollback-preview-only",
                "server_issued": True,
                "single_use": True,
            },
            "preview": {
                "status": "allowed_preview",
                "allowed": True,
                "resolved_path": request.path,
                "audit": {"payload_hash": "k" * 64},
            },
            "blocked_reasons": [],
            "safety": {"action_loop_dispatch": "disabled", "rollback_executor": "disabled"},
            "ui": {
                "response_type": "rollback_approval_preview",
                "severity": "warning",
                "primary_text": "rollback approval preview only",
                "display": "panel",
            },
        }

    def rollback_execute(self, request):
        return {
            "service": "local-ai-server",
            "mode": "rollback-executor-locked",
            "status": "disabled",
            "rollback_enabled": False,
            "execution_enabled": False,
            "would_apply": False,
            "reason": "ROLLBACK_EXECUTOR_ENABLED=false",
            "preview": {
                "status": "allowed_preview",
                "allowed": True,
                "resolved_path": request.path,
                "audit": {"payload_hash": request.approval_payload_hash or "k" * 64},
            },
            "blocked_reasons": [],
            "required_approval_hash": request.approval_payload_hash,
            "provided_approval_id": request.approval_id,
            "provided_approval_hash": request.approval_payload_hash,
            "approval_check": {"status": "valid_consumed", "valid": True},
            "rollback_result": None,
            "result_wrapper": {
                "schema": "assistant.rollback_execute.result_wrapper.v1",
                "untrusted": True,
                "paste_safe": True,
            },
            "audit": {"schema": "assistant.rollback_execute.v1", "payload": {}, "payload_hash": "k" * 64},
            "safety": {"action_loop_dispatch": "disabled", "rollback_executor": "disabled"},
            "ui": {"response_type": "rollback_execute", "severity": "warning", "primary_text": "disabled", "display": "panel"},
        }

    def read_only_scan(self, request):
        return {
            "service": "local-ai-server",
            "project_root": request.project_root,
            "resolved_path": request.project_root,
            "mode": "read-only",
            "would_execute": False,
            "summary": {"status": "completed", "files_count": 1, "dirs_count": 1},
            "important_files": [{"name": "README.md", "exists": True, "type": "file", "path": f"{request.project_root}/README.md"}],
            "top_level_items": [{"name": "README.md", "type": "file", "extension": ".md"}],
            "extension_counts": {".md": 1},
            "safety": {"shell_execution": "disabled", "browser_interaction": "blocked"},
            "ui": {"response_type": "read_only_scan", "severity": "info", "primary_text": "scan", "display": "panel"},
        }

    def file_preview(self, request):
        return {
            "service": "local-ai-server",
            "path": request.path,
            "resolved_path": request.path,
            "mode": "read-only",
            "status": "completed",
            "would_execute": False,
            "metadata": {"filename": "README.md", "size_bytes": 10},
            "content_preview": "# Demo",
            "truncated": False,
            "masked": False,
            "safety": {"shell_execution": "disabled", "file_write_delete": "blocked"},
            "ui": {"response_type": "file_preview", "severity": "info", "primary_text": "file", "display": "panel"},
        }

    def url_preview(self, request):
        return {
            "service": "local-ai-server",
            "url": request.url,
            "mode": "read-only-url-preflight",
            "status": "disabled",
            "would_fetch": False,
            "reason": "disabled",
            "safety": {"browser_interaction": "blocked"},
            "ui": {"response_type": "url_preview", "severity": "warning", "primary_text": "disabled", "display": "panel"},
        }

    def web_search_provider_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "external-web-search-provider-gate-preview",
            "status": "provider_not_configured",
            "provider": request.provider,
            "query_preview": request.query,
            "would_search": False,
            "would_fetch": False,
            "external_api_enabled": False,
            "provider_config": {
                "schema": "assistant.web_search.provider_config.v1",
                "configured": False,
                "provider": request.provider,
                "external_api_enabled": False,
                "api_key_configured": False,
                "paid_provider_enabled": False,
            },
            "gate": {
                "schema": "assistant.web_search.provider_gate.v1",
                "contract_mode": "locked-preview",
                "provider_not_configured": True,
                "external_api_enabled": False,
                "would_search": False,
                "would_fetch": False,
                "external_call_performed": False,
                "network_request_performed": False,
                "result_wrapper_untrusted_required": True,
            },
            "result_wrapper": {
                "schema": "assistant.web_search.result_wrapper.v1",
                "required": True,
                "provided": True,
                "untrusted": True,
                "valid": True,
                "raw_content_allowed": False,
                "approval_like_json_trusted": False,
                "execution_enabled": False,
            },
            "audit": {
                "schema": "assistant.web_search.provider_gate.preview.v1",
                "payload_hash": "w" * 64,
                "payload": {"would_search": False, "would_fetch": False},
            },
            "safety": {"external_web_search": "provider_not_configured", "external_api_enabled": False},
            "ui": {
                "response_type": "web_search_provider_preview",
                "severity": "warning",
                "primary_text": "provider_not_configured",
                "display": "panel",
            },
        }

    def app_os_interaction_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "app-os-interaction-gate-preview",
            "status": "observe_plan_candidate",
            "action": request.action,
            "app_name": request.app_name,
            "window_title": request.window_title,
            "target_path": request.target_path,
            "allowed": False,
            "observe_plan_candidate": True,
            "would_control_app": False,
            "os_action_executed": False,
            "reason": "observe-plan candidate only",
            "taxonomy": {
                "allowed_actions": [],
                "observe_plan_actions": ["observe", "observe-plan", "status"],
                "blocked_actions": ["open", "click", "type", "hotkey", "file_dialog"],
            },
            "permission_model": {
                "schema": "assistant.app_os.permission_model.v1",
                "os_control_enabled": False,
                "blocked_permissions": ["app_open", "mouse_click", "keyboard_type", "hotkey", "file_dialog"],
            },
            "approval_binding": {
                "schema": "assistant.app_os.approval_binding_design.v1",
                "designed_only": True,
                "approval_store": "not-created",
                "payload_hash": "o" * 64,
            },
            "gate": {
                "schema": "assistant.app_os.interaction_gate.v1",
                "contract_mode": "locked-preview",
                "allowed": False,
                "observe_plan_candidate": True,
                "app_os_control_enabled": False,
                "would_control_app": False,
                "os_action_executed": False,
                "computer_use_connected": False,
                "applescript_connected": False,
                "osascript_connected": False,
                "open_command_connected": False,
            },
            "audit": {
                "schema": "assistant.app_os.interaction_gate.preview.v1",
                "payload_hash": "o" * 64,
                "payload": {"would_control_app": False, "os_action_executed": False},
            },
            "safety": {"app_os_control": "observe_plan_candidate", "os_action_execution": "disabled"},
            "ui": {
                "response_type": "app_os_interaction_preview",
                "severity": "warning",
                "primary_text": "observe_plan_candidate",
                "display": "panel",
            },
        }

    def workspace_brief(self, request):
        return {
            "service": "local-ai-server",
            "project_root": request.project_root,
            "mode": "read-only-workspace-brief",
            "would_execute": False,
            "scan": self.read_only_scan(request),
            "previews": [{"path": "README.md", "status": "completed", "metadata": {}, "content_preview": "# Demo", "truncated": False, "masked": False}],
            "next_safe_actions": ["file preview"],
            "safety": {"shell_execution": "disabled", "file_write_delete": "blocked"},
            "ui": {"response_type": "workspace_brief", "severity": "info", "primary_text": "brief", "display": "panel"},
        }

    def shell_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "shell-sandbox-preview",
            "command_preview": request.command,
            "cwd": request.cwd,
            "resolved_cwd": request.cwd,
            "status": "allowed_preview",
            "would_execute": False,
            "allowed": True,
            "reason": "preview only",
            "timeout_seconds": request.timeout_seconds,
            "policy": {"allowlist": {"exact": ["git status"]}},
            "audit": {"schema": "assistant.shell_sandbox.preview.v1", "payload_hash": "a" * 64, "payload": {}},
            "output_preview": {"stdout": "", "stderr": "", "truncated": False},
            "safety": {"shell_execution": "disabled", "shell_sandbox_execution": "locked"},
            "ui": {"response_type": "shell_preview", "severity": "info", "primary_text": "allowed", "display": "panel"},
        }

    def shell_approval_preview(self, request):
        preview = self.shell_preview(request)
        return {
            "service": "local-ai-server",
            "mode": "shell-approval-binding-preview",
            "status": "approval_required",
            "approval_required": True,
            "would_execute": False,
            "binding": {
                "payload_hash": "b" * 64,
                "approval_scope": "single-command-preview-only",
                "store": "not-created",
            },
            "preview": preview,
            "safety": {"shell_execution": "disabled", "shell_sandbox_execution": "locked"},
            "ui": {
                "response_type": "shell_approval_preview",
                "severity": "warning",
                "primary_text": "approval preview only",
                "display": "panel",
            },
        }

    def approval_console_pending(self):
        return {
            "service": "local-ai-server",
            "mode": "approval-console-read-only",
            "status": "completed",
            "approvals": [
                {
                    "approval_ref": "approval-ref:abc123",
                    "tool_name": "shell",
                    "scope": "single-command-preview-only",
                    "console_state": "pending",
                    "raw_approval_id_included": False,
                    "payload_hash_included": False,
                }
            ],
            "count": 1,
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": {
                "approve_endpoint_connected": False,
                "reject_endpoint_connected": False,
                "action_loop_full_dispatch_connected": False,
                "browser_actual_interaction_connected": False,
                "app_os_actual_action_connected": False,
            },
            "audit": {
                "schema": "assistant.approval_console.read_only.v1",
                "audit_summary_hash": "c" * 64,
                "raw_approval_id_included": False,
                "payload_hash_included": False,
            },
            "safety": {"action_loop_dispatch": "disabled", "browser_interaction": "blocked"},
            "ui": {"response_type": "approval_console_pending", "severity": "info", "primary_text": "read-only approval console", "display": "panel"},
        }

    def approval_console_detail(self, approval_id):
        return {
            "service": "local-ai-server",
            "mode": "approval-console-read-only",
            "status": "completed",
            "approval": {
                "approval_ref": "approval-ref:abc123",
                "tool_name": "shell",
                "scope": "single-command-preview-only",
                "console_state": "pending",
                "raw_approval_id_included": False,
                "payload_hash_included": False,
            },
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": {
                "approve_endpoint_connected": False,
                "reject_endpoint_connected": False,
                "action_loop_full_dispatch_connected": False,
                "browser_actual_interaction_connected": False,
                "app_os_actual_action_connected": False,
            },
            "audit": {
                "schema": "assistant.approval_console.read_only.v1",
                "audit_summary_hash": "d" * 64,
                "raw_approval_id_included": False,
                "payload_hash_included": False,
            },
            "safety": {"action_loop_dispatch": "disabled", "browser_interaction": "blocked"},
            "ui": {"response_type": "approval_console_detail", "severity": "info", "primary_text": "completed", "display": "panel"},
        }

    def approval_console_cleanup_expired(self):
        return {
            "service": "local-ai-server",
            "mode": "approval-console-read-only",
            "status": "cleaned",
            "cleanup": {
                "schema": "assistant.approval_store.expiry_cleanup.v1",
                "status": "cleaned",
                "expired_count": 1,
                "records_removed": 1,
                "state_only": True,
                "execution_triggered": False,
                "approval_consumed": False,
                "raw_approval_id_included": False,
                "payload_hash_included": False,
                "paste_safe_summary": "approval-store-expiry-cleanup completed",
            },
            "read_only": True,
            "would_execute": False,
            "approval_consumed": False,
            "gates": {
                "approve_endpoint_connected": False,
                "reject_endpoint_connected": False,
                "action_loop_full_dispatch_connected": False,
                "browser_actual_interaction_connected": False,
                "app_os_actual_action_connected": False,
            },
            "audit": {
                "schema": "assistant.approval_console.read_only.v1",
                "audit_summary_hash": "e" * 64,
                "raw_approval_id_included": False,
                "payload_hash_included": False,
            },
            "safety": {"action_loop_dispatch": "disabled", "browser_interaction": "blocked"},
            "ui": {"response_type": "approval_console_cleanup_expired", "severity": "info", "primary_text": "cleaned", "display": "panel"},
        }

    def durable_state_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "durable-state-preview-read-only",
            "status": "completed",
            "preview_state": {
                "state_schema_version": "durable_state_preview.v1",
                "preview_state_id": "preview-state:abc123",
                "state_status": "candidate-preview",
                "owner_session_ref": "session-ref:abc123",
                "request_context_ref": "request-ref:abc123",
                "plan_ref": "plan-ref:abc123",
                "payload_hash_ref": "payload-hash-ref:abc123",
                "masked_params": {"goal": request.goal, "metadata": {}},
                "candidate_steps_count": len(request.proposed_steps),
                "manual_review_required": True,
                "stop_on_first_blocked": True,
            },
            "candidate_steps": request.proposed_steps,
            "read_only": True,
            "schema_only": True,
            "response_only": True,
            "would_execute": False,
            "would_persist": False,
            "would_dispatch": False,
            "approval_consumed": False,
            "gates": {
                "endpoint_surface": "response-only-read-only-schema-only",
                "protected_endpoint_only": True,
                "stored_preview_lookup_connected": False,
                "stored_preview_list_connected": False,
                "stored_preview_cleanup_connected": False,
                "durable_storage_migration_connected": False,
                "durable_table_created": False,
                "approval_consumed": False,
                "would_execute": False,
                "would_persist": False,
                "would_dispatch": False,
                "action_loop_full_dispatch_connected": False,
                "browser_actual_interaction_connected": False,
                "app_os_actual_action_connected": False,
            },
            "audit": {
                "schema": "assistant.durable_state_preview.read_only.v1",
                "audit_summary_hash": "f" * 64,
                "raw_approval_id_included": False,
                "payload_hash_included": False,
            },
            "blocked_reasons": [],
            "required_user_decisions": ["stored preview lookup/list/cleanup endpoints remain Decision Required"],
            "safety": {"durable_state_preview": "read-only-schema-only"},
            "ui": {"response_type": "durable_state_preview", "severity": "info", "primary_text": "read-only durable state preview", "display": "panel"},
        }

    def shell_run(self, request):
        return {
            "service": "local-ai-server",
            "mode": "shell-run-locked",
            "status": "locked",
            "would_execute": False,
            "execution_enabled": False,
            "reason": "locked",
            "preview": self.shell_preview(request),
            "required_approval_hash": "a" * 64,
            "provided_approval_hash": request.approval_payload_hash,
            "safety": {"shell_execution": "disabled", "shell_sandbox_execution": "locked"},
            "ui": {
                "response_type": "shell_run_locked",
                "severity": "warning",
                "primary_text": "locked",
                "display": "panel",
            },
        }

    def patch_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "patch-preview-locked",
            "path": request.path,
            "resolved_path": request.path,
            "status": "allowed_preview",
            "would_apply": False,
            "allowed": True,
            "reason": "preview only",
            "diff_preview": "--- a/note.md\n+++ b/note.md\n",
            "truncated": False,
            "secret_scan": {"has_secret_like_value": False, "findings_count": 0},
            "rollback": {"available": True, "note": "manual rollback"},
            "audit": {"schema": "assistant.patch_preview.v1", "payload_hash": "c" * 64, "payload": {}},
            "safety": {"file_write_delete": "blocked", "patch_apply": "allowed_preview"},
            "ui": {"response_type": "patch_preview", "severity": "info", "primary_text": "allowed", "display": "panel"},
        }

    def patch_approval_preview(self, request):
        preview = self.patch_preview(request)
        return {
            "service": "local-ai-server",
            "mode": "patch-approval-binding-preview",
            "status": "approval_required",
            "approval_required": True,
            "would_apply": False,
            "binding": {
                "payload_hash": "d" * 64,
                "approval_scope": "single-file-patch-preview-only",
                "store": "not-created",
            },
            "preview": preview,
            "safety": {"file_write_delete": "blocked", "patch_apply": "allowed_preview"},
            "ui": {
                "response_type": "patch_approval_preview",
                "severity": "warning",
                "primary_text": "patch approval preview only",
                "display": "panel",
            },
        }

    def patch_apply(self, request):
        return {
            "service": "local-ai-server",
            "mode": "patch-apply-locked",
            "status": "locked",
            "would_apply": False,
            "execution_enabled": False,
            "reason": "locked",
            "preview": self.patch_preview(request),
            "required_approval_hash": "c" * 64,
            "provided_approval_hash": request.approval_payload_hash,
            "safety": {"file_write_delete": "blocked", "patch_apply": "locked"},
            "ui": {
                "response_type": "patch_apply_locked",
                "severity": "warning",
                "primary_text": "locked",
                "display": "panel",
            },
        }

    def browser_preview(self, request):
        return {
            "service": "local-ai-server",
            "mode": "browser-interaction-preview-locked",
            "status": "allowed_preview",
            "action": request.action,
            "target_url": request.target_url,
            "app_name": request.app_name,
            "would_interact": False,
            "allowed": True,
            "reason": "preview only",
            "risk": "low",
            "required_manual_confirmation": True,
            "taxonomy": {"blocked_actions": ["click", "fill", "submit", "login", "payment", "delete"]},
            "gate": {
                "schema": "assistant.browser_interaction.gate.v1",
                "contract_mode": "locked-preview",
                "execution_enabled": False,
                "launch_enabled": False,
                "would_interact": False,
                "browser_launch": "not_performed",
                "domain_allowlist_candidate": {"mode": "design-only", "enforced": False, "configured_domains": []},
            },
            "audit": {"schema": "assistant.browser_interaction.preview.v1", "payload_hash": "e" * 64, "payload": {}},
            "safety": {"browser_interaction": "blocked", "browser_interaction_preview": "allowed_preview"},
            "ui": {"response_type": "browser_preview", "severity": "info", "primary_text": "allowed", "display": "panel"},
        }

    def browser_approval_preview(self, request):
        preview = self.browser_preview(request)
        return {
            "service": "local-ai-server",
            "mode": "browser-approval-binding-preview",
            "status": "approval_required",
            "approval_required": True,
            "would_interact": False,
            "binding": {
                "payload_hash": "f" * 64,
                "approval_scope": "single-browser-preview-only",
                "store": "not-created",
            },
            "preview": preview,
            "safety": {"browser_interaction": "blocked", "browser_interaction_preview": "allowed_preview"},
            "ui": {
                "response_type": "browser_approval_preview",
                "severity": "warning",
                "primary_text": "browser approval preview only",
                "display": "panel",
            },
        }

    def browser_interact(self, request):
        return {
            "service": "local-ai-server",
            "mode": "browser-interact-locked",
            "status": "locked",
            "would_interact": False,
            "execution_enabled": False,
            "reason": "locked",
            "preview": self.browser_preview(request),
            "required_approval_hash": "e" * 64,
            "provided_approval_hash": request.approval_payload_hash,
            "safety": {"browser_interaction": "blocked", "browser_interaction_preview": "locked"},
            "ui": {
                "response_type": "browser_interact_locked",
                "severity": "warning",
                "primary_text": "locked",
                "display": "panel",
            },
        }

    def ping(self):
        return {
            "status": "ok",
            "service": "local-ai-server",
            "protected": True,
            "local_only": True,
            "ui_ready": True,
        }

    def config(self):
        return {
            "service": "local-ai-server",
            "protected": True,
            "local_only": True,
            "cors_origins": ["http://127.0.0.1:5173"],
            "allowed_roots": [{"path": "/tmp/project", "exists": True, "is_dir": True}],
            "models": {"llm_provider": "ollama-local", "llm_model": "llama3.2", "embedding_model": "nomic-embed-text"},
            "storage": {"database": "sqlite-local", "vector_store": "chroma-local"},
            "safety": {"shell_execution": "disabled"},
            "rate_limit": {"enabled": True, "per_minute": 120},
        }

    def status(self, db):
        return {
            "service": "local-ai-server",
            "current_phase": {"phase": 15, "title": "Live browser UI QA", "status": "next", "summary": "qa"},
            "documents": {
                "documents_count": 1,
                "chunks_count": 2,
                "chroma_vectors_count": 2,
                "missing_stored_files_count": 0,
            },
            "integrity": {
                "status": "ok",
                "chunks_missing_vectors_count": 0,
                "orphan_vectors_count": 0,
                "repair_available": False,
            },
            "sessions": {"sessions_count": 1, "messages_count": 2},
            "safety": {"shell_execution": "disabled"},
        }

    def dashboard(self, db):
        return {
            "service": "local-ai-server",
            "current_phase": self.status(db)["current_phase"],
            "cards": {
                "documents": self.status(db)["documents"],
                "integrity": self.status(db)["integrity"],
                "sessions": self.status(db)["sessions"],
                "connection": {"status": "ready", "protected": True, "local_only": True},
            },
            "recent_sessions": self.list_sessions(db, limit=5, offset=0)["sessions"],
            "safety": {"shell_execution": "disabled"},
            "ui": {"ready": True, "badge": "DASHBOARD READY"},
        }

    def bootstrap(self, db, project_root=None, include_sessions=True, sessions_limit=10):
        return {
            "service": "local-ai-server",
            "capabilities": self.capabilities(),
            "status": self.status(db),
            "project_root": {
                "project_root": project_root,
                "resolved_path": project_root,
                "safe_for_read_only_agent": True,
            }
            if project_root
            else None,
            "sessions": self.list_sessions(db, limit=sessions_limit, offset=0) if include_sessions else None,
            "recommended_calls": [
                {"method": "POST", "path": "/assistant/message", "when": "user sends a message"}
            ],
            "ui": {
                "ready": True,
                "badge": "LOCAL API READY",
                "message": "로컬 assistant API가 준비되었습니다.",
                "blocked_actions": ["shell_execution", "browser_interaction"],
            },
        }

    def create_session(self, db, title=None, project_root=None):
        return SimpleNamespace(
            id="session-1",
            title=title or "New local assistant session",
            project_root=project_root,
            created_at=NOW,
            updated_at=NOW,
            messages=[],
        )

    def list_sessions(self, db, limit: int = 20, offset: int = 0):
        return {
            "sessions": [
                {
                    "session_id": "session-1",
                    "title": "Demo",
                    "project_root": "/tmp/project",
                    "created_at": NOW,
                    "updated_at": NOW,
                    "messages_count": 1,
                    "last_message_preview": "JWT",
                }
            ],
            "limit": limit,
            "offset": offset,
        }

    def _session(self):
        return SimpleNamespace(
            id="session-1",
            title="Demo",
            project_root="/tmp/project",
            created_at=NOW,
            updated_at=NOW,
            messages=[
                SimpleNamespace(
                    id=1,
                    role="user",
                    content="JWT",
                    message_type="input",
                    payload_json=None,
                    created_at=NOW,
                )
            ],
        )

    def get_session(self, db, session_id: str):
        if session_id != "session-1":
            return None
        return self._session()

    def list_session_messages(self, db, session_id: str, limit: int = 50, offset: int = 0):
        if session_id != "session-1":
            return None
        messages = self._session().messages[offset : offset + limit]
        return {
            "session_id": session_id,
            "total_messages": 1,
            "limit": limit,
            "offset": offset,
            "messages": [
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "message_type": message.message_type,
                    "payload": None,
                    "created_at": message.created_at,
                }
                for message in messages
            ],
        }

    async def handle_message(self, db, request):
        return {
            "session_id": request.session_id or "session-1",
            "type": "answer",
            "answer": f"assistant: {request.message}",
            "used_documents": True,
            "sources": [{"document_id": 1, "filename": "note.md", "chunk_index": 0, "chunk_id": 3}],
            "request_id": "123",
            "safety": {
                "shell_execution": "disabled",
                "browser_interaction": "blocked",
                "file_write_delete": "blocked",
            },
            "ui": {"response_type": "answer", "severity": "info", "primary_text": "assistant", "display": "message"},
        }

    def validate_project_root(self, request):
        return {
            "project_root": request.project_root,
            "resolved_path": request.project_root,
            "exists": True,
            "is_dir": True,
            "inside_allowed_roots": True,
            "allowed_roots": [request.project_root],
            "safe_for_read_only_agent": True,
            "message": "read-only agent root로 사용할 수 있습니다.",
        }


def test_assistant_capabilities_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/capabilities")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["llm_provider"] == "ollama-local"
    assert response.json()["safe_defaults"]["shell_execution"] == "disabled"


def test_assistant_action_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/action-preview", json={"message": "브라우저 열어줘", "mode": "auto"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "agent_plan"
    assert body["would_execute"] is False
    assert body["requires_approval"] is True
    assert body["ui"]["response_type"] == "action_preview"


def test_stage8_action_loop_preflight_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/action-loop-preflight",
        json={"goal": "safe dispatch preflight", "proposed_steps": []},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["would_dispatch"] is False
    assert body["execution_enabled"] is False
    assert body["fail_closed"] is True
    assert body["gates"]["dispatch_connected"] is False


def test_stage10_action_loop_noop_dispatch_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/action-loop-noop-dispatch",
        json={"goal": "safe noop dispatch", "proposed_steps": []},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["would_dispatch"] is False
    assert body["would_dispatch_noop_only"] is False
    assert body["execution_enabled"] is False
    assert body["approval_consume_mode"] == "validate-only"
    assert body["gates"]["real_dispatch_connected"] is False
    assert body["gates"]["approval_consumed"] is False


def test_stage11_action_loop_read_only_dispatch_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/action-loop-read-only-dispatch-preview",
        json={"goal": "safe read-only boundary", "proposed_steps": []},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["would_dispatch"] is False
    assert body["would_read"] is False
    assert body["would_fetch"] is False
    assert body["execution_enabled"] is False
    assert body["boundary_mode"] == "classification-only"
    assert body["gates"]["adapter_execution_connected"] is False


def test_stage13_action_loop_read_only_dispatch_preview_exposes_result_wrapper_schema_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/action-loop-read-only-dispatch-preview",
        json={"goal": "safe read-only result wrapper", "proposed_steps": []},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["result_wrapper_schema"]["schema"] == "assistant.action_loop.read_only_result_wrapper.v1"
    assert body["result_wrapper_schema"]["contract_mode"] == "preview-only"
    assert body["result_wrapper_schema"]["raw_content_allowed"] is False
    assert body["result_wrapper_schema"]["approval_like_json_trusted"] is False
    assert body["result_wrapper_schema"]["can_mutate_frozen_plan"] is False
    assert body["would_dispatch"] is False
    assert body["would_read"] is False
    assert body["would_fetch"] is False
    assert body["execution_enabled"] is False


def test_assistant_automation_plan_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/automation-plan", json={"goal": "내 개인 API 자동화"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["goal"] == "내 개인 API 자동화"
    assert body["would_execute"] is False
    assert body["local_only"] is True
    assert body["ui"]["response_type"] == "automation_plan"
    assert "실제 shell 실행" in body["blocked_until_review"]


def test_stage21_workflow_preset_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    listing = client.get("/assistant/workflow-presets")
    detail = client.get("/assistant/workflow-presets/project_review")
    preview = client.post(
        "/assistant/workflow-presets/project_review/preview",
        json={"params": {"project_root": "/tmp/project"}},
    )

    app.dependency_overrides.clear()
    assert listing.status_code == 200
    assert listing.json()["would_dispatch"] is False
    assert listing.json()["execution_enabled"] is False
    assert detail.status_code == 200
    assert detail.json()["preset_id"] == "project_review"
    assert preview.status_code == 200
    body = preview.json()
    assert body["status"] == "proposed_steps_preview"
    assert body["would_dispatch"] is False
    assert body["execution_enabled"] is False
    assert body["frozen_proposed_steps"][0]["wrapper"]["untrusted"] is True


def test_stage22_task_queue_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    created = client.post("/assistant/task-queue/preview", json={"task_type": "noop", "params": {"note": "plan"}})
    listing = client.get("/assistant/task-queue")
    drained = client.post("/assistant/task-queue/drain", json={"limit": 1})
    detail = client.get("/assistant/task-queue/task-1")
    cancelled = client.post("/assistant/task-queue/task-1/cancel-preview")

    app.dependency_overrides.clear()
    assert created.status_code == 200
    assert created.json()["status"] == "queued"
    assert created.json()["would_enqueue"] is False
    assert created.json()["worker_enabled"] is False
    assert created.json()["execution_enabled"] is False
    assert listing.status_code == 200
    assert listing.json()["would_execute"] is False
    assert drained.status_code == 200
    assert drained.json()["status"] == "disabled"
    assert drained.json()["worker"]["daemon_started"] is False
    assert detail.status_code == 200
    assert detail.json()["worker_enabled"] is False
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert cancelled.json()["would_cancel_worker"] is False


def test_stage23_failure_recovery_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/failure-recovery-preview",
        json={"tool": "patch", "failure_reason": "hash_mismatch", "original_sha256": "a" * 64},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rollback_preview"
    assert body["rollback_plan"]["original_sha256"] == "a" * 64
    assert body["would_execute"] is False
    assert body["would_apply"] is False
    assert body["would_interact"] is False
    assert body["rollback_enabled"] is False
    assert body["execution_enabled"] is False


def test_stage35_rollback_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)
    payload = {
        "path": "/tmp/project/a.md",
        "restored_content": "old\n",
        "current_sha256": "a" * 64,
        "original_sha256": "b" * 64,
        "session_id": "s1",
    }

    approval = client.post("/assistant/rollback-approval-preview", json=payload)
    execute = client.post(
        "/assistant/rollback-execute",
        json={**payload, "approval_id": "approval-1", "approval_payload_hash": "k" * 64},
    )

    app.dependency_overrides.clear()
    assert approval.status_code == 200
    assert approval.json()["status"] == "approval_required"
    assert approval.json()["would_apply"] is False
    assert execute.status_code == 200
    assert execute.json()["status"] == "disabled"
    assert execute.json()["result_wrapper"]["untrusted"] is True


def test_stage4_read_only_automation_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    scan = client.post("/assistant/read-only-scan", json={"project_root": "/tmp/project"})
    file_preview = client.post("/assistant/file-preview", json={"path": "/tmp/project/README.md", "project_root": "/tmp/project"})
    url_preview = client.post("/assistant/url-preview", json={"url": "https://example.com"})
    brief = client.post("/assistant/workspace-brief", json={"project_root": "/tmp/project"})

    app.dependency_overrides.clear()
    assert scan.status_code == 200
    assert scan.json()["would_execute"] is False
    assert file_preview.status_code == 200
    assert file_preview.json()["status"] == "completed"
    assert url_preview.status_code == 200
    assert url_preview.json()["would_fetch"] is False
    assert brief.status_code == 200
    assert brief.json()["ui"]["response_type"] == "workspace_brief"


def test_stage19_web_search_provider_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/web-search-provider-preview",
        json={"query": "latest FastAPI release notes", "provider": "brave", "result_wrapper": {"untrusted": True}},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "provider_not_configured"
    assert body["external_api_enabled"] is False
    assert body["would_search"] is False
    assert body["would_fetch"] is False
    assert body["gate"]["schema"] == "assistant.web_search.provider_gate.v1"
    assert body["gate"]["external_call_performed"] is False


def test_stage20_app_os_interaction_preview_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/app-os-interaction-preview",
        json={"action": "observe-plan", "app_name": "Preview", "window_title": "Status"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "observe_plan_candidate"
    assert body["allowed"] is False
    assert body["would_control_app"] is False
    assert body["os_action_executed"] is False
    assert body["gate"]["schema"] == "assistant.app_os.interaction_gate.v1"
    assert body["gate"]["computer_use_connected"] is False


def test_stage5_shell_sandbox_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    preview = client.post("/assistant/shell-preview", json={"command": "git status", "cwd": "/tmp/project"})
    approval = client.post(
        "/assistant/shell-approval-preview",
        json={"command": "git status", "cwd": "/tmp/project", "reason": "local CI"},
    )
    run = client.post("/assistant/shell-run", json={"command": "git status", "cwd": "/tmp/project"})

    app.dependency_overrides.clear()
    assert preview.status_code == 200
    assert preview.json()["would_execute"] is False
    assert preview.json()["status"] == "allowed_preview"
    assert approval.status_code == 200
    assert approval.json()["binding"]["store"] == "not-created"
    assert run.status_code == 200
    assert run.json()["status"] == "locked"
    assert run.json()["execution_enabled"] is False


def test_stage6_patch_sandbox_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    preview = client.post(
        "/assistant/patch-preview",
        json={"path": "/tmp/project/note.md", "proposed_content": "hello\n", "project_root": "/tmp/project"},
    )
    approval = client.post(
        "/assistant/patch-approval-preview",
        json={
            "path": "/tmp/project/note.md",
            "proposed_content": "hello\n",
            "project_root": "/tmp/project",
            "reason": "docs",
        },
    )
    apply = client.post(
        "/assistant/patch-apply",
        json={"path": "/tmp/project/note.md", "proposed_content": "hello\n", "project_root": "/tmp/project"},
    )

    app.dependency_overrides.clear()
    assert preview.status_code == 200
    assert preview.json()["would_apply"] is False
    assert preview.json()["status"] == "allowed_preview"
    assert approval.status_code == 200
    assert approval.json()["binding"]["store"] == "not-created"
    assert apply.status_code == 200
    assert apply.json()["status"] == "locked"
    assert apply.json()["execution_enabled"] is False


def test_stage7_browser_sandbox_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    preview = client.post(
        "/assistant/browser-preview",
        json={"action": "observe", "target_url": "https://example.com"},
    )
    approval = client.post(
        "/assistant/browser-approval-preview",
        json={"action": "screenshot", "target_url": "https://example.com", "reason": "read-only QA"},
    )
    interact = client.post(
        "/assistant/browser-interact",
        json={"action": "observe", "target_url": "https://example.com"},
    )

    app.dependency_overrides.clear()
    assert preview.status_code == 200
    assert preview.json()["would_interact"] is False
    assert preview.json()["status"] == "allowed_preview"
    assert preview.json()["gate"]["schema"] == "assistant.browser_interaction.gate.v1"
    assert preview.json()["gate"]["execution_enabled"] is False
    assert preview.json()["gate"]["browser_launch"] == "not_performed"
    assert approval.status_code == 200
    assert approval.json()["binding"]["store"] == "not-created"
    assert interact.status_code == 200
    assert interact.json()["status"] == "locked"
    assert interact.json()["execution_enabled"] is False


def test_assistant_ui_contract_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/ui-contract")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["auth"]["secret_returned"] is False
    assert body["startup_sequence"][0]["path"] == "/assistant/startup"
    assert body["refresh_endpoints"][0]["path"] == "/assistant/ping"
    assert "shell_execution" in body["blocked_actions"]


def test_assistant_startup_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/startup")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["ping"]["status"] == "ok"
    assert body["config"]["protected"] is True
    assert body["dashboard"]["cards"]["connection"]["status"] == "ready"
    assert body["ui_contract"]["auth"]["secret_returned"] is False
    assert body["ui_contract"]["startup_sequence"][0]["path"] == "/assistant/startup"
    assert body["ui"]["display"] == "startup_snapshot"


def test_assistant_ping_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/ping")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ui_ready"] is True


def test_assistant_config_endpoint_with_mock_does_not_return_secret() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/config")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["protected"] is True
    assert "local_api_key" not in body
    assert body["allowed_roots"][0]["exists"] is True


def test_assistant_status_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/status")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["documents"]["documents_count"] == 1
    assert body["sessions"]["messages_count"] == 2


def test_assistant_dashboard_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.get("/assistant/dashboard")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["cards"]["connection"]["status"] == "ready"
    assert body["recent_sessions"][0]["session_id"] == "session-1"
    assert body["ui"]["ready"] is True


def test_assistant_bootstrap_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/bootstrap",
        json={"project_root": "/tmp/project", "include_sessions": True, "sessions_limit": 5},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["capabilities"]["endpoints"]["message"] == "POST /assistant/message"
    assert body["status"]["current_phase"]["phase"] == 15
    assert body["project_root"]["safe_for_read_only_agent"] is True
    assert body["sessions"]["limit"] == 5
    assert body["ui"]["ready"] is True


def test_assistant_session_endpoints_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    create_response = client.post(
        "/assistant/sessions",
        json={"title": "Demo", "project_root": "/tmp/project"},
    )
    list_response = client.get("/assistant/sessions?limit=5&offset=0")
    get_response = client.get("/assistant/sessions/session-1")
    messages_response = client.get("/assistant/sessions/session-1/messages?limit=10&offset=0")
    missing_response = client.get("/assistant/sessions/missing")
    missing_messages_response = client.get("/assistant/sessions/missing/messages")

    app.dependency_overrides.clear()
    assert create_response.status_code == 200
    assert create_response.json()["session_id"] == "session-1"
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["messages_count"] == 1
    assert get_response.status_code == 200
    assert get_response.json()["messages"][0]["content"] == "JWT"
    assert messages_response.status_code == 200
    assert messages_response.json()["total_messages"] == 1
    assert messages_response.json()["messages"][0]["content"] == "JWT"
    assert missing_response.status_code == 404
    assert missing_messages_response.status_code == 404


def test_assistant_message_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/message",
        json={"message": "JWT 설명해줘", "session_id": "session-1", "mode": "auto"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "answer"
    assert body["used_documents"] is True
    assert body["sources"][0]["chunk_id"] == 3
    assert body["safety"]["shell_execution"] == "disabled"
    assert body["ui"]["response_type"] == "answer"


def test_assistant_project_root_validate_endpoint_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/project-root/validate", json={"project_root": "/tmp/project"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["safe_for_read_only_agent"] is True


def test_stage70_approval_console_read_only_api_exposes_only_safe_surface_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    pending = client.get("/assistant/approval-console/pending")
    detail = client.get("/assistant/approval-console/server-issued-id")
    cleanup = client.post("/assistant/approval-console/cleanup-expired")
    approve = client.post("/assistant/approval-console/server-issued-id/approve")
    reject = client.post("/assistant/approval-console/server-issued-id/reject")

    app.dependency_overrides.clear()
    assert pending.status_code == 200
    assert detail.status_code == 200
    assert cleanup.status_code == 200
    assert approve.status_code == 404
    assert reject.status_code == 404
    pending_body = pending.json()
    detail_body = detail.json()
    cleanup_body = cleanup.json()
    assert pending_body["read_only"] is True
    assert pending_body["would_execute"] is False
    assert pending_body["approval_consumed"] is False
    assert pending_body["approvals"][0]["raw_approval_id_included"] is False
    assert pending_body["approvals"][0]["payload_hash_included"] is False
    assert "approval_id" not in pending_body["approvals"][0]
    assert "payload_hash" not in pending_body["approvals"][0]
    assert detail_body["approval"]["raw_approval_id_included"] is False
    assert detail_body["approval"]["payload_hash_included"] is False
    assert cleanup_body["cleanup"]["approval_consumed"] is False
    assert cleanup_body["cleanup"]["payload_hash_included"] is False
    assert pending_body["gates"]["approve_endpoint_connected"] is False
    assert pending_body["gates"]["reject_endpoint_connected"] is False
    assert pending_body["gates"]["action_loop_full_dispatch_connected"] is False


def test_stage70_approval_console_api_surface_exposes_no_approve_or_reject_routes() -> None:
    route_paths = {getattr(route, "path", "") for route in app.routes}
    read_only_surface = {
        "/assistant/approval-console/pending",
        "/assistant/approval-console/{approval_id}",
        "/assistant/approval-console/cleanup-expired",
    }
    blocked_surface = {
        "/assistant/approval-console/{approval_id}/approve",
        "/assistant/approval-console/{approval_id}/reject",
    }

    assert read_only_surface.issubset(route_paths)
    assert blocked_surface.isdisjoint(route_paths)
    assert "/assistant/full-automation-dispatch" in route_paths


def test_stage74_durable_state_preview_read_only_api_candidate_exposes_response_only_surface_with_mock() -> None:
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/durable-state-preview/preview",
        json={
            "goal": "review durable state",
            "session_id": "session-1",
            "request_id": "request-1",
            "proposed_steps": [{"tool": "read_only_scan", "params": {"path": "README.md"}}],
            "metadata": {"approval_id": "client-injected", "payload_hash": "raw-hash"},
        },
    )
    detail = client.get("/assistant/durable-state-preview/preview-state-1")
    listing = client.get("/assistant/durable-state-preview")
    cleanup = client.post("/assistant/durable-state-preview/cleanup-expired")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert detail.status_code == 404
    assert listing.status_code in {404, 405}
    assert cleanup.status_code == 404
    body = response.json()
    assert body["mode"] == "durable-state-preview-read-only"
    assert body["read_only"] is True
    assert body["schema_only"] is True
    assert body["response_only"] is True
    assert body["would_execute"] is False
    assert body["would_persist"] is False
    assert body["would_dispatch"] is False
    assert body["approval_consumed"] is False
    assert body["preview_state"]["state_schema_version"] == "durable_state_preview.v1"
    assert body["preview_state"]["state_status"] == "candidate-preview"
    assert body["gates"]["stored_preview_lookup_connected"] is False
    assert body["gates"]["durable_table_created"] is False
    assert body["gates"]["action_loop_full_dispatch_connected"] is False
    assert body["audit"]["raw_approval_id_included"] is False
    assert body["audit"]["payload_hash_included"] is False


def test_stage74_durable_state_preview_route_surface_exposes_only_preview_endpoint() -> None:
    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert "/assistant/durable-state-preview/preview" in route_paths
    assert "/assistant/durable-state-preview/{preview_state_id}" not in route_paths
    assert "/assistant/durable-state-preview" not in route_paths
    assert "/assistant/durable-state-preview/cleanup-expired" not in route_paths


def test_stage75_durable_state_preview_api_regression_guard_keeps_only_protected_preview_route() -> None:
    inventory = build_api_inventory(app.routes)
    durable_endpoints = [
        endpoint for endpoint in inventory["endpoints"] if endpoint["path"].startswith("/assistant/durable-state-preview")
    ]

    assert durable_endpoints == [
        {
            "path": "/assistant/durable-state-preview/preview",
            "methods": ["POST"],
            "tags": ["assistant"],
            "name": "assistant_durable_state_preview",
            "requires_api_key": True,
        }
    ]
    assert inventory["endpoints_count"] == 94
    assert inventory["protected_endpoints_count"] == 78
    assert inventory["public_endpoints_count"] == 16

    route_paths = {getattr(route, "path", "") for route in app.routes}
    blocked_routes = {
        "/assistant/durable-state-preview/{preview_state_id}",
        "/assistant/durable-state-preview",
        "/assistant/durable-state-preview/cleanup-expired",
    }
    assert blocked_routes.isdisjoint(route_paths)
