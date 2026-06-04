# local-ai-server

`local-ai-server`는 내 컴퓨터 또는 내 서버에서만 동작하는 백엔드 전용 로컬 AI 지식 서버입니다. 런타임에서 OpenAI, Claude, Gemini 같은 외부 LLM API를 사용하지 않고, Ollama local API만 호출합니다.

## Highlights

- 로컬 Ollama 기반 direct ask와 문서 기반 RAG 답변 API를 제공합니다.
- SQLite를 문서 metadata, chunk, chat log, feedback의 source of truth로 사용합니다.
- Chroma는 vector search 전용으로 사용하고, cloud vector DB는 사용하지 않습니다.
- Typer CLI는 FastAPI 백엔드를 HTTP로 호출해 API 계약을 재사용합니다.
- Agent/assistant 기능은 preview, dry-run, approval, read-only 경계를 기본값으로 둡니다.

## Who This Helps

This project is for developers and students who want to experiment with private, local-first AI workflows:

- Build a local document RAG backend without sending personal notes to external LLM APIs by default.
- Reuse one FastAPI contract from CLI, tests, and future local UI surfaces.
- Study practical backend boundaries for document upload, indexing, vector search, chat logs, feedback, and assistant-style previews.
- Keep shell, browser, file automation, cloud resources, and external provider calls outside the default safe runtime.

## Current Status Snapshot

| 구분 | 상태 | 공개용 설명 |
|---|---|---|
| 로컬 API 서버 | 구현됨 | FastAPI, SQLite, Chroma, Ollama local API 기반으로 실행됩니다. |
| 문서 기반 RAG | 구현됨 | `.txt`, `.md`, `.html`, `.htm`, optional `.pdf`, `.docx` 문서 색인과 검색/답변을 지원합니다. PDF OCR fallback은 `[ocr]` extra와 로컬 `tesseract`가 있을 때 PyPDF image XObject 범위에서 동작합니다. |
| CLI 로컬 비서 | 구현됨 | Typer CLI가 FastAPI 백엔드를 호출하며 `local-ai assistant` REPL을 제공합니다. |
| Agent 실행 엔진 | preview-only | 승인 상태와 read-only preview 중심이며 실제 shell/file/browser 실행은 하지 않습니다. |
| 배포/외부 자동화 | 하지 않음 | 운영 배포, 브라우저 조작, 파일 자동 수정/삭제, 외부 LLM API 연결은 현재 범위 밖입니다. |

## Quick Start

Ollama는 보통 별도 터미널에서 먼저 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,documents]"

ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Verification

서버 없이 안전한 로컬 검증을 한 번에 실행하려면:

```bash
.venv/bin/python scripts/local_ci_check.py --root .
```

이 명령은 아래 순서로 멈춤 없는 정적 검증을 실행하고, 실패하면 해당 단계에서 중단합니다.

1. `.venv/bin/python -m pytest`
2. `.venv/bin/python -m compileall app cli scripts`
3. `.venv/bin/python scripts/public_release_check.py --root . --json`
4. `git diff --check`

서버 실행 후 assistant bridge API만 smoke test하려면:

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
```

문서 업로드, 검색, RAG smoke test까지 확인하려면 Ollama와 기본 모델이 필요합니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000
```

작업 기록에 붙일 때는 민감하거나 불필요한 세부값을 뺀 summary만 출력합니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --sanitized-summary
```

승인된 실제 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서로 확인할 때는 `--document`를 사용합니다. PDF OCR fallback 검증도 같은 옵션을 쓰며, 이 명령은 SQLite, Chroma, `data/uploads/`에 테스트 데이터를 추가할 수 있으므로 사용자 승인 후에만 실행합니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-notes.md --sanitized-summary
```

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-scan.pdf --sanitized-summary
```

`--sanitized-summary`는 질문/답변 원문, request id, header, 로컬 project root, stored path를 제외하고 `safe_to_paste=true`, `mode`, `excluded_fields`, step별 status/count만 남깁니다.

검증 명령의 저장 영향:

| 명령 | 서버 필요 | Ollama 필요 | 저장 영향 |
|---|---:|---:|---|
| `.venv/bin/python scripts/local_ci_check.py --root .` | 아니오 | 아니오 | read-only 검증. 파일/DB 수정 없음 |
| `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server` | 예 | 아니오 | assistant 세션/메시지 기록만 SQLite에 추가될 수 있음 |
| `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000` | 예 | 예 | 임시 Markdown/Text 문서를 업로드하므로 SQLite, Chroma, `data/uploads/`에 테스트 데이터 추가 |
| `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --sanitized-summary` | 예 | 예 | 문서/RAG smoke와 저장 영향은 같지만 출력에서 질문/답변 원문, request id, header, local path를 제외 |

## Local Assistant Quick Flow

서버가 실행 중이면 아래 순서만으로 "내 문서 / 내 폴더 기준 로컬 비서" 흐름을 바로 확인할 수 있습니다.

```bash
local-ai doctor
local-ai index-preview ./notes
local-ai index-job-preview ./notes
local-ai index ./notes
local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름 설명해줘"
local-ai assistant
```

`local-ai assistant` 안에서는 일반 질문을 바로 입력하거나, `/search JWT`, `/docs`, `/status`, `/next`, `/summary`처럼 짧은 명령으로 현재 문서와 서버 상태를 확인할 수 있습니다. 기본값에서는 실제 shell 실행, 브라우저 클릭, 파일 생성/수정/삭제는 하지 않고, 위험 작업은 preview 또는 dry-run으로만 다룹니다. 27차부터 `/assistant/shell-run`은 `SHELL_EXECUTION_ENABLED=true`와 서버 발급 approval, allowlist, cwd 제한을 모두 통과한 단건 명령만 제한적으로 실행할 수 있습니다.

## Safe Boundaries

- 런타임 LLM/embedding 호출은 Ollama local API만 사용합니다.
- OpenAI, Claude, Gemini 외부 LLM API를 호출하지 않습니다.
- LangChain과 cloud vector DB를 사용하지 않습니다.
- 서버 실행 예시는 기본적으로 `127.0.0.1` bind를 권장합니다.
- `LOCAL_API_KEY`가 설정되면 보호 endpoint는 `X-API-Key`를 요구합니다.
- 브라우저 클릭/입력/전송 자동화는 구현하지 않습니다.
- shell 관련 기능은 기본값에서 `shell dry-run` 정책 확인과 locked preview만 제공한다. `SHELL_EXECUTION_ENABLED=true`를 명시하면 `/assistant/shell-run`이 allowlist 단건 명령만 실행할 수 있지만 arbitrary shell, pipe/redirect/chaining, install/delete/network command는 계속 차단한다.
- 파일 생성/수정/삭제 자동화는 구현 범위 밖입니다.
- 운영 배포, 클라우드/Oracle 리소스 생성/변경은 이 프로젝트의 현재 범위 밖입니다.

## Capability Boundary Matrix

| 구분 | 현재 상태 | 설명 |
|---|---|---|
| 문서 업로드/검색/RAG | 가능 | `.txt`, `.md`, `.html`, `.htm`, optional `.pdf`, `.docx`를 로컬에서 색인하고 Ollama로 답변합니다. PDF OCR fallback은 `[ocr]` extra와 로컬 tesseract가 있을 때 PyPDF image XObject 범위에서만 동작합니다. |
| 폴더 색인 preview | 가능 | 실제 저장 전 대상 파일, 예상 chunk, 예상 embedding batch를 read-only로 확인합니다. |
| 개인 API 자동화 plan | 가능 | `/assistant/automation-plan`과 `local-ai assistant-automation-plan`으로 현재 가능한 자동화와 막힌 기능을 plan-only로 확인합니다. |
| Agent plan/approval | 가능 | 요청을 action 후보와 위험도로 기록하고 승인/거절 상태를 저장합니다. |
| Agent execution v1 | 조건부 read-only | `AGENT_EXECUTION_ENABLED=true`에서도 허용 root 안의 폴더 목록 조회, 텍스트 파일 preview, 명시 URL 단건 read-only fetch만 지원합니다. Agent web fetch host allowlist는 아직 없으며 private/loopback/link-local host는 차단합니다. |
| Read-only adapter execution | env opt-in read-only | `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`일 때만 `/assistant/read-only-adapter/execute`가 file/list/safe URL adapter를 untrusted wrapper로 반환합니다. |
| Read-only action-loop dispatch | env opt-in read-only | `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 read-only adapter flag가 모두 켜졌을 때만 `/assistant/action-loop-read-only-dispatch`가 read-only adapter를 호출합니다. shell/patch/browser dispatch는 연결하지 않습니다. |
| shell | dry-run only 기본값 / locked preview / env opt-in allowlist execution | `shell-policy`, `shell-dry-run`, `assistant-shell-preview`, `assistant-shell-approval-preview`는 정책 판단과 audit만 반환합니다. `assistant-shell-run`은 기본값 disabled이며 `SHELL_EXECUTION_ENABLED=true`, 서버 approval, cwd allowlist, command allowlist를 모두 통과한 단건만 실행합니다. |
| patch / rollback | locked preview 기본값 / env opt-in single-file apply 또는 restore | `assistant-patch-preview`, `assistant-patch-approval-preview`는 diff preview, secret scan, rollback note, approval binding만 반환합니다. `assistant-patch-apply`는 기본값 disabled이며 `PATCH_APPLY_ENABLED=true`, 서버 approval, `original_sha256`, path allowlist, secret scan을 모두 통과한 기존 UTF-8 단일 파일만 덮어씁니다. 35차 `assistant-rollback-approval-preview`, `assistant-rollback-execute`는 `ROLLBACK_EXECUTOR_ENABLED=true`와 rollback 전용 approval/hash/precondition을 모두 통과한 단일 UTF-8 파일 restore만 허용합니다. |
| full personal automation | env opt-in safe orchestrator | 36차 `POST /assistant/full-automation-preflight`는 shell/patch/read-only/rollback/task/browser/external/app-os 후보를 통합 route plan으로 분류합니다. 38차는 read-only category step, 39차는 allowlist shell category step, 40차는 single-file patch step, 41차는 single-file rollback step, 42차는 `noop`, `read_only_scan`, `file_preview` task queue step, 43차는 browser observe metadata step, 44차는 browser limited candidate validation step, 45차는 `brave` external web search step, 46차는 app-os observe-plan preview step만 기존 boundary로 처리합니다. 47차는 gate/audit/safety matrix가 실제 연결 범위와 일치하도록 고정했습니다. 48차는 Full Automation Action-loop Dispatch Decision Required를 문서/테스트로 고정했고, 61~70차 Local Jarvis runtime drift guard, failure/timeout drill, manual review packet, approval console state-only/hash/cleanup review, API surface Decision Required, approval-console-read-only endpoint는 실제 action-loop full dispatch를 계속 금지합니다. 70차는 read-only pending/list/detail/cleanup만 protected endpoint로 열고 approve/reject routes not added, `approval_consumed=false`, `would_execute=false`, raw approval id/payload_hash 미반환을 유지합니다. 71차 Durable Automation v2 Candidate Decision Required는 durable-automation-v2-candidate-decision-required 상태로 persistence/recovery/replay boundary만 문서화하고 no durable worker started, no scheduler started, no daemon/service/background loop, no automatic replay, no autonomous recovery를 고정합니다. 72차 Durable State Preview Schema Candidate는 durable-state-preview-schema-candidate 상태로 `state_schema_version=durable_state_preview.v1`, `state_status=candidate-preview`, proposal-only contract, schema-only, no durable storage migration, no durable table created, `state_preview_is_not_execution`, `state_preview_does_not_consume_approval`, `state_preview_does_not_mutate_queue`를 고정합니다. 73차 Durable State Preview API Surface Decision Required는 durable-state-preview-api-surface-decision-required 상태로 endpoint exposure remains blocked, no durable-state-preview endpoints added, route_absence_is_required, `would_expose_endpoint=false`를 고정합니다. `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`는 사용자 최종 승인과 Opus 리뷰 전까지 유지됩니다. |
| 브라우저/파일/배포 | 금지 | 29차 단일 파일 patch apply 범위를 제외하면 브라우저 클릭/입력, 폴더 UI 열기, 파일 생성/삭제, bulk write, 운영 배포, 클라우드/Oracle 리소스 변경은 구현하지 않았습니다. |
| 외부 API | 외부 LLM/cloud vector DB 금지 / env opt-in web search | 외부 LLM API와 cloud vector DB는 사용하지 않습니다. 명시 URL 단건 read-only fetch는 LLM API 연동이나 크롤링/브라우저 이동이 아닙니다. 33차부터 `/assistant/web-search-provider/search`는 provider/key/rate/query/wrapper gate를 모두 통과한 `brave` 단건 web search만 env opt-in으로 수행할 수 있습니다. |
| Production hardening | 문서/테스트 계약 완료 | 1~24차 기준 capabilities honesty, locked/preview/read-only/candidate 경계, public release scanner, local CI green 상태를 유지합니다. 운영 배포는 수행하지 않았습니다. |

## Runtime Contract Snapshot

| 항목 | 현재 값 | 기준 |
|---|---:|---|
| FastAPI endpoints | 94 | `build_api_inventory(app.routes).endpoints_count` |
| Protected endpoints | 78 | `build_api_inventory(app.routes).protected_endpoints_count` |
| Public endpoints | 16 | `build_api_inventory(app.routes).public_endpoints_count` |
| Typer CLI commands | 69 | `typer.main.get_command(cli.main.app).commands` |
| Document/RAG smoke steps | 6 | `DOCUMENT_RAG_SMOKE_FLOW` |
| Assistant bridge smoke steps | 8 | `ASSISTANT_BRIDGE_SMOKE_FLOW` |
| Assistant bridge preflight steps | 3 | `ASSISTANT_BRIDGE_PREFLIGHT_FLOW` |

이 표는 README의 요약 숫자가 실제 route, CLI command, smoke flow와 어긋나지 않도록 pytest로 검증합니다.

## Key Docs

- 전체 API 계약: [docs/API.md](docs/API.md)
- 최종 결과 보고: [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md)
- 최종 요약: [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- 작업 보드: [docs/TASKS.md](docs/TASKS.md)
- OCR 통합 계획: [docs/OCR_INTEGRATION_PLAN.md](docs/OCR_INTEGRATION_PLAN.md)
- 실제 사용자 문서 E2E 계획: [docs/USER_DOCUMENT_E2E_PLAN.md](docs/USER_DOCUMENT_E2E_PLAN.md)
- 로컬 운영 Runbook: [docs/OPERATIONS.md](docs/OPERATIONS.md)
- Smoke summary 예시: [docs/SMOKE_SUMMARY_EXAMPLES.md](docs/SMOKE_SUMMARY_EXAMPLES.md)
- Preview 활성화 정책: [docs/PREVIEW_ACTIVATION_POLICY.md](docs/PREVIEW_ACTIVATION_POLICY.md)
- Action-loop 실제 활성화 Decision Required: [docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md](docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md)
- Full personal automation boundary Decision Required: [docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md](docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md)
- Durable Automation v2 candidate Decision Required: [docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md](docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md)
- Durable State Preview Schema Candidate: [docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md](docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md)
- Durable State Preview API Surface Decision Required: [docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md](docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md)
- Local Jarvis v1 candidate Decision Required: [docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md](docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md)
- Local Jarvis approval gate review: [docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md](docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md)
- Read-only adapter 실행 Decision Required: [docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md](docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md)
- Read-only result wrapper schema: [docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md](docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md)
- GitHub 공개 전 체크리스트: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)
- 공개 상태 요약: [docs/PUBLIC_RELEASE_SUMMARY.md](docs/PUBLIC_RELEASE_SUMMARY.md)
- UI 연결 가이드: [docs/UI_CONNECT_GUIDE.md](docs/UI_CONNECT_GUIDE.md)
- UI 필드 치트시트: [docs/UI_CONTRACT_CHEATSHEET.md](docs/UI_CONTRACT_CHEATSHEET.md)
- 브라우저 UI 연동 예시 payload: [docs/UI_BRIDGE_EXAMPLES.md](docs/UI_BRIDGE_EXAMPLES.md)
- 브라우저 UI 수동 QA 기준: [docs/UI_QA_CHECKLIST.md](docs/UI_QA_CHECKLIST.md)
- 문서 정합성 리뷰 handoff: [docs/CLAUDE_REVIEW_HANDOFF.md](docs/CLAUDE_REVIEW_HANDOFF.md)
- Codex 구현/self-review 노트: [docs/CODEX_IMPLEMENTATION_NOTES.md](docs/CODEX_IMPLEMENTATION_NOTES.md)
- OpenAI Codex for OSS 신청 준비: [docs/CODEX_FOR_OSS_APPLICATION.md](docs/CODEX_FOR_OSS_APPLICATION.md)
- 기여 가이드: [CONTRIBUTING.md](CONTRIBUTING.md)
- 작업 기록: [docs/WORKLOG.md](docs/WORKLOG.md)
- 다음 작업 인계: [docs/NEXT_CHAT_HANDOFF.md](docs/NEXT_CHAT_HANDOFF.md)
- 보안 기준: [SECURITY.md](SECURITY.md)
- 라이선스: [LICENSE](LICENSE)

## 개발 배경

개인 문서 기반 Q&A를 만들 때 외부 LLM API로 문서 내용이 전송되는 구조는 비용, 개인정보, 재현성 측면에서 부담이 있습니다. 이 프로젝트는 로컬 모델과 로컬 저장소만으로 문서 업로드, 색인, 검색, RAG 답변, 피드백 수집, SFT 데이터 export까지 이어지는 백엔드 흐름을 검증하기 위해 만들었습니다.

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

## 포트폴리오 포인트

이 프로젝트에서 맡은 역할은 백엔드 API 설계, 로컬 RAG 파이프라인 구현, SQLite/Chroma 저장소 분리, Typer CLI, 테스트/문서/보안 기준 정리까지 포함한 end-to-end 구현입니다.

강조할 수 있는 학습 포인트:

- FastAPI route를 얇게 유지하고 service 계층에 비즈니스 로직을 모으는 구조
- SQLite와 Chroma를 각각 metadata source of truth와 vector search 전용 저장소로 분리한 설계
- 외부 LLM API 없이 Ollama local `/api/chat`, `/api/embed`만 사용하는 로컬 AI 흐름
- 문서 업로드, chunking, embedding batch, RAG 답변, feedback, SFT export로 이어지는 데이터 흐름
- 실제 실행 기능을 바로 열지 않고 preview, dry-run, approval, protected endpoint로 나눈 안전 설계
- README/API/보안 문서 예시가 실제 Pydantic schema와 어긋나지 않도록 테스트로 고정한 문서 품질 관리

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

PDF/DOCX 문서까지 색인하려면 optional dependency를 추가로 설치합니다. 일반 PDF/DOCX 텍스트 추출은 Python 패키지만 사용합니다.

```bash
pip install -e ".[dev,documents]"
```

이미지 기반 PDF 페이지 OCR fallback까지 쓰려면 Python OCR extra와 로컬 `tesseract` binary가 필요합니다. 시스템 패키지는 자동 설치하지 않습니다.

```bash
pip install -e ".[dev,documents,ocr]"
brew install tesseract
```

Ubuntu/Debian에서는 `sudo apt install tesseract-ocr`를 사용하세요. 한국어 OCR이 필요하면 `tesseract --list-langs`에서 `kor` 지원 여부를 확인하고 language pack을 별도로 설치하세요.

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

## API endpoint inventory

현재 공개 문서에서 다루는 FastAPI endpoint 목록입니다. 상세 payload와 응답 필드는 [docs/API.md](docs/API.md)를 기준으로 확인합니다.

Health/Ask/Search:

- `GET /health`
- `GET /health/ollama`
- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`

Documents:

- `POST /documents/upload`
- `GET /documents`
- `GET /documents/supported-types`
- `GET /documents/stats`
- `GET /documents/integrity`
- `GET /documents/repair-preview`
- `GET /documents/vector-rebuild-preview`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/chunks`
- `DELETE /documents/{document_id}`
- `POST /documents/index-folder`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder-job-preview`

Chat/Feedback:

- `GET /chat-logs`
- `GET /chat-logs/{chat_log_id}`
- `GET /feedback`
- `POST /feedback`

Agent/Project:

- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`
- `GET /agent/runs/{run_id}/results`
- `GET /agent/runs/{run_id}/actions`
- `POST /agent/runs/{run_id}/dry-run`
- `POST /agent/runs/{run_id}/approve`
- `POST /agent/runs/{run_id}/reject`
- `POST /agent/runs/{run_id}/execute`
- `GET /project/status`
- `GET /project/next`
- `GET /project/api-inventory`
- `GET /project/shell-policy`
- `POST /project/shell-dry-run`

Assistant UI bridge:

- `GET /assistant/capabilities`
- `POST /assistant/action-preview`
- `POST /assistant/action-loop-preflight`
- `POST /assistant/action-loop-noop-dispatch`
- `POST /assistant/action-loop-read-only-dispatch-preview`
- `POST /assistant/action-loop-read-only-dispatch`
- `POST /assistant/action-loop-shell-dispatch`
- `POST /assistant/action-loop-patch-dispatch`
- `POST /assistant/full-automation-preflight`
- `POST /assistant/full-automation-dispatch`
- `POST /assistant/automation-plan`
- `GET /assistant/workflow-presets`
- `GET /assistant/workflow-presets/{preset_id}`
- `POST /assistant/workflow-presets/{preset_id}/preview`
- `POST /assistant/task-queue/preview`
- `GET /assistant/task-queue`
- `POST /assistant/task-queue/drain`
- `GET /assistant/task-queue/{task_id}`
- `POST /assistant/task-queue/{task_id}/cancel-preview`
- `POST /assistant/failure-recovery-preview`
- `POST /assistant/rollback-approval-preview`
- `POST /assistant/rollback-execute`
- `POST /assistant/read-only-scan`
- `POST /assistant/file-preview`
- `POST /assistant/url-preview`
- `POST /assistant/read-only-adapter/execute`
- `POST /assistant/web-search-provider-preview`
- `POST /assistant/web-search-provider/search`
- `POST /assistant/app-os-interaction-preview`
- `POST /assistant/workspace-brief`
- `POST /assistant/shell-preview`
- `POST /assistant/shell-approval-preview`
- `POST /assistant/shell-run`
- `POST /assistant/durable-state-preview/preview`
- `GET /assistant/approval-console/pending`
- `GET /assistant/approval-console/{approval_id}`
- `POST /assistant/approval-console/cleanup-expired`
- `POST /assistant/patch-preview`
- `POST /assistant/patch-approval-preview`
- `POST /assistant/patch-apply`
- `POST /assistant/browser-preview`
- `POST /assistant/browser-approval-preview`
- `POST /assistant/browser-interact`
- `POST /assistant/browser-observe`
- `POST /assistant/browser-limited-interact`
- `GET /assistant/ui-contract`
- `GET /assistant/startup`
- `GET /assistant/ping`
- `GET /assistant/config`
- `GET /assistant/status`
- `GET /assistant/dashboard`
- `POST /assistant/bootstrap`
- `POST /assistant/sessions`
- `GET /assistant/sessions`
- `GET /assistant/sessions/{session_id}`
- `GET /assistant/sessions/{session_id}/messages`
- `POST /assistant/message`
- `POST /assistant/project-root/validate`

## 문서 업로드

기본 텍스트 문서는 `.txt`, `.md`, `.html`, `.htm`을 지원합니다. HTML은 UTF-8 파일에서 본문 텍스트를 추출하고 `script`, `style`, `head` 내용은 제외합니다. PDF/DOCX는 `pip install -e ".[dev,documents]"`로 optional dependency를 설치한 경우 사용할 수 있습니다. 이미지 기반 PDF 페이지는 `pip install -e ".[dev,documents,ocr]"`와 로컬 `tesseract`가 준비된 경우에만 OCR fallback을 시도합니다.

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
local-ai index-job-preview ./backend-study
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
local-ai assistant-action-loop-preflight "개인 API dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-action-loop-noop-dispatch "개인 API dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-action-loop-read-only-dispatch-preview "read only dispatch" --project-root /Users/juyoung/local-ai-server
local-ai assistant-automation-plan "내 개인 API 자동화" --project-root /Users/juyoung/local-ai-server
local-ai assistant-read-only-scan /Users/juyoung/local-ai-server
local-ai assistant-file-preview /Users/juyoung/local-ai-server/README.md --project-root /Users/juyoung/local-ai-server
local-ai assistant-url-preview https://example.com
local-ai assistant-workspace-brief /Users/juyoung/local-ai-server
local-ai assistant-shell-preview "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-shell-approval-preview "git status" --cwd /Users/juyoung/local-ai-server --reason "local CI"
local-ai assistant-shell-run "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-patch-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-patch-approval-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server" --reason "docs"
local-ai assistant-patch-apply /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-browser-preview observe --target-url https://example.com
local-ai assistant-browser-approval-preview screenshot --target-url https://example.com --reason "read-only QA"
local-ai assistant-browser-interact observe --target-url https://example.com
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
/shell-preview <command>
/shell-approval-preview <command>
/shell-run <command>
/patch-preview <path>
/patch-approval-preview <path>
/patch-apply <path>
/browser-preview <action>
/browser-approval-preview <action>
/browser-interact <action>
/action-loop-preflight <goal>
/action-loop-noop-dispatch <goal>
/action-loop-read-only-dispatch-preview <goal>
/api-inventory
/capabilities
/automation-plan <goal>
/workspace-brief <project_root>
/file-preview <path>
/url-preview <url>
/root <project_root>
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
- `GET /documents/vector-rebuild-preview`

```bash
curl http://127.0.0.1:8000/documents/stats
curl http://127.0.0.1:8000/documents/integrity
curl http://127.0.0.1:8000/documents/repair-preview
local-ai stats
local-ai integrity
local-ai repair-preview
local-ai vector-rebuild-preview
```

현재 환경에서 사용할 수 있는 문서 타입, optional dependency, PDF OCR fallback 준비 상태는 다음 명령으로 확인합니다.

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
- `POST /documents/index-folder-job-preview`
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
- `POST /assistant/action-loop-preflight`
- `POST /assistant/action-loop-noop-dispatch`
- `POST /assistant/action-loop-read-only-dispatch-preview`
- `POST /assistant/action-loop-read-only-dispatch`
- `POST /assistant/action-loop-shell-dispatch`
- `POST /assistant/action-loop-patch-dispatch`
- `POST /assistant/full-automation-preflight`
- `POST /assistant/full-automation-dispatch`
- `POST /assistant/automation-plan`
- `GET /assistant/workflow-presets`
- `GET /assistant/workflow-presets/{preset_id}`
- `POST /assistant/workflow-presets/{preset_id}/preview`
- `POST /assistant/task-queue/preview`
- `GET /assistant/task-queue`
- `POST /assistant/task-queue/drain`
- `GET /assistant/task-queue/{task_id}`
- `POST /assistant/task-queue/{task_id}/cancel-preview`
- `POST /assistant/failure-recovery-preview`
- `POST /assistant/rollback-approval-preview`
- `POST /assistant/rollback-execute`
- `POST /assistant/read-only-scan`
- `POST /assistant/file-preview`
- `POST /assistant/url-preview`
- `POST /assistant/read-only-adapter/execute`
- `POST /assistant/web-search-provider-preview`
- `POST /assistant/web-search-provider/search`
- `POST /assistant/app-os-interaction-preview`
- `POST /assistant/workspace-brief`
- `POST /assistant/shell-preview`
- `POST /assistant/shell-approval-preview`
- `POST /assistant/shell-run`
- `POST /assistant/durable-state-preview/preview`
- `GET /assistant/approval-console/pending`
- `GET /assistant/approval-console/{approval_id}`
- `POST /assistant/approval-console/cleanup-expired`
- `POST /assistant/patch-preview`
- `POST /assistant/patch-approval-preview`
- `POST /assistant/patch-apply`
- `POST /assistant/browser-preview`
- `POST /assistant/browser-approval-preview`
- `POST /assistant/browser-interact`
- `POST /assistant/browser-observe`
- `POST /assistant/browser-limited-interact`
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
curl http://127.0.0.1:8000/project/api-inventory
curl -H "X-API-Key: change-me" http://127.0.0.1:8000/project/shell-policy
local-ai status
local-ai next
local-ai api-inventory
```

`local-ai status`는 완료 차수와 현재 차수를 함께 보여주고, `local-ai next`는 다음에 Codex가 계속 진행하기 좋은 안전 작업만 요약합니다. `project/status`, `project/next`, `project/api-inventory`는 조회 전용 continuation endpoint이고, shell dry-run 정책 endpoint는 명령 후보가 포함될 수 있어 `LOCAL_API_KEY` 설정 시 보호됩니다. shell 실행, 파일 수정/삭제, 브라우저 interaction, 배포, fine-tuning 실행은 여전히 별도 승인 전 보류 항목으로 표시됩니다.

지원 endpoint:

- `GET /project/status`: 현재 완료 차수와 다음 안전 작업 조회
- `GET /project/next`: 다음 작업 후보와 Recommended Next Model 조회
- `GET /project/api-inventory`: endpoint 목록, tag, 보호 여부를 read-only로 조회
- `GET /project/shell-policy`: shell dry-run 정책 조회
- `POST /project/shell-dry-run`: 실제 실행 없이 shell 명령 후보의 정책 판단만 조회

CLI 대응:

- `local-ai status`
- `local-ai next`
- `local-ai api-inventory`
- `local-ai shell-policy`
- `local-ai shell-dry-run "pwd"`

## Local Assistant Automation

`local-ai assistant`는 세션 안에서 짧은 요약과 온보딩 상태를 확인할 수 있습니다.

- `/summary`: 현재 assistant 세션의 질문 수, 명령 수, 최근 질문, 사용한 source를 메모리 안에서 요약합니다. 파일 저장이나 fine-tuning은 수행하지 않습니다.
- `/roots`: `AGENT_ALLOWED_ROOTS` 기준으로 Agent가 read-only 접근할 수 있는 root와 존재 여부를 보여줍니다.
- `/shell-policy`: shell dry-run allowlist와 blocked token을 보여줍니다.
- `/shell-dry-run <command>`: 실제 shell 실행 없이 명령이 허용 후보인지 정책 판단만 반환합니다.
- `/shell-preview <command>`: 5차 shell sandbox allowlist, cwd, timeout, masking, audit payload를 preview합니다.
- `/shell-approval-preview <command>`: 서버 발급 single-use approval id와 payload hash binding을 preview store에 생성합니다.
- `/shell-run <command>`: 기본값 locked/disabled라 실제 subprocess 실행 없이 차단 상태를 반환합니다. `SHELL_EXECUTION_ENABLED=true`와 유효한 서버 approval이 있을 때만 allowlist 단건 명령을 실행합니다.
- `/patch-preview <path>`: 6차 patch sandbox diff, secret scan, rollback note, audit payload를 preview합니다.
- `/patch-approval-preview <path>`: 서버 발급 single-use approval id와 payload hash binding을 preview store에 생성합니다.
- `/patch-apply <path>`: 기본값 locked/disabled라 실제 파일 수정 없이 차단 상태를 반환합니다. `PATCH_APPLY_ENABLED=true`와 유효한 서버 approval, `original_sha256` precondition이 있을 때만 기존 UTF-8 단일 파일을 덮어씁니다.
- `/browser-preview <action>`: 7차 browser/app interaction taxonomy와 audit payload를 preview합니다.
- `/browser-approval-preview <action>`: 서버 발급 single-use approval id와 payload hash binding을 preview store에 생성합니다.
- `/browser-interact <action>`: endpoint는 있지만 기본값 locked/disabled라 실제 browser/app interaction 없이 차단 상태를 반환합니다.
- `/assistant/browser-observe`: 31차 Browser Observe v1 HTTP endpoint입니다. 기본값 disabled이고, `BROWSER_OBSERVE_ENABLED=true`와 유효한 서버 approval이 있을 때만 loopback/명시 allowlist URL의 read-only metadata를 untrusted wrapper로 반환합니다.
- `/assistant/browser-limited-interact`: 32차 Browser Limited Interaction v1 HTTP endpoint입니다. 기본값 disabled이고, `BROWSER_LIMITED_INTERACTION_ENABLED=true`에서도 selector/origin/field/approval 후보 검증만 수행하며 실제 browser launch/click/fill은 아직 연결하지 않습니다.
- `/api-inventory`: 현재 FastAPI endpoint 목록과 API key 보호 여부를 read-only로 보여줍니다.
- `/automation-plan <goal>`: 개인 API 자동화 목표를 현재 안전 경계 기준의 단계별 plan-only 응답으로 정리합니다.
- `/workspace-brief <project_root>`: 프로젝트 구조, 중요 파일, 짧은 masked preview를 read-only로 요약합니다.
- `/file-preview <path>`: 허용 root 안의 텍스트 파일만 secret-like 값을 masking해 preview합니다.
- `/url-preview <url>`: 네트워크 호출 없이 URL read-only fetch 가능 조건과 차단 이유를 확인합니다.
- `/status`, `/next`: 차수와 다음 안전 작업을 REPL 안에서 확인합니다.

CLI에서도 같은 내용을 확인할 수 있습니다.

```bash
local-ai roots
local-ai api-inventory
local-ai shell-policy
local-ai shell-dry-run "pwd"
local-ai assistant-automation-plan "내 개인 API 자동화" --project-root /Users/juyoung/local-ai-server
local-ai assistant-read-only-scan /Users/juyoung/local-ai-server
local-ai assistant-file-preview /Users/juyoung/local-ai-server/README.md --project-root /Users/juyoung/local-ai-server
local-ai assistant-url-preview https://example.com
local-ai assistant-workspace-brief /Users/juyoung/local-ai-server
local-ai assistant-shell-preview "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-shell-approval-preview "git status" --cwd /Users/juyoung/local-ai-server --reason "local CI"
local-ai assistant-shell-run "git status" --cwd /Users/juyoung/local-ai-server
local-ai assistant-patch-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-patch-approval-preview /Users/juyoung/local-ai-server/README.md "# local-ai-server" --reason "docs"
local-ai assistant-patch-apply /Users/juyoung/local-ai-server/README.md "# local-ai-server"
local-ai assistant-browser-preview observe --target-url https://example.com
local-ai assistant-browser-approval-preview screenshot --target-url https://example.com --reason "read-only QA"
local-ai assistant-browser-interact observe --target-url https://example.com
```

## UI Bridge Assistant API

브라우저 기반 로컬 비서 UI는 `/assistant/ping`으로 연결/token 상태를 빠르게 확인하고, `/assistant/config`로 secret 없이 안전 설정을 읽고, `/assistant/dashboard`로 첫 화면 카드를 구성할 수 있습니다. 시작 시에는 `/assistant/startup`으로 `ping`, `config`, `dashboard`, `ui_contract`를 한 번에 읽을 수 있고, project root가 준비되면 `/assistant/bootstrap`으로 기능, 상태, project root 검증, 최근 세션 목록, UI 힌트를 받을 수 있습니다. 개인 API 자동화 방향은 `/assistant/automation-plan`으로 plan-only 확인하고, 4차 read-only 자동화는 `/assistant/read-only-scan`, `/assistant/file-preview`, `/assistant/url-preview`, `/assistant/workspace-brief`로 확인합니다. 5차 shell sandbox는 `/assistant/shell-preview`, `/assistant/shell-approval-preview`, `/assistant/shell-run`으로 allowlist와 approval binding을 확인하고, 27차부터 `/assistant/shell-run`은 `SHELL_EXECUTION_ENABLED=true`일 때만 allowlist 단건 subprocess를 실행합니다. 6차 patch sandbox는 `/assistant/patch-preview`, `/assistant/patch-approval-preview`, `/assistant/patch-apply`로 diff preview, secret scan, rollback note, locked-apply audit을 확인하고, 29차부터 `/assistant/patch-apply`는 `PATCH_APPLY_ENABLED=true`일 때만 승인된 기존 UTF-8 단일 파일을 `original_sha256` precondition으로 덮어쓸 수 있습니다. 35차 rollback executor는 `/assistant/rollback-approval-preview`, `/assistant/rollback-execute`에서 `ROLLBACK_EXECUTOR_ENABLED=true`와 rollback 전용 approval/hash/precondition을 모두 통과한 단일 UTF-8 파일 restore만 허용합니다. 7차 browser/app interaction sandbox는 `/assistant/browser-preview`, `/assistant/browser-approval-preview`, `/assistant/browser-interact`로 read-only taxonomy preview와 locked-interact audit만 확인하며 실제 click/fill/submit/login/payment/delete 또는 OS app control은 하지 않습니다. 31차 Browser Observe v1은 `/assistant/browser-observe`에서 `BROWSER_OBSERVE_ENABLED=true`와 유효한 서버 approval이 있을 때만 loopback/명시 allowlist URL의 title/current URL 같은 read-only metadata를 untrusted wrapper로 반환하고, browser click/fill/profile/session mutation과 action-loop 연결은 하지 않습니다. 32차 Browser Limited Interaction v1은 `/assistant/browser-limited-interact`에서 `BROWSER_LIMITED_INTERACTION_ENABLED=true`와 유효한 approval, origin/selector/fill-field allowlist를 검증하지만 실제 browser launch/click/fill/profile/session mutation과 action-loop 연결은 하지 않습니다. 8차 action-loop preflight는 `/assistant/action-loop-preflight`로 frozen plan, wrapper, approval binding, payload hash gate만 확인하며 실제 dispatch는 하지 않습니다. 10차 no-op dispatcher는 `/assistant/action-loop-noop-dispatch`로 route plan과 noop audit만 반환하고 approval은 validate-only로 확인합니다. 11차 read-only boundary는 `/assistant/action-loop-read-only-dispatch-preview`로 adapter routing만 분류하며 파일 읽기, 폴더 스캔, URL fetch를 수행하지 않습니다. 21차 workflow presets는 `/assistant/workflow-presets` 계열로 frozen proposed_steps 후보만 만들고, 22차 long-running task queue는 `/assistant/task-queue` 계열로 no-op/read-only task 상태와 cancellation state를 반환합니다. 34차 task queue worker는 `/assistant/task-queue/drain`에서 `TASK_QUEUE_WORKER_ENABLED=true`일 때만 request-scoped one-shot drain으로 `noop`, `read_only_scan`, `file_preview` task를 처리하며 daemon/service/background loop를 시작하지 않습니다. 23차 failure recovery는 `/assistant/failure-recovery-preview`로 failure reason taxonomy와 rollback plan만 반환하며 자동 rollback, git reset, file restore, shell execution, browser interaction은 하지 않습니다. 13차 result wrapper schema는 [docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md](docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md)에 고정되어 있고 raw content, approval-like JSON, next step mutation을 신뢰하지 않습니다. read-only adapter execution은 25차부터 env opt-in과 untrusted wrapper 조건에서만 활성화됩니다. 실제 메시지는 기능별 endpoint를 직접 조합하지 않고 `/assistant/message` 하나로 보낼 수 있습니다.

24차 Production Hardening 기준으로 `/assistant/capabilities`는 위험 기능을 enabled로 광고하지 않고, shell/patch/browser/action-loop/task-queue/rollback/external API는 disabled, blocked, locked, preview-only 또는 명시 env opt-in 상태로 표시한다. 25차 Read-only Adapter Execution은 `POST /assistant/read-only-adapter/execute`에서 `READ_ONLY_ADAPTER_EXECUTION_ENABLED=true`와 untrusted result wrapper가 있을 때만 file/list/safe URL adapter를 실제 read-only로 실행한다. 26차 Read-only Action-loop Dispatch는 `POST /assistant/action-loop-read-only-dispatch`에서 `READ_ONLY_ACTION_LOOP_DISPATCH_ENABLED=true`와 read-only adapter flag가 모두 켜졌을 때만 read-only adapter를 호출하며 shell/patch/browser에는 연결하지 않는다. 28차 Shell Action-loop Dispatch는 `POST /assistant/action-loop-shell-dispatch`에서 `SHELL_ACTION_LOOP_DISPATCH_ENABLED=true`와 `SHELL_EXECUTION_ENABLED=true`가 모두 켜졌을 때만 27차 allowlist shell step을 호출한다. 30차 Patch Action-loop Dispatch는 `POST /assistant/action-loop-patch-dispatch`에서 `PATCH_ACTION_LOOP_DISPATCH_ENABLED=true`와 `PATCH_APPLY_ENABLED=true`가 모두 켜졌을 때만 29차 단일 파일 patch step을 호출한다. 33차 External Web Search Provider v1은 `POST /assistant/web-search-provider/search`에서 `EXTERNAL_WEB_SEARCH_ENABLED=true`, `EXTERNAL_WEB_SEARCH_PROVIDER=brave`, API key, rate limit, query safety, untrusted wrapper가 모두 통과한 단건 search만 수행한다. 34차 Task Queue Worker v1은 `POST /assistant/task-queue/drain`에서 `TASK_QUEUE_WORKER_ENABLED=true`일 때만 one-shot drain으로 제한되며 shell/browser/external API/rollback/app-os task는 연결하지 않는다. 35차 Rollback Executor Boundary는 `POST /assistant/rollback-execute`에서 `ROLLBACK_EXECUTOR_ENABLED=true`일 때만 rollback 전용 approval과 hash precondition을 통과한 단일 파일 restore만 수행한다. 46차 Full Automation App-OS Preview는 `POST /assistant/full-automation-dispatch`에서 app_os category step을 observe-plan preview wrapper로만 중첩하며 실제 app open/click/type/hotkey/file dialog는 수행하지 않는다. 47차 Policy/Audit Hardening은 `actual_connector_execution_connected`, `preview_connector_execution_connected`, `mutating_connector_execution_connected`, `browser_actual_interaction_connected`, `app_os_actual_action_connected`, `action_loop_full_dispatch_connected`를 gate/audit/safety에서 명시한다. 48차 Full Automation Action-loop Dispatch Decision Required와 61~70차 Local Jarvis 문서/API 계약은 실제 action-loop full dispatch는 계속 금지하고, approval console approve/reject도 state-only로 유지한다. 70차는 `GET /assistant/approval-console/pending`, `GET /assistant/approval-console/{approval_id}`, `POST /assistant/approval-console/cleanup-expired`만 approval-console-read-only로 추가했다. approve/reject routes not added, protected endpoint only, masked response only, raw approval id not included, payload_hash not included, `audit_summary_hash`, `approval_consumed=false`, `would_execute=false`, cleanup is not approval consume 원칙을 유지한다. connector별 approval consume, rollback/failure strategy, 사용자 최종 승인, Opus 리뷰 전까지 `action_loop_full_dispatch_connected=false`, `browser_actual_interaction_connected=false`, `app_os_actual_action_connected=false`를 유지한다고 문서/테스트로 고정했다.

브라우저 UI를 붙이는 기본 순서는 아래처럼 잡으면 됩니다.

1. `GET /assistant/startup`: token, CORS, 모델, dashboard, UI contract snapshot을 한 번에 읽습니다.
2. `POST /assistant/bootstrap`: 사용자가 입력한 project root와 최근 session 상태를 확인합니다.
3. `POST /assistant/action-preview`: 메시지를 보내기 전에 intent, 위험도, 필요한 입력값을 preview합니다.
4. `POST /assistant/automation-plan`: 자동화 목표가 있으면 현재 가능/차단/승인 필요 범위를 plan-only로 확인합니다.
5. `POST /assistant/workspace-brief`: 4차 read-only 자동화로 프로젝트 구조와 중요 파일 preview를 확인합니다.
6. `POST /assistant/shell-preview`: shell 후보는 실행 전 allowlist, cwd, timeout, masking, audit payload만 확인합니다.
7. `POST /assistant/patch-preview`: patch 후보는 diff, secret scan, rollback note, audit payload만 확인합니다.
8. `POST /assistant/message`: 사용자가 확인한 메시지를 보내고 `ui.response_type` 기준으로 렌더링합니다.
9. `GET /assistant/sessions/{session_id}/messages`: 긴 대화 기록은 paging으로 가져옵니다.

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

`/assistant/message` 응답에는 UI가 바로 렌더링에 참고할 수 있는 `ui.response_type`, `ui.severity`, `ui.primary_text`, `ui.display` 힌트가 포함됩니다. 폴더 색인은 preview까지만 수행하고, shell은 message route에서는 dry-run 정책 판단만 수행합니다. `/assistant/shell-run`의 실제 allowlist subprocess 실행은 별도 endpoint, `SHELL_EXECUTION_ENABLED=true`, 서버 approval이 필요합니다. patch apply는 별도 endpoint에서 `PATCH_APPLY_ENABLED=true`, 서버 approval, `original_sha256` precondition이 있을 때만 기존 UTF-8 단일 파일에 제한됩니다. 브라우저 클릭, 파일 생성/삭제, bulk write, arbitrary shell 실행은 하지 않습니다.

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

`local-ai vector-rebuild-preview`는 Chroma vector가 누락된 SQLite chunk만 대상으로 재생성 후보를 미리 보여줍니다. 이 명령도 read-only이며 실제 Ollama embedding 생성, Chroma 수정, DB 수정은 수행하지 않습니다.

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
.venv/bin/pytest
```

전체 로컬 검증을 한 번에 실행하려면 아래 명령을 사용합니다.

```bash
.venv/bin/python scripts/local_ci_check.py --root .
.venv/bin/python scripts/local_ci_check.py --root . --json
```

이 스크립트는 `pytest`, `compileall`, public release check, `git diff --check`를 순서대로 실행합니다. 실패가 발생하면 그 단계에서 멈추며, 시스템 의존성 설치나 배포는 수행하지 않습니다.

내부 실행 단계는 아래와 같습니다.

- `.venv/bin/python -m pytest`
- `.venv/bin/python -m compileall app cli scripts`
- `.venv/bin/python scripts/public_release_check.py --root . --json`
- `git diff --check`

## E2E Smoke Test

서버와 Ollama 모델이 실행 중일 때 임시 Markdown/Text 문서로 `health → upload → search → ask-with-docs → feedback → stats` 흐름을 확인할 수 있습니다. 기본 샘플은 `smoke-backend-notes.md`와 `smoke-architecture-notes.txt`이며, `.md`와 `.txt` 업로드가 같은 RAG 흐름에서 함께 동작하는지 확인합니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000
```

`LOCAL_API_KEY`가 설정되어 있으면 smoke test도 자동으로 `X-API-Key` 헤더를 보냅니다. 이 스크립트는 테스트용 Markdown/Text 문서를 업로드하므로 SQLite, Chroma, `data/uploads/`에 테스트 데이터가 추가됩니다. 자동 삭제는 수행하지 않습니다.

브라우저 조작 없이 Assistant UI bridge 계약만 확인하려면 아래처럼 실행합니다. 이 흐름은 업로드/RAG/Ollama 호출을 피하고 `assistant-startup → api-inventory → assistant-bootstrap → action-preview → read-only-result-wrapper → assistant-message(auto/status intent) → sessions → messages`만 확인합니다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
```

`--assistant-bridge-only`는 `/assistant/message`를 `mode=auto`와 상태 질문으로 호출해 status intent로 분기하므로 외부 LLM API나 Ollama 답변 생성은 사용하지 않습니다. 다만 assistant session/message 확인을 위해 SQLite에 세션과 메시지 기록은 추가됩니다.

## GitHub 공개 전 보안 점검

로컬 데이터와 secret 후보가 공개 대상에 섞여 있는지 read-only로 점검할 수 있습니다.

```bash
.venv/bin/python scripts/public_release_check.py --root . --json
```

현재 로컬 DB, Chroma index, 업로드 파일이 있으면 이 스크립트는 실패 코드와 함께 항목을 출력합니다. 삭제는 수행하지 않으며, 공개 전 `.gitignore`와 실제 포함 파일을 확인하기 위한 안전장치입니다.

## 실제 RAG 검증 상태

현재 로컬 환경에서 아래 흐름을 확인했습니다.

- `local-ai doctor`: `llm_model_ready=true`, `embedding_model_ready=true`
- `local-ai stats`: SQLite/Chroma 저장 상태 확인 성공
- `local-ai integrity`: SQLite/Chroma 정합성 점검 성공
- `local-ai repair-preview`: repair action 미리보기 성공
- `local-ai vector-rebuild-preview`: 누락 vector 재생성 후보 미리보기 성공
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
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000`: 임시 Markdown/Text 문서 기반 API smoke test 가능
- `python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server`: 브라우저 조작 없는 Assistant UI bridge smoke test 가능
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
- 이미지 기반 PDF OCR이 필요하면 `pip install -e ".[dev,documents,ocr]"`와 로컬 `tesseract` 설치 상태를 확인합니다.
- UTF-8 텍스트 파일만 지원합니다.

### 401 응답이 나옵니다

- `LOCAL_API_KEY`가 설정되어 있으면 `X-API-Key` 헤더를 보내야 합니다.

## 현재 한계

- PDF/DOCX는 optional dependency 설치 시 텍스트 추출을 지원합니다. PDF OCR fallback은 PyPDF로 추출 가능한 image XObject가 있는 페이지에 한정되며, flat scan PDF나 page rendering이 필요한 PDF는 아직 지원하지 않습니다.
- HTML/HTM은 표준 라이브러리 기반 텍스트 추출을 지원하지만, JavaScript 렌더링 결과나 동적 페이지 크롤링은 지원하지 않습니다.
- Chroma와 SQLite 동기화 복구는 read-only 점검과 repair preview까지만 지원합니다. 실제 repair/rebuild는 아직 수행하지 않습니다.
- 실행형 Agent는 계획, 승인, read-only 실행 엔진 v1 단계입니다. 실제 웹 이동, 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 아직 수행하지 않습니다.
- 실행 엔진 v1은 승인된 run에 대해 허용 root 안의 폴더 목록 조회와 텍스트 파일 내용 preview만 지원합니다. 웹 fetch는 `AGENT_WEB_FETCH_ENABLED=true`와 명시 URL이 있을 때만 read-only로 동작하며, `AGENT_WEB_FETCH_MAX_BYTES` 이후 응답을 자릅니다.
- Agent web fetch host allowlist는 아직 구현하지 않았고, private/loopback/link-local host는 차단합니다.
- embedding은 batch 처리되고 preview에서 예상 batch 수를 볼 수 있지만, 매우 큰 문서의 실시간 진행률 표시는 아직 없습니다.
- 자동 로그 rotation은 아직 구현하지 않았고, 운영 로그 정책은 문서로만 제공합니다.
- 인증은 로컬 API key 수준이며, 다중 사용자 권한 관리는 없습니다.
- 보호 endpoint에는 process-local in-memory rate limit이 적용됩니다. 다중 worker/분산 환경용 rate limit은 아직 지원하지 않습니다.
- HTTPS termination은 애플리케이션에서 직접 제공하지 않으며, 외부 공개가 필요하면 reverse proxy와 TLS 설정을 별도로 검토해야 합니다.

## 다음 추천 개선

Codex가 바로 이어서 할 수 있는 안전한 개선:

1. README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트와 runtime endpoint count drift check 유지
2. README/Project Summary Runtime Contract Snapshot 값을 실제 API/CLI/smoke flow inventory와 비교하는 계약 유지
3. 승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary가 민감 정보 없이 유지되는지 검증
4. 대용량 색인 job/status API progress response schema preview-only 계약을 기준으로 실제 queue 활성화 조건 문서 유지
5. Chroma 누락 vector 재생성 preview-only endpoint를 기준으로 실제 rebuild 활성화 조건 문서 유지
6. assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 표시 기준과 함께 유지
7. PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지

별도 승인 또는 보안 리뷰가 필요한 개선:

1. 실제 repair/delete/rebuild 실행 명령
2. 실제 브라우저 click/fill/submit 자동화
3. 실제 shell 실행 또는 파일 생성/수정/삭제 자동화
4. JavaScript 렌더링, 외부 URL 크롤링, pdf2image/poppler 기반 page rendering OCR 확장
5. 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit
6. DB migration, 운영 데이터 변경, 비용이 발생할 수 있는 cloud/Oracle 리소스 사용

## 배포 상태

- 현재 구현은 로컬 실행 기준입니다.
- 외부 클라우드 배포는 구현하지 않았습니다.
- 외부 클라우드 credential, API key, DB password는 사용하지 않습니다.
- DB migration, 운영 데이터 변경, 비용이 발생할 수 있는 리소스 사용은 수행하지 않았습니다.
