# API Reference

`local-ai-server`는 FastAPI 기반 로컬 전용 API 서버다. 런타임 LLM과 embedding 호출은 Ollama local API만 사용한다.

브라우저 UI 연동용 예시 payload는 [UI_BRIDGE_EXAMPLES.md](UI_BRIDGE_EXAMPLES.md)에 별도로 정리되어 있다.
브라우저 UI 수동 QA 기준은 [UI_QA_CHECKLIST.md](UI_QA_CHECKLIST.md)에 별도로 정리되어 있다.
GitHub 공개 전 체크리스트는 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)에 별도로 정리되어 있다.
공개 상태 요약은 [PUBLIC_RELEASE_SUMMARY.md](PUBLIC_RELEASE_SUMMARY.md)에 별도로 정리되어 있다.

기본 실행 주소:

```bash
http://127.0.0.1:8000
```

## 인증

`LOCAL_API_KEY`가 설정되어 있으면 보호 endpoint는 `X-API-Key` 헤더를 요구한다. 외부 로컬 UI가 Bearer token 입력만 지원하는 경우를 위해 `Authorization: Bearer <LOCAL_API_KEY>`도 같은 키로 허용한다.

```bash
X-API-Key: <LOCAL_API_KEY>
Authorization: Bearer <LOCAL_API_KEY>
```

보호 endpoint:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`
- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder-job-preview`
- `POST /documents/index-folder`
- `DELETE /documents/{document_id}`
- `POST /feedback`
- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`
- `GET /agent/runs/{run_id}/results`
- `GET /agent/runs/{run_id}/actions`
- `POST /agent/runs/{run_id}/dry-run`
- `POST /agent/runs/{run_id}/approve`
- `POST /agent/runs/{run_id}/reject`
- `POST /agent/runs/{run_id}/execute`
- `GET /project/shell-policy`
- `POST /project/shell-dry-run`
- `GET /assistant/capabilities`
- `POST /assistant/action-preview`
- `POST /assistant/action-loop-preflight`
- `POST /assistant/action-loop-noop-dispatch`
- `POST /assistant/action-loop-read-only-dispatch-preview`
- `POST /assistant/action-loop-read-only-dispatch`
- `POST /assistant/action-loop-shell-dispatch`
- `POST /assistant/action-loop-patch-dispatch`
- `POST /assistant/full-automation-preflight`
- `POST /assistant/full-automation-dispatch`
- `POST /assistant/automation-plan`
- `GET /assistant/workflow-presets`
- `GET /assistant/workflow-presets/{preset_id}`
- `POST /assistant/workflow-presets/{preset_id}/preview`
- `POST /assistant/task-queue/preview`
- `GET /assistant/task-queue`
- `POST /assistant/task-queue/drain`
- `GET /assistant/task-queue/{task_id}`
- `POST /assistant/task-queue/{task_id}/cancel-preview`
- `POST /assistant/failure-recovery-preview`
- `POST /assistant/rollback-approval-preview`
- `POST /assistant/rollback-execute`
- `POST /assistant/read-only-scan`
- `POST /assistant/file-preview`
- `POST /assistant/url-preview`
- `POST /assistant/read-only-adapter/execute`
- `POST /assistant/web-search-provider-preview`
- `POST /assistant/web-search-provider/search`
- `POST /assistant/app-os-interaction-preview`
- `POST /assistant/workspace-brief`
- `POST /assistant/shell-preview`
- `POST /assistant/shell-approval-preview`
- `POST /assistant/shell-run`
- `POST /assistant/durable-state-preview/preview`
- `GET /assistant/approval-console/pending`
- `GET /assistant/approval-console/{approval_id}`
- `POST /assistant/approval-console/cleanup-expired`
- `POST /assistant/patch-preview`
- `POST /assistant/patch-approval-preview`
- `POST /assistant/patch-apply`
- `POST /assistant/browser-preview`
- `POST /assistant/browser-approval-preview`
- `POST /assistant/browser-interact`
- `POST /assistant/browser-observe`
- `POST /assistant/browser-limited-interact`
- `GET /assistant/ping`
- `GET /assistant/config`
- `GET /assistant/ui-contract`
- `GET /assistant/startup`
- `GET /assistant/status`
- `GET /assistant/dashboard`
- `POST /assistant/bootstrap`
- `POST /assistant/sessions`
- `GET /assistant/sessions`
- `GET /assistant/sessions/{session_id}`
- `GET /assistant/sessions/{session_id}/messages`
- `POST /assistant/message`
- `POST /assistant/project-root/validate`

주의:

현재 API key 없이 읽을 수 있는 public read-only endpoint는 `GET /health`, `GET /health/ollama`, `GET /documents`, `GET /documents/{document_id}`, `GET /documents/{document_id}/chunks`, `GET /documents/supported-types`, `GET /documents/stats`, `GET /documents/integrity`, `GET /documents/repair-preview`, `GET /documents/vector-rebuild-preview`, `GET /chat-logs`, `GET /chat-logs/{chat_log_id}`, `GET /feedback`, `GET /project/status`, `GET /project/next`, `GET /project/api-inventory`이다. `/agent/runs`는 사용자 요청 내용이 포함될 수 있어 보호 endpoint로 둔다. shell dry-run 정책 endpoint는 명령 후보가 포함될 수 있어 `LOCAL_API_KEY` 설정 시 보호된다. 개인 문서가 들어가는 환경에서는 서버를 `127.0.0.1`에만 bind하는 것을 권장한다.

24차 Production Hardening 기준으로 `/assistant/capabilities`와 `/assistant/ui-contract`는 위험 기능을 과장해 enabled로 광고하지 않는다. shell은 27차 allowlist env opt-in, patch는 29차 단일 파일 env opt-in 범위만 표시할 수 있고, task queue worker는 34차 env opt-in one-shot drain 범위만 표시할 수 있다. rollback executor는 35차 env opt-in 단일 파일 restore 범위만 표시할 수 있다. 36~48차 full personal automation은 preflight, no-op orchestrator, read-only adapter step integration, allowlist shell step integration, single-file patch step integration, single-file rollback step integration, read-only task queue step integration, browser observe metadata step integration, browser limited candidate validation step integration, external web search provider step integration, app-os observe-plan preview step integration, policy/audit matrix hardening, Full Automation Action-loop Dispatch Decision Required까지만 제공한다. 실제 action-loop full dispatch는 계속 금지하며, 사용자 최종 승인과 Opus 리뷰 전까지 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 유지한다. browser actual interaction/app-os actual action dispatch는 아직 연결하지 않는다. browser와 app/OS control은 disabled/blocked/locked/preview-only로 표시되어야 한다. 운영 배포 또는 service/daemon 활성화는 이 API 계약에 포함되지 않는다.

## Rate Limit

보호 endpoint는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit을 적용한다. 기본값은 분당 `120`회이며, `0`으로 설정하면 비활성화된다.

제한을 초과하면 `429 Too Many Requests`와 `Retry-After` header를 반환한다.

## CORS

브라우저 기반 로컬 UI 호출을 위해 `LOCAL_CORS_ORIGINS`에 명시된 origin만 허용한다. `LOCAL_CORS_ALLOW_CREDENTIALS`의 기본값은 `false`이며, cookie/auth credential이 필요한 별도 UI를 붙일 때만 명시적으로 켠다.

기본값:

```env
LOCAL_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
LOCAL_CORS_ALLOW_CREDENTIALS=false
```

허용 header:

- `Authorization`
- `Content-Type`
- `X-API-Key`

## Health

### `GET /health`

서버 설정 기본값을 확인한다. Ollama 연결을 강제하지 않는다.

```bash
curl http://127.0.0.1:8000/health
```

응답 예:

```json
{
  "status": "ok",
  "service": "local-ai-server",
  "ollama_base_url": "http://localhost:11434",
  "llm_model": "llama3.2",
  "embedding_model": "nomic-embed-text"
}
```

### `GET /health/ollama`

Ollama server와 모델 준비 상태를 확인한다.

```bash
curl http://127.0.0.1:8000/health/ollama
```

## Project Status

### `GET /project/status`

현재 완료 차수, 다음 안전 작업, 보류 중인 고위험 작업, Recommended Next Model을 반환한다.

```bash
curl http://127.0.0.1:8000/project/status
```

### `GET /project/next`

다음에 이어갈 안전 작업과 Recommended Next Model만 요약해 반환한다.

```bash
curl http://127.0.0.1:8000/project/next
```

### `GET /project/api-inventory`

현재 FastAPI endpoint 목록, tag, HTTP method, API key 보호 여부를 read-only로 조회한다. 브라우저 UI나 CLI가 어떤 endpoint를 연결해야 하는지 확인할 때 사용한다.
UI bridge 예시 문서의 `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count`는 runtime endpoint count drift check로 실제 FastAPI route 수와 비교한다.

```bash
curl http://127.0.0.1:8000/project/api-inventory
```

응답 핵심 필드:

- `mode=read-only`
- `endpoints_count`
- `protected_endpoints_count`
- `public_endpoints_count`
- `endpoints[].path`
- `endpoints[].methods`
- `endpoints[].requires_api_key`
- `safety.external_llm_api=disabled`
- `safety.shell_execution=dry-run-only`
- `safety.browser_interaction=disabled`
- `safety.file_write_delete=disabled`

### `GET /project/shell-policy`

shell 실행 엔진을 활성화하기 전, dry-run 기준의 allowlist와 blocked token을 조회한다. 실제 shell 명령은 실행하지 않는다.

```bash
curl http://127.0.0.1:8000/project/shell-policy
```

응답 핵심 필드:

- `mode=dry-run-only`
- `allowed_commands`
- `blocked_tokens`
- `note`

### `POST /project/shell-dry-run`

입력한 shell 명령 후보가 현재 정책상 허용 preview인지 차단 대상인지 판단한다. 이 endpoint는 명령을 실행하지 않으며 항상 `would_execute=false`를 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/project/shell-dry-run \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd"}'
```

응답 핵심 필드:

- `command`
- `status=allowed_preview|blocked`
- `would_execute=false`
- `reason`

## Assistant

### `GET /assistant/capabilities`

브라우저 UI나 외부 로컬 클라이언트가 현재 서버 기능과 안전 기본값을 확인한다.

```bash
curl http://127.0.0.1:8000/assistant/capabilities
```

응답 핵심 필드:

- `service`
- `local_only`
- `llm_provider`
- `storage`
- `vector_store`
- `modes`
- `protected`
- `safe_defaults`
- `endpoints`

### `POST /assistant/action-preview`

메시지를 실제 처리하기 전에 intent, 추천 endpoint, 위험도, 필요한 입력값을 preview한다. 이 endpoint는 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-preview \
  -H "Content-Type: application/json" \
  -d '{"message":"브라우저 열어줘","project_root":"/Users/juyoung/local-ai-server","mode":"auto"}'
```

응답 핵심 필드:

- `intent`
- `recommended_endpoint`
- `would_execute=false`
- `requires_approval`
- `risk_level`
- `needs`
- `safety`
- `ui`

### `POST /assistant/automation-plan`

개인 API 자동화 목표를 현재 안전 경계 안에서 단계별 plan-only 계약으로 정리한다. 이 endpoint는 shell 실행, 브라우저 조작, 파일 생성/수정/삭제, 외부 LLM/API 호출을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/automation-plan \
  -H "Content-Type: application/json" \
  -d '{"goal":"내 개인 API 자동화","project_root":"/Users/juyoung/local-ai-server"}'
```

응답 핵심 필드:

- `goal`
- `service`
- `local_only=true`
- `would_execute=false`
- `current_capabilities`
- `automation_stages`
- `codex_safe_now`
- `blocked_until_review`
- `required_user_decisions`
- `recommended_next_model`
- `safety`
- `ui.response_type=automation_plan`

### `POST /assistant/read-only-scan`

허용 root 안의 프로젝트 구조를 read-only로 스캔한다. 파일 내용은 읽지 않고 top-level item, 확장자 count, 중요 파일 존재 여부만 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/read-only-scan \
  -H "Content-Type: application/json" \
  -d '{"project_root":"/Users/juyoung/local-ai-server","max_items":120}'
```

응답 핵심 필드:

- `service`
- `project_root`
- `resolved_path`
- `mode=read-only`
- `would_execute=false`
- `summary`
- `important_files`
- `top_level_items`
- `extension_counts`
- `safety`
- `ui`

### `POST /assistant/file-preview`

허용 root 안의 UTF-8 텍스트 파일만 read-only로 preview한다. `.env`, key, credential 후보는 차단하고 secret-looking 값은 masking한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/file-preview \
  -H "Content-Type: application/json" \
  -d '{"path":"/Users/juyoung/local-ai-server/README.md","project_root":"/Users/juyoung/local-ai-server","max_bytes":8000}'
```

응답 핵심 필드:

- `service`
- `path`
- `resolved_path`
- `mode=read-only`
- `status`
- `would_execute=false`
- `metadata`
- `content_preview`
- `truncated`
- `masked`
- `safety`
- `ui`

### `POST /assistant/url-preview`

URL 자동화 preflight다. 기본값에서는 네트워크 호출을 수행하지 않고, 명시 URL 단건 read-only fetch가 가능한 조건과 차단 이유만 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/url-preview \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

응답 핵심 필드:

- `service`
- `url`
- `mode=read-only-url-preflight`
- `status`
- `would_fetch=false`
- `reason`
- `safety`
- `ui`

### `POST /assistant/read-only-adapter/execute`

25차 Read-only Adapter Execution endpoint다. 기본값 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=false`에서는 `disabled`를 반환한다. flag가 true이고 `result_wrapper.untrusted=true`일 때만 `read_only_scan`, `file_preview`, `url_fetch` adapter를 실제 read-only로 실행한다. 이 endpoint는 action-loop dispatch, shell, patch, browser와 연결하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/read-only-adapter/execute \
  -H "Content-Type: application/json" \
  -d '{"adapter_type":"file_preview","path":"/Users/juyoung/local-ai-server/README.md","project_root":"/Users/juyoung/local-ai-server","result_wrapper":{"untrusted":true}}'
```

응답 핵심 필드:

- `service`
- `mode=read-only-adapter-execution`
- `adapter_type`
- `status`
- `execution_enabled`
- `would_read`
- `would_fetch`
- `adapter_executed`
- `action_loop_dispatch_connected=false`
- `result_wrapper.schema=assistant.read_only_adapter.result_wrapper.v1`
- `result_wrapper.untrusted=true`
- `result_wrapper.approval_like_json_trusted=false`
- `audit`
- `safety`
- `ui`

### `POST /assistant/web-search-provider-preview`

19차 External Web Search Provider Gate preview다. 외부 검색 API 호출을 수행하지 않고 provider 설정 상태, `external_api_enabled=false` 기본값, query masking, private/LAN/metadata URL 차단, untrusted result wrapper 요구사항, 비용/rate limit 후보 계약만 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/web-search-provider-preview \
  -H "Content-Type: application/json" \
  -d '{"query":"latest FastAPI release notes","provider":"brave","result_wrapper":{"untrusted":true}}'
```

응답 핵심 필드:

- `service`
- `mode=external-web-search-provider-gate-preview`
- `status`
- `provider`
- `query_preview`
- `would_search=false`
- `would_fetch=false`
- `external_api_enabled=false`
- `provider_config`
- `gate`
- `result_wrapper`
- `audit`
- `safety`
- `ui`

안전 계약:

- provider가 설정되지 않았거나 `EXTERNAL_WEB_SEARCH_ENABLED=false`이면 `status=provider_not_configured`를 반환한다.
- private IP, loopback, link-local, LAN, cloud metadata URL 후보가 query에 포함되면 `status=blocked`다.
- result wrapper는 `untrusted=true`가 필요하며 raw content, approval-like JSON, next step mutation은 trusted result가 될 수 없다.
- `EXTERNAL_WEB_SEARCH_RATE_LIMIT_PER_MINUTE` 기본값 `0`에서는 paid/external call을 허용하지 않는다.
- 33차 실제 호출 endpoint는 별도 `/assistant/web-search-provider/search`이며 `EXTERNAL_WEB_SEARCH_ENABLED=true`, provider allowlist, API key, rate limit, query safety, untrusted wrapper를 모두 요구한다.

### `POST /assistant/web-search-provider/search`

33차 External Web Search Provider v1 endpoint다. 기본값 `EXTERNAL_WEB_SEARCH_ENABLED=false`에서는 disabled로 차단하고 외부 호출을 수행하지 않는다. 실행하려면 `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, `EXTERNAL_WEB_SEARCH_API_KEY`, `EXTERNAL_WEB_SEARCH_RATE_LIMIT_PER_MINUTE>=1`, `result_wrapper.untrusted=true`, query safety gate를 모두 통과해야 한다. private/LAN/metadata URL, secret-like query, approval-like JSON injection, unsupported provider는 차단한다. 결과는 `assistant.external_web_search.result_wrapper.v1` untrusted wrapper로 반환하며 raw content, approval-like JSON, next action, frozen plan mutation을 허용하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/web-search-provider/search \
  -H "Content-Type: application/json" \
  -d '{"query":"latest FastAPI release notes","provider":"brave","result_wrapper":{"untrusted":true}}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `provider`
- `query_preview`
- `would_search`
- `would_fetch`
- `external_api_enabled`
- `reason`
- `provider_config`
- `gate`
- `search_result`
- `result_wrapper`
- `audit`
- `safety`
- `ui`

### `POST /assistant/app-os-interaction-preview`

20차 App/OS Interaction Gate preview다. 실제 OS app control을 수행하지 않고 observe-plan 후보, blocked action taxonomy, permission model, approval binding 설계, masking된 audit payload만 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/app-os-interaction-preview \
  -H "Content-Type: application/json" \
  -d '{"action":"observe-plan","app_name":"Preview","window_title":"Status"}'
```

응답 핵심 필드:

- `service`
- `mode=app-os-interaction-gate-preview`
- `status`
- `action`
- `app_name`
- `window_title`
- `target_path`
- `allowed=false`
- `observe_plan_candidate`
- `would_control_app=false`
- `os_action_executed=false`
- `reason`
- `taxonomy`
- `permission_model`
- `approval_binding`
- `gate`
- `audit`
- `safety`
- `ui`

안전 계약:

- `APP_OS_CONTROL_ENABLED=false` 기본값에서는 app open, click, type, hotkey, file dialog, file open을 수행하지 않는다.
- observe/status/read 계열은 observe-plan candidate로만 표시되며 실행 허용이 아니다.
- app name, window title, target path, input preview, reason은 audit payload 이전에 masking한다.
- credential/private path 후보는 blocked 상태로 남는다.
- approval binding은 설계 계약만 노출하며 서버 store approval을 생성하거나 실제 OS action approval로 사용하지 않는다.
- Computer Use, AppleScript, `osascript`, `open` command, keyboard/mouse/app control 연결은 없다.

### `GET /assistant/workflow-presets`

21차 Personal Workflow Presets list preview다. 안전한 workflow template/preset 목록만 반환하고 action-loop dispatch, shell, patch, browser, external API 실행은 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/assistant/workflow-presets
```

응답 핵심 필드:

- `service`
- `mode=workflow-preset-list-preview`
- `presets`
- `would_dispatch=false`
- `execution_enabled=false`
- `safety`
- `ui`

### `GET /assistant/workflow-presets/{preset_id}`

workflow preset detail preview다. `project_review`, `docs_check`, `ci_preview`, `patch_review`, `browser_review_plan` 같은 preset 정의와 필요한 params schema만 반환한다.

```bash
curl http://127.0.0.1:8000/assistant/workflow-presets/project_review
```

응답 핵심 필드:

- `service`
- `mode=workflow-preset-detail-preview`
- `preset_id`
- `status`
- `preset`
- `would_dispatch=false`
- `execution_enabled=false`
- `safety`
- `ui`

### `POST /assistant/workflow-presets/{preset_id}/preview`

workflow preset을 frozen proposed_steps 후보로만 변환한다. 생성된 steps는 action-loop preflight에 넘길 수 있는 검토용 구조지만 이 endpoint는 dispatch하지 않고 approval store도 소비하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/workflow-presets/project_review/preview \
  -H "Content-Type: application/json" \
  -d '{"params":{"project_root":"/Users/juyoung/local-ai-server"}}'
```

응답 핵심 필드:

- `service`
- `mode=workflow-preset-proposed-steps-preview`
- `preset_id`
- `status`
- `preset`
- `frozen_proposed_steps`
- `would_dispatch=false`
- `execution_enabled=false`
- `blocked_reasons`
- `unsafe_policy`
- `audit`
- `safety`
- `ui`

안전 계약:

- preset은 proposed_steps 후보만 생성하며 실제 dispatch, shell subprocess, patch apply, browser/app-os control, external API 호출을 수행하지 않는다.
- params는 secret-like 값 masking 후 frozen proposed_steps와 audit payload에 반영한다.
- client-supplied approval-like JSON은 `approval_like_json_injection_blocked`로 차단한다.
- `unsafe_direct_shell`, `unsafe_browser_click`, `unsafe_external_api` 같은 unsafe preset id는 blocked 상태로 남는다.

### `POST /assistant/task-queue/preview`

22차 Long-running Task Queue locked preview다. no-op/read-only task만 `queued` 상태 preview record로 만들고, 실제 background worker loop나 daemon/service는 시작하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/task-queue/preview \
  -H "Content-Type: application/json" \
  -d '{"task_type":"noop","params":{"note":"plan only"},"ttl_seconds":300}'
```

응답 핵심 필드:

- `service`
- `mode=long-running-queue-locked-preview`
- `status`
- `task`
- `blocked_reasons`
- `allowed_task_types`
- `would_enqueue=false`
- `worker_enabled=false`
- `execution_enabled=false`
- `audit`
- `cleanup_policy`
- `safety`
- `ui`

### `GET /assistant/task-queue`

task queue 상태를 read-only로 조회한다. 반환되는 `statuses`는 `queued`, `running`, `completed`, `blocked`, `cancelled` taxonomy지만 현재 worker loop는 disabled라 실제 running/completed 전이는 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/assistant/task-queue
```

응답 핵심 필드:

- `service`
- `mode=long-running-queue-list-read-only`
- `tasks`
- `statuses`
- `would_execute=false`
- `worker_enabled=false`
- `execution_enabled=false`
- `cleanup_policy`
- `safety`
- `ui`

### `POST /assistant/task-queue/drain`

34차 Task Queue Worker v1 endpoint다. 기본값 `TASK_QUEUE_WORKER_ENABLED=false`에서는 disabled로 차단하고 queued task 상태를 변경하지 않는다. `TASK_QUEUE_WORKER_ENABLED=true`에서만 request-scoped one-shot drain을 수행하며, daemon/service/background infinite loop는 시작하지 않는다. 실제 처리 범위는 `noop`, `read_only_scan`, `file_preview`이고 read-only 실행은 기존 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`와 untrusted wrapper gate를 재사용한다. `url_preview` task는 queue에는 만들 수 있지만 worker network fetch에는 아직 연결하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/task-queue/drain \
  -H "Content-Type: application/json" \
  -d '{"limit":1}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `worker_enabled`
- `execution_enabled`
- `would_execute=false`
- `drained_count`
- `tasks`
- `results`
- `blocked_reasons`
- `allowed_task_types`
- `worker`
- `audit`
- `cleanup_policy`
- `safety`
- `ui`

안전 계약:

- `TASK_QUEUE_WORKER_ENABLED=false`가 기본값이며 이 상태에서는 task 상태를 변경하지 않는다.
- worker는 explicit request 한 번에만 동작하는 one-shot drain이며 `background_loop_created=false`, `daemon_started=false`, `service_installed=false`를 반환한다.
- shell task는 queue worker에 연결하지 않았다. shell은 27차 `/assistant/shell-run`과 28차 shell action-loop dispatch의 approval-bound allowlist 계약에만 남아 있다.
- patch/browser/external API/rollback/app-os/action-loop full dispatch task는 worker에서 실행하지 않는다.
- result는 `assistant.task_queue.worker_result_wrapper.v1` untrusted wrapper로 반환하며 secret-like 값은 masking된다.

### `GET /assistant/task-queue/{task_id}`

task detail을 read-only로 조회한다. unknown 또는 TTL cleanup 이후 task는 `status=blocked`로 남는다.

```bash
curl http://127.0.0.1:8000/assistant/task-queue/task-id
```

응답 핵심 필드:

- `service`
- `mode=long-running-queue-detail-read-only`
- `task_id`
- `status`
- `task`
- `would_execute=false`
- `worker_enabled=false`
- `execution_enabled=false`
- `audit`
- `safety`
- `ui`

### `POST /assistant/task-queue/{task_id}/cancel-preview`

task cancellation state만 preview로 기록한다. 실제 worker cancellation, signal, process kill은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/task-queue/task-id/cancel-preview
```

응답 핵심 필드:

- `service`
- `mode=long-running-cancel-locked-preview`
- `task_id`
- `status`
- `task`
- `cancellation`
- `would_cancel_worker=false`
- `worker_enabled=false`
- `execution_enabled=false`
- `audit`
- `safety`
- `ui`

안전 계약:

- 허용 task type은 `noop`, `read_only_scan`, `file_preview`, `url_preview`, `workflow_preset_preview` 후보뿐이다.
- 34차 worker one-shot drain의 실제 처리 범위는 `noop`, `read_only_scan`, `file_preview`로 제한된다. `url_preview`는 network fetch worker에 아직 연결하지 않는다.
- shell, patch, browser, app/os, external API, action-loop dispatch task는 blocked 상태로 남는다.
- task params와 audit payload는 secret-like 값 masking 후 반환한다.
- approval-like JSON injection은 서버 approval이나 task authority로 승격하지 않는다.
- TTL cleanup은 process-local preview record 정리 정책이며 durable queue나 background worker를 의미하지 않는다.

### `POST /assistant/failure-recovery-preview`

23차 Failure Recovery / Rollback locked preview다. 실패 이유 taxonomy와 rollback plan만 반환하며 자동 rollback 실행, git reset, file restore, shell execution, browser interaction은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/failure-recovery-preview \
  -H "Content-Type: application/json" \
  -d '{"tool":"patch","failure_reason":"hash_mismatch","original_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}'
```

응답 핵심 필드:

- `service`
- `mode=failure-recovery-rollback-locked-preview`
- `tool`
- `status`
- `failure`
- `rollback_plan`
- `manual_instructions`
- `paste_safe_summary`
- `would_execute=false`
- `would_apply=false`
- `would_interact=false`
- `rollback_enabled=false`
- `execution_enabled=false`
- `audit`
- `safety`
- `ui`

안전 계약:

- patch rollback plan은 `original_sha256` precondition을 포함하지만 실제 restore/apply/delete/write를 수행하지 않는다.
- shell failure recovery는 manual instruction only이며 command 재실행이나 자동 cleanup을 수행하지 않는다.
- browser failure recovery는 manual instruction only이며 click/fill/submit/session 조작을 수행하지 않는다.
- failure summary와 params는 paste-safe masking 후 audit과 UI 응답에 포함한다.

### `POST /assistant/rollback-approval-preview`

35차 Rollback Executor Boundary approval endpoint다. 단일 UTF-8 텍스트 파일 restore 후보만 검토하고 서버 발급 approval binding을 만든다. 이 endpoint는 파일을 수정하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/rollback-approval-preview \
  -H "Content-Type: application/json" \
  -d '{"path":"/tmp/project/a.md","restored_content":"old\n","current_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","original_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}'
```

응답 핵심 필드:

- `service`
- `mode=rollback-approval-binding-preview`
- `status`
- `approval_required=true`
- `rollback_enabled=false`
- `would_apply=false`
- `binding`
- `preview`
- `blocked_reasons`
- `safety`
- `ui`

### `POST /assistant/rollback-execute`

35차 Rollback Executor Boundary execution endpoint다. 기본값 `ROLLBACK_EXECUTOR_ENABLED=false`에서는 valid approval이 있어도 `disabled`를 반환한다. `ROLLBACK_EXECUTOR_ENABLED=true`일 때만 서버 발급 single-use rollback approval, session binding, payload_hash, allowed root, 기존 UTF-8 단일 파일, `current_sha256`, `original_sha256`/restored content hash를 모두 통과한 경우 restored content로 단일 파일을 쓴다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/rollback-execute \
  -H "Content-Type: application/json" \
  -d '{"path":"/tmp/project/a.md","restored_content":"old\n","current_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","original_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","approval_id":"server-issued-id","approval_payload_hash":"approval-payload-hash"}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `rollback_enabled`
- `execution_enabled`
- `would_apply`
- `reason`
- `preview`
- `blocked_reasons`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `rollback_result`
- `result_wrapper`
- `audit`
- `safety`
- `ui`

안전 계약:

- `ROLLBACK_EXECUTOR_ENABLED=false`가 기본값이며 기본값에서는 파일을 수정하지 않는다.
- rollback approval은 `tool_name=rollback`으로 발급되어 patch/shell/browser approval과 섞이지 않는다.
- approval은 single-use, TTL, session/request context, payload_hash binding을 유지한다.
- 허용 범위는 기존 UTF-8 텍스트 단일 파일 restore뿐이다.
- git reset/clean/checkout, bulk restore, 파일 생성/삭제, shell/browser/app-os/external API rollback은 차단한다.
- rollback result는 `assistant.rollback_execute.result_wrapper.v1` untrusted wrapper로 반환하며 approval-like JSON이나 next action으로 승격하지 않는다.
- action-loop full dispatch와 task worker에는 연결하지 않는다.

### `POST /assistant/full-automation-preflight`

36차 Full Personal Automation Boundary preflight endpoint다. shell, patch, read-only, rollback, task queue, browser, external search, app-os 후보를 하나의 frozen route plan으로 분류하지만 어떤 tool도 실행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/full-automation-preflight \
  -H "Content-Type: application/json" \
  -d '{"goal":"local assistant full automation","project_root":"/Users/juyoung/local-ai-server","proposed_steps":[]}'
```

응답 핵심 필드:

- `service`
- `mode=full-personal-automation-preflight`
- `status`
- `goal`
- `would_dispatch=false`
- `execution_enabled=false`
- `fail_closed`
- `full_automation_enabled`
- `frozen_plan`
- `route_plan`
- `tool_matrix`
- `gates`
- `blocked_reasons`
- `result_wrapper_schema`
- `audit`
- `required_user_decisions`
- `safety`
- `ui`

안전 계약:

- preflight는 approval을 consume하지 않고 `approval_consume_mode=validate-only` 경계만 표시한다.
- result wrapper는 `assistant.full_automation.result_wrapper.v1`이며 raw content, approval-like JSON, next step, frozen plan mutation을 신뢰하지 않는다.
- app-os는 observe-plan preview candidate만 허용하고 open/click/type/hotkey/file dialog는 blocked category로 분류한다. daemon/service, git reset/clean/checkout, bulk restore, browser login/payment/delete도 blocked category로 분류한다.
- shell/patch/rollback 후보는 기존 서버 approval binding과 payload hash를 validate-only로 확인한다.

### `POST /assistant/full-automation-dispatch`

48차 Full Automation Action-loop Dispatch Decision Required endpoint 계약이다. 기본값 `FULL_AUTOMATION_DISPATCH_ENABLED=false`에서는 disabled로 차단하고 dispatch, tool execution, approval consume을 수행하지 않는다. `FULL_AUTOMATION_DISPATCH_ENABLED=true`만 켜진 경우에는 37차처럼 no-op aggregation만 반환한다. `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`가 함께 켜지면 read-only category step만 기존 read-only adapter wrapper로 실행한다. `SHELL_EXECUTION_ENABLED=true`와 valid shell approval이 함께 있으면 shell category step만 기존 shell sandbox로 실행한다. `PATCH_APPLY_ENABLED=true`, valid patch approval, allowed root, 기존 UTF-8 단일 파일, `original_sha256` precondition, secret scan을 모두 만족하면 patch category step만 기존 patch boundary로 실행한다. `ROLLBACK_EXECUTOR_ENABLED=true`, valid rollback approval, allowed root, 기존 UTF-8 단일 파일, current/original hash precondition을 모두 만족하면 rollback category step만 기존 rollback boundary로 실행한다. `TASK_QUEUE_WORKER_ENABLED=true`, read-only task type, wrapper gate, params masking, approval-like JSON injection 차단을 모두 만족하면 `noop`, `read_only_scan`, `file_preview` task queue step만 기존 one-shot worker boundary로 실행한다. `BROWSER_OBSERVE_ENABLED=true`, valid browser approval, loopback/명시 allowlist URL, read-only observe action을 모두 만족하면 browser_observe category step만 기존 browser observe metadata boundary로 실행한다. `BROWSER_LIMITED_INTERACTION_ENABLED=true`, valid browser approval, loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist를 모두 만족하면 browser_limited_interaction category step만 기존 candidate validation boundary로 실행한다. `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, provider configured, rate limit, query safety, `wrapper.untrusted=true`를 모두 만족하면 external_web_search category step만 기존 external web search provider boundary로 실행한다. app_os category step은 기존 `/assistant/app-os-interaction-preview` boundary로만 처리해 observe-plan candidate wrapper를 중첩하며 실제 app open/click/type/hotkey/file dialog는 수행하지 않는다. 47차에서는 `gates`, `audit.payload`, `safety`가 safe connector, preview connector, mutating connector, browser actual interaction, app-os actual action, action-loop full dispatch 상태를 명시했다. 48차에서는 실제 action-loop full dispatch는 계속 금지하고 connector별 approval consume, rollback/failure strategy, 사용자 최종 승인, Opus 리뷰 조건을 Decision Required로 고정한다. 61~73차 Local Jarvis runtime drift guard, failure/timeout drill, manual review packet, approval console state-only review, approval payload hash review, approval store expiry cleanup review, approval console API surface Decision Required, approval-console-read-only API, Durable Automation v2 Candidate Decision Required, Durable State Preview Schema Candidate, and Durable State Preview API Surface Decision Required는 `docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md`, `docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md`, `docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md`, `docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md`와 함께 실제 action-loop full dispatch, browser actual interaction, app-os actual action을 계속 미연결로 유지한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/full-automation-dispatch \
  -H "Content-Type: application/json" \
  -d '{"goal":"local assistant full automation","project_root":"/Users/juyoung/local-ai-server","proposed_steps":[]}'
```

응답 핵심 필드:

- `service`
- `mode=full-personal-automation-safe-orchestrator`
- `status`
- `goal`
- `dispatched`
- `would_dispatch`
- `execution_enabled`
- `fail_closed`
- `approval_consume_mode`
- `approval_consumed`
- `route_plan`
- `tool_results`
- `step_result_wrappers`
- `orchestrator_plan`
- `dependency_graph`
- `failure_strategy`
- `rollback_strategy`
- `preflight`
- `gates`
- `audit`
- `blocked_reasons`
- `safety`
- `ui`

안전 계약:

- 기본값 `FULL_AUTOMATION_DISPATCH_ENABLED=false`에서는 approval을 소비하지 않고 실제 dispatch도 하지 않는다.
- read-only step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`, preflight ready, `wrapper.untrusted=true`가 모두 필요하다.
- shell step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `SHELL_EXECUTION_ENABLED=true`, valid shell approval, allowlist command, allowed cwd, payload hash/session binding이 모두 필요하다.
- patch step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `PATCH_APPLY_ENABLED=true`, valid patch approval, allowed root, 기존 UTF-8 단일 파일, `original_sha256` precondition, secret scan이 모두 필요하다.
- rollback step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `ROLLBACK_EXECUTOR_ENABLED=true`, valid rollback approval, allowed root, 기존 UTF-8 단일 파일, current/original hash precondition이 모두 필요하다.
- task queue step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `TASK_QUEUE_WORKER_ENABLED=true`, `wrapper.untrusted=true`, read-only task type이 모두 필요하다. 허용 task type은 `noop`, `read_only_scan`, `file_preview`뿐이다.
- browser observe step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `BROWSER_OBSERVE_ENABLED=true`, valid browser approval, loopback/명시 allowlist URL, read-only observe action이 모두 필요하다.
- browser limited step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `BROWSER_LIMITED_INTERACTION_ENABLED=true`, valid browser approval, loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist가 모두 필요하다.
- external web search step 실행에는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, provider configured, rate limit, query safety, `wrapper.untrusted=true`가 모두 필요하다.
- app-os step 처리는 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `wrapper.untrusted=true`, observe-plan action이 모두 필요하다. 성공해도 preview wrapper만 중첩하며 실제 OS action은 수행하지 않는다.
- 47차 safe orchestrator는 browser observe metadata connector, browser limited candidate validation connector, external web search provider connector, app-os observe-plan preview connector만 제한적으로 호출하고, browser actual interaction/app-os actual action connector를 직접 호출하지 않는다.
- `gates`와 `audit.payload`의 `safe_connector_execution_connected`, `preview_connector_execution_connected`, `mutating_connector_execution_connected`, `browser_actual_interaction_connected`, `app_os_actual_action_connected`, `action_loop_full_dispatch_connected`는 실제 연결 범위와 일치해야 한다.
- 48차 Decision Required 기준에서 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`는 사용자 최종 승인과 Opus 리뷰 전까지 유지한다.
- 61~73차 Local Jarvis runtime drift guard, failure/timeout drill, manual review packet, approval console state-only review, approval payload hash review, approval store expiry cleanup review, approval console API surface Decision Required, approval-console-read-only API, Durable Automation v2 Candidate Decision Required, Durable State Preview Schema Candidate, and Durable State Preview API Surface Decision Required 기준에서 `docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md`, `docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md`, `docs/LOCAL_JARVIS_APPROVAL_CONSOLE_API_SURFACE_DECISION_REQUIRED.md`, `docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md`, `docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md`는 public docs link contract에 포함되어야 하고, actual action false assertions는 runtime `gates`, `audit.payload`, `safety`와 일치해야 한다. approval console approve/reject는 state-only이며 no execution on approve를 유지해야 한다. 70차 기준 read-only pending/list/detail/cleanup endpoint만 추가했고 approve/reject routes not added 상태다. 71차 기준 durable-automation-v2-candidate-decision-required는 no durable worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery를 유지한다. 72차 기준 durable-state-preview-schema-candidate는 `state_schema_version=durable_state_preview.v1`, proposal-only contract, schema-only, no durable storage migration, no durable table created, `state_preview_is_not_execution`, `state_preview_does_not_consume_approval`, `state_preview_does_not_mutate_queue`, `would_persist=false`, `approval_consumed=false`를 유지한다. 73차 기준 durable-state-preview-api-surface-decision-required는 endpoint exposure remains blocked, no durable-state-preview endpoints added, route_absence_is_required, `would_expose_endpoint=false`를 유지한다.
- `step_result_wrappers`는 `assistant.full_automation.step_result_wrapper.v1`이며 raw content, approval-like JSON, next action, frozen plan mutation을 허용하지 않는다.
- read-only adapter 결과는 기존 `assistant.read_only_adapter.result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩한다.
- shell stdout/stderr는 기존 shell sandbox의 secret-like masking과 max bytes cap을 거친 뒤 full automation step wrapper 안에 untrusted로 중첩한다.
- patch result는 기존 `assistant.patch_apply.v1` audit과 rollback preview metadata를 full automation step wrapper 안에 untrusted로 중첩한다.
- rollback result는 기존 `assistant.rollback_execute.v1` audit과 `assistant.rollback_execute.result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩한다.
- task queue result는 기존 `assistant.task_queue.worker_result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩한다.
- browser observe result는 기존 `assistant.browser_observe.result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩한다.
- browser limited result는 기존 `assistant.browser_limited_interact.result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩하며 성공 응답도 `would_interact=false`, `interaction_executed=false`, `browser_launch=not_performed`를 유지한다.
- external web search result는 기존 `assistant.external_web_search.result_wrapper.v1` wrapper를 full automation step wrapper 안에 untrusted로 중첩하며 API key 원문, raw content, next action authority를 반환하지 않는다.
- app-os preview result는 기존 `assistant.app_os.interaction_gate.preview.v1` audit을 full automation step wrapper 안에 untrusted로 중첩하며 `would_control_app=false`, `os_action_executed=false`, `can_set_next_action=false`를 유지한다.
- shell/patch/rollback/browser observe/browser limited approval은 해당 step이 실제 실행될 때만 기존 boundary에서 single-use로 consume한다. read-only step과 task queue step은 approval을 consume하지 않는다.
- `orchestrator_plan`, `dependency_graph`, `failure_strategy`, `rollback_strategy`는 audit 가능한 metadata이며 mutating 실행 권한이 아니다.
- browser actual interaction, app-os control, daemon/service, git reset/bulk restore, 운영 배포는 계속 미연결이다.

### `POST /assistant/workspace-brief`

프로젝트 구조 scan과 중요 파일의 masked preview를 묶어 read-only workspace brief를 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/workspace-brief \
  -H "Content-Type: application/json" \
  -d '{"project_root":"/Users/juyoung/local-ai-server","include_previews":true}'
```

응답 핵심 필드:

- `service`
- `project_root`
- `mode=read-only-workspace-brief`
- `would_execute=false`
- `scan`
- `previews`
- `next_safe_actions`
- `safety`
- `ui`

### `POST /assistant/shell-preview`

5차 shell sandbox preview다. allowlist, cwd 제한, timeout, output masking, audit payload만 반환하며 실제 subprocess 실행은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/shell-preview \
  -H "Content-Type: application/json" \
  -d '{"command":"git status","cwd":"/Users/juyoung/local-ai-server","timeout_seconds":30}'
```

응답 핵심 필드:

- `service`
- `mode=shell-sandbox-preview`
- `command_preview`
- `cwd`
- `resolved_cwd`
- `status`
- `would_execute=false`
- `allowed`
- `reason`
- `timeout_seconds`
- `policy`
- `audit`
- `output_preview`
- `safety`
- `ui`

### `POST /assistant/shell-approval-preview`

shell 후보 명령을 단일 서버 발급 approval payload에 binding하는 preview다. approval은 process-local in-memory store에 저장되며 single-use, session/request context, payload_hash, TTL에 바인딩된다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/shell-approval-preview \
  -H "Content-Type: application/json" \
  -d '{"command":"git status","cwd":"/Users/juyoung/local-ai-server","timeout_seconds":30,"reason":"local CI"}'
```

응답 핵심 필드:

- `service`
- `mode=shell-approval-binding-preview`
- `status`
- `approval_required`
- `would_execute=false`
- `binding`
- `preview`
- `safety`
- `ui`

### `POST /assistant/shell-run`

27차 Shell Sandbox v1 실행 endpoint다. 기본값 `SHELL_EXECUTION_ENABLED=false`에서는 allowlist preview와 서버 발급 approval binding이 유효해도 `status=disabled`, `execution_enabled=false`, `would_execute=false`를 반환한다. `SHELL_EXECUTION_ENABLED=true`일 때만 allowlist command, `AGENT_ALLOWED_ROOTS` 안쪽 cwd, 1~120초 timeout, 서버 발급 single-use approval, session/request context binding, payload_hash binding을 모두 통과한 단건 subprocess를 `shell=False`로 실행한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/shell-run \
  -H "Content-Type: application/json" \
  -d '{"command":"git status","cwd":"/Users/juyoung/local-ai-server","timeout_seconds":30}'
```

응답 핵심 필드:

- `service`
- `mode=shell-run-locked` 또는 `mode=shell-sandbox-v1`
- `status`
- `would_execute`
- `execution_enabled`
- `reason`
- `preview`
- `output`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `audit`
- `safety`
- `ui`

`output`은 secret-like masking과 byte cap 적용 후 `stdout`, `stderr`, `exit_code`, `timeout`, `stdout_truncated`, `stderr_truncated`, `stdout_masked`, `stderr_masked`, `paste_safe_summary`를 반환한다. timeout이나 non-zero exit도 paste-safe summary로 반환하며 action-loop dispatch에는 연결하지 않는다.

### `POST /assistant/durable-state-preview/preview`

74차 Durable State Preview Read-only API Candidate endpoint다. protected endpoint only이며 `LOCAL_API_KEY`가 설정된 경우 `X-API-Key`가 필요하다. 이 endpoint는 response-only/read-only/schema-only preview만 반환하고 durable storage migration, durable table creation, queue mutation, worker, scheduler, replay, recovery, connector dispatch를 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/durable-state-preview/preview \
  -H "Content-Type: application/json" \
  -d '{"goal":"durable preview","proposed_steps":[],"require_schema_only":true,"require_read_only":true,"require_no_persistence":true}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `preview_state`
- `preview_state.state_schema_version=durable_state_preview.v1`
- `preview_state.state_status=candidate-preview`
- `candidate_steps`
- `read_only`
- `schema_only`
- `response_only`
- `would_execute`
- `would_persist`
- `would_dispatch`
- `approval_consumed`
- `gates`
- `audit`
- `audit.schema=assistant.durable_state_preview.read_only.v1`
- `audit.audit_summary_hash`
- `blocked_reasons`
- `required_user_decisions`
- `safety`
- `ui`

대표 값은 `mode=durable-state-preview-read-only`, `status=completed`, `read_only=true`, `schema_only=true`, `response_only=true`, `would_execute=false`, `would_persist=false`, `would_dispatch=false`, `approval_consumed=false`다.

응답은 masked response only다. raw approval id not included, payload_hash not included 정책을 유지하며 approval-like JSON injection은 실행 또는 approval revive 권한이 아니다.

명시적으로 추가하지 않은 route:

- `GET /assistant/durable-state-preview/{preview_state_id} remains absent`
- `GET /assistant/durable-state-preview remains absent`
- `POST /assistant/durable-state-preview/cleanup-expired remains absent`

stored preview lookup/list/cleanup remain Decision Required 상태다. `stored_preview_lookup_connected=false`, `stored_preview_list_connected=false`, `stored_preview_cleanup_connected=false`, `durable_storage_migration_connected=false`, `durable_table_created=false`, `persistence_mutation_connected=false`, `queue_mutation_connected=false`, `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 고정한다.

75차 Durable State Preview API Regression Guard는 이 endpoint가 계속 단일 protected preview route로만 남는지 확인한다. `approval_id`, `approval_payload_hash`, `payload_hash`, `token`, `password` 계열 key는 `candidate_steps`와 `metadata` 양쪽에서 `[REDACTED]` 처리되어야 하며 stored preview lookup/list/cleanup route는 계속 absent다.

76차 Durable State Preview Docs/API Drift Guard는 이 섹션의 API docs response fields가 `AssistantDurableStatePreviewResponse`와 계속 일치하는지 확인한다. public docs endpoint listing, security boundary, release summary, handoff도 `POST /assistant/durable-state-preview/preview` protected endpoint only, response-only/read-only/schema-only, no persistence mutation, no approval consume, no queue mutation 범위를 유지해야 한다.

### Approval Console Read-only API

70차 Local Jarvis Approval Console Read-only API Candidate endpoint다. protected endpoint only이며 실제 실행, approve/reject, approval consume을 수행하지 않는다. 응답은 masked response only이고 raw approval id not included, payload_hash not included 정책을 따른다.

- `GET /assistant/approval-console/pending`: pending/list view. `approval-console-read-only`, `would_execute=false`, `approval_consumed=false`를 반환한다.
- `GET /assistant/approval-console/{approval_id}`: detail view. path의 approval id는 조회에만 쓰고 응답에는 `approval_ref`만 포함한다.
- `POST /assistant/approval-console/cleanup-expired`: TTL cleanup exposure. `expired_count`, `records_removed`, paste-safe summary를 반환하며 cleanup is not approval consume이다.

명시적으로 추가하지 않은 route:

- `POST /assistant/approval-console/{approval_id}/approve` remains absent
- `POST /assistant/approval-console/{approval_id}/reject` remains absent

응답 핵심 필드:

- `service`
- `mode=approval-console-read-only`
- `status`
- `read_only=true`
- `would_execute=false`
- `approval_consumed=false`
- `approvals` 또는 `approval` 또는 `cleanup`
- `gates`
- `audit.audit_summary_hash`
- `safety`
- `ui`

### `POST /assistant/patch-preview`

6차 patch sandbox preview다. 허용 root 안의 기존 UTF-8 텍스트 파일만 대상으로 diff, secret scan, rollback note, audit payload를 반환하며 실제 파일 수정은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/patch-preview \
  -H "Content-Type: application/json" \
  -d '{"path":"/Users/juyoung/local-ai-server/README.md","proposed_content":"# local-ai-server\n","project_root":"/Users/juyoung/local-ai-server"}'
```

응답 핵심 필드:

- `service`
- `mode=patch-preview-locked`
- `path`
- `resolved_path`
- `status`
- `would_apply=false`
- `allowed`
- `reason`
- `diff_preview`
- `truncated`
- `secret_scan`
- `rollback`
- `audit`
- `safety`
- `ui`

### `POST /assistant/patch-approval-preview`

patch 후보를 단일 서버 발급 approval payload에 binding하는 preview다. approval은 process-local in-memory store에 저장되며 single-use, session/request context, payload_hash, TTL에 바인딩된다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/patch-approval-preview \
  -H "Content-Type: application/json" \
  -d '{"path":"/Users/juyoung/local-ai-server/README.md","proposed_content":"# local-ai-server\n","project_root":"/Users/juyoung/local-ai-server","reason":"docs"}'
```

응답 핵심 필드:

- `service`
- `mode=patch-approval-binding-preview`
- `status`
- `approval_required`
- `would_apply=false`
- `binding`
- `preview`
- `safety`
- `ui`

### `POST /assistant/patch-apply`

29차 Patch Apply Sandbox v1 endpoint다. 기본값 `PATCH_APPLY_ENABLED=false`에서는 patch preview와 서버 발급 approval binding이 유효해도 `status=disabled`, `execution_enabled=false`, `would_apply=false`를 반환한다. `PATCH_APPLY_ENABLED=true`일 때만 허용 root 안의 기존 UTF-8 텍스트 단일 파일, secret scan 통과, 서버 발급 single-use approval, session/request context binding, payload_hash binding, `original_sha256` precondition을 모두 만족하면 proposed content로 파일을 덮어쓴다. 파일 생성/삭제, bulk apply, binary file, sensitive path, workspace 밖 path, 자동 rollback, action-loop dispatch 연결은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/patch-apply \
  -H "Content-Type: application/json" \
  -d '{"path":"/Users/juyoung/local-ai-server/README.md","proposed_content":"# local-ai-server\n","project_root":"/Users/juyoung/local-ai-server","original_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","approval_id":"server-issued","approval_payload_hash":"preview-payload-hash"}'
```

응답 핵심 필드:

- `service`
- `mode=patch-apply-locked` 또는 `mode=patch-apply-v1`
- `status`
- `would_apply`
- `execution_enabled`
- `reason`
- `preview`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `apply_result`
- `rollback`
- `audit`
- `safety`
- `ui`

### `POST /assistant/browser-preview`

7차 browser/app interaction preview다. read-only action taxonomy, 금지 action, URL 형식, OS app control 차단 여부, masking된 audit payload만 반환하며 실제 브라우저 또는 앱 조작은 수행하지 않는다.
18차 Browser Interaction Sandbox gate 보강 이후 응답에는 `gate.schema=assistant.browser_interaction.gate.v1`도 포함된다. 이 gate는 observe/read 계열을 allowed candidate로만 표시하고, click/fill/submit/login/payment/delete 및 browser launch는 계속 차단한다. domain allowlist는 `domain_allowlist_candidate.mode=design-only`로만 노출되며 실제 browser/network control에는 사용되지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/browser-preview \
  -H "Content-Type: application/json" \
  -d '{"action":"observe","target_url":"https://example.com","reason":"read-only QA"}'
```

응답 핵심 필드:

- `service`
- `mode=browser-interaction-preview-locked`
- `status`
- `action`
- `target_url`
- `app_name`
- `would_interact=false`
- `allowed`
- `reason`
- `risk`
- `required_manual_confirmation=true`
- `taxonomy`
- `gate`
- `audit`
- `safety`
- `ui`

### `POST /assistant/browser-approval-preview`

browser/app 후보를 단일 서버 발급 approval payload에 binding하는 preview다. approval은 process-local in-memory store에 저장되며 single-use, session/request context, payload_hash, TTL에 바인딩된다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/browser-approval-preview \
  -H "Content-Type: application/json" \
  -d '{"action":"screenshot","target_url":"https://example.com","reason":"read-only QA"}'
```

응답 핵심 필드:

- `service`
- `mode=browser-approval-binding-preview`
- `status`
- `approval_required`
- `would_interact=false`
- `binding`
- `preview`
- `safety`
- `ui`

### `POST /assistant/browser-interact`

interaction endpoint 이름을 갖지만 7차 기본값에서는 locked/disabled다. browser preview와 서버 발급 approval binding을 검증한 뒤에도 `execution_enabled=false`, `would_interact=false`를 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/browser-interact \
  -H "Content-Type: application/json" \
  -d '{"action":"observe","target_url":"https://example.com"}'
```

응답 핵심 필드:

- `service`
- `mode=browser-interact-locked`
- `status`
- `would_interact=false`
- `execution_enabled=false`
- `reason`
- `preview`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `safety`
- `ui`

### `POST /assistant/browser-observe`

31차 Browser Observe v1 endpoint다. 기본값은 `BROWSER_OBSERVE_ENABLED=false`이며 disabled 상태에서는 approval을 소비하지 않는다. `BROWSER_OBSERVE_ENABLED=true`와 서버 발급 browser approval이 모두 유효할 때만 loopback 또는 `BROWSER_OBSERVE_ALLOWED_ORIGINS`에 명시된 origin에 대해 read-only observe 계열 metadata를 조회한다. 실제 click/fill/type/submit/login/payment/delete/download/upload/file dialog, browser profile/session mutation, OS app control, action-loop browser dispatch는 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/browser-observe \
  -H "Content-Type: application/json" \
  -d '{"action":"page_title","target_url":"http://127.0.0.1:8000/docs"}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `action`
- `target_url`
- `would_observe`
- `execution_enabled`
- `reason`
- `preview`
- `observe_result`
- `result_wrapper`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `audit`
- `safety`
- `ui`

### `POST /assistant/browser-limited-interact`

32차 Browser Limited Interaction v1 endpoint다. 기본값은 `BROWSER_LIMITED_INTERACTION_ENABLED=false`이며 disabled 상태에서는 approval을 소비하지 않는다. 현재 v1은 실제 browser engine launch/click/fill을 수행하지 않고, loopback 또는 명시 allowlist origin, selector allowlist, safe fill field allowlist, 서버 approval binding을 모두 검증한 뒤 candidate result를 untrusted wrapper로 반환한다. login/payment/delete/credential/password/token/secret/submit/download/upload/file dialog, persistent profile/session mutation, action-loop browser dispatch, OS app control은 계속 차단한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/browser-limited-interact \
  -H "Content-Type: application/json" \
  -d '{"action":"click","target_url":"http://127.0.0.1:8000/docs","selector":"#ok"}'
```

응답 핵심 필드:

- `service`
- `mode`
- `status`
- `action`
- `target_url`
- `selector`
- `would_interact`
- `execution_enabled`
- `reason`
- `policy`
- `interaction_result`
- `result_wrapper`
- `required_approval_hash`
- `provided_approval_id`
- `provided_approval_hash`
- `approval_check`
- `audit`
- `safety`
- `ui`

### `POST /assistant/action-loop-preflight`

8차 action-loop dispatch preflight다. frozen plan, wrapper 강제, approval binding, payload hash gate만 확인하며 실제 dispatch, shell 실행, patch apply, browser/app interaction은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-preflight \
  -H "Content-Type: application/json" \
  -d '{"goal":"개인 API dispatch","proposed_steps":[]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-dispatch-preflight-locked`
- `status`
- `goal`
- `would_dispatch=false`
- `execution_enabled=false`
- `fail_closed`
- `frozen_plan`
- `step_previews`
- `gates`
- `required_user_decisions`
- `safety`
- `ui`

### `POST /assistant/action-loop-noop-dispatch`

10차 no-op dispatcher dry-run이다. action-loop preflight 결과를 route plan과 noop audit으로 변환하지만 실제 dispatch, shell 실행, patch apply, browser/app interaction은 수행하지 않는다. approval은 consume하지 않고 validate-only로 확인한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-noop-dispatch \
  -H "Content-Type: application/json" \
  -d '{"goal":"개인 API dispatch","proposed_steps":[]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-noop-dispatch-preview`
- `status`
- `goal`
- `would_dispatch=false`
- `would_dispatch_noop_only`
- `execution_enabled=false`
- `fail_closed`
- `approval_consume_mode`
- `route_plan`
- `noop_audit`
- `preflight`
- `gates`
- `required_user_decisions`
- `safety`
- `ui`

### `POST /assistant/action-loop-read-only-dispatch-preview`

11차 read-only dispatch boundary preview다. `read_only_scan`, `file_preview`, `url_preview`, `workspace_brief` 후보를 classification-only route plan으로 분류하지만 실제 파일 내용 읽기, 폴더 스캔, URL fetch, dispatch는 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-read-only-dispatch-preview \
  -H "Content-Type: application/json" \
  -d '{"goal":"read only dispatch","proposed_steps":[]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-read-only-dispatch-boundary-preview`
- `status`
- `goal`
- `would_dispatch=false`
- `would_read=false`
- `would_fetch=false`
- `execution_enabled=false`
- `fail_closed`
- `boundary_mode=classification-only`
- `route_plan`
- `result_wrapper_schema`
- `boundary_audit`
- `gates`
- `safety`
- `ui`

`result_wrapper_schema`는 13차 preview-only 계약이다. schema 값은 `assistant.action_loop.read_only_result_wrapper.v1`이며 `raw_content_allowed=false`, `approval_like_json_trusted=false`, `can_mutate_frozen_plan=false`, `can_set_next_action=false`를 유지한다. 자세한 계약은 `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`를 본다.

### `POST /assistant/action-loop-read-only-dispatch`

26차 Read-only Action-loop Dispatch endpoint다. 기본값 `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=false`에서는 `disabled`를 반환한다. `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`가 모두 설정된 경우에만 frozen proposed_steps 중 read-only adapter 후보를 실제 read-only로 호출한다. shell, patch, browser dispatch는 연결하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-read-only-dispatch \
  -H "Content-Type: application/json" \
  -d '{"goal":"read workspace","project_root":"/Users/juyoung/local-ai-server","proposed_steps":[{"tool":"file_preview","params":{"path":"/Users/juyoung/local-ai-server/README.md"},"wrapper":{"untrusted":true}}]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-read-only-dispatch`
- `status`
- `goal`
- `dispatched`
- `execution_enabled`
- `fail_closed`
- `would_read`
- `would_fetch`
- `shell_execution_connected=false`
- `patch_apply_connected=false`
- `browser_interaction_connected=false`
- `adapter_results`
- `boundary_preview`
- `gates`
- `audit`
- `safety`
- `ui`

### `POST /assistant/action-loop-shell-dispatch`

28차 Shell Action-loop Integration endpoint다. 기본값 `SHELL_ACTION_LOOP_DISPATCH_ENABLED=false`에서는 `disabled`를 반환하고 approval을 소비하지 않는다. `SHELL_ACTION_LOOP_DISPATCH_ENABLED=true`와 `SHELL_EXECUTION_ENABLED=true`가 모두 설정된 경우에만 frozen proposed_steps 중 `tool=shell` step을 27차 `/assistant/shell-run` allowlist 계약으로 호출한다. patch, browser, external API, task worker, rollback, app-os dispatch는 연결하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-shell-dispatch \
  -H "Content-Type: application/json" \
  -d '{"goal":"run safe shell","project_root":"/Users/juyoung/local-ai-server","proposed_steps":[{"tool":"shell","params":{"command":"pwd","cwd":"/Users/juyoung/local-ai-server"},"wrapper":{"untrusted":true},"approval_binding":{"approval_id":"server-issued","payload_hash":"preview-hash","session_id":"session-1"}}]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-shell-dispatch`
- `status`
- `goal`
- `dispatched`
- `execution_enabled`
- `fail_closed`
- `shell_execution_connected`
- `patch_apply_connected=false`
- `browser_interaction_connected=false`
- `route_plan`
- `shell_results`
- `gates`
- `audit`
- `safety`
- `ui`

`shell_results`는 `assistant.action_loop.shell_result_wrapper.v1` wrapper로 감싼다. wrapper는 `untrusted=true`, `approval_like_json_trusted=false`, `can_mutate_frozen_plan=false`, `can_set_next_action=false`를 유지한다.

### `POST /assistant/action-loop-patch-dispatch`

30차 Patch Action-loop Integration endpoint다. 기본값 `PATCH_ACTION_LOOP_DISPATCH_ENABLED=false`에서는 `disabled`를 반환하고 approval을 소비하지 않는다. `PATCH_ACTION_LOOP_DISPATCH_ENABLED=true`와 `PATCH_APPLY_ENABLED=true`가 모두 설정된 경우에만 frozen proposed_steps 중 `tool=patch` step을 29차 `/assistant/patch-apply` 단일 파일 계약으로 호출한다. shell, browser, external API, task worker, rollback executor, app-os dispatch는 연결하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-loop-patch-dispatch \
  -H "Content-Type: application/json" \
  -d '{"goal":"apply safe patch","project_root":"/Users/juyoung/local-ai-server","proposed_steps":[{"tool":"patch","params":{"path":"/Users/juyoung/local-ai-server/README.md","proposed_content":"# local-ai-server\n","project_root":"/Users/juyoung/local-ai-server","original_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"wrapper":{"untrusted":true},"approval_binding":{"approval_id":"server-issued","payload_hash":"preview-payload-hash","session_id":"session-1"}}]}'
```

응답 핵심 필드:

- `service`
- `mode=action-loop-patch-dispatch`
- `status`
- `goal`
- `dispatched`
- `execution_enabled`
- `fail_closed`
- `shell_execution_connected=false`
- `patch_apply_connected`
- `browser_interaction_connected=false`
- `route_plan`
- `patch_results`
- `gates`
- `audit`
- `safety`
- `ui`

`patch_results`는 `assistant.action_loop.patch_result_wrapper.v1` wrapper로 감싼다. wrapper는 `untrusted=true`, `approval_like_json_trusted=false`, `can_mutate_frozen_plan=false`, `can_set_next_action=false`를 유지한다.

### `GET /assistant/ping`

브라우저 UI가 서버 연결, 인증 header, 로컬 API ready 상태를 가볍게 확인한다.

```bash
curl http://127.0.0.1:8000/assistant/ping
```

응답 핵심 필드:

- `service`
- `status=ok`
- `protected`
- `local_only`
- `ui_ready`

### `GET /assistant/config`

브라우저 UI가 사용할 수 있는 설정을 secret 없이 조회한다. `LOCAL_API_KEY` 값은 반환하지 않고 `protected` 여부만 반환한다.

```bash
curl http://127.0.0.1:8000/assistant/config
```

응답 핵심 필드:

- `service`
- `local_only`
- `protected`
- `cors_origins`
- `allowed_roots`
- `models`
- `storage`
- `safety`
- `rate_limit`

### `GET /assistant/ui-contract`

브라우저 UI가 따라야 할 시작 순서, refresh endpoint, 메시지 흐름, 응답 타입, 차단 기능을 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/ui-contract
```

응답 핵심 필드:

- `service`
- `version`
- `protected`
- `startup_sequence`
- `refresh_endpoints`
- `message_flow`
- `response_types`
- `blocked_actions`
- `safety`
- `auth.secret_returned=false`
- `notes`

### `GET /assistant/startup`

브라우저 UI의 첫 로딩에 필요한 `ping`, `config`, `dashboard`, `ui_contract`를 read-only snapshot으로 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/startup
```

응답 핵심 필드:

- `service`
- `local_only`
- `protected`
- `ping`
- `config`
- `dashboard`
- `ui_contract`
- `recommended_calls`
- `safety`
- `ui`

### `GET /assistant/status`

UI 첫 화면에서 필요한 현재 차수, 문서 저장소 요약, integrity 요약, assistant 세션 요약, 안전 상태를 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/status
```

응답 핵심 필드:

- `service`
- `current_phase`
- `documents`
- `integrity`
- `sessions`
- `safety`

### `GET /assistant/dashboard`

UI 첫 화면 카드에 바로 쓰기 좋은 문서, 세션, integrity, 연결 상태와 최근 세션 목록을 반환한다.

```bash
curl http://127.0.0.1:8000/assistant/dashboard
```

응답 핵심 필드:

- `service`
- `current_phase`
- `cards.documents`
- `cards.integrity`
- `cards.sessions`
- `cards.connection`
- `recent_sessions`
- `safety`
- `ui`

### `POST /assistant/bootstrap`

브라우저 UI 시작 흐름에서 필요한 capabilities, status, project root 검증 결과, 최근 session 목록, UI 표시 힌트를 한 번에 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "project_root":"/Users/juyoung/local-ai-server",
    "include_sessions":true,
    "sessions_limit":10
  }'
```

응답 핵심 필드:

- `service`
- `capabilities`
- `status`
- `project_root`
- `sessions`
- `recommended_calls`
- `ui.ready`
- `ui.blocked_actions`

### `POST /assistant/sessions`

assistant 대화 세션을 생성한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo","project_root":"/Users/juyoung/local-ai-server"}'
```

### `GET /assistant/sessions`

assistant 최근 세션 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/assistant/sessions?limit=20&offset=0"
```

응답 핵심 필드:

- `sessions`
- `sessions[].session_id`
- `sessions[].messages_count`
- `sessions[].last_message_preview`
- `limit`
- `offset`

### `GET /assistant/sessions/{session_id}`

assistant 세션과 메시지 기록을 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/sessions/<session_id>
```

### `GET /assistant/sessions/{session_id}/messages`

assistant 세션 메시지를 paging으로 조회한다. UI에서 긴 대화 기록을 렌더링할 때 사용한다.

```bash
curl "http://127.0.0.1:8000/assistant/sessions/<session_id>/messages?limit=50&offset=0"
```

응답 핵심 필드:

- `session_id`
- `total_messages`
- `limit`
- `offset`
- `messages`

### `POST /assistant/message`

UI 입력창에서 들어온 문장을 자동 분기한다. `mode=auto`에서는 문서 RAG, 검색, folder index preview, agent plan, shell dry-run 중 안전한 경로로 분류한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/message \
  -H "Content-Type: application/json" \
  -d '{"message":"내 문서 기준으로 JWT 설명해줘","project_root":"/Users/juyoung/local-ai-server","mode":"auto"}'
```

응답 핵심 필드:

- `session_id`
- `type`
- `answer`
- `data`
- `used_documents`
- `sources`
- `request_id`
- `safety`
- `ui`

안전 기준:

- 폴더 색인은 assistant API에서 preview-only로 처리한다.
- shell은 실제 실행하지 않고 dry-run 정책 판단만 반환한다.
- 브라우저 클릭, 파일 수정/삭제, 외부 LLM API 호출은 수행하지 않는다.

### `POST /assistant/project-root/validate`

UI에서 입력한 project root가 존재하는 폴더인지, `AGENT_ALLOWED_ROOTS` 안에 있는지 확인한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/project-root/validate \
  -H "Content-Type: application/json" \
  -d '{"project_root":"/Users/juyoung/local-ai-server"}'
```

## Ask

### `POST /ask`

문서 검색 없이 Ollama local chat API로 답변한다. 질문과 답변은 SQLite `chat_logs`에 저장된다.

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Spring Boot가 뭐야?","temperature":0.2}'
```

응답 핵심 필드:

- `answer`
- `model`
- `used_documents=false`
- `request_id`

### `POST /ask-with-docs`

Chroma에서 관련 chunk를 검색한 뒤, 검색 context 기반으로 Ollama local chat API를 호출한다.

```bash
curl -X POST http://127.0.0.1:8000/ask-with-docs \
  -H "Content-Type: application/json" \
  -d '{"question":"내 문서 기준으로 JWT 인증 흐름 설명해줘","top_k":5,"temperature":0.2}'
```

응답 핵심 필드:

- `answer`
- `model`
- `used_documents=true`
- `sources`
- `request_id`

RAG 답변은 문서 밖 코드, 링크, 보안 세부사항, 추측성 표현을 감지하면 보수적인 fallback 답변으로 대체될 수 있다.

## Documents

### `POST /documents/upload`

문서를 업로드하고 SQLite/Chroma에 색인한다.

지원 형식:

- 기본: `.txt`, `.md`, `.html`, `.htm`
- optional dependency 필요: `.pdf`, `.docx`

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@./notes/backend.md"
```

응답 예:

```json
{
  "document_id": 1,
  "filename": "backend.md",
  "chunks_created": 3
}
```

응답 핵심 필드:

- `document_id`
- `filename`
- `chunks_created`

### `POST /documents/index-folder-preview`

실제 저장 전에 폴더 색인 예상 작업량을 read-only로 확인한다. 원본 파일 수정, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder-preview \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 예시:

```json
{
  "folder_path": "/Users/example/notes",
  "recursive": true,
  "files_count": 2,
  "skipped_files_count": 1,
  "chunks_estimated": 5,
  "embedding_batch_size": 8,
  "embedding_batches_estimated": 1,
  "token_estimate": 1200,
  "files": [
    {
      "path": "/Users/example/notes/backend.md",
      "filename": "backend.md",
      "file_type": "md",
      "chunks_estimated": 3,
      "embedding_batches_estimated": 1,
      "token_estimate": 700
    },
    {
      "path": "/Users/example/notes/security.txt",
      "filename": "security.txt",
      "file_type": "txt",
      "chunks_estimated": 2,
      "embedding_batches_estimated": 1,
      "token_estimate": 500
    }
  ],
  "skipped_files": [
    {
      "path": "/Users/example/notes/broken.pdf",
      "reason": "PDF에서 추출 가능한 텍스트가 없습니다."
    }
  ],
  "dry_run": true,
  "note": "미리보기 전용입니다. 파일 수정, DB 저장, embedding 생성, Chroma 저장은 수행하지 않습니다."
}
```

응답 핵심 필드:

- `folder_path`
- `recursive`
- `files_count`
- `skipped_files_count`
- `chunks_estimated`
- `embedding_batch_size`
- `embedding_batches_estimated`
- `token_estimate`
- `files`
- `skipped_files`
- `dry_run=true`
- `note`

### `POST /documents/index-folder-job-preview`

대용량 폴더 색인을 나중에 job/status API로 분리할 때 사용할 progress response schema를 preview-only로 확인한다. 이 endpoint는 queue 생성, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder-job-preview \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 예시:

```json
{
  "job_id": "preview-only",
  "status": "planned",
  "folder_path": "/Users/example/notes",
  "recursive": true,
  "dry_run": true,
  "would_enqueue": false,
  "progress": {
    "total_files": 3,
    "processed_files": 0,
    "indexed_documents": 0,
    "skipped_files": 1,
    "chunks_created": 0,
    "embedding_batches_total": 2,
    "embedding_batches_completed": 0,
    "percent": 0.0
  },
  "status_endpoint": "/documents/index-jobs/{job_id}",
  "note": "대용량 색인 job/status API의 preview-only 응답입니다. 현재 요청은 queue 생성, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않습니다."
}
```

응답 핵심 필드:

- `job_id`
- `status`
- `folder_path`
- `recursive`
- `dry_run`
- `would_enqueue`
- `progress`
- `status_endpoint`
- `note`

`progress`에는 `total_files`, `processed_files`, `indexed_documents`, `skipped_files`, `chunks_created`, `embedding_batches_total`, `embedding_batches_completed`, `percent`가 포함된다.

### `POST /documents/index-folder`

로컬 폴더의 지원 파일을 실제로 색인한다. 원본 폴더 파일은 수정하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 예시:

```json
{
  "indexed_documents": 2,
  "skipped_files": 1,
  "chunks_created": 5,
  "document_ids": [
    10,
    11
  ],
  "indexed_files": [
    {
      "path": "/Users/example/notes/backend.md",
      "document_id": 10,
      "filename": "backend.md",
      "file_type": "md",
      "chunks_created": 3
    },
    {
      "path": "/Users/example/notes/security.txt",
      "document_id": 11,
      "filename": "security.txt",
      "file_type": "txt",
      "chunks_created": 2
    }
  ],
  "skipped_file_details": [
    {
      "path": "/Users/example/notes/empty.md",
      "filename": "empty.md",
      "reason": "비어 있는 문서는 색인할 수 없습니다."
    }
  ]
}
```

응답 핵심 필드:

- `indexed_documents`
- `skipped_files`
- `chunks_created`
- `document_ids`
- `indexed_files`
- `skipped_file_details`

### `GET /documents`

문서 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/documents?source_type=upload&file_type=md&query=backend"
```

응답 예시:

```json
[
  {
    "id": 1,
    "original_filename": "backend.md",
    "stored_path": "data/uploads/backend.md",
    "file_type": "md",
    "source_type": "upload",
    "created_at": "2026-05-26T18:00:00",
    "chunks_count": 3
  },
  {
    "id": 2,
    "original_filename": "security-notes.md",
    "stored_path": "/Users/example/notes/security-notes.md",
    "file_type": "md",
    "source_type": "folder",
    "created_at": "2026-05-26T18:05:00",
    "chunks_count": 2
  }
]
```

필터:

- `source_type=upload|folder`
- `file_type=txt|md|pdf|docx|html`
- `query=<filename 또는 path keyword>`

응답 핵심 필드:

- `id`
- `original_filename`
- `stored_path`
- `file_type`
- `source_type`
- `created_at`
- `chunks_count`

### `GET /documents/{document_id}`

문서 상세와 chunk 목록을 조회한다.

```bash
curl http://127.0.0.1:8000/documents/1
```

응답 예시:

```json
{
  "id": 1,
  "original_filename": "backend.md",
  "stored_path": "data/uploads/backend.md",
  "file_type": "md",
  "source_type": "upload",
  "created_at": "2026-05-26T18:00:00",
  "chunks_count": 2,
  "chunks": [
    {
      "id": 10,
      "document_id": 1,
      "chunk_index": 0,
      "content": "Spring Boot controller and service notes.",
      "token_estimate": 8,
      "created_at": "2026-05-26T18:00:01"
    },
    {
      "id": 11,
      "document_id": 1,
      "chunk_index": 1,
      "content": "Repository and transaction boundary notes.",
      "token_estimate": 6,
      "created_at": "2026-05-26T18:00:02"
    }
  ]
}
```

응답 핵심 필드:

- `id`
- `original_filename`
- `stored_path`
- `file_type`
- `source_type`
- `created_at`
- `chunks_count`
- `chunks`

### `GET /documents/{document_id}/chunks`

문서 chunk를 페이지 단위로 조회한다.

```bash
curl "http://127.0.0.1:8000/documents/1/chunks?limit=20&offset=0"
```

응답 예시:

```json
{
  "document_id": 1,
  "total_chunks": 2,
  "limit": 20,
  "offset": 0,
  "chunks": [
    {
      "id": 10,
      "document_id": 1,
      "chunk_index": 0,
      "content": "Spring Boot controller and service notes.",
      "token_estimate": 8,
      "created_at": "2026-05-26T18:00:01"
    },
    {
      "id": 11,
      "document_id": 1,
      "chunk_index": 1,
      "content": "Repository and transaction boundary notes.",
      "token_estimate": 6,
      "created_at": "2026-05-26T18:00:02"
    }
  ]
}
```

응답 핵심 필드:

- `document_id`
- `total_chunks`
- `limit`
- `offset`
- `chunks`

### `DELETE /documents/{document_id}`

문서 metadata, chunk, vector를 삭제한다.

```bash
curl -X DELETE http://127.0.0.1:8000/documents/1
```

주의: 이 endpoint는 삭제 작업이므로 실제 사용자 데이터가 있는 환경에서는 신중하게 호출한다.

### `GET /documents/supported-types`

문서 타입별 사용 가능 여부를 확인한다.

```bash
curl http://127.0.0.1:8000/documents/supported-types
```

응답 예시:

```json
{
  "types": [
    {
      "extension": ".txt",
      "file_type": "txt",
      "available": true,
      "optional_dependency": null,
      "install_hint": null,
      "description": "Plain UTF-8 text."
    },
    {
      "extension": ".md",
      "file_type": "md",
      "available": true,
      "optional_dependency": null,
      "install_hint": null,
      "description": "Markdown text."
    },
    {
      "extension": ".html",
      "file_type": "html",
      "available": true,
      "optional_dependency": "beautifulsoup4",
      "install_hint": "pip install -e '.[documents]'",
      "description": "HTML body text without script/style/head content."
    },
    {
      "extension": ".pdf",
      "file_type": "pdf",
      "available": true,
      "optional_dependency": "pypdf",
      "install_hint": null,
      "description": "Text-based PDF with optional OCR fallback for PyPDF image XObjects."
    },
    {
      "extension": ".docx",
      "file_type": "docx",
      "available": false,
      "optional_dependency": "python-docx",
      "install_hint": "pip install -e '.[documents]'",
      "description": "Word document paragraphs and tables."
    }
  ],
  "install_hint": "PDF OCR은 pip install -e '.[ocr]'와 로컬 tesseract 설치가 필요합니다.",
  "pdf_ocr": false,
  "pdf_ocr_install_hint": "PDF OCR을 사용하려면 Python dependency와 로컬 tesseract binary가 필요합니다: pip install -e '.[ocr]' 후 brew install tesseract 또는 apt install tesseract-ocr를 실행하세요. 한국어 OCR은 tesseract language pack(kor)을 별도로 설치해야 합니다."
}
```

응답 핵심 필드:

- `types[]`
- `install_hint`
- `pdf_ocr`
- `pdf_ocr_install_hint`

`pdf_ocr=false`이면 이미지 기반 PDF OCR fallback을 사용할 수 없는 상태다. `pytesseract`, `Pillow`, 로컬 `tesseract` binary 중 하나라도 없으면 false가 된다. 일반 PDF 텍스트 추출은 `pdf_ocr`와 별개로 `[documents]` extra의 `pypdf` 준비 상태를 따른다.

### `GET /documents/stats`

SQLite/Chroma 저장 상태를 read-only로 확인한다.

```bash
curl http://127.0.0.1:8000/documents/stats
```

응답 예시:

```json
{
  "documents_count": 3,
  "chunks_count": 12,
  "chat_logs_count": 5,
  "feedback_count": 1,
  "chroma_vectors_count": 12,
  "missing_stored_files_count": 0,
  "missing_stored_files": []
}
```

응답 핵심 필드:

- `documents_count`
- `chunks_count`
- `chat_logs_count`
- `feedback_count`
- `chroma_vectors_count`
- `missing_stored_files_count`
- `missing_stored_files`

### `GET /documents/integrity`

SQLite chunk와 Chroma vector 정합성을 read-only로 확인한다.

```bash
curl http://127.0.0.1:8000/documents/integrity
```

응답 예시:

```json
{
  "status": "needs_attention",
  "sqlite_chunks_count": 12,
  "chroma_vectors_count": 11,
  "missing_stored_files_count": 1,
  "missing_stored_files": [
    {
      "document_id": 1,
      "original_filename": "missing.md",
      "stored_path": "/Users/example/local-ai-server/data/uploads/missing.md"
    }
  ],
  "chunks_missing_vectors_count": 1,
  "chunks_missing_vectors": [
    {
      "chunk_id": 10,
      "document_id": 1,
      "chunk_index": 0
    }
  ],
  "orphan_vectors_count": 1,
  "orphan_vector_chunk_ids": [
    99
  ],
  "repair_available": false,
  "repair_note": "현재 endpoint는 read-only dry-run입니다. 실제 repair/delete는 사용자 승인 후 별도 구현하세요."
}
```

응답 핵심 필드:

- `status`
- `sqlite_chunks_count`
- `chroma_vectors_count`
- `missing_stored_files_count`
- `missing_stored_files`
- `chunks_missing_vectors_count`
- `chunks_missing_vectors`
- `orphan_vectors_count`
- `orphan_vector_chunk_ids`
- `repair_available`
- `repair_note`

### `GET /documents/repair-preview`

필요한 repair action 후보만 반환한다. 실제 repair/delete/rebuild는 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/documents/repair-preview
```

응답 예시:

```json
{
  "status": "needs_repair",
  "dry_run": true,
  "actions_count": 3,
  "actions": [
    {
      "action": "review_missing_file",
      "target_type": "document",
      "target_id": 1,
      "reason": "stored_path가 존재하지 않습니다: /Users/example/local-ai-server/data/uploads/missing.md",
      "requires_user_approval": true
    },
    {
      "action": "rebuild_vector",
      "target_type": "chunk",
      "target_id": 10,
      "reason": "SQLite chunk는 있지만 Chroma vector가 없습니다.",
      "requires_user_approval": true
    },
    {
      "action": "review_orphan_vector",
      "target_type": "chroma_vector",
      "target_id": 99,
      "reason": "Chroma vector는 있지만 SQLite chunk가 없습니다.",
      "requires_user_approval": true
    }
  ],
  "note": "미리보기 전용입니다. 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않습니다."
}
```

응답 핵심 필드:

- `status`
- `dry_run`
- `actions_count`
- `actions`
- `note`

### `GET /documents/vector-rebuild-preview`

Chroma vector가 누락된 SQLite chunk만 대상으로 재생성 후보를 반환한다. 실제 Ollama embedding 생성, Chroma vector 재생성, DB 수정은 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/documents/vector-rebuild-preview
```

응답 예시:

```json
{
  "status": "needs_rebuild",
  "dry_run": true,
  "chunks_missing_vectors_count": 2,
  "embedding_batch_size": 8,
  "embedding_batches_estimated": 1,
  "actions_count": 2,
  "actions": [
    {
      "action": "rebuild_vector",
      "target_type": "chunk",
      "target_id": 10,
      "reason": "SQLite chunk는 있지만 Chroma vector가 없습니다.",
      "requires_user_approval": true
    },
    {
      "action": "rebuild_vector",
      "target_type": "chunk",
      "target_id": 11,
      "reason": "SQLite chunk는 있지만 Chroma vector가 없습니다.",
      "requires_user_approval": true
    }
  ],
  "note": "미리보기 전용입니다. 실제 Ollama embedding 생성, Chroma vector 재생성, DB 수정은 수행하지 않습니다."
}
```

응답 핵심 필드:

- `status`
- `dry_run`
- `chunks_missing_vectors_count`
- `embedding_batch_size`
- `embedding_batches_estimated`
- `actions_count`
- `actions`
- `note`

## Search

### `POST /search`

Ollama embedding과 Chroma를 사용해 의미 검색을 수행한다.

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"JWT authentication","top_k":5}'
```

응답 예시:

```json
{
  "query": "JWT authentication",
  "results": [
    {
      "chunk_id": 10,
      "document_id": 1,
      "filename": "backend.md",
      "chunk_index": 0,
      "content": "JWT authentication flow notes.",
      "score": 0.123
    }
  ]
}
```

응답 핵심 필드:

- `query`
- `results`
- `results[].chunk_id`
- `results[].document_id`
- `results[].filename`
- `results[].chunk_index`
- `results[].content`
- `results[].score`

## Chat Logs

### `GET /chat-logs`

질문/답변 기록 목록을 preview 형태로 조회한다.

```bash
curl "http://127.0.0.1:8000/chat-logs?limit=20&offset=0"
curl "http://127.0.0.1:8000/chat-logs?mode=rag&query=JWT&limit=20&offset=0"
```

응답 예시:

```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "mode": "rag",
  "query": "JWT",
  "items": [
    {
      "id": 1,
      "question_preview": "JWT 인증 흐름 설명해줘",
      "answer_preview": "문서 기준으로 JWT 인증은...",
      "mode": "rag",
      "model": "llama3.2",
      "used_sources_count": 2,
      "created_at": "2026-05-26T18:10:00"
    }
  ]
}
```

필터:

- `mode=direct|rag`
- `query=<keyword>`

응답 핵심 필드:

- `total`
- `limit`
- `offset`
- `mode`
- `query`
- `items`

### `GET /chat-logs/{chat_log_id}`

chat log 상세를 조회한다.

```bash
curl http://127.0.0.1:8000/chat-logs/1
```

응답 예시:

```json
{
  "id": 1,
  "question": "JWT 인증 흐름 설명해줘",
  "answer": "문서 기준으로 JWT 인증은 access token 검증과 권한 확인 흐름으로 설명할 수 있습니다.",
  "mode": "rag",
  "model": "llama3.2",
  "used_sources": [
    {
      "document_id": 1,
      "filename": "backend.md",
      "chunk_index": 0,
      "chunk_id": 10
    }
  ],
  "created_at": "2026-05-26T18:10:00"
}
```

응답 핵심 필드:

- `id`
- `question`
- `answer`
- `mode`
- `model`
- `used_sources`
- `created_at`

## Feedback

### `POST /feedback`

`request_id` 기준으로 답변 피드백을 저장한다.

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"request_id":"1","rating":"good","corrected_answer":"수정 답변","note":"좋은 답변"}'
```

응답 예시:

```json
{
  "feedback_id": 1,
  "chat_log_id": 1,
  "rating": "good"
}
```

`rating` 허용 값:

- `good`
- `bad`
- `neutral`

응답 핵심 필드:

- `feedback_id`
- `chat_log_id`
- `rating`

### `GET /feedback`

피드백 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/feedback?limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?rating=bad&limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?chat_log_id=1&limit=20&offset=0"
```

응답 예시:

```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "rating": "good",
  "chat_log_id": 1,
  "items": [
    {
      "id": 1,
      "chat_log_id": 1,
      "rating": "good",
      "corrected_answer_preview": "수정 답변",
      "note_preview": "좋은 답변",
      "created_at": "2026-05-26T18:15:00"
    }
  ]
}
```

응답 핵심 필드:

- `total`
- `limit`
- `offset`
- `rating`
- `chat_log_id`
- `items`

## Agent

### `POST /agent/plan`

실행형 Agent 요청을 preview-only 실행 계획으로 분류한다. 실제 웹 이동, 브라우저 클릭, 폴더 열기, 파일 수정, shell 실행은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/agent/plan \
  -H "Content-Type: application/json" \
  -d '{"instruction":"GitHub 웹 열고 내 폴더도 열어줘"}'
```

응답 핵심 필드:

- `run_id`
- `status=planned`
- `risk_level`
- `execution_enabled=false`
- `actions`
- `actions[].tool`
- `actions[].risk_level`
- `actions[].requires_approval`
- `note`

### `GET /agent/runs`

agent plan 기록을 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs
```

### `GET /agent/runs/{run_id}`

agent plan 상세를 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1
```

### `GET /agent/runs/{run_id}/actions`

agent action별 상태, dry-run 결과, execution 결과를 함께 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1/actions
```

### `POST /agent/runs/{run_id}/dry-run`

실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 실행 전 정책 판단만 기록한다.
dry-run 응답의 `would_execute`는 항상 `false`이며, 실제 `execute` 단계에서 현재 설정상 read-only 실행 후보가 될 수 있는지는 `execute_phase_would_run`으로 구분한다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/dry-run
```

### `POST /agent/runs/{run_id}/approve`

agent plan을 승인 상태로 바꾼다. 상태는 `approved_pending_execution`이 되며, 실제 실행은 별도 `execute` 호출에서만 시도한다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/approve
```

### `POST /agent/runs/{run_id}/reject`

agent plan을 거절 상태로 바꾼다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/reject
```

### `POST /agent/runs/{run_id}/execute`

승인된 agent run만 실행 시도한다. 기본값 `AGENT_EXECUTION_ENABLED=false`에서는 실제 실행을 차단하고 `blocked` 결과를 기록한다.

`AGENT_EXECUTION_ENABLED=true` 상태의 v1 실행 엔진은 아래만 지원한다.

- 허용 root 안의 폴더 read-only list 조회
- 허용 root 안의 텍스트 파일 read-only content preview
- 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자 차단
- `AGENT_WEB_FETCH_ENABLED=true`이고 명시 URL이 있는 경우 read-only URL fetch
- URL fetch 응답은 `AGENT_WEB_FETCH_MAX_BYTES` 이후 truncate

브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/execute
```

### `GET /agent/runs/{run_id}/results`

agent 실행 결과만 조회한다. 실행 전이면 빈 배열을 반환한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1/results
```

## CLI 대응

CLI는 위 API를 HTTP로 호출한다. CLI 내부에 비즈니스 로직을 중복 구현하지 않는다.

```bash
local-ai health
local-ai doctor
local-ai status
local-ai next
local-ai api-inventory
local-ai roots
local-ai shell-policy
local-ai shell-dry-run "pwd"
local-ai assistant-capabilities
local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server
local-ai assistant-action-loop-preflight "개인 API dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-action-loop-noop-dispatch "개인 API dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-action-loop-read-only-dispatch-preview "read only dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-automation-plan "내 개인 API 자동화" --project-root /Users/juyoung/local-ai-server
local-ai assistant-read-only-scan /Users/juyoung/local-ai-server
local-ai assistant-file-preview /Users/juyoung/local-ai-server/README.md --project-root /Users/juyoung/local-ai-server
local-ai assistant-url-preview https://example.com
local-ai assistant-workspace-brief /Users/juyoung/local-ai-server
local-ai assistant-shell-preview "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-shell-approval-preview "git status" --cwd /Users/juyoung/local-ai-server --reason "local CI"
local-ai assistant-shell-run "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-patch-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-patch-approval-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server" --reason "docs"
local-ai assistant-patch-apply /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-browser-preview observe --target-url https://example.com
local-ai assistant-browser-approval-preview screenshot --target-url https://example.com --reason "read-only QA"
local-ai assistant-browser-interact observe --target-url https://example.com
local-ai assistant-ping
local-ai assistant-config
local-ai assistant-ui-contract
local-ai assistant-startup
local-ai assistant-status
local-ai assistant-dashboard
local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server
local-ai assistant-session --title "Demo" --project-root /Users/juyoung/local-ai-server
local-ai assistant-sessions
local-ai assistant-messages session-1 --limit 50 --offset 0
local-ai assistant-message "질문" --project-root /Users/juyoung/local-ai-server
local-ai assistant-root /Users/juyoung/local-ai-server
local-ai assist "질문"
local-ai assistant
local-ai ask "질문"
local-ai ask-docs "질문"
local-ai search "검색어"
local-ai upload ./notes/backend.md
local-ai index-preview ./notes
local-ai index-job-preview ./notes
local-ai index ./notes
local-ai docs
local-ai document-types
local-ai chunks 1
local-ai stats
local-ai integrity
local-ai repair-preview
local-ai vector-rebuild-preview
local-ai logs
local-ai log 1
local-ai feedbacks
local-ai agent-plan "GitHub 웹 열어줘"
local-ai agent-runs
local-ai agent-run 1
local-ai agent-actions 1
local-ai agent-dry-run 1
local-ai agent-results 1
local-ai agent-approve 1
local-ai agent-reject 1
local-ai agent-execute 1
local-ai agent-shell
local-ai export-sft --output data/sft_dataset.jsonl
```

## Smoke Script

실행 중인 서버 기준 문서/RAG E2E smoke test:

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000
```

기본 smoke sample은 `smoke-backend-notes.md`와 `smoke-architecture-notes.txt`다. 이 흐름은 `.md`와 `.txt` 업로드를 모두 수행한 뒤 `search`, `ask-with-docs`, `feedback`, `stats`를 확인한다.

공개 문서나 작업 기록에는 paste-safe 결과만 남긴다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --sanitized-summary
```

승인된 실제 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서로 확인할 때는 `--document`를 사용한다. PDF OCR fallback 검증도 같은 옵션을 사용한다. 이 모드는 SQLite, Chroma, `data/uploads/`에 기록을 추가할 수 있으므로 사용자 승인 후에만 실행한다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-notes.md --sanitized-summary
```

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-scan.pdf --sanitized-summary
```

sanitized smoke summary는 `safe_to_paste=true`, `mode=document-rag`, `steps[].status`, `documents_count`, `results_count`, `sources_count`, `chunks_count`, `excluded_fields`를 포함하고, 질문/답변 원문, request id, header, 로컬 project root, stored path는 제외한다.

브라우저 조작 없는 Assistant UI bridge smoke test:

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
```

Assistant bridge smoke는 `GET /assistant/startup`, `GET /project/api-inventory`, `POST /assistant/bootstrap`, `POST /assistant/action-preview`, `POST /assistant/action-loop-read-only-dispatch-preview`, `POST /assistant/message`, `GET /assistant/sessions`, `GET /assistant/sessions/{session_id}/messages` 순서로 호출한다. read-only wrapper step은 `result_wrapper_schema`의 safe flag만 요약하며 실제 파일 읽기, URL fetch, dispatch를 수행하지 않는다. `/assistant/message`는 `mode=auto`와 상태 질문으로 호출해 status intent로 분기하므로 Ollama 답변 생성은 사용하지 않지만 SQLite에 assistant session/message 기록은 추가된다.

## Local CI Check

로컬에서 공개 전 최소 검증을 한 번에 실행한다.

```bash
.venv/bin/python scripts/local_ci_check.py --root .
.venv/bin/python scripts/local_ci_check.py --root . --json
```

실행 순서:

1. `.venv/bin/python -m pytest`
2. `.venv/bin/python -m compileall app cli scripts`
3. `.venv/bin/python scripts/public_release_check.py --root . --json`
4. `git diff --check`

실패가 발생하면 그 단계에서 멈춘다. 시스템 패키지 설치, 운영 배포, 외부 API 활성화는 수행하지 않는다.
