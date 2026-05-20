# NEXT_CHAT_HANDOFF

## Recommended Next Model

- Recommended AI: Codex
- Recommended model: Codex GPT-5.5
- Reason: 로컬 전용 FastAPI/Ollama/SQLite/Chroma 백엔드 구현과 검증은 Codex가 안전하게 계속 처리 가능
- Next task: 실제 사용자 문서 기반 E2E 검증, 또는 OCR/대용량 진행률/repair 명령 범위 결정
- User action required: 없음. 단, 시스템 의존성 설치, 파일 삭제, 운영 배포, 외부 LLM API 활성화는 사용자 승인 전 진행 불가

## 프로젝트 루트

```bash
cd /Users/juyoung/local-ai-server
pwd
ls
git status
```

주의: 현재 폴더는 Git 저장소가 아닐 수 있다. `git status`가 실패하면 그 사실을 보고하고 계속 진행한다.

## 현재 상태

로컬 AI 지식 서버의 기본 MVP가 구현되어 있다.

- FastAPI backend
- SQLite metadata/log/feedback 저장
- Chroma vector search
- Ollama local chat/embed client
- 문서 업로드 및 폴더 색인
- 실제 저장 전 read-only 폴더 색인 preview
- 실제 폴더 색인 후 파일별 성공/스킵 상세 응답
- `.html`, `.htm` 로컬 HTML 텍스트 추출
- RAG 답변 API
- Typer CLI
- SFT JSONL export
- README, AGENTS, API, PROJECT_SUMMARY, CLAUDE_REVIEW_HANDOFF, WORKLOG, OPERATIONS, SECURITY 문서

## 먼저 읽을 파일

- `AGENTS.md`
- `SECURITY.md`
- `README.md`
- `docs/API.md`
- `docs/PROJECT_SUMMARY.md`
- `docs/CLAUDE_REVIEW_HANDOFF.md`
- `docs/WORKLOG.md`
- `docs/OPERATIONS.md`
- `app/main.py`
- `app/api/*.py`
- `app/services/*.py`
- `tests/*.py`

## 검증 명령

```bash
source .venv/bin/activate
pytest
python -m compileall app cli scripts
```

PDF/DOCX 실제 색인 검증을 위해 Python optional dependency는 현재 venv에 설치되어 있다.

```bash
pip install -e ".[dev,documents]"
```

## 실제 로컬 실행 검증

```bash
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

다른 터미널:

```bash
curl http://127.0.0.1:8000/health
local-ai health
local-ai doctor
local-ai stats
local-ai integrity
local-ai repair-preview
local-ai document-types
local-ai index-preview ./notes
local-ai upload ./notes/backend.md
local-ai search "JWT"
local-ai chunks 1 --limit 20 --offset 0
local-ai docs --source-type upload --file-type md --query backend
local-ai logs --limit 20 --offset 0
local-ai logs --mode rag --query JWT --limit 20 --offset 0
local-ai log 1
local-ai feedbacks --limit 20 --offset 0
local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름 설명해줘"
```

## 현재 확인된 상태

- `llama3.2`는 로컬 Ollama에 있음.
- `nomic-embed-text`는 로컬 Ollama에 있음.
- `/ask` 실제 Ollama 호출은 성공했음.
- upload/search/RAG 실제 end-to-end 검증 성공.
- `/documents/stats`와 `local-ai stats`로 SQLite/Chroma 상태 read-only 점검 가능.
- `/documents/integrity`와 `local-ai integrity`로 SQLite/Chroma 정합성 read-only dry-run 점검 가능.
- `/documents/repair-preview`와 `local-ai repair-preview`로 실제 수정 없이 repair action 후보 확인 가능.
- `/documents/index-folder-preview`와 `local-ai index-preview`로 실제 저장 없이 폴더 색인 대상, 예상 chunk 수, 예상 embedding batch 수 확인 가능.
- `/documents/index-folder`는 `indexed_files`, `skipped_file_details`로 파일별 색인 결과 확인 가능.
- `/documents/supported-types`와 `local-ai document-types`로 문서 타입별 optional dependency 준비 상태 확인 가능.
- `/documents/{document_id}/chunks`와 `local-ai chunks`로 chunk 페이지 조회 가능.
- `/documents?source_type=&file_type=&query=`와 `local-ai docs --source-type --file-type --query`로 문서 목록 필터 조회 가능.
- `.pdf`, `.docx`는 optional dependency 설치 시 텍스트 추출 가능. dependency가 없으면 명확한 설치 안내 오류를 반환함.
- `.html`, `.htm`은 표준 라이브러리 기반으로 UTF-8 HTML 본문 텍스트 추출 가능. `file_type=html`로 정규화됨.
- 현재 venv 기준 `.pdf`, `.docx` 모두 available=true.
- 실제 DOCX/PDF 샘플 업로드, search, ask-docs 검증 완료.
- 문서 업로드 중 SQLite write lock을 줄이도록 embedding을 DB write 전에 수행하게 개선.
- `EMBEDDING_BATCH_SIZE` 설정과 Ollama `/api/embed` batch 호출 기반 embedding 최적화 완료. Preview 응답에서 `embedding_batch_size`, `embedding_batches_estimated` 확인 가능.
- `EMBEDDING_MAX_RETRIES` 기반 embedding batch 재시도 완료.
- Chroma `PersistentClient` singleton 공유로 동시 첫 요청 search/stats/integrity 500 오류 수정.
- DB/Chroma 저장 단계 실패 시 SQLite rollback과 명확한 `DocumentIndexingError` 반환 완료.
- `CHUNK_SIZE=120`, `CHUNK_OVERLAP=20`, `EMBEDDING_BATCH_SIZE=2` 조건에서 22개 chunk 업로드와 검색 검증 완료.
- `/chat-logs`, `/chat-logs/{chat_log_id}`와 `local-ai logs`, `local-ai log`로 chat log 조회 가능. `mode=direct|rag`, `query=<keyword>` 필터 지원.
- `GET /feedback`와 `local-ai feedbacks`로 feedback 목록 조회 가능. `rating`, `chat_log_id` 필터 지원.
- `docs/API.md`에 endpoint별 요청 예시, 응답 핵심 필드, 보호 endpoint, CLI 대응 관계가 정리되어 있음.
- `docs/OPERATIONS.md`에 로컬 운영 로그, 저장공간 점검, 백업, 수동 rotation 예시가 정리되어 있음.
- `SECURITY.md`에 로컬 운영 보안 원칙, 공개 전 체크리스트, 고위험 작업 기준이 정리되어 있음.
- README 앞부분에 개발 배경, 기술 선택 이유, 핵심 구현 포인트가 포트폴리오용으로 정리되어 있음.
- `docs/PROJECT_SUMMARY.md`에 endpoint/CLI/실행/테스트/한계/다음 개선 요약이 정리되어 있음.
- `docs/CLAUDE_REVIEW_HANDOFF.md`에 Claude Sonnet 문서 정합성 리뷰용 입력과 출력 형식이 정리되어 있음.
- `data/logs/`는 운영 로그용 디렉터리이며 로그 파일은 Git 제외 대상임.
- RAG guard가 추가되어 문서 밖 코드/링크/보안 세부사항/추측성 표현을 감지하면 fallback 답변으로 대체함.
- 실행형 Agent dry-run/승인/실행 엔진 v1 API가 추가됨. 기본값에서는 실제 실행을 차단하고, enabled 상태에서도 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원함.

## 금지사항

- OpenAI, Claude, Gemini 외부 API를 런타임에 추가하지 말 것.
- LangChain을 추가하지 말 것.
- 프론트엔드를 만들지 말 것.
- 원본 색인 대상 파일을 삭제하거나 수정하지 말 것.
- secret, API key, DB password를 출력하지 말 것.
- 운영 배포, 클라우드 리소스 변경, DB migration을 사용자 승인 없이 하지 말 것.

## 응답 형식 지침

이 프로젝트는 로컬 전용 백엔드 서버다. 실제 배포/클라우드/DB migration 작업이 없다면 최종 보고에 배포 여부 섹션을 반복하지 않는다.

마지막에는 아래처럼 다음 진행을 명확히 적는다.

```markdown
## Recommended Next Model

- Recommended AI: Codex
- Recommended model: Codex GPT-5.5
- Reason: README/docs 최종 정합성 점검은 Codex가 안전하게 처리 가능
- Next task: 실제 사용자 문서 기반 E2E 검증 또는 선택형 개선 범위 결정
- User action required: 없음. 단, 외부 STT/TTS/realtime tool call/browser interaction 활성화는 사용자 승인 전 진행 불가
```

## 다음 추천 작업

1. 실제 사용자 `.md` 또는 `.txt` 문서 업로드 검증
2. `/search` 실제 embedding + Chroma 검색 재확인
3. `/ask-with-docs` 실제 RAG 답변 품질 확인
4. `local-ai stats`로 SQLite/Chroma 상태 확인
5. `local-ai integrity`로 SQLite/Chroma 정합성 확인
6. `local-ai repair-preview`로 repair 후보 확인
7. `local-ai index-preview <folder>`로 실제 색인 전 예상 chunk 수 확인
8. `local-ai chunks <document_id>`로 chunk 내용 확인
9. `local-ai docs --source-type upload --file-type md --query <keyword>`로 문서 목록 필터 확인
10. `local-ai logs`와 `local-ai log <id>`로 chat log 확인
11. `local-ai feedbacks`로 feedback 확인
12. 필요하면 OCR loader 또는 HTML JavaScript 렌더링/크롤링 범위 결정
13. 필요하면 대용량 문서 진행률 표시 또는 Chroma 누락 vector 재생성 명령 설계
14. 필요하면 자동 로그 rotation 구현. 단 실제 삭제/압축 자동화 정책은 사용자 승인 필요
15. 필요하면 Chroma/SQLite 실제 repair 명령 추가. 단 실제 repair/delete는 사용자 승인 필요
16. 필요하면 Claude Sonnet으로 README/문서 정합성 리뷰 진행

## 최근 Codex self-check

- README/docs 링크와 기능 설명 정합성을 Codex가 직접 점검했다.
- `docs/API.md` CLI 대응 목록의 `local-ai document-types` 누락을 반영했다.
- README 현재 한계에 HTTPS termination 미지원 상태와 process-local rate limit 한계를 명시했다.
- 최신 검증:
  - `.venv/bin/pytest`: `133 passed`
  - `.venv/bin/python -m compileall app cli scripts`: 성공
  - `python scripts/public_release_check.py --root . --json`: 현재 로컬 DB/Chroma/uploads 파일을 공개 전 제외 대상 finding으로 탐지함

## 최근 테스트 보강

- `tests/test_cli.py`를 추가해 CLI가 FastAPI 백엔드를 HTTP로 호출하는 계약을 mock 기반으로 검증한다.
- `tests/test_security.py`를 확장해 보호 endpoint 전체의 `LOCAL_API_KEY` 요구 동작을 검증한다.
- `tests/test_rate_limiter.py`를 추가해 process-local in-memory rate limiter를 검증한다.
- `tests/test_smoke_script.py`를 추가해 `scripts/smoke_test_api.py`의 API 호출 순서를 mock으로 검증한다.
- `tests/test_public_release_check.py`를 추가해 공개 전 read-only 보안 점검 스크립트를 검증한다.
- `tests/test_agent_service.py`, `tests/test_agent_api.py`를 추가해 Agent preview plan 생성과 조회 API를 검증한다.
- assistant REPL에 `/summary`, `/roots`, `/status`, `/next`, `/shell-policy`, `/shell-dry-run <command>`를 추가했다.
- `local-ai roots`, `local-ai shell-policy`, `local-ai shell-dry-run "pwd"`를 추가했다.
- `/project/shell-policy`, `/project/shell-dry-run`은 실제 shell을 실행하지 않고 정책 판단만 반환한다.
- `/project/status`는 4차 safer automation loop 완료 이력을 포함한다.
- `/assistant/capabilities`, `/assistant/sessions`, `/assistant/sessions/{session_id}`, `/assistant/message`, `/assistant/project-root/validate`를 추가했다.
- `local-ai assistant-capabilities`, `local-ai assistant-session`, `local-ai assistant-message`, `local-ai assistant-root`를 추가했다.
- `/project/status`는 5차 UI Bridge Assistant API 완료 이력을 포함한다.
- `LOCAL_CORS_ORIGINS`와 FastAPI CORS middleware를 추가해 `127.0.0.1:5173`/`localhost:5173` 로컬 브라우저 UI 호출을 허용했다.
- `GET /assistant/sessions`와 `local-ai assistant-sessions`를 추가했다.
- `/project/status`는 6차 Browser UI integration support 완료, 7차 Live browser UI QA를 다음 단계로 표시한다.
- 확인 항목:
  - `local-ai ask`가 `LOCAL_AI_SERVER_URL`, payload, `X-API-Key`를 올바르게 사용함
  - `local-ai docs`가 필터 query parameter를 올바르게 전달함
  - `local-ai index-preview`가 보호 endpoint에 API key header를 전달함
  - `local-ai upload`가 파일 누락 시 HTTP 호출 전에 실패함
  - 보호 endpoint가 API key 누락 시 `401`을 반환함
  - rate limit 초과 시 `429`와 `Retry-After` header를 반환함
  - smoke script가 `health → upload → search → ask-with-docs → feedback → stats` 순서로 호출함
  - public release check가 `.env`, SQLite, uploads, Chroma, secret 후보를 탐지하고 `.env.example`, `.gitkeep`는 허용함
  - `/agent/plan`이 browser/file/shell 요청을 preview-only high-risk action으로 분류함
  - `/agent/runs/{run_id}/approve`와 `/reject`가 상태만 바꾸고 실제 실행하지 않음
  - `/agent/runs/{run_id}/execute`가 승인된 run만 실행 시도하고, 기본값에서 blocked 결과를 기록함
  - `AGENT_ALLOWED_ROOTS` 밖의 파일/폴더 접근은 blocked 처리함
  - `AGENT_WEB_FETCH_MAX_BYTES` 이후 URL fetch 응답은 truncate함
