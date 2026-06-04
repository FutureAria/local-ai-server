# Action Loop Activation Decision Required

작성일: 2026-06-02 KST

이 문서는 8차 action-loop dispatch preflight 이후 실제 개인 API 자동화를 활성화하기 전에 필요한 보안 판단을 정리한다. 26차에서 env opt-in read-only action-loop dispatch를 추가했고, 27차에서 env opt-in allowlist shell subprocess를 단독 endpoint에 제한 연결했으며, 28차에서 env opt-in shell action-loop dispatch를 27차 allowlist shell step에만 제한 연결했다. 48차 Full Automation Action-loop Dispatch Decision Required에서는 full automation의 실제 action-loop full dispatch를 열지 않고 사용자 최종 승인, Opus 리뷰, connector별 approval consume, rollback/failure strategy 조건을 문서/테스트로 고정했다. patch apply는 29~30차 단일 파일 env opt-in 범위만, browser/app interaction은 observe/candidate preview 범위만 유지하고 외부 LLM/API 호출은 활성화하지 않는다.

## 현재 안전 상태

- 1차부터 8차까지의 구현은 로컬 백엔드 API와 CLI 계약, read-only preview, locked preview, preflight 검증 중심이다.
- `/assistant/action-loop-preflight`는 frozen plan, wrapper, approval binding, payload hash, unsafe action gate를 검사하지만 실제 action dispatch를 수행하지 않는다.
- shell 후보 step은 28차 env opt-in에서만 27차 allowlist subprocess를 호출할 수 있다. patch, browser/app 후보 step은 각각 기존 preview 계약을 요약할 뿐 action-loop 안에서 파일 쓰기/삭제, 브라우저 조작을 하지 않는다.
- preflight/no-op/boundary preview 응답은 `would_dispatch=false`, `execution_enabled=false`를 유지한다. 26차 `/assistant/action-loop-read-only-dispatch`만 별도 env opt-in에서 read-only adapter를 호출한다.
- 48차 기준 full automation action-loop full dispatch는 실제로 연결하지 않는다. `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`는 사용자 최종 승인과 Opus 리뷰 전까지 유지한다.
- 외부 GPT API, Claude API, Gemini API, 외부 embedding API, cloud vector DB는 활성화하지 않는다.

## 이미 구현된 안전 계약

| 영역 | 현재 계약 | 활성화 상태 |
|---|---|---|
| Read-only scan/file/url/workspace | 허용 root, secret file block, masking, preview-only | read-only preview |
| Shell sandbox | allowlist, cwd 제한, timeout contract, output masking, audit payload | 27차 단독 endpoint env opt-in allowlist subprocess, 28차 action-loop allowlist shell dispatch env opt-in |
| Patch sandbox | diff preview, path allowlist, credential path block, payload hash, rollback note | locked, no apply |
| Browser/app | action taxonomy, unsafe action block, target/input masking, approval preview, gate schema | locked, no interaction, no browser launch |
| External web search provider | provider config contract, query masking, private/LAN/metadata URL block, untrusted result wrapper, cost/rate limit docs | locked, no external API call |
| App/OS interaction | observe-plan candidate, blocked action taxonomy, permission model, approval binding design, masked audit | locked, no app/OS control |
| Workflow presets | safe template list/detail, frozen proposed_steps, unsafe preset block, params masking | preview only, no dispatch |
| Long-running task queue | task status taxonomy, no-op/read-only task preview, cancellation state, audit link, TTL cleanup policy | locked preview only, no worker loop |
| Failure recovery / rollback | failure reason taxonomy, patch rollback plan, shell/browser manual instructions, paste-safe summary | locked preview only, no automatic rollback |
| Action-loop preflight | frozen plan, wrapper gate, approval binding gate, payload hash gate | preflight only, no dispatch |
| Full automation action-loop dispatch | Full Automation Action-loop Dispatch Decision Required, connector approval consume matrix, rollback/failure strategy | blocked, no action-loop full dispatch |

## 활성화 전 필수 결정

### P0: 활성화 전 반드시 결정

- 단일 dispatch feedback boundary를 정의한다. 모든 tool result가 LLM context 또는 다음 step 판단으로 들어가기 전에 같은 wrapper/masking boundary를 통과해야 한다.
- wrapper enforcement 위치를 확정한다. wrapper가 누락되거나 `untrusted` 표시가 없으면 fail closed 해야 한다.
- frozen plan 불변성을 유지한다. tool result의 텍스트가 다음 URL, shell command, patch path, browser action, approval payload, plan step을 결정하거나 수정하면 안 된다.
- approval binding 저장/검증 방식을 확정한다. session ownership, approval id, payload hash, expiry, single-use 성격을 명확히 해야 한다.
- 9차 preview approval store는 process-local in-memory로 구현되어 있다. 서버 발급 approval id, single-use, session/request context binding, payload_hash binding, TTL, unknown/expired/used/mismatch 차단을 locked endpoint와 action-loop preflight 테스트로 고정했다.
- preview approval store 검증 성공은 patch/browser 실행 승인이 아니다. `/assistant/browser-interact`는 approval을 소비해도 locked 응답만 반환하고 `execution_enabled=false`를 유지한다. `/assistant/shell-run`은 27차 env opt-in 조건에서만 단건 allowlist subprocess로 제한되고, `/assistant/patch-apply`는 29차 env opt-in 조건에서만 단일 파일 patch apply로 제한된다. `/assistant/browser-observe`는 31차 env opt-in 조건에서만 loopback/명시 allowlist URL read-only metadata observe로 제한되며 action-loop browser dispatch에는 연결되지 않는다. `/assistant/browser-limited-interact`는 32차 env opt-in 조건에서도 candidate validation만 수행하고 실제 browser launch/click/fill 또는 action-loop browser dispatch에는 연결되지 않는다. `/assistant/web-search-provider/search`는 33차 env opt-in 조건에서만 `brave` 단건 search를 수행하며 action-loop external dispatch에는 연결되지 않는다.
- 10차 no-op dispatcher는 route plan과 noop audit만 반환하도록 구현되어 있다. `approval_consume_mode=validate-only`이며 실제 dispatch, shell 실행, patch apply, browser/app interaction은 연결하지 않았다.
- 11차 read-only dispatch boundary preview는 read-only adapter routing을 classification-only로 검토하도록 구현되어 있다. 파일 내용 읽기, 폴더 스캔, URL fetch, 실제 dispatch는 연결하지 않았다.
- 13차 read-only result wrapper schema는 `assistant.action_loop.read_only_result_wrapper.v1`로 고정되어 있다. raw content, approval-like JSON, next step, shell command, patch payload, browser action은 trusted result로 승격할 수 없다.
- 14차 assistant bridge smoke summary는 `assistant-read-only-result-wrapper` step에서 wrapper schema safe flag만 확인한다. 이 smoke step도 실제 파일 읽기, URL fetch, dispatch를 수행하지 않는다.
- 18차 Browser Interaction Sandbox gate는 `assistant.browser_interaction.gate.v1`로 observe/read allowed candidate, click/fill/submit/login/payment/delete blocked execution, design-only domain allowlist, selector/input masking, approval injection 차단, no browser launch를 고정한다.
- 19차 External Web Search Provider Gate는 `assistant.web_search.provider_gate.v1`로 provider_not_configured, `external_api_enabled=false`, query masking, private/LAN/metadata URL 차단, untrusted result wrapper required, cost/rate limit 후보 문서화를 고정한다. 실제 외부 검색 API 호출, API key 추가, paid provider 활성화는 연결하지 않았다.
- 20차 App/OS Interaction Gate는 `assistant.app_os.interaction_gate.v1`로 observe-plan candidate, app open/click/type/hotkey/file dialog blocked, permission model 문서화, approval binding 설계, no OS action executed를 고정한다. Computer Use, AppleScript, `osascript`, `open` command, app control 실행은 연결하지 않았다.
- 21차 Personal Workflow Presets는 `project_review`, `docs_check`, `ci_preview`, `patch_review`, `browser_review_plan` preset을 safe template으로 노출하고 frozen `proposed_steps` 후보만 만든다. unsafe preset id, approval-like JSON injection, unmasked secret-like params는 blocked 상태로 남긴다.
- 22차 Long-running Task Queue는 `queued`, `running`, `completed`, `blocked`, `cancelled` status taxonomy와 no-op/read-only task preview, cancellation state, audit link, TTL/cleanup policy만 고정한다. 실제 background worker loop, daemon/service, shell/patch/browser/app-os/external API 실행은 연결하지 않았다.
- 23차 Failure Recovery / Rollback은 failure reason taxonomy, patch rollback plan의 `original_sha256`, shell/browser manual instruction only, paste-safe summary를 고정한다. 자동 rollback, git reset, file restore, shell execution, browser interaction은 연결하지 않았다.
- 실제 활성화 전에는 durable approval 저장소가 필요한지, multi-process/재시작 시 approval 소멸 정책을 어떻게 둘지 별도로 결정해야 한다.
- tool result 또는 클라이언트 입력의 approval-like payload가 서버 binding을 대체하거나 병합하면 안 된다.
- patch 승인 해시는 raw proposed content bytes와 original SHA-256 precondition에 바인딩해야 한다. 실제 apply 직전에는 디스크 원본의 SHA-256을 다시 검증해야 한다.
- patch `project_root`는 `AGENT_ALLOWED_ROOTS`를 대체할 수 없고, configured allowed roots 안쪽일 때만 더 좁은 교집합 root로 사용해야 한다.
- patch diff preview가 raw operation source가 되지 않도록 한다. diff preview는 설명/검토용이며 apply payload나 payload hash 재계산 근거가 되면 안 된다.
- secret-looking value는 LLM context, audit log, UI response에 들어가기 전에 masking 되어야 한다.
- frozen plan의 goal뿐 아니라 steps params와 중첩 params도 masking해야 한다. raw params를 LLM context/UI/audit에 그대로 반환하면 안 된다.
- `require_wrappers` 또는 `require_approval_bindings` 같은 fail-closed gate opt-out footgun은 제거하거나 `true` 외 값을 거부해야 한다.
- missing wrapper, payload hash mismatch, approval injection, unsafe browser action은 모두 fail closed 회귀 테스트로 고정한다.
- 실제 활성화 전 Claude Opus 보안 리뷰와 사용자 최종 승인을 받는다.
- 48차 Full Automation Action-loop Dispatch Decision Required 기준으로 실제 action-loop full dispatch는 계속 금지한다. connector별 approval consume, rollback/failure strategy, browser actual interaction, app-os actual action, external provider 확장, daemon/service 조건은 사용자 최종 승인과 Opus 리뷰 전 실행 권한이 아니다.

### P1: 활성화 전 강하게 권장

- 실제 dispatch 시작 전 no-op dispatcher dry-run 결과를 route별로 검토한다.
- no-op dispatcher도 서버 store approval을 직접 소비하기 전에 preview-only 검증 모드와 consume 모드를 분리한다. 현재 구현은 validate-only다.
- audit payload schema를 고정하고, masked preview와 raw payload 보관 금지 범위를 문서화한다.
- rate limit, session binding, manual interrupt, kill switch, rollback note 표시를 API 계약에 포함한다.
- read-only dispatch와 mutating dispatch를 분리한다.
- read-only boundary preview를 실제 read-only adapter 실행으로 전환하기 전, 어떤 adapter가 파일 내용/폴더 목록/URL 응답을 실제로 읽을 수 있는지 별도 승인한다.
- 위험 action은 한 번에 하나만 승인되도록 하고 approve-all 또는 bulk approval을 추가하지 않는다.

### P2: 이후 개선

- UI에서 locked/preview/dispatch 상태를 명확히 구분한다.
- action-loop failure reason을 사용자에게 paste-safe summary로 제공한다.
- 장기적으로 로컬-only policy와 외부 provider policy를 분리 문서로 관리한다.

## 활성화 후보 단계

아래 단계는 다음 리뷰 후의 후보일 뿐이며, 이 문서 작성 시점에는 구현하지 않는다.

1. No-op dispatcher dry-run: step routing만 기록하고 어떤 tool도 실행하지 않는다.
2. Read-only dispatch only: 파일/폴더/로컬 preview처럼 mutation 없는 action만 단일 boundary를 통해 실행한다.
3. Manual shell/patch/browser preview loop: 실제 실행 없이 approval preview와 payload hash만 반복 검증한다.
4. Single-action execution: 별도 보안 리뷰와 사용자 최종 승인 후, 가장 낮은 위험의 단일 action부터 제한적으로 검토한다.

## 구현 금지 조건

- `ENABLE_ACTION_LOOP` 같은 실제 dispatch 활성화 값을 기본값에서 켜지 않는다.
- 무제한 shell 실행, 실제 subprocess dispatch, sudo, destructive command, network installer를 허용하지 않는다.
- 파일 생성, 수정, 삭제, patch apply를 자동 적용하지 않는다.
- 브라우저 click, fill, submit, login, payment, delete 또는 OS app control을 활성화하지 않는다.
- 외부 LLM/API provider, LAN/private-network crawling, cloud runner를 활성화하지 않는다.
- 외부 web search API provider, API key, paid search provider, browser fetch를 활성화하지 않는다.
- Computer Use, AppleScript, `osascript`, `open` command, app launch, click/type/hotkey, file dialog를 활성화하지 않는다.
- background worker loop, daemon/service, long-running queue auto-run, retry worker를 활성화하지 않는다.
- 자동 rollback, git reset, file restore, shell 재실행, browser interaction 기반 복구를 활성화하지 않는다.
- full automation action-loop full dispatch를 활성화하지 않는다.
- 새 store, table, endpoint, 위험 flag를 활성화 우회 목적으로 추가하지 않는다.
- master unlock, approval binding, payload hash 검증을 완화하지 않는다.
- approve-all 또는 bulk approval을 추가하지 않는다.

## 활성화 전 회귀 테스트 요구사항

- Missing wrapper는 fail closed 되어야 한다.
- Wrapper가 있더라도 untrusted marker가 없으면 fail closed 되어야 한다.
- Tool result에 포함된 지시문은 frozen plan의 steps, 순서, 개수, params, 중첩 params를 바꾸지 못해야 한다.
- Tool result에 포함된 approval-like payload는 manual approval payload를 대체하거나 병합하지 못해야 한다.
- Read-only result wrapper에 포함된 raw content, approval-like JSON, next step, shell command, patch payload, browser action은 LLM context나 다음 step 결정으로 승격되지 않아야 한다.
- Payload hash mismatch는 dispatch 불가 상태로 남아야 한다.
- Unknown approval id, expired approval, already-used approval, session/request context mismatch는 dispatch 불가 상태로 남아야 한다.
- Client-supplied approval-like JSON은 서버 store approval로 승격되거나 병합되면 안 된다.
- Patch diff preview는 raw operation source나 payload hash 재계산 근거로 사용되지 않아야 한다.
- Secret-looking value는 LLM context, audit payload, UI response 이전에 masking 되어야 한다.
- Unsafe browser/app action은 approval preview가 있어도 locked 상태로 남아야 한다.
- Browser gate 응답은 `execution_enabled=false`, `would_interact=false`, `browser_launch=not_performed`를 유지해야 한다.
- External web search provider gate 응답은 `external_api_enabled=false`, `would_search=false`, `would_fetch=false`, `external_call_performed=false`, `network_request_performed=false`를 유지해야 한다.
- App/OS interaction gate 응답은 `allowed=false`, `would_control_app=false`, `os_action_executed=false`, `app_os_control_enabled=false`를 유지해야 한다.
- Workflow preset preview 응답은 `would_dispatch=false`, `execution_enabled=false`를 유지하고, 생성된 `frozen_proposed_steps`를 자동 dispatch 또는 approval consume으로 연결하지 않아야 한다.
- Long-running task queue 응답은 `worker_enabled=false`, `execution_enabled=false`를 유지하고, create/cancel/list/detail 중 어떤 endpoint도 background worker, shell, patch, browser, app/os, external API, action-loop dispatch를 시작하지 않아야 한다.
- Failure recovery preview 응답은 `rollback_enabled=false`, `execution_enabled=false`, `would_execute=false`, `would_apply=false`, `would_interact=false`를 유지하고 rollback plan을 자동 실행하지 않아야 한다.

## Codex가 지금 할 수 있는 일

- 문서 정합성 유지
- locked/preview 계약 테스트 보강
- local CI, docs contract, public release scanner 검증
- Claude Opus 리뷰용 handoff 작성

## 리뷰 또는 사용자 승인 전 하면 안 되는 일

- action-loop dispatch 구현
- arbitrary shell 또는 27차 allowlist 밖 shell dispatch 연결
- patch apply/file write/delete 연결
- browser/app interaction 연결
- 외부 LLM/API provider 연결
- 위험 기본값 변경
- approval binding 완화

## Decision Required

현재 8차까지의 구현은 개인 API 자동화의 사전 안전장치다. 실제 자동화를 켜려면 먼저 위 P0 항목을 리뷰하고, 어떤 action부터 어떤 boundary로 열지 사용자 최종 승인이 필요하다.

## 48차 Full Automation Action-loop Dispatch Decision Required

48차는 실제 action-loop full dispatch를 열지 않고 Decision Required만 고정했다.

- Full Automation Action-loop Dispatch Decision Required
- 실제 action-loop full dispatch는 계속 금지
- 사용자 최종 승인
- Opus 리뷰
- connector별 approval consume
- rollback/failure strategy
- browser actual interaction
- app-os actual action
- `action_loop_full_dispatch_connected=false`
- `browser_actual_interaction_connected=false`
- `app_os_actual_action_connected=false`
