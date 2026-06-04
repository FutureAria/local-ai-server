# Security Policy

`local-ai-server`는 개인 PC 또는 개인 서버에서 실행하는 로컬 전용 AI 지식 서버다. 이 문서는 안전한 로컬 운영과 GitHub/포트폴리오 공개 전 확인할 보안 기준을 정리한다.

## 기본 보안 원칙

- 런타임 LLM과 embedding은 Ollama local API만 사용한다.
- OpenAI, Claude, Gemini 등 외부 LLM API를 운영 경로에 추가하지 않는다.
- LangChain, cloud vector DB, 외부 유료 API를 사용하지 않는다.
- 기본 서버 bind는 `127.0.0.1`을 권장한다.
- 개인 문서, 업로드 파일, SQLite DB, Chroma index, 운영 로그는 Git에 올리지 않는다.
- `.env`, API key, DB password, token, credential은 출력하거나 커밋하지 않는다.
- 원본 색인 대상 폴더의 파일을 수정하거나 삭제하지 않는다.

## 인증과 접근 제어

`LOCAL_API_KEY`가 설정되어 있으면 보호 endpoint는 `X-API-Key` 헤더를 요구한다. 로컬 UI 호환을 위해 `Authorization: Bearer <LOCAL_API_KEY>`도 같은 키로 허용한다.

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

- `GET /documents`, `GET /documents/stats`, `GET /documents/integrity`, `GET /documents/repair-preview`, `GET /chat-logs`, `GET /feedback`, `GET /project/status`, `GET /project/next`는 현재 read-only 조회 endpoint다.
- `GET /project/shell-policy`와 `POST /project/shell-dry-run`은 실제 shell을 실행하지 않지만 명령 후보가 포함될 수 있어 보호 endpoint로 둔다.
- `/assistant/*`는 사용자 메시지, 세션 기록, project root를 다루므로 보호 endpoint로 둔다.
- 보호 endpoint에는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit이 적용된다. 기본값은 분당 `120`회이며, `0`으로 설정하면 비활성화된다.
- 개인 문서가 들어 있는 환경에서는 서버를 외부 네트워크에 공개하지 말고 `127.0.0.1`에 bind한다.
- 다중 사용자 인증/인가, 사용자별 문서 격리는 아직 구현하지 않았다.
- 브라우저 UI CORS는 `LOCAL_CORS_ORIGINS`에 명시된 로컬 origin만 허용한다. 기본값은 `http://127.0.0.1:5173,http://localhost:5173`이다.

## 데이터 저장 위치

| 데이터 | 기본 위치 | Git 포함 |
|---|---|---|
| SQLite DB | `data/local_ai.sqlite3`, `data/*.sqlite3`, `data/*.sqlite3-*`, `data/*.sqlite`, `data/*.sqlite-*`, `data/*.db`, `data/*.db-*` | 제외 |
| Chroma vector index | `data/chroma/` | 제외 |
| 업로드 파일 | `data/uploads/` | 제외 |
| 운영 로그 | `data/logs/` | 제외 |
| SFT export | `data/*.jsonl` | 제외 |
| 환경변수/credential 파일 | `.env`, `.env.*`, `.envrc`, `.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.pnpmrc`, `.pypirc`, `pip.conf`, `.config/pip/pip.conf`, `.config/pypoetry/auth.toml`, `pypoetry/auth.toml`, `.netrc`, `.git-credentials`, `.boto`, `.s3cfg`, `.pgpass`, `.sentryclirc`, `auth.json`, `.terraformrc`, `terraform.rc`, `secrets/`, `.secrets/`, `.ssh/`, `.gnupg/`, `.password-store/`, `.vault-token`, `.config/doppler/config.yaml`, `.config/infisical/infisical-config.json`, `.config/op/config`, `.config/1Password/credentials.json`, `.config/sops/age/keys.txt`, `.docker/`, `.config/containers/auth.json`, `.config/helm/registry/config.json`, `.config/helm/repositories.yaml`, `.config/hub`, `.config/gh/hosts.yml`, `.config/gh/hosts.yaml`, `.config/doctl/config.yaml`, `.config/doctl/config.yml`, `.vercel/auth.json`, `.netlify/config.json`, `.fly/config.yml`, `.fly/config.yaml`, `.openai/`, `.config/openai/`, `.anthropic/`, `.claude.json`, `.claude/settings.local.json`, `.gemini/settings.json`, `.config/gemini/settings.json`, `.postman/`, `.config/Postman/`, `.insomnia/`, `.config/Insomnia/`, `.httpie/`, `.config/httpie/`, `.bruno/`, `.cursor/mcp.json`, `.cursor/settings.json`, `.continue/config.json`, `.aider.conf.yml`, `.aider.env`, `.codeium/config.json`, `.config/Codeium/config.json`, `.gem/credentials`, `.cargo/credentials`, `.cargo/credentials.toml`, `.composer/auth.json`, `.config/composer/auth.json`, `.condarc`, `.config/conda/condarc`, `.continuum/anaconda-client/tokens`, `.dbt/profiles.yml`, `.databrickscfg`, `.config/databricks/credentials`, `.snowsql/config`, `.config/snowflake/config.toml`, `.huggingface/token`, `.cache/huggingface/token`, `.cache/huggingface/stored_tokens`, `.config/huggingface/token`, `.kaggle/kaggle.json`, `.config/kaggle/kaggle.json`, `.wandb/settings`, `.config/wandb/settings`, `.gradle/gradle.properties`, `.m2/settings.xml`, `NuGet.Config`, `nuget.config`, `.nuget/NuGet/NuGet.Config`, `.pulumi/credentials.json`, `.aws/`, `.gcloud/`, `.config/gcloud/application_default_credentials.json`, `.config/gcloud/credentials.db`, `.config/gcloud/access_tokens.db`, `.config/gcloud/legacy_credentials/`, `clouds.yaml`, `secure.yaml`, `.config/openstack/clouds.yaml`, `.config/openstack/secure.yaml`, `rclone.conf`, `.config/rclone/rclone.conf`, `.azure/`, `.kube/`, `.oci/`, `.oraclebmc/`, `kubeconfig`, `kube.config`, `credentials.json`, `application_default_credentials.json`, `client_secret*.json`, `service-account*.json`, `firebase-adminsdk*.json`, `google-credentials*.json` (`.env.example` 예외) | 제외 |

추가로 key/certificate, 로그, IaC state, vault 계열 private data 패턴인 `*.key`, `*.pem`, `*.crt`, `*.cer`, `*.der`, `*.csr`, `*.p7b`, `*.p7c`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.truststore`, `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ecdsa_sk`, `id_ed25519`, `id_ed25519_sk`, `*.log`, `*.tfstate`, `*.tfstate.*`, `Pulumi.*.yaml`, `Pulumi.*.json`, `.vault_pass`, `.vault_password`, `*.vault`도 Git에 포함하지 않는다.

## 로그 정책

- 질문, 답변, 문서 원문, API key, 환경변수 원문을 운영 로그에 남기지 않는다.
- 장애 분석에는 endpoint, status code, request id, 짧은 오류 메시지 수준만 사용한다.
- 파일 로그가 필요하면 `data/logs/` 아래에 두고 Git에 포함하지 않는다.
- 로그 rotation 자동화는 아직 구현하지 않았다.

## 파일 업로드와 폴더 색인

지원 형식:

- 기본: `.txt`, `.md`, `.html`, `.htm`
- optional dependency 설치 시: `.pdf`, `.docx`
- OCR optional dependency와 로컬 `tesseract` 설치 시: PDF image XObject fallback OCR

보안 기준:

- 지원하지 않는 확장자는 거부한다.
- `.txt`, `.md`, `.html`, `.htm`은 UTF-8 텍스트만 처리한다.
- HTML은 `head`, `script`, `style`, `noscript` 내용을 제외하고 텍스트만 추출한다.
- PDF OCR은 로컬 `tesseract` binary만 사용하며 이미지 bytes는 저장하지 않고 OCR 결과 텍스트만 chunk로 저장한다.
- JavaScript 렌더링, 외부 URL 크롤링, 브라우저 interaction은 지원하지 않는다.
- 폴더 색인은 `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `dist`, `build`, `target` 등을 무시한다.

## RAG 안전 기준

- 답변은 가능한 한 검색된 context를 기준으로 생성한다.
- 문서에 근거가 부족하면 충분한 정보가 없다고 답한다.
- 출처를 지어내지 않는다.
- 문서 밖 코드, 링크, 보안 세부사항, 추측성 표현이 감지되면 보수적인 fallback 답변으로 대체될 수 있다.

## Agent 안전 기준

- `/agent/plan`은 preview-only 계획 생성만 수행한다.
- `/agent/runs/{run_id}/dry-run`은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 정책 판단만 기록한다.
- `/agent/runs/{run_id}/actions`는 action별 상태와 dry-run/execution 결과를 조회한다.
- `/agent/runs/{run_id}/approve`는 승인 상태만 기록하고 실제 실행은 수행하지 않는다.
- `/agent/runs/{run_id}/reject`는 거절 상태만 기록한다.
- `/agent/runs/{run_id}/execute`는 승인된 run만 실행 시도한다.
- `AGENT_EXECUTION_ENABLED=false` 기본값에서는 실제 실행을 차단한다.
- `AGENT_EXECUTION_ENABLED=true`에서도 v1 실행 엔진은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원한다.
- 파일 preview는 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자를 차단한다.
- `/project/shell-policy`는 shell dry-run allowlist와 blocked token을 조회한다.
- `/project/shell-dry-run`은 입력 명령을 실행하지 않고 `would_execute=false`인 정책 판단만 반환한다.
- `/assistant/action-preview`는 intent와 위험도만 preview하고 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.
- `/assistant/action-loop-preflight`는 8차 action-loop dispatch 전 frozen plan, wrapper, approval binding, payload hash gate만 확인하고 실제 dispatch, shell 실행, patch apply, browser/app interaction은 수행하지 않는다.
- `/assistant/action-loop-noop-dispatch`는 10차 no-op dispatcher dry-run endpoint이며 preflight 검증 결과를 route plan과 noop audit으로 기록할 뿐 실제 dispatch, shell 실행, patch apply, browser/app interaction을 수행하지 않는다.
- no-op dispatcher는 approval을 consume하지 않고 validate-only로 확인한다. 실제 approval consume mode 전환은 별도 보안 리뷰와 사용자 최종 승인 전 진행하지 않는다.
- `/assistant/action-loop-read-only-dispatch-preview`는 11차 read-only dispatch boundary preview endpoint이며 read-only adapter routing을 classification-only로 검토한다. 파일 내용 읽기, 폴더 스캔, URL fetch, 실제 dispatch는 수행하지 않는다.
- 13차 read-only result wrapper schema는 `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`에 정의되어 있으며 raw content, approval-like JSON, next step, shell command, patch payload, browser action을 trusted result로 승격하지 않는다.
- 실제 read-only adapter execution은 `docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md`의 policy matrix와 Decision Required가 해소되기 전까지 활성화하지 않는다.
- `/assistant/action-loop-preflight`의 frozen plan은 secret-like 값이 LLM context, audit, UI 응답으로 넘어가기 전에 nested params까지 masking해야 한다.
- action-loop preflight의 wrapper와 approval binding gate는 사용자가 끌 수 없는 fail-closed 조건이다. `require_wrappers=false` 또는 `require_approval_bindings=false` 같은 opt-out은 허용하지 않는다.
- `/assistant/automation-plan`은 개인 API 자동화 목표를 단계별 plan-only 계약으로 정리하며 shell 실행, browser interaction, file write/delete, 외부 LLM/API 호출을 수행하지 않는다.
- `/assistant/read-only-scan`, `/assistant/file-preview`, `/assistant/url-preview`, `/assistant/workspace-brief`는 4차 read-only 자동화 endpoint이며 원본 파일 수정, shell 실행, 브라우저 조작, 외부 URL fetch를 기본값에서 수행하지 않는다.
- `/assistant/web-search-provider-preview`는 19차 External Web Search Provider Gate endpoint이며 provider 설정 상태, query masking, private/LAN/metadata URL 차단, untrusted result wrapper 요구, 비용/rate limit 후보만 반환한다. `/assistant/web-search-provider/search`는 33차 env opt-in 조건에서만 `brave` provider 단건 search를 수행한다.
- `EXTERNAL_WEB_SEARCH_ENABLED` 기본값은 `false`이고 `EXTERNAL_WEB_SEARCH_RATE_LIMIT_PER_MINUTE` 기본값은 `0`이다. 이 값들은 provider gate 설계 후보를 표시할 뿐 실제 외부 호출 권한을 의미하지 않는다.
- `/assistant/app-os-interaction-preview`는 20차 App/OS Interaction Gate endpoint이며 observe-plan 후보, blocked action taxonomy, permission model, approval binding 설계, masking된 audit payload만 반환한다. 실제 app open, click, type, hotkey, file dialog, AppleScript, `osascript`, `open` command, Computer Use 연결은 수행하지 않는다.
- `APP_OS_CONTROL_ENABLED` 기본값은 `false`이며, permission model은 문서화 전용이다. approval binding은 설계 계약만 노출하고 실제 OS action approval로 사용하지 않는다.
- `/assistant/workflow-presets`, `/assistant/workflow-presets/{preset_id}`, `/assistant/workflow-presets/{preset_id}/preview`는 21차 Personal Workflow Presets endpoint이며 안전한 workflow template과 frozen proposed_steps 후보만 반환한다. 실제 action-loop dispatch, shell subprocess, patch apply, browser/app-os control, external API 호출은 수행하지 않는다.
- workflow preset params는 masking하고, client-supplied approval-like JSON 또는 unsafe preset id는 blocked 상태로 남긴다.
- `/assistant/task-queue/preview`, `/assistant/task-queue`, `/assistant/task-queue/{task_id}`, `/assistant/task-queue/{task_id}/cancel-preview`는 22차 Long-running Task Queue locked preview endpoint다. no-op/read-only task 상태, cancellation state, audit link, TTL/cleanup policy를 반환한다.
- `/assistant/task-queue/drain`은 34차 Task Queue Worker v1 endpoint다. 기본값 `TASK_QUEUE_WORKER_ENABLED=false`에서는 disabled로 차단하고 task 상태를 변경하지 않는다. env opt-in 시에도 request-scoped one-shot drain만 수행하며 daemon/service/background infinite loop를 시작하지 않는다. 실제 처리 범위는 `noop`, `read_only_scan`, `file_preview`로 제한되고 read-only 실행은 기존 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`와 untrusted wrapper gate를 재사용한다.
- task queue params는 masking하고, approval-like JSON injection과 mutating task type은 blocked 상태로 남긴다.
- `/assistant/failure-recovery-preview`는 23차 Failure Recovery / Rollback locked preview endpoint다. failure reason taxonomy, patch rollback plan, shell/browser manual instruction만 반환하며 자동 rollback 실행, git reset, file restore, shell execution, browser interaction은 수행하지 않는다.
- `/assistant/rollback-approval-preview`, `/assistant/rollback-execute`는 35차 Rollback Executor Boundary endpoint다. 기본값 `ROLLBACK_EXECUTOR_ENABLED=false`에서는 실행이 disabled이며, env opt-in에서도 rollback 전용 서버 approval, single-use, TTL, session binding, payload_hash, allowed root, 기존 UTF-8 단일 파일, current/original hash precondition을 통과한 단일 파일 restore만 허용한다.
- `/assistant/full-automation-preflight`, `/assistant/full-automation-dispatch`는 36~48차 Full Personal Automation Boundary endpoint다. 기본값 `FULL_AUTOMATION_DISPATCH_ENABLED=false`에서는 통합 dispatch와 approval consume을 하지 않는다. 38차 범위에서는 read-only category step만 기존 read-only adapter wrapper로 실행하고, 39차 범위에서는 allowlist shell category step만 기존 shell sandbox로 실행한다. 40차 범위에서는 `PATCH_APPLY_ENABLED=true`, valid patch approval, allowed root, 기존 UTF-8 단일 파일, `original_sha256` precondition, secret scan을 모두 만족한 patch category step만 기존 patch boundary로 실행한다. 41차 범위에서는 `ROLLBACK_EXECUTOR_ENABLED=true`, valid rollback approval, allowed root, 기존 UTF-8 단일 파일, current/original hash precondition을 모두 만족한 rollback category step만 기존 rollback boundary로 실행한다. 42차 범위에서는 `TASK_QUEUE_WORKER_ENABLED=true`, read-only task type, wrapper gate, params masking, approval-like JSON injection 차단을 통과한 `noop`, `read_only_scan`, `file_preview` task queue step만 기존 one-shot worker boundary로 실행한다. 43차 범위에서는 `BROWSER_OBSERVE_ENABLED=true`, valid browser approval, loopback/명시 allowlist URL, read-only observe action을 통과한 browser_observe step만 기존 HTTP metadata/title/current URL boundary로 실행한다. 44차 범위에서는 `BROWSER_LIMITED_INTERACTION_ENABLED=true`, valid browser approval, loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist를 통과한 browser_limited_interaction step만 기존 candidate validation boundary로 실행한다. 45차 범위에서는 `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, provider configured, rate limit, query safety, `wrapper.untrusted=true`를 통과한 external_web_search step만 기존 provider boundary로 실행한다. 46차 범위에서는 app_os step을 기존 app-os interaction preview boundary로만 처리하고 observe-plan candidate wrapper를 untrusted로 중첩한다. 47차 범위에서는 gate/audit/safety matrix가 preview connector, actual connector, mutating connector, browser actual interaction, app-os actual action, action-loop full dispatch 상태를 명시한다. 48차 Full Automation Action-loop Dispatch Decision Required에서는 실제 action-loop full dispatch는 계속 금지하며, 사용자 최종 승인과 Opus 리뷰 전까지 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 유지한다. 66차 approval console/pending/detail/approve/reject는 state-only이며 approve/reject can update only approval-store state, no execution on approve 원칙을 따른다. 68차 approval-store-expiry-cleanup은 pending/list/detail cleanup과 paste-safe expired summary만 수행하며 raw approval id not included, payload_hash not included, expired_count, records_removed, no execution triggered 계약을 유지한다. browser actual interaction/app-os actual action 실행은 아직 연결하지 않는다.
- failure recovery summary와 rollback params는 paste-safe masking 후 반환한다.
- 24차 Production Hardening 기준으로 `/assistant/capabilities`는 실제 실행이 비활성인 기능을 enabled로 광고하지 않는다. shell execution, patch apply, rollback executor, browser interaction, action-loop dispatch, task queue worker, external web search, app/OS control, file write/delete는 disabled/blocked/locked/preview-only 또는 명시 env opt-in 상태로 표시해야 한다.
- 25차 Read-only Adapter Execution은 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`에서만 `/assistant/read-only-adapter/execute`를 통해 file/list/safe URL adapter를 실제 read-only로 실행한다. 결과는 `assistant.read_only_adapter.result_wrapper.v1` untrusted wrapper로 반환하며 approval-like JSON을 신뢰하지 않는다.
- 26차 Read-only Action-loop Dispatch는 `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 read-only adapter flag가 모두 켜졌을 때만 `/assistant/action-loop-read-only-dispatch`에서 read-only adapter를 호출한다. shell, patch, browser dispatch는 연결하지 않는다.
- 27차 Shell Sandbox v1은 `SHELL_EXECUTION_ENABLED=false` 기본값을 유지한다. `/assistant/shell-run`은 flag가 true이고 allowlist command, `AGENT_ALLOWED_ROOTS` 안쪽 cwd, 1~120초 timeout, 서버 발급 single-use approval, session/request context, payload_hash binding을 모두 통과할 때만 `shell=False` 단건 subprocess를 실행한다.
- `/assistant/shell-preview`, `/assistant/shell-approval-preview`는 계속 preview/approval binding만 반환한다. `/assistant/shell-run`은 기본값 disabled이고, 27차 env opt-in 조건에서만 제한 실행한다.
- 28차 Shell Action-loop Dispatch는 `SHELL_ACTION_LOOP_DISPATCH_ENABLED=false` 기본값을 유지한다. `/assistant/action-loop-shell-dispatch`는 이 flag와 `SHELL_EXECUTION_ENABLED=true`가 모두 켜졌고, 각 shell step이 27차 allowlist/cwd/approval/payload_hash/session binding을 통과할 때만 shell step을 호출한다.
- 28차 shell action-loop 결과는 `assistant.action_loop.shell_result_wrapper.v1` untrusted wrapper로 반환하며 approval-like JSON을 신뢰하지 않고 frozen plan/next step mutation을 허용하지 않는다.
- 30차 Patch Action-loop Dispatch는 `PATCH_ACTION_LOOP_DISPATCH_ENABLED=false` 기본값을 유지한다. `/assistant/action-loop-patch-dispatch`는 이 flag와 `PATCH_APPLY_ENABLED=true`가 모두 켜졌고, 각 patch step이 29차 단일 파일/path/secret/original_sha256/approval binding을 통과할 때만 patch step을 호출한다.
- 29차 Patch Apply Sandbox v1은 `PATCH_APPLY_ENABLED=false` 기본값을 유지한다. `/assistant/patch-apply`는 flag가 true이고 기존 UTF-8 텍스트 단일 파일, `AGENT_ALLOWED_ROOTS` 안쪽 path, secret scan 통과, 서버 발급 single-use approval, session/request context, payload_hash binding, `original_sha256` precondition을 모두 통과할 때만 파일을 덮어쓴다.
- `/assistant/patch-preview`, `/assistant/patch-approval-preview`는 계속 diff preview, path allowlist, secret scan, rollback note, 서버 발급 approval binding만 반환한다. 파일 생성/삭제, bulk apply, binary/sensitive file write, workspace 밖 write, 자동 rollback, action-loop patch dispatch는 수행하지 않는다.
- patch `project_root`는 `AGENT_ALLOWED_ROOTS`를 대체하지 못한다. 요청된 `project_root`는 configured allowed roots 안쪽일 때만 더 좁은 교집합 root로 사용하고, 밖이면 차단한다.
- patch 승인 해시는 raw proposed content bytes와 apply 직전 original SHA-256 precondition에 바인딩되어야 하며, 실제 apply가 도입되더라도 디스크 원본을 apply 직전에 재검증해야 한다.
- 9차 approval store는 process-local in-memory preview store다. approval id는 서버가 발급하고, approval은 단일 사용, session/request context 바인딩, payload_hash 바인딩, TTL을 필수 조건으로 검증한다.
- expired approval, already-used approval, payload_hash mismatch, session/request context mismatch, unknown approval은 blocked로 남는다.
- expired approval은 cleanup 이후 pending/list/detail에서 보이지 않아야 하며 approve/reject cannot revive expired approval 원칙을 따른다. client-supplied approval-like JSON, next_action, payload_hash 주입은 서버 approval store record를 생성하거나 되살릴 수 없다.
- 69차 approval console API surface는 Decision Required 상태였다. endpoint exposure remains blocked, no approval-console endpoints added 상태에서 pending/list/detail/approve/reject/cleanup endpoint 후보의 인증/권한/감사/마스킹/TTL cleanup 조건을 먼저 고정했다.
- 70차 approval console read-only API는 protected endpoint only로 `GET /assistant/approval-console/pending`, `GET /assistant/approval-console/{approval_id}`, `POST /assistant/approval-console/cleanup-expired`만 노출한다. approve/reject routes not added 상태이며, 응답은 masked response only로 raw approval id not included, payload_hash not included, `audit_summary_hash`만 포함한다. cleanup is not approval consume이고 `approval_consumed=false`, `would_execute=false`를 유지한다.
- 71차 Durable Automation v2 Candidate Decision Required는 durable-automation-v2-candidate-decision-required 상태다. persistence/recovery/replay boundary만 문서화하고 no durable worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery를 유지한다. durable task persistence, replay queue, recovery checkpoint는 decision-required 후보이며 실제 scheduler loop, autonomous retry, action-loop full dispatch는 blocked 상태다.
- 72차 Durable State Preview Schema Candidate는 durable-state-preview-schema-candidate 상태다. `state_schema_version=durable_state_preview.v1`, `preview_state_id`, `state_status=candidate-preview`, proposal-only contract, schema-only, owner/session/request context binding, payload_hash binding, masked params only, no raw secrets, no raw approval id, payload_hash not included, `audit_summary_hash`만 문서화한다. no durable storage migration, no durable table created, no queue worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery를 유지한다. state_preview_is_not_execution, state_preview_does_not_consume_approval, state_preview_does_not_mutate_queue, `would_persist=false`, `approval_consumed=false`를 고정한다.
- 73차 Durable State Preview API Surface Decision Required는 durable-state-preview-api-surface-decision-required 상태다. endpoint exposure remains blocked, no durable-state-preview endpoints added, route_absence_is_required, endpoint_candidate_is_not_exposure, `would_expose_endpoint=false`를 고정한다. 후보 endpoint는 `POST /assistant/durable-state-preview/preview`, `GET /assistant/durable-state-preview/{preview_state_id}`, `GET /assistant/durable-state-preview`, `POST /assistant/durable-state-preview/cleanup-expired`로만 문서화하고 FastAPI route 또는 CLI command는 추가하지 않는다. 향후 노출하려면 `LOCAL_API_KEY required`, protected endpoint only, read-only/schema-only response, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash` required를 먼저 만족해야 한다.
- 74차 Durable State Preview Read-only API Candidate는 `POST /assistant/durable-state-preview/preview` 하나만 protected endpoint only로 노출한다. endpoint는 `durable-state-preview-read-only`, response-only/read-only/schema-only, state_schema_version=durable_state_preview.v1, state_status=candidate-preview, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash`를 반환한다. stored preview lookup/list/cleanup remain Decision Required이며 `GET /assistant/durable-state-preview/{preview_state_id} remains absent`, `GET /assistant/durable-state-preview remains absent`, `POST /assistant/durable-state-preview/cleanup-expired remains absent` 상태를 유지한다. `would_execute=false`, `would_persist=false`, `would_dispatch=false`, `approval_consumed=false`, `durable_storage_migration_connected=false`, `durable_table_created=false`, `persistence_mutation_connected=false`, `queue_mutation_connected=false`를 고정한다.
- 75차 Durable State Preview API Regression Guard는 nested sensitive key redaction, route inventory drift, absent stored preview routes, no persistence mutation, no approval consume, no queue mutation을 테스트로 보강한다. `approval_id`, `approval_payload_hash`, `payload_hash`, `token`, `password` 계열 key는 `candidate_steps`와 `metadata` 양쪽에서 `[REDACTED]`로 반환되어야 하며 raw value는 응답에 남지 않아야 한다.
- 76차 Durable State Preview Docs/API Drift Guard는 API docs response fields, public docs endpoint listing, security boundary, release summary, handoff 문구가 `AssistantDurableStatePreviewResponse`와 runtime route inventory를 계속 반영하는지 고정한다. stored preview lookup/list/cleanup route absent, no persistence mutation, no approval consume, no queue mutation을 문서/런타임 양쪽에서 유지한다.
- 클라이언트가 보낸 approval-like JSON, tool result, user payload는 서버 approval store record를 대체하거나 병합할 수 없다.
- approval store 검증이 성공해도 `/assistant/browser-interact`는 locked 응답만 반환하며 `would_interact=false`, `execution_enabled=false`를 유지한다. `/assistant/shell-run`은 27차 env opt-in 조건에서만 `would_execute=true`가 될 수 있고, `/assistant/patch-apply`는 29차 env opt-in 조건에서만 기존 UTF-8 단일 파일에 대해 `would_apply=true`가 될 수 있다. `/assistant/browser-observe`는 31차 env opt-in 조건에서만 loopback/명시 allowlist URL read-only metadata observe로 제한된다. `/assistant/browser-limited-interact`는 32차 env opt-in 조건에서도 candidate validation만 수행하고 실제 browser launch/click/fill은 수행하지 않는다.
- `/assistant/browser-preview`, `/assistant/browser-approval-preview`, `/assistant/browser-interact`는 7차 browser/app interaction 계약 endpoint이며 read-only taxonomy, 서버 발급 approval binding, locked-interact 상태만 반환하고 실제 click/fill/submit/login/payment/delete 또는 OS app control은 수행하지 않는다.
- `/assistant/browser-observe`는 `BROWSER_OBSERVE_ENABLED=false` 기본값을 유지한다. 활성화하더라도 서버 발급 single-use approval, session/request context binding, payload_hash binding, URL allowlist를 통과한 `observe`, `screenshot`, `page_title`, `current_url` 계열만 허용하고 raw page content, approval-like JSON, next action mutation을 trusted result로 승격하지 않는다.
- `/assistant/browser-limited-interact`는 `BROWSER_LIMITED_INTERACTION_ENABLED=false` 기본값을 유지한다. 활성화하더라도 loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist, 서버 발급 approval binding을 검증한 candidate result만 반환하며 browser engine/profile/session mutation은 하지 않는다.
- Browser observe는 실제 browser profile/session mutation, click/fill/type/submit, credential input, login/payment/delete flow, download/upload/file dialog, action-loop browser dispatch, OS app control을 수행하지 않는다.
- Browser limited interaction도 login/payment/delete/credential/password/token/secret/submit/download/upload/file dialog, action-loop browser dispatch, OS app control을 수행하지 않는다.
- `/assistant/web-search-provider/search`는 `EXTERNAL_WEB_SEARCH_ENABLED=false` 기본값을 유지한다. 활성화하더라도 provider allowlist, API key configured 여부, rate limit, query safety, untrusted result wrapper를 모두 통과한 `brave` 단건 web search만 허용하고 API key 원문은 반환하지 않는다.
- External web search 결과는 raw content, approval-like JSON, next action, frozen plan mutation으로 승격하지 않으며 action-loop external dispatch, task worker, rollback, app-os control에 연결하지 않는다.
- 18차 Browser Interaction Sandbox gate는 `assistant.browser_interaction.gate.v1` preview schema로 observe/read 계열을 allowed candidate로만 표시한다. click/fill/submit/login/payment/delete, browser launch, OS app control은 blocked execution으로 유지한다.
- Browser domain allowlist는 `design-only` 후보로만 문서화하며 실제 browser/network control에는 연결하지 않는다.
- Browser selector/input/reason은 audit payload 이전에 masking하고, client-supplied approval-like JSON은 서버 approval store record를 대체하거나 병합할 수 없다.
- `/assistant/ping`, `/assistant/config`, `/assistant/ui-contract`, `/assistant/startup`, `/assistant/dashboard`, `/assistant/bootstrap`은 UI 초기화/상태 조회용이지만 사용자 환경과 세션 요약을 다루므로 보호 endpoint로 둔다.
- `/assistant/ui-contract`는 UI 계약을 반환하지만 실제 실행 기능을 활성화하지 않는다.
- `/assistant/startup`은 UI 초기 snapshot을 반환하지만 실제 실행 기능을 활성화하지 않는다.
- `/assistant/config`는 `LOCAL_API_KEY` 값을 반환하지 않고 보호 여부만 반환한다.
- `/assistant/sessions/{session_id}/messages`는 사용자 대화 기록을 반환하므로 보호 endpoint로 둔다.
- `/assistant/message`는 UI 입력을 자동 분기하지만 폴더 색인은 preview-only, shell은 dry-run만 수행한다.
- 실제 웹 이동, 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 수행하지 않는다.
- `AGENT_EXECUTION_ENABLED` 기본값은 `false`다.
- `AGENT_ALLOWED_ROOTS`는 파일/폴더 agent action이 접근할 수 있는 root를 제한한다.
- `AGENT_WEB_FETCH_ENABLED`는 명시 URL read-only fetch를 별도로 제어한다.
- `AGENT_WEB_FETCH_MAX_BYTES`는 URL fetch 응답을 지정한 바이트 이후 truncate한다.
- `AGENT_FILE_PREVIEW_MAX_BYTES`와 `AGENT_FILE_PREVIEW_EXTENSIONS`는 파일 내용 preview 범위를 제한한다.
- agent plan 기록은 사용자 요청 내용을 포함할 수 있으므로 `/agent/*` endpoint는 `LOCAL_API_KEY`가 설정된 경우 보호된다.
- 브라우저 클릭, 파일 수정, shell 실행 같은 고위험 실행 기능을 활성화하려면 별도 보안 리뷰와 사용자 승인이 필요하다.

## Production Hardening 상태

24차 기준 production hardening은 운영 배포가 아니라 로컬 서버의 보안/테스트/문서/계약 정리다.

| 영역 | 상태 | 근거 |
|---|---|---|
| Capabilities honesty | 고정 | 위험 기능은 disabled/blocked/locked/preview-only로 광고 |
| Read-only adapter execution | env opt-in | 기본값 disabled. sensitive path, private/LAN/metadata URL, wrapper 누락은 blocked |
| Read-only action-loop dispatch | env opt-in | 기본값 disabled. read-only adapter만 호출하며 shell/patch/browser 연결 없음 |
| External API | 비활성 | `EXTERNAL_WEB_SEARCH_ENABLED=false`, provider_not_configured |
| Shell/Patch/Browser | 기본값 locked/preview, 제한 env opt-in | shell은 27차 allowlist, patch는 29차 단일 파일 apply만 env opt-in 가능. browser는 locked |
| Action-loop | dispatch disabled | preflight/no-op/boundary preview only |
| Approval gate opt-out | 차단 | `require_wrappers`와 `require_approval_bindings`는 false 허용 안 함 |
| Task queue / rollback | env opt-in one-shot drain / env opt-in single-file rollback restore | daemon/service worker, git reset, bulk restore disabled |
| Public release scanner | 유지 | `.venv/bin/python scripts/public_release_check.py --root . --json` clean |
| Deployment | 미수행 | service/daemon/cloud/Oracle/HTTPS 전환 없음 |

## 공개 전 체크리스트

자동 점검:

```bash
.venv/bin/python scripts/public_release_check.py --root . --json
```

이 명령은 read-only 점검만 수행한다. 로컬 DB, Chroma index, 업로드 파일, 로그, SFT export, secret 후보가 발견되면 실패 코드로 종료한다.

- [ ] `.env`가 포함되지 않았는가?
- [ ] `data/local_ai.sqlite3`가 포함되지 않았는가?
- [ ] `data/chroma/`가 포함되지 않았는가?
- [ ] `data/uploads/`가 포함되지 않았는가?
- [ ] `data/logs/` 로그 파일이 포함되지 않았는가?
- [ ] `data/*.jsonl` SFT export 파일이 포함되지 않았는가?
- [ ] API key, provider token, DB password, credential, key/certificate 파일이 포함되지 않았는가?
- [ ] 개인 문서 원문 또는 민감 정보가 README, docs, tests에 들어가지 않았는가?
- [ ] 실제 배포되지 않은 기능을 배포 완료처럼 설명하지 않았는가?
- [ ] 외부 LLM API를 사용하는 것처럼 오해될 문구가 없는가?

## 고위험 작업

아래 작업은 사용자 승인 없이 진행하지 않는다.

- 실제 repair/delete/rebuild 실행
- 브라우저 interaction, 파일 수정, shell agent 실행
- 실제 shell 실행은 27차 allowlist 단건 범위를 제외하면 고위험이다. arbitrary shell 실행 또는 action-loop shell dispatch는 별도 승인/리뷰 전 금지
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 활성화
- 외부 URL 크롤링
- 브라우저 click/fill/submit interaction 추가
- 시스템 의존성 설치
- 운영 배포
- 클라우드 리소스 생성/삭제/변경
- Oracle DB, Oracle Object Storage, Oracle VM 같은 실제 Oracle 리소스 연결 또는 변경
- DB migration, 운영 데이터 삭제, 저장공간에 비용 영향을 줄 수 있는 작업

## 보안 한계

- 현재 인증은 `LOCAL_API_KEY` 기반 단일 API key 수준이다.
- 사용자 계정, RBAC, 문서별 접근 제어는 없다.
- rate limit은 단일 프로세스 메모리 기준이다. 여러 worker나 여러 서버 인스턴스에 공유되는 분산 rate limit은 아니다.
- HTTPS termination은 애플리케이션에서 직접 제공하지 않는다.
- 서버를 외부 네트워크에 공개하려면 reverse proxy, TLS, 접근 제어, 로그 정책, 백업 정책을 별도로 검토해야 한다.
