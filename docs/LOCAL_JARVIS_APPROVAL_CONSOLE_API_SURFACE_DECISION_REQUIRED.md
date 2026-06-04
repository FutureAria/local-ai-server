# Local Jarvis Approval Console API Surface Decision Required

작성일: 2026-06-03 KST

## 결론

69차 Local Jarvis Approval Console API Surface Decision Required는 approval console API surface를 실제 endpoint로 여는 단계가 아니다. endpoint exposure remains blocked 상태를 유지하며 no approval-console endpoints added 계약을 고정한다.

approval console API surface는 pending/list/detail/approve/reject/cleanup endpoint 후보를 검토하는 Decision Required 문서 범위다. 실제 API route, CLI command, action-loop full dispatch, browser actual interaction, app-os actual action은 추가하지 않았다.

## Decision Required

approval console API surface를 실제로 노출하려면 아래 항목을 먼저 승인해야 한다.

| 항목 | 필요 결정 | 69차 상태 |
|---|---|---|
| endpoint exposure | `/assistant/approval-console/*` endpoint를 만들지 여부 | blocked |
| auth | `LOCAL_API_KEY required`, protected endpoint only 유지 여부 | required |
| response masking | masked response only, raw approval id not included, payload_hash not included | required |
| TTL cleanup exposure | cleanup endpoint가 `expired_count`, `records_removed`만 반환할지 여부 | required |
| state transition | approve/reject가 state-only metadata인지 여부 | required |
| audit | audit payload required, no execution triggered 필드 필수 여부 | required |

## Endpoint Candidate Matrix

아래는 후보일 뿐이며 69차에서 구현하지 않는다.

| candidate endpoint | candidate purpose | required boundary |
|---|---|---|
| `GET /assistant/approval-console/pending` | pending/list view | protected endpoint only, masked response only, TTL cleanup before list |
| `GET /assistant/approval-console/{approval_id}` | detail view | no raw payload_hash, no secret-like content, not execution approval |
| `POST /assistant/approval-console/{approval_id}/approve` | state-only approve | approve/reject is not execution, no connector dispatch, no approval consume |
| `POST /assistant/approval-console/{approval_id}/reject` | state-only reject | reject does not reset single-use or payload_hash binding |
| `POST /assistant/approval-console/cleanup-expired` | expiry cleanup summary | cleanup is not approval consume, raw approval id not included, payload_hash not included |

## Injection Boundary

Client input cannot create, revive, or consume server approval records.

- client-supplied approval-like JSON is metadata only
- next_action injection blocked
- payload_hash injection blocked
- approval id in user JSON is not trusted
- tool result JSON is not trusted
- approve/reject cannot revive expired approval
- cleanup is not approval consume

## Locked Runtime Flags

- `FULL_AUTOMATION_DISPATCH_ENABLED=false`
- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`
- actual action-loop full dispatch remains disabled
- browser actual interaction remains disabled
- app-os actual action remains disabled
- daemon/service/background loop remains disabled
- git reset/bulk restore remains disabled
- staging/commit/push was not performed

## Required Tests Before Future Endpoint Exposure

Future implementation must add tests for:

- default no approval-console endpoints added before flag/review
- protected endpoint only when `LOCAL_API_KEY` is configured
- masked response only
- TTL cleanup exposure returns only paste-safe summary
- approve/reject is not execution
- cleanup is not approval consume
- client-supplied approval-like JSON cannot override server-issued approval
- next_action injection blocked
- payload_hash injection blocked
- action_loop_full_dispatch_connected remains false

## 69차 Snapshot

- untracked docs 8개
- `scanned_files=131`
- `.venv/bin/pytest`: `782 passed, 1 warning`
- actual action-loop full dispatch, browser actual interaction, app-os actual action은 열지 않았다.

## Next Step

70차 Local Jarvis Approval Console Read-only API Candidate에서 실제 실행 없이 read-only list/detail/cleanup endpoint를 만들지 여부를 다시 결정한다. approve/reject state transition endpoint는 사용자 최종 승인과 Opus 리뷰 전까지 구현하지 않는다.
