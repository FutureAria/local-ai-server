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

개별 refresh가 필요할 때만 `GET /assistant/ping`, `GET /assistant/config`, `GET /assistant/dashboard`, `GET /assistant/sessions`를 호출한다. 개발/디버그 화면에서 현재 백엔드 API 목록과 보호 여부를 보여줘야 하면 read-only `GET /project/api-inventory`를 호출한다.

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
    },
    {
      "method": "GET",
      "path": "/project/api-inventory",
      "purpose": "read-only endpoint inventory for developer/debug UI"
    }
  ],
  "message_flow": [
    {
      "step": 1,
      "method": "POST",
      "path": "/assistant/action-preview",
      "purpose": "preview intent, risk, and missing inputs"
    },
    {
      "step": 2,
      "method": "POST",
      "path": "/assistant/message",
      "purpose": "send confirmed message"
    },
    {
      "step": 3,
      "method": "GET",
      "path": "/assistant/sessions/{session_id}/messages",
      "purpose": "page message history"
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
  ],
  "safety": {
    "shell_execution": "disabled",
    "browser_interaction": "blocked",
    "file_write_delete": "blocked",
    "external_llm_api": "not-used"
  },
  "notes": [
    "UI contract is read-only.",
    "Do not enable shell/browser/file-write actions from this response."
  ]
}
```

## `GET /project/api-inventory`

UI 개발자가 현재 FastAPI route 목록, HTTP method, tag, API key 보호 여부를 read-only로 확인할 때 사용한다. 이 endpoint는 API 목록만 반환하며 shell 실행, 파일 수정, 브라우저 조작을 수행하지 않는다.

```json
{
  "service": "local-ai-server",
  "total_routes": 42,
  "protected_routes": 31,
  "routes": [
    {
      "path": "/assistant/startup",
      "methods": [
        "GET"
      ],
      "name": "get_assistant_startup",
      "tags": [
        "assistant"
      ],
      "protected": true
    },
    {
      "path": "/project/api-inventory",
      "methods": [
        "GET"
      ],
      "name": "get_project_api_inventory",
      "tags": [
        "project"
      ],
      "protected": false
    }
  ],
  "safety": {
    "read_only": true,
    "shell_execution": "disabled",
    "browser_interaction": "blocked",
    "file_write_delete": "blocked"
  }
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
      "phase": 15,
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
  "ui_contract": {
    "service": "local-ai-server",
    "version": "1",
    "protected": true,
    "auth": {
      "supported_headers": [
        "X-API-Key",
        "Authorization: Bearer <LOCAL_API_KEY>"
      ],
      "secret_returned": false
    },
    "startup_sequence": [
      {
        "step": 1,
        "method": "GET",
        "path": "/assistant/startup"
      }
    ],
    "refresh_endpoints": [
      {
        "method": "GET",
        "path": "/assistant/dashboard"
      }
    ],
    "message_flow": [
      {
        "step": 1,
        "method": "POST",
        "path": "/assistant/action-preview"
      },
      {
        "step": 2,
        "method": "POST",
        "path": "/assistant/message"
      }
    ],
    "response_types": {
      "answer": "assistant answer bubble",
      "agent_plan": "high-risk plan preview panel"
    },
    "safety": {
      "shell_execution": "disabled",
      "browser_interaction": "blocked",
      "file_write_delete": "blocked",
      "external_llm_api": "not-used"
    },
    "blocked_actions": [
      "shell_execution",
      "browser_interaction",
      "file_write_delete",
      "external_llm_api"
    ],
    "notes": [
      "Startup embeds the same UI contract shape."
    ]
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
  },
  "safety": {
    "shell_execution": "disabled",
    "browser_interaction": "blocked",
    "file_write_delete": "blocked",
    "external_llm_api": "not-used"
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

## Assistant Message Response Types

`POST /assistant/message`는 `type`과 `ui.response_type`으로 UI 렌더링 방식을 알려준다.

### `type=answer`

문서 기반 답변 또는 일반 답변이다. `ui.display="message"`이므로 채팅 bubble로 렌더링한다.

```json
{
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
  "ui": {
    "response_type": "answer",
    "severity": "info",
    "primary_text": "문서 기준 답변입니다.",
    "display": "message"
  }
}
```

### `type=search_results`

문서 chunk 검색 결과다. 결과 목록은 `data.results`에 들어가며 panel로 렌더링한다.

```json
{
  "type": "search_results",
  "answer": "2개 검색 결과를 찾았습니다.",
  "data": {
    "query": "JWT",
    "results": [
      {
        "chunk_id": 3,
        "document_id": 1,
        "filename": "backend-notes.md",
        "chunk_index": 0,
        "content": "JWT 인증 흐름 요약...",
        "score": 0.12
      }
    ]
  },
  "used_documents": true,
  "ui": {
    "response_type": "search_results",
    "severity": "info",
    "primary_text": "2개 검색 결과",
    "display": "panel"
  }
}
```

### `type=index_preview`

폴더 색인 미리보기다. 실제 저장, embedding, Chroma write를 수행하지 않는 preview로 표시한다.

```json
{
  "type": "index_preview",
  "answer": "색인 미리보기 완료: 파일 3개, 예상 chunk 12개입니다.",
  "data": {
    "folder_path": "/Users/example/project/notes",
    "files_count": 3,
    "chunks_estimated": 12,
    "embedding_batches_estimated": 3
  },
  "safety": {
    "folder_index": "preview-only via assistant",
    "file_write_delete": "blocked"
  },
  "ui": {
    "response_type": "index_preview",
    "severity": "info",
    "primary_text": "색인 미리보기 완료",
    "display": "panel"
  }
}
```

### `type=needs_project_root`

요청 처리에 project root가 필요한 상태다. UI는 project root 입력 또는 선택 UI를 보여준다.

```json
{
  "type": "needs_project_root",
  "answer": "폴더 색인 미리보기를 하려면 project_root가 필요합니다.",
  "data": {
    "required_field": "project_root"
  },
  "ui": {
    "response_type": "needs_project_root",
    "severity": "warning",
    "primary_text": "project root 필요",
    "display": "panel"
  }
}
```

### `type=shell_dry_run`

shell 명령을 실행하지 않고 정책 판단만 반환한다. UI는 실제 실행 버튼을 활성화하지 않는다.

```json
{
  "type": "shell_dry_run",
  "answer": "이 명령은 dry-run 기준 허용 후보입니다.",
  "data": {
    "command": "pwd",
    "status": "allowed_preview",
    "would_execute": false,
    "reason": "허용된 조회 명령입니다."
  },
  "safety": {
    "shell_execution": "disabled",
    "shell_dry_run": "allowed_preview"
  },
  "ui": {
    "response_type": "shell_dry_run",
    "severity": "info",
    "primary_text": "allowed_preview",
    "display": "panel"
  }
}
```

### `type=agent_plan`

브라우저 조작, 파일 수정/삭제, shell 실행 같은 고위험 요청은 실제 실행 대신 계획으로만 기록된다.

```json
{
  "type": "agent_plan",
  "answer": "실행형 요청은 안전한 agent plan으로만 기록했습니다. 실제 shell/browser/file-write 실행은 하지 않았습니다.",
  "data": {
    "run_id": 1,
    "status": "planned",
    "actions": [
      {
        "action_type": "browser_interaction",
        "risk_level": "high",
        "requires_approval": true,
        "status": "blocked"
      }
    ]
  },
  "safety": {
    "shell_execution": "disabled",
    "browser_interaction": "blocked",
    "file_write_delete": "blocked"
  },
  "ui": {
    "response_type": "agent_plan",
    "severity": "warning",
    "primary_text": "실행 대신 계획만 생성",
    "display": "panel"
  }
}
```

### `type=status`

현재 프로젝트 차수와 다음 안전 작업을 보여주는 상태 응답이다.

```json
{
  "type": "status",
  "answer": "현재 차수는 15차입니다.",
  "data": {
    "current_phase": {
      "phase": 15,
      "title": "Live browser UI QA",
      "status": "next"
    },
    "safe_next_tasks": [
      "Use GET /assistant/startup from the browser UI."
    ]
  },
  "ui": {
    "response_type": "status",
    "severity": "info",
    "primary_text": "15차",
    "display": "panel"
  }
}
```

## UI Rendering Notes

- `ui.display="message"`는 채팅 bubble로 렌더링한다.
- `ui.display="panel"`은 검색 결과, 색인 preview, shell dry-run, agent plan 같은 구조화 응답으로 렌더링한다.
- `ui.display="startup_snapshot"`은 첫 화면 hydration 결과로 렌더링한다.
- `safety.shell_execution`, `safety.browser_interaction`, `safety.file_write_delete` 값이 `disabled` 또는 `blocked`이면 실행 버튼을 활성화하지 않는다.
- `auth.secret_returned=false`는 API가 key 값을 반환하지 않는다는 계약이다.
