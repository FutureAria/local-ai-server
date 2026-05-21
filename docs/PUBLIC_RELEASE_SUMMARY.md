# Public Release Summary

이 문서는 `local-ai-server`를 GitHub/포트폴리오에 공개할 때 현재 상태를 빠르게 확인하기 위한 요약이다.

## 현재 공개 상태

- 공개 목적: 로컬 전용 AI 지식 서버 포트폴리오
- 실행 기준: 개인 PC 또는 개인 서버의 `127.0.0.1` 로컬 실행
- 런타임 LLM/embedding: Ollama local API only
- 외부 LLM API: 사용하지 않음
- LangChain/cloud vector DB: 사용하지 않음
- 운영 배포: 하지 않음
- 클라우드/Oracle 리소스: 연결 또는 생성하지 않음

## 공개 가능한 핵심 구현

- FastAPI backend
- SQLite metadata/chat log/feedback 저장
- Chroma vector search
- Ollama `/api/chat`, `/api/embed` client
- 문서 업로드, 폴더 색인, read-only folder index preview
- RAG answer API
- Typer CLI
- Assistant UI bridge API contract
- Project API inventory
- Assistant UI bridge smoke test
- Agent plan/dry-run/approval/read-only execution v1
- Feedback 저장과 SFT JSONL export
- API, 보안, 운영, QA, handoff 문서

## 기능 경계 요약

| 구분 | 공개 설명 |
|---|---|
| 문서 업로드/검색/RAG | 구현됨. 로컬 Ollama, SQLite, Chroma 기준으로 동작한다. |
| Assistant UI bridge | 구현됨. API 계약과 smoke test를 제공하지만 프론트엔드는 포함하지 않는다. |
| Agent plan/approval | 구현됨. 요청을 action 후보, 위험도, 승인 상태로 기록한다. |
| Agent read-only execution v1 | 조건부 기능. 기본값은 차단이며, 활성화해도 허용 root 폴더 목록 조회, 텍스트 파일 preview, 명시 URL 단건 read-only fetch만 지원한다. |
| shell | dry-run only. 실제 shell 실행은 지원하지 않는다. |
| 브라우저/파일/배포 | 지원하지 않음. 클릭/입력, 폴더 UI 열기, 파일 생성/수정/삭제, 운영 배포는 범위 밖이다. |
| 외부 LLM API/cloud vector DB | 사용하지 않음. 런타임 AI 호출은 Ollama local API only다. |

## 공개하지 않는 로컬 데이터

- `.env`
- `data/local_ai.sqlite3`
- `data/chroma/`
- `data/uploads/`
- `data/logs/`
- `data/*.jsonl`
- 개인 문서 원문
- API key, token, password, credential

## 검증 기준

공개 전 아래 명령이 통과해야 한다.

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
python scripts/local_ci_check.py --root .
```

현재 검증 상태:

- `.venv/bin/pytest`: `222 passed`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `.venv/bin/python scripts/public_release_check.py --root . --json`: `ok=true`, finding 없음
- `git diff --check`: 성공
- `python scripts/local_ci_check.py --root .`: 성공

## 명확한 한계

- 브라우저 클릭/입력/전송 자동화는 지원하지 않는다.
- 실제 shell 실행은 지원하지 않고 dry-run 정책 판단만 제공한다.
- 파일 생성/수정/삭제 자동화는 지원하지 않는다.
- Chroma/SQLite repair는 `repair-preview`만 제공하며 실제 repair/delete/rebuild는 수행하지 않는다.
- 운영 배포, 클라우드 리소스 생성, Oracle 리소스 연결은 수행하지 않았다.
- 다중 사용자 auth/RBAC, HTTPS termination은 제공하지 않는다.

## 공개 전 마지막 확인

- [ ] `docs/RELEASE_CHECKLIST.md` 확인
- [ ] `SECURITY.md` 확인
- [ ] `README.md`의 배포 상태가 로컬 실행 기준으로 표시되어 있는지 확인
- [ ] README와 Project Summary의 기능 경계 표가 현재 구현과 맞는지 확인
- [ ] `python scripts/public_release_check.py --root . --json` 결과 확인
- [ ] 민감 파일이 staging되지 않았는지 `git status --short`로 확인
