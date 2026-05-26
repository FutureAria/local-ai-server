# UI Contract Cheatsheet

브라우저 UI 또는 로컬 앱이 `local-ai-server`에 붙을 때 필요한 핵심 endpoint와 표시 필드만 모은 요약표다.

## 공통 연결

| 항목 | 값 |
|---|---|
| API base URL | `http://127.0.0.1:8000` |
| Project root | `/Users/juyoung/local-ai-server` |
| Auth header | `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key: <LOCAL_API_KEY>` |

주의:

- 실제 `LOCAL_API_KEY` 값은 코드, 문서, 로그, 스크린샷에 남기지 않는다.
- 응답의 `safety` 값이 실행 차단 상태면 UI도 실행 버튼을 활성화하지 않는다.

## Endpoint별 표시 필드

| Endpoint | UI 목적 | 우선 표시 필드 |
|---|---|---|
| `GET /assistant/startup` | 첫 화면 hydration | `ping.status`, `config.protected`, `dashboard.cards.connection.status`, `ui.display` |
| `POST /assistant/bootstrap` | project root와 세션 초기화 | `project_root.safe_for_read_only_agent`, `sessions.sessions`, `ui.blocked_actions` |
| `POST /assistant/action-preview` | 전송 전 위험도 미리보기 | `intent`, `risk_level`, `requires_approval`, `missing_inputs`, `ui` |
| `POST /assistant/message` | 실제 메시지 API | `type`, `answer`, `data`, `sources`, `request_id`, `ui.response_type`, `ui.display` |
| `GET /assistant/sessions` | 세션 목록 | `sessions`, `limit`, `offset`, `sessions[].messages_count`, `sessions[].last_message_preview` |
| `GET /assistant/sessions/{session_id}/messages` | 메시지 기록 | `messages`, `limit`, `offset`, `total_messages` |
| `GET /project/api-inventory` | 개발/디버그 API 목록 | `endpoints[].path`, `endpoints[].methods`, `endpoints[].tags`, `endpoints[].requires_api_key` |
| `POST /documents/index-folder-job-preview` | 대용량 색인 progress preview | `job_id`, `status`, `dry_run`, `would_enqueue`, `progress.total_files`, `progress.embedding_batches_total`, `progress.percent`, `status_endpoint` |
| `GET /documents/repair-preview` | SQLite/Chroma repair preview | `status`, `dry_run`, `actions_count`, `actions[].requires_user_approval`, `note` |
| `GET /documents/vector-rebuild-preview` | 누락 vector 재생성 preview | `status`, `dry_run`, `chunks_missing_vectors_count`, `embedding_batches_estimated`, `actions[].requires_user_approval` |

## Message response type 매핑

| `type` | UI 렌더링 | 주요 필드 |
|---|---|---|
| `answer` | 채팅 bubble | `answer`, `used_documents`, `sources`, `ui.primary_text` |
| `search_results` | 검색 결과 panel | `data.query`, `data.results[]`, `ui.primary_text` |
| `index_preview` | 폴더 색인 미리보기 panel | `data.files_count`, `data.chunks_estimated`, `data.embedding_batches_estimated` |
| `needs_project_root` | project root 입력 warning | `data.required_field`, `ui.severity` |
| `shell_dry_run` | shell 정책 판단 panel | `data.command`, `data.status`, `data.would_execute` |
| `agent_plan` | 실행 대신 계획/승인 필요 panel | `data.run_id`, `data.actions[]`, `ui.severity` |
| `status` | 프로젝트 상태 panel | `data.current_phase`, `data.safe_next_tasks` |
| `action_preview` | 전송 전 preview panel | `data.intent`, `data.risk_level`, `data.requires_approval` |

## Safety 필드

UI는 아래 값이 보이면 실제 실행 버튼을 활성화하지 않는다.

| Field | Expected value | UI 처리 |
|---|---|---|
| `safety.shell_execution` | `disabled` | shell 실행 버튼 비활성 |
| `safety.browser_interaction` | `blocked` | 브라우저 click/fill/submit 버튼 비활성 |
| `safety.file_write_delete` | `blocked` | 파일 생성/수정/삭제 버튼 비활성 |
| `safety.external_llm_api` | `not-used` | 외부 LLM provider 선택/전송 비활성 |

## 에러 표시

| HTTP status | UI 메시지 |
|---|---|
| `401` | API key가 필요하거나 잘못되었습니다. |
| `404` | 요청한 endpoint 또는 session을 찾을 수 없습니다. |
| `422` | 요청 필드 형식이 맞지 않습니다. |
| `429` | 요청이 너무 많습니다. 잠시 후 다시 시도하세요. |
| `500` | 서버 내부 오류입니다. 서버 로그를 확인하세요. |

## 금지된 UI 동작

- 브라우저 클릭/입력/전송 자동화
- 실제 shell 실행
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 호출
- 운영 배포 또는 클라우드/Oracle 리소스 변경
