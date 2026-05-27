# Security Policy

`local-ai-server`는 개인 PC 또는 개인 서버에서 실행하는 로컬 전용 AI 지식 서버다. 이 문서는 안전한 로컬 운영과 GitHub/포트폴리오 공개 전 확인할 보안 기준을 정리한다.

## 기본 보안 원칙

- 런타임 LLM과 embedding은 Ollama local API만 사용한다.
- OpenAI, Claude, Gemini 등 외부 LLM API를 운영 경로에 추가하지 않는다.
- LangChain, cloud vector DB, 외부 유료 API를 사용하지 않는다.
- 기본 서버 bind는 `127.0.0.1`을 권장한다.
- 개인 문서, 업로드 파일, SQLite DB, Chroma index, 운영 로그는 Git에 올리지 않는다.
- `.env`, API key, DB password, token, credential은 출력하거나 커밋하지 않는다.
- 원본 색인 대상 폴더의 파일을 수정하거나 삭제하지 않는다.

## 인증과 접근 제어

`LOCAL_API_KEY`가 설정되어 있으면 보호 endpoint는 `X-API-Key` 헤더를 요구한다. 로컬 UI 호환을 위해 `Authorization: Bearer <LOCAL_API_KEY>`도 같은 키로 허용한다.

보호 endpoint:

- `POST /ask`
- `POST /ask-with-docs`
- `POST /search`
- `POST /documents/upload`
- `POST /documents/index-folder-preview`
- `POST /documents/index-folder-job-preview`
- `POST /documents/index-folder`
- `DELETE /documents/{document_id}`
- `POST /feedback`
- `POST /agent/plan`
- `GET /agent/runs`
- `GET /agent/runs/{run_id}`
- `GET /agent/runs/{run_id}/results`
- `GET /agent/runs/{run_id}/actions`
- `POST /agent/runs/{run_id}/dry-run`
- `POST /agent/runs/{run_id}/approve`
- `POST /agent/runs/{run_id}/reject`
- `POST /agent/runs/{run_id}/execute`
- `GET /project/shell-policy`
- `POST /project/shell-dry-run`
- `GET /assistant/capabilities`
- `POST /assistant/action-preview`
- `GET /assistant/ping`
- `GET /assistant/config`
- `GET /assistant/ui-contract`
- `GET /assistant/startup`
- `GET /assistant/status`
- `GET /assistant/dashboard`
- `POST /assistant/bootstrap`
- `POST /assistant/sessions`
- `GET /assistant/sessions`
- `GET /assistant/sessions/{session_id}`
- `GET /assistant/sessions/{session_id}/messages`
- `POST /assistant/message`
- `POST /assistant/project-root/validate`

주의:

- `GET /documents`, `GET /documents/stats`, `GET /documents/integrity`, `GET /documents/repair-preview`, `GET /chat-logs`, `GET /feedback`, `GET /project/status`, `GET /project/next`는 현재 read-only 조회 endpoint다.
- `GET /project/shell-policy`와 `POST /project/shell-dry-run`은 실제 shell을 실행하지 않지만 명령 후보가 포함될 수 있어 보호 endpoint로 둔다.
- `/assistant/*`는 사용자 메시지, 세션 기록, project root를 다루므로 보호 endpoint로 둔다.
- 보호 endpoint에는 `LOCAL_RATE_LIMIT_PER_MINUTE` 기준 process-local in-memory rate limit이 적용된다. 기본값은 분당 `120`회이며, `0`으로 설정하면 비활성화된다.
- 개인 문서가 들어 있는 환경에서는 서버를 외부 네트워크에 공개하지 말고 `127.0.0.1`에 bind한다.
- 다중 사용자 인증/인가, 사용자별 문서 격리는 아직 구현하지 않았다.
- 브라우저 UI CORS는 `LOCAL_CORS_ORIGINS`에 명시된 로컬 origin만 허용한다. 기본값은 `http://127.0.0.1:5173,http://localhost:5173`이다.

## 데이터 저장 위치

| 데이터 | 기본 위치 | Git 포함 |
|---|---|---|
| SQLite DB | `data/local_ai.sqlite3`, `data/*.sqlite3`, `data/*.sqlite3-*`, `data/*.sqlite`, `data/*.sqlite-*`, `data/*.db`, `data/*.db-*` | 제외 |
| Chroma vector index | `data/chroma/` | 제외 |
| 업로드 파일 | `data/uploads/` | 제외 |
| 운영 로그 | `data/logs/` | 제외 |
| SFT export | `data/*.jsonl` | 제외 |
| 환경변수/credential 파일 | `.env`, `.env.*`, `.envrc`, `.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.pnpmrc`, `.pypirc`, `pip.conf`, `.config/pip/pip.conf`, `.config/pypoetry/auth.toml`, `pypoetry/auth.toml`, `.netrc`, `.git-credentials`, `.boto`, `.s3cfg`, `.pgpass`, `.sentryclirc`, `auth.json`, `.terraformrc`, `terraform.rc`, `secrets/`, `.secrets/`, `.ssh/`, `.gnupg/`, `.password-store/`, `.config/sops/age/keys.txt`, `.docker/`, `.config/containers/auth.json`, `.config/helm/registry/config.json`, `.config/helm/repositories.yaml`, `.config/hub`, `.config/gh/hosts.yml`, `.config/gh/hosts.yaml`, `.config/doctl/config.yaml`, `.config/doctl/config.yml`, `.vercel/auth.json`, `.netlify/config.json`, `.fly/config.yml`, `.fly/config.yaml`, `.gem/credentials`, `.cargo/credentials`, `.cargo/credentials.toml`, `.composer/auth.json`, `.config/composer/auth.json`, `.condarc`, `.config/conda/condarc`, `.continuum/anaconda-client/tokens`, `.dbt/profiles.yml`, `.databrickscfg`, `.config/databricks/credentials`, `.snowsql/config`, `.config/snowflake/config.toml`, `.gradle/gradle.properties`, `.m2/settings.xml`, `NuGet.Config`, `nuget.config`, `.nuget/NuGet/NuGet.Config`, `.pulumi/credentials.json`, `.aws/`, `.gcloud/`, `.config/gcloud/application_default_credentials.json`, `.config/gcloud/credentials.db`, `.config/gcloud/access_tokens.db`, `.config/gcloud/legacy_credentials/`, `clouds.yaml`, `secure.yaml`, `.config/openstack/clouds.yaml`, `.config/openstack/secure.yaml`, `rclone.conf`, `.config/rclone/rclone.conf`, `.azure/`, `.kube/`, `.oci/`, `.oraclebmc/`, `kubeconfig`, `kube.config`, `credentials.json`, `application_default_credentials.json`, `client_secret*.json`, `service-account*.json`, `firebase-adminsdk*.json`, `google-credentials*.json` (`.env.example` 예외) | 제외 |

## 로그 정책

- 질문, 답변, 문서 원문, API key, 환경변수 원문을 운영 로그에 남기지 않는다.
- 장애 분석에는 endpoint, status code, request id, 짧은 오류 메시지 수준만 사용한다.
- 파일 로그가 필요하면 `data/logs/` 아래에 두고 Git에 포함하지 않는다.
- 로그 rotation 자동화는 아직 구현하지 않았다.

## 파일 업로드와 폴더 색인

지원 형식:

- 기본: `.txt`, `.md`, `.html`, `.htm`
- optional dependency 설치 시: `.pdf`, `.docx`
- OCR optional dependency와 로컬 `tesseract` 설치 시: PDF image XObject fallback OCR

보안 기준:

- 지원하지 않는 확장자는 거부한다.
- `.txt`, `.md`, `.html`, `.htm`은 UTF-8 텍스트만 처리한다.
- HTML은 `head`, `script`, `style`, `noscript` 내용을 제외하고 텍스트만 추출한다.
- PDF OCR은 로컬 `tesseract` binary만 사용하며 이미지 bytes는 저장하지 않고 OCR 결과 텍스트만 chunk로 저장한다.
- JavaScript 렌더링, 외부 URL 크롤링, 브라우저 interaction은 지원하지 않는다.
- 폴더 색인은 `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `dist`, `build`, `target` 등을 무시한다.

## RAG 안전 기준

- 답변은 가능한 한 검색된 context를 기준으로 생성한다.
- 문서에 근거가 부족하면 충분한 정보가 없다고 답한다.
- 출처를 지어내지 않는다.
- 문서 밖 코드, 링크, 보안 세부사항, 추측성 표현이 감지되면 보수적인 fallback 답변으로 대체될 수 있다.

## Agent 안전 기준

- `/agent/plan`은 preview-only 계획 생성만 수행한다.
- `/agent/runs/{run_id}/dry-run`은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 정책 판단만 기록한다.
- `/agent/runs/{run_id}/actions`는 action별 상태와 dry-run/execution 결과를 조회한다.
- `/agent/runs/{run_id}/approve`는 승인 상태만 기록하고 실제 실행은 수행하지 않는다.
- `/agent/runs/{run_id}/reject`는 거절 상태만 기록한다.
- `/agent/runs/{run_id}/execute`는 승인된 run만 실행 시도한다.
- `AGENT_EXECUTION_ENABLED=false` 기본값에서는 실제 실행을 차단한다.
- `AGENT_EXECUTION_ENABLED=true`에서도 v1 실행 엔진은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원한다.
- 파일 preview는 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자를 차단한다.
- `/project/shell-policy`는 shell dry-run allowlist와 blocked token을 조회한다.
- `/project/shell-dry-run`은 입력 명령을 실행하지 않고 `would_execute=false`인 정책 판단만 반환한다.
- `/assistant/action-preview`는 intent와 위험도만 preview하고 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.
- `/assistant/ping`, `/assistant/config`, `/assistant/ui-contract`, `/assistant/startup`, `/assistant/dashboard`, `/assistant/bootstrap`은 UI 초기화/상태 조회용이지만 사용자 환경과 세션 요약을 다루므로 보호 endpoint로 둔다.
- `/assistant/ui-contract`는 UI 계약을 반환하지만 실제 실행 기능을 활성화하지 않는다.
- `/assistant/startup`은 UI 초기 snapshot을 반환하지만 실제 실행 기능을 활성화하지 않는다.
- `/assistant/config`는 `LOCAL_API_KEY` 값을 반환하지 않고 보호 여부만 반환한다.
- `/assistant/sessions/{session_id}/messages`는 사용자 대화 기록을 반환하므로 보호 endpoint로 둔다.
- `/assistant/message`는 UI 입력을 자동 분기하지만 폴더 색인은 preview-only, shell은 dry-run만 수행한다.
- 실제 웹 이동, 브라우저 클릭, 폴더 UI 열기, 파일 수정, shell 실행은 수행하지 않는다.
- `AGENT_EXECUTION_ENABLED` 기본값은 `false`다.
- `AGENT_ALLOWED_ROOTS`는 파일/폴더 agent action이 접근할 수 있는 root를 제한한다.
- `AGENT_WEB_FETCH_ENABLED`는 명시 URL read-only fetch를 별도로 제어한다.
- `AGENT_WEB_FETCH_MAX_BYTES`는 URL fetch 응답을 지정한 바이트 이후 truncate한다.
- `AGENT_FILE_PREVIEW_MAX_BYTES`와 `AGENT_FILE_PREVIEW_EXTENSIONS`는 파일 내용 preview 범위를 제한한다.
- agent plan 기록은 사용자 요청 내용을 포함할 수 있으므로 `/agent/*` endpoint는 `LOCAL_API_KEY`가 설정된 경우 보호된다.
- 브라우저 클릭, 파일 수정, shell 실행 같은 고위험 실행 기능을 활성화하려면 별도 보안 리뷰와 사용자 승인이 필요하다.

## 공개 전 체크리스트

자동 점검:

```bash
.venv/bin/python scripts/public_release_check.py --root . --json
```

이 명령은 read-only 점검만 수행한다. 로컬 DB, Chroma index, 업로드 파일, 로그, SFT export, secret 후보가 발견되면 실패 코드로 종료한다.

- [ ] `.env`가 포함되지 않았는가?
- [ ] `data/local_ai.sqlite3`가 포함되지 않았는가?
- [ ] `data/chroma/`가 포함되지 않았는가?
- [ ] `data/uploads/`가 포함되지 않았는가?
- [ ] `data/logs/` 로그 파일이 포함되지 않았는가?
- [ ] `data/*.jsonl` SFT export 파일이 포함되지 않았는가?
- [ ] API key, provider token, DB password, credential, key/certificate 파일이 포함되지 않았는가?
- [ ] 개인 문서 원문 또는 민감 정보가 README, docs, tests에 들어가지 않았는가?
- [ ] 실제 배포되지 않은 기능을 배포 완료처럼 설명하지 않았는가?
- [ ] 외부 LLM API를 사용하는 것처럼 오해될 문구가 없는가?

## 고위험 작업

아래 작업은 사용자 승인 없이 진행하지 않는다.

- 실제 repair/delete/rebuild 실행
- 브라우저 interaction, 파일 수정, shell agent 실행
- 실제 shell 실행
- 파일 생성/수정/삭제 자동화
- 외부 LLM API 활성화
- 외부 URL 크롤링
- 브라우저 click/fill/submit interaction 추가
- 시스템 의존성 설치
- 운영 배포
- 클라우드 리소스 생성/삭제/변경
- Oracle DB, Oracle Object Storage, Oracle VM 같은 실제 Oracle 리소스 연결 또는 변경
- DB migration, 운영 데이터 삭제, 저장공간에 비용 영향을 줄 수 있는 작업

## 보안 한계

- 현재 인증은 `LOCAL_API_KEY` 기반 단일 API key 수준이다.
- 사용자 계정, RBAC, 문서별 접근 제어는 없다.
- rate limit은 단일 프로세스 메모리 기준이다. 여러 worker나 여러 서버 인스턴스에 공유되는 분산 rate limit은 아니다.
- HTTPS termination은 애플리케이션에서 직접 제공하지 않는다.
- 서버를 외부 네트워크에 공개하려면 reverse proxy, TLS, 접근 제어, 로그 정책, 백업 정책을 별도로 검토해야 한다.
