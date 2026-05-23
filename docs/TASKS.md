# TASKS

이 문서는 `local-ai-server`의 다음 작업을 안전 범위별로 나누어 추적한다.

현재 프로젝트는 로컬 전용 FastAPI/Ollama/SQLite/Chroma 백엔드와 Typer CLI를 구현한 상태다. 다음 작업은 기본적으로 문서, 테스트, API 계약, smoke 검증 중심으로 진행한다.

## 상태 기준

| 상태 | 의미 | 진행 조건 |
|---|---|---|
| `done` | 구현, 문서화, 테스트가 완료된 항목 | 검증 결과를 `docs/WORKLOG.md`에 기록 |
| `safe-next` | Codex가 바로 이어서 할 수 있는 안전 작업 | 외부 LLM API, 실제 shell 실행, 파일 수정/삭제 자동화, 브라우저 interaction 없음 |
| `manual-check` | 사용자가 로컬 화면 또는 실제 서버에서 확인해야 하는 작업 | Codex가 브라우저 조작이나 메시지 전송을 대신하지 않음 |
| `review-required` | 보안/운영 리뷰 또는 사용자 승인이 필요한 작업 | 실제 실행, 삭제, 배포, 외부 호출, 비용/보안 영향 가능 |
| `blocked` | 현재 범위 밖 작업 | 별도 설계와 승인 전 진행하지 않음 |

## 완료된 핵심 작업

- [x] FastAPI MVP와 `/health`, `/ask`
- [x] SQLite metadata, chunk, chat log, feedback 저장
- [x] `.txt`, `.md`, `.html`, `.htm`, optional `.pdf`, `.docx` 문서 로더
- [x] Chroma vector search와 Ollama local embedding
- [x] `/ask-with-docs` RAG 답변 API
- [x] 폴더 색인과 read-only index preview
- [x] Typer 기반 `local-ai` CLI
- [x] feedback 저장과 SFT JSONL export
- [x] assistant bridge API와 CLI
- [x] project continuation API, API inventory, shell dry-run policy
- [x] agent plan/approval/read-only execution v1
- [x] public release check와 local CI script
- [x] README, API, 운영, 보안, 최종 보고 문서

## Codex가 바로 이어서 할 수 있는 안전 작업

- [ ] README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트 유지
- [ ] runtime endpoint count drift check 유지
- [ ] assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 기준으로 유지
- [x] `scripts/smoke_test_api.py --sanitized-summary` 결과 예시가 원문/secret/local path를 제외하는지 계속 검증
- [ ] 실제 사용자 `.md` 또는 `.txt` 문서 기준 upload/search/ask-with-docs end-to-end 재검증 결과를 paste-safe summary로 기록
- [ ] 대용량 색인 job/status API progress response schema를 preview-only 계약 기준으로 문서화 유지
- [ ] Chroma 누락 vector 재생성 preview-only endpoint 기준 실제 rebuild 활성화 조건 문서 유지
- [ ] `docs/NEXT_CHAT_HANDOFF.md`와 이 문서의 safe/manual/review 경계 정합성 유지

## 사용자 수동 확인 작업

- [ ] 로컬 서버 실행 후 `GET /assistant/startup`이 실제 브라우저 UI 첫 화면에 올바르게 표시되는지 확인
- [ ] `GET /assistant/ui-contract`의 startup sequence, refresh endpoint, response type, blocked action 표시 확인
- [ ] `POST /assistant/bootstrap`의 project root, session, UI hint 표시 확인
- [ ] `POST /assistant/action-preview`의 intent, risk level, missing input 표시 확인
- [ ] `POST /assistant/message` 실제 메시지 응답이 `ui.response_type` 기준으로 렌더링되는지 확인
- [ ] `GET /assistant/sessions`와 `GET /assistant/sessions/{session_id}/messages` paging 표시 확인

## 별도 승인 또는 보안 리뷰가 필요한 작업

- [ ] 실제 repair/delete/rebuild 실행 명령
- [ ] 실제 shell 실행
- [ ] 파일 생성, 수정, 삭제 자동화
- [ ] 브라우저 click/fill/submit/login 자동화
- [ ] OCR loader 또는 JavaScript 렌더링/외부 URL 크롤링
- [ ] Docker sandbox, cloud/local runner bridge, 서비스화 구조 변경
- [ ] 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit
- [ ] Oracle Cloud, Oracle DB, Oracle Object Storage, Oracle VM/Compute 리소스 생성/변경

## Stop Conditions

아래 상황이 필요해지면 Codex는 구현을 멈추고 `Decision Required` 또는 Claude Opus 보안/아키텍처 리뷰로 넘긴다.

- 외부 GPT API, Claude API, Gemini API 또는 외부 embedding API 활성화
- OpenAI/Claude/Gemini API key, DB password, Oracle credential 출력 또는 저장
- 실제 shell 실행, patch apply, file write/delete 자동화
- 브라우저 interaction 자동화
- 운영 배포 또는 클라우드/Oracle 리소스 변경
- 비용, 보안, 운영 데이터, workspace 밖 접근에 영향이 있는 작업

## 검증 명령

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
```

한 번에 실행하려면:

```bash
.venv/bin/python scripts/local_ci_check.py --root .
```
