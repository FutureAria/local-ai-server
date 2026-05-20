# UI Bridge Examples

이 문서는 브라우저 기반 로컬 비서 UI가 `local-ai-server` 백엔드에 붙을 때 참고할 수 있는 예시 payload 모음이다.

주의:

- 예시는 모두 read-only 계약 설명용이다.
- 실제 `LOCAL_API_KEY` 값은 문서나 API 응답에 포함하지 않는다.
- `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key: <LOCAL_API_KEY>` 헤더만 사용한다.
- shell 실행, 파일 수정/삭제, 브라우저 클릭/입력 자동화는 이 계약에 포함되지 않는다.

## Recommended Startup Flow

1. `GET /assistant/startup`
2. `POST /assistant/bootstrap`
3. `POST /assistant/action-preview`
4. `POST /assistant/message`
5. `GET /assistant/sessions/{session_id}/messages`

개별 refresh가 필요할 때만 `GET /assistant/ping`, `GET /assistant/config`, `GET /assistant/dashboard`, `GET /assistant/sessions`를 호출한다.

## `GET /assistant/ui-contract`

UI가 따라야 할 API 순서와 렌더링 타입을 확인한다.

```json
{
  "service": "local-ai-server",
  "version": "1",
  "protected": true,
  "auth": {
    "supported_headers": [
      "X-API-Key",
      "Authorization: Bearer <LOCAL_API_KEY>"
    ],
    "secret_returned": false,
    "note": "LOCAL_API_KEY 값은 API 응답에 포함하지 않습니다."
  },
  "startup_sequence": [
    {
      "step": 1,
      "method": "GET",
      "path": "/assistant/startup",
      "purpose": "one-call UI hydration"
    },
    {
      "step": 2,
      "method": "POST",
      "path": "/assistant/bootstrap",
      "purpose": "sessions and project root state"
    },
    {
      "step": 3,
      "method": "POST",
      "path": "/assistant/action-preview",
      "purpose": "pre-send intent/risk check"
    },
    {
      "step": 4,
      "method": "POST",
      "path": "/assistant/message",
      "purpose": "send confirmed message"
    }
  ],
  "refresh_endpoints": [
    {
      "method": "GET",
      "path": "/assistant/ping",
      "purpose": "server/auth quick check"
    },
    {
      "method": "GET",
      "path": "/assistant/config",
      "purpose": "safe local settings"
    },
    {
      "method": "GET",
      "path": "/assistant/dashboard",
      "purpose": "dashboard cards"
    },
    {
      "method": "GET",
      "path": "/assistant/sessions",
      "purpose": "session sidebar refresh"
    }
  ],
  "response_types": {
    "answer": "assistant answer bubble",
    "search_results": "search result panel",
    "index_preview": "folder index preview panel",
    "needs_project_root": "project root required warning",
    "shell_dry_run": "shell dry-run policy panel",
    "agent_plan": "high-risk plan preview panel",
    "status": "project phase/status panel",
    "action_preview": "pre-send intent preview panel"
  },
  "blocked_actions": [
    "shell_execution",
    "browser_interaction",
    "file_write_delete",
    "external_llm_api"
  ]
}
```

## `GET /assistant/startup`

첫 화면을 그리기 위한 snapshot이다. UI는 이 응답만으로 연결 상태, 설정, dashboard 카드, UI 계약을 초기 렌더링할 수 있다.

```json
{
  "service": "local-ai-server",
  "protected": true,
  "local_only": true,
  "ping": {
    "status": "ok",
    "service": "local-ai-server",
    "protected": true,
    "local_only": true,
    "ui_ready": true
  },
  "config": {
    "service": "local-ai-server",
    "protected": true,
    "local_only": true,
    "cors_origins": [
      "http://127.0.0.1:5173",
      "http://localhost:5173"
    ],
    "allowed_roots": [
      {
        "path": "/Users/example/project",
        "exists": true,
        "is_dir": true
      }
    ],
    "models": {
      "llm_provider": "ollama-local",
      "llm_model": "llama3.2",
      "embedding_model": "nomic-embed-text"
    },
    "storage": {
      "database": "sqlite-local",
      "vector_store": "chroma-local",
      "upload_dir": "data/uploads",
      "chroma_path": "data/chroma"
    }
  },
  "dashboard": {
    "current_phase": {
      "phase": 14,
      "title": "Live browser UI QA",
      "status": "next"
    },
    "cards": {
      "documents": {
        "documents_count": 0,
        "chunks_count": 0,
        "chroma_vectors_count": 0,
        "missing_stored_files_count": 0
      },
      "integrity": {
        "status": "ok",
        "chunks_missing_vectors_count": 0,
        "orphan_vectors_count": 0,
        "repair_available": false
      },
      "sessions": {
        "sessions_count": 0,
        "messages_count": 0
      },
      "connection": {
        "status": "ready",
        "protected": true,
        "local_only": true
      }
    },
    "recent_sessions": [],
    "ui": {
      "ready": true,
      "badge": "DASHBOARD READY",
      "recommended_refresh_seconds": 30
    }
  },
  "recommended_calls": [
    {
      "method": "POST",
      "path": "/assistant/bootstrap",
      "when": "project_root is available"
    },
    {
      "method": "POST",
      "path": "/assistant/action-preview",
      "when": "before sending user text"
    },
    {
      "method": "POST",
      "path": "/assistant/message",
      "when": "user confirms message send"
    }
  ],
  "ui": {
    "ready": true,
    "badge": "STARTUP SNAPSHOT READY",
    "message": "UI 초기 렌더링에 필요한 read-only snapshot입니다.",
    "display": "startup_snapshot"
  }
}
```

## `POST /assistant/message`

일반 질문, 문서 기반 질문, 검색, 상태 조회, 색인 미리보기 요청은 모두 같은 endpoint로 보낼 수 있다.

요청:

```json
{
  "message": "내 문서 기준으로 JWT 인증 흐름 설명해줘",
  "session_id": "optional-session-id",
  "project_root": "/Users/example/project",
  "mode": "auto",
  "top_k": 5,
  "temperature": 0.2
}
```

응답:

```json
{
  "session_id": "session-id",
  "type": "answer",
  "answer": "문서 기준 답변입니다.",
  "used_documents": true,
  "sources": [
    {
      "document_id": 1,
      "filename": "backend-notes.md",
      "chunk_index": 0,
      "chunk_id": 3
    }
  ],
  "request_id": "123",
  "safety": {
    "shell_execution": "disabled",
    "browser_interaction": "blocked",
    "file_write_delete": "blocked",
    "external_llm_api": "not-used"
  },
  "ui": {
    "response_type": "answer",
    "severity": "info",
    "primary_text": "문서 기준 답변입니다.",
    "display": "message"
  }
}
```

## UI Rendering Notes

- `ui.display="message"`는 채팅 bubble로 렌더링한다.
- `ui.display="panel"`은 검색 결과, 색인 preview, shell dry-run, agent plan 같은 구조화 응답으로 렌더링한다.
- `ui.display="startup_snapshot"`은 첫 화면 hydration 결과로 렌더링한다.
- `safety.shell_execution`, `safety.browser_interaction`, `safety.file_write_delete` 값이 `disabled` 또는 `blocked`이면 실행 버튼을 활성화하지 않는다.
- `auth.secret_returned=false`는 API가 key 값을 반환하지 않는다는 계약이다.
