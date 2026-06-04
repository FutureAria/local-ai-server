# Project Summary

## 한 줄 소개

`local-ai-server`는 외부 LLM API 없이 Ollama, FastAPI, SQLite, Chroma, Typer로 동작하는 로컬 전용 AI 지식 서버다.

## 무엇을 만들었는지

- 로컬 Ollama 기반 direct ask API
- 로컬 문서 업로드와 폴더 색인
- SQLite 기반 문서 metadata, chunk, chat log, feedback 저장
- Chroma 기반 vector search
- 문서 검색 기반 RAG 답변 API
- 로컬 서버를 호출하는 Typer CLI
- assistant 세션 요약, allowed root 온보딩, shell dry-run 정책 확인
- feedback 저장과 SFT JSONL export
- 문서/운영/보안/API/UI 연결/UI field cheatsheet/인계 문서

## 핵심 설계

```text
CLI / curl
  -> FastAPI route
  -> service layer
  -> Ollama local API
  -> SQLite metadata/log source of truth
  -> Chroma vector search
```

설계 기준:

- API route는 얇게 유지한다.
- 비즈니스 로직은 `app/services/`에 둔다.
- SQLite는 source of truth, Chroma는 vector search 전용으로 분리한다.
- CLI는 백엔드 API를 호출하고 로직을 중복 구현하지 않는다.
- 외부 LLM API, LangChain, cloud vector DB는 사용하지 않는다.

## 포트폴리오 포인트

- 담당 범위: FastAPI API, service layer, SQLite metadata 저장, Chroma vector search, Ollama local client, Typer CLI, 테스트/문서/보안 기준 정리
- 설계 포인트: route와 service 책임 분리, SQLite와 Chroma 역할 분리, CLI의 HTTP API 재사용, local-only LLM/embedding 정책
- 안정성 포인트: folder index preview, shell dry-run, agent approval 상태, LOCAL_API_KEY 보호 endpoint, public release check
- 검증 포인트: API contract, schema validation, CLI mock, security docs contract, UI bridge example validation, public docs contract를 pytest로 고정
- 한계 명시: 실제 브라우저 클릭, shell 실행, 파일 수정/삭제, 운영 배포, 외부 LLM API는 구현 범위 밖으로 분리

## 실행 가능 기능과 금지 기능

| 구분 | 상태 | 포트폴리오 설명 기준 |
|---|---|---|
| 문서 업로드, 검색, RAG | 가능 | 로컬 파일을 chunking, embedding, SQLite/Chroma 저장 후 Ollama로 답변한다. |
| CLI와 HTTP API | 가능 | CLI는 백엔드 HTTP API를 호출하며 비즈니스 로직을 중복 구현하지 않는다. |
| Assistant UI bridge | 가능 | startup, bootstrap, action-preview, automation-plan, workflow-presets, task-queue locked preview, failure-recovery preview, rollback approval/execute, read-only scan/file-preview/url-preview/web-search-provider-preview/app-os-interaction-preview/workspace-brief, shell sandbox, patch sandbox, message, sessions API를 제공하되 UI 자체는 만들지 않는다. |
| Agent plan/approval | 가능 | 요청을 실행하지 않고 action 후보, 위험도, 승인 상태로 기록한다. |
| Agent execution v1 | 조건부 read-only | 기본값은 차단이며, 활성화해도 허용 root 폴더 목록 조회, 텍스트 preview, 명시 URL 단건 read-only fetch만 지원한다. |
| shell 명령 | dry-run only 기본값 / locked preview / env opt-in allowlist execution | `shell-policy`, `shell-dry-run`, `assistant-shell-preview`, `assistant-shell-approval-preview`는 정책 판단과 audit만 수행한다. `assistant-shell-run`은 `SHELL_EXECUTION_ENABLED=true`에서만 27차 allowlist 단건 subprocess를 실행한다. |
| patch 명령 | locked preview 기본값 / env opt-in single-file apply | `assistant-patch-preview`, `assistant-patch-approval-preview`는 diff preview, secret scan, rollback note, approval binding만 수행한다. `assistant-patch-apply`는 `PATCH_APPLY_ENABLED=true`, 서버 approval, path allowlist, `original_sha256` precondition을 통과한 기존 UTF-8 단일 파일만 덮어쓴다. |
| browser/app interaction | locked preview / env opt-in observe and candidate validation only | `assistant-browser-preview`, `assistant-browser-approval-preview`, `assistant-browser-interact`은 read-only action taxonomy, approval binding, locked audit만 수행한다. `POST /assistant/browser-observe`는 `BROWSER_OBSERVE_ENABLED=true`에서만 loopback/명시 allowlist URL의 read-only metadata를 untrusted wrapper로 반환한다. `POST /assistant/browser-limited-interact`는 `BROWSER_LIMITED_INTERACTION_ENABLED=true`에서도 selector/origin/field/approval 후보 검증만 수행한다. 실제 click/fill/submit/login/payment/delete, browser profile/session mutation, OS app control은 하지 않는다. |
| external web search provider | locked preview / env opt-in brave search | `/assistant/web-search-provider-preview`는 provider_not_configured, query masking, private/LAN/metadata URL block, untrusted result wrapper required를 반환한다. `/assistant/web-search-provider/search`는 `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, API key, rate limit, query safety, untrusted wrapper를 모두 통과한 단건 search만 수행한다. action-loop external dispatch에는 연결하지 않는다. |
| app/os interaction | locked preview only | `/assistant/app-os-interaction-preview`는 observe-plan 후보와 permission model만 반환하고 실제 app open/click/type/hotkey/file dialog를 수행하지 않는다. |
| workflow presets | preview only | `/assistant/workflow-presets` 계열은 안전한 preset list/detail과 frozen proposed_steps 후보만 반환하고 실제 dispatch를 수행하지 않는다. |
| long-running task queue | env opt-in one-shot drain | `/assistant/task-queue` 계열은 no-op/read-only task 상태와 cancellation state를 반환한다. `/assistant/task-queue/drain`은 `TASK_QUEUE_WORKER_ENABLED=true`에서만 request-scoped one-shot drain으로 `noop`, `read_only_scan`, `file_preview` task를 처리하며 daemon/service/background loop나 shell/patch/browser 실행을 시작하지 않는다. |
| failure recovery / rollback | locked preview 기본값 / env opt-in single-file restore | `/assistant/failure-recovery-preview`는 failure reason taxonomy와 rollback plan만 반환한다. `/assistant/rollback-execute`는 `ROLLBACK_EXECUTOR_ENABLED=true`, rollback 전용 approval, allowed root, existing UTF-8 file, current/original hash precondition을 모두 통과한 단일 파일 restore만 수행한다. git reset, bulk restore, shell/browser/app-os rollback은 수행하지 않는다. |
| production hardening | docs/tests/contracts | 1~24차 capabilities honesty, locked/preview/read-only/candidate 경계, public release scanner, local CI green 상태를 테스트와 문서로 고정했다. 운영 배포는 수행하지 않았다. |
| action-loop dispatch | preflight / no-op / read-only env opt-in / shell allowlist env opt-in / patch single-file env opt-in | `assistant-action-loop-preflight`는 frozen plan gate, `assistant-action-loop-noop-dispatch`는 route plan/noop audit, `assistant-action-loop-read-only-dispatch-preview`는 read-only adapter boundary와 `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`의 result wrapper schema를 확인한다. `assistant-action-loop-read-only-dispatch`는 `docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md` 기준 read-only adapter만, `assistant-action-loop-shell-dispatch`는 27차 shell allowlist step만, `assistant-action-loop-patch-dispatch`는 29차 단일 파일 patch step만 env opt-in으로 호출한다. browser/external API/task worker/rollback/app-os dispatch는 수행하지 않는다. |
| full personal automation | env opt-in safe orchestrator | `POST /assistant/full-automation-preflight`, `POST /assistant/full-automation-dispatch`는 shell/patch/read-only/rollback/task/browser/external/app-os 후보를 통합 route plan으로 분류한다. 기본값 `FULL_AUTOMATION_DISPATCH_ENABLED=false`에서는 dispatch와 approval consume을 하지 않는다. 47차 기준 flag true와 read-only adapter, allowlist shell, single-file patch, single-file rollback, read-only task queue, browser observe, browser limited candidate validation, `brave` external web search flag/precondition, app-os observe-plan preview를 각각 만족한 category step만 기존 boundary로 처리한다. browser observe는 HTTP metadata/title/current URL 수준이고 browser limited는 candidate validation only이며 external search는 provider-gated 단건 search only, app-os는 preview wrapper only다. gate/audit/safety matrix는 safe/preview/mutating connector 상태를 명시하고 browser actual interaction/app-os actual action/action-loop full dispatch는 미연결이다. 48차에서는 Full Automation Action-loop Dispatch Decision Required를 문서/테스트로 고정했고, 61~70차 Local Jarvis runtime drift guard, failure/timeout drill, manual review packet, approval console state-only/hash/cleanup review, API surface Decision Required, approval-console-read-only API는 실제 action-loop full dispatch를 계속 금지한다. 70차 approval console read-only API는 pending/list/detail/cleanup만 protected endpoint로 열고 approve/reject routes not added, raw approval id not included, payload_hash not included, `audit_summary_hash`, `approval_consumed=false`, `would_execute=false`, cleanup is not approval consume을 유지한다. 71차 Durable Automation v2 Candidate Decision Required는 durable-automation-v2-candidate-decision-required 상태로 persistence/recovery/replay boundary만 문서화하고 no durable worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery를 고정한다. 72차 Durable State Preview Schema Candidate는 durable-state-preview-schema-candidate 상태로 `state_schema_version=durable_state_preview.v1`, `state_status=candidate-preview`, proposal-only contract, schema-only, no durable storage migration, no durable table created, `state_preview_is_not_execution`, `state_preview_does_not_consume_approval`, `state_preview_does_not_mutate_queue`, `would_persist=false`, `approval_consumed=false`를 고정한다. 73차 Durable State Preview API Surface Decision Required는 endpoint exposure remains blocked, no durable-state-preview endpoints added, route_absence_is_required, `would_expose_endpoint=false`를 고정했다. 74차 Durable State Preview Read-only API Candidate는 `POST /assistant/durable-state-preview/preview` 하나만 protected endpoint only로 열고 durable-state-preview-read-only, response-only/read-only/schema-only, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash`, `would_execute=false`, `would_persist=false`, `would_dispatch=false`, `approval_consumed=false`를 유지한다. 75차 Durable State Preview API Regression Guard는 nested sensitive key redaction, route inventory drift, absent stored preview routes, no persistence mutation, no approval consume, no queue mutation을 테스트로 보강한다. 76차 Durable State Preview Docs/API Drift Guard는 API docs response fields, public docs endpoint listing, security boundary, release summary, handoff 문구가 `AssistantDurableStatePreviewResponse`와 runtime route inventory를 계속 반영하는지 고정한다. stored preview lookup/list/cleanup remain Decision Required이며 `GET /assistant/durable-state-preview/{preview_state_id} remains absent`, `GET /assistant/durable-state-preview remains absent`, `POST /assistant/durable-state-preview/cleanup-expired remains absent`다. 사용자 최종 승인과 Opus 리뷰 전까지 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 유지한다. |
| 브라우저/파일/배포 | 금지 | 브라우저 클릭/입력, 폴더 UI 열기, 파일 생성/수정/삭제, 운영 배포, 클라우드/Oracle 리소스 변경은 구현 범위 밖이다. |
| 외부 LLM API/cloud vector DB | 금지 | 런타임 AI 호출은 Ollama local API만 사용한다. |

## Runtime Contract Snapshot

| 항목 | 현재 값 | 기준 |
|---|---:|---|
| FastAPI endpoints | 94 | `build_api_inventory(app.routes).endpoints_count` |
| Protected endpoints | 78 | `build_api_inventory(app.routes).protected_endpoints_count` |
| Public endpoints | 16 | `build_api_inventory(app.routes).public_endpoints_count` |
| Typer CLI commands | 69 | `typer.main.get_command(cli.main.app).commands` |
| Document/RAG smoke steps | 6 | `DOCUMENT_RAG_SMOKE_FLOW` |
| Assistant bridge smoke steps | 8 | `ASSISTANT_BRIDGE_SMOKE_FLOW` |
| Assistant bridge preflight steps | 3 | `ASSISTANT_BRIDGE_PREFLIGHT_FLOW` |

이 표는 Project Summary의 요약 숫자가 실제 route, CLI command, smoke flow와 어긋나지 않도록 pytest로 검증한다.

## Endpoint 목록

Health:

- `GET /health`
- `GET /health/ollama`

Ask/Search:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`

Assistant:

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

Documents:

- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder-job-preview`
- `POST /documents/index-folder`
- `GET /documents`
- `GET /documents/supported-types`
- `GET /documents/stats`
- `GET /documents/integrity`
- `GET /documents/repair-preview`
- `GET /documents/vector-rebuild-preview`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/chunks`
- `DELETE /documents/{document_id}`

Chat/Feedback:

- `GET /chat-logs`
- `GET /chat-logs/{chat_log_id}`
- `POST /feedback`
- `GET /feedback`

Agent:

- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`
- `GET /agent/runs/{run_id}/results`
- `GET /agent/runs/{run_id}/actions`
- `POST /agent/runs/{run_id}/dry-run`
- `POST /agent/runs/{run_id}/approve`
- `POST /agent/runs/{run_id}/reject`
- `POST /agent/runs/{run_id}/execute`

Project:

- `GET /project/status`
- `GET /project/next`
- `GET /project/api-inventory`
- `GET /project/shell-policy`
- `POST /project/shell-dry-run`

## CLI 명령어 목록

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

## 서버 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,documents]"

ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 테스트 실행 방법

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
.venv/bin/python scripts/local_ci_check.py --root .
```

현재 검증 상태:

- `.venv/bin/pytest`: `815 passed, 1 warning`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `.venv/bin/python scripts/local_ci_check.py --root .`: pytest, compileall, public release check, git diff check를 순서대로 실행 가능
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000`: 실행 중인 서버 기준 문서/RAG E2E smoke test 가능
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server`: 실행 중인 서버 기준 Assistant UI bridge smoke test 가능
- `.venv/bin/python scripts/public_release_check.py --root . --json`: GitHub 공개 전 로컬 데이터/secret 후보 read-only 점검 가능. 최신 검증 기준 `ok=true`, `scanned_files=134`, finding 없음
- `local-ai agent-plan "GitHub 웹 열고 내 폴더도 열어줘"`: 실행형 Agent 계획 생성 가능
- `local-ai agent-approve 1`: agent plan 승인 상태 기록 가능. 실제 실행은 하지 않음
- `local-ai agent-execute 1`: 승인된 run 실행 시도 가능. 기본 설정에서는 고위험 실행을 차단함
- `local-ai assistant` 내부 `/summary`, `/roots`, `/status`, `/next`, `/shell-policy`, `/shell-dry-run pwd`: 로컬 비서 세션과 안전 정책 확인 가능
- `local-ai assistant-message "질문" --project-root /Users/juyoung/local-ai-server`: UI bridge와 같은 `/assistant/message` 호출 가능
- `local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server`: 실제 실행 없이 intent, 위험도, 필요 입력값 preview 가능
- `local-ai assistant-action-loop-preflight "개인 API dispatch" --project-root /Users/juyoung/local-ai-server`: 실제 dispatch 없이 frozen plan preflight 확인 가능
- `local-ai assistant-action-loop-noop-dispatch "개인 API dispatch" --project-root /Users/juyoung/local-ai-server`: 실제 dispatch 없이 no-op route plan과 audit 확인 가능
- `local-ai assistant-action-loop-read-only-dispatch-preview "read only dispatch" --project-root /Users/juyoung/local-ai-server`: 실제 dispatch/파일 읽기/URL fetch 없이 read-only boundary 분류 가능
- `local-ai assistant-automation-plan "내 개인 API 자동화" --project-root /Users/juyoung/local-ai-server`: 현재 가능/차단/승인 필요 범위를 plan-only로 확인 가능
- `local-ai assistant-ping`, `local-ai assistant-config`, `local-ai assistant-dashboard`: UI 연결 확인, secret 없는 설정 조회, 대시보드 카드 상태 확인 가능
- `local-ai assistant-ui-contract`: UI 시작 순서, refresh endpoint, 메시지 흐름, 응답 타입, 차단 기능 계약 요약 확인 가능
- `local-ai assistant-startup`: UI 초기 렌더링용 ping/config/dashboard/ui-contract snapshot 확인 가능
- `local-ai assistant-messages session-1 --limit 50 --offset 0`: 긴 대화 기록을 paging으로 조회 가능
- `local-ai assistant-status`: UI 첫 화면용 문서/세션/integrity/안전 상태 요약 확인 가능
- `local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server`: UI 시작에 필요한 capabilities/status/project root/session/UI 힌트 통합 응답 확인 가능

## 구현된 문서 타입

기본 지원:

- `.txt`
- `.md`
- `.html`
- `.htm`

optional dependency 설치 시 지원:

- `.pdf`
- `.docx`
- PDF OCR fallback: `[ocr]` extra와 로컬 `tesseract`가 준비된 경우, 일반 텍스트 추출이 비어 있거나 매우 짧은 PDF 페이지에서 PyPDF image XObject에 한해 적용

지원하지 않는 것:

- PyPDF가 image XObject를 추출하지 못하는 flat scan PDF OCR
- JavaScript 렌더링 결과
- 외부 URL 크롤링
- 브라우저 interaction

## 보안과 운영 기준

- 기본 서버 bind는 `127.0.0.1` 권장
- `LOCAL_API_KEY` 설정 시 보호 endpoint는 `X-API-Key` 또는 `Authorization: Bearer <LOCAL_API_KEY>` 필요
- `LOCAL_CORS_ORIGINS` 기본값으로 `127.0.0.1:5173`, `localhost:5173` 로컬 UI 호출 허용
- 보호 endpoint에는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit 적용
- 실행형 Agent는 계획, dry-run, 승인, 실행 엔진 v1 단계이며 기본값에서는 실제 실행 비활성
- 실행 엔진 v1은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원
- shell dry-run은 allowlist/blocked token 기반 정책 판단만 제공하며 실제 명령을 실행하지 않음
- assistant message API는 UI 입력을 안전하게 RAG/search/index preview/agent plan/shell dry-run으로 분기
- `.env`, SQLite DB, Chroma index, 업로드 파일, 로그 파일, SFT export 파일은 Git 제외
- 질문/답변/문서 원문/API key를 운영 로그에 남기지 않는 것을 권장
- 실제 repair/delete/rebuild, 외부 크롤링, 시스템 의존성 설치, 운영 배포는 사용자 승인 전 진행하지 않음

관련 문서:

- `README.md`
- `docs/API.md`
- `docs/TASKS.md`
- `docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md`
- `docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md`
- `docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md`
- `docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md`
- `docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md`
- `docs/OCR_INTEGRATION_PLAN.md`
- `docs/USER_DOCUMENT_E2E_PLAN.md`
- `docs/SMOKE_SUMMARY_EXAMPLES.md`
- `docs/PREVIEW_ACTIVATION_POLICY.md`
- `docs/UI_BRIDGE_EXAMPLES.md`
- `docs/UI_QA_CHECKLIST.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/PUBLIC_RELEASE_SUMMARY.md`
- `docs/OPERATIONS.md`
- `SECURITY.md`
- `docs/WORKLOG.md`
- `docs/NEXT_CHAT_HANDOFF.md`

## 현재 한계

- 실시간 색인 진행률 job API는 아직 없다.
- Chroma/SQLite repair는 read-only integrity와 repair preview까지만 제공한다.
- Agent는 실제 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 아직 지원하지 않는다.
- shell dry-run은 실행 엔진이 아니라 사전 정책 판단 기능이다.
- Agent file action은 `AGENT_ALLOWED_ROOTS` 안에서만 read-only로 동작한다.
- Agent file preview는 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자를 차단한다.
- Agent URL fetch는 `AGENT_WEB_FETCH_ENABLED=true`일 때만 동작하고 `AGENT_WEB_FETCH_MAX_BYTES` 이후 응답을 자른다.
- OCR은 PDF fallback 범위에서만 지원한다. PyPDF image XObject 추출이 불가능한 스캔 PDF, page rendering 기반 OCR, poppler/pdf2image fallback은 아직 지원하지 않는다.
- HTML은 정적 UTF-8 텍스트 추출만 지원한다.
- 인증은 단일 `LOCAL_API_KEY` 수준이다.
- 다중 사용자 권한 관리와 HTTPS termination은 없다.
- rate limit은 단일 프로세스 메모리 기준이며, 분산 rate limit은 없다.

## 다음 추천 개선

Codex가 바로 이어서 할 수 있는 안전한 개선:

1. README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트와 runtime endpoint count drift check 유지
2. README/Project Summary Runtime Contract Snapshot 값을 실제 API/CLI/smoke flow inventory와 비교하는 계약 유지
3. 승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary가 민감 정보 없이 유지되는지 검증
4. 대용량 색인 job/status API progress response schema preview-only 계약을 기준으로 실제 queue 활성화 조건 문서 유지
5. Chroma 누락 vector 재생성 preview-only endpoint를 기준으로 실제 rebuild 활성화 조건 문서 유지
6. assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 표시 기준과 함께 유지
7. PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지

별도 승인 또는 보안 리뷰가 필요한 개선:

1. 실제 repair/delete/rebuild 실행 명령
2. 실제 브라우저 click/fill/submit 자동화
3. 실제 shell 실행 또는 파일 생성/수정/삭제 자동화
4. JavaScript 렌더링, 외부 URL 크롤링, pdf2image/poppler 기반 page rendering OCR 확장
5. 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit
6. DB migration, 운영 데이터 변경, 비용이 발생할 수 있는 cloud/Oracle 리소스 사용
