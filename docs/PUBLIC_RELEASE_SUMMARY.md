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
- Agent plan/dry-run/approval/read-only execution v1
- Feedback 저장과 SFT JSONL export
- API, 보안, 운영, QA, handoff 문서

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
```

현재 검증 상태:

- `.venv/bin/pytest`: `178 passed`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `.venv/bin/python scripts/public_release_check.py --root . --json`: `ok=true`, finding 없음
- `git diff --check`: 성공

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
- [ ] `python scripts/public_release_check.py --root . --json` 결과 확인
- [ ] 민감 파일이 staging되지 않았는지 `git status --short`로 확인
