# Project Summary

## 한 줄 소개

`local-ai-server`는 외부 LLM API 없이 Ollama, FastAPI, SQLite, Chroma, Typer로 동작하는 로컬 전용 AI 지식 서버다.

## 무엇을 만들었는지

- 로컬 Ollama 기반 direct ask API
- 로컬 문서 업로드와 폴더 색인
- SQLite 기반 문서 metadata, chunk, chat log, feedback 저장
- Chroma 기반 vector search
- 문서 검색 기반 RAG 답변 API
- 로컬 서버를 호출하는 Typer CLI
- feedback 저장과 SFT JSONL export
- 문서/운영/보안/API/인계 문서

## 핵심 설계

```text
CLI / curl
  -> FastAPI route
  -> service layer
  -> Ollama local API
  -> SQLite metadata/log source of truth
  -> Chroma vector search
```

설계 기준:

- API route는 얇게 유지한다.
- 비즈니스 로직은 `app/services/`에 둔다.
- SQLite는 source of truth, Chroma는 vector search 전용으로 분리한다.
- CLI는 백엔드 API를 호출하고 로직을 중복 구현하지 않는다.
- 외부 LLM API, LangChain, cloud vector DB는 사용하지 않는다.

## Endpoint 목록

Health:

- `GET /health`
- `GET /health/ollama`

Ask/Search:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`

Documents:

- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder`
- `GET /documents`
- `GET /documents/supported-types`
- `GET /documents/stats`
- `GET /documents/integrity`
- `GET /documents/repair-preview`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/chunks`
- `DELETE /documents/{document_id}`

Chat/Feedback:

- `GET /chat-logs`
- `GET /chat-logs/{chat_log_id}`
- `POST /feedback`
- `GET /feedback`

Agent Preview:

- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`

## CLI 명령어 목록

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
local-ai agent-plan "GitHub 웹 열어줘"
local-ai agent-runs
local-ai agent-run 1
local-ai export-sft --output data/sft_dataset.jsonl
```

## 서버 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,documents]"

ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 테스트 실행 방법

```bash
pytest
python -m compileall app cli scripts
```

현재 검증 상태:

- `.venv/bin/pytest`: `86 passed`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000`: 실행 중인 서버 기준 E2E smoke test 가능
- `python scripts/public_release_check.py --root .`: GitHub 공개 전 로컬 데이터/secret 후보 read-only 점검 가능
- `local-ai agent-plan "GitHub 웹 열고 내 폴더도 열어줘"`: 실행형 Agent preview-only 계획 생성 가능

## 구현된 문서 타입

기본 지원:

- `.txt`
- `.md`
- `.html`
- `.htm`

optional dependency 설치 시 지원:

- `.pdf`
- `.docx`

지원하지 않는 것:

- 스캔 이미지 기반 PDF OCR
- JavaScript 렌더링 결과
- 외부 URL 크롤링
- 브라우저 interaction

## 보안과 운영 기준

- 기본 서버 bind는 `127.0.0.1` 권장
- `LOCAL_API_KEY` 설정 시 보호 endpoint는 `X-API-Key` 필요
- 보호 endpoint에는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit 적용
- 실행형 Agent는 preview-only 계획 단계이며 실제 browser/file/shell 실행은 비활성
- `.env`, SQLite DB, Chroma index, 업로드 파일, 로그 파일, SFT export 파일은 Git 제외
- 질문/답변/문서 원문/API key를 운영 로그에 남기지 않는 것을 권장
- 실제 repair/delete/rebuild, 외부 크롤링, 시스템 의존성 설치, 운영 배포는 사용자 승인 전 진행하지 않음

관련 문서:

- `README.md`
- `docs/API.md`
- `docs/OPERATIONS.md`
- `SECURITY.md`
- `docs/WORKLOG.md`
- `docs/NEXT_CHAT_HANDOFF.md`

## 현재 한계

- 실시간 색인 진행률 job API는 아직 없다.
- Chroma/SQLite repair는 read-only integrity와 repair preview까지만 제공한다.
- Agent는 preview-only 계획만 제공한다. 실제 웹 이동, 폴더 열기, shell 실행은 아직 비활성이다.
- OCR은 지원하지 않는다.
- HTML은 정적 UTF-8 텍스트 추출만 지원한다.
- 인증은 단일 `LOCAL_API_KEY` 수준이다.
- 다중 사용자 권한 관리와 HTTPS termination은 없다.
- rate limit은 단일 프로세스 메모리 기준이며, 분산 rate limit은 없다.

## 다음 추천 개선

1. 실제 사용자 문서로 upload/search/ask-with-docs end-to-end 재검증
2. 대용량 색인 job/status API 설계
3. Chroma 누락 vector 재생성 명령 설계
4. OCR loader 도입 여부 검토
5. 자동 로그 rotation 정책 검토
6. README와 API 문서 Claude Sonnet 리뷰
7. 실제 배포가 필요하면 보안/운영 리뷰 후 별도 결정
