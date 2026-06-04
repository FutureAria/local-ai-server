# Durable Automation v2 Candidate Decision Required

작성일: 2026-06-03 KST

## 목적

71차 Durable Automation v2 Candidate Decision Required는 실제 durable worker, scheduler, daemon, service, background loop를 열지 않고 장기 자동화 후보 조건을 문서/테스트로 고정하는 단계다.

70차까지는 Local Jarvis approval console read-only API를 protected/masked endpoint로 열었지만, approval console은 실행 권한이 아니다. 71차에서는 durable automation v2가 필요해질 때 어떤 persistence, recovery, replay, approval, audit 조건을 먼저 만족해야 하는지 정리한다.

## 현재 결론

- durable-automation-v2-candidate-decision-required 상태다.
- no durable worker started
- no scheduler started
- no daemon/service/background loop
- no automatic replay
- no autonomous recovery
- no action-loop full dispatch
- no browser actual interaction
- no app-os actual action
- no git reset/bulk restore
- no staging/commit/push

## Candidate Scope

Durable Automation v2 후보는 아래 기능을 검토 대상으로만 둔다.

| candidate | 71차 status | required decision |
|---|---|---|
| durable task persistence | decision-required | 저장소 schema, retention, masking, owner/session binding |
| replay queue | decision-required | replay source, replay idempotency, dry-run first |
| recovery checkpoint | decision-required | checkpoint schema, failure boundary, rollback availability |
| scheduler loop | blocked | daemon/service/background loop 사용자 승인 필요 |
| autonomous retry | blocked | retry budget, stop-on-first-blocked, human review 필요 |
| action-loop full dispatch | blocked | 사용자 최종 승인과 Opus 리뷰 전 금지 |
| browser actual interaction | blocked | click/fill/submit/login/payment/delete 금지 |
| app-os actual action | blocked | app open/click/type/hotkey/file dialog 금지 |

## Persistence Boundary

Durable state를 만들려면 아래가 먼저 결정되어야 한다.

- persistence_schema_v2
- retention policy
- owner/session/request context binding
- payload_hash binding
- masked params only
- no raw secrets
- no raw browser content
- no raw shell stdout/stderr beyond existing masking caps
- no raw approval id in UI-facing summaries
- audit_summary_hash instead of exposing payload_hash

현재 71차에서는 새 durable storage table, queue table, scheduler state table을 만들지 않는다.

## Recovery Boundary

Recovery 후보는 실행이 아니라 실패 상태를 설명하는 metadata여야 한다.

- recovery_plan is metadata only
- auto_recovery=false
- auto_retry=false
- stop_on_first_blocked=true
- manual_review_required=true
- rollback_available must be explicit
- rollback_unavailable must be explicit
- paste-safe recovery summary only

현재 71차에서는 failure recovery preview, rollback preview/executor의 기존 제한 범위를 넓히지 않는다.

## Replay Boundary

Replay 후보는 connector 재실행 권한이 아니다.

- replay_candidate is dry-run first
- replay_does_not_consume_approval
- replay_does_not_mutate_state
- replay_does_not_dispatch_connector
- replay_requires_original_plan_hash
- replay_requires_wrapper_untrusted=true
- replay_blocks approval-like JSON injection
- replay_blocks next_action mutation

현재 71차에서는 automatic replay 또는 queued replay worker를 구현하지 않는다.

## Approval/Audit Lock

Durable Automation v2는 기존 approval store binding을 약화할 수 없다.

- server-issued approval id
- single-use
- TTL
- session/request context binding
- payload_hash binding
- client-supplied approval-like JSON rejected
- approval console state cannot override payload_hash
- cleanup is not approval consume
- read-only approval console remains read-only

감사 payload에는 실행 여부를 명시해야 한다.

- `durable_automation_v2_candidate=true`
- `would_start_worker=false`
- `would_schedule=false`
- `would_replay=false`
- `would_recover=false`
- `would_dispatch=false`
- `approval_consumed=false`
- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`

## Stop Conditions

아래가 필요하면 71차 Codex 작업을 멈추고 사용자 최종 승인 또는 Opus 리뷰가 필요하다.

- 실제 daemon/service/background loop 시작
- scheduler/timer/cron/launchd/systemd 등록
- durable queue worker 실행
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

- daemon/service/background loop는 계속 금지한다.
- action-loop full dispatch는 계속 금지한다.
- browser actual interaction과 app-os actual action은 계속 금지한다.
- approval store single-use/TTL/session/payload_hash binding은 유지한다.
- replay/recovery/persistence 후보는 실행 권한이 아니다.

### P1

- docs/API.md, README.md, SECURITY.md, TASKS, WORKLOG, NEXT_CHAT_HANDOFF에 71차 상태를 반영한다.
- public docs link contract에 이 문서를 포함한다.
- portfolio docs contract가 durable-automation-v2-candidate-decision-required 문구를 검증한다.

### P2

- 72차에서 구현할 경우에도 먼저 read-only durable state preview 또는 schema-only proposal부터 검토한다.
- scheduler/daemon/worker는 별도 사용자 최종 승인과 Opus 리뷰 전 열지 않는다.

## Codex Follow-up Prompt

```text
프로젝트 루트:
/Users/juyoung/local-ai-server

역할:
Codex GPT-5.5 구현자.

현재 상태:
1~71차 계약 완료. 71차 Durable Automation v2 Candidate Decision Required는 실제 durable worker, scheduler, daemon/service/background loop를 열지 않고 persistence/recovery/replay boundary와 approval/audit lock을 문서/테스트로 고정했다.

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
docs/API.md
app/services/assistant_service.py
tests/test_portfolio_docs_contract.py

다음 작업:
72차 Durable State Preview Schema Candidate. 실제 worker/scheduler/daemon/background loop 없이 durable state preview schema 또는 proposal-only contract를 검토한다.

금지:
action-loop full dispatch, browser actual interaction, app-os actual action, daemon/service/background loop, automatic replay, autonomous recovery, git reset/bulk restore, staging/commit/push, 운영 배포.

최종 응답:
변경 파일, 테스트 결과, 열린 범위, 여전히 비활성인 범위, 다음 Recommended Next Model.
```
