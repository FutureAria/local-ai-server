# WORKLOG

## 2026-05-20

### 완료

- `AGENTS.md` 프로젝트 규칙 작성
- FastAPI 백엔드 구조 생성
- Ollama local chat API client 구현
- Ollama local embedding API client 구현
- SQLite DB 모델 및 초기화 구현
- Chroma vector store 구현
- `.txt`, `.md` 문서 로더 구현
- 표준 라이브러리 기반 `.html`, `.htm` 문서 로더 구현
- optional dependency 기반 `.pdf`, `.docx` 문서 로더 구현
- optional dependency 설치 후 실제 PDF/DOCX 업로드, 검색, RAG 검증 완료
- 문서 업로드 중 SQLite write lock을 줄이도록 embedding을 DB write 전에 수행하게 개선
- `EMBEDDING_BATCH_SIZE` 설정과 Ollama `/api/embed` batch 호출 기반 대용량 문서 embedding 개선
- `EMBEDDING_MAX_RETRIES` 기반 embedding batch 재시도 추가
- Chroma `PersistentClient`를 service dependency에서 singleton으로 공유해 동시 첫 요청 500 오류 수정
- DB/Chroma 저장 단계 실패 시 SQLite rollback과 명확한 `DocumentIndexingError` 반환 추가
- character-based chunking 구현
- 문서 업로드, 문서 목록, 문서 상세, 문서 삭제 API 구현
- 로컬 폴더 색인 API 구현
- 로컬 폴더 색인 응답에 파일별 성공/스킵 상세 추가
- search API 구현
- RAG ask API 구현
- feedback API 구현
- Typer CLI 구현
- SFT JSONL export 스크립트 구현
- Ollama 준비 상태 점검용 `/health/ollama`와 `local-ai doctor` 추가
- SQLite/Chroma 상태 점검용 `/documents/stats`와 `local-ai stats` 추가
- SQLite/Chroma 정합성 dry-run 점검용 `/documents/integrity`와 `local-ai integrity` 추가
- SQLite/Chroma repair 후보 미리보기용 `/documents/repair-preview`와 `local-ai repair-preview` 추가
- 실제 저장 전 폴더 색인 read-only preview용 `/documents/index-folder-preview`와 `local-ai index-preview` 추가
- 폴더 색인 preview 응답에 예상 embedding batch 수 추가
- 문서 타입/optional dependency 점검용 `/documents/supported-types`와 `local-ai document-types` 추가
- 문서 chunk 페이지 조회용 `/documents/{document_id}/chunks`와 `local-ai chunks` 추가
- chat log 조회용 `/chat-logs`, `/chat-logs/{chat_log_id}`와 `local-ai logs`, `local-ai log` 추가
- feedback 목록 조회용 `GET /feedback`와 `local-ai feedbacks` 추가
- 문서 목록 필터용 `/documents?source_type=&file_type=&query=`와 `local-ai docs --source-type --file-type --query` 추가
- API 계약 문서 `docs/API.md` 추가
- 운영 로그/저장공간/백업 기준 문서 `docs/OPERATIONS.md` 추가
- 최종/포트폴리오 요약 문서 `docs/PROJECT_SUMMARY.md` 추가
- Claude Sonnet 문서 정합성 리뷰용 handoff `docs/CLAUDE_REVIEW_HANDOFF.md` 추가
- 로컬 운영/공개 전 보안 기준 문서 `SECURITY.md` 추가
- `data/logs/` 운영 로그 디렉터리와 `.gitignore` 로그 제외 규칙 추가
- README 실행 문서와 포트폴리오용 개발 배경/기술 선택/핵심 구현 포인트 정리
- pytest 테스트 추가

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest` | `169 passed` |
| `.venv/bin/python -m compileall app cli scripts` | 성공 |
| `test -f docs/API.md` | API 문서 존재 확인 |
| `test -f docs/CLAUDE_REVIEW_HANDOFF.md` | Claude 리뷰 handoff 문서 존재 확인 |
| `test -f docs/OPERATIONS.md` | 운영 문서 존재 확인 |
| `test -f docs/PROJECT_SUMMARY.md` | 프로젝트 요약 문서 존재 확인 |
| `test -f SECURITY.md` | 보안 문서 존재 확인 |
| `.venv/bin/pip install -e '.[dev,documents]'` | 성공 |
| `curl http://127.0.0.1:8000/health` | `200 OK` |
| `curl http://127.0.0.1:8000/health/ollama` | Ollama/model readiness 확인 가능 |
| `curl -X POST /ask` | Ollama `llama3.2` 실제 호출 성공 |
| `.venv/bin/local-ai health` | 성공 |
| `.venv/bin/local-ai doctor` | Ollama/model readiness 확인 가능 |
| `.venv/bin/local-ai docs` | 성공 |
| `.venv/bin/local-ai stats` | SQLite/Chroma 상태 확인 성공 |
| `.venv/bin/local-ai integrity` | SQLite/Chroma 정합성 dry-run 확인 성공 |
| `.venv/bin/local-ai repair-preview` | repair action 미리보기 성공 |
| `.venv/bin/local-ai document-types` | 문서 타입별 사용 가능 여부 확인 성공 |
| `curl http://127.0.0.1:8000/documents/supported-types` | 문서 타입별 사용 가능 여부 확인 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-documents/jwt-docx-notes.docx` | DOCX 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-documents/jwt-pdf-notes.pdf` | PDF 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "DOCX Authorization header" --top-k 5` | DOCX chunk 검색 성공 |
| `.venv/bin/local-ai search "PDF refresh token local ai server" --top-k 5` | PDF chunk 검색 성공 |
| `.venv/bin/local-ai ask-docs "내 문서 기준으로 access token 전달 방식..." --top-k 3` | DOCX/PDF source 포함 RAG 답변 성공 |
| `CHUNK_SIZE=120 CHUNK_OVERLAP=20 EMBEDDING_BATCH_SIZE=2 .venv/bin/uvicorn ...` | batch embedding 검증 서버 실행 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-batch/batch-notes.txt` | 22개 chunk 업로드, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "batch Authorization header access token" --top-k 5` | batch 업로드 문서 검색 성공 |
| `.venv/bin/local-ai stats` | `documents_count=4`, `chunks_count=25`, `chroma_vectors_count=25` |
| `.venv/bin/local-ai integrity` | `status=ok` |
| `search/stats/integrity 동시 호출` | Chroma singleton 적용 후 모두 성공 |
| `tests/test_document_service.py` | vector store 실패 시 SQLite document/chunk rollback 확인 |
| `.venv/bin/local-ai index-preview /tmp/local-ai-preview` | read-only preview 성공, `files_count=2`, `chunks_estimated=2`, stats 변경 없음 |
| `curl -X POST /documents/index-folder-preview` | read-only preview endpoint 성공 |
| `tests/test_document_service.py` | preview의 `embedding_batch_size`, `embedding_batches_estimated` 계산 확인 |
| `tests/test_document_service.py` | 실제 폴더 색인 응답의 `indexed_files`, `skipped_file_details` 확인 |
| `tests/test_api_contracts.py` | `/documents/index-folder` 파일별 상세 응답 contract 확인 |
| `.venv/bin/local-ai chunks 1 --limit 5 --offset 0` | chunk 페이지 조회 성공 |
| `.venv/bin/local-ai logs --limit 2 --offset 0` | chat log 목록 조회 성공 |
| `.venv/bin/local-ai logs --mode rag --query JWT --limit 3 --offset 0` | chat log 필터 조회 성공 |
| `.venv/bin/local-ai log 9` | chat log 상세 조회 성공 |
| `.venv/bin/local-ai feedbacks --limit 5 --offset 0` | feedback 목록 조회 성공 |
| `curl 'http://127.0.0.1:8000/documents?source_type=upload&file_type=md&query=backend'` | 문서 목록 필터 조회 성공 |
| `.venv/bin/local-ai docs --source-type upload --file-type md --query backend` | 문서 목록 필터 조회 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-smoke/backend-notes.md` | 문서 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "JWT 인증 흐름"` | Chroma 검색 결과 반환 성공 |
| `.venv/bin/local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름..."` | RAG 답변 및 sources 반환 성공 |

### 확인한 로컬 Ollama 상태

- Ollama server: 실행 중
- 사용 가능 모델:
  - `llama3.2:latest`
  - `codellama:latest`
  - `nomic-embed-text:latest`
- `local-ai doctor` 기준:
  - `llm_model_ready=true`
  - `embedding_model_ready=true`

### 남은 작업

- 실제 사용자 문서로 upload/search/ask-with-docs 검증
- 필요하면 OCR loader 추가
- 필요하면 HTML JavaScript 렌더링/크롤링 범위 결정
- Chroma/SQLite 실제 복구 명령 추가. 단 실제 repair/delete/rebuild는 사용자 승인 필요
- 필요하면 자동 로그 rotation 구현. 단 실제 삭제/압축 자동화 정책은 사용자 승인 후 진행

### RAG 품질 보강

- `llama3.2`가 문서 밖 코드, 링크, 보안 세부사항을 만들 수 있어 RAG prompt를 강화함.
- 코드 블록, 외부 URL, 문서에 없는 보안 키워드, 추측성 표현이 감지되면 보수적인 문서 기반 fallback 답변으로 대체하는 guard를 추가함.
- 관련 테스트를 `tests/test_rag_service.py`에 추가함.

### Integrity dry-run

- `/documents/integrity`는 read-only 점검만 수행한다.
- 실제 repair/delete는 수행하지 않는다.
- 확인 항목:
  - 저장 파일 누락
  - SQLite chunk는 있지만 Chroma vector가 없는 항목
  - Chroma vector는 있지만 SQLite chunk가 없는 orphan vector

### Repair preview

- `/documents/repair-preview`는 integrity 결과를 기반으로 필요한 action 후보만 반환한다.
- 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않는다.
- 현재 로컬 상태에서는 `actions_count=0`이다.

### Folder index preview

- `/documents/index-folder-preview`는 실제 색인 전에 대상 파일, skip 파일, 예상 chunk 수, token estimate를 read-only로 반환한다.
- 전체 응답에는 `embedding_batch_size`, `embedding_batches_estimated`를 포함한다.
- 각 file 항목에는 파일별 `embedding_batches_estimated`를 포함한다.
- CLI는 `local-ai index-preview <folder>`를 제공한다.
- 원본 파일 수정, SQLite 저장, Ollama embedding 생성, Chroma 저장은 수행하지 않는다.
- `LOCAL_API_KEY`가 설정되어 있으면 실제 색인 API와 동일하게 `X-API-Key` 보호를 적용한다.

### Folder index result details

- `/documents/index-folder` 응답에 `indexed_files`와 `skipped_file_details`를 추가했다.
- `indexed_files`는 `path`, `document_id`, `filename`, `file_type`, `chunks_created`를 반환한다.
- `skipped_file_details`는 `path`, `filename`, `reason`을 반환한다.
- 기존 `indexed_documents`, `skipped_files`, `chunks_created`, `document_ids` 필드는 유지한다.

### Chat log 조회

- `/chat-logs`는 질문/답변 preview 중심의 목록을 반환한다.
- `/chat-logs`는 `mode=direct|rag`, `query=<keyword>` 필터를 지원한다.
- `/chat-logs/{chat_log_id}`는 전체 질문/답변/source를 반환한다.
- CLI는 `local-ai logs`, `local-ai log <id>`를 제공한다.

### Feedback 조회

- `GET /feedback`는 feedback preview 목록을 반환한다.
- `rating=good|bad|neutral`, `chat_log_id=<id>` 필터를 지원한다.
- CLI는 `local-ai feedbacks`를 제공한다.

### 문서 목록 필터

- `GET /documents`는 `source_type=upload|folder`, `file_type=txt|md|pdf|docx|html`, `query=<keyword>` 필터를 지원한다.
- `query`는 filename과 stored path 기준으로 검색한다.
- CLI는 `local-ai docs --source-type upload --file-type md --query backend`를 제공한다.

### PDF/DOCX loader

- `.pdf`, `.docx` 확장자를 문서 업로드와 폴더 색인 대상에 포함했다.
- `pypdf`, `python-docx`는 optional dependency로 분리했다.
- optional dependency가 없으면 명확한 `pip install -e '.[documents]'` 안내 메시지를 반환한다.
- `/documents/supported-types`와 `local-ai document-types`로 현재 환경의 문서 타입별 사용 가능 여부를 확인할 수 있다.
- 현재 venv에는 `pypdf`, `python-docx`, `lxml` 설치 완료 상태다.
- 실제 DOCX/PDF 샘플 업로드, 검색, RAG source 반환을 확인했다.
- 스캔 이미지 기반 PDF OCR은 지원하지 않는다.

### HTML/HTM loader

- `.html`, `.htm` 확장자를 문서 업로드와 폴더 색인 대상에 포함했다.
- Python 표준 라이브러리 `html.parser` 기반으로 UTF-8 HTML에서 본문 텍스트를 추출한다.
- `head`, `script`, `style`, `noscript` 내용은 색인 대상에서 제외한다.
- `.htm`과 `.html`은 SQLite `file_type=html`로 정규화한다.
- JavaScript 렌더링 결과, 외부 페이지 fetch, 브라우저 interaction은 지원하지 않는다.

### SQLite write lock / embedding batch 개선

- 기존에는 DB flush 이후 Ollama embedding 호출을 수행해 SQLite write transaction이 길어질 수 있었다.
- 업로드가 겹치면 `sqlite3.OperationalError: database is locked`가 발생할 수 있어, embedding을 DB write 전에 생성하도록 순서를 조정했다.
- DB write 구간은 document/chunk insert와 Chroma 기록 직전 commit으로 짧게 유지한다.
- `EMBEDDING_BATCH_SIZE` 기본값은 `8`이다.
- `EMBEDDING_MAX_RETRIES` 기본값은 `2`이다.
- 여러 chunk embedding은 batch 단위로 Ollama `/api/embed`에 요청한다.
- 일시적인 `OllamaError`는 batch 단위로 재시도하고, 재시도 소진 시 명확한 오류를 반환한다.
- `CHUNK_SIZE=120`, `CHUNK_OVERLAP=20`, `EMBEDDING_BATCH_SIZE=2` 조건에서 22개 chunk 업로드와 검색을 확인했다.
- 동시 첫 요청에서 Chroma client를 여러 개 만들면 `default_tenant`/`bindings` 관련 500 오류가 발생할 수 있어, service dependency가 단일 `VectorStore`를 공유하도록 수정했다.
- DB/Chroma 저장 단계 실패 시 `db.rollback()`을 명시적으로 호출하고 `DocumentIndexingError`를 반환한다.
- vector store 실패 시 SQLite `documents`, `document_chunks`가 남지 않는 테스트를 추가했다.

### 로컬 저장소 / 배포 상태

- 현재 배포: 로컬 실행 기준
- 외부 클라우드 배포: 진행하지 않음
- 외부 LLM API: 사용하지 않음
- 외부 credential: 사용하지 않음
- 로컬 저장 위치:
  - SQLite: `data/local_ai.sqlite3`
  - Chroma: `data/chroma/`
  - 업로드 파일: `data/uploads/`
  - 운영 로그 파일: `data/logs/`

### 운영 로그 / 저장공간 문서

- `docs/OPERATIONS.md`에 로컬 운영 원칙, 저장 위치, 로그 정책, 수동 rotation 예시, 저장공간 점검, 백업 기준, 장애 점검 순서를 정리했다.
- 애플리케이션 코드가 파일 logger를 강제로 만들지는 않는다.
- 파일 로그가 필요하면 `uvicorn ... >> data/logs/server.log 2>&1` 형태로 시작할 수 있게 문서화했다.
- `data/logs/*`는 Git 제외 대상이고, 디렉터리 보존용 `.gitkeep`만 유지한다.

### API 문서

- `docs/API.md`에 endpoint별 요청 예시, 응답 핵심 필드, 보호 endpoint, CLI 대응 관계를 정리했다.
- 실제 repair/delete/rebuild가 수행되지 않는 read-only preview endpoint를 명확히 구분했다.
- CLI는 FastAPI API를 호출하고 비즈니스 로직을 중복 구현하지 않는다는 원칙을 문서화했다.

### Security 문서

- `SECURITY.md`에 로컬 전용 보안 원칙, API key 보호 endpoint, 데이터 저장 위치, 로그 정책, 파일 업로드/색인 보안 기준, RAG 안전 기준, 공개 전 체크리스트를 정리했다.
- 외부 LLM API, 외부 크롤링, browser interaction, 실제 repair/delete/rebuild, Oracle 실제 리소스 작업은 사용자 승인 전 진행하지 않는 고위험 작업으로 명시했다.

### README 포트폴리오 정리

- README 앞부분에 개발 배경, 포트폴리오 관점의 핵심 목표, 기술 선택 이유, 핵심 구현 포인트를 추가했다.
- 구현된 기능과 미구현 기능이 섞이지 않도록 현재 한계와 배포 상태는 별도 섹션으로 유지했다.

### Project summary 문서

- `docs/PROJECT_SUMMARY.md`에 한 줄 소개, 만든 것, 핵심 설계, endpoint 목록, CLI 목록, 실행/테스트 방법, 보안/운영 기준, 현재 한계, 다음 추천 개선을 정리했다.
- 최종 보고나 포트폴리오 제출 시 빠르게 확인할 수 있는 요약 문서 역할을 한다.

### Claude Review Handoff 문서

- `docs/CLAUDE_REVIEW_HANDOFF.md`에 Claude Sonnet이 문서 정합성만 리뷰할 수 있도록 리뷰 목표, 읽을 파일, P0/P1/P2 기준, 금지사항, 출력 형식을 정리했다.
- 이 handoff는 리뷰용이며 코드 수정, 파일 생성, 실제 배포, 외부 API 활성화를 지시하지 않는다.

### 문서 self-check 반영

- `docs/API.md`의 CLI 대응 목록에 `local-ai document-types`를 추가했다.
- README 현재 한계 섹션에 rate limit과 HTTPS termination 미지원 상태를 명시했다.
- `docs/NEXT_CHAT_HANDOFF.md`의 다음 작업을 이미 완료된 README/docs 정합성 점검이 아니라 실제 사용자 문서 E2E 검증과 선택형 개선 후보 중심으로 갱신했다.
- CLI가 FastAPI 백엔드를 호출하는 계약을 mock 기반으로 검증하는 `tests/test_cli.py`를 추가했다.
- `tests/test_security.py`를 확장해 `/ask`, `/ask-with-docs`, `/search`, `/documents/upload`, `/documents/index-folder-preview`, `/documents/index-folder`, `DELETE /documents/{document_id}`, `/feedback` 전체가 `LOCAL_API_KEY` 설정 시 `X-API-Key`를 요구하는지 확인했다.
- `LOCAL_RATE_LIMIT_PER_MINUTE` 기반 process-local in-memory rate limit을 보호 endpoint에 적용했다.
- `tests/test_rate_limiter.py`를 추가해 rate limiter window, 비활성화, API key hash identity를 검증했다.
- `scripts/smoke_test_api.py`를 추가해 실행 중인 서버 기준 `health → upload → search → ask-with-docs → feedback → stats` smoke test를 수행할 수 있게 했다.
- `tests/test_smoke_script.py`를 추가해 smoke script의 API 호출 순서를 mock으로 검증했다.
- `scripts/public_release_check.py`를 추가해 GitHub 공개 전 로컬 데이터와 secret 후보를 read-only로 점검할 수 있게 했다.
- `tests/test_public_release_check.py`를 추가해 `.env`, SQLite, `.env.example`, `.gitkeep` 처리 기준을 검증했다.
- 현재 실제 워크스페이스에서 `python scripts/public_release_check.py --root . --json`는 로컬 SQLite, Chroma, uploads 파일을 공개 전 제외 대상 finding으로 탐지한다. 삭제는 수행하지 않았다.
- 실행형 Agent 계획 API를 추가했다. `/agent/plan`, `/agent/runs`, `/agent/runs/{run_id}`는 요청을 위험도와 승인 필요 action으로 분류/저장/조회한다.
- agent plan 승인/거절 상태 전환 API `/agent/runs/{run_id}/approve`, `/agent/runs/{run_id}/reject`를 추가했다. 승인되어도 실제 실행은 수행하지 않는다.
- agent 실행 엔진 v1과 `/agent/runs/{run_id}/execute`를 추가했다.
- `AGENT_EXECUTION_ENABLED=false` 기본값에서는 실제 실행을 차단한다.
- `AGENT_EXECUTION_ENABLED=true`에서도 v1 실행 엔진은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원한다.
- file preview는 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자를 차단한다.
- `AGENT_WEB_FETCH_MAX_BYTES`로 URL fetch 응답 크기를 제한한다.
- 2차 실행 엔진 A단계로 `/agent/runs/{run_id}/dry-run`, `/agent/runs/{run_id}/actions`를 추가했다.
- dry-run은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 action별 정책 판단만 기록한다.
- `local-ai agent-actions`, `local-ai agent-dry-run`, `local-ai agent-shell` CLI 명령을 추가했다.
- 문서 기반 로컬 비서용 `local-ai assist`와 통합 REPL `local-ai assistant`를 추가했다.
- 차수/다음 작업/Recommended Next Model을 확인하는 `/project/status`, `/project/next`, `local-ai status`, `local-ai next`를 추가했다.
- `local-ai agent-plan`, `local-ai agent-runs`, `local-ai agent-run`, `local-ai agent-results`, `local-ai agent-approve`, `local-ai agent-reject`, `local-ai agent-execute` CLI 명령을 추가했다.
- `tests/test_agent_service.py`, `tests/test_agent_api.py`를 추가했고, `tests/test_security.py`와 `tests/test_cli.py`를 Agent endpoint/CLI까지 확장했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.

### Assistant automation safeguard polish

- assistant REPL에 `/summary`, `/status`, `/next`, `/roots`, `/shell-policy`, `/shell-dry-run <command>` 흐름을 추가했다.
- `local-ai roots`, `local-ai shell-policy`, `local-ai shell-dry-run "pwd"` CLI 명령을 추가했다.
- `/project/shell-policy`와 `/project/shell-dry-run` API를 추가해 shell 실행 전 dry-run 정책 판단만 제공하도록 했다.
- shell dry-run은 allowlist/blocked token 기반으로 `allowed_preview` 또는 `blocked`를 반환하며 실제 명령은 실행하지 않는다.
- `/project/status` 차수를 4차 완료, 5차 수동 로컬 QA/운영 polish 단계로 갱신했다.
- README, `docs/API.md`, `SECURITY.md`, `docs/OPERATIONS.md`, `docs/PROJECT_SUMMARY.md`를 실제 동작과 맞게 갱신했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### Local UI Bearer token 호환

- `LOCAL_API_KEY` 보호 endpoint가 기존 `X-API-Key`와 함께 `Authorization: Bearer <LOCAL_API_KEY>`도 허용하도록 했다.
- 브라우저 기반 로컬 UI의 `Bearer token` 입력칸에 같은 로컬 키를 넣어 붙일 수 있게 했다.
- `tests/test_security.py`에 Bearer header 허용 테스트를 추가했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### UI Bridge Assistant API

- `/assistant/capabilities`, `/assistant/sessions`, `/assistant/sessions/{session_id}`, `/assistant/message`, `/assistant/project-root/validate`를 추가했다.
- `assistant_sessions`, `assistant_messages` SQLite 테이블을 추가해 UI 대화 세션과 메시지를 저장한다.
- `/assistant/message`는 `mode=auto` 기준으로 RAG 답변, 검색, folder index preview, agent plan, shell dry-run으로 안전 분기한다.
- assistant API에서는 실제 폴더 색인 대신 preview만 수행하고, shell은 실제 실행 없이 dry-run 정책 판단만 반환한다.
- `local-ai assistant-capabilities`, `local-ai assistant-session`, `local-ai assistant-message`, `local-ai assistant-root` CLI 명령을 추가했다.
- 테스트 격리를 위해 `tests/conftest.py`에서 로컬 `.env`의 `LOCAL_API_KEY`가 일반 테스트를 오염시키지 않도록 처리했다.

### Browser UI integration support

- `LOCAL_CORS_ORIGINS` 설정을 추가하고 기본값으로 `http://127.0.0.1:5173,http://localhost:5173`을 허용했다.
- FastAPI `CORSMiddleware`를 추가해 로컬 브라우저 UI가 `Authorization`, `Content-Type`, `X-API-Key` header로 API를 호출할 수 있게 했다.
- `GET /assistant/sessions`와 `local-ai assistant-sessions`를 추가해 UI가 최근 대화 세션 목록을 조회할 수 있게 했다.
- `GET /assistant/status`와 `local-ai assistant-status`를 추가해 UI 첫 화면용 문서/세션/integrity/안전 상태를 한 번에 조회할 수 있게 했다.
- CORS preflight와 assistant session list 테스트를 추가했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### UI bootstrap contract

- `POST /assistant/bootstrap`를 추가해 브라우저 UI가 시작 시 capabilities, status, project root 검증, 최근 session 목록, UI 힌트를 한 번에 받을 수 있게 했다.
- `local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server` CLI 명령을 추가했다.
- `/assistant/message` 응답에 `ui.response_type`, `ui.severity`, `ui.primary_text`, `ui.display` 힌트를 추가했다.
- shell 실행, 파일 수정/삭제, 브라우저 interaction은 계속 비활성/보호 상태로 유지했다.
- `/project/status` 차수를 8차 UI bootstrap contract 완료, 9차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `61 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### UI readiness helper APIs

- `GET /assistant/ping`을 추가해 브라우저 UI가 token/header/server 연결 상태를 가볍게 확인할 수 있게 했다.
- `GET /assistant/config`를 추가해 CORS origin, allowed roots, 모델명, 저장소, 안전 설정, rate limit을 secret 없이 조회할 수 있게 했다.
- `GET /assistant/dashboard`를 추가해 문서/세션/integrity/연결 상태 카드와 최근 세션을 UI 카드 구조로 반환한다.
- `local-ai assistant-ping`, `local-ai assistant-config`, `local-ai assistant-dashboard` CLI 명령을 추가했다.
- `/project/status` 차수를 9차 UI readiness helper APIs 완료, 10차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `67 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant message paging

- `GET /assistant/sessions/{session_id}/messages`를 추가해 UI가 긴 대화 기록을 paging으로 조회할 수 있게 했다.
- `local-ai assistant-messages <session_id> --limit 50 --offset 0` CLI 명령을 추가했다.
- `/project/status` 차수를 10차 Assistant message paging 완료, 11차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `68 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant action preview

- `POST /assistant/action-preview`를 추가해 UI가 메시지 전송 전 intent, 추천 endpoint, 위험도, 필요한 입력값을 preview할 수 있게 했다.
- 이 endpoint는 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.
- `local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server` CLI 명령을 추가했다.
- `/project/status` 차수를 11차 Assistant action preview 완료, 12차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `70 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant UI contract

- `GET /assistant/ui-contract`를 추가해 UI 시작 순서, 메시지 흐름, 응답 타입, 차단 기능, 인증 header 계약을 한 번에 조회할 수 있게 했다.
- 이 endpoint는 read-only 계약 요약이며 실제 실행 기능을 활성화하지 않는다.
- `local-ai assistant-ui-contract` CLI 명령을 추가했다.
- `/project/status` 차수를 12차 Assistant UI contract 완료, 13차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `72 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant startup snapshot

- `GET /assistant/startup`를 추가해 UI 첫 로딩에 필요한 `ping`, `config`, `dashboard`, `ui_contract`를 read-only snapshot으로 한 번에 조회할 수 있게 했다.
- `/assistant/ui-contract`의 `startup_sequence`를 `/assistant/startup` 우선 흐름으로 정리하고, 개별 조회 endpoint는 `refresh_endpoints`로 분리했다.
- `docs/UI_BRIDGE_EXAMPLES.md`를 추가해 startup, ui-contract, assistant message 예시 payload를 안전한 placeholder로 문서화했다.
- `docs/UI_BRIDGE_EXAMPLES.md`에 `/assistant/message` 응답 타입별 예시를 추가했다.
- `docs/UI_QA_CHECKLIST.md`를 추가해 실제 브라우저 조작 없이 확인할 수 있는 수동 QA 기준과 stop condition을 문서화했다.
- README에 브라우저 UI를 붙이는 기본 순서 `startup -> bootstrap -> action-preview -> message -> messages paging`를 추가했다.
- README/API/PROJECT_SUMMARY 핵심 endpoint, CLI, 공개 문서 링크가 서로 맞는지 확인하는 public docs contract 테스트를 추가했다.
- `docs/RELEASE_CHECKLIST.md`를 추가해 GitHub 공개 전 코드, 문서, 보안, 실행 경계, stop condition을 한 곳에서 확인할 수 있게 했다.
- 이 endpoint는 상태/계약 조회만 수행하며 shell 실행, 파일 수정/삭제, 브라우저 조작을 활성화하지 않는다.
- `local-ai assistant-startup` CLI 명령을 추가했다.
- `/project/status` 차수를 13차 Assistant startup snapshot 완료, 14차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `5 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `164 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Next chat handoff safety polish

- `docs/NEXT_CHAT_HANDOFF.md`의 다음 작업을 실제 브라우저 조작으로 오해되지 않도록 API 계약/문서 QA 보강 중심으로 수정했다.
- Codex가 바로 할 수 있는 안전 작업과 사용자 수동 확인 또는 별도 승인 후에만 진행할 작업을 분리했다.
- `tests/test_next_chat_handoff.py`를 추가해 handoff 문서가 브라우저 조작 없이 진행하는 안전 작업, 최신 검증 gate, UI/release 문서 링크를 유지하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_public_docs_contract.py tests/test_ui_qa_checklist.py tests/test_readme_ui_bridge.py` 결과는 `11 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `167 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Assistant/project docs contract polish

- README `Continuation Status` 섹션에 `GET /project/status`, `GET /project/next`, `GET /project/shell-policy`, `POST /project/shell-dry-run` endpoint와 CLI 대응을 명시했다.
- `tests/test_public_docs_contract.py`를 확장해 assistant endpoint 전체, assistant CLI 전체, project continuation endpoint/CLI가 README, API 문서, PROJECT_SUMMARY에 모두 포함되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `8 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `168 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### UI bridge schema example validation

- `docs/UI_BRIDGE_EXAMPLES.md`의 `/assistant/ui-contract` 예시에 `message_flow`, `safety`, `notes`를 추가했다.
- `docs/UI_BRIDGE_EXAMPLES.md`의 `/assistant/startup` 예시에 `ui_contract`와 top-level `safety`를 추가해 실제 `AssistantStartupResponse` schema와 맞췄다.
- `tests/test_ui_bridge_examples.py`를 확장해 UI bridge 예시 JSON이 `AssistantUiContractResponse`, `AssistantStartupResponse`, `AssistantMessageRequest`, `AssistantMessageResponse`로 validate되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py` 결과는 `4 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `169 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### API docs payload schema validation

- `tests/test_api_docs_payloads.py`를 추가해 `docs/API.md`의 curl `-d` JSON payload 예시를 추출하고 실제 request schema로 validate한다.
- 검증 대상은 assistant, ask, ask-with-docs, folder index preview/index, search, feedback, agent plan, project shell dry-run request payload다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py` 결과는 `1 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `169 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### 응답 형식 업데이트

- 실제 배포/클라우드/DB migration 작업이 없으면 배포 여부 섹션을 반복하지 않기로 정리함.
- 최종 보고는 `Recommended Next Model` 섹션 중심으로 다음 작업을 이어갈 수 있게 작성함.
