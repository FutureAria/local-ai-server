# UI Connect Guide

이 문서는 별도 브라우저 UI 또는 로컬 앱이 `local-ai-server` 백엔드에 안전하게 붙을 때 필요한 최소 연결값과 호출 순서를 정리한다.

## 연결값

| 항목 | 권장값 | 설명 |
|---|---|---|
| API base URL | `http://127.0.0.1:8000` | FastAPI 서버를 로컬에서 실행한 주소 |
| API key header | `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key: <LOCAL_API_KEY>` | `LOCAL_API_KEY`가 설정된 경우에만 필요 |
| Project root | `/Users/juyoung/local-ai-server` | assistant bridge가 read-only 상태 점검에 사용할 로컬 프로젝트 경로 |
| CORS origin | `http://127.0.0.1:5173`, `http://localhost:5173` | 기본 개발 UI origin |

주의:

- 실제 `LOCAL_API_KEY` 값은 이 문서, README, 로그, 스크린샷에 남기지 않는다.
- 브라우저 storage에 token을 저장해야 한다면 사용자가 직접 입력하고, 저장 정책은 UI 쪽에서 별도로 결정한다.
- 이 백엔드는 OpenAI, Claude, Gemini 외부 LLM API를 호출하지 않는다.

## 서버 시작

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Ollama 기반 문서 답변까지 확인하려면 별도 터미널에서:

```bash
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

## UI 시작 호출 순서

1. `GET /assistant/startup`
2. `POST /assistant/bootstrap`
3. `POST /assistant/action-preview`
4. 사용자가 확인한 뒤 `POST /assistant/message`
5. 필요하면 `GET /assistant/sessions/{session_id}/messages`

개발/디버그 화면에서 현재 endpoint 목록을 보여주려면 `GET /project/api-inventory`를 호출한다.

```bash
curl http://127.0.0.1:8000/project/api-inventory \
  -H "Authorization: Bearer <LOCAL_API_KEY>"
```

## 최소 요청 예시

```bash
curl http://127.0.0.1:8000/assistant/startup \
  -H "Authorization: Bearer <LOCAL_API_KEY>"
```

```bash
curl -X POST http://127.0.0.1:8000/assistant/bootstrap \
  -H "Authorization: Bearer <LOCAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"project_root":"/Users/juyoung/local-ai-server"}'
```

```bash
curl -X POST http://127.0.0.1:8000/assistant/message \
  -H "Authorization: Bearer <LOCAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"내 문서 기준으로 현재 상태 요약해줘","project_root":"/Users/juyoung/local-ai-server","mode":"status"}'
```

## UI가 표시해야 할 안전 상태

- `safety.shell_execution`: `disabled`
- `safety.browser_interaction`: `blocked`
- `safety.file_write_delete`: `blocked`
- `safety.external_llm_api`: `not-used`

이 값이 위와 다르게 보이거나, UI가 실행 버튼을 활성화하려고 하면 연결을 멈추고 보안 리뷰를 먼저 진행한다.

## 연결 문제 확인

| 증상 | 확인할 것 |
|---|---|
| `401 Unauthorized` | `LOCAL_API_KEY` 설정 여부와 header 값 |
| CORS 오류 | UI origin이 `LOCAL_CORS_ORIGINS`에 포함되어 있는지 |
| `404 Not Found` | endpoint path 오타 또는 서버 버전 |
| Ollama 오류 | `ollama serve`, `ollama pull llama3.2`, `ollama pull nomic-embed-text` |
| project root warning | 입력한 경로가 실제 존재하는 폴더인지 |

## 하지 않는 것

- 브라우저 클릭/입력/전송 자동화
- 실제 shell 실행
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 호출
- 운영 배포 또는 클라우드/Oracle 리소스 변경
