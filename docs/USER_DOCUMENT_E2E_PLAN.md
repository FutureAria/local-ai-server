# User Document E2E Smoke Plan

이 문서는 실제 사용자 `.md` 또는 `.txt` 문서를 기준으로 upload/search/ask-with-docs 흐름을 검증하기 위한 안전 실행 계획이다.

실제 실행은 SQLite, Chroma, `data/uploads/`에 문서와 vector 기록을 추가할 수 있으므로 사용자 승인 후에만 진행한다. 이 문서는 승인 전 준비와 paste-safe 기록 기준만 정의하며, 원본 문서를 삭제하거나 수정하지 않는다.

## 목적

- 실제 사용자 문서가 `POST /documents/upload`, `POST /search`, `POST /ask-with-docs` 흐름에서 동작하는지 확인한다.
- 기록에 붙일 결과는 `safe_to_paste=true` summary만 남긴다.
- 질문/답변 원문, request id, header, local path, stored path, API key, 문서 원문은 보고서에 남기지 않는다.

## 승인 전 확인

아래 조건이 모두 맞을 때만 실제 smoke를 실행한다.

| 항목 | 기준 |
|---|---|
| 사용자 승인 | 실제 사용자 문서 E2E 실행을 승인받은 상태 |
| 서버 bind | `127.0.0.1` 또는 `localhost` |
| Ollama | `ollama serve` 실행 중 |
| LLM model | `llama3.2` pull 완료 |
| Embedding model | `nomic-embed-text` pull 완료 |
| 인증 | `LOCAL_API_KEY` 설정 시 `X-API-Key` header 사용 |
| 문서 타입 | `.md` 또는 `.txt` |
| 저장 영향 인지 | SQLite, Chroma, `data/uploads/`에 테스트 데이터가 추가될 수 있음을 인지 |

## 권장 실행 순서

```bash
git status --short --branch
python scripts/local_ci_check.py --root .

ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text

uvicorn app.main:app --host 127.0.0.1 --port 8000
```

별도 터미널에서 승인된 문서만 대상으로 smoke를 실행한다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --document /path/to/approved-notes.md --sanitized-summary
```

`LOCAL_API_KEY`가 설정된 서버라면 CLI 또는 HTTP client가 `X-API-Key`를 보내도록 환경변수를 맞춘다. key 값 자체는 문서, 로그, GitHub, 채팅에 붙이지 않는다.

## Paste-safe 기록 기준

작업 기록에는 아래 정보만 남긴다.

- `safe_to_paste=true`
- `mode`
- `excluded_fields`
- step별 `status`
- document/chunk/search/source count
- 실패 시 sanitized error category

아래 정보는 남기지 않는다.

- API key, token, header 값
- 질문/답변 원문
- request id
- 로컬 절대 경로
- stored path
- 문서 원문 또는 민감한 파일명
- SQLite row 원문
- Chroma vector payload 원문

## Stop Conditions

아래 중 하나라도 해당하면 실행하지 않고 멈춘다.

- 사용자 승인이 없는 실제 사용자 문서 smoke
- `.md`, `.txt`가 아닌 문서
- 민감한 원문이 포함되어 있어 summary만으로도 식별 위험이 있는 문서
- `ollama serve`가 실행 중이지 않거나 모델이 준비되지 않은 상태
- 서버가 `127.0.0.1` 또는 `localhost`가 아닌 주소에 bind된 상태
- `LOCAL_API_KEY`가 필요한데 `X-API-Key`가 준비되지 않은 상태
- `/assistant/startup`, `/health`, `/documents/supported-types` 같은 기본 점검 endpoint가 실패하는 상태
- repair/delete/rebuild, 실제 shell 실행, 파일 자동 수정/삭제, browser interaction이 필요한 상태

## Cleanup 원칙

실제 smoke 실행 후 SQLite, Chroma, `data/uploads/`에 추가된 테스트 데이터 정리는 자동으로 수행하지 않는다.

삭제, repair, rebuild, DB 초기화는 되돌리기 어려울 수 있으므로 사용자 승인 또는 별도 보안 리뷰 후 진행한다.

수동 정리가 승인된 경우에만 아래처럼 대상 document id를 먼저 확인한 뒤 삭제한다. 아래 명령은 예시이며, 실제 실행 전 삭제 대상과 저장 영향에 대한 사용자 승인이 필요하다.

```bash
local-ai docs --query approved-notes
curl -X DELETE http://127.0.0.1:8000/documents/<document_id> -H "X-API-Key: <local-api-key>"
local-ai integrity
```

## TASKS 반영 기준

`docs/TASKS.md`의 실제 사용자 문서 E2E 항목은 아래 조건이 모두 충족될 때만 완료로 바꾼다.

- 사용자 승인 후 실제 `.md` 또는 `.txt` 문서로 smoke 실행
- `--sanitized-summary` 출력 확인
- 민감 정보가 없는 paste-safe summary를 `docs/WORKLOG.md`에 기록
- public release check 통과
- `.env`, SQLite DB, Chroma data, uploads, logs, JSONL export가 Git에 stage되지 않음
