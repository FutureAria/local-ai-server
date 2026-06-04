# Local Jarvis v1 Candidate Decision Required

작성일: 2026-06-03 KST

## 결론

61차 Local Jarvis v1 Candidate는 실제 action-loop full dispatch, browser actual interaction, app-os actual action을 활성화하는 단계가 아니다. 이 문서는 61~70차 후보 범위, 승인 조건, Opus review gate, 금지 조건을 고정한다.

현재 유지해야 하는 lock flags:

- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`
- `would_dispatch=false` for actual full dispatch
- `would_interact=false` for browser actual interaction
- `would_act=false` for app-os actual action

## 61차 Candidate Boundary

Local Jarvis v1 후보는 아래 세 갈래로만 검토한다.

| candidate | status | 61차 처리 |
|---|---|---|
| action-loop full dispatch candidate | review-required | 실제 dispatch 금지. route plan, approval consume design, failure/rollback/audit prerequisite만 정리 |
| limited browser actual interaction candidate | review-required | 실제 click/fill/type/submit 금지. allowed origin, selector, field, profile/session mutation policy만 정리 |
| limited app-os actual action candidate | review-required | 실제 app open/click/type/hotkey/file dialog 금지. observe-plan preview와 explicit user approval boundary만 정리 |

61차에서 허용되는 작업:

- candidate boundary 문서화
- public/security docs link sync
- tests drift guard 추가
- latest local CI, public release scanner, `git diff --check`, `git status --short --branch` 검증
- next handoff를 62차 Local Jarvis approval gate review로 갱신

61차에서 금지되는 작업:

- action-loop full dispatch 실제 연결
- browser engine/profile/session launch
- browser click/fill/type/submit/login/payment/delete/download/upload/file dialog
- app open/click/type/hotkey/file dialog
- daemon/service/background loop
- arbitrary shell, pipe/redirect/chaining/substitution
- bulk patch apply, file create/delete, workspace 밖 write
- git reset, git clean, bulk restore
- external LLM API, cloud vector DB, Oracle/cloud 리소스
- staging/commit/push

## Prerequisites From 54~60차

61차 이후 후보를 실제 구현으로 넘기려면 아래 54~60차 release-lock 산출물이 먼저 유지되어야 한다.

- 54차 Automation Roadmap / Release Lock
- 55차 Approval Consume Strategy Review
- 56차 Failure Strategy Matrix
- 57차 Audit Payload Schema Lock
- 58차 Connector Dry-run Replay Contract
- 59차 Release Lock Diff Inventory
- 60차 Release Lock Final Verification / Stage Decision Required

모든 후보는 다음 prerequisites를 통과해야 한다.

- server-issued approval id
- single-use approval
- TTL
- session/request context binding
- payload_hash binding
- approval-like JSON injection 차단
- connector별 failure/timeout/blocked paste-safe summary
- rollback availability 명시
- audit payload masked fields
- dry-run replay consistency
- wrapper untrusted boundary 유지

## User Final Approval Required

아래 항목은 사용자 최종 승인 없이는 진행하지 않는다.

- `FULL_AUTOMATION_DISPATCH_ENABLED=true`에서 full dispatch connector consume mode 변경
- browser actual interaction env flag 도입 또는 실제 browser automation tool 연결
- app-os actual action env flag 도입 또는 실제 OS/application automation tool 연결
- persistent profile/session mutation
- task worker가 browser/app-os/external action을 실행하는 구조
- staging/commit/push

사용자가 승인해야 할 최소 문구:

```text
61~70차 Local Jarvis v1 Candidate 중 <범위>를 <목적>으로 실제 구현 검토 승인합니다.
단, <금지 범위>는 유지합니다.
```

## Opus Review Gate

아래 단계는 Claude Opus 보안/아키텍처 리뷰 전에는 구현하지 않는다.

- action-loop full dispatch actual execution
- browser actual click/fill/type/submit
- app-os actual action
- daemon/service/background loop
- credential, session, browser profile, local app control 관련 정책 변경
- external provider 범위 확장

Opus review는 최소 아래를 검토해야 한다.

- P0/P1/P2 risk list
- approval consume mode 전환 조건
- rollback strategy
- audit payload schema
- failure/timeout handling
- browser/app-os safety boundary
- user consent wording
- disable switch and emergency stop

## Stage/Commit Boundary

61차에서도 staging/commit/push는 수행하지 않는다. 현재 누적 diff를 commit하려면 사용자가 commit scope, commit message, push/PR 여부를 명시해야 한다.

commit 전 필수 확인:

- `.venv/bin/python scripts/local_ci_check.py --root .`
- `.venv/bin/python scripts/public_release_check.py --root . --json`
- `git diff --check`
- `git status --short --branch`

## 62차 후보

62차 Local Jarvis Approval Gate Review에서 실제 action을 열지 않고 아래 항목을 문서/테스트로 더 좁힌다.

- candidate별 approval consume transition table
- user final approval wording
- Opus review prompt
- disabled default flags
- emergency stop / kill-switch checklist
- no actual browser/app-os/action-loop full dispatch
