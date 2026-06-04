# Claude Review Handoff

## Recommended AI

- Recommended AI: Claude
- Recommended model: Claude Sonnet
- Reason: 이번 작업은 README, API 문서, 운영 문서, 보안 문서, 프로젝트 요약의 표현/정합성 리뷰다. 고위험 보안 아키텍처 결정이나 실제 배포 작업은 포함하지 않는다.
- User action required: Claude Sonnet 리뷰 환경에서 아래 내용을 전달해 리뷰만 수행한다. 코드를 수정하지 않는다.

참고: 실제 action-loop dispatch, read-only adapter execution, approval consume mode, shell/patch/browser 실행 활성화 판단은 Claude Sonnet 문서 리뷰 범위가 아니다. 그런 판단이 필요하면 Claude Opus 보안/아키텍처 리뷰와 사용자 최종 승인으로 넘긴다.

## 사용자 실행 가이드

Claude Sonnet 환경(`claude.ai` 또는 Claude Code Sonnet 세션)에서 아래 프롬프트를 그대로 붙여 넣는다.

```text
프로젝트 경로: /Users/juyoung/local-ai-server

`docs/CLAUDE_REVIEW_HANDOFF.md` 를 읽고, 그 안에 정의된 리뷰 목표, 교차 정합성 체크 anchor, 금지사항, 출력 형식을 그대로 따라 문서 정합성 리뷰만 수행해줘.

- 코드를 수정하거나 파일을 생성/삭제하지 말 것
- pytest, uvicorn, ollama, curl, local-ai 명령을 실행하지 말 것
- 출력은 한국어
- 마지막에 "Codex Follow-up Prompt" 와 "Next Action Decision", "Recommended Next Model" 섹션을 반드시 포함
```

리뷰어가 읽을 파일은 본 문서의 "반드시 읽을 파일" 섹션을 따른다.

## Claude Opus Escalation Prompt

아래 항목 중 하나라도 리뷰 범위에 들어오면 Sonnet 문서 리뷰로 처리하지 말고 Claude Opus 보안/아키텍처 리뷰로 넘긴다.

```text
프로젝트 경로: /Users/juyoung/local-ai-server

역할:
Claude Opus 보안/아키텍처 리뷰어.
목표:
실제 action-loop dispatch, read-only adapter execution, approval consume mode, shell/patch/browser 실행 활성화 여부를 판단한다.

먼저 읽을 파일:
- AGENTS.md
- SECURITY.md
- docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md
- docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md
- docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md
- docs/NEXT_CHAT_HANDOFF.md
- docs/TASKS.md
- docs/WORKLOG.md
- app/services/assistant_service.py
- app/api/assistant.py
- app/schemas/assistant.py
- tests/test_assistant_service.py
- tests/test_security.py

리뷰 범위:
- 실제 dispatch를 열어도 되는지
- read-only adapter가 실제 파일 내용/폴더 목록/URL 응답을 읽어도 되는지
- approval을 validate-only에서 consume mode로 전환해도 되는지
- raw content, approval-like JSON, next step mutation을 차단하는 wrapper boundary가 충분한지
- shell subprocess, patch apply, browser/app interaction을 계속 차단해야 하는지
- Oracle/cloud/cost/credential 영향이 있는지

제약:
- 코드를 수정하지 말 것
- 실제 shell/patch/browser/read-only adapter execution을 실행하지 말 것
- 외부 LLM/API, Oracle/cloud, credential, 운영 배포를 활성화하지 말 것
- 현재 `would_* = false`, `execution_enabled=false` 경계를 승인 없이 완화하지 말 것

출력:
- P0/P1/P2 findings
- Decision Required
- Codex Follow-up Prompt
- Recommended Next Model
```

## 프로젝트 루트

```bash
cd /Users/juyoung/local-ai-server
pwd
ls
git status
```

주의: 현재 handoff 작성 시점의 프로젝트 루트는 Git 저장소다. 다른 환경에서 `git status`가 실패하면 그 사실을 리뷰에 포함한다.

## 리뷰 목표

`local-ai-server` 문서 세트가 실제 구현 상태와 일치하는지 확인한다.

리뷰 범위:

- README가 포트폴리오 문서로 충분한지
- API 문서와 실제 구현 설명이 충돌하지 않는지
- 보안/운영 문서가 과장 없이 현재 한계를 명확히 말하는지
- 구현된 기능과 미구현 기능이 섞여 있지 않은지
- 외부 LLM API를 사용하지 않는다는 제약이 일관되게 표현되어 있는지
- Oracle/클라우드 배포가 실제로 되지 않았는데 배포된 것처럼 보이는 표현이 없는지
- 9-15차 locked/preview 계약이 실제 실행 완료처럼 과장되지 않았는지
- Decision Required 문서들이 README/API/SECURITY/FINAL_REPORT/NEXT_CHAT_HANDOFF와 충돌하지 않는지

## 반드시 읽을 파일

- `README.md`
- `docs/PROJECT_SUMMARY.md`
- `docs/API.md`
- `docs/OPERATIONS.md`
- `SECURITY.md`
- `docs/WORKLOG.md`
- `docs/NEXT_CHAT_HANDOFF.md`
- `docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md`
- `docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md`
- `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`
- `docs/FINAL_REPORT.md`
- `AGENTS.md`

## 현재 구현 요약

- FastAPI backend
- Ollama local chat/embed client
- SQLite metadata/chunk/chat log/feedback 저장
- Chroma vector search
- 문서 업로드와 폴더 색인
- `.txt`, `.md`, `.html`, `.htm` 기본 지원
- optional dependency 기반 `.pdf`, `.docx` 지원
- read-only folder index preview
- folder index 결과 파일별 성공/스킵 상세
- `/documents/stats`, `/documents/integrity`, `/documents/repair-preview`
- `/chat-logs`, `GET /feedback`
- 9차 approval store preview: 서버 발급 approval id, single-use, TTL, session/request context binding, payload_hash binding
- 10차 no-op dispatcher: route plan/noop audit only, approval validate-only
- 11차 read-only boundary preview: classification-only, 파일 읽기/URL fetch 없음
- 12차 read-only adapter execution Decision Required
- 13차 `assistant.action_loop.read_only_result_wrapper.v1` schema
- 14차 assistant bridge smoke expected output에 result wrapper safe flag 반영
- 15차 `docs/NEXT_CHAT_HANDOFF.md`와 Decision Required 문서 최신화
- Typer CLI
- SFT JSONL export
- API/운영/보안/요약 문서

## 현재 검증 상태

- `.venv/bin/pytest`: `815 passed, 1 warning`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `.venv/bin/python scripts/public_release_check.py --root . --json`: `ok=true`, `scanned_files=134`, finding 없음
- `git diff --check`: 성공
- `.venv/bin/python scripts/local_ci_check.py --root .`: 성공. 내부 pytest `815 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=134`, finding 없음, git diff check 성공
- `git status`: 현재 프로젝트 루트 기준 실행 가능
- 실제 로컬 Ollama 검증 이력은 `docs/WORKLOG.md`에 기록됨

리뷰어는 위 명령을 다시 실행하지 않는다. 위 값과 `docs/WORKLOG.md` 검증 표를 그대로 인용한다.

## 교차 정합성 체크 anchor

리뷰는 아래 anchor를 우선 점검한다. 세 위치 사이에 차이가 있으면 P0로 분류한다.

1. 보호 endpoint 목록
   - `README.md` "LOCAL_API_KEY" 섹션
   - `SECURITY.md` "인증과 접근 제어" 섹션
   - `docs/API.md` "인증" 섹션
2. CLI 명령어 목록
   - `README.md` "CLI 사용법" 섹션
   - `docs/PROJECT_SUMMARY.md` "CLI 명령어 목록" 섹션
   - `docs/API.md` "CLI 대응" 섹션
3. 현재 한계
   - `README.md` "현재 한계" 섹션
   - `docs/PROJECT_SUMMARY.md` "현재 한계" 섹션
   - `SECURITY.md` "보안 한계" 섹션
4. 배포 상태
   - `README.md` "배포 상태" 섹션
   - `SECURITY.md` 전체
   - `docs/PROJECT_SUMMARY.md` "보안과 운영 기준" 섹션
5. 검증 수치 (`pytest 815 passed, 1 warning` 등)
   - `README.md`, `docs/PROJECT_SUMMARY.md`, `docs/WORKLOG.md`, `docs/CLAUDE_REVIEW_HANDOFF.md`
6. 9-15차 locked/preview와 Decision Required
   - `SECURITY.md` "Agent 안전 기준"
   - `docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md`
   - `docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md`
   - `docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md`
   - `docs/NEXT_CHAT_HANDOFF.md`

## 리뷰할 세부 항목

### P0 확인

- 구현되지 않은 기능을 구현된 것처럼 말하는 문구
- 실제 외부 API를 사용하는 것처럼 보이는 문구
- 실제 배포되지 않았는데 배포 완료처럼 보이는 문구
- 삭제/repair/rebuild가 read-only preview가 아닌 실제 수행처럼 보이는 문구
- action-loop dispatch, read-only adapter execution, shell/patch/browser가 실제 활성화된 것처럼 보이는 문구
- `execution_enabled=true` 또는 `would_* true`를 허용하는 듯한 문구
- 민감 정보 또는 실제 개인 문서 내용 노출

### P1 확인

- README와 `docs/PROJECT_SUMMARY.md`의 endpoint/CLI 목록 불일치
- `SECURITY.md`의 보호 endpoint 목록과 `docs/API.md` 설명 불일치
- 현재 한계가 README, SECURITY, PROJECT_SUMMARY에서 다르게 표현되는 문제
- 포트폴리오 관점에서 기술 선택 이유가 부족하거나 과장된 부분

### P2 확인

- 문서 흐름, 문장 다듬기
- 초보자 관점에서 실행 순서가 헷갈리는 부분
- 중복 설명을 줄일 수 있는 부분
- 추가하면 좋은 diagram 또는 표

## 금지사항

- 코드를 수정하지 않는다.
- 파일을 생성하지 않는다.
- 파일을 삭제하지 않는다.
- `pytest`, `uvicorn`, `ollama`, `local-ai`, `curl`을 새로 실행하지 않는다. 검증 결과는 본 문서와 `docs/WORKLOG.md`를 인용한다.
- 외부 LLM API, 외부 크롤링, browser interaction, 시스템 의존성 설치, 운영 배포를 제안하더라도 실행하지 않는다.
- Oracle 실제 배포, Oracle DB 연결, Oracle Object Storage, Oracle VM 리소스 변경을 진행하지 않는다.
- 실제 action-loop dispatch, read-only adapter execution, shell subprocess, patch apply/file write/delete, browser/app interaction 활성화를 제안하더라도 실행하지 않는다.

## 출력 형식

응답은 한국어로 작성한다. 마크다운 표는 그대로 유지한다. 각 발견 항목의 "위치"는 파일 경로와 가능하면 줄 번호 또는 섹션 제목으로 적는다 (예: `README.md:291`, `SECURITY.md "인증과 접근 제어"`).

```markdown
## Claude Sonnet Review

### 전체 평가

### 좋은 점

### P0 — 반드시 수정

| 위치 | 문제 | 이유 | 권장 수정 |
|---|---|---|---|

### P1 — 다음 작업 전 수정 권장

| 위치 | 문제 | 이유 | 권장 수정 |
|---|---|---|---|

### P2 — 보류 가능

| 위치 | 문제 | 이유 | 권장 수정 |
|---|---|---|---|

### 문서 정합성 체크

### 보안/운영 표현 체크

### 포트폴리오 관점 개선 제안

### Decision Required 경계 체크

Sonnet은 문서 표현과 정합성만 리뷰한다. 아래 중 하나라도 실제 활성화 판단이 필요하면 `USER_DECISION_REQUIRED`로 분류하고 Claude Opus 보안/아키텍처 리뷰를 권장한다.

- 실제 action-loop dispatch
- 실제 read-only adapter execution
- shell subprocess 실행
- patch apply/file write/delete
- browser/app interaction
- 외부 LLM/API provider 연결
- Oracle/cloud/cost/credential 영향 작업

### Codex Follow-up Prompt

Codex가 바로 반영할 수 있는 수정 지시를 작성한다.

### Next Action Decision

Decision:
- GO_NEXT
- CODEX_FIX_REQUIRED
- USER_DECISION_REQUIRED

### Recommended Next Model

- Recommended AI:
- Recommended model:
- Reason:
- Next task:
- User action required:
```
