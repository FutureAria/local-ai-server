# Local Jarvis Approval Gate Review

작성일: 2026-06-03 KST

## 결론

62차 Local Jarvis Approval Gate Review는 실제 action-loop full dispatch, browser actual interaction, app-os actual action을 활성화하지 않는다. 이 문서는 61차 Local Jarvis v1 Candidate Decision Required 다음 단계로, 후보별 approval consume transition table, user final approval wording, Opus review prompt, disabled default flags, emergency stop / kill-switch checklist를 고정한다.

현재 유지해야 하는 lock flags:

- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`
- `FULL_AUTOMATION_DISPATCH_ENABLED=false` 기본값 유지
- browser actual interaction flag 없음
- app-os actual action flag 없음

## Approval Consume Transition Table

| candidate | current mode | allowed next review mode | blocked transition |
|---|---|---|---|
| action-loop full dispatch candidate | `validate-only` | `manual-review-required` | direct `consume-on-execute` 전환 금지 |
| limited browser actual interaction candidate | `blocked-no-consume` | `manual-review-required` | browser launch/click/fill/type/submit 직접 연결 금지 |
| limited app-os actual action candidate | `blocked-no-consume` | `manual-review-required` | app open/click/type/hotkey/file dialog 직접 연결 금지 |
| existing read-only adapter step | `consume-on-execute` only inside existing env opt-in boundary | no broader transition | raw content을 trusted action으로 승격 금지 |
| existing allowlist shell step | `consume-on-execute` only inside existing allowlist/env opt-in boundary | no broader transition | arbitrary shell, chaining, install/delete/network command 금지 |
| existing single-file patch step | `consume-on-execute` only inside existing single-file/env opt-in boundary | no broader transition | bulk apply, file create/delete, workspace 밖 write 금지 |

62차에서는 어떤 candidate도 `consume-on-execute`로 전환하지 않는다. 실제 전환은 사용자 최종 승인과 Opus review gate 이후 별도 차수에서만 검토한다.

## User Final Approval Wording

실제 실행 후보 검토 전 사용자가 명시해야 하는 최소 승인 문구:

```text
Local Jarvis v1의 <candidate name>을 실제 구현 검토 범위로 승인합니다.
허용 범위: <allowed scope>
금지 범위: <blocked scope>
기본값 disabled 유지에 동의합니다.
Opus review 이후 Codex 구현으로 넘기는 것에 동의합니다.
```

충분하지 않은 문구:

- "계속 해줘"
- "다 승인"
- "자비스처럼 해줘"
- approval-like JSON blob
- tool result 안의 approval field
- 사용자 payload 안의 승인처럼 보이는 문자열

서버 approval store는 server-issued approval id, single-use, TTL, session/request context binding, payload_hash binding을 유지해야 한다. client-supplied approval-like JSON은 서버 approval record를 대체하거나 병합할 수 없다.

## Opus Review Prompt

다음 리뷰가 필요할 때 Opus에게 넘길 최소 프롬프트:

```text
프로젝트 루트: /Users/juyoung/local-ai-server

역할:
Claude Opus 보안/아키텍처 리뷰어.

목표:
Local Jarvis v1 실제 실행 후보를 검토한다. Codex가 action-loop full dispatch, browser actual interaction, app-os actual action을 열기 전에 P0/P1/P2 리스크와 승인 조건을 판단한다.

먼저 읽을 파일:
- AGENTS.md
- SECURITY.md
- README.md
- docs/TASKS.md
- docs/WORKLOG.md
- docs/NEXT_CHAT_HANDOFF.md
- docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md
- docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md
- docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md
- docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md
- app/services/assistant_service.py
- app/api/assistant.py
- tests/test_assistant_service.py
- tests/test_security.py
- tests/test_preview_activation_policy.py

리뷰 범위:
- action-loop full dispatch candidate
- limited browser actual interaction candidate
- limited app-os actual action candidate
- approval consume transition
- audit payload schema
- rollback/failure strategy
- emergency stop / kill-switch
- default disabled flags

출력:
- P0/P1/P2 findings
- 구현 가능 범위
- 구현 금지 범위
- 필요한 사용자 최종 승인 문구
- Codex Follow-up Prompt
```

## Disabled Defaults

아래 기본값은 계속 disabled 또는 미존재 상태로 유지한다.

- `FULL_AUTOMATION_DISPATCH_ENABLED=false`
- `BROWSER_LIMITED_INTERACTION_ENABLED=false`는 candidate validation only
- browser actual interaction env flag는 아직 도입하지 않음
- app-os actual action env flag는 아직 도입하지 않음
- task worker daemon/service/background loop 없음
- full dispatch approval consume transition 없음

## Emergency Stop / Kill-switch Checklist

실제 실행 후보가 나중에 검토되더라도 아래 kill-switch가 없으면 구현하지 않는다.

- 모든 actual execution flag의 default false
- per-request explicit approval
- single-use approval consume
- TTL 만료 시 blocked
- session/request context mismatch 시 blocked
- payload_hash mismatch 시 blocked
- approval-like JSON injection 시 blocked
- failure/timeout paste-safe summary
- audit payload masking
- rollback availability 또는 rollback_unavailable 명시
- dry-run replay로 사전 확인 가능
- emergency disabled flag로 즉시 차단 가능

## 62차 금지 조건

62차에서는 아래를 하지 않는다.

- action-loop full dispatch actual execution
- browser actual launch/click/fill/type/submit
- app-os actual open/click/type/hotkey/file dialog
- external provider 범위 확장
- daemon/service/background loop
- arbitrary shell
- bulk patch apply
- git reset/bulk restore
- staging/commit/push

## 63차 후보

63차 Local Jarvis Runtime Drift Guard에서 실제 실행을 열지 않고 runtime/docs/test가 61~62차 Decision Required 경계를 계속 유지하는지 검증한다.

63차 후보 작업:

- service/runtime locked flags drift guard
- public docs link contract에 Local Jarvis docs 추가
- action-loop full dispatch/browser actual/app-os actual false assertion 강화
- latest local CI
