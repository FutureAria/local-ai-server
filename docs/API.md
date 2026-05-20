# API Reference

`local-ai-server`는 FastAPI 기반 로컬 전용 API 서버다. 런타임 LLM과 embedding 호출은 Ollama local API만 사용한다.

기본 실행 주소:

```bash
http://127.0.0.1:8000
```

## 인증

`LOCAL_API_KEY`가 설정되어 있으면 보호 endpoint는 `X-API-Key` 헤더를 요구한다.

```bash
X-API-Key: <LOCAL_API_KEY>
```

보호 endpoint:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`
- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder`
- `DELETE /documents/{document_id}`
- `POST /feedback`

조회 전용 endpoint 중 `GET /documents`, `GET /documents/stats`, `GET /documents/integrity`, `GET /documents/repair-preview`, `GET /chat-logs`, `GET /feedback`는 현재 API key 없이 읽을 수 있다. 개인 문서가 들어가는 환경에서는 서버를 `127.0.0.1`에만 bind하는 것을 권장한다.

## Rate Limit

보호 endpoint는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit을 적용한다. 기본값은 분당 `120`회이며, `0`으로 설정하면 비활성화된다.

제한을 초과하면 `429 Too Many Requests`와 `Retry-After` header를 반환한다.

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

## CLI 대응

CLI는 위 API를 HTTP로 호출한다. CLI 내부에 비즈니스 로직을 중복 구현하지 않는다.

```bash
local-ai health
local-ai doctor
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
local-ai logs
local-ai log 1
local-ai feedbacks
local-ai export-sft --output data/sft_dataset.jsonl
```
