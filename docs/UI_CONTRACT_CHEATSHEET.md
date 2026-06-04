# UI Contract Cheatsheet

브라우저 UI 또는 로컬 앱이 `local-ai-server`에 붙을 때 필요한 핵심 endpoint와 표시 필드만 모은 요약표다.

## 공통 연결

| 항목 | 값 |
|---|---|
| API base URL | `http://127.0.0.1:8000` |
| Project root | `/Users/juyoung/local-ai-server` |
| Auth header | `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key: <LOCAL_API_KEY>` |

주의:

- 실제 `LOCAL_API_KEY` 값은 코드, 문서, 로그, 스크린샷에 남기지 않는다.
- 응답의 `safety` 값이 실행 차단 상태면 UI도 실행 버튼을 활성화하지 않는다.

## Endpoint별 표시 필드

| Endpoint | UI 목적 | 우선 표시 필드 |
|---|---|---|
| `GET /assistant/startup` | 첫 화면 hydration | `ping.status`, `config.protected`, `dashboard.cards.connection.status`, `ui.display` |
| `POST /assistant/bootstrap` | project root와 세션 초기화 | `project_root.safe_for_read_only_agent`, `sessions.sessions`, `ui.blocked_actions` |
| `POST /assistant/action-preview` | 전송 전 위험도 미리보기 | `intent`, `risk_level`, `requires_approval`, `missing_inputs`, `ui` |
| `POST /assistant/automation-plan` | 개인 API 자동화 plan-only | `goal`, `would_execute`, `current_capabilities`, `automation_stages`, `blocked_until_review`, `recommended_next_model`, `ui.response_type` |
| `GET /assistant/workflow-presets` | workflow preset list | `presets`, `would_dispatch=false`, `execution_enabled=false` |
| `GET /assistant/workflow-presets/{preset_id}` | workflow preset detail | `status`, `preset`, `would_dispatch=false`, `execution_enabled=false` |
| `POST /assistant/workflow-presets/{preset_id}/preview` | workflow preset proposed steps | `status`, `frozen_proposed_steps`, `blocked_reasons`, `unsafe_policy`, `would_dispatch=false`, `execution_enabled=false` |
| `POST /assistant/task-queue/preview` | long-running task create preview | `status`, `task`, `blocked_reasons`, `would_enqueue=false`, `worker_enabled=false`, `execution_enabled=false` |
| `GET /assistant/task-queue` | long-running task status list | `tasks`, `statuses`, `would_execute=false`, `worker_enabled=false`, `execution_enabled=false` |
| `POST /assistant/task-queue/drain` | one-shot task queue worker drain | `status`, `drained_count`, `results`, `worker`, `would_execute=false`, `worker_enabled`, `execution_enabled` |
| `GET /assistant/task-queue/{task_id}` | long-running task detail | `task_id`, `status`, `task`, `would_execute=false`, `worker_enabled=false`, `execution_enabled=false` |
| `POST /assistant/task-queue/{task_id}/cancel-preview` | long-running task cancellation preview | `task_id`, `status`, `cancellation`, `would_cancel_worker=false`, `worker_enabled=false`, `execution_enabled=false` |
| `POST /assistant/failure-recovery-preview` | failure recovery rollback preview | `failure`, `rollback_plan`, `manual_instructions`, `paste_safe_summary`, `rollback_enabled=false`, `execution_enabled=false` |
| `POST /assistant/rollback-approval-preview` | rollback approval binding preview | `status`, `binding`, `preview`, `blocked_reasons`, `rollback_enabled=false`, `would_apply=false` |
| `POST /assistant/rollback-execute` | rollback executor boundary | 기본값 `execution_enabled=false`, `would_apply=false`; env opt-in 성공 시 `status=applied`, `rollback_result`, `result_wrapper`, `audit` |
| `POST /assistant/action-loop-preflight` | action-loop dispatch preflight | `status`, `frozen_plan`, `gates`, `would_dispatch=false`, `execution_enabled=false` |
| `POST /assistant/action-loop-noop-dispatch` | no-op dispatcher route plan | `status`, `route_plan`, `noop_audit`, `would_dispatch=false`, `would_dispatch_noop_only`, `execution_enabled=false`, `approval_consume_mode=validate-only` |
| `POST /assistant/action-loop-read-only-dispatch-preview` | read-only dispatch boundary preview | `status`, `route_plan`, `result_wrapper_schema`, `boundary_audit`, `would_dispatch=false`, `would_read=false`, `would_fetch=false`, `execution_enabled=false` |
| `POST /assistant/read-only-scan` | 프로젝트 구조 scan | `summary`, `important_files`, `top_level_items`, `extension_counts`, `would_execute` |
| `POST /assistant/file-preview` | 안전한 파일 preview | `status`, `metadata`, `content_preview`, `masked`, `truncated`, `would_execute` |
| `POST /assistant/url-preview` | URL fetch preflight | `status`, `would_fetch`, `reason`, `safety` |
| `POST /assistant/web-search-provider-preview` | external web search provider gate | `status`, `provider_config`, `gate`, `result_wrapper`, `would_search=false`, `would_fetch=false`, `external_api_enabled=false` |
| `POST /assistant/web-search-provider/search` | external web search provider result | `status`, `provider_config`, `gate`, `search_result`, `result_wrapper`, `would_search` |
| `POST /assistant/app-os-interaction-preview` | app/OS interaction gate | `status`, `taxonomy`, `permission_model`, `approval_binding`, `gate`, `would_control_app=false`, `os_action_executed=false` |
| `POST /assistant/workspace-brief` | 프로젝트 요약 panel | `scan`, `previews`, `next_safe_actions`, `would_execute` |
| `POST /assistant/shell-preview` | shell sandbox preview | `status`, `allowed`, `command_preview`, `audit`, `would_execute=false` |
| `POST /assistant/shell-approval-preview` | approval binding preview | `approval_required`, `binding`, `preview`, `would_execute=false` |
| `POST /assistant/shell-run` | locked shell run | `status=locked`, `execution_enabled=false`, `preview`, `would_execute=false` |
| `POST /assistant/patch-preview` | patch diff preview | `status`, `allowed`, `diff_preview`, `secret_scan`, `rollback`, `would_apply=false` |
| `POST /assistant/patch-approval-preview` | patch approval binding preview | `approval_required`, `binding`, `preview`, `would_apply=false` |
| `POST /assistant/patch-apply` | patch apply sandbox | 기본값 `execution_enabled=false`, `would_apply=false`; env opt-in 성공 시 `status=applied`, `apply_result`, `rollback`, `audit` |
| `POST /assistant/browser-preview` | browser/app taxonomy preview | `status`, `allowed`, `taxonomy`, `gate`, `audit`, `would_interact=false`, `gate.browser_launch=not_performed` |
| `POST /assistant/browser-approval-preview` | browser/app approval binding preview | `approval_required`, `binding`, `preview`, `would_interact=false` |
| `POST /assistant/browser-interact` | locked browser/app interact | `status=locked`, `execution_enabled=false`, `preview`, `would_interact=false` |
| `POST /assistant/browser-observe` | browser observe sandbox | 기본값 `execution_enabled=false`; env opt-in 성공 시 `observe_result`, `result_wrapper`, `would_observe=true` |
| `POST /assistant/browser-limited-interact` | browser limited interaction candidate | 기본값 `execution_enabled=false`; env opt-in에서도 `interaction_result`, `result_wrapper`, `would_interact=false` |
| `POST /assistant/message` | 실제 메시지 API | `type`, `answer`, `data`, `sources`, `request_id`, `ui.response_type`, `ui.display` |
| `GET /assistant/sessions` | 세션 목록 | `sessions`, `limit`, `offset`, `sessions[].messages_count`, `sessions[].last_message_preview` |
| `GET /assistant/sessions/{session_id}/messages` | 메시지 기록 | `messages`, `limit`, `offset`, `total_messages` |
| `GET /project/api-inventory` | 개발/디버그 API 목록 | `mode`, `local_only`, `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count`, `endpoints[].path`, `endpoints[].methods`, `endpoints[].tags`, `endpoints[].requires_api_key`, `safety` |
| `POST /documents/index-folder-job-preview` | 대용량 색인 progress preview | `job_id`, `status`, `dry_run`, `would_enqueue`, `progress.total_files`, `progress.embedding_batches_total`, `progress.percent`, `status_endpoint` |
| `GET /documents/repair-preview` | SQLite/Chroma repair preview | `status`, `dry_run`, `actions_count`, `actions[].requires_user_approval`, `note` |
| `GET /documents/vector-rebuild-preview` | 누락 vector 재생성 preview | `status`, `dry_run`, `chunks_missing_vectors_count`, `embedding_batches_estimated`, `actions[].requires_user_approval` |

## Refresh endpoints

`GET /assistant/ui-contract`의 `refresh_endpoints`에 포함되는 endpoint다.

| Method | Path | UI 목적 |
|---|---|---|
| `GET` | `/assistant/ping` | 서버/auth quick check |
| `GET` | `/assistant/config` | safe local settings |
| `GET` | `/assistant/dashboard` | dashboard cards |
| `GET` | `/assistant/sessions` | session sidebar refresh |
| `GET` | `/project/api-inventory` | read-only endpoint inventory for developer/debug UI |

## Message response type 매핑

| `type` | UI 렌더링 | 주요 필드 |
|---|---|---|
| `answer` | 채팅 bubble | `answer`, `used_documents`, `sources`, `ui.primary_text` |
| `search_results` | 검색 결과 panel | `data.query`, `data.results[]`, `ui.primary_text` |
| `index_preview` | 폴더 색인 미리보기 panel | `data.files_count`, `data.chunks_estimated`, `data.embedding_batches_estimated` |
| `needs_project_root` | project root 입력 warning | `data.required_field`, `ui.severity` |
| `shell_dry_run` | shell 정책 판단 panel | `data.command`, `data.status`, `data.would_execute` |
| `agent_plan` | 실행 대신 계획/승인 필요 panel | `data.run_id`, `data.actions[]`, `ui.severity` |
| `automation_plan` | 개인 API 자동화 준비도 panel | `data.current_capabilities`, `data.automation_stages`, `data.blocked_until_review` |
| `workflow_presets` | personal workflow preset list panel | `presets`, `would_dispatch=false`, `execution_enabled=false` |
| `workflow_preset_detail` | personal workflow preset detail panel | `status`, `preset`, `would_dispatch=false`, `execution_enabled=false` |
| `workflow_preset_preview` | personal workflow preset preview panel | `status`, `frozen_proposed_steps`, `blocked_reasons`, `unsafe_policy`, `would_dispatch=false`, `execution_enabled=false` |
| `task_queue_preview` | locked long-running task queue create preview panel | `status`, `task`, `blocked_reasons`, `would_enqueue=false`, `worker_enabled=false`, `execution_enabled=false` |
| `task_queue` | locked long-running task queue list panel | `tasks`, `statuses`, `would_execute=false`, `worker_enabled=false`, `execution_enabled=false` |
| `task_queue_drain` | one-shot task queue worker drain panel | `status`, `drained_count`, `results`, `worker`, `would_execute=false` |
| `task_queue_detail` | locked long-running task queue detail panel | `task_id`, `status`, `task`, `would_execute=false`, `worker_enabled=false`, `execution_enabled=false` |
| `task_queue_cancel_preview` | locked long-running task cancellation preview panel | `task_id`, `status`, `cancellation`, `would_cancel_worker=false`, `worker_enabled=false`, `execution_enabled=false` |
| `failure_recovery_preview` | locked failure recovery and rollback plan panel | `failure`, `rollback_plan`, `manual_instructions`, `paste_safe_summary`, `rollback_enabled=false`, `execution_enabled=false` |
| `rollback_approval_preview` | rollback approval binding preview panel | `status`, `binding`, `preview`, `blocked_reasons`, `would_apply=false` |
| `rollback_execute` | single-file rollback execution panel | `status`, `rollback_enabled`, `execution_enabled`, `rollback_result`, `result_wrapper`, `audit` |
| `read_only_scan` | 프로젝트 구조 read-only scan panel | `summary`, `important_files`, `extension_counts` |
| `file_preview` | masked 파일 preview panel | `metadata`, `content_preview`, `masked`, `truncated` |
| `url_preview` | URL fetch preflight panel | `status`, `would_fetch`, `reason` |
| `web_search_provider_preview` | external web search provider gate panel | `status`, `provider_config`, `gate`, `result_wrapper`, `would_search=false`, `would_fetch=false`, `external_api_enabled=false` |
| `web_search_provider_search` | external web search provider result panel | `status`, `provider_config`, `gate`, `search_result`, `result_wrapper`, `external_api_enabled` |
| `app_os_interaction_preview` | app/OS interaction gate panel | `status`, `taxonomy`, `permission_model`, `approval_binding`, `gate`, `would_control_app=false`, `os_action_executed=false` |
| `workspace_brief` | workspace brief panel | `scan`, `previews`, `next_safe_actions` |
| `shell_preview` | locked shell sandbox preview panel | `status`, `allowed`, `command_preview`, `audit`, `would_execute=false` |
| `shell_approval_preview` | approval binding preview panel | `approval_required`, `binding`, `preview`, `would_execute=false` |
| `shell_run_locked` | locked shell run panel | `status`, `execution_enabled=false`, `preview`, `would_execute=false` |
| `patch_preview` | locked patch diff preview panel | `status`, `allowed`, `diff_preview`, `secret_scan`, `rollback`, `would_apply=false` |
| `patch_approval_preview` | patch approval binding preview panel | `approval_required`, `binding`, `preview`, `would_apply=false` |
| `patch_apply_locked` | locked patch apply panel | `status`, `execution_enabled=false`, `preview`, `would_apply=false` |
| `patch_apply` | single-file patch apply panel | `status=applied`, `execution_enabled=true`, `apply_result`, `rollback`, `audit`, `would_apply=true` |
| `browser_preview` | locked browser/app interaction preview panel | `status`, `allowed`, `taxonomy`, `gate`, `audit`, `would_interact=false`, `gate.browser_launch=not_performed` |
| `browser_approval_preview` | browser/app approval binding preview panel | `approval_required`, `binding`, `preview`, `would_interact=false` |
| `browser_interact_locked` | locked browser/app interact panel | `status`, `execution_enabled=false`, `preview`, `would_interact=false` |
| `browser_observe` | browser observe read-only result panel | `status`, `execution_enabled`, `observe_result`, `result_wrapper`, `would_observe` |
| `browser_limited_interact` | browser limited interaction candidate panel | `status`, `policy`, `interaction_result`, `result_wrapper`, `would_interact=false` |
| `action_loop_preflight` | locked action-loop dispatch preflight panel | `status`, `frozen_plan`, `gates`, `would_dispatch=false`, `execution_enabled=false` |
| `action_loop_noop_dispatch` | no-op action-loop route plan panel | `status`, `route_plan`, `noop_audit`, `would_dispatch=false`, `execution_enabled=false` |
| `action_loop_read_only_dispatch_preview` | read-only dispatch boundary preview panel | `status`, `route_plan`, `result_wrapper_schema`, `boundary_audit`, `would_dispatch=false`, `would_read=false`, `would_fetch=false` |
| `action_loop_shell_dispatch` | shell action-loop allowlist dispatch panel | `status`, `route_plan`, `shell_results`, `shell_execution_connected`, `patch_apply_connected=false`, `browser_interaction_connected=false` |
| `action_loop_patch_dispatch` | patch action-loop single-file dispatch panel | `status`, `route_plan`, `patch_results`, `shell_execution_connected=false`, `patch_apply_connected`, `browser_interaction_connected=false` |
| `full_automation_preflight` | full personal automation route preflight panel | `status`, `frozen_plan`, `route_plan`, `tool_matrix`, `blocked_reasons`, `would_dispatch=false`, `execution_enabled=false` |
| `full_automation_dispatch` | full personal automation dispatch gate panel | `status`, `route_plan`, `tool_results`, `approval_consume_mode=validate-only`, `approval_consumed=false`, `dispatched=false` |
| `status` | 프로젝트 상태 panel | `data.current_phase`, `data.safe_next_tasks` |
| `action_preview` | 전송 전 preview panel | `data.intent`, `data.risk_level`, `data.requires_approval` |

## Safety 필드

UI는 아래 값이 보이면 실제 실행 버튼을 활성화하지 않는다.

| Field | Expected value | UI 처리 |
|---|---|---|
| `safety.shell_execution` | `disabled` | shell 실행 버튼 비활성 |
| `safety.shell_dry_run` | `blocked` 또는 정책 판단 결과 | dry-run 결과 panel만 표시 |
| `safety.shell_sandbox_execution` | `locked` | shell sandbox는 preview/locked-run panel만 표시 |
| `safety.patch_apply` | `locked`, `disabled`, `applied`, preview/blocked 상태 | 기본값은 patch apply 버튼 비활성. env opt-in apply 결과는 단일 파일 변경 summary와 rollback note만 표시 |
| `safety.browser_interaction` | `blocked` | 브라우저 click/fill/submit 버튼 비활성 |
| `safety.browser_interaction_preview` | `locked` 또는 preview/blocked 상태 | browser/app interaction은 taxonomy preview와 locked panel만 표시 |
| `safety.action_loop_dispatch` | `disabled` | action-loop dispatch 버튼 비활성 |
| `safety.action_loop_preflight` | `locked` 또는 preview/blocked 상태 | action-loop는 frozen plan preflight panel만 표시 |
| `safety.file_write_delete` | `blocked` | 파일 생성/수정/삭제 버튼 비활성 |
| `safety.folder_index` | `preview-only via assistant` | assistant 경유 폴더 색인은 preview만 허용 |
| `safety.external_llm_api` | `not-used` | 외부 LLM provider 선택/전송 비활성 |
| `safety.external_web_search` | `disabled` 또는 `provider_not_configured` | 외부 web search provider 호출 비활성 |
| `safety.external_api_enabled` | `false` | 외부 API 호출 기본값 비활성 |
| `safety.app_os_control` | `disabled` 또는 preview 상태 | App/OS control 비활성 |
| `safety.os_action_execution` | `disabled` | OS action 실행 비활성 |

## 에러 표시

| HTTP status | UI 메시지 |
|---|---|
| `401` | API key가 필요하거나 잘못되었습니다. |
| `404` | 요청한 endpoint 또는 session을 찾을 수 없습니다. |
| `422` | 요청 필드 형식이 맞지 않습니다. |
| `429` | 요청이 너무 많습니다. 잠시 후 다시 시도하세요. |
| `500` | 서버 내부 오류입니다. 서버 로그를 확인하세요. |

## 금지된 UI 동작

- 브라우저 클릭/입력/전송 자동화
- 실제 shell 실행
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 호출
- 운영 배포 또는 클라우드/Oracle 리소스 변경
