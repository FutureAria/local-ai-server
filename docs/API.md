# API Reference

`local-ai-server`는 FastAPI 기반 로컬 전용 API 서버다. 런타임 LLM과 embedding 호출은 Ollama local API만 사용한다.

브라우저 UI 연동용 예시 payload는 [UI_BRIDGE_EXAMPLES.md](UI_BRIDGE_EXAMPLES.md)에 별도로 정리되어 있다.
브라우저 UI 수동 QA 기준은 [UI_QA_CHECKLIST.md](UI_QA_CHECKLIST.md)에 별도로 정리되어 있다.
GitHub 공개 전 체크리스트는 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)에 별도로 정리되어 있다.
공개 상태 요약은 [PUBLIC_RELEASE_SUMMARY.md](PUBLIC_RELEASE_SUMMARY.md)에 별도로 정리되어 있다.

기본 실행 주소:

```bash
http://127.0.0.1:8000
```

## 인증

`LOCAL_API_KEY`가 설정되어 있으면 보호 endpoint는 `X-API-Key` 헤더를 요구한다. 외부 로컬 UI가 Bearer token 입력만 지원하는 경우를 위해 `Authorization: Bearer <LOCAL_API_KEY>`도 같은 키로 허용한다.

```bash
X-API-Key: <LOCAL_API_KEY>
Authorization: Bearer <LOCAL_API_KEY>
```

보호 endpoint:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`
- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder-job-preview`
- `POST /documents/index-folder`
- `DELETE /documents/{document_id}`
- `POST /feedback`
- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`
- `GET /agent/runs/{run_id}/results`
- `GET /agent/runs/{run_id}/actions`
- `POST /agent/runs/{run_id}/dry-run`
- `POST /agent/runs/{run_id}/approve`
- `POST /agent/runs/{run_id}/reject`
- `POST /agent/runs/{run_id}/execute`
- `GET /project/shell-policy`
- `POST /project/shell-dry-run`
- `GET /assistant/capabilities`
- `POST /assistant/action-preview`
- `GET /assistant/ping`
- `GET /assistant/config`
- `GET /assistant/ui-contract`
- `GET /assistant/startup`
- `GET /assistant/status`
- `GET /assistant/dashboard`
- `POST /assistant/bootstrap`
- `POST /assistant/sessions`
- `GET /assistant/sessions`
- `GET /assistant/sessions/{session_id}`
- `GET /assistant/sessions/{session_id}/messages`
- `POST /assistant/message`
- `POST /assistant/project-root/validate`

조회 전용 endpoint 중 `GET /documents`, `GET /documents/stats`, `GET /documents/integrity`, `GET /documents/repair-preview`, `GET /documents/vector-rebuild-preview`, `GET /chat-logs`, `GET /feedback`, `GET /project/status`, `GET /project/next`, `GET /project/api-inventory`는 현재 API key 없이 읽을 수 있다. `/agent/runs`는 사용자 요청 내용이 포함될 수 있어 보호 endpoint로 둔다. shell dry-run 정책 endpoint는 명령 후보가 포함될 수 있어 `LOCAL_API_KEY` 설정 시 보호된다. 개인 문서가 들어가는 환경에서는 서버를 `127.0.0.1`에만 bind하는 것을 권장한다.

## Rate Limit

보호 endpoint는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit을 적용한다. 기본값은 분당 `120`회이며, `0`으로 설정하면 비활성화된다.

제한을 초과하면 `429 Too Many Requests`와 `Retry-After` header를 반환한다.

## CORS

브라우저 기반 로컬 UI 호출을 위해 `LOCAL_CORS_ORIGINS`에 명시된 origin만 허용한다.

기본값:

```env
LOCAL_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

허용 header:

- `Authorization`
- `Content-Type`
- `X-API-Key`

## Health

### `GET /health`

서버 설정 기본값을 확인한다. Ollama 연결을 강제하지 않는다.

```bash
curl http://127.0.0.1:8000/health
```

응답 예:

```json
{
  "status": "ok",
  "service": "local-ai-server",
  "ollama_base_url": "http://localhost:11434",
  "llm_model": "llama3.2",
  "embedding_model": "nomic-embed-text"
}
```

### `GET /health/ollama`

Ollama server와 모델 준비 상태를 확인한다.

```bash
curl http://127.0.0.1:8000/health/ollama
```

## Project Status

### `GET /project/status`

현재 완료 차수, 다음 안전 작업, 보류 중인 고위험 작업, Recommended Next Model을 반환한다.

```bash
curl http://127.0.0.1:8000/project/status
```

### `GET /project/next`

다음에 이어갈 안전 작업과 Recommended Next Model만 요약해 반환한다.

```bash
curl http://127.0.0.1:8000/project/next
```

### `GET /project/api-inventory`

현재 FastAPI endpoint 목록, tag, HTTP method, API key 보호 여부를 read-only로 조회한다. 브라우저 UI나 CLI가 어떤 endpoint를 연결해야 하는지 확인할 때 사용한다.

```bash
curl http://127.0.0.1:8000/project/api-inventory
```

응답 핵심 필드:

- `mode=read-only`
- `endpoints_count`
- `protected_endpoints_count`
- `public_endpoints_count`
- `endpoints[].path`
- `endpoints[].methods`
- `endpoints[].requires_api_key`
- `safety`

### `GET /project/shell-policy`

shell 실행 엔진을 활성화하기 전, dry-run 기준의 allowlist와 blocked token을 조회한다. 실제 shell 명령은 실행하지 않는다.

```bash
curl http://127.0.0.1:8000/project/shell-policy
```

응답 핵심 필드:

- `mode=dry-run-only`
- `allowed_commands`
- `blocked_tokens`
- `note`

### `POST /project/shell-dry-run`

입력한 shell 명령 후보가 현재 정책상 허용 preview인지 차단 대상인지 판단한다. 이 endpoint는 명령을 실행하지 않으며 항상 `would_execute=false`를 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/project/shell-dry-run \
  -H "Content-Type: application/json" \
  -d '{"command":"pwd"}'
```

응답 핵심 필드:

- `command`
- `status=allowed_preview|blocked`
- `would_execute=false`
- `reason`

## Assistant

### `GET /assistant/capabilities`

브라우저 UI나 외부 로컬 클라이언트가 현재 서버 기능과 안전 기본값을 확인한다.

```bash
curl http://127.0.0.1:8000/assistant/capabilities
```

응답 핵심 필드:

- `modes`
- `protected`
- `safe_defaults`
- `endpoints`

### `POST /assistant/action-preview`

메시지를 실제 처리하기 전에 intent, 추천 endpoint, 위험도, 필요한 입력값을 preview한다. 이 endpoint는 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/action-preview \
  -H "Content-Type: application/json" \
  -d '{"message":"브라우저 열어줘","project_root":"/Users/juyoung/local-ai-server","mode":"auto"}'
```

응답 핵심 필드:

- `intent`
- `recommended_endpoint`
- `would_execute=false`
- `requires_approval`
- `risk_level`
- `needs`
- `ui`

### `GET /assistant/ping`

브라우저 UI가 서버 연결, 인증 header, 로컬 API ready 상태를 가볍게 확인한다.

```bash
curl http://127.0.0.1:8000/assistant/ping
```

응답 핵심 필드:

- `status=ok`
- `protected`
- `local_only`
- `ui_ready`

### `GET /assistant/config`

브라우저 UI가 사용할 수 있는 설정을 secret 없이 조회한다. `LOCAL_API_KEY` 값은 반환하지 않고 `protected` 여부만 반환한다.

```bash
curl http://127.0.0.1:8000/assistant/config
```

응답 핵심 필드:

- `protected`
- `cors_origins`
- `allowed_roots`
- `models`
- `storage`
- `safety`
- `rate_limit`

### `GET /assistant/ui-contract`

브라우저 UI가 따라야 할 시작 순서, refresh endpoint, 메시지 흐름, 응답 타입, 차단 기능을 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/ui-contract
```

응답 핵심 필드:

- `startup_sequence`
- `refresh_endpoints`
- `message_flow`
- `response_types`
- `blocked_actions`
- `auth.secret_returned=false`

### `GET /assistant/startup`

브라우저 UI의 첫 로딩에 필요한 `ping`, `config`, `dashboard`, `ui_contract`를 read-only snapshot으로 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/startup
```

응답 핵심 필드:

- `ping`
- `config`
- `dashboard`
- `ui_contract`
- `recommended_calls`
- `ui`

### `GET /assistant/status`

UI 첫 화면에서 필요한 현재 차수, 문서 저장소 요약, integrity 요약, assistant 세션 요약, 안전 상태를 한 번에 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/status
```

응답 핵심 필드:

- `current_phase`
- `documents`
- `integrity`
- `sessions`
- `safety`

### `GET /assistant/dashboard`

UI 첫 화면 카드에 바로 쓰기 좋은 문서, 세션, integrity, 연결 상태와 최근 세션 목록을 반환한다.

```bash
curl http://127.0.0.1:8000/assistant/dashboard
```

응답 핵심 필드:

- `current_phase`
- `cards.documents`
- `cards.integrity`
- `cards.sessions`
- `cards.connection`
- `recent_sessions`
- `ui`

### `POST /assistant/bootstrap`

브라우저 UI 시작 흐름에서 필요한 capabilities, status, project root 검증 결과, 최근 session 목록, UI 표시 힌트를 한 번에 반환한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "project_root":"/Users/juyoung/local-ai-server",
    "include_sessions":true,
    "sessions_limit":10
  }'
```

응답 핵심 필드:

- `capabilities`
- `status`
- `project_root`
- `sessions`
- `recommended_calls`
- `ui.ready`
- `ui.blocked_actions`

### `POST /assistant/sessions`

assistant 대화 세션을 생성한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo","project_root":"/Users/juyoung/local-ai-server"}'
```

### `GET /assistant/sessions`

assistant 최근 세션 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/assistant/sessions?limit=20&offset=0"
```

응답 핵심 필드:

- `sessions`
- `sessions[].session_id`
- `sessions[].messages_count`
- `sessions[].last_message_preview`
- `limit`
- `offset`

### `GET /assistant/sessions/{session_id}`

assistant 세션과 메시지 기록을 조회한다.

```bash
curl http://127.0.0.1:8000/assistant/sessions/<session_id>
```

### `GET /assistant/sessions/{session_id}/messages`

assistant 세션 메시지를 paging으로 조회한다. UI에서 긴 대화 기록을 렌더링할 때 사용한다.

```bash
curl "http://127.0.0.1:8000/assistant/sessions/<session_id>/messages?limit=50&offset=0"
```

응답 핵심 필드:

- `session_id`
- `total_messages`
- `limit`
- `offset`
- `messages`

### `POST /assistant/message`

UI 입력창에서 들어온 문장을 자동 분기한다. `mode=auto`에서는 문서 RAG, 검색, folder index preview, agent plan, shell dry-run 중 안전한 경로로 분류한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/message \
  -H "Content-Type: application/json" \
  -d '{"message":"내 문서 기준으로 JWT 설명해줘","project_root":"/Users/juyoung/local-ai-server","mode":"auto"}'
```

응답 핵심 필드:

- `session_id`
- `type`
- `answer`
- `data`
- `used_documents`
- `sources`
- `request_id`
- `safety`
- `ui`

안전 기준:

- 폴더 색인은 assistant API에서 preview-only로 처리한다.
- shell은 실제 실행하지 않고 dry-run 정책 판단만 반환한다.
- 브라우저 클릭, 파일 수정/삭제, 외부 LLM API 호출은 수행하지 않는다.

### `POST /assistant/project-root/validate`

UI에서 입력한 project root가 존재하는 폴더인지, `AGENT_ALLOWED_ROOTS` 안에 있는지 확인한다.

```bash
curl -X POST http://127.0.0.1:8000/assistant/project-root/validate \
  -H "Content-Type: application/json" \
  -d '{"project_root":"/Users/juyoung/local-ai-server"}'
```

## Ask

### `POST /ask`

문서 검색 없이 Ollama local chat API로 답변한다. 질문과 답변은 SQLite `chat_logs`에 저장된다.

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Spring Boot가 뭐야?","temperature":0.2}'
```

응답 핵심 필드:

- `answer`
- `model`
- `used_documents=false`
- `request_id`

### `POST /ask-with-docs`

Chroma에서 관련 chunk를 검색한 뒤, 검색 context 기반으로 Ollama local chat API를 호출한다.

```bash
curl -X POST http://127.0.0.1:8000/ask-with-docs \
  -H "Content-Type: application/json" \
  -d '{"question":"내 문서 기준으로 JWT 인증 흐름 설명해줘","top_k":5,"temperature":0.2}'
```

응답 핵심 필드:

- `answer`
- `model`
- `used_documents=true`
- `sources`
- `request_id`

RAG 답변은 문서 밖 코드, 링크, 보안 세부사항, 추측성 표현을 감지하면 보수적인 fallback 답변으로 대체될 수 있다.

## Documents

### `POST /documents/upload`

문서를 업로드하고 SQLite/Chroma에 색인한다.

지원 형식:

- 기본: `.txt`, `.md`, `.html`, `.htm`
- optional dependency 필요: `.pdf`, `.docx`

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@./notes/backend.md"
```

응답 예:

```json
{
  "document_id": 1,
  "filename": "backend.md",
  "chunks_created": 3
}
```

### `POST /documents/index-folder-preview`

실제 저장 전에 폴더 색인 예상 작업량을 read-only로 확인한다. 원본 파일 수정, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder-preview \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 핵심 필드:

- `files_count`
- `skipped_files_count`
- `chunks_estimated`
- `embedding_batch_size`
- `embedding_batches_estimated`
- `token_estimate`
- `files`
- `skipped_files`
- `dry_run=true`

### `POST /documents/index-folder-job-preview`

대용량 폴더 색인을 나중에 job/status API로 분리할 때 사용할 progress response schema를 preview-only로 확인한다. 이 endpoint는 queue 생성, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder-job-preview \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 핵심 필드:

- `job_id`
- `status`
- `folder_path`
- `recursive`
- `dry_run`
- `would_enqueue`
- `progress`
- `status_endpoint`
- `note`

`progress`에는 `total_files`, `processed_files`, `indexed_documents`, `skipped_files`, `chunks_created`, `embedding_batches_total`, `embedding_batches_completed`, `percent`가 포함된다.

### `POST /documents/index-folder`

로컬 폴더의 지원 파일을 실제로 색인한다. 원본 폴더 파일은 수정하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답 핵심 필드:

- `indexed_documents`
- `skipped_files`
- `chunks_created`
- `document_ids`
- `indexed_files`
- `skipped_file_details`

### `GET /documents`

문서 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/documents?source_type=upload&file_type=md&query=backend"
```

필터:

- `source_type=upload|folder`
- `file_type=txt|md|pdf|docx|html`
- `query=<filename 또는 path keyword>`

### `GET /documents/{document_id}`

문서 상세와 chunk 목록을 조회한다.

```bash
curl http://127.0.0.1:8000/documents/1
```

### `GET /documents/{document_id}/chunks`

문서 chunk를 페이지 단위로 조회한다.

```bash
curl "http://127.0.0.1:8000/documents/1/chunks?limit=20&offset=0"
```

### `DELETE /documents/{document_id}`

문서 metadata, chunk, vector를 삭제한다.

```bash
curl -X DELETE http://127.0.0.1:8000/documents/1
```

주의: 이 endpoint는 삭제 작업이므로 실제 사용자 데이터가 있는 환경에서는 신중하게 호출한다.

### `GET /documents/supported-types`

문서 타입별 사용 가능 여부를 확인한다.

```bash
curl http://127.0.0.1:8000/documents/supported-types
```

### `GET /documents/stats`

SQLite/Chroma 저장 상태를 read-only로 확인한다.

```bash
curl http://127.0.0.1:8000/documents/stats
```

### `GET /documents/integrity`

SQLite chunk와 Chroma vector 정합성을 read-only로 확인한다.

```bash
curl http://127.0.0.1:8000/documents/integrity
```

### `GET /documents/repair-preview`

필요한 repair action 후보만 반환한다. 실제 repair/delete/rebuild는 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/documents/repair-preview
```

### `GET /documents/vector-rebuild-preview`

Chroma vector가 누락된 SQLite chunk만 대상으로 재생성 후보를 반환한다. 실제 Ollama embedding 생성, Chroma vector 재생성, DB 수정은 수행하지 않는다.

```bash
curl http://127.0.0.1:8000/documents/vector-rebuild-preview
```

응답 핵심 필드:

- `status`
- `dry_run`
- `chunks_missing_vectors_count`
- `embedding_batch_size`
- `embedding_batches_estimated`
- `actions_count`
- `actions`
- `note`

## Search

### `POST /search`

Ollama embedding과 Chroma를 사용해 의미 검색을 수행한다.

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"JWT authentication","top_k":5}'
```

응답 핵심 필드:

- `query`
- `results`
- `results[].chunk_id`
- `results[].document_id`
- `results[].filename`
- `results[].chunk_index`
- `results[].content`
- `results[].score`

## Chat Logs

### `GET /chat-logs`

질문/답변 기록 목록을 preview 형태로 조회한다.

```bash
curl "http://127.0.0.1:8000/chat-logs?limit=20&offset=0"
curl "http://127.0.0.1:8000/chat-logs?mode=rag&query=JWT&limit=20&offset=0"
```

필터:

- `mode=direct|rag`
- `query=<keyword>`

### `GET /chat-logs/{chat_log_id}`

chat log 상세를 조회한다.

```bash
curl http://127.0.0.1:8000/chat-logs/1
```

## Feedback

### `POST /feedback`

`request_id` 기준으로 답변 피드백을 저장한다.

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"request_id":"1","rating":"good","corrected_answer":"수정 답변","note":"좋은 답변"}'
```

`rating` 허용 값:

- `good`
- `bad`
- `neutral`

### `GET /feedback`

피드백 목록을 조회한다.

```bash
curl "http://127.0.0.1:8000/feedback?limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?rating=bad&limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?chat_log_id=1&limit=20&offset=0"
```

## Agent

### `POST /agent/plan`

실행형 Agent 요청을 preview-only 실행 계획으로 분류한다. 실제 웹 이동, 브라우저 클릭, 폴더 열기, 파일 수정, shell 실행은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/agent/plan \
  -H "Content-Type: application/json" \
  -d '{"instruction":"GitHub 웹 열고 내 폴더도 열어줘"}'
```

응답 핵심 필드:

- `run_id`
- `status=planned`
- `risk_level`
- `execution_enabled=false`
- `actions`
- `actions[].tool`
- `actions[].risk_level`
- `actions[].requires_approval`

### `GET /agent/runs`

agent plan 기록을 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs
```

### `GET /agent/runs/{run_id}`

agent plan 상세를 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1
```

### `GET /agent/runs/{run_id}/actions`

agent action별 상태, dry-run 결과, execution 결과를 함께 조회한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1/actions
```

### `POST /agent/runs/{run_id}/dry-run`

실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 실행 전 정책 판단만 기록한다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/dry-run
```

### `POST /agent/runs/{run_id}/approve`

agent plan을 승인 상태로 바꾼다. 상태는 `approved_pending_execution`이 되며, 실제 실행은 별도 `execute` 호출에서만 시도한다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/approve
```

### `POST /agent/runs/{run_id}/reject`

agent plan을 거절 상태로 바꾼다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/reject
```

### `POST /agent/runs/{run_id}/execute`

승인된 agent run만 실행 시도한다. 기본값 `AGENT_EXECUTION_ENABLED=false`에서는 실제 실행을 차단하고 `blocked` 결과를 기록한다.

`AGENT_EXECUTION_ENABLED=true` 상태의 v1 실행 엔진은 아래만 지원한다.

- 허용 root 안의 폴더 read-only list 조회
- 허용 root 안의 텍스트 파일 read-only content preview
- 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자 차단
- `AGENT_WEB_FETCH_ENABLED=true`이고 명시 URL이 있는 경우 read-only URL fetch
- URL fetch 응답은 `AGENT_WEB_FETCH_MAX_BYTES` 이후 truncate

브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 수행하지 않는다.

```bash
curl -X POST http://127.0.0.1:8000/agent/runs/1/execute
```

### `GET /agent/runs/{run_id}/results`

agent 실행 결과만 조회한다. 실행 전이면 빈 배열을 반환한다.

```bash
curl http://127.0.0.1:8000/agent/runs/1/results
```

## CLI 대응

CLI는 위 API를 HTTP로 호출한다. CLI 내부에 비즈니스 로직을 중복 구현하지 않는다.

```bash
local-ai health
local-ai doctor
local-ai status
local-ai next
local-ai api-inventory
local-ai roots
local-ai shell-policy
local-ai shell-dry-run "pwd"
local-ai assistant-capabilities
local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server
local-ai assistant-ping
local-ai assistant-config
local-ai assistant-ui-contract
local-ai assistant-startup
local-ai assistant-status
local-ai assistant-dashboard
local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server
local-ai assistant-session --title "Demo" --project-root /Users/juyoung/local-ai-server
local-ai assistant-sessions
local-ai assistant-messages session-1 --limit 50 --offset 0
local-ai assistant-message "질문" --project-root /Users/juyoung/local-ai-server
local-ai assistant-root /Users/juyoung/local-ai-server
local-ai assist "질문"
local-ai assistant
local-ai ask "질문"
local-ai ask-docs "질문"
local-ai search "검색어"
local-ai upload ./notes/backend.md
local-ai index-preview ./notes
local-ai index ./notes
local-ai docs
local-ai document-types
local-ai chunks 1
local-ai stats
local-ai integrity
local-ai repair-preview
local-ai vector-rebuild-preview
local-ai logs
local-ai log 1
local-ai feedbacks
local-ai agent-plan "GitHub 웹 열어줘"
local-ai agent-runs
local-ai agent-run 1
local-ai agent-actions 1
local-ai agent-dry-run 1
local-ai agent-results 1
local-ai agent-approve 1
local-ai agent-reject 1
local-ai agent-execute 1
local-ai agent-shell
local-ai export-sft --output data/sft_dataset.jsonl
```

## Smoke Script

실행 중인 서버 기준 문서/RAG E2E smoke test:

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000
```

기본 smoke sample은 `smoke-backend-notes.md`와 `smoke-architecture-notes.txt`다. 이 흐름은 `.md`와 `.txt` 업로드를 모두 수행한 뒤 `search`, `ask-with-docs`, `feedback`, `stats`를 확인한다.

공개 문서나 작업 기록에는 paste-safe 결과만 남긴다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --sanitized-summary
```

sanitized smoke summary는 `safe_to_paste=true`, `mode=document-rag`, `steps[].status`, `documents_count`, `results_count`, `sources_count`, `chunks_count`, `excluded_fields`를 포함하고, 질문/답변 원문, request id, header, 로컬 project root, stored path는 제외한다.

브라우저 조작 없는 Assistant UI bridge smoke test:

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
```

Assistant bridge smoke는 `GET /assistant/startup`, `GET /project/api-inventory`, `POST /assistant/bootstrap`, `POST /assistant/action-preview`, `POST /assistant/message`, `GET /assistant/sessions`, `GET /assistant/sessions/{session_id}/messages` 순서로 호출한다. `/assistant/message`는 `mode=auto`와 상태 질문으로 호출해 status intent로 분기하므로 Ollama 답변 생성은 사용하지 않지만 SQLite에 assistant session/message 기록은 추가된다.

## Local CI Check

로컬에서 공개 전 최소 검증을 한 번에 실행한다.

```bash
python scripts/local_ci_check.py --root .
python scripts/local_ci_check.py --root . --json
```

실행 순서:

1. `pytest`
2. `python -m compileall app cli scripts`
3. `python scripts/public_release_check.py --root . --json`
4. `git diff --check`

실패가 발생하면 그 단계에서 멈춘다. 시스템 패키지 설치, 운영 배포, 외부 API 활성화는 수행하지 않는다.
