# UI QA Checklist

이 체크리스트는 브라우저 기반 로컬 비서 UI가 `local-ai-server` API에 붙었는지 확인하기 위한 수동 QA 기준이다.

중요:

- 이 문서는 QA 기준이다. Codex가 브라우저를 클릭하거나 메시지를 대신 전송하지 않는다.
- shell 실행, 파일 수정/삭제, 브라우저 click/fill/submit 자동화, 운영 배포는 이 체크리스트 범위가 아니다.
- `LOCAL_API_KEY` 값은 화면 녹화, 로그, 스크린샷, 문서에 남기지 않는다.
- 서버는 기본적으로 `127.0.0.1`에 bind해서 테스트한다.

## 준비

- [ ] Ollama가 실행 중이다.
- [ ] `llama3.2` 모델이 pull 되어 있다.
- [ ] `nomic-embed-text` 모델이 pull 되어 있다.
- [ ] FastAPI 서버가 `127.0.0.1:8000`에서 실행 중이다.
- [ ] UI의 API base URL이 `http://127.0.0.1:8000` 또는 `http://localhost:8000`이다.
- [ ] `LOCAL_API_KEY`가 설정된 경우 UI가 `Authorization: Bearer <LOCAL_API_KEY>` 또는 `X-API-Key`를 보낸다.
- [ ] project root 입력값은 실제 존재하는 로컬 폴더다.

## Startup

- [ ] `GET /assistant/startup` 호출이 `200`을 반환한다.
- [ ] `ping.status`가 `ok`로 표시된다.
- [ ] `config.protected`가 token 필요 여부와 일치한다.
- [ ] `config.models.llm_provider`가 `ollama-local`로 표시된다.
- [ ] `dashboard.cards.connection.status`가 `ready`로 표시된다.
- [ ] `ui_contract.startup_sequence[0].path`가 `/assistant/startup`이다.
- [ ] `ui.display`가 `startup_snapshot`이다.
- [ ] API key 원문은 응답, 화면, 로그 어디에도 표시되지 않는다.

## Bootstrap

- [ ] `POST /assistant/bootstrap` 호출이 `200`을 반환한다.
- [ ] project root를 입력했을 때 `project_root.safe_for_read_only_agent`가 표시된다.
- [ ] project root가 유효하지 않으면 사용자가 고칠 수 있는 warning 상태가 표시된다.
- [ ] `sessions.sessions`가 최근 대화 목록으로 렌더링된다.
- [ ] `ui.blocked_actions`가 실행 금지 항목으로 표시된다.

## Message Flow

- [ ] 메시지 전송 전 `POST /assistant/action-preview`가 먼저 호출된다.
- [ ] 일반 질문은 `risk_level=low` 또는 안전한 preview로 표시된다.
- [ ] 브라우저 조작, shell 실행, 파일 수정/삭제 요청은 high-risk 또는 approval-required UI로 표시된다.
- [ ] 사용자가 전송한 메시지는 `POST /assistant/message`로 전달된다.
- [ ] `type=answer`는 채팅 bubble로 렌더링된다.
- [ ] `type=search_results`는 검색 결과 panel로 렌더링된다.
- [ ] `type=index_preview`는 실제 저장 없이 미리보기 panel로 렌더링된다.
- [ ] `type=needs_project_root`는 project root 입력 요청 warning으로 렌더링된다.
- [ ] `type=shell_dry_run`은 실제 실행이 아니라 정책 판단 panel로 렌더링된다.
- [ ] `type=agent_plan`은 실행 대신 계획/승인 필요 panel로 렌더링된다.

## Session History

- [ ] `GET /assistant/sessions`가 최근 세션 목록을 반환한다.
- [ ] `GET /assistant/sessions/{session_id}/messages`가 paging 가능한 메시지 목록을 반환한다.
- [ ] 긴 메시지 목록에서도 UI가 멈추지 않는다.
- [ ] 없는 session id는 `404`로 표시되고, UI가 복구 가능한 에러 상태를 보여준다.

## Security And Safety

- [ ] `LOCAL_API_KEY`가 설정되어 있고 header가 없으면 보호 endpoint는 `401`을 반환한다.
- [ ] 잘못된 token이면 `401`을 반환한다.
- [ ] 분당 요청 제한 초과 시 `429`와 `Retry-After`가 표시된다.
- [ ] `safety.shell_execution`이 `disabled`이면 실행 버튼을 활성화하지 않는다.
- [ ] `safety.browser_interaction`이 `blocked`이면 브라우저 조작 버튼을 활성화하지 않는다.
- [ ] `safety.file_write_delete`가 `blocked`이면 파일 수정/삭제 버튼을 활성화하지 않는다.
- [ ] `external_llm_api`는 `not-used`로 표시된다.

## Manual Smoke Commands

서버가 실행 중일 때 아래 명령으로 UI가 호출할 API를 확인할 수 있다.

```bash
curl http://127.0.0.1:8000/assistant/startup \
  -H "Authorization: Bearer <LOCAL_API_KEY>"

curl -X POST http://127.0.0.1:8000/assistant/action-preview \
  -H "Authorization: Bearer <LOCAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"내 문서 기준으로 JWT 설명해줘","project_root":"/Users/example/project"}'

curl -X POST http://127.0.0.1:8000/assistant/message \
  -H "Authorization: Bearer <LOCAL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"내 문서 기준으로 JWT 설명해줘","project_root":"/Users/example/project","mode":"auto"}'
```

## Stop Conditions

아래 항목이 필요해지면 QA를 멈추고 별도 승인 또는 보안 리뷰를 진행한다.

- 실제 브라우저 click/fill/submit 자동화
- 실제 shell 실행 활성화
- 파일 생성, 수정, 삭제 자동화
- workspace 밖 파일 접근
- 외부 LLM API 연결
- 운영 배포 또는 클라우드 리소스 변경
- 실제 repair/delete/rebuild 실행
