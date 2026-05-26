# UI Connect Guide

이 문서는 별도 브라우저 UI 또는 로컬 앱이 `local-ai-server` 백엔드에 안전하게 붙을 때 필요한 최소 연결값과 호출 순서를 정리한다.

## 연결값

| 항목 | 권장값 | 설명 |
|---|---|---|
| API base URL | `http://127.0.0.1:8000` | FastAPI 서버를 로컬에서 실행한 주소 |
| API key header | `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key: <LOCAL_API_KEY>` | `LOCAL_API_KEY`가 설정된 경우에만 필요 |
| Project root | `/Users/juyoung/local-ai-server` | assistant bridge가 read-only 상태 점검에 사용할 로컬 프로젝트 경로 |
| CORS origin | `http://127.0.0.1:5173`, `http://localhost:5173` | 기본 개발 UI origin |

UI나 로컬 앱에 값만 옮길 때는 아래 형태를 기준으로 둔다.

```text
LOCAL_AI_SERVER_URL=http://127.0.0.1:8000
LOCAL_AI_PROJECT_ROOT=/Users/juyoung/local-ai-server
LOCAL_AI_AUTH_HEADER=Authorization: Bearer <LOCAL_API_KEY>
```

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

브라우저 UI를 열기 전에는 read-only preflight를 먼저 실행한다.

```bash
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-preflight
```

`GET /assistant/ui-contract`의 `refresh_endpoints`는 아래 path를 UI의 개별 새로고침 버튼 또는 polling 후보로 제공한다.

- `/assistant/ping`
- `/assistant/config`
- `/assistant/dashboard`
- `/assistant/sessions`
- `/project/api-inventory`

`8000` 포트를 다른 서버가 쓰고 있으면 `local-ai-server`를 다른 포트로 띄운 뒤 같은 `--base-url`만 바꿔 실행한다.

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8010 --assistant-bridge-preflight
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8010 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
```

## Assistant bridge smoke 기대 출력

`--assistant-bridge-preflight`는 read-only로 서버 identity만 확인한다. 성공 기준은 JSON 결과의 `ok=true`와 아래 step 상태다.

| step | 기대 값 | 의미 |
|---|---|---|
| `health.status` | `200` | FastAPI 서버가 응답함 |
| `assistant-startup.status` | `200` | 이 서버가 assistant bridge API를 제공함 |
| `api-inventory.status` | `200` | read-only API inventory를 조회할 수 있음 |

`--assistant-bridge-only`는 브라우저 조작 없이 UI bridge API 흐름을 확인한다. 성공 기준은 `ok=true`와 아래 summary field다.

| step | 확인할 summary field | 기대 값 |
|---|---|---|
| `assistant-startup` | `ui_ready`, `protected` | `ui_ready=true`, token 필요 여부 표시 |
| `api-inventory` | `endpoints_count`, `protected_endpoints_count` | endpoint 수와 보호 endpoint 수가 표시됨 |
| `assistant-bootstrap` | `ui_ready`, `has_project_root` | `ui_ready=true`, project root 검증 결과 포함 |
| `assistant-action-preview` | `intent`, `would_execute` | `intent=status`, `would_execute=false` |
| `assistant-message` | `session_id`, `response_type` | `session_id` 존재, `response_type=status` |
| `assistant-sessions` | `sessions_count` | 최근 세션 수 표시 |
| `assistant-messages` | `total_messages` | paging 가능한 메시지 수 표시 |

이 smoke는 업로드, RAG, Ollama 답변 생성을 피한다. 다만 `/assistant/message`를 호출하므로 SQLite에 assistant session/message 기록은 추가될 수 있다.

API inventory 화면에서는 최신 문서/복구 preview endpoint도 함께 표시되어야 한다.

| endpoint | UI 표시 기준 |
|---|---|
| `/documents/index-folder-job-preview` | 대용량 색인 job/status progress schema 미리보기. `dry_run=true`, `would_enqueue=false`, `status=planned`, `job_id=preview-only`, `progress.total_files`, `progress.embedding_batches_total`, `progress.percent=0`을 강조 |
| `/documents/repair-preview` | SQLite/Chroma repair 후보 미리보기. `dry_run=true`, `status=needs_repair 또는 ok`, `actions_count`, `actions[].requires_user_approval=true`를 강조하고 실제 repair/delete/rebuild 버튼은 제공하지 않음 |
| `/documents/vector-rebuild-preview` | Chroma 누락 vector 재생성 후보 미리보기. `dry_run=true`, `status=needs_rebuild 또는 ok`, `chunks_missing_vectors_count`, `embedding_batches_estimated`, `actions[].requires_user_approval=true` 표시 |

두 endpoint 모두 실제 queue 생성, Ollama embedding 생성, Chroma write, DB 수정, repair/delete/rebuild 실행 버튼으로 연결하지 않는다.

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
  -d '{"message":"내 문서 기준으로 현재 상태 요약해줘","project_root":"/Users/juyoung/local-ai-server","mode":"auto"}'
```

## UI가 읽어야 할 응답 필드

`GET /assistant/startup`은 첫 화면을 그리기 위한 read-only snapshot이다. UI는 아래 필드를 기준으로 초기 화면을 구성한다.

| 필드 | 용도 |
|---|---|
| `service` | 백엔드 서비스 식별 |
| `protected` | token 필요 여부 표시 |
| `local_only` | 로컬 전용 연결 표시 |
| `ping.status` | 서버 연결 상태 표시 |
| `config.cors_origins` | 허용된 로컬 UI origin 확인 |
| `config.allowed_roots` | read-only agent root 후보 표시 |
| `config.models` | Ollama 모델명 표시 |
| `dashboard.cards` | 첫 화면 문서, integrity, 세션, 연결 카드 구성 |
| `ui_contract.startup_sequence` | UI 시작 순서 표시 |
| `ui_contract.refresh_endpoints` | 개별 새로고침 endpoint 목록 표시 |
| `ui_contract.message_flow` | 메시지 전송 전후 순서 표시 |
| `ui_contract.response_types` | 응답 렌더링 타입 매핑 |
| `recommended_calls` | 다음에 호출할 endpoint 힌트 |
| `safety` | 실행 금지 상태 표시 |
| `ui.display` | `startup_snapshot` 렌더링 |

`POST /assistant/bootstrap`은 project root와 세션 목록이 준비된 뒤 UI를 활성화하는 응답이다.

| 필드 | 용도 |
|---|---|
| `service` | 백엔드 서비스 식별 |
| `capabilities.modes` | UI가 제공할 수 있는 안전 모드 표시 |
| `capabilities.safe_defaults` | 기본 차단 정책 표시 |
| `status.current_phase` | 현재 프로젝트 차수 표시 |
| `status.safety` | shell/browser/file/external LLM 상태 표시 |
| `project_root.safe_for_read_only_agent` | 입력한 project root 사용 가능 여부 표시 |
| `sessions.sessions` | 최근 대화 목록 표시 |
| `recommended_calls` | 다음 호출 후보 표시 |
| `ui.ready` | UI 활성화 가능 여부 표시 |
| `ui.blocked_actions` | 실행 금지 항목 표시 |

`GET /assistant/ui-contract`의 `response_types`는 `/assistant/message` 응답 렌더링 타입이다.

| response type | UI 렌더링 기준 |
|---|---|
| `answer` | 채팅 bubble |
| `search_results` | 검색 결과 panel |
| `index_preview` | 폴더 색인 미리보기 panel |
| `needs_project_root` | project root 입력 warning |
| `shell_dry_run` | shell 정책 판단 panel |
| `agent_plan` | 실행 대신 계획/승인 필요 panel |
| `status` | 프로젝트 상태 panel |
| `action_preview` | 전송 전 intent preview panel |

## Copy-ready fetch 예시

브라우저 UI에서 사용할 수 있는 최소 `fetch` 예시다. token 값은 사용자가 입력한 값을 런타임에 넣고, 코드나 문서에 하드코딩하지 않는다.

```js
const API_BASE_URL = "http://127.0.0.1:8000";
const PROJECT_ROOT = "/Users/juyoung/local-ai-server";

function authHeaders(localApiKey) {
  return localApiKey
    ? { Authorization: `Bearer ${localApiKey}` }
    : {};
}

export async function loadAssistantStartup(localApiKey) {
  const response = await fetch(`${API_BASE_URL}/assistant/startup`, {
    headers: authHeaders(localApiKey),
  });
  if (!response.ok) {
    throw new Error(`startup failed: ${response.status}`);
  }
  return response.json();
}

export async function bootstrapAssistant(localApiKey) {
  const response = await fetch(`${API_BASE_URL}/assistant/bootstrap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(localApiKey),
    },
    body: JSON.stringify({ project_root: PROJECT_ROOT }),
  });
  if (!response.ok) {
    throw new Error(`bootstrap failed: ${response.status}`);
  }
  return response.json();
}

export async function sendAssistantMessage(localApiKey, message) {
  const response = await fetch(`${API_BASE_URL}/assistant/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(localApiKey),
    },
    body: JSON.stringify({
      message,
      project_root: PROJECT_ROOT,
      mode: "auto",
    }),
  });
  if (!response.ok) {
    throw new Error(`message failed: ${response.status}`);
  }
  return response.json();
}
```

## UI가 표시해야 할 안전 상태

- `safety.shell_execution`: `disabled`
- `safety.shell_dry_run`: `blocked` 또는 dry-run 정책 판단 결과
- `safety.browser_interaction`: `blocked`
- `safety.file_write_delete`: `blocked`
- `safety.folder_index`: `preview-only via assistant`
- `safety.external_llm_api`: `not-used`

이 값이 위와 다르게 보이거나, UI가 실행 버튼을 활성화하려고 하면 연결을 멈추고 보안 리뷰를 먼저 진행한다.

## 연결 문제 확인

| 증상 | 확인할 것 |
|---|---|
| `401 Unauthorized` | `LOCAL_API_KEY` 설정 여부와 header 값 |
| CORS 오류 | UI origin이 `LOCAL_CORS_ORIGINS`에 포함되어 있는지 |
| `404 Not Found` | endpoint path 오타 또는 서버 버전 |
| `/health`는 성공하지만 `/assistant/startup`은 `404` | `127.0.0.1:8000`을 다른 서버가 사용 중일 수 있음 |
| Ollama 오류 | `ollama serve`, `ollama pull llama3.2`, `ollama pull nomic-embed-text` |
| project root warning | 입력한 경로가 실제 존재하는 폴더인지 |

## 하지 않는 것

- 브라우저 클릭/입력/전송 자동화
- 실제 shell 실행
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 호출
- 운영 배포 또는 클라우드/Oracle 리소스 변경
