# Release Checklist

이 체크리스트는 `local-ai-server`를 GitHub/포트폴리오에 공개하기 전 확인할 항목이다.

주의:

- 이 문서는 공개 전 점검용이다.
- 운영 배포, 클라우드 리소스 생성, Oracle 리소스 연결, DB migration을 실행하지 않는다.
- 실제 API key, `.env`, SQLite DB, Chroma index, 업로드 파일, 로그, JSONL export를 공개하지 않는다.

## 1. 코드 상태

- [ ] `git status --short --branch`가 의도한 변경만 보여준다.
- [ ] `.env`가 staging에 없다.
- [ ] `data/local_ai.sqlite3`가 staging에 없다.
- [ ] `data/chroma/` 파일이 staging에 없다.
- [ ] `data/uploads/` 파일이 staging에 없다.
- [ ] `data/logs/` 로그 파일이 staging에 없다.
- [ ] `data/*.jsonl` export 파일이 staging에 없다.

## 2. 자동 검증

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
python scripts/local_ci_check.py --root .
```

통과 기준:

- [ ] pytest가 통과한다.
- [ ] compileall이 성공한다.
- [ ] public release check가 `ok=true`를 반환한다.
- [ ] `git diff --check`가 whitespace 오류를 출력하지 않는다.
- [ ] `python scripts/local_ci_check.py --root .`가 통과한다.
- [ ] `tests/test_smoke_script.py`가 sanitized smoke summary 계약을 검증한다.
- [ ] `tests/test_ui_bridge_examples.py`가 runtime endpoint count drift check를 검증한다.
- [ ] `tests/test_public_docs_contract.py`와 `tests/test_security_docs_contract.py`가 공개 문서 endpoint/보안 경계를 검증한다.

## 3. 문서 정합성

- [ ] `README.md`에 프로젝트 목적, 실행 방법, CLI 사용법, 보안 한계가 있다.
- [ ] `docs/API.md`에 endpoint와 CLI 대응 관계가 있다.
- [ ] `docs/PROJECT_SUMMARY.md`에 endpoint 목록, CLI 목록, 테스트 방법, 현재 한계가 있다.
- [ ] `docs/UI_BRIDGE_EXAMPLES.md`에 UI startup/message 예시 payload가 있다.
- [ ] `docs/UI_QA_CHECKLIST.md`에 수동 QA 기준과 stop condition이 있다.
- [ ] `SECURITY.md`에 GitHub 공개 전 보안 기준이 있다.
- [ ] `docs/NEXT_CHAT_HANDOFF.md`에 다음 작업 기준이 있다.

## 4. 보안 경계

- [ ] 런타임 LLM과 embedding은 Ollama local API만 사용한다고 문서화되어 있다.
- [ ] OpenAI, Claude, Gemini 외부 LLM API를 사용하지 않는다고 문서화되어 있다.
- [ ] LangChain과 cloud vector DB를 사용하지 않는다고 문서화되어 있다.
- [ ] `LOCAL_API_KEY`는 예시 placeholder로만 표시된다.
- [ ] `Authorization: Bearer <LOCAL_API_KEY>`처럼 placeholder를 사용한다.
- [ ] 실제 token, password, private key, credential은 문서와 테스트에 없다.

## 5. 실행 경계

- [ ] Agent 기본값은 실제 실행 비활성이다.
- [ ] Agent execution v1은 조건부 read-only 기능이며 기본값은 차단이라고 설명되어 있다.
- [ ] Agent execution v1은 허용 root 폴더 목록 조회, 텍스트 파일 preview, 명시 URL 단건 read-only fetch만 지원한다고 설명되어 있다.
- [ ] shell은 dry-run 정책 판단만 제공한다고 설명되어 있다.
- [ ] browser click/fill/submit 자동화는 지원하지 않는다고 설명되어 있다.
- [ ] 폴더 UI 열기는 지원하지 않는다고 설명되어 있다.
- [ ] 파일 수정/삭제 자동화는 지원하지 않는다고 설명되어 있다.
- [ ] repair/delete/rebuild 실제 실행은 사용자 승인 전 하지 않는다고 설명되어 있다.
- [ ] 폴더 색인 preview는 실제 저장 없이 동작한다고 설명되어 있다.

## 6. 로컬 실행 확인

서버가 실행 중일 때만 선택적으로 확인한다.

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/ollama
local-ai health
local-ai doctor
local-ai assistant-startup
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --assistant-bridge-only --project-root /Users/juyoung/local-ai-server
python scripts/smoke_test_api.py --base-url http://127.0.0.1:8000 --sanitized-summary
local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server
local-ai integrity
local-ai vector-rebuild-preview
```

통과 기준:

- [ ] `/health`가 `status=ok`를 반환한다.
- [ ] Ollama 모델 준비 상태를 확인했다.
- [ ] assistant startup 응답에 secret 원문이 없다.
- [ ] assistant bridge smoke가 브라우저 조작 없이 startup/api-inventory/bootstrap/action-preview/message/session history 흐름을 확인한다.
- [ ] sanitized smoke summary가 `safe_to_paste=true`를 포함하고 질문/답변 원문, request id, header, 로컬 project root, stored path를 제외한다.
- [ ] action preview가 실행하지 않고 위험도만 보여준다.
- [ ] integrity 점검이 read-only로 동작한다.

## 7. 공개 상태

- [ ] README가 배포 완료처럼 오해되지 않는다.
- [ ] 현재 구현은 로컬 실행 기준이라고 명확하다.
- [ ] 클라우드/Oracle 배포는 실행하지 않았다고 명확하다.
- [ ] 운영 배포가 필요하면 별도 보안/운영 리뷰 후 결정한다고 명확하다.
- [ ] README, Project Summary, Public Release Summary의 다음 개선 경계가 서로 맞는다.

## 8. 공개 후 다음 개선 경계

Codex가 바로 이어서 할 수 있는 안전한 개선:

- [ ] endpoint/response field 계약 테스트와 runtime endpoint count drift check 유지
- [ ] 승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary가 민감 정보 없이 유지되는지 검증
- [ ] 대용량 색인 job/status API progress response schema preview-only 계약 기준 실제 queue 활성화 조건 문서 유지
- [ ] Chroma 누락 vector 재생성 preview-only endpoint 기준 실제 rebuild 활성화 조건 문서 유지
- [ ] assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 표시 기준과 함께 유지
- [ ] PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지

별도 승인 또는 보안 리뷰가 필요한 개선:

- [ ] 실제 repair/delete/rebuild 실행 명령
- [ ] 브라우저 click/fill/submit 자동화
- [ ] 실제 shell 실행 또는 파일 생성/수정/삭제 자동화
- [ ] JavaScript 렌더링, 외부 URL 크롤링, pdf2image/poppler 기반 page rendering OCR 확장
- [ ] 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit

## 9. 최종 공개 판단

- [ ] 현재 공개 범위는 로컬 백엔드 API, CLI, 문서, 테스트 코드로 한정된다.
- [ ] 실제 `.env`, SQLite DB, Chroma index, 업로드 문서, 로그, SFT JSONL은 공개하지 않는다.
- [ ] 구현된 기능과 preview-only 기능이 README/API/PROJECT_SUMMARY/PUBLIC_RELEASE_SUMMARY에서 구분된다.
- [ ] release checklist final pass 후에도 실제 배포, repair/delete/rebuild, browser interaction, shell/file 자동 실행은 진행하지 않는다.

## Stop Conditions

아래 항목이 필요해지면 공개 준비를 멈추고 별도 승인 또는 보안 리뷰를 진행한다.

- 실제 외부 LLM API 활성화
- 실제 shell 실행 활성화
- 브라우저 interaction 자동화
- 파일 생성, 수정, 삭제 자동화
- 운영 배포
- 클라우드 또는 Oracle 리소스 연결/생성/삭제/확장
- DB migration 또는 운영 데이터 변경
- 비용이 발생할 수 있는 리소스 사용
