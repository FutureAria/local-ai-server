# local-ai-server

`local-ai-server`는 내 컴퓨터 또는 내 서버에서만 동작하는 백엔드 전용 로컬 AI 지식 서버입니다. 런타임에서 OpenAI, Claude, Gemini 같은 외부 LLM API를 사용하지 않고, Ollama local API만 호출합니다.

## 개발 배경

개인 문서 기반 Q&A를 만들 때 외부 LLM API로 문서 내용이 전송되는 구조는 비용, 개인정보, 재현성 측면에서 부담이 있습니다. 이 프로젝트는 로컬 모델과 로컬 저장소만으로 문서 업로드, 색인, 검색, RAG 답변, 피드백 수집, SFT 데이터 export까지 이어지는 백엔드 흐름을 검증하기 위해 만들었습니다.

최종 요약은 [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)에 별도로 정리되어 있습니다.
문서 정합성 리뷰가 필요하면 [docs/CLAUDE_REVIEW_HANDOFF.md](docs/CLAUDE_REVIEW_HANDOFF.md)를 사용하면 됩니다.
브라우저 UI 연동 예시 payload는 [docs/UI_BRIDGE_EXAMPLES.md](docs/UI_BRIDGE_EXAMPLES.md)에 정리되어 있습니다.
브라우저 UI 수동 QA 기준은 [docs/UI_QA_CHECKLIST.md](docs/UI_QA_CHECKLIST.md)에 정리되어 있습니다.
GitHub 공개 전 체크리스트는 [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)에 정리되어 있습니다.

포트폴리오 관점의 핵심 목표는 다음과 같습니다.

- FastAPI route는 얇게 유지하고 실제 로직은 service 계층에 둔다.
- SQLite를 metadata source of truth로 사용하고 Chroma는 vector search 전용으로 분리한다.
- Ollama local API만 사용해 외부 LLM API 의존성을 제거한다.
- CLI는 백엔드를 HTTP로 호출하게 만들어 API 계약을 재사용한다.
- 테스트와 문서로 구현된 기능, 미구현 기능, 보안 한계를 명확히 구분한다.

## 현재 구현 범위

- FastAPI API 서버
- Ollama local chat API 연동
- Ollama local embedding API 연동
- SQLite 기반 문서/청크/채팅 로그/피드백 저장
- Chroma 기반 로컬 vector search
- `EMBEDDING_BATCH_SIZE` 기반 Ollama embedding batch 처리
- `.txt`, `.md`, `.html`, `.htm` 문서 업로드, 로컬 폴더 색인, read-only 폴더 색인 preview
- optional dependency 설치 시 `.pdf`, `.docx` 문서 텍스트 추출
- 문서 검색 기반 RAG 답변
- 실행형 Agent 계획, 승인, read-only 실행 엔진 v1 API
- Typer CLI
- SFT JSONL export
- pytest 기반 기본 테스트

## 기술 선택 이유

| 기술 | 사용 위치 | 선택 이유 |
|---|---|---|
| FastAPI | HTTP API | Pydantic schema 기반 request/response 검증과 테스트가 쉽고 Python AI 생태계와 잘 맞음 |
| Ollama | local LLM/embedding | 외부 LLM API 없이 로컬 모델로 chat과 embedding을 처리하기 위함 |
| SQLite | metadata/log/feedback | 단일 사용자 로컬 서버에서 운영이 단순하고 파일 기반 백업이 쉬움 |
| Chroma | vector search | 문서 chunk embedding 검색을 로컬에서 처리하기 위함 |
| Typer | CLI | FastAPI 백엔드를 호출하는 개발자 친화적 CLI를 빠르게 제공하기 위함 |
| SQLAlchemy | DB access | ORM 모델과 테스트용 DB 세션 구성이 명확함 |
| pytest | test | service/API contract 중심 검증에 적합함 |

## 핵심 구현 포인트

- `/ask`와 `/ask-with-docs`는 질문/답변을 SQLite `chat_logs`에 저장하고 `request_id`를 반환합니다.
- 문서 업로드와 폴더 색인은 텍스트 추출, chunking, embedding, SQLite 저장, Chroma 저장 순서로 처리합니다.
- SQLite write transaction을 짧게 유지하기 위해 Ollama embedding은 DB write 전에 생성합니다.
- 여러 chunk embedding은 `EMBEDDING_BATCH_SIZE` 단위로 Ollama `/api/embed`에 batch 요청합니다.
- Chroma `PersistentClient`는 요청마다 새로 만들지 않고 프로세스 안에서 공유해 동시 요청 초기화 충돌을 줄입니다.
- DB/Chroma 저장 단계 실패 시 SQLite 변경을 rollback하고 명확한 `DocumentIndexingError`를 반환합니다.
- `/documents/index-folder-preview`는 실제 저장 없이 예상 chunk 수와 embedding batch 수를 계산합니다.
- RAG 답변은 문서 밖 코드, 링크, 보안 세부사항, 추측성 표현을 감지하면 보수적인 fallback 답변으로 대체될 수 있습니다.
- `/agent/plan`은 웹 이동, 폴더 열기, shell 실행 같은 요청을 위험도와 승인 필요 action으로 분류하지만 실제 실행하지 않습니다.

## Architecture

```text
CLI / curl
   |
   v
FastAPI routes
   |
   v
Services
  - RagService
  - DocumentService
  - SearchService
  - FeedbackService
   |
   +--> Ollama local API
   |      - /api/chat
   |      - /api/embed
   |
   +--> SQLite
   |      - documents
   |      - document_chunks
   |      - chat_logs
   |      - feedback
   |
   +--> Chroma
          - vector search only
```

## 요구사항

- Python 3.11 이상
- Ollama
- 로컬 모델:
  - LLM: `llama3.2`
  - Embedding: `nomic-embed-text`

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

PDF/DOCX 문서까지 색인하려면 optional dependency를 추가로 설치합니다. 시스템 패키지는 필요하지 않고 Python 패키지만 사용합니다.

```bash
pip install -e ".[dev,documents]"
```

## Ollama 실행

```bash
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

## 서버 실행

기본적으로 로컬에서만 접근하도록 `127.0.0.1`에 bind하는 것을 권장합니다.

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## curl 테스트

```bash
curl http://127.0.0.1:8000/health
```

전체 API 계약은 [docs/API.md](docs/API.md)에 정리되어 있습니다.

Ollama 서버와 필요한 모델 준비 상태를 확인하려면:

```bash
curl http://127.0.0.1:8000/health/ollama
```

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Spring Boot가 뭐야?","temperature":0.2}'
```

## 문서 업로드

기본 텍스트 문서는 `.txt`, `.md`, `.html`, `.htm`을 지원합니다. HTML은 UTF-8 파일에서 본문 텍스트를 추출하고 `script`, `style`, `head` 내용은 제외합니다. PDF/DOCX는 `pip install -e ".[dev,documents]"`로 optional dependency를 설치한 경우 사용할 수 있습니다.

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@./notes/backend.md"
```

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@./notes/backend.pdf"
```

## 폴더 색인

원본 파일은 삭제하거나 수정하지 않습니다. `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `dist`, `build`, `target` 폴더는 무시합니다.

실제 저장 전에 색인 대상 파일과 예상 chunk 수만 확인하려면 read-only preview를 먼저 실행합니다. 이 API는 원본 파일 수정, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않습니다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder-preview \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

preview 응답에는 `chunks_estimated`, `embedding_batch_size`, `embedding_batches_estimated`가 포함됩니다. 실제 색인 전에 Ollama embedding batch 호출이 대략 몇 번 발생할지 확인하는 용도입니다.

실제 색인은 아래 명령을 사용합니다.

```bash
curl -X POST http://127.0.0.1:8000/documents/index-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path":"./notes","recursive":true}'
```

응답에는 전체 색인 수뿐 아니라 `indexed_files`, `skipped_file_details`가 포함됩니다. 큰 폴더를 색인한 뒤 어떤 파일이 저장됐고 어떤 파일이 UTF-8 오류 등으로 건너뛰어졌는지 확인할 수 있습니다.

## 검색

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"JWT authentication","top_k":5}'
```

## 문서 기반 질문

```bash
curl -X POST http://127.0.0.1:8000/ask-with-docs \
  -H "Content-Type: application/json" \
  -d '{"question":"내 문서 기준으로 JWT 인증 흐름 설명해줘","top_k":5,"temperature":0.2}'
```

## Feedback

`/ask`와 `/ask-with-docs` 응답의 `request_id`는 내부 `chat_logs.id`입니다. 이 값을 사용해 피드백을 저장합니다.

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"request_id":"1","rating":"good","corrected_answer":"수정 답변","note":"좋은 답변"}'
```

`rating`은 `good`, `bad`, `neutral`만 허용합니다.

## Chat Log 조회

질문/답변 기록은 SQLite `chat_logs`에 저장됩니다. 목록 조회는 긴 답변 전체를 노출하지 않고 preview만 반환합니다.

```bash
local-ai logs --limit 20 --offset 0
local-ai logs --mode rag --query JWT --limit 20 --offset 0
```

단건 상세 조회는 전체 질문, 전체 답변, 사용 source를 반환합니다.

```bash
local-ai log 1
```

HTTP API:

```bash
curl "http://127.0.0.1:8000/chat-logs?limit=20&offset=0"
curl "http://127.0.0.1:8000/chat-logs?mode=rag&query=JWT&limit=20&offset=0"
curl "http://127.0.0.1:8000/chat-logs/1"
```

## CLI 사용법

CLI는 FastAPI 백엔드를 호출합니다. 비즈니스 로직을 CLI에 중복 구현하지 않습니다.

```bash
local-ai health
local-ai doctor
local-ai status
local-ai next
local-ai stats
local-ai integrity
local-ai repair-preview
local-ai document-types
local-ai assist "내 문서 기준으로 JWT 인증 흐름 설명해줘"
local-ai assistant
local-ai ask "Spring Boot에서 Controller와 Service 차이 설명해줘"
local-ai upload ./notes/backend.md
local-ai search "JWT"
local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름 설명해줘"
local-ai index-preview ./backend-study
local-ai index ./backend-study
local-ai docs
local-ai docs --source-type upload --file-type md --query backend
local-ai chunks 1 --limit 20 --offset 0
local-ai logs --limit 20 --offset 0
local-ai logs --mode rag --query JWT --limit 20 --offset 0
local-ai log 1
local-ai feedbacks --limit 20 --offset 0
local-ai agent-plan "GitHub 웹 열고 내 폴더도 열어줘"
local-ai agent-runs --limit 20 --offset 0
local-ai agent-run 1
local-ai agent-actions 1
local-ai agent-dry-run 1
local-ai agent-results 1
local-ai agent-approve 1
local-ai agent-reject 1
local-ai agent-execute 1
local-ai agent-shell
local-ai roots
local-ai shell-policy
local-ai shell-dry-run "pwd"
local-ai assistant-capabilities
local-ai assistant-ping
local-ai assistant-config
local-ai assistant-ui-contract
local-ai assistant-startup
local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server
local-ai assistant-status
local-ai assistant-dashboard
local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server
local-ai assistant-session --title "Demo" --project-root /Users/juyoung/local-ai-server
local-ai assistant-sessions
local-ai assistant-messages session-1 --limit 50 --offset 0
local-ai assistant-message "내 문서 기준으로 JWT 설명해줘" --project-root /Users/juyoung/local-ai-server
local-ai assistant-root /Users/juyoung/local-ai-server
local-ai export-sft --output data/sft_dataset.jsonl
```

기본 서버 주소는 `http://127.0.0.1:8000`입니다. 바꾸려면:

```bash
export LOCAL_AI_SERVER_URL=http://127.0.0.1:8000
```

`local-ai docs`는 문서 목록을 read-only로 조회합니다. 필요하면 `source_type`, `file_type`, filename/path 검색어로 좁힐 수 있습니다.

`local-ai assist`는 `/ask-with-docs`를 호출해 내 문서 기준 답변을 사람이 읽기 좋은 형태로 출력합니다. `local-ai assistant`는 문서 질문, 검색, 폴더 색인, Agent dry-run을 한 자리에서 쓰는 통합 REPL입니다.

```bash
local-ai assist "내 문서 기준으로 JWT 인증 흐름 설명해줘"
local-ai assistant
```

`local-ai assistant` 안에서는 일반 문장을 입력하면 문서 기반 답변을 받고, 아래 명령도 사용할 수 있습니다.

```text
/ask <질문>
/search <검색어>
/docs
/stats
/roots
/index-preview <folder>
/index <folder>
/agent <지시>
/runs
/run <id>
/actions <id>
/dry-run <id>
/approve <id>
/execute <id>
/results <id>
/shell-policy
/shell-dry-run <command>
/summary
/status
/next
/quit
```

```bash
local-ai docs --source-type upload
local-ai docs --file-type md
local-ai docs --file-type html
local-ai docs --file-type pdf
local-ai docs --source-type upload --file-type md --query backend
curl "http://127.0.0.1:8000/documents?source_type=upload&file_type=md&query=backend"
```

문서 저장소 상태와 정합성은 아래 read-only endpoint로 확인할 수 있습니다. `repair-preview`는 실제 수정 없이 필요한 조치 후보만 보여줍니다.

- `GET /documents/stats`
- `GET /documents/integrity`
- `GET /documents/repair-preview`

```bash
curl http://127.0.0.1:8000/documents/stats
curl http://127.0.0.1:8000/documents/integrity
curl http://127.0.0.1:8000/documents/repair-preview
local-ai stats
local-ai integrity
local-ai repair-preview
```

현재 환경에서 사용할 수 있는 문서 타입과 optional dependency 준비 상태는 다음 명령으로 확인합니다.

```bash
local-ai document-types
curl http://127.0.0.1:8000/documents/supported-types
```

## LOCAL_API_KEY

`LOCAL_API_KEY`를 설정하면 보호 endpoint는 `X-API-Key` 헤더를 요구합니다. 외부 UI가 token 입력칸에서 `Authorization: Bearer <token>` 형태로만 보낼 경우도 같은 키로 허용합니다.

보호 endpoint:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder`
- `DELETE /documents/{document_id}`
- `POST /search`
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

```bash
export LOCAL_API_KEY=change-me
curl -X POST http://127.0.0.1:8000/ask \
  -H "X-API-Key: change-me" \
  -H "Content-Type: application/json" \
  -d '{"question":"안녕"}'
```

Bearer token 입력만 지원하는 로컬 UI에는 `LOCAL_API_KEY` 값을 그대로 token 칸에 넣으면 됩니다. 서버는 아래 요청도 같은 키로 인정합니다.

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Authorization: Bearer change-me" \
  -H "Content-Type: application/json" \
  -d '{"question":"안녕"}'
```

보안 운영 기준과 GitHub 공개 전 체크리스트는 [SECURITY.md](SECURITY.md)에 정리되어 있습니다.

## Continuation Status

작업이 끝날 때마다 차수, 다음 안전 작업, Recommended Next Model을 확인할 수 있습니다.

```bash
curl http://127.0.0.1:8000/project/status
curl http://127.0.0.1:8000/project/next
curl -H "X-API-Key: change-me" http://127.0.0.1:8000/project/shell-policy
local-ai status
local-ai next
```

`local-ai status`는 완료 차수와 현재 차수를 함께 보여주고, `local-ai next`는 다음에 Codex가 계속 진행하기 좋은 안전 작업만 요약합니다. `project/status`와 `project/next`는 조회 전용 continuation endpoint이고, shell dry-run 정책 endpoint는 명령 후보가 포함될 수 있어 `LOCAL_API_KEY` 설정 시 보호됩니다. shell 실행, 파일 수정/삭제, 브라우저 interaction, 배포, fine-tuning 실행은 여전히 별도 승인 전 보류 항목으로 표시됩니다.

## Local Assistant Automation

`local-ai assistant`는 세션 안에서 짧은 요약과 온보딩 상태를 확인할 수 있습니다.

- `/summary`: 현재 assistant 세션의 질문 수, 명령 수, 최근 질문, 사용한 source를 메모리 안에서 요약합니다. 파일 저장이나 fine-tuning은 수행하지 않습니다.
- `/roots`: `AGENT_ALLOWED_ROOTS` 기준으로 Agent가 read-only 접근할 수 있는 root와 존재 여부를 보여줍니다.
- `/shell-policy`: shell dry-run allowlist와 blocked token을 보여줍니다.
- `/shell-dry-run <command>`: 실제 shell 실행 없이 명령이 허용 후보인지 정책 판단만 반환합니다.
- `/status`, `/next`: 차수와 다음 안전 작업을 REPL 안에서 확인합니다.

CLI에서도 같은 내용을 확인할 수 있습니다.

```bash
local-ai roots
local-ai shell-policy
local-ai shell-dry-run "pwd"
```

## UI Bridge Assistant API

브라우저 기반 로컬 비서 UI는 `/assistant/ping`으로 연결/token 상태를 빠르게 확인하고, `/assistant/config`로 secret 없이 안전 설정을 읽고, `/assistant/dashboard`로 첫 화면 카드를 구성할 수 있습니다. 시작 시에는 `/assistant/startup`으로 `ping`, `config`, `dashboard`, `ui_contract`를 한 번에 읽을 수 있고, project root가 준비되면 `/assistant/bootstrap`으로 기능, 상태, project root 검증, 최근 세션 목록, UI 힌트를 받을 수 있습니다. 실제 메시지는 기능별 endpoint를 직접 조합하지 않고 `/assistant/message` 하나로 보낼 수 있습니다.

브라우저 UI를 붙이는 기본 순서는 아래처럼 잡으면 됩니다.

1. `GET /assistant/startup`: token, CORS, 모델, dashboard, UI contract snapshot을 한 번에 읽습니다.
2. `POST /assistant/bootstrap`: 사용자가 입력한 project root와 최근 session 상태를 확인합니다.
3. `POST /assistant/action-preview`: 메시지를 보내기 전에 intent, 위험도, 필요한 입력값을 preview합니다.
4. `POST /assistant/message`: 사용자가 확인한 메시지를 보내고 `ui.response_type` 기준으로 렌더링합니다.
5. `GET /assistant/sessions/{session_id}/messages`: 긴 대화 기록은 paging으로 가져옵니다.

수동 QA 기준은 [docs/UI_QA_CHECKLIST.md](docs/UI_QA_CHECKLIST.md), 응답 예시는 [docs/UI_BRIDGE_EXAMPLES.md](docs/UI_BRIDGE_EXAMPLES.md)를 기준으로 확인합니다.

```bash
curl http://127.0.0.1:8000/assistant/ping \
  -H "Authorization: Bearer change-me"

curl http://127.0.0.1:8000/assistant/config \
  -H "Authorization: Bearer change-me"

curl http://127.0.0.1:8000/assistant/dashboard \
  -H "Authorization: Bearer change-me"

curl http://127.0.0.1:8000/assistant/startup \
  -H "Authorization: Bearer change-me"
```

```bash
curl -X POST http://127.0.0.1:8000/assistant/bootstrap \
  -H "Authorization: Bearer change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "project_root":"/Users/juyoung/local-ai-server",
    "include_sessions":true,
    "sessions_limit":10
  }'
```

```bash
curl -X POST http://127.0.0.1:8000/assistant/message \
  -H "Authorization: Bearer change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "message":"내 문서 기준으로 JWT 설명해줘",
    "project_root":"/Users/juyoung/local-ai-server",
    "mode":"auto"
  }'
```

지원 endpoint:

- `GET /assistant/capabilities`: UI가 사용할 수 있는 기능과 안전 기본값 확인
- `POST /assistant/action-preview`: 실제 실행 없이 메시지 intent, 위험도, 필요 입력값 preview
- `GET /assistant/ping`: UI 연결, token, 로컬 API ready 상태 빠른 확인
- `GET /assistant/config`: secret 없이 CORS, allowed roots, 모델명, 저장소, 안전 설정 확인
- `GET /assistant/ui-contract`: UI 시작 순서, refresh endpoint, 메시지 흐름, 응답 타입, 차단 기능 계약 요약
- `GET /assistant/startup`: UI 초기 렌더링용 ping/config/dashboard/ui-contract read-only snapshot
- `GET /assistant/status`: UI 첫 화면용 문서/세션/integrity/안전 상태 요약
- `GET /assistant/dashboard`: UI 카드용 문서/세션/integrity/연결 상태와 최근 세션 요약
- `POST /assistant/bootstrap`: UI 초기화용 capabilities/status/project root/sessions/UI 힌트 통합 응답
- `POST /assistant/sessions`: 대화 세션 생성
- `GET /assistant/sessions`: 최근 대화 세션 목록 조회
- `GET /assistant/sessions/{session_id}`: 세션 기록 조회
- `GET /assistant/sessions/{session_id}/messages`: UI 대화 기록 paging 조회
- `POST /assistant/message`: 입력 메시지를 RAG/search/index preview/agent plan/shell dry-run으로 안전 분기
- `POST /assistant/project-root/validate`: 화면에 입력한 project root 검증

`/assistant/message` 응답에는 UI가 바로 렌더링에 참고할 수 있는 `ui.response_type`, `ui.severity`, `ui.primary_text`, `ui.display` 힌트가 포함됩니다. 폴더 색인은 preview까지만 수행하고, shell은 dry-run 정책 판단만 반환합니다. 브라우저 클릭, 파일 수정/삭제, 실제 shell 실행은 하지 않습니다.

브라우저 UI에서 호출할 수 있도록 기본 CORS 허용 origin은 아래와 같습니다.

```env
LOCAL_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

## Rate Limit

보호 endpoint에는 process-local in-memory rate limit이 적용됩니다. 기본값은 분당 `120`회입니다.

```bash
export LOCAL_RATE_LIMIT_PER_MINUTE=120
```

`LOCAL_RATE_LIMIT_PER_MINUTE=0`으로 설정하면 rate limit을 비활성화합니다. 이 제한은 단일 프로세스 메모리 기준이므로 여러 worker나 여러 서버 인스턴스를 운영하는 공개 서비스용 분산 rate limit은 아닙니다.

## Agent API

실행형 Agent의 첫 단계로 계획, 승인, read-only 실행 API를 제공합니다.

```bash
curl -X POST http://127.0.0.1:8000/agent/plan \
  -H "Content-Type: application/json" \
  -d '{"instruction":"GitHub 웹 열고 내 폴더도 열어줘"}'
```

CLI:

```bash
local-ai agent-plan "GitHub 웹 열고 내 폴더도 열어줘"
local-ai agent-runs
local-ai agent-run 1
local-ai agent-actions 1
local-ai agent-dry-run 1
local-ai agent-results 1
local-ai agent-approve 1
local-ai agent-reject 1
local-ai agent-execute 1
local-ai agent-shell
```

현재 이 API는 요청을 `browser`, `web_search`, `file`, `shell`, `rag` action 후보로 분류하고 위험도, 승인 필요 여부, 실행 상태를 반환합니다. `agent-dry-run`은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 실행 전 정책 판단만 기록합니다. `agent-approve`는 상태를 `approved_pending_execution`으로 바꾸고, `agent-execute`는 승인된 run만 실행 시도합니다.

`agent-shell`은 Codex/Claude CLI처럼 터미널을 열어 사용하는 얇은 대화형 CLI입니다. 일반 문장을 입력하면 agent plan을 만들고, `/runs`, `/run 1`, `/actions 1`, `/dry-run 1`, `/approve 1`, `/execute 1`, `/results 1` 같은 명령으로 같은 FastAPI 백엔드를 호출합니다.

기본값에서는 `AGENT_EXECUTION_ENABLED=false`라 모든 실제 실행이 차단됩니다. `true`로 바꿔도 현재 v1 실행 엔진은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원합니다. 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자는 차단합니다. 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 아직 수행하지 않습니다.

```bash
export AGENT_EXECUTION_ENABLED=true
export AGENT_ALLOWED_ROOTS=/Users/me/project,/Users/me/notes
export AGENT_WEB_FETCH_ENABLED=false
export AGENT_WEB_FETCH_MAX_BYTES=100000
export AGENT_FILE_PREVIEW_MAX_BYTES=50000
export AGENT_FILE_PREVIEW_EXTENSIONS=.txt,.md,.py,.json,.yaml,.yml,.toml,.csv,.html,.htm,.log
```

## SFT Export

아직 fine-tuning을 수행하지 않습니다. 미래 LoRA/QLoRA 학습을 위한 JSONL 데이터만 준비합니다.

```bash
python scripts/export_sft_data.py --output data/sft_dataset.jsonl
```

출력 형식:

```json
{"messages":[{"role":"system","content":"You are a helpful local AI assistant."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}]}
```

## Feedback 조회

저장된 피드백을 read-only로 확인할 수 있습니다.

```bash
local-ai feedbacks --limit 20 --offset 0
local-ai feedbacks --rating bad --limit 20 --offset 0
local-ai feedbacks --chat-log-id 9 --limit 20 --offset 0
```

HTTP API:

```bash
curl "http://127.0.0.1:8000/feedback?limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?rating=bad&limit=20&offset=0"
curl "http://127.0.0.1:8000/feedback?chat_log_id=9&limit=20&offset=0"
```

## 저장소 상태 점검

SQLite와 Chroma의 현재 상태를 read-only로 확인할 수 있습니다.

```bash
local-ai stats
local-ai integrity
local-ai repair-preview
```

`local-ai stats` 확인 항목:

- 문서 수
- chunk 수
- chat log 수
- feedback 수
- Chroma vector 수
- SQLite에는 기록되어 있지만 저장 파일이 없는 문서 목록

`local-ai integrity` 확인 항목:

- SQLite chunk 수와 Chroma vector 수 일치 여부
- SQLite에는 chunk가 있지만 Chroma vector가 없는 항목
- Chroma에는 vector가 있지만 SQLite chunk가 없는 orphan vector
- 저장 파일 누락 여부

현재 integrity 기능은 read-only dry-run입니다. 실제 repair/delete는 수행하지 않습니다.

`local-ai repair-preview`는 integrity 결과를 기반으로 필요한 복구 후보를 미리 보여줍니다. 이 명령도 read-only이며 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않습니다.

## 운영 로그와 저장공간

운영 로그, 저장공간 점검, 백업 기준은 [docs/OPERATIONS.md](docs/OPERATIONS.md)에 정리되어 있습니다.

핵심 원칙:

- 기본 운영은 `uvicorn` stdout/stderr 로그를 사용합니다.
- 질문, 답변, 문서 원문, `LOCAL_API_KEY`는 일반 운영 로그에 남기지 않습니다.
- 파일 로그가 필요하면 `data/logs/` 아래에 두며 Git에는 포함하지 않습니다.
- 실제 repair/delete/rebuild나 운영 DB 복구는 사용자 승인 후 진행합니다.

```bash
mkdir -p data/logs
uvicorn app.main:app --host 127.0.0.1 --port 8000 >> data/logs/server.log 2>&1
```

## Chunk 페이지 조회

문서 상세 전체를 한 번에 받지 않고 chunk만 페이지 단위로 확인할 수 있습니다.

```bash
local-ai chunks 1 --limit 20 --offset 0
```

HTTP API:

```bash
curl "http://127.0.0.1:8000/documents/1/chunks?limit=20&offset=0"
```

## 테스트

```bash
pytest
```

## E2E Smoke Test

서버와 Ollama 모델이 실행 중일 때 임시 Markdown 문서로 `health → upload → search → ask-with-docs → feedback → stats` 흐름을 확인할 수 있습니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000
```

`LOCAL_API_KEY`가 설정되어 있으면 smoke test도 자동으로 `X-API-Key` 헤더를 보냅니다. 이 스크립트는 테스트용 문서를 업로드하므로 SQLite, Chroma, `data/uploads/`에 테스트 데이터가 추가됩니다. 자동 삭제는 수행하지 않습니다.

## GitHub 공개 전 보안 점검

로컬 데이터와 secret 후보가 공개 대상에 섞여 있는지 read-only로 점검할 수 있습니다.

```bash
python scripts/public_release_check.py --root .
python scripts/public_release_check.py --root . --json
```

현재 로컬 DB, Chroma index, 업로드 파일이 있으면 이 스크립트는 실패 코드와 함께 항목을 출력합니다. 삭제는 수행하지 않으며, 공개 전 `.gitignore`와 실제 포함 파일을 확인하기 위한 안전장치입니다.

## 실제 RAG 검증 상태

현재 로컬 환경에서 아래 흐름을 확인했습니다.

- `local-ai doctor`: `llm_model_ready=true`, `embedding_model_ready=true`
- `local-ai stats`: SQLite/Chroma 저장 상태 확인 성공
- `local-ai integrity`: SQLite/Chroma 정합성 점검 성공
- `local-ai repair-preview`: repair action 미리보기 성공
- `local-ai document-types`: 문서 타입별 사용 가능 여부 확인 성공
- `local-ai chunks 1 --limit 5 --offset 0`: chunk 페이지 조회 성공
- `local-ai logs --limit 2 --offset 0`: chat log 목록 조회 성공
- `local-ai logs --mode rag --query JWT --limit 3 --offset 0`: chat log 필터 조회 성공
- `local-ai log 9`: chat log 상세 조회 성공
- `local-ai feedbacks --limit 5 --offset 0`: feedback 목록 조회 성공
- `local-ai docs --source-type upload --file-type md --query backend`: 문서 목록 필터 조회 성공
- `local-ai index-preview /tmp/local-ai-preview`: read-only 폴더 색인 preview 성공, stats 변경 없음
- `POST /documents/index-folder-preview`: `embedding_batch_size`, `embedding_batches_estimated` 응답 contract 확인 성공
- `POST /documents/index-folder`: 파일별 `indexed_files`, `skipped_file_details` 응답 contract 확인 성공
- `local-ai document-types`: PDF/DOCX optional dependency 준비 상태 확인 성공
- `local-ai upload /tmp/local-ai-documents/jwt-docx-notes.docx`: DOCX 텍스트 추출, embedding, Chroma 저장 성공
- `local-ai upload /tmp/local-ai-documents/jwt-pdf-notes.pdf`: PDF 텍스트 추출, embedding, Chroma 저장 성공
- `local-ai search "DOCX Authorization header"`: DOCX chunk 검색 성공
- `local-ai search "PDF refresh token local ai server"`: PDF chunk 검색 성공
- `local-ai ask-docs "내 문서 기준으로 access token 전달 방식..."`: DOCX/PDF source 포함 RAG 답변 성공
- `CHUNK_SIZE=120 CHUNK_OVERLAP=20 EMBEDDING_BATCH_SIZE=2` 환경에서 `batch-notes.txt` 업로드: 22개 chunk embedding 및 Chroma 저장 성공
- `local-ai search "batch Authorization header access token"`: batch 업로드 문서 검색 성공
- `local-ai upload /tmp/local-ai-smoke/backend-notes.md`: 업로드 및 chunk 저장 성공
- `local-ai search "JWT 인증 흐름"`: Chroma 검색 성공
- `local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름..."`: sources 포함 RAG 답변 성공
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000`: 임시 Markdown 문서 기반 API smoke test 가능
- `local-ai agent-plan "GitHub 웹 열고 내 폴더도 열어줘"`: 실행형 Agent 계획 생성 가능

`llama3.2`가 문서 밖 코드나 링크를 만들 수 있어, RAG 답변에는 보수적인 guard가 들어 있습니다. 코드 블록, 외부 URL, 문서에 없는 보안 세부사항, 추측성 표현이 감지되면 문서 기반 fallback 답변으로 대체합니다.

문서 업로드는 SQLite write transaction이 오래 유지되지 않도록, Ollama embedding 생성 후 짧게 DB write를 수행하는 흐름으로 조정했습니다.
여러 chunk embedding은 `EMBEDDING_BATCH_SIZE` 단위로 Ollama `/api/embed`에 묶어서 요청합니다. 기본값은 `8`입니다.
일시적인 embedding 실패는 `EMBEDDING_MAX_RETRIES`만큼 batch 단위로 재시도합니다. 기본값은 `2`입니다.
Chroma `PersistentClient`는 요청마다 새로 만들지 않고 프로세스 안에서 공유해 동시 요청 시 client 초기화 충돌을 줄입니다.
DB/Chroma 저장 단계에서 오류가 나면 SQLite 변경은 rollback하고 명확한 색인 오류를 반환합니다.

## Troubleshooting

### Ollama에 연결할 수 없습니다

- `ollama serve`가 실행 중인지 확인합니다.
- `.env` 또는 환경변수의 `OLLAMA_BASE_URL`이 맞는지 확인합니다.
- 기본값은 `http://localhost:11434`입니다.

### 모델을 찾을 수 없습니다

먼저 현재 준비 상태를 확인합니다.

```bash
local-ai doctor
```

`embedding_model_ready`가 `false`라면 embedding 모델이 아직 준비되지 않은 상태입니다.

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 업로드가 실패합니다

- 기본 지원은 `.txt`, `.md`, `.html`, `.htm`입니다.
- HTML은 UTF-8 파일만 처리하며, JavaScript 렌더링 결과는 추출하지 않습니다.
- `.pdf`, `.docx`에서 optional dependency 오류가 나오면 `pip install -e ".[dev,documents]"`를 실행합니다.
- UTF-8 텍스트 파일만 지원합니다.

### 401 응답이 나옵니다

- `LOCAL_API_KEY`가 설정되어 있으면 `X-API-Key` 헤더를 보내야 합니다.

## 현재 한계

- PDF/DOCX는 optional dependency 설치 시 텍스트 추출을 지원합니다. 스캔 이미지 기반 PDF OCR은 아직 지원하지 않습니다.
- HTML/HTM은 표준 라이브러리 기반 텍스트 추출을 지원하지만, JavaScript 렌더링 결과나 동적 페이지 크롤링은 지원하지 않습니다.
- Chroma와 SQLite 동기화 복구는 read-only 점검과 repair preview까지만 지원합니다. 실제 repair/rebuild는 아직 수행하지 않습니다.
- 실행형 Agent는 계획, 승인, read-only 실행 엔진 v1 단계입니다. 실제 웹 이동, 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 아직 수행하지 않습니다.
- 실행 엔진 v1은 승인된 run에 대해 허용 root 안의 폴더 목록 조회와 텍스트 파일 내용 preview만 지원합니다. 웹 fetch는 `AGENT_WEB_FETCH_ENABLED=true`와 명시 URL이 있을 때만 read-only로 동작하며, `AGENT_WEB_FETCH_MAX_BYTES` 이후 응답을 자릅니다.
- embedding은 batch 처리되고 preview에서 예상 batch 수를 볼 수 있지만, 매우 큰 문서의 실시간 진행률 표시는 아직 없습니다.
- 자동 로그 rotation은 아직 구현하지 않았고, 운영 로그 정책은 문서로만 제공합니다.
- 인증은 로컬 API key 수준이며, 다중 사용자 권한 관리는 없습니다.
- 보호 endpoint에는 process-local in-memory rate limit이 적용됩니다. 다중 worker/분산 환경용 rate limit은 아직 지원하지 않습니다.
- HTTPS termination은 애플리케이션에서 직접 제공하지 않으며, 외부 공개가 필요하면 reverse proxy와 TLS 설정을 별도로 검토해야 합니다.

## 배포 상태

- 현재 구현은 로컬 실행 기준입니다.
- 외부 클라우드 배포는 구현하지 않았습니다.
- 외부 클라우드 credential, API key, DB password는 사용하지 않습니다.
