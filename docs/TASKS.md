# TASKS

이 문서는 `local-ai-server`의 다음 작업을 안전 범위별로 나누어 추적한다.

현재 프로젝트는 로컬 전용 FastAPI/Ollama/SQLite/Chroma 백엔드와 Typer CLI를 구현한 상태다. 다음 작업은 기본적으로 문서, 테스트, API 계약, smoke 검증 중심으로 진행한다.

## 상태 기준

| 상태 | 의미 | 진행 조건 |
|---|---|---|
| `done` | 구현, 문서화, 테스트가 완료된 항목 | 검증 결과를 `docs/WORKLOG.md`에 기록 |
| `safe-next` | Codex가 바로 이어서 할 수 있는 안전 작업 | 외부 LLM API, arbitrary shell 실행, 파일 수정/삭제 자동화, 브라우저 interaction 없음. 실제 shell 실행은 27차 allowlist 단건 범위를 제외하면 review-required |
| `manual-check` | 사용자가 로컬 화면 또는 실제 서버에서 확인해야 하는 작업 | Codex가 브라우저 조작이나 메시지 전송을 대신하지 않음 |
| `review-required` | 보안/운영 리뷰 또는 사용자 승인이 필요한 작업 | 실제 실행, 삭제, 배포, 외부 호출, 비용/보안 영향 가능 |
| `blocked` | 현재 범위 밖 작업 | 별도 설계와 승인 전 진행하지 않음 |

## 완료된 핵심 작업

- [x] FastAPI MVP와 `/health`, `/ask`
- [x] SQLite metadata, chunk, chat log, feedback 저장
- [x] `.txt`, `.md`, `.html`, `.htm`, optional `.pdf`, `.docx` 문서 로더
- [x] Chroma vector search와 Ollama local embedding
- [x] `/ask-with-docs` RAG 답변 API
- [x] 폴더 색인과 read-only index preview
- [x] Typer 기반 `local-ai` CLI
- [x] feedback 저장과 SFT JSONL export
- [x] assistant bridge API와 CLI
- [x] 개인 API 자동화 plan-only preflight API와 CLI
- [x] 4차 read-only 자동화 API와 CLI
- [x] project continuation API, API inventory, shell dry-run policy
- [x] agent plan/approval/read-only execution v1
- [x] PDF OCR fallback 설계와 PyPDF image XObject 기반 optional OCR loader
- [x] public release check와 local CI script
- [x] README, API, 운영, 보안, 최종 보고 문서

## Codex가 바로 이어서 할 수 있는 안전 작업

- [x] OpenAI Codex for OSS 신청 준비용 공개 문구, GitHub checklist, 기여 가이드, 라이선스 정리
- [x] README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트 유지
- [x] runtime endpoint count drift check 유지
- [x] README/Project Summary Runtime Contract Snapshot 값을 실제 API/CLI/smoke flow inventory와 비교하는 테스트 유지
- [x] assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 기준으로 유지
- [x] `scripts/smoke_test_api.py --sanitized-summary` 결과 예시가 원문/secret/local path를 제외하는지 계속 검증
- [x] 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 기준 upload/search/ask-with-docs end-to-end 재검증 결과를 paste-safe summary로 기록
  - 준비 문서: `docs/USER_DOCUMENT_E2E_PLAN.md`
  - 승인 후 `docs/PROJECT_SUMMARY.md` 기준으로 실행했고, safe-to-paste summary를 `docs/WORKLOG.md`에 기록했다.
- [x] 대용량 색인 job/status API progress response schema를 preview-only 계약 기준으로 문서화 유지
- [x] Chroma 누락 vector 재생성 preview-only endpoint 기준 실제 rebuild 활성화 조건 문서 유지
- [x] `docs/NEXT_CHAT_HANDOFF.md`와 이 문서의 safe/manual/review 경계 정합성 유지
- [x] PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지
- [x] `/assistant/automation-plan`과 `local-ai assistant-automation-plan`이 shell/browser/file-write/external API 활성화 없이 현재 가능/차단/승인 필요 범위를 반환하는 계약 유지
- [x] `/assistant/read-only-scan`, `/assistant/file-preview`, `/assistant/url-preview`, `/assistant/workspace-brief`가 원본 파일 수정, shell 실행, browser interaction, 기본 외부 fetch 없이 read-only 자동화 계약을 반환하는지 유지
- [x] `/assistant/shell-preview`, `/assistant/shell-approval-preview`, `/assistant/shell-run`이 allowlist, cwd 제한, timeout, masking, audit payload, approval binding을 유지하는지 검증. 27차부터 `/assistant/shell-run`은 `SHELL_EXECUTION_ENABLED=true`에서만 allowlist 단건 subprocess를 실행
- [x] `/assistant/patch-preview`, `/assistant/patch-approval-preview`, `/assistant/patch-apply`가 기본값 locked/disabled를 유지하고, 29차 env opt-in에서는 path allowlist, secret scan, approval binding, `original_sha256` precondition을 통과한 기존 UTF-8 단일 파일만 덮어쓰는지 유지
- [x] `/assistant/browser-preview`, `/assistant/browser-approval-preview`, `/assistant/browser-interact`가 browser/app action taxonomy, secret masking, approval binding, locked-interact 계약만 반환하고 실제 click/fill/submit/login/payment/delete 또는 OS app control을 하지 않는지 유지
- [x] `/assistant/browser-observe`가 `BROWSER_OBSERVE_ENABLED=false` 기본값을 유지하고, 31차 env opt-in에서는 loopback/명시 allowlist URL의 read-only metadata만 untrusted wrapper로 반환하는지 유지
- [x] `/assistant/browser-limited-interact`가 `BROWSER_LIMITED_INTERACTION_ENABLED=false` 기본값을 유지하고, 32차 env opt-in에서도 selector/origin/field/approval candidate validation만 수행하며 실제 browser launch/click/fill은 하지 않는지 유지
- [x] `/assistant/task-queue/drain`이 `TASK_QUEUE_WORKER_ENABLED=false` 기본값을 유지하고, 34차 env opt-in에서도 request-scoped one-shot drain으로 `noop`, `read_only_scan`, `file_preview` task만 처리하며 daemon/service/background loop와 shell/browser/external API/rollback/app-os task를 연결하지 않는지 유지
- [x] `/assistant/rollback-approval-preview`, `/assistant/rollback-execute`가 `ROLLBACK_EXECUTOR_ENABLED=false` 기본값을 유지하고, 35차 env opt-in에서도 rollback 전용 approval, current/original hash, allowed root, existing UTF-8 single file을 모두 통과한 단일 파일 restore만 수행하며 git reset/bulk restore/shell/browser/external API/task-worker/app-os/action-loop full dispatch를 연결하지 않는지 유지
- [x] `/assistant/full-automation-preflight`, `/assistant/full-automation-dispatch`가 `FULL_AUTOMATION_DISPATCH_ENABLED=false` 기본값을 유지하고, 36차에서는 통합 route plan과 dispatch gate만 반환하며 실제 connector dispatch와 approval consume을 수행하지 않는지 유지
- [x] `/assistant/full-automation-dispatch`가 37차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`일 때도 실제 connector 실행 없이 ordered route plan, dependency graph, failure/rollback strategy, per-step no-op wrapper aggregation만 반환하는지 유지
- [x] `/assistant/full-automation-dispatch`가 38차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`와 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`가 모두 켜진 경우에만 read-only category step을 기존 read-only adapter wrapper로 실행하고, shell/patch/rollback/task/browser/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 39차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `SHELL_EXECUTION_ENABLED=true`, valid shell approval, allowlist command, allowed cwd를 모두 통과한 shell category step만 기존 shell sandbox로 실행하고, patch/rollback/task/browser/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 40차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `PATCH_APPLY_ENABLED=true`, valid patch approval, allowed root, existing UTF-8 single file, original_sha256 precondition, secret scan을 모두 통과한 patch category step만 기존 patch boundary로 실행하고 rollback/task/browser/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 41차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `ROLLBACK_EXECUTOR_ENABLED=true`, valid rollback approval, allowed root, existing UTF-8 single file, current/original hash precondition을 모두 통과한 rollback category step만 기존 rollback boundary로 실행하고 task/browser/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 42차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `TASK_QUEUE_WORKER_ENABLED=true`, read-only task type, wrapper gate, params masking, approval-like JSON injection 차단을 모두 통과한 task_queue category step만 기존 one-shot worker boundary로 실행하고 browser/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 43차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `BROWSER_OBSERVE_ENABLED=true`, valid browser approval, loopback/명시 allowlist URL, read-only observe action을 모두 통과한 browser_observe category step만 기존 browser observe metadata boundary로 실행하고 browser actual interaction/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 44차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `BROWSER_LIMITED_INTERACTION_ENABLED=true`, valid browser approval, loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist를 모두 통과한 browser_limited_interaction category step만 기존 browser limited candidate validation boundary로 실행하고 browser actual interaction/external/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 45차에서 `FULL_AUTOMATION_DISPATCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, provider configured, rate limit, query safety, wrapper gate를 모두 통과한 external_web_search category step만 기존 external web search provider boundary로 실행하고 browser actual interaction/app-os는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 46차에서 app_os category step을 기존 app-os interaction preview boundary로만 처리하고 observe-plan candidate wrapper를 untrusted로 중첩하며 실제 app open/click/type/hotkey/file dialog는 계속 미연결로 유지하는지 검증
- [x] `/assistant/full-automation-dispatch`가 47차에서 safe/preview/mutating connector gate, audit payload, safety map을 실제 연결 범위와 일치시키고 browser actual interaction/app-os actual action/action-loop full dispatch가 계속 false/disabled인지 검증
- [x] 48차 Full Automation Action-loop Dispatch Decision Required를 문서/테스트로 고정해 실제 action-loop full dispatch는 계속 금지하고, connector별 approval consume, rollback/failure strategy, 사용자 최종 승인, Opus 리뷰 조건과 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false` 계약을 유지
- [x] 49차 Full Automation Contract Review / Runtime Drift Guard를 추가해 runtime `gates`/`audit.payload`/`safety`와 README/SECURITY/API/PROJECT_SUMMARY/TASKS/NEXT_CHAT_HANDOFF/Decision Required 문서가 actual action locked flag를 함께 유지하는지 검증
- [x] 50차 Full Automation Commit-readiness / Cumulative Diff Review를 `docs/CODEX_IMPLEMENTATION_NOTES.md`와 테스트로 고정해 누적 변경 파일 그룹, untracked docs 5개 의도성, 최신 local CI `755 passed, 1 warning`, 여전히 미연결인 actual action 범위를 정리
- [x] 51차 Full Automation Final Docs Sync / Handoff Freeze를 추가해 PROJECT_SUMMARY, FINAL_REPORT, CLAUDE_REVIEW_HANDOFF, PUBLIC_RELEASE_SUMMARY, TASKS, WORKLOG, NEXT_CHAT_HANDOFF의 최신 검증 수치와 commit-readiness 문구를 동기화
- [x] 52차 Final Verification Sweep / Commit Decision Required를 추가해 최종 검증 sweep, `git status --short --branch`, untracked docs 5개 의도성, `758 passed, 1 warning`, staging/commit/push 사용자 명시 요청 전 금지 계약을 문서/테스트로 고정
- [x] 53차 Commit / Stage Decision Required를 추가해 commit/stage decision packet, modified tracked files 40개, untracked docs 5개, `759 passed, 1 warning`, staging/commit/push 미수행, 사용자 commit 범위/message/push 여부 명시 필요 계약을 문서/테스트로 고정
- [x] 54차 Automation Roadmap / Release Lock을 추가해 54~90차 roadmap을 safe-next/review-required/blocked 경계로 재정렬하고, release lock, roadmap boundary contract, `760 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 55차 Approval Consume Strategy Review를 추가해 connector별 approval consume mode, failure strategy, rollback strategy, audit payload, wrapper trust boundary, `761 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 56차 Failure Strategy Matrix를 추가해 connector별 failure/timeout/blocked summary, rollback 가능/불가능 조건, paste-safe audit summary, `762 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 57차 Audit Payload Schema Lock을 추가해 connector별 audit payload schema, masked field policy, wrapper trust indicators, `763 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 58차 Connector Dry-run Replay Contract를 추가해 connector별 dry-run replay input/output, replay audit consistency, masked replay summary, `764 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 59차 Release Lock Diff Inventory를 추가해 54~58차 release-lock 누적 diff group, modified tracked files 40개, untracked docs 5개, commit-before checklist, `765 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 60차 Release Lock Final Verification / Stage Decision Required를 추가해 54~60차 release lock final verification contract, modified tracked files 40개, untracked docs 5개, stage/commit/push 미수행, commit scope/message/push 여부 Decision Required, `766 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 61차 Local Jarvis v1 Candidate Decision Required를 추가해 action-loop full dispatch candidate, limited browser actual interaction candidate, limited app-os actual action candidate, 사용자 최종 승인 조건, Opus review gate, untracked docs 6개, `767 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 62차 Local Jarvis Approval Gate Review를 추가해 approval consume transition table, user final approval wording, Opus review prompt, disabled default flags, emergency stop / kill-switch checklist, untracked docs 7개, `768 passed, 1 warning`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 63차 Local Jarvis Runtime Drift Guard를 추가해 runtime/docs/test, public docs link contract, Local Jarvis docs anchors, actual action false assertions, state-only/validate-only approval boundary, untracked docs 7개, `770 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 64차 Local Jarvis Failure/Timeout Drill을 추가해 failure/timeout/manual-review-required summary, paste-safe audit summary, emergency stop drill, `raw_error_content_allowed=false`, `auto_retry=false`, `stop_on_first_blocked=true`, untracked docs 7개, `772 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 65차 Local Jarvis Manual Review Packet을 추가해 manual-review-packet-is-not-approval, P0/P1/P2 checklist, approval wording diff, Opus review handoff, Codex Follow-up Prompt, untracked docs 7개, `774 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 66차 Local Jarvis Approval Console State-only Review를 추가해 approval console/pending/detail/approve/reject, approve-reject-state-only, state-change-is-not-execution, no execution on approve, masked payload, untracked docs 7개, `776 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 67차 Local Jarvis Approval Payload Hash Review를 추가해 payload-hash-binding-remains-authoritative, console-state-cannot-bypass-binding, approved-state-does-not-override-payload_hash, rejected-state-does-not-reset-single-use, untracked docs 7개, `778 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 68차 Local Jarvis Approval Store Expiry Cleanup Review를 추가해 approval-store-expiry-cleanup, expired-approval-not-visible-after-cleanup, pending/list/detail cleanup, paste-safe expired summary, raw approval id not included, payload_hash not included, approve/reject cannot revive expired approval, client-supplied approval-like JSON `unknown_approval`, `expired_count`, `records_removed`, untracked docs 7개, `780 passed, 1 warning`, `scanned_files=130`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 69차 Local Jarvis Approval Console API Surface Decision Required를 추가해 approval-console-api-surface-decision-required, endpoint exposure remains blocked, no approval-console endpoints added, pending/list/detail/approve/reject/cleanup endpoint 후보, `LOCAL_API_KEY required`, protected endpoint only, masked response only, TTL cleanup exposure, audit payload required, approve/reject is not execution, cleanup is not approval consume, untracked docs 8개, `782 passed, 1 warning`, `scanned_files=131`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 70차 Local Jarvis Approval Console Read-only API Candidate를 추가해 `GET /assistant/approval-console/pending`, `GET /assistant/approval-console/{approval_id}`, `POST /assistant/approval-console/cleanup-expired` protected read-only endpoint, approval-console-read-only, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash`, approve/reject routes not added, cleanup is not approval consume, `approval_consumed=false`, `would_execute=false`, FastAPI endpoints 93, protected endpoints 77, public endpoints 16, untracked docs 8개, `788 passed, 1 warning`, `scanned_files=131`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 71차 Durable Automation v2 Candidate Decision Required를 추가해 durable-automation-v2-candidate-decision-required, persistence/recovery/replay boundary, approval/audit lock, durable task persistence/replay queue/recovery checkpoint decision-required, no durable worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery, replay_candidate is dry-run first, manual_review_required=true, stop_on_first_blocked=true, `would_start_worker=false`, `would_schedule=false`, `would_replay=false`, `would_recover=false`, `would_dispatch=false`, `approval_consumed=false`, untracked docs 9개, `789 passed, 1 warning`, `scanned_files=132`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 72차 Durable State Preview Schema Candidate를 추가해 durable-state-preview-schema-candidate, proposal-only contract, schema-only, `state_schema_version=durable_state_preview.v1`, `preview_state_id`, `state_status=candidate-preview`, owner/session/request context binding, payload_hash binding, masked params only, no raw secrets, no raw approval id, payload_hash not included, `audit_summary_hash`, no durable storage migration, no durable table created, no queue worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery, `state_preview_is_not_execution`, `state_preview_does_not_consume_approval`, `state_preview_does_not_mutate_queue`, `would_persist=false`, `approval_consumed=false`, untracked docs 10개, `790 passed, 1 warning`, `scanned_files=133`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 73차 Durable State Preview API Surface Decision Required를 추가해 durable-state-preview-api-surface-decision-required, endpoint exposure remains blocked, no durable-state-preview endpoints added, candidate endpoint `POST /assistant/durable-state-preview/preview`, `GET /assistant/durable-state-preview/{preview_state_id}`, `GET /assistant/durable-state-preview`, `POST /assistant/durable-state-preview/cleanup-expired`, route_absence_is_required, `would_expose_endpoint=false`, `LOCAL_API_KEY required`, protected endpoint only, read-only/schema-only response, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash required`, no durable storage migration, no durable table created, no queue worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery, untracked docs 11개, `791 passed, 1 warning`, `scanned_files=134`, actual action 미연결 범위를 문서/테스트로 고정
- [x] 74차 Durable State Preview Read-only API Candidate를 추가해 `POST /assistant/durable-state-preview/preview` protected endpoint only, durable-state-preview-read-only, response-only/read-only/schema-only, `state_schema_version=durable_state_preview.v1`, `state_status=candidate-preview`, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash`, stored preview lookup/list/cleanup remain Decision Required, `GET /assistant/durable-state-preview/{preview_state_id} remains absent`, `GET /assistant/durable-state-preview remains absent`, `POST /assistant/durable-state-preview/cleanup-expired remains absent`, `stored_preview_lookup_connected=false`, `stored_preview_list_connected=false`, `stored_preview_cleanup_connected=false`, `would_execute=false`, `would_persist=false`, `would_dispatch=false`, `approval_consumed=false`, `durable_storage_migration_connected=false`, `durable_table_created=false`, `persistence_mutation_connected=false`, `queue_mutation_connected=false`, FastAPI endpoints 94, protected endpoints 78, public endpoints 16, untracked docs 11개, actual action 미연결 범위를 문서/테스트로 고정
- [x] 75차 Durable State Preview API Regression Guard로 read-only preview endpoint, absent stored preview routes, nested sensitive key redaction, no persistence mutation, no approval consume, no queue mutation, runtime inventory count drift를 회귀 테스트로 보강
- [x] 76차 Durable State Preview Docs/API Drift Guard로 API docs response fields, public docs endpoint listing, NEXT_CHAT_HANDOFF, release summary, security boundary 문구를 추가 점검
- [x] 77차 Durable State Preview Release-lock Guard로 74~76차 누적 durable-state-preview diff, 검증 수치, modified tracked files 40개, untracked docs 11개, staging/commit/push 금지를 release-lock 문서/테스트로 고정
- [x] 78차 Durable State Preview Final Verification Sweep으로 74~77차 durable-state-preview release-lock 구간의 full pytest/compileall/public-release/git diff/local CI를 다시 고정
- [x] 79차 Durable State Preview Handoff/Commit Readiness Packet으로 74~78차 durable-state-preview 누적 변경, 검증 수치, modified tracked files 40개, untracked docs 11개, staging/commit/push 미수행 상태를 commit-readiness 관점으로 정리
- [x] 80차 Durable Automation v2 Release-lock Final Decision Packet으로 71~79차 Durable Automation v2 Candidate 구간의 release-lock, 검증 수치, commit/stage Decision Required 상태를 최종 고정
- [x] 81차 Personal Automation Hardening Candidate Entry Decision으로 81~90차 구간 진입 조건, 사용자 승인/Opus review gate, actual action 금지 범위를 고정
- [x] 82차 Personal Automation Approval/Opus Gate Matrix로 user final approval gate, Opus review gate, connector별 blocked/review-required matrix를 고정
- [x] 83차 Personal Automation Failure/Stop Hardening Matrix로 stop-on-first-blocked, emergency stop, timeout/failure paste-safe summary를 고정
- [x] 84차 Personal Automation Audit/Observability Hardening으로 audit/observability/paste-safe reporting 범위를 고정
- [x] 85차 Personal Automation Session/Context Binding Review로 session/request context binding과 operator-visible context boundary를 고정
- [x] 86차 Personal Automation Operator Confirmation Boundary로 operator confirmation wording과 final human action boundary를 고정
- [x] 87차 Personal Automation Manual Review Packet Finalization으로 manual review packet 최종 형식과 escalation boundary를 고정
- [x] 88차 Personal Automation Release-lock Drift Guard로 81~87차 personal automation hardening 누적 경계를 고정
- [x] 89차 Personal Automation Final Verification Sweep으로 81~88차 personal automation hardening 구간을 최종 검증
- [x] 90차 Personal Automation Release-lock Final Decision Packet으로 81~89차 personal automation hardening 구간의 final decision/stage boundary를 고정
- [x] 91차 Commit / Stage Decision Required로 1~90차 누적 diff의 Commit / Stage Decision Required packet, stage/commit/push decision boundary, commit scope, commit message, push/PR 여부 사용자 최종 승인 필요, modified tracked files 40개, untracked docs 11개, `815 passed, 1 warning`, `scanned_files=134`, public release finding 없음, stage/commit/push 미수행을 문서/테스트로 고정
- [x] 92차 Commit Approval or Jarvis v1 Safe Planning으로 "멈추지 말고 해줘"를 git 작업 명시 승인으로 해석하지 않고, commit approval flow blocked, Jarvis v1 Safe Planning, 120차까지 28차 남음, 150차까지 58차 남음, safe planning only, docs/test/review-required 중심, actual action 없이 stage/commit/push 미수행을 문서/테스트로 고정
- [x] 93차 Jarvis v1 Safe Roadmap Drift Guard로 93~120차 Jarvis v1 실사용형 구간의 safe-next/review-required/blocked 경계, roadmap drift guard, actual action으로 새지 않게 막는 문서/테스트 guard, 120차까지 27차 남음, 150차까지 57차 남음, stage/commit/push 미수행을 문서/테스트로 고정
- [x] 94차 Jarvis v1 Capability Honesty Guard로 Jarvis v1 관련 문서가 실제 열린 기능, env opt-in 기능, blocked 기능을 정확히 구분하고, Jarvis v1은 실행형 완성 제품이 아니라 safe-local assistant boundary이며, capability wording이 actual action을 과장하지 않게 문서/테스트로 고정
- [x] 95차 Jarvis v1 Manual UX Contract Guard로 수동 UX, approval wording, blocked state 표시가 실제 runtime boundary와 일치하고 approval 상태 변경은 실행 승인으로 오해되면 안 되며 manual UX는 operator review surface임을 문서/테스트로 고정
- [x] 96차 Jarvis v1 Evidence Packet Guard로 Jarvis v1 관련 증거 패킷이 actual verification results, disabled boundary, remaining Decision Required를 함께 포함하고 실행하지 않은 검증/빌드/배포/실제 action을 완료처럼 표현하지 않도록 문서/테스트로 고정
- [x] 97차 Jarvis v1 Decision Required Packet Guard로 commit/browser/app-os/action-loop/durable activation Decision Required 항목이 증거 패킷과 handoff에 같이 남고 사용자 최종 승인이나 Opus review가 필요한 항목을 safe-next 작업으로 오분류하지 않도록 문서/테스트로 고정
- [x] 98차 Jarvis v1 Approval Wording Drift Guard로 approval wording이 실행 승인, 상태 변경, 검증 완료, Decision Required를 혼동하지 않고 approval 상태 변경, approved console state, confirmation state가 execution approval로 승격되지 않도록 문서/테스트로 고정
- [x] 99차 Jarvis v1 Release-lock Drift Guard로 92~98차 Jarvis v1 safe guard 누적 경계와 stage/commit/push 미수행 상태가 유지되고 browser/app-os/action-loop/daemon/durable execution이 다시 열리지 않았는지 문서/테스트로 고정
- [x] 100차 Jarvis v1 Final Verification Sweep으로 92~99차 Jarvis v1 safe guard 구간의 full pytest, compileall, public release check, git diff check, local CI, git status를 다시 확인하고 최신 검증 수치를 문서/테스트로 고정
- [x] 101차 Jarvis v1 Commit Readiness Packet으로 92~100차 Jarvis v1 safe guard 구간의 commit scope/message/push 여부 Decision Required를 다시 정리하고 사용자 최종 승인 필요 상태를 문서/테스트로 고정
- [x] 102차 Jarvis v1 Handoff Freeze로 92~101차 Jarvis v1 safe guard 구간의 다음 handoff와 검증 프롬프트를 동결
- [x] 103차 Jarvis v1 Release Candidate Prep으로 92~102차 Jarvis v1 safe guard 구간의 release candidate readiness와 남은 Decision Required를 정리
- [x] 104차 Jarvis v1 Final RC Verification으로 92~103차 Jarvis v1 safe guard 구간의 full verification과 RC boundary를 재확인
- [x] 105차 Jarvis v1 Final Stage Decision Packet으로 Jarvis v1 RC 구간의 stage/commit/push 최종 Decision Required를 정리
- [x] 106차 Jarvis v1 Public Release Guard로 public release scanner와 공개 문서의 Jarvis v1 안전 경계를 재확인
- [x] 107차 Jarvis v1 Evidence Freeze로 Jarvis v1 RC 증거 패킷과 검증 수치를 동결
- [x] 108차 Jarvis v1 Release Lock Refresh로 92~107차 Jarvis v1 RC 구간의 release lock과 남은 Decision Required를 갱신
- [x] 109차 Jarvis v1 Final Handoff Refresh로 108차 release lock 결과와 110차 다음 작업 프롬프트를 동결
- [x] 110차 Jarvis v1 Verification Refresh로 Jarvis v1 RC 구간의 최신 검증 수치와 public release scanner 기준을 재확인
- [x] 111차 Jarvis v1 Commit Boundary Refresh로 commit scope/message/push/PR 사용자 최종 승인 경계를 재확인
- [x] 112차 Jarvis v1 Final Verification Packet으로 Jarvis v1 RC 구간의 최종 검증 packet과 남은 Decision Required를 정리
- [x] 113차 Jarvis v1 Release Readiness Closure로 Jarvis v1 RC 구간의 release readiness와 commit 전 닫힘 상태를 정리
- [x] 114차 Jarvis v1 Commit Approval Decision Packet으로 commit approval 전 사용자 최종 승인 필요 항목을 다시 정리
- [x] 115차 Jarvis v1 Pre-120 Remaining Scope Plan으로 120차까지 남은 safe-next 범위를 정리
- [x] 116차 Jarvis v1 Pre-120 Verification Matrix로 남은 safe-next 검증 matrix를 고정
- [x] 117차 Jarvis v1 Pre-120 Handoff Sync로 118차 다음 handoff와 검증 프롬프트를 동기화
- [x] 118차 Jarvis v1 Pre-120 Final Evidence Refresh로 120차 직전 evidence 기준을 재확인
- [x] 119차 Jarvis v1 Readiness Freeze로 120차 직전 readiness 상태를 동결
- [x] 120차 Jarvis v1 실사용형 목표 Decision Packet으로 Jarvis v1 safe-local 실사용형 경계와 남은 Decision Required를 최종 정리
- [x] 121차 Jarvis v2 Entry Scope Plan으로 121~150차 v2 완성권 범위를 safe-next/review-required/blocked 경계로 분류
- [x] 122차 Jarvis v2 Safety Contract Matrix로 v2 안전 계약과 disabled boundary matrix를 고정
- [x] 123차 Jarvis v2 Runtime Docs Drift Guard로 runtime/docs drift와 capability honesty를 재확인
- [x] 124차 Jarvis v2 Capability Honesty Refresh로 실제 열린 기능/env opt-in/blocked 기능 문구를 재동기화
- [x] 125차 Jarvis v2 Approval Wording Guard로 approval/confirmation/verification wording이 execution approval로 승격되지 않게 고정
- [x] 126차 Jarvis v2 Evidence Packet Refresh로 actual verification results, disabled boundary, remaining Decision Required 증거 패킷을 갱신
- [x] 127차 Jarvis v2 Handoff Sync로 126차 evidence packet과 다음 검증 프롬프트를 handoff에 동기화
- [x] 128차 Jarvis v2 Release-lock Drift Guard로 121~127차 v2 safe guard 누적 경계와 stage/commit/push 미수행 상태를 재확인
- [x] 129차 Jarvis v2 Final Verification Sweep으로 121~128차 v2 safe guard 구간의 full verification과 release-lock boundary를 재확인
- [x] 130차 Jarvis v2 Commit Readiness Packet으로 121~129차 v2 safe guard 구간의 commit scope/message/push/PR Decision Required를 정리
- [x] 131차 Jarvis v2 Evidence Lock Refresh로 121~130차 v2 safe guard 구간의 evidence/release readiness 기준을 재확인
- [x] 132차 Jarvis v2 Release Readiness Drift Guard로 121~131차 v2 safe guard 구간의 release readiness 문구가 activation approval로 새지 않게 재확인
- [x] 133차 Jarvis v2 Public Release Evidence Refresh로 공개 릴리스 evidence 기준과 disabled boundary를 재확인
- [x] 134차 Jarvis v2 Disabled Boundary Evidence Guard로 disabled actual action boundary와 remaining Decision Required를 재확인
- [x] 135차 Jarvis v2 Remaining Decision Required Sync로 remaining Decision Required 항목과 handoff/public release evidence를 재동기화
- [x] 136차 Jarvis v2 Release Evidence Consistency Guard로 release evidence와 remaining Decision Required 문구의 정합성을 재확인
- [x] 137차 Jarvis v2 Pre-final Evidence Freeze로 141~150차 final decision 구간 전 evidence 기준을 동결
- [x] 138차 Jarvis v2 Final Decision Prep Boundary Guard로 final decision 준비 문구가 approval로 새지 않게 고정
- [x] 139차 Jarvis v2 Final Decision Readiness Matrix로 141~150차 final decision 구간 진입 전 readiness matrix를 고정
- [x] 140차 Jarvis v2 Pre-final Verification Refresh로 141~150차 final decision 구간 전 검증 기준을 재확인
- [x] 141차 Jarvis v2 Final Decision Entry Packet으로 141~150차 final decision 구간 진입 packet을 정리
- [x] 142차 Jarvis v2 Final Decision Approval Boundary Packet으로 final decision approval boundary를 정리
- [x] 143차 Jarvis v2 Final Decision Evidence Packet으로 final decision 구간 evidence packet을 정리
- [x] 144차 Jarvis v2 Final Decision Release Lock Packet으로 final decision release lock을 정리
- [x] 145차 Jarvis v2 Final Decision Commit Boundary Packet으로 final decision commit boundary를 정리
- [x] 146차 Jarvis v2 Final Decision Verification Packet으로 final decision verification 기준을 정리
- [x] 147차 Jarvis v2 Final Decision Status Freeze Packet으로 final decision status를 동결
- [x] 148차 Jarvis v2 Final Decision Closure Prep Packet으로 final decision closure prep을 정리
- [x] 149차 Jarvis v2 Final Decision Final Packet으로 final decision final packet을 정리
- [x] 150차 Jarvis v2 Final Handoff Packet으로 Jarvis v2 완성권 final handoff를 정리
- [x] 151차 Commit / Stage Final Decision Required Packet으로 final handoff 이후 commit/stage/push 승인 경계를 최종 Decision Required로 재고정
- [x] 152차 Post-151 Commit Decision Hold Guard로 151차 이후 사용자 승인 대기 상태를 유지
- [x] 153차 Explicit Approval Awaiting Packet으로 사용자 최종 승인 대기 상태를 명시적으로 유지
- [x] 154차 Git Action Still Blocked Verification Packet으로 git action still blocked 상태를 검증
- [x] 155차 Commit Scope Still Unresolved Packet으로 commit scope still unresolved 상태를 유지
- [x] 156차 Commit Message Still Unresolved Packet으로 commit message still unresolved 상태를 유지
- [x] 157차 Push PR Still Unresolved Packet으로 push/PR still unresolved 상태를 유지
- [x] 158차 Final Approval Required Hold Packet으로 final approval required hold 상태를 유지
- [x] 159차 Continue Instruction Is Not Git Approval Guard로 continue instruction이 git approval로 해석되지 않게 유지
- [x] 160차 Continue Still Not Git Approval Guard로 반복 continue instruction도 git approval로 해석되지 않게 유지
- [x] 사용자 최종 승인 후 commit scope, commit message, push/PR 여부를 결정하고 stage/commit/push 완료
- [x] 161차 Post-push Clean State Sync로 push 완료 후 clean 상태를 handoff/release summary에 반영
- [x] `/assistant/action-loop-preflight`가 frozen plan, wrapper, approval binding, payload hash gate만 반환하고 실제 action-loop dispatch를 하지 않는지 유지
- [x] 8차 이후 실제 action-loop 활성화 전 Decision Required 문서를 작성해 activation 조건, 금지 조건, P0/P1/P2, 회귀 테스트 요구사항을 고정
- [x] 9차 approval store를 in-memory preview store로 구현해 서버 발급 approval id, single-use, session/request context binding, payload_hash binding, TTL, injection 차단을 locked endpoint와 action-loop preflight 테스트로 고정
- [x] 10차 no-op dispatcher dry-run을 구현해 route plan과 noop audit만 반환하고 approval은 validate-only로 확인하며 실제 dispatch/shell/patch/browser 실행은 계속 차단
- [x] 11차 read-only dispatch boundary preview를 구현해 read-only adapter routing을 classification-only로 검토하고 실제 파일 읽기, 폴더 스캔, URL fetch, dispatch는 계속 차단
- [x] 12차 read-only adapter execution Decision Required와 preview-only policy matrix를 문서화해 실제 adapter 실행 전 승인 조건을 고정
- [x] 13차 read-only result wrapper schema를 preview-only 계약으로 고정해 raw content, approval-like JSON, next step mutation을 trusted result로 승격하지 않도록 테스트
- [x] 14차 read-only result wrapper schema를 UI bridge 예시와 assistant bridge smoke summary expected output에 반영해 safe-to-paste summary에서도 실행 flag false를 확인
- [x] 15차 NEXT_CHAT_HANDOFF와 Decision Required 문서를 9-14차 최신 locked/preview 계약, 검증 수치, Ready-to-send Next Prompt 기준으로 갱신
- [x] 16차 Claude/Sonnet review handoff와 FINAL_REPORT를 9-15차 최신 상태, Decision Required, Sonnet/Opus 역할 분리 기준으로 갱신
- [x] 17차 public docs link contract에 action-loop/read-only Decision Required 문서와 result wrapper schema 문서 링크 누락 방지 테스트 추가
- [x] 18차 NEXT_CHAT_HANDOFF를 9-17차 최신 상태, public docs Decision Required link contract, `621 passed, 1 warning` 기준으로 갱신
- [x] 18차 Browser Interaction Sandbox gate schema를 `browser-preview` 응답에 추가해 observe/read allowed candidate, click/fill/submit/login/payment/delete blocked, design-only domain allowlist, selector/input masking, approval injection 차단, no browser launch 계약을 테스트로 고정
- [x] 19차 External Web Search Provider Gate를 `web-search-provider-preview` 응답에 추가해 provider_not_configured, `external_api_enabled=false`, query masking, private/LAN/metadata URL block, untrusted result wrapper required, cost/rate limit docs, no external call 계약을 테스트로 고정
- [x] 33차 External Web Search Provider v1을 `web-search-provider/search` 응답에 추가해 `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, API key, rate limit, query safety, untrusted wrapper를 모두 통과한 단건 search만 수행하도록 고정
- [x] 20차 App/OS Interaction Gate를 `app-os-interaction-preview` 응답에 추가해 observe-plan candidate only, app open/click/type/hotkey/file dialog blocked, permission model, approval binding design, no OS action executed 계약을 테스트로 고정
- [x] 21차 Personal Workflow Presets를 workflow-presets list/detail/preview 응답에 추가해 `project_review`, `docs_check`, `ci_preview`, `patch_review`, `browser_review_plan` preset과 frozen `proposed_steps` only, params masking, unsafe preset block, no dispatch 계약을 테스트로 고정
- [x] 22차 Long-running Task Queue를 task-queue locked preview 응답에 추가해 queued/running/completed/blocked/cancelled status taxonomy, no-op/read-only task create/list/detail/cancel-preview, cancellation state, audit link, TTL cleanup policy, no worker loop 계약을 테스트로 고정
- [x] 23차 Failure Recovery / Rollback을 failure-recovery locked preview 응답에 추가해 failure reason taxonomy, patch rollback plan `original_sha256`, shell/browser manual instruction only, paste-safe summary, no automatic rollback 계약을 테스트로 고정
- [x] 24차 Production Hardening을 문서/테스트/API 계약 정리로 수행해 capabilities honesty, external API disabled, shell/patch/browser/action-loop/task-queue/rollback locked boundary, public release scanner clean, full pytest green 상태를 고정
- [x] 25차 Read-only Adapter Execution을 env opt-in으로 구현해 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`일 때만 file/list/safe URL adapter를 untrusted wrapper로 실제 read-only 실행하도록 고정
- [x] 26차 Read-only Action-loop Dispatch를 env opt-in으로 구현해 `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 read-only adapter flag가 모두 켜졌을 때만 read-only adapter를 호출하고 shell/patch/browser dispatch는 계속 차단
- [x] 19차 Codex implementation self-review와 9-18차 변경 파일/안전 경계 요약을 `docs/CODEX_IMPLEMENTATION_NOTES.md`에 정리
- [x] 20차 commit 전 최종 diff review와 변경 파일 그룹별 요약을 `docs/CODEX_IMPLEMENTATION_NOTES.md`에 추가

## 20차 자동화 로드맵 현재 상태

| 차수 | 이름 | 상태 | 다음 조건 |
|---|---|---|---|
| 1차 | 로컬 지식 API | `done` | 유지보수 |
| 2차 | Assistant UI/API bridge | `done` | 유지보수 |
| 3차 | 자동화 plan-only preflight | `done` | 유지보수 |
| 4차 | read-only 파일/폴더/URL preflight 자동화 | `done` | 유지보수 |
| 5차 | shell 실행 sandbox | `done` | 실제 실행은 계속 locked; 6차 file patch preview로 이동 |
| 6차 | file write/patch 자동화 | `done` | 실제 apply는 계속 locked; 7차 browser/app read-only preview로 이동 |
| 7차 | browser/app interaction 자동화 | `done` | 실제 interaction은 계속 locked; 8차 action-loop preflight로 이동 |
| 8차 | action loop 통합 개인 비서 | `done` | 실제 dispatch는 계속 disabled; 9차 approval store binding hardening으로 이동 |
| 9차 | approval store binding hardening | `done` | 실제 dispatch/shell/patch/browser 실행은 계속 disabled; 10차 no-op dispatcher dry-run 후보 |
| 10차 | no-op dispatcher dry-run | `done` | route plan/audit only; 실제 dispatch 또는 approval consume mode 전환은 별도 리뷰 필요 |
| 11차 | read-only dispatch boundary preview | `done` | classification-only; 실제 read-only adapter 실행도 별도 리뷰 필요 |
| 12차 | read-only adapter execution Decision Required | `done` | policy matrix only; 실제 read-only adapter execution은 사용자 승인/리뷰 필요 |
| 13차 | read-only result wrapper schema | `done` | preview-only schema; raw content/approval-like JSON/next step mutation은 trusted result로 승격 금지 |
| 14차 | UI/smoke wrapper schema expected output | `done` | UI bridge examples와 sanitized smoke summary에 wrapper schema safe flags 반영 |
| 15차 | handoff and Decision Required sync | `done` | NEXT_CHAT_HANDOFF, action-loop/read-only Decision docs가 9-14차 상태와 최신 검증 수치를 반영 |
| 16차 | Claude/Sonnet handoff and final report sync | `done` | Claude Sonnet 문서 리뷰와 Claude Opus 보안/아키텍처 escalation prompt를 분리하고 FINAL_REPORT가 Decision Required 상태를 반영 |
| 17차 | public docs Decision Required link contract | `done` | README/Project Summary/API 공개 문서에서 action-loop activation, read-only adapter execution, read-only result wrapper schema 링크 세트를 테스트로 고정 |
| 18차 | NEXT_CHAT_HANDOFF 17차 상태 sync / Browser Interaction Sandbox gate | `done` | handoff 제목, 상태표, Ready-to-send prompt가 9-17차 locked/preview와 public docs link contract를 반영하고, browser gate schema가 no-launch locked preview 계약을 고정 |
| 19차 | External Web Search Provider Gate / Codex implementation self-review | `done` | web search provider gate가 no external API call 계약을 고정하고, 9-18차 누적 변경 표면, locked flags, approval/result wrapper 경계, Decision Required, 검증 snapshot을 구현 노트로 고정 |
| 20차 | App/OS Interaction Gate / commit-ready diff review | `done` | app/os interaction gate가 no OS action executed 계약을 고정하고, 구현/API/CLI/docs/UI/tests 변경 파일 그룹, untracked 신규 문서, commit 전 검증 결과를 self-review 노트로 고정 |
| 21차 | Personal Workflow Presets | `done` | safe workflow template/preset list/detail/preview가 frozen proposed_steps만 생성하고 실제 dispatch/shell/patch/browser/external API 실행은 계속 비활성 |
| 22차 | Long-running Task Queue | `done` | task queue locked preview가 no-op/read-only task 상태와 cancellation state만 반환하고 실제 worker loop, daemon/service, shell/patch/browser 실행은 계속 비활성 |
| 23차 | Failure Recovery / Rollback | `done` | failure recovery preview가 rollback plan과 manual instruction만 반환하고 자동 rollback, git reset, file restore, shell/browser 실행은 계속 비활성 |
| 24차 | Production Hardening | `done` | capabilities honesty와 production safety boundary를 테스트/문서로 고정하고 운영 배포, 외부 API, 실제 실행 기능은 계속 비활성 |
| 25차 | Read-only Adapter Execution | `done` | env opt-in file/list/safe URL read-only adapter 실행. 기본값 disabled, wrapper required, sensitive/private 차단 |
| 26차 | Read-only Action-loop Dispatch | `done` | env opt-in read-only adapter dispatch만 허용. shell/patch/browser dispatch 미연결 |
| 27차 | Shell Sandbox v1 | `done` | 실제 subprocess를 처음 열되 기본값 disabled, allowlist 명령만, cwd allowlist, timeout, approval binding, stdout/stderr masking을 적용 |
| 28차 | Shell Action-loop Integration | `done` | action-loop가 27차 shell allowlist task만 호출. arbitrary shell, pipe/redirect/chaining, install/delete/network command는 계속 blocked |
| 29차 | Patch Apply Sandbox v1 | `done` | env opt-in 승인된 단일 파일 patch apply. original_sha256 precondition, rollback note, path allowlist, secret scan 필수 |
| 30차 | Patch Action-loop Integration | `done` | action-loop가 29차 승인 단일 파일 patch task만 호출. bulk apply, delete, workspace 밖 write는 blocked |
| 31차 | Browser Observe v1 | `done` | env opt-in read-only metadata observe only. click/fill/submit/login/payment/delete는 계속 blocked |
| 32차 | Browser Limited Interaction v1 | `done` | env opt-in candidate validation only. 실제 browser launch/click/fill, login/payment/delete/credential input은 blocked |
| 33차 | External Web Search Provider v1 | `done` | env opt-in `brave` 단건 search only. private/LAN/metadata URL, secret query, unsupported provider는 blocked |
| 34차 | Task Queue Worker v1 | `done` | env opt-in one-shot drain only. `noop`, `read_only_scan`, `file_preview` task만 처리하고 daemon/service/background loop, shell/browser/external API/rollback/app-os task는 미연결 |
| 35차 | Rollback Executor Boundary | `done` | env opt-in single-file restore only. rollback 전용 approval/hash/precondition 필수, git reset/bulk restore/shell/browser/external API/task-worker/app-os/action-loop full dispatch는 미연결 |
| 36차 | Full Personal Automation Boundary | `done` | full automation preflight/dispatch gate only. 기본 disabled, approval validate-only, shell/patch/read-only/rollback/task/browser/external/app-os connector 실행 미연결 |
| 37차 | Full Automation Orchestrator No-op Aggregation | `done` | flag true에서도 connector 실행 없이 ordered route plan, dependency graph, failure/rollback strategy, per-step no-op wrapper만 집계. approval consume 미연결 |
| 38차 | Full Automation Read-only Connector Integration | `done` | full automation dispatch에서 read-only category step만 기존 read-only adapter gate로 실행. shell/patch/rollback/task/browser/external/app-os와 approval consume은 미연결 |
| 39차 | Full Automation Shell Connector Candidate | `done` | full automation dispatch에서 shell category step만 기존 allowlist shell sandbox로 실행. patch/rollback/task/browser/external/app-os는 미연결 |
| 40차 | Full Automation Patch Connector Candidate | `done` | full automation dispatch에서 patch category step만 기존 single-file patch boundary로 실행. rollback/task/browser/external/app-os는 미연결 |
| 41차 | Full Automation Rollback Connector Candidate | `done` | full automation dispatch에서 rollback category step만 기존 single-file rollback boundary로 실행. task/browser/external/app-os는 미연결 |
| 42차 | Full Automation Task Queue Connector Candidate | `done` | full automation dispatch에서 `noop`, `read_only_scan`, `file_preview` task_queue step만 기존 one-shot worker boundary로 실행. browser/external/app-os는 미연결 |
| 43차 | Full Automation Browser Observe Connector Candidate | `done` | full automation dispatch에서 browser_observe category step만 기존 read-only metadata/title/current URL boundary로 실행. browser actual interaction/external/app-os는 미연결 |
| 44차 | Full Automation Browser Limited Candidate Validation | `done` | full automation dispatch에서 browser_limited_interaction category step만 기존 candidate validation boundary로 실행. `would_interact=false`, browser actual interaction/external/app-os는 미연결 |
| 45차 | Full Automation External Web Search Connector Candidate | `done` | full automation dispatch에서 external_web_search category step만 기존 `brave` provider boundary로 실행. arbitrary provider/external LLM/app-os는 미연결 |
| 46차 | Full Automation App-OS Preview Connector Candidate | `done` | full automation dispatch에서 app_os category step만 기존 app-os interaction preview boundary로 처리. observe-plan candidate wrapper only, 실제 OS action은 미연결 |
| 47차 | Full Automation Policy/Audit Hardening | `done` | full automation dispatch의 gates/audit/safety matrix를 실제 연결 범위와 일치하도록 고정. browser actual/app-os actual/action-loop full dispatch는 미연결 |
| 48차 | Full Automation Action-loop Dispatch Decision Required | `done` | 실제 action-loop full dispatch는 계속 금지. connector별 approval consume, rollback/failure strategy, 사용자 최종 승인, Opus 리뷰 조건을 Decision Required 문서와 public docs contract로 고정 |
| 49차 | Full Automation Contract Review / Runtime Drift Guard | `done` | runtime gates/audit/safety와 public docs locked flag 문구가 함께 유지되는지 테스트로 고정. 실제 action-loop full dispatch는 미연결 |
| 50차 | Full Automation Commit-readiness / Cumulative Diff Review | `done` | 누적 diff를 runtime/API/schema/service/CLI/scripts/tests/docs 그룹으로 정리하고 untracked docs 5개 의도성과 최신 검증 수치를 implementation notes에 고정 |
| 51차 | Full Automation Final Docs Sync / Handoff Freeze | `done` | public docs와 handoff/review docs의 최신 검증 수치, 50차 commit-readiness, actual action 미연결 범위를 최종 동기화 |
| 52차 | Final Verification Sweep / Commit Decision Required | `done` | 최종 local CI/public release/git diff/status sweep와 commit 전 Decision Required를 고정. staging/commit/push는 사용자 명시 요청 전 수행하지 않음 |
| 53차 | Commit / Stage Decision Required | `done` | commit/stage decision packet 고정. modified tracked files 40개, untracked docs 5개, staging/commit/push 미수행, 사용자 commit 범위/message/push 여부 명시 필요 |
| 54차 | Automation Roadmap / Release Lock | `done` | 54~90차 roadmap을 safe-next/review-required/blocked 경계로 재정렬. release lock과 roadmap boundary contract 고정 |
| 55차 | Approval Consume Strategy Review | `done` | connector별 approval consume mode와 61~70차 진입 전 failure/rollback/audit/wrapper checklist를 고정. actual action-loop full dispatch는 미연결 |
| 56차 | Failure Strategy Matrix | `done` | connector별 failure/timeout/blocked summary, rollback 가능/불가능 조건, paste-safe audit summary를 고정. actual action-loop full dispatch는 미연결 |
| 57차 | Audit Payload Schema Lock | `done` | connector별 audit payload schema, masked field policy, wrapper trust indicators를 고정. actual action-loop full dispatch는 미연결 |
| 58차 | Connector Dry-run Replay Contract | `done` | connector별 dry-run replay input/output, replay audit consistency, masked replay summary를 고정. actual action-loop full dispatch는 미연결 |
| 59차 | Release Lock Diff Inventory | `done` | 54~58차 release-lock 누적 diff group, modified tracked files 40개, untracked docs 5개, commit-before checklist를 고정. actual action-loop full dispatch는 미연결 |
| 60차 | Release Lock Final Verification / Stage Decision Required | `done` | 54~60차 release-lock 최종 검증, modified tracked files 40개, untracked docs 5개, stage/commit Decision Required를 고정. actual action-loop full dispatch는 미연결 |
| 61차 | Local Jarvis v1 Candidate Decision Required | `done` | action-loop full dispatch, limited browser actual interaction, limited app-os actual action 후보를 Decision Required로 분리. actual action-loop full dispatch는 미연결 |
| 62차 | Local Jarvis Approval Gate Review | `done` | approval consume transition table, user final approval wording, Opus review prompt, disabled defaults, kill-switch checklist를 고정. actual action-loop full dispatch는 미연결 |
| 63차 | Local Jarvis Runtime Drift Guard | `done` | runtime/docs/test drift guard, public docs link contract, actual action false assertions를 고정. actual action-loop full dispatch는 미연결 |
| 64차 | Local Jarvis Failure/Timeout Drill | `done` | failure/timeout/manual-review-required summary, paste-safe audit summary, emergency stop drill을 고정. actual action-loop full dispatch는 미연결 |
| 65차 | Local Jarvis Manual Review Packet | `done` | manual review packet, P0/P1/P2 checklist, approval wording diff, Opus review handoff를 고정. actual action-loop full dispatch는 미연결 |
| 66차 | Local Jarvis Approval Console State-only Review | `done` | approval console/pending/detail/approve/reject는 state-only. no execution on approve, actual action-loop full dispatch는 미연결 |
| 67차 | Local Jarvis Approval Payload Hash Review | `done` | approval payload_hash/session/single-use/TTL 경계가 approval console state와 섞이지 않는지 문서/테스트로 고정 |
| 68차 | Local Jarvis Approval Store Expiry Cleanup Review | `done` | approval store pending/list/detail cleanup, expired approval visibility, paste-safe expired summary를 문서/테스트로 고정 |
| 69차 | Local Jarvis Approval Console API Surface Decision Required | `done` | approval console API surface를 endpoint로 열지 여부와 인증/권한/감사/마스킹/TTL cleanup 노출 범위를 Decision Required로 고정 |
| 70차 | Local Jarvis Approval Console Read-only API Candidate | `done` | 실제 실행 없이 read-only pending/list/detail/cleanup endpoint만 protected/masked API로 추가. approve/reject state transition은 계속 review-required |
| 71차 | Durable Automation v2 Candidate Decision Required | `done` | daemon/service/background loop 없이 durable automation v2 후보 조건, persistence/recovery/replay boundary, approval/audit lock을 문서/테스트로 고정 |
| 72차 | Durable State Preview Schema Candidate | `done` | 실제 durable worker/storage migration 없이 durable state preview schema/proposal-only contract를 문서/테스트로 고정 |
| 73차 | Durable State Preview API Surface Decision Required | `done` | 실제 endpoint 노출 없이 durable state preview API surface 후보와 route absence를 Decision Required로 고정 |
| 74차 | Durable State Preview Read-only API Candidate | `done` | 실제 persistence/worker/scheduler 없이 `POST /assistant/durable-state-preview/preview`만 response-only/read-only/schema-only endpoint로 추가 |
| 75차 | Durable State Preview API Regression Guard | `done` | route inventory, nested sensitive key redaction, absent stored preview routes, no persistence mutation, no approval consume, no queue mutation을 회귀 테스트로 고정 |
| 76차 | Durable State Preview Docs/API Drift Guard | `done` | API docs response fields, public docs endpoint listing, security boundary, release summary, handoff 문구를 runtime contract와 동기화 |
| 77차 | Durable State Preview Release-lock Guard | `done` | 74~76차 durable-state-preview 누적 diff, 검증 수치, modified tracked files 40개, untracked docs 11개, staging/commit/push 미수행을 release-lock으로 고정 |
| 91차 | Commit / Stage Decision Required | `done` | 1~90차 누적 diff의 commit scope, commit message, push/PR 여부는 사용자 최종 승인 필요. stage/commit/push는 수행하지 않았다 |
| 92차 | Commit Approval or Jarvis v1 Safe Planning | `done` | "멈추지 말고 해줘"는 git 작업 명시 승인으로 해석하지 않는다. commit approval flow는 사용자 명시 승인 전 blocked. Jarvis v1 Safe Planning은 actual action 없이 docs/test/review-required 중심으로 진행 |
| 93차 | Jarvis v1 Safe Roadmap Drift Guard | `done` | 93~120차 Jarvis v1 실사용형 구간이 safe-next/review-required/blocked 경계를 유지하고 actual action으로 새지 않게 문서/테스트로 고정 |
| 94차 | Jarvis v1 Capability Honesty Guard | `done` | Jarvis v1 문서의 capability wording이 실제 열린 기능, env opt-in 기능, blocked 기능을 정확히 구분하고 actual action을 과장하지 않게 고정 |
| 95차 | Jarvis v1 Manual UX Contract Guard | `done` | 수동 UX, approval wording, blocked state 표시가 실제 runtime boundary와 일치하고 실행 승인으로 오해되지 않게 고정 |
| 96차 | Jarvis v1 Evidence Packet Guard | `done` | 증거 패킷이 actual verification results, disabled boundary, remaining Decision Required를 함께 포함하고 실행하지 않은 action을 완료처럼 표현하지 않게 고정 |
| 97차 | Jarvis v1 Decision Required Packet Guard | `done` | commit/browser/app-os/action-loop/durable activation Decision Required 항목이 증거 패킷과 handoff에 같이 남고 approval/review 필요 항목이 safe-next로 오분류되지 않게 고정 |
| 98차 | Jarvis v1 Approval Wording Drift Guard | `done` | approval wording이 실행 승인, 상태 변경, 검증 완료, Decision Required를 혼동하지 않고 approval/confirmation 상태가 execution approval로 승격되지 않게 고정 |
| 99차 | Jarvis v1 Release-lock Drift Guard | `done` | 92~98차 Jarvis v1 safe guard 누적 경계, actual action 비활성, stage/commit/push 미수행 상태를 release-lock으로 고정 |
| 100차 | Jarvis v1 Final Verification Sweep | `done` | 92~99차 Jarvis v1 safe guard 구간의 full pytest, compileall, public release check, git diff check, local CI, git status를 다시 확인하고 검증 수치를 고정 |
| 101차 | Jarvis v1 Commit Readiness Packet | `done` | 92~100차 Jarvis v1 safe guard 구간의 commit scope/message/push 여부 Decision Required와 사용자 최종 승인 필요 상태를 고정 |
| 102차 | Jarvis v1 Handoff Freeze | `done` | 92~101차 Jarvis v1 safe guard 구간의 다음 handoff와 검증 프롬프트를 동결 |
| 103차 | Jarvis v1 Release Candidate Prep | `done` | 92~102차 Jarvis v1 safe guard 구간의 release candidate readiness와 남은 Decision Required를 정리 |
| 104차 | Jarvis v1 Final RC Verification | `done` | 92~103차 Jarvis v1 safe guard 구간의 full verification과 RC boundary를 재확인 |
| 105차 | Jarvis v1 Final Stage Decision Packet | `done` | Jarvis v1 RC 구간의 stage/commit/push 최종 Decision Required를 정리 |
| 106차 | Jarvis v1 Public Release Guard | `done` | public release scanner와 공개 문서의 Jarvis v1 안전 경계를 재확인 |
| 107차 | Jarvis v1 Evidence Freeze | `done` | Jarvis v1 RC 증거 패킷과 검증 수치를 동결 |
| 108차 | Jarvis v1 Release Lock Refresh | `done` | 92~107차 Jarvis v1 RC 구간의 release lock과 남은 Decision Required를 갱신 |
| 109차 | Jarvis v1 Final Handoff Refresh | `done` | 108차 release lock 결과와 110차 다음 작업 프롬프트를 동결 |
| 110차 | Jarvis v1 Verification Refresh | `done` | Jarvis v1 RC 구간의 최신 검증 수치와 public release scanner 기준을 재확인 |
| 111차 | Jarvis v1 Commit Boundary Refresh | `done` | commit scope/message/push/PR 사용자 최종 승인 경계를 재확인 |
| 112차 | Jarvis v1 Final Verification Packet | `done` | Jarvis v1 RC 구간의 최종 검증 packet과 남은 Decision Required를 정리 |
| 113차 | Jarvis v1 Release Readiness Closure | `done` | Jarvis v1 RC 구간의 release readiness와 commit 전 닫힘 상태를 정리 |
| 114차 | Jarvis v1 Commit Approval Decision Packet | `done` | commit approval 전 사용자 최종 승인 필요 항목을 다시 정리 |
| 115차 | Jarvis v1 Pre-120 Remaining Scope Plan | `done` | 120차까지 남은 safe-next 범위를 정리 |
| 116차 | Jarvis v1 Pre-120 Verification Matrix | `done` | 남은 safe-next 검증 matrix를 고정 |
| 117차 | Jarvis v1 Pre-120 Handoff Sync | `done` | 118차 다음 handoff와 검증 프롬프트를 동기화 |
| 118차 | Jarvis v1 Pre-120 Final Evidence Refresh | `done` | 120차 직전 evidence 기준을 재확인 |
| 119차 | Jarvis v1 Readiness Freeze | `safe-next` | 120차 직전 readiness 상태를 동결 |

## 27~68차 실행 활성화 로드맵 해석

- 최소 개발 보조 자동화는 28차까지다. read-only action-loop와 safe shell allowlist 실행이 가능해진다.
- 코드 수정 자동화 MVP는 30차까지다. 승인된 단일 파일 patch apply와 action-loop patch 호출이 가능해진다.
- 브라우저 관찰/수동 QA 보조는 31차까지다. 실제 observe/screenshot까지만 가능하다.
- 제한적 브라우저 interaction은 32차부터지만 login/payment/delete/credential 입력은 계속 금지한다.
- 외부 검색을 포함한 개인 API 자동화는 33차 이후다. API key, 비용, rate limit, private URL 차단 계약이 먼저 필요하다.
- 백그라운드 작업 큐는 34차에서 one-shot drain까지만 열렸다. worker가 shell/patch/browser/external API/rollback/app-os를 임의 실행하면 안 된다.
- 거의 완전한 로컬 개인 자동화는 73차에서 통합 preflight, no-op orchestration aggregation, read-only connector integration, allowlist shell connector integration, single-file patch connector integration, single-file rollback connector integration, read-only task queue connector integration, browser observe metadata connector integration, browser limited candidate validation integration, external web search provider connector integration, app-os observe-plan preview integration, policy/audit matrix hardening, Full Automation Action-loop Dispatch Decision Required, runtime/docs drift guard, commit-readiness cumulative diff review, final docs sync/handoff freeze, final verification sweep, commit/stage decision packet, automation roadmap/release lock, approval consume strategy review, failure strategy matrix, audit payload schema lock, connector dry-run replay contract, release lock diff inventory, release lock final verification, Local Jarvis v1 Candidate Decision Required, Local Jarvis Approval Gate Review, Local Jarvis Runtime Drift Guard, Local Jarvis Failure/Timeout Drill, Local Jarvis Manual Review Packet, Local Jarvis Approval Console State-only Review, Local Jarvis Approval Payload Hash Review, Local Jarvis Approval Store Expiry Cleanup Review, Local Jarvis Approval Console API Surface Decision Required, Local Jarvis Approval Console Read-only API Candidate, Durable Automation v2 Candidate Decision Required, Durable State Preview Schema Candidate, Durable State Preview API Surface Decision Required까지 도달했다. 54~60차 Release Lock / Approval Strategy는 safe-next 구간으로 완료했고, 61~70차 Local Jarvis v1 Candidate는 review-required 중심으로 완료했다. 71~80차 Durable Automation v2 Candidate는 review-required/blocked 중심으로 진행 중이며 81~90차 Personal Automation Hardening Candidate도 review-required/blocked 중심으로 진행한다. 실제 action-loop full dispatch, browser click/fill/submit, app-os multi-tool dispatch는 사용자 최종 승인과 Opus 리뷰 전 열지 않는다. staging/commit/push는 사용자 명시 요청 전 수행하지 않는다. 90차까지 이어갈 때도 각 차수 끝에 Recommended Next Model 섹션을 유지한다.

## 사용자 수동 확인 작업

- [x] GitHub repository description과 topics를 `docs/CODEX_FOR_OSS_APPLICATION.md` 기준으로 설정
- [ ] GitHub profile bio를 직접 설정
- [ ] OpenAI Platform에서 Organization ID를 직접 확인해 공식 Codex for Open Source form에 입력
- [ ] 공식 form 제출은 사용자가 로그인된 브라우저에서 직접 진행
- [ ] 로컬 서버 실행 후 `GET /assistant/startup`이 실제 브라우저 UI 첫 화면에 올바르게 표시되는지 확인
- [ ] `GET /assistant/ui-contract`의 startup sequence, refresh endpoint, response type, blocked action 표시 확인
- [ ] `POST /assistant/bootstrap`의 project root, session, UI hint 표시 확인
- [ ] `POST /assistant/action-preview`의 intent, risk level, missing input 표시 확인
- [ ] `POST /assistant/message` 실제 메시지 응답이 `ui.response_type` 기준으로 렌더링되는지 확인
- [ ] `GET /assistant/sessions`와 `GET /assistant/sessions/{session_id}/messages` paging 표시 확인

## 별도 승인 또는 보안 리뷰가 필요한 작업

- [ ] 실제 repair/delete/rebuild 실행 명령
- [ ] arbitrary shell 실행
- [x] shell sandbox locked-run을 27차 allowlist subprocess 실행으로 제한 연결
- [ ] 파일 생성, 수정, 삭제 자동화
- [x] patch sandbox locked-apply를 env opt-in 기존 UTF-8 단일 파일 write로 연결
- [ ] 브라우저 click/fill/submit/login 자동화
- [x] browser observe를 env opt-in read-only metadata observe로 제한 연결
- [x] browser limited interaction을 env opt-in candidate validation으로 제한 연결. 실제 browser launch/click/fill은 미연결
- [ ] action-loop dispatch 실제 활성화
- [ ] full automation action-loop full dispatch 실제 활성화
- [ ] approval store를 실제 실행 승인으로 사용하는 단계 전환
- [ ] no-op dispatcher를 실제 dispatch boundary로 전환
- [ ] read-only boundary preview를 실제 read-only adapter 실행으로 전환
- [x] long-running task queue를 env opt-in one-shot drain으로 제한 연결
- [ ] long-running task queue를 실제 background worker loop 또는 daemon/service로 전환
- [x] failure recovery preview와 분리된 rollback executor를 env opt-in 단일 파일 restore로 제한 연결
- [ ] failure recovery를 git reset/file restore/bulk restore/shell/browser 복구 실행으로 전환
- [ ] durable approval table 또는 multi-process approval 공유 구조 도입
- [ ] JavaScript 렌더링/외부 URL 크롤링
- [ ] pdf2image/poppler 기반 page rendering OCR 확장
- [ ] Docker sandbox, cloud/local runner bridge, 서비스화 구조 변경
- [ ] 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit
- [ ] Oracle Cloud, Oracle DB, Oracle Object Storage, Oracle VM/Compute 리소스 생성/변경

## Stop Conditions

아래 상황이 필요해지면 Codex는 구현을 멈추고 `Decision Required` 또는 Claude Opus 보안/아키텍처 리뷰로 넘긴다.

- 외부 GPT API, Claude API, Gemini API 또는 외부 embedding API 활성화
- OpenAI/Claude/Gemini API key, DB password, Oracle credential 출력 또는 저장
- arbitrary shell 실행, allowlist 밖 shell dispatch, bulk patch apply, file create/delete 자동화
- 브라우저 interaction 자동화
- long-running background worker, daemon/service, queue auto-run 활성화
- 자동 rollback, git reset, file restore, shell/browser 기반 복구 실행
- 운영 배포 또는 클라우드/Oracle 리소스 변경
- 비용, 보안, 운영 데이터, workspace 밖 접근에 영향이 있는 작업

## 검증 명령

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
```

한 번에 실행하려면:

```bash
.venv/bin/python scripts/local_ci_check.py --root .
```
