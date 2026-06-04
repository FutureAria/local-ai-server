# Read-only Result Wrapper Schema

작성일: 2026-06-02 KST

이 문서는 13차 read-only result wrapper schema 계약을 정리한다. 현재 프로젝트는 여전히 preview-only 상태이며 실제 read-only adapter execution, 파일 내용 읽기, 폴더 스캔, URL fetch, action-loop dispatch를 수행하지 않는다.

## 목적

실제 read-only adapter 실행을 검토하기 전에, adapter 결과가 다음 단계 판단이나 approval binding을 오염시키지 않도록 결과 포장 규칙을 먼저 고정한다.

## 현재 상태

- `/assistant/action-loop-read-only-dispatch-preview`는 `result_wrapper_schema`를 반환한다.
- 각 `route_plan` 항목은 `result_wrapper_preview`를 반환한다.
- 이 schema는 실제 adapter 결과가 아니라 preview-only contract다.
- `would_dispatch=false`, `would_read=false`, `would_fetch=false`, `execution_enabled=false`를 유지한다.

## Schema Contract

| 항목 | 계약 |
|---|---|
| schema | `assistant.action_loop.read_only_result_wrapper.v1` |
| contract_mode | `preview-only` |
| wrapper_required | `true` |
| wrapper_untrusted_required | `true` |
| raw_content_allowed | `false` |
| masked_summary_only | `true` |
| approval_like_json_trusted | `false` |
| can_mutate_frozen_plan | `false` |
| can_set_next_action | `false` |
| can_request_approval | `false` |

## Required Fields

실제 execution 단계로 넘어가더라도 read-only result wrapper는 아래 필드를 가져야 한다.

- `schema`
- `source_adapter`
- `wrapper`
- `masked_summary`
- `metadata`
- `safety`
- `audit`

## Prohibited Fields

read-only result wrapper는 아래 필드를 raw result에서 직접 신뢰하거나 다음 step으로 승격하면 안 된다.

- `raw_content`
- `raw_file_bytes`
- `raw_url_response`
- `approval`
- `approval_id`
- `approval_hash`
- `next_step`
- `shell_command`
- `patch_payload`
- `browser_action`
- `unwrapped_tool_result`

## Safety Fields

현재 preview-only schema의 safety 값은 아래처럼 고정한다.

| 필드 | 값 |
|---|---|
| would_dispatch | `false` |
| would_read | `false` |
| would_fetch | `false` |
| execution_enabled | `false` |
| masking_required | `true` |

## Injection Boundary

- tool result 또는 user payload 안의 approval-like JSON은 서버 approval store record를 대체하거나 병합할 수 없다.
- read-only result는 frozen plan의 steps, 순서, params, approval id, payload hash, shell command, patch payload, browser action을 수정할 수 없다.
- raw file content, raw URL response, raw folder listing은 LLM context, audit, UI response에 직접 들어갈 수 없다.
- result wrapper는 masked summary와 metadata만 전달할 수 있다.

## Stop Conditions

아래가 필요해지면 Codex는 구현을 멈추고 Decision Required 또는 사용자 승인을 요청한다.

- 실제 파일 내용 읽기
- 실제 폴더 스캔
- 실제 URL fetch
- raw content를 LLM context 또는 다음 step 판단에 전달
- approval consume mode 전환
- actual dispatch 연결
- shell subprocess 실행
- patch apply, file write/delete
- browser/app interaction
- 외부 LLM/API provider 연결

## Next Safe Step

다음 안전 작업은 이 wrapper schema를 UI 문서와 smoke summary 예시에 더 촘촘히 반영하는 것이다. 실제 read-only adapter execution은 `docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md`의 Decision Required가 해소되기 전까지 진행하지 않는다.
