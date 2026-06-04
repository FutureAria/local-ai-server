# Durable State Preview Schema Candidate

작성일: 2026-06-03 KST

## 목적

72차 Durable State Preview Schema Candidate는 실제 durable worker, scheduler, daemon, service, background loop를 열지 않고 durable state preview schema/proposal-only contract만 고정하는 단계다.

71차 Durable Automation v2 Candidate Decision Required가 persistence/recovery/replay boundary와 approval/audit lock을 정리했다면, 72차는 그 다음에 필요한 state preview 형태를 문서화한다. 이 문서는 실행 API가 아니고 저장소 migration도 아니다.

## 현재 결론

- durable-state-preview-schema-candidate 상태다.
- proposal-only contract
- schema-only
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

## Durable State Preview v1

`durable_state_preview.v1`은 실행 전 사람이 검토할 수 있는 paste-safe metadata schema 후보로만 둔다.

| field | required | rule |
|---|---:|---|
| `state_schema_version=durable_state_preview.v1` | yes | schema identity only |
| `preview_state_id` | yes | server generated candidate id; raw approval id 아님 |
| `state_status=candidate-preview` | yes | execution state가 아님 |
| `owner_session_ref` | yes | owner/session/request context binding |
| `request_context_ref` | yes | request context binding |
| `plan_ref` | yes | frozen plan reference only |
| `payload_hash_ref` | yes | payload_hash binding reference only; raw payload_hash 미노출 |
| `masked_params` | yes | masked params only |
| `candidate_steps` | yes | step summary only, connector dispatch 권한 아님 |
| `recovery_boundary` | yes | recovery metadata only |
| `replay_boundary` | yes | replay metadata only |
| `approval_boundary` | yes | approval/audit lock summary only |
| `audit_summary_hash` | yes | UI-facing summary hash, raw approval id/payload_hash 미노출 |
| `manual_review_required=true` | yes | 사람이 승인/검토하기 전 실행 불가 |
| `stop_on_first_blocked=true` | yes | blocked step 뒤 자동 진행 금지 |

## Execution Flags

Durable state preview는 실행이 아니다.

- `state_preview_is_not_execution`
- `state_preview_does_not_consume_approval`
- `state_preview_does_not_mutate_queue`
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

## Persistence Boundary

72차에서는 persistence 후보를 실제 DB schema로 만들지 않는다.

- no durable storage migration
- no durable table created
- no scheduler state table
- no queue mutation
- no retention job
- no automatic cleanup job
- no raw secrets
- no raw approval id
- no raw payload_hash
- no raw browser content
- no unmasked shell stdout/stderr
- masked params only

## Recovery Boundary

Recovery는 사람이 볼 수 있는 후보 metadata여야 한다.

- recovery metadata only
- auto_recovery=false
- auto_retry=false
- manual_review_required=true
- stop_on_first_blocked=true
- rollback_available must be explicit
- rollback_unavailable must be explicit
- paste-safe recovery summary only

## Replay Boundary

Replay는 connector 재실행 권한이 아니다.

- replay preview only
- no automatic replay
- no queued replay worker
- state_preview_does_not_consume_approval
- state_preview_does_not_mutate_queue
- replay_does_not_dispatch_connector
- replay_requires_original_plan_hash
- replay_blocks approval-like JSON injection
- replay_blocks next_action mutation

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
- raw approval id not included
- payload_hash not included
- `audit_summary_hash` 사용

## Stop Conditions

아래가 필요하면 72차 Codex 작업을 멈추고 사용자 최종 승인 또는 Opus 리뷰가 필요하다.

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

- durable state preview는 실행이 아니다.
- durable state preview는 approval consume이 아니다.
- durable state preview는 queue mutation이 아니다.
- durable storage migration과 durable table creation은 하지 않는다.
- daemon/service/background loop는 계속 금지한다.
- action-loop full dispatch, browser actual interaction, app-os actual action은 계속 금지한다.

### P1

- README.md, SECURITY.md, docs/API.md, docs/TASKS.md, docs/WORKLOG.md, docs/NEXT_CHAT_HANDOFF.md에 72차 상태를 반영한다.
- public docs link contract에 이 문서를 포함한다.
- portfolio docs contract가 durable-state-preview-schema-candidate 문구를 검증한다.

### P2

- 73차에서 API surface를 검토하더라도 read-only preview API 후보만 검토한다.
- 실제 persistence, worker, scheduler, replay queue는 별도 사용자 최종 승인과 Opus 리뷰 전 열지 않는다.

## Codex Follow-up Prompt

```text
프로젝트 루트:
/Users/juyoung/local-ai-server

역할:
Codex GPT-5.5 구현자.

현재 상태:
1~72차 계약 완료. 72차 Durable State Preview Schema Candidate는 실제 durable worker, scheduler, daemon/service/background loop, durable storage migration 없이 durable_state_preview.v1 proposal-only contract를 문서/테스트로 고정했다.

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
docs/API.md
app/services/assistant_service.py
tests/test_portfolio_docs_contract.py

다음 작업:
73차 Durable State Preview API Surface Decision Required. 실제 durable persistence/worker/scheduler 없이 read-only durable state preview API surface를 열지 여부를 Decision Required로 검토한다.

금지:
durable storage migration, durable table creation, queue worker, scheduler, daemon/service/background loop, automatic replay, autonomous recovery, action-loop full dispatch, browser actual interaction, app-os actual action, git reset/bulk restore, staging/commit/push, 운영 배포.

최종 응답:
변경 파일, 테스트 결과, 열린 범위, 여전히 비활성인 범위, 다음 Recommended Next Model.
```
