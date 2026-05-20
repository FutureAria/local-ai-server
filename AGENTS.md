# local-ai-server 작업 지침

## 프로젝트 목적

`local-ai-server`는 외부 GPT API, Claude API, Gemini API 없이 동작하는 백엔드 전용 로컬 AI 지식 서버다. 런타임 LLM과 embedding 호출은 Ollama local API만 사용한다.

## 핵심 규칙

- 프론트엔드를 만들지 않는다.
- FastAPI를 백엔드 프레임워크로 사용한다.
- SQLite는 문서 메타데이터, chunk 기록, 채팅 로그, 피드백의 source of truth로 사용한다.
- Chroma는 vector search 전용으로 사용한다.
- CLI는 Typer로 만들고, FastAPI 서버를 HTTP로 호출한다.
- LangChain은 사용하지 않는다.
- 외부 유료 API 또는 cloud vector DB를 사용하지 않는다.
- API route 파일은 얇게 유지하고 비즈니스 로직은 `app/services/`에 둔다.
- 오류를 조용히 무시하지 않고 명확한 예외와 응답을 반환한다.
- 기본 서버 bind 예시는 `127.0.0.1`로 안내한다.
- `LOCAL_API_KEY`가 설정된 경우 보호 endpoint는 `X-API-Key` 헤더를 요구한다.

## 고위험 작업

아래 작업은 사용자 승인 없이 진행하지 않는다.

- 외부 LLM API 활성화
- OpenAI/Claude/Gemini/Gemini embedding 연동
- 원본 로컬 파일 삭제 또는 수정
- 시스템 패키지 설치
- 운영 배포 또는 클라우드 리소스 생성/변경
- secret, API key, DB password 출력

## 검증 원칙

- 가능한 변경 후 `pytest`를 실행한다.
- 실행하지 않은 테스트를 통과했다고 말하지 않는다.
- Ollama가 실행 중이지 않아도 서버 import와 테스트가 가능해야 한다.

## 최종 보고 방식

이 프로젝트는 로컬 전용 백엔드 서버이므로, 실제 배포/클라우드/DB migration 작업이 없으면 최종 응답에 별도의 배포 여부 섹션을 반복하지 않는다.

대신 작업을 계속 이어가기 위한 마지막 섹션은 아래 형식을 기본으로 한다.

```markdown
## Recommended Next Model

- Recommended AI: Codex
- Recommended model: Codex GPT-5.5
- Reason: <Codex가 계속 처리 가능한 이유>
- Next task: <다음 작업>
- User action required: 없음. 단, 외부 LLM API, 시스템 의존성 설치, 파일 삭제, 운영 배포, browser interaction, 비용/보안 영향 작업은 사용자 승인 전 진행 불가
```

다음 작업이 안전한 Codex 구현/검증 작업이면 사용자에게 새 프롬프트를 붙여넣으라고 하지 말고 현재 세션에서 계속 진행한다.
