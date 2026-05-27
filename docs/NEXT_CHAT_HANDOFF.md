# NEXT_CHAT_HANDOFF

## Recommended Next Model

- Recommended AI: Codex
- Recommended model: Codex GPT-5.5
- Reason: 로컬 전용 FastAPI/Ollama/SQLite/Chroma 백엔드 구현과 검증은 Codex가 안전하게 계속 처리 가능
- Next task: 실제 사용자 문서 E2E는 완료됨. 다음은 브라우저 조작 없이 문서/테스트/API 계약 polish 또는 사용자의 수동 UI 확인 결과 반영
- User action required: 없음. 단, 실제 브라우저 렌더링 확인, 메시지 전송, 시스템 의존성 설치, 파일 삭제, 운영 배포, 외부 LLM API 활성화는 사용자 승인 또는 수동 확인 전 진행 불가

## 프로젝트 루트

```bash
cd /Users/juyoung/local-ai-server
pwd
ls
git status
```

주의: 이 handoff 작성 시점의 프로젝트 루트는 Git 저장소다. 다른 환경에서 `git status`가 실패하면 그 사실을 보고하고 계속 진행한다.

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
- `docs/TASKS.md`에 safe-next, manual-check, review-required, blocked 작업 경계 정리
- 실제 사용자 문서 E2E 실행 전 승인/저장 영향/paste-safe 기준 문서 `docs/USER_DOCUMENT_E2E_PLAN.md`
- GitHub 공개용 현재 상태 요약 문서 `docs/PUBLIC_RELEASE_SUMMARY.md`

## 먼저 읽을 파일

- `AGENTS.md`
- `SECURITY.md`
- `README.md`
- `docs/TASKS.md`
- `docs/USER_DOCUMENT_E2E_PLAN.md`
- `docs/API.md`
- `docs/UI_BRIDGE_EXAMPLES.md`
- `docs/UI_CONNECT_GUIDE.md`
- `docs/UI_CONTRACT_CHEATSHEET.md`
- `docs/UI_QA_CHECKLIST.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/PUBLIC_RELEASE_SUMMARY.md`
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
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
.venv/bin/python scripts/local_ci_check.py --root .
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
- `/documents/supported-types`와 `local-ai document-types`로 문서 타입별 optional dependency와 `pdf_ocr` 준비 상태 확인 가능.
- `/project/api-inventory`와 `local-ai api-inventory`로 endpoint 목록, tag, method, API key 보호 여부를 read-only로 확인 가능.
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
- `docs/UI_BRIDGE_EXAMPLES.md`에 브라우저 UI 연동용 startup/ui-contract/message 예시 payload가 정리되어 있음.
- `docs/UI_CONNECT_GUIDE.md`에 별도 로컬 UI가 입력해야 할 API base URL, API key header, project root, startup 호출 순서가 정리되어 있음.
- `docs/UI_CONTRACT_CHEATSHEET.md`에 UI가 endpoint별로 읽어야 할 핵심 응답 필드와 safety/error 표시 규칙이 정리되어 있음.
- `docs/UI_QA_CHECKLIST.md`에 브라우저 UI 수동 QA 기준과 stop condition이 정리되어 있음.
- `docs/RELEASE_CHECKLIST.md`에 GitHub 공개 전 release checklist와 stop condition이 정리되어 있음.
- `docs/PUBLIC_RELEASE_SUMMARY.md`에 GitHub 공개 가능 범위, 비공개 로컬 데이터, 검증 명령, 현재 한계가 정리되어 있음.
- `scripts/smoke_test_api.py --assistant-bridge-only`로 브라우저 조작 없이 assistant startup/api-inventory/bootstrap/action-preview/message/session history API 흐름을 확인 가능.
- `scripts/local_ci_check.py`로 pytest, compileall, public release check, git diff check를 한 번에 실행 가능.
- `docs/OPERATIONS.md`에 로컬 운영 로그, 저장공간 점검, 백업, 수동 rotation 예시, 로컬 운영 Runbook이 정리되어 있음.
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
- 사용자 승인과 실제 지원 문서 경로 없이 실제 사용자 문서 E2E smoke를 실행하지 말 것.
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
- Next task: 문서/테스트/API 계약 polish 또는 사용자 수동 UI 확인 결과 반영
- User action required: 없음. 단, 외부 STT/TTS/realtime tool call/browser interaction 활성화는 사용자 승인 전 진행 불가
```

## 다음 추천 작업

Codex가 바로 이어서 할 수 있는 안전 작업:

1. `docs/USER_DOCUMENT_E2E_PLAN.md`, `docs/TASKS.md`, `docs/WORKLOG.md`의 완료된 실제 사용자 문서 E2E summary 정합성 유지
2. `README.md`, `docs/API.md`, `docs/PROJECT_SUMMARY.md`의 assistant endpoint와 CLI 목록 교차 검증
   - endpoint/response field 계약 테스트와 runtime endpoint count drift check 유지
3. README/Project Summary Runtime Contract Snapshot 값을 실제 API/CLI/smoke flow inventory와 비교하는 계약 유지
4. `tests/test_public_docs_contract.py`, `tests/test_user_document_e2e_plan.py`, `tests/test_readme_ui_bridge.py`로 문서 계약 유지
5. `docs/RELEASE_CHECKLIST.md` 기준 공개 전 stop condition 누락 여부 확인
6. PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지
7. assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 표시 기준과 함께 유지
8. `.venv/bin/pytest`, compileall, public release check, `git diff --check` 재실행

사용자 수동 확인 또는 별도 승인 후에만 진행할 작업:

1. `docs/UI_QA_CHECKLIST.md` 기준으로 실제 브라우저 UI에서 `GET /assistant/startup` 렌더링 확인
2. UI에서 `GET /assistant/ping`, `GET /assistant/config`, `GET /assistant/dashboard` 개별 refresh 동작 확인
3. UI에서 `GET /assistant/ui-contract` 시작 순서, 메시지 흐름, 응답 타입, 차단 기능 계약 표시 확인
4. UI에서 `POST /assistant/bootstrap` project root/session/UI 힌트 렌더링 확인
5. UI에서 `POST /assistant/action-preview` 위험도/필요 입력값 표시 확인
6. UI에서 `POST /assistant/message` 실제 메시지 전송과 `ui` 힌트 렌더링 확인
7. UI에서 `GET /assistant/sessions`, `GET /assistant/sessions/{session_id}/messages` 대화 목록과 paging 확인
8. 추가 사용자 문서로 재검증이 필요하면 사용자 승인과 실제 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 경로를 받은 뒤 실행
9. `/search` 실제 embedding + Chroma 검색 재확인
10. `/ask-with-docs` 실제 RAG 답변 품질 확인
11. 필요하면 HTML JavaScript 렌더링/크롤링 또는 pdf2image/poppler 기반 page rendering OCR 확장 범위 결정
12. 필요하면 대용량 문서 진행률 표시 또는 Chroma 누락 vector 실제 rebuild 활성화 조건 문서화
13. 필요하면 자동 로그 rotation 구현. 단 실제 삭제/압축 자동화 정책은 사용자 승인 필요
14. 필요하면 Chroma/SQLite 실제 repair 명령 추가. 단 실제 repair/delete는 사용자 승인 필요
15. 실제 repair/delete/rebuild, 브라우저 click/fill/submit, shell 실행, 파일 생성/수정/삭제 자동화는 별도 승인 또는 보안 리뷰 전 진행하지 않음
16. 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit은 별도 보안/운영 리뷰 전 진행하지 않음

## 최근 Codex self-check

- README/docs 링크와 기능 설명 정합성을 Codex가 직접 점검했다.
- `docs/API.md` CLI 대응 목록의 `local-ai document-types` 누락을 반영했다.
- README 현재 한계에 HTTPS termination 미지원 상태와 process-local rate limit 한계를 명시했다.
- PDF OCR fallback은 PyPDF image XObject 기반 optional loader로 구현했고, 외부 OCR/cloud OCR/pdf2image/poppler는 추가하지 않았다.
- 최신 검증:
  - `.venv/bin/pytest`: `524 passed`
  - `.venv/bin/python -m compileall app cli scripts`: 성공
  - `.venv/bin/python scripts/public_release_check.py --root . --json`: `ok=true`, finding 없음
  - `git diff --check`: 성공
  - `.venv/bin/python scripts/local_ci_check.py --root .`: 성공

## 최근 테스트 보강

- `tests/test_cli.py`를 추가해 CLI가 FastAPI 백엔드를 HTTP로 호출하는 계약을 mock 기반으로 검증한다.
- `tests/test_security.py`를 확장해 보호 endpoint 전체의 `LOCAL_API_KEY` 요구 동작을 검증한다.
- `tests/test_rate_limiter.py`를 추가해 process-local in-memory rate limiter를 검증한다.
- `tests/test_smoke_script.py`를 추가해 `scripts/smoke_test_api.py`의 문서/RAG smoke와 assistant bridge smoke API 호출 순서를 mock으로 검증한다.
- `tests/test_public_release_check.py`를 보강해 public release scanner, `.gitignore`, release checklist, public release summary의 private data 제외 목록 정합성을 검증한다.
- `tests/test_local_ci_check.py`를 추가해 `scripts/local_ci_check.py`가 고정된 안전 검증 명령을 순서대로 실행하고 실패 시 중단하는지 mock으로 검증한다.
- `tests/test_operations_runbook.py`를 추가해 `docs/OPERATIONS.md`의 로컬 운영 Runbook이 안전한 점검 순서와 위험 작업 제외 원칙을 유지하는지 검증한다.
- `tests/test_operations_runbook.py`와 `tests/test_readme_quick_start.py`를 보강해 검증 명령별 저장 영향이 README/운영 Runbook에 드러나는지 확인한다.
- `tests/test_readme_quick_start.py`를 추가해 README 상단 Quick Start, Verification, Safe Boundaries, Key Docs 계약을 검증한다.
- `tests/test_readme_quick_start.py`를 보강해 README 상단 Highlights가 프로젝트 핵심과 안전 경계를 압축해 보여주는지 검증한다.
- `tests/test_public_docs_contract.py`를 보강해 런타임 FastAPI endpoint와 Typer CLI command가 README/API 문서에서 누락되지 않도록 검증한다.
- `tests/test_tasks_doc.py`를 추가해 `docs/TASKS.md`가 safe-next/manual-check/review-required 작업 경계와 stop condition을 유지하는지 검증한다.
- `tests/test_ui_bridge_examples.py`를 보강해 `/assistant/ui-contract` 예시의 response type, refresh endpoint, blocked action이 실제 service 계약과 일치하는지 검증한다.
- `tests/test_ui_qa_checklist.py`를 보강해 수동 QA 체크리스트가 `/assistant/ui-contract`의 startup sequence, refresh endpoint, message flow, response type, blocked action을 빠뜨리지 않도록 검증한다.
- `tests/test_ui_connect_guide.py`를 보강해 UI 연결 가이드의 `/assistant/startup`과 `/assistant/bootstrap` 응답 필드 설명이 실제 Pydantic response schema와 어긋나지 않도록 검증한다.
- `tests/test_smoke_script.py`를 보강해 UI 연결 가이드의 assistant bridge smoke expected output이 실제 smoke summary field와 어긋나지 않도록 검증한다.
- `tests/test_portfolio_docs_contract.py`를 보강해 README와 PROJECT_SUMMARY의 다음 추천 개선이 최신 API 상태와 안전 경계를 같이 반영하는지 검증한다.
- `scripts/smoke_test_api.py`의 문서/RAG smoke가 `smoke-backend-notes.md`와 `smoke-architecture-notes.txt`를 함께 업로드하도록 확장했다.
- `tests/test_smoke_script.py`가 Markdown/Text sample 업로드, content type, README/OPERATIONS 안내 문구를 검증한다.
- `docs/UI_QA_CHECKLIST.md`, `docs/UI_CONNECT_GUIDE.md`, `docs/UI_BRIDGE_EXAMPLES.md`, `docs/UI_CONTRACT_CHEATSHEET.md`에 최신 preview endpoint인 `/documents/index-folder-job-preview`, `/documents/vector-rebuild-preview` UI 표시 기준을 반영했다.
- `tests/test_ui_qa_checklist.py`, `tests/test_ui_connect_guide.py`, `tests/test_ui_bridge_examples.py`, `tests/test_ui_contract_cheatsheet.py`, `tests/test_smoke_script.py`가 최신 preview endpoint UI 문서 계약을 검증한다.
- `tests/test_readme_quick_start.py`를 보강해 README 상단 Local Assistant Quick Flow와 preview/dry-run 안전 문구를 검증한다.
- `tests/test_readme_quick_start.py`를 보강해 CLI assistant REPL 도움말과 README 명령 목록 정합성을 검증한다.
- `tests/test_ui_connect_guide.py`를 추가해 UI 연결값, startup flow, 안전 경계 문서 계약을 검증한다.
- `tests/test_ui_contract_cheatsheet.py`를 추가해 UI field cheatsheet의 endpoint, response type, safety/error 계약을 검증한다.
- `scripts/smoke_test_api.py --assistant-bridge-preflight`와 관련 테스트를 추가해 wrong-server base URL을 read-only로 감지한다.
- `tests/test_public_release_check.py`를 추가해 공개 전 read-only 보안 점검 스크립트를 검증한다.
- `tests/test_agent_service.py`, `tests/test_agent_api.py`를 추가해 Agent preview plan 생성과 조회 API를 검증한다.
- assistant REPL에 `/summary`, `/roots`, `/status`, `/next`, `/shell-policy`, `/shell-dry-run <command>`를 추가했다.
- `local-ai roots`, `local-ai shell-policy`, `local-ai shell-dry-run "pwd"`를 추가했다.
- `/project/shell-policy`, `/project/shell-dry-run`은 실제 shell을 실행하지 않고 정책 판단만 반환한다.
- `/project/api-inventory`와 `local-ai api-inventory`를 추가해 endpoint 목록과 API key 보호 여부를 read-only로 확인할 수 있다.
- `docs/UI_BRIDGE_EXAMPLES.md`와 `docs/UI_QA_CHECKLIST.md`에 read-only `GET /project/api-inventory` UI 연동/QA 기준을 추가했다.
- `/project/status`는 4차 safer automation loop 완료 이력을 포함한다.
- `/assistant/capabilities`, `/assistant/sessions`, `/assistant/sessions/{session_id}`, `/assistant/message`, `/assistant/project-root/validate`를 추가했다.
- `local-ai assistant-capabilities`, `local-ai assistant-session`, `local-ai assistant-message`, `local-ai assistant-root`를 추가했다.
- `/project/status`는 5차 UI Bridge Assistant API 완료 이력을 포함한다.
- `LOCAL_CORS_ORIGINS`와 FastAPI CORS middleware를 추가해 `127.0.0.1:5173`/`localhost:5173` 로컬 브라우저 UI 호출을 허용했다.
- `GET /assistant/sessions`와 `local-ai assistant-sessions`를 추가했다.
- `/assistant/bootstrap`와 `local-ai assistant-bootstrap`을 추가했다.
- `/assistant/message` 응답에 `ui.response_type`, `ui.severity`, `ui.primary_text`, `ui.display` 힌트를 추가했다.
- `/assistant/ping`, `/assistant/config`, `/assistant/dashboard`와 대응 CLI를 추가했다.
- `/assistant/sessions/{session_id}/messages`와 `local-ai assistant-messages`를 추가했다.
- `/assistant/action-preview`와 `local-ai assistant-action-preview`를 추가했다.
- `/assistant/ui-contract`와 `local-ai assistant-ui-contract`를 추가했다.
- `/assistant/startup`와 `local-ai assistant-startup`을 추가했다.
- `/project/status`는 14차 Project API inventory 완료, 15차 Live browser UI QA를 다음 단계로 표시한다.
- `tests/test_next_chat_handoff.py`를 추가해 이 handoff가 브라우저 조작 없이 가능한 Codex 작업과 사용자 수동 확인 작업을 분리하는지 검증한다.
- `tests/test_public_docs_contract.py`가 README와 Project Summary의 `Runtime Contract Snapshot` 값을 실제 API/CLI/smoke flow inventory와 비교한다.
- `tests/test_tasks_doc.py`, `tests/test_public_release_summary.py`, `tests/test_portfolio_docs_contract.py`, `tests/test_next_chat_handoff.py`가 Runtime Contract Snapshot guard가 task board, release summary, portfolio docs, handoff에 남아 있는지 검증한다.
- `tests/test_public_docs_contract.py`를 확장해 assistant endpoint/CLI 전체와 project continuation endpoint/CLI가 README/API/PROJECT_SUMMARY에 모두 문서화되어 있는지 검증한다.
- `tests/test_ui_bridge_examples.py`를 확장해 UI bridge 예시 JSON이 실제 assistant Pydantic schema와 맞는지 검증한다.
- `tests/test_api_docs_payloads.py`를 추가해 `docs/API.md` curl JSON payload 예시가 실제 request schema와 맞는지 검증한다.
- `tests/test_api_docs_payloads.py`를 보강해 `docs/API.md` top-level 섹션 순서와 Ask endpoint 배치를 검증한다.
- `tests/test_security_docs_contract.py`를 추가해 README/SECURITY/RELEASE_CHECKLIST 보안 문구와 보호 endpoint 목록 정합성을 검증한다.
- `tests/test_portfolio_docs_contract.py`를 추가해 README/PROJECT_SUMMARY 포트폴리오 설명과 한계 명시가 유지되는지 검증한다.
- `tests/test_portfolio_docs_contract.py`를 보강해 README/PROJECT_SUMMARY/SECURITY의 현재 한계와 금지 기능 표현을 교차 검증한다.
- 확인 항목:
  - `local-ai ask`가 `LOCAL_AI_SERVER_URL`, payload, `X-API-Key`를 올바르게 사용함
  - `local-ai docs`가 필터 query parameter를 올바르게 전달함
  - `local-ai index-preview`가 보호 endpoint에 API key header를 전달함
  - `local-ai upload`가 파일 누락 시 HTTP 호출 전에 실패함
  - 보호 endpoint가 API key 누락 시 `401`을 반환함
  - rate limit 초과 시 `429`와 `Retry-After` header를 반환함
  - smoke script가 `health → upload → search → ask-with-docs → feedback → stats` 순서로 호출함
  - assistant bridge smoke script가 `startup → api-inventory → bootstrap → action-preview → message(auto/status intent) → sessions → messages` 순서로 호출함
  - public release check가 `.env`, `.env.*`, SQLite, uploads, Chroma, secret 후보를 탐지하고 `.env.example`, `.gitkeep`는 허용함
  - `/agent/plan`이 browser/file/shell 요청을 preview-only high-risk action으로 분류함
  - `/agent/runs/{run_id}/approve`와 `/reject`가 상태만 바꾸고 실제 실행하지 않음
  - `/agent/runs/{run_id}/execute`가 승인된 run만 실행 시도하고, 기본값에서 blocked 결과를 기록함
  - `AGENT_ALLOWED_ROOTS` 밖의 파일/폴더 접근은 blocked 처리함
  - `AGENT_WEB_FETCH_MAX_BYTES` 이후 URL fetch 응답은 truncate함
