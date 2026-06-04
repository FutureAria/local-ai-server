# SMOKE_SUMMARY_EXAMPLES

이 문서는 `scripts/smoke_test_api.py --sanitized-summary` 출력 예시를 기록한다. 아래 JSON은 형식 예시이며, 질문/답변 원문, request id, header, API key, 로컬 project root, stored path를 포함하지 않는다.

## Document/RAG Smoke Summary

```json
{
  "ok": true,
  "mode": "document-rag",
  "base_url": "http://127.0.0.1:8000",
  "safe_to_paste": true,
  "sample_documents": [
    "smoke-backend-notes.md",
    "smoke-architecture-notes.txt"
  ],
  "steps": [
    {
      "step": "health",
      "status": 200
    },
    {
      "step": "upload",
      "status": 200,
      "documents_count": 2,
      "chunks_count": 2,
      "documents": [
        {
          "filename": "smoke-backend-notes.md",
          "chunks_created": 1
        },
        {
          "filename": "smoke-architecture-notes.txt",
          "chunks_created": 1
        }
      ]
    },
    {
      "step": "search",
      "status": 200,
      "results_count": 2
    },
    {
      "step": "ask-with-docs",
      "status": 200,
      "sources_count": 2
    },
    {
      "step": "feedback",
      "status": 200,
      "feedback_id": 1
    },
    {
      "step": "stats",
      "status": 200,
      "documents_count": 2,
      "chunks_count": 2
    }
  ],
  "excluded_fields": [
    "question",
    "answer",
    "content",
    "headers",
    "note",
    "api_key",
    "project_root",
    "request_id",
    "stored_path",
    "document_id",
    "chunk_id"
  ]
}
```

## Assistant Bridge Smoke Summary

```json
{
  "ok": true,
  "mode": "assistant-bridge",
  "base_url": "http://127.0.0.1:8000",
  "safe_to_paste": true,
  "steps": [
    {
      "step": "assistant-startup",
      "status": 200,
      "ui_ready": true,
      "protected": true
    },
    {
      "step": "api-inventory",
      "status": 200,
      "endpoints_count": 94,
      "protected_endpoints_count": 78
    },
    {
      "step": "assistant-bootstrap",
      "status": 200,
      "ui_ready": true,
      "has_project_root": true
    },
    {
      "step": "assistant-action-preview",
      "status": 200,
      "intent": "status",
      "would_execute": false
    },
    {
      "step": "assistant-read-only-result-wrapper",
      "status": 200,
      "schema": "assistant.action_loop.read_only_result_wrapper.v1",
      "contract_mode": "preview-only",
      "raw_content_allowed": false,
      "approval_like_json_trusted": false,
      "can_mutate_frozen_plan": false,
      "would_dispatch": false,
      "would_read": false,
      "would_fetch": false,
      "execution_enabled": false
    },
    {
      "step": "assistant-message",
      "status": 200,
      "response_type": "status"
    },
    {
      "step": "assistant-sessions",
      "status": 200,
      "sessions_count": 1
    },
    {
      "step": "assistant-messages",
      "status": 200,
      "total_messages": 2
    }
  ],
  "excluded_fields": [
    "question",
    "answer",
    "content",
    "headers",
    "note",
    "api_key",
    "project_root",
    "request_id",
    "stored_path",
    "document_id",
    "chunk_id"
  ]
}
```

## 사용 규칙

- `safe_to_paste=true`가 없으면 공개 문서나 작업 기록에 붙이지 않는다.
- `excluded_fields`는 `scripts/smoke_test_api.py`의 `SANITIZED_SUMMARY_EXCLUDED_FIELDS`와 같아야 한다.
- `excluded_fields`에는 `question`, `answer`, `content`, `headers`, `note`, `api_key`, `project_root`, `request_id`, `stored_path`, `document_id`, `chunk_id`가 포함되어야 한다.
- 문서/RAG smoke는 SQLite, Chroma, `data/uploads/`에 테스트 데이터를 추가할 수 있다.
- Assistant bridge smoke는 SQLite에 assistant session/message 기록을 추가할 수 있다.
- `.env`, 실제 `LOCAL_API_KEY`, 로컬 절대 경로, 문서 원문, 답변 원문은 기록하지 않는다.
