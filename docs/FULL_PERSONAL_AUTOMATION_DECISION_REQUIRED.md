# Full Personal Automation Boundary Decision Required

작성일: 2026-06-02 KST

## 결론

36~48차에서는 full personal automation을 browser actual interaction/app-os multi-tool dispatch/action-loop full dispatch로 열지 않고, 통합 preflight, no-op orchestrator aggregation, read-only connector integration, allowlist shell connector integration, single-file patch connector integration, single-file rollback connector integration, read-only task queue connector integration, browser observe metadata connector integration, browser limited candidate validation integration, external web search provider connector integration, app-os observe-plan preview integration, policy/audit matrix hardening, Full Automation Action-loop Dispatch Decision Required까지만 구현했다.

- `FULL_AUTOMATION_DISPATCH_ENABLED=false`가 기본값이다.
- `POST /assistant/full-automation-preflight`는 shell, patch, read-only, rollback, task queue, browser, external search, app-os 후보를 frozen route plan으로 분류한다.
- `POST /assistant/full-automation-dispatch`는 기본값 false에서 disabled로 차단하고 approval을 consume하지 않는다.
- flag를 켜도 48차 범위에서는 read-only category step, allowlist shell category step, valid patch approval과 single-file precondition을 모두 통과한 patch category step, valid rollback approval과 current/original hash precondition을 모두 통과한 rollback category step, read-only task type을 통과한 task_queue category step, valid browser approval과 loopback/명시 allowlist URL을 통과한 browser_observe category step, valid browser approval과 selector/field allowlist를 통과한 browser_limited_interaction category step, provider/key/rate/query/wrapper gate를 통과한 external_web_search category step, observe-plan action을 통과한 app_os preview step만 기존 boundary로 처리한다. gate/audit/safety matrix는 safe/preview/mutating connector 상태를 명시한다. browser actual interaction/app-os actual action/action-loop full dispatch connector는 계속 실행하지 않는다.

## Runtime Boundary

| 영역 | 48차 상태 | 실제 실행 연결 |
|---|---|---|
| read-only adapter | route classification + wrapper aggregation + env opt-in adapter 실행 | `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`에서만 연결 |
| shell | allowlist/approval validate + env opt-in shell sandbox 실행 | `SHELL_EXECUTION_ENABLED=true`와 valid approval에서만 연결 |
| patch | single-file approval/hash validate + env opt-in patch apply 실행 | `PATCH_APPLY_ENABLED=true`와 valid approval/precondition에서만 연결 |
| rollback | single-file approval/hash validate + env opt-in rollback restore 실행 | `ROLLBACK_EXECUTOR_ENABLED=true`와 valid approval/precondition에서만 연결 |
| task queue worker | one-shot worker 후보 분류 + env opt-in one-shot task 실행 | `TASK_QUEUE_WORKER_ENABLED=true`에서 `noop`, `read_only_scan`, `file_preview`만 연결 |
| browser observe | 후보 분류 + env opt-in HTTP metadata/title/current URL observe 실행 | `BROWSER_OBSERVE_ENABLED=true`와 valid approval에서만 연결 |
| browser limited interaction | 후보 분류 + env opt-in candidate validation 실행 | `BROWSER_LIMITED_INTERACTION_ENABLED=true`와 valid approval/allowlist에서만 연결 |
| external web search | 후보 분류 + env opt-in provider search 실행 | `EXTERNAL_WEB_SEARCH_ENABLED=true`, `brave`, provider configured, rate limit, wrapper gate에서만 연결 |
| app-os preview | 후보 분류 + observe-plan preview wrapper 중첩 | 실제 OS action 없이 preview-only 연결 |
| app-os control | blocked | 실제 app open/click/type/hotkey/file dialog 미연결 |
| policy/audit matrix | gate/audit/safety hardening | safe/preview/mutating/browser actual/app-os actual/action-loop full 상태 명시 |
| action-loop full dispatch | Full Automation Action-loop Dispatch Decision Required | 실제 action-loop full dispatch는 계속 금지 |
| daemon/service | blocked | 미연결 |
| git reset/bulk restore | blocked | 미연결 |

## Approval Contract

- preflight와 disabled dispatch는 approval을 consume하지 않는다.
- approval-like JSON injection은 tool result나 params 내부에 있어도 authority로 승격하지 않는다.
- tool result wrapper는 `assistant.full_automation.result_wrapper.v1`이며 raw content, approval id, next step, patch payload, rollback payload, browser action, app-os action을 trusted field로 취급하지 않는다.
- frozen plan은 tool result로 mutate할 수 없다.

## Stop Conditions

- arbitrary shell
- pipe, redirect, command chaining, substitution
- file create/delete, bulk patch, workspace 밖 write
- git reset, git clean, git checkout, bulk restore
- browser login/payment/delete/credential input
- actual browser click/fill/type/submit
- app-os open/click/type/hotkey/file dialog
- daemon/service/background loop
- external LLM API, credential 저장/출력
- 운영 배포, cloud/Oracle 리소스 변경

## 37차 완료

37차는 full automation orchestrator를 실제 dispatch로 열지 않고, connector별 route order와 per-step result wrapper aggregation을 no-op으로 고정했다.

- 기본값 disabled 유지
- approval consume은 계속 validate-only
- shell/patch/rollback/read-only connector 실제 호출 금지
- route plan order, dependency, failure strategy, rollback strategy를 paste-safe audit으로 반환
- browser/app-os/daemon/git reset/bulk restore는 계속 blocked

## 38차 완료

38차는 full automation orchestrator를 전체 dispatch로 열지 않고, read-only connector만 기존 read-only adapter execution gate를 재사용해 제한적으로 연결했다.

- 기본값 disabled 유지
- approval consume은 계속 validate-only
- `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`와 full automation flag가 모두 켜진 경우에만 read-only step 실행
- shell/patch/rollback/task/browser/external/app-os connector 실제 호출 금지
- read-only result wrapper를 full automation aggregation wrapper 안에 untrusted로 보관
- browser/app-os/daemon/git reset/bulk restore는 계속 blocked

## 39차 완료

39차는 full automation 안에서 shell connector를 arbitrary shell로 열지 않고, 27~28차 allowlist shell boundary를 재사용해 shell category step만 제한적으로 연결했다.

- 기본값 disabled 유지
- approval consume은 shell step 실행 시에만 기존 shell boundary에서 single-use
- `SHELL_EXECUTION_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, 서버 발급 approval, allowlist command, allowed cwd, payload_hash/session binding을 모두 통과한 shell step만 후보
- patch/rollback/task/browser/external/app-os connector 실제 호출 금지
- shell stdout/stderr는 masking/truncation 후 full automation step wrapper 안에 untrusted로 보관
- browser/app-os/daemon/git reset/bulk restore는 계속 blocked

## 40차 완료

40차는 full automation 안에서 patch connector를 broad file write로 열지 않고, 29~30차 단일 파일 patch boundary를 재사용해 patch category step만 제한적으로 연결했다.

- 기본값 disabled 유지
- `PATCH_APPLY_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, 서버 발급 patch approval, payload_hash/session binding, allowed root, existing UTF-8 single file, original_sha256 precondition, secret scan을 모두 통과한 patch step만 후보
- rollback/task/browser/external/app-os connector 실제 호출 금지
- patch result는 full automation step wrapper 안에 untrusted로 보관하고 raw patch content를 authority로 승격하지 않음
- browser/app-os/daemon/git reset/bulk restore/file delete/file create는 계속 blocked

## 41차 완료

41차는 full automation 안에서 rollback connector를 broad restore로 열지 않고, 35차 단일 파일 rollback boundary를 재사용해 rollback category step만 제한적으로 연결했다.

필수 조건:

- 기본값 disabled 유지
- `ROLLBACK_EXECUTOR_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, 서버 발급 rollback approval, payload_hash/session binding, allowed root, existing UTF-8 single file, current/original hash precondition을 모두 통과한 rollback step만 후보
- task/browser/external/app-os connector 실제 호출 금지
- rollback result는 full automation step wrapper 안에 untrusted로 보관하고 raw restored content를 authority로 승격하지 않음
- git reset/clean/checkout, bulk restore, file delete/file create는 계속 blocked

## 42차 완료

42차는 full automation 안에서 task queue connector를 daemon/service/background worker로 열지 않고, 34차 request-scoped one-shot worker boundary를 재사용해 `noop`, `read_only_scan`, `file_preview` task만 제한적으로 연결했다.

필수 조건:

- 기본값 disabled 유지
- `TASK_QUEUE_WORKER_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, read-only task type, wrapper gate, params masking, approval-like JSON injection 차단을 모두 통과한 task queue step만 후보
- shell/patch/rollback/browser/external/app-os task type은 계속 blocked
- daemon/service/background infinite loop, auto-run worker, durable worker process는 계속 금지

## 43차 완료

43차는 full automation 안에서 browser connector를 실제 click/fill/submit으로 열지 않고, 31차 browser observe read-only metadata boundary를 재사용해 browser_observe category step만 제한적으로 연결했다.

필수 조건:

- 기본값 disabled 유지
- `BROWSER_OBSERVE_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, loopback/명시 allowlist URL, read-only observe action, wrapper gate, approval binding을 모두 통과한 browser_observe step만 후보
- browser observe result는 `assistant.browser_observe.result_wrapper.v1`로 full automation step wrapper 안에 untrusted로 중첩
- browser click/fill/type/submit/login/payment/delete/download/upload/file dialog는 계속 blocked
- persistent browser profile/session mutation과 app-os control은 계속 금지

## 44차 완료

44차는 full automation 안에서 browser limited interaction을 실제 browser launch/click/fill로 열지 않고, 32차 browser limited candidate validation boundary를 재사용해 browser_limited_interaction category step만 제한적으로 연결했다.

필수 조건:

- 기본값 disabled 유지
- `BROWSER_LIMITED_INTERACTION_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, loopback/명시 allowlist origin, selector allowlist, safe fill field allowlist, wrapper gate, approval binding을 모두 통과한 candidate validation step만 후보
- 성공 응답도 `would_interact=false`, `interaction_executed=false`, `browser_launch=not_performed`를 유지
- actual click/fill/type/submit/login/payment/delete/download/upload/file dialog는 계속 blocked

## 45차 완료

45차는 full automation 안에서 external web search를 arbitrary external API로 열지 않고, 33차 `brave` 단건 provider boundary를 재사용해 external_web_search category step만 제한적으로 연결했다.

필수 조건:

- 기본값 disabled 유지
- `EXTERNAL_WEB_SEARCH_ENABLED=true`, `FULL_AUTOMATION_DISPATCH_ENABLED=true`, provider allowlist, provider configured, rate limit, query safety, `wrapper.untrusted=true`를 모두 통과한 단건 search step만 후보
- external search result는 `assistant.external_web_search.result_wrapper.v1`로 full automation step wrapper 안에 untrusted로 중첩
- external LLM API, cloud vector DB, arbitrary provider, browser dispatch, task worker, app-os control은 계속 금지

## 46차 완료

46차는 full automation 안에서 app-os connector를 실제 OS action으로 열지 않고, 20차 app-os interaction preview boundary를 재사용해 app_os category step의 candidate validation/blocked wrapper만 연결했다.

필수 조건:

- 기본값 disabled 유지
- 실제 app open/click/type/hotkey/file dialog는 계속 금지
- app-os preview result만 full automation step wrapper 안에 untrusted로 중첩
- OS permission, approval binding, user confirmation은 설계 계약으로만 유지하고 실행 권한으로 쓰지 않음

## 47차 완료

47차는 full automation을 더 큰 실제 실행으로 열지 않고, connector별 gate/audit/policy matrix를 강화해 action-loop full dispatch나 실제 browser/app-os action 전 Decision Required 조건을 더 명확히 고정했다.

필수 조건:

- 기본값 disabled 유지
- browser actual interaction/app-os actual action은 계속 금지
- connector별 `actual_connector_execution_connected`, `mutating_connector_execution_connected`, approval consume mode를 문서/테스트로 재검증
- external provider 확장, task worker external execution, daemon/service/background loop는 계속 금지

## 48차 완료

48차 Full Automation Action-loop Dispatch Decision Required는 full automation action-loop dispatch를 실제로 열지 않고, action-loop full dispatch Decision Required 문서와 public docs contract를 작성/갱신해 어떤 조건에서 다음 단계로 넘어갈지 고정한 단계다.

필수 조건:

- 실제 action-loop full dispatch는 계속 금지
- browser actual interaction/app-os actual action은 계속 금지
- connector별 approval consume, rollback/failure strategy, user final approval 조건을 Decision Required로 명시
- Codex 구현 가능 범위와 Opus/사용자 승인 필요 범위를 분리
- 사용자 최종 승인과 Opus 리뷰 전까지 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 유지

## Full Automation Action-loop Dispatch Decision Required

실제 action-loop full dispatch를 열려면 아래 조건을 모두 별도 단계에서 충족해야 한다. 이 문서 작성 시점에는 어떤 조건도 실행 권한으로 승격하지 않는다.

| 결정 항목 | 48차 결정 | 다음 단계 전 필요 조건 |
|---|---|---|
| connector별 approval consume | Decision Required | read-only/shell/patch/rollback/task/browser/external/app-os step별 approval consume 시점과 single-use 실패 처리를 Opus 리뷰와 사용자 최종 승인으로 확정 |
| rollback/failure strategy | Decision Required | 실패 step 이후 중단, manual recovery, 단일 파일 rollback 범위, approval 재사용 금지, paste-safe summary 형식을 확정 |
| browser actual interaction | blocked | click/fill/type/submit/login/payment/delete/download/upload/file dialog는 별도 브라우저 actual interaction Decision Required 전 금지 |
| app-os actual action | blocked | app open/click/type/hotkey/file dialog/permission escalation은 별도 app-os actual action Decision Required 전 금지 |
| external provider 확장 | blocked | `brave` 단건 search 밖 provider, 외부 LLM API, cloud vector DB는 별도 provider/cost/security 리뷰 전 금지 |
| daemon/service/background loop | blocked | request-scoped one-shot 범위를 넘는 worker loop, retry daemon, service install은 금지 |
| action-loop full dispatch | blocked | 사용자 최종 승인과 Opus 리뷰 전 실제 action-loop full dispatch는 계속 금지 |

고정 문구:

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

## 검증 앵커

- `tests/test_assistant_service.py -k stage36`
- `tests/test_api_docs_payloads.py`
- `tests/test_public_docs_contract.py`
- `tests/test_security.py::test_protected_endpoint_cases_match_api_inventory`
- `tests/test_ui_bridge_examples.py`
- `tests/test_ui_connect_guide.py`
- `tests/test_ui_contract_cheatsheet.py`
- `tests/test_ui_qa_checklist.py`
