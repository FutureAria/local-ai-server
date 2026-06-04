# Durable State Preview API Surface Decision Required

작성일: 2026-06-03 KST

## 목적

73차 Durable State Preview API Surface Decision Required는 72차 `durable_state_preview.v1` schema 후보를 실제 API로 노출할지 결정하기 전 필요한 인증, 마스킹, 감사, 저장소, 실행 차단 조건을 문서/테스트로 고정하는 단계다.

이번 단계에서는 실제 endpoint를 추가하지 않는다. 실제 durable storage migration, durable table creation, queue worker, scheduler, daemon/service/background loop, automatic replay, autonomous recovery도 구현하지 않는다.

## 현재 결론

- durable-state-preview-api-surface-decision-required 상태다.
- endpoint exposure remains blocked
- no durable-state-preview endpoints added
- no durable storage migration
- no durable table created
- no queue worker started
- no scheduler started
- no daemon/service/background loop
- no automatic replay
- no autonomous recovery
- no action-loop full dispatch
- no browser actual interaction
- no app-os actual action
- no git reset/bulk restore
- no staging/commit/push

## Candidate API Surface

아래 endpoint들은 후보 이름일 뿐이며 73차에서는 FastAPI route로 추가하지 않는다.

| candidate endpoint | 73차 status | required decision |
|---|---|---|
| `POST /assistant/durable-state-preview/preview` | blocked | schema-only preview 생성 여부, persistence 없이 response-only로 둘지 결정 |
| `GET /assistant/durable-state-preview/{preview_state_id}` | blocked | preview_state_id 조회가 raw approval id/payload_hash를 노출하지 않는지 결정 |
| `GET /assistant/durable-state-preview` | blocked | list endpoint가 owner/session scope와 TTL visibility를 지키는지 결정 |
| `POST /assistant/durable-state-preview/cleanup-expired` | blocked | cleanup이 persistence mutation인지, approval consume과 분리되는지 결정 |

## Exposure Requirements

후보 endpoint를 실제로 열려면 아래 조건이 먼저 필요하다.

- `LOCAL_API_KEY required`
- protected endpoint only
- read-only/schema-only response
- masked response only
- raw approval id not included
- payload_hash not included
- raw secrets not included
- raw browser content not included
- raw shell stdout/stderr not included beyond existing masking caps
- `audit_summary_hash` required
- `state_schema_version=durable_state_preview.v1`
- `state_status=candidate-preview`
- owner/session/request context binding
- payload_hash binding
- approval/audit lock required
- manual_review_required=true
- stop_on_first_blocked=true

## Route Absence Lock

73차에서는 아래 route가 없어야 한다.

- `POST /assistant/durable-state-preview/preview remains absent`
- `GET /assistant/durable-state-preview/{preview_state_id} remains absent`
- `GET /assistant/durable-state-preview remains absent`
- `POST /assistant/durable-state-preview/cleanup-expired remains absent`

Route absence는 “사용자 최종 승인과 Opus 리뷰 전까지 API surface를 열지 않는다”는 안전 계약이다.

## State Boundary

Durable state preview API 후보는 실행 권한이 아니다.

- state_preview_is_not_execution
- state_preview_does_not_consume_approval
- state_preview_does_not_mutate_queue
- endpoint_candidate_is_not_exposure
- route_absence_is_required
- `would_expose_endpoint=false`
- `would_persist=false`
- `would_start_worker=false`
- `would_schedule=false`
- `would_replay=false`
- `would_recover=false`
- `would_dispatch=false`
- `approval_consumed=false`
- `FULL_AUTOMATION_DISPATCH_ENABLED=false`
- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`

## Approval/Audit Lock

기존 approval store binding은 유지된다.

- server-issued approval id
- single-use
- TTL
- owner/session/request context binding
- payload_hash binding
- client-supplied approval-like JSON rejected
- approval console state cannot override payload_hash
- cleanup is not approval consume
- approve/reject routes not added
- approval console remains read-only for pending/list/detail/cleanup

## Stop Conditions

아래가 필요하면 73차 Codex 작업을 멈추고 사용자 최종 승인 또는 Opus 리뷰가 필요하다.

- durable-state-preview FastAPI route 추가
- durable-state-preview CLI command 추가
- 실제 durable storage migration
- durable table/queue table/scheduler state table 생성
- queue worker 실행
- scheduler/timer/cron/launchd/systemd 등록
- daemon/service/background loop 시작
- automatic replay
- autonomous retry/recovery
- action-loop full dispatch
- browser actual click/fill/type/submit/login/payment/delete
- app-os open/click/type/hotkey/file dialog
- git reset/clean/checkout 또는 bulk restore
- external provider 확장
- 운영 배포 또는 cloud/Oracle 리소스 변경
- staging/commit/push

## P0/P1/P2

### P0

- durable-state-preview endpoint exposure는 blocked 상태로 둔다.
- 실제 route/CLI command를 추가하지 않는다.
- durable state preview API 후보는 실행, approval consume, queue mutation, persistence mutation이 아니다.
- daemon/service/background loop는 계속 금지한다.
- action-loop full dispatch, browser actual interaction, app-os actual action은 계속 금지한다.

### P1

- README.md, SECURITY.md, docs/API.md, docs/TASKS.md, docs/WORKLOG.md, docs/NEXT_CHAT_HANDOFF.md에 73차 상태를 반영한다.
- public docs link contract에 이 문서를 포함한다.
- portfolio docs contract가 durable-state-preview-api-surface-decision-required 문구와 route absence를 검증한다.

### P2

- 74차에서 구현을 검토하더라도 먼저 read-only response-only preview endpoint 후보만 검토한다.
- 실제 persistence, worker, scheduler, replay queue는 별도 사용자 최종 승인과 Opus 리뷰 전 열지 않는다.

## Codex Follow-up Prompt

```text
프로젝트 루트:
/Users/juyoung/local-ai-server

역할:
Codex GPT-5.5 구현자.

현재 상태:
1~73차 계약 완료. 73차 Durable State Preview API Surface Decision Required는 실제 durable-state-preview endpoint를 추가하지 않고 후보 API surface, route absence, protected/masked/read-only/schema-only 조건을 문서/테스트로 고정했다.

먼저 실행:
cd /Users/juyoung/local-ai-server
pwd
ls
git status --short --branch
.venv/bin/python scripts/local_ci_check.py --root .

먼저 읽을 파일:
AGENTS.md
SECURITY.md
README.md
docs/TASKS.md
docs/WORKLOG.md
docs/NEXT_CHAT_HANDOFF.md
docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md
docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md
docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md
docs/API.md
app/api/assistant.py
app/services/assistant_service.py
tests/test_portfolio_docs_contract.py
tests/test_assistant_api.py

다음 작업:
74차 Durable State Preview Read-only API Candidate. 실제 persistence/worker/scheduler 없이 response-only/read-only/schema-only endpoint를 구현할지 검토한다. 구현한다면 protected endpoint only, masked response only, no persistence mutation, no approval consume, no queue mutation이 필수다.

금지:
durable storage migration, durable table creation, queue worker, scheduler, daemon/service/background loop, automatic replay, autonomous recovery, action-loop full dispatch, browser actual interaction, app-os actual action, git reset/bulk restore, staging/commit/push, 운영 배포.

최종 응답:
변경 파일, 테스트 결과, 열린 범위, 여전히 비활성인 범위, 다음 Recommended Next Model.
```
