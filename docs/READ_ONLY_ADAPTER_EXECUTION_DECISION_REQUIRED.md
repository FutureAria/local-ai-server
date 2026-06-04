# Read-only Adapter Execution Decision Required

작성일: 2026-06-02 KST

이 문서는 11차 `action-loop-read-only-dispatch-preview` 이후 실제 read-only adapter 실행으로 넘어가기 전에 필요한 결정 조건을 정리한다. 25차에서 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true` opt-in 범위의 file/list/safe URL adapter 실행을 추가했고, 26차에서 `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 read-only adapter flag가 모두 켜졌을 때만 read-only action-loop dispatch를 허용했다. 기본값은 여전히 disabled이며 shell/patch/browser dispatch는 수행하지 않는다.

## 현재 상태

- `/assistant/action-loop-read-only-dispatch-preview`는 read-only adapter 후보를 route plan으로 분류한다.
- `would_dispatch=false`, `would_read=false`, `would_fetch=false`, `execution_enabled=false`를 유지한다.
- `read_only_scan`, `file_preview`, `url_preview`, `workspace_brief` 후보만 boundary에서 허용한다.
- mutating tool, wrapper 누락, allowed root 밖 path/root, sensitive path, invalid URL은 fail closed로 blocked 된다.
- 13차 `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`는 `assistant.action_loop.read_only_result_wrapper.v1` preview-only 계약을 고정했다.
- 14차 assistant bridge smoke summary는 wrapper schema safe flag만 확인하고 raw content를 포함하지 않는다.
- 25차 `/assistant/read-only-adapter/execute`는 기본값 disabled이며, env opt-in과 `result_wrapper.untrusted=true`가 있을 때만 실제 read-only adapter를 실행한다.
- 26차 `/assistant/action-loop-read-only-dispatch`는 기본값 disabled이며, read-only action-loop flag와 adapter flag가 모두 켜졌을 때만 read-only adapter를 호출한다.

## Preview-only Policy Matrix

| Adapter | 현재 11차 상태 | 실제 실행 시 읽는 데이터 | 실행 전 필수 gate | 현재 허용 여부 |
|---|---|---|---|---|
| `read_only_scan` | env opt-in read-only | 허용 root 안의 폴더 목록, 파일명, 확장자 count | allowed root 재검증, sensitive path skip, result masking boundary | `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`에서 가능 |
| `file_preview` | env opt-in read-only | 허용 root 안의 UTF-8 텍스트 파일 일부 내용 | path 재검증, sensitive path block, max bytes, binary block, masking boundary | `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`에서 가능 |
| `url_preview` / `url_fetch` | env opt-in read-only | 명시 http/https URL 응답 일부 | `AGENT_WEB_FETCH_ENABLED`, private/loopback/link-local/metadata host 차단, max bytes, no browser session | 두 flag가 켜진 경우 가능 |
| `workspace_brief` | action-loop에서는 scan adapter로 축소 | scan 요약 중심 | scan gate 통과, raw content 금지, paste-safe summary | read-only dispatch에서 scan adapter로만 처리 |

## Decision Required

실제 read-only adapter 실행으로 전환하려면 아래 항목을 먼저 결정해야 한다.

- 어떤 adapter를 첫 실행 대상으로 할지 선택한다.
- 파일 내용, 폴더 목록, URL 응답이 LLM context, audit, UI response에 들어가기 전 masking boundary를 확정한다.
- read-only 결과가 다음 shell, patch, browser, approval, URL, path, plan step을 수정하지 못하게 frozen plan 불변성을 유지한다.
- read-only result wrapper의 `raw_content`, `approval_id`, `next_step`, `shell_command`, `patch_payload`, `browser_action` 후보를 trusted result로 승격하지 않는 정책을 유지한다.
- approval을 validate-only로 둘지 consume할지 결정한다. 현재는 validate-only다.
- rate limit, max bytes, timeout, kill switch, paste-safe summary 형식을 고정한다.
- private/loopback/link-local host, workspace 밖 path, sensitive path, binary/large file은 fail closed로 유지한다.
- 실제 실행 전 Claude Opus 보안 리뷰 또는 사용자 최종 승인을 받는다.

## Stop Conditions

아래가 필요해지면 Codex는 구현을 멈추고 별도 리뷰 또는 사용자 승인을 요청한다.

- 실제 파일 내용 읽기 활성화
- 실제 폴더 스캔 활성화
- 실제 URL fetch 활성화
- read-only result를 LLM context 또는 다음 step 결정에 투입
- raw content 또는 approval-like JSON을 result wrapper 밖에서 신뢰
- approval consume mode 전환
- shell subprocess 실행
- patch apply, file write/delete
- browser/app interaction
- 외부 LLM/API provider 연결
- 운영 배포, cloud/Oracle 리소스 변경, 비용 영향 작업

## Codex Safe Work

Codex가 지금 할 수 있는 안전 작업은 아래로 제한한다.

- preview-only policy matrix 유지
- fail-closed 테스트 보강
- docs/API/SECURITY/README 계약 정합성 유지
- public release check와 local CI 검증

## Next Safe Step

다음 안전 작업은 실제 실행이 아니라 handoff, UI, smoke, 문서 계약을 최신 preview-only 상태로 유지하는 것이다. 실제 read-only adapter execution은 Decision Required가 해소되기 전까지 진행하지 않는다.
