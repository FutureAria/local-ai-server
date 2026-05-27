# Public Release Summary

이 문서는 `local-ai-server`를 GitHub/포트폴리오에 공개할 때 현재 상태를 빠르게 확인하기 위한 요약이다.

## 현재 공개 상태

- 공개 목적: 로컬 전용 AI 지식 서버 포트폴리오
- 실행 기준: 개인 PC 또는 개인 서버의 `127.0.0.1` 로컬 실행
- 런타임 LLM/embedding: Ollama local API only
- 외부 LLM API: 사용하지 않음
- LangChain/cloud vector DB: 사용하지 않음
- 운영 배포: 하지 않음
- 클라우드/Oracle 리소스: 연결 또는 생성하지 않음

## 공개 가능한 핵심 구현

- FastAPI backend
- SQLite metadata/chat log/feedback 저장
- Chroma vector search
- Ollama `/api/chat`, `/api/embed` client
- 문서 업로드, 폴더 색인, read-only folder index preview
- RAG answer API
- Typer CLI
- Assistant UI bridge API contract
- Project API inventory
- Assistant UI bridge smoke test
- Agent plan/dry-run/approval/read-only execution v1
- Feedback 저장과 SFT JSONL export
- API, 보안, 운영, QA, handoff 문서

## 공개용 상태 스냅샷

| 구분 | 상태 | 공개 설명 |
|---|---|---|
| 로컬 API 서버 | 구현됨 | FastAPI, SQLite, Chroma, Ollama local API 기준으로 실행한다. |
| 문서 기반 RAG | 구현됨 | 로컬 문서 업로드, 폴더 색인, 검색, 문서 기반 답변을 지원한다. PDF OCR fallback은 `[ocr]` extra와 로컬 `tesseract`가 있을 때 PyPDF image XObject 범위에서만 동작한다. |
| CLI 로컬 비서 | 구현됨 | Typer CLI와 `local-ai assistant` REPL이 FastAPI 백엔드를 호출한다. |
| Agent 실행 엔진 | preview-only | 승인/거절 상태와 조건부 read-only preview 중심이며 실제 shell/file/browser 실행은 하지 않는다. |
| 배포/외부 자동화 | 하지 않음 | 운영 배포, 브라우저 조작, 파일 자동 수정/삭제, 외부 LLM API 연결은 현재 범위 밖이다. |

## Release Contract Snapshot

| 항목 | 현재 값 | 기준 |
|---|---:|---|
| FastAPI endpoints | 51 | `build_api_inventory(app.routes).endpoints_count` |
| Protected endpoints | 35 | `build_api_inventory(app.routes).protected_endpoints_count` |
| Public endpoints | 16 | `build_api_inventory(app.routes).public_endpoints_count` |
| Typer CLI commands | 52 | `typer.main.get_command(cli.main.app).commands` |
| Document/RAG smoke steps | 6 | `DOCUMENT_RAG_SMOKE_FLOW` |
| Assistant bridge smoke steps | 7 | `ASSISTANT_BRIDGE_SMOKE_FLOW` |
| Assistant bridge preflight steps | 3 | `ASSISTANT_BRIDGE_PREFLIGHT_FLOW` |

이 표는 공개 문서가 실제 route, CLI command, smoke flow와 어긋나지 않도록 테스트로 검증한다.

## 기능 경계 요약

| 구분 | 공개 설명 |
|---|---|
| 문서 업로드/검색/RAG | 구현됨. 로컬 Ollama, SQLite, Chroma 기준으로 동작한다. |
| Assistant UI bridge | 구현됨. API 계약과 smoke test를 제공하지만 프론트엔드는 포함하지 않는다. |
| Agent plan/approval | 구현됨. 요청을 action 후보, 위험도, 승인 상태로 기록한다. |
| Agent read-only execution v1 | 조건부 기능. 기본값은 차단이며, 활성화해도 허용 root 폴더 목록 조회, 텍스트 파일 preview, 명시 URL 단건 read-only fetch만 지원한다. |
| shell | dry-run only. 실제 shell 실행은 지원하지 않는다. |
| 브라우저/파일/배포 | 지원하지 않음. 클릭/입력, 폴더 UI 열기, 파일 생성/수정/삭제, 운영 배포는 범위 밖이다. |
| 외부 LLM API/cloud vector DB | 사용하지 않음. 런타임 AI 호출은 Ollama local API only다. |

## 공개하지 않는 로컬 데이터

- `.env`
- `.env.*`
- `.envrc`
- `.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.pnpmrc`, `.pypirc`, `pip.conf`, `.config/pip/pip.conf`, `.config/pypoetry/auth.toml`, `pypoetry/auth.toml`, `.netrc`
- `.git-credentials`, `.boto`, `.s3cfg`, `.pgpass`, `.sentryclirc`
- `auth.json`, `.gem/credentials`, `.cargo/credentials`, `.cargo/credentials.toml`, `.composer/auth.json`, `.config/composer/auth.json`, `.condarc`, `.config/conda/condarc`, `.continuum/anaconda-client/tokens`, `.dbt/profiles.yml`, `.databrickscfg`, `.config/databricks/credentials`, `.snowsql/config`, `.config/snowflake/config.toml`, `.huggingface/token`, `.cache/huggingface/token`, `.cache/huggingface/stored_tokens`, `.config/huggingface/token`, `.kaggle/kaggle.json`, `.config/kaggle/kaggle.json`, `.wandb/settings`, `.config/wandb/settings`, `.gradle/gradle.properties`, `.m2/settings.xml`, `NuGet.Config`, `nuget.config`, `.nuget/NuGet/NuGet.Config`
- `.terraformrc`, `terraform.rc`, `.pulumi/credentials.json`
- `secrets/`, `.secrets/`
- `.ssh/`, `.gnupg/`, `.password-store/`, `.config/sops/age/keys.txt`, `.docker/`, `.config/containers/auth.json`, `.config/helm/registry/config.json`, `.config/helm/repositories.yaml`
- `.vault-token`, `.config/doppler/config.yaml`, `.config/infisical/infisical-config.json`, `.config/op/config`, `.config/1Password/credentials.json`
- `.config/hub`, `.config/gh/hosts.yml`, `.config/gh/hosts.yaml`
- `.config/doctl/config.yaml`, `.config/doctl/config.yml`
- `.vercel/auth.json`, `.netlify/config.json`
- `.fly/config.yml`, `.fly/config.yaml`
- `.openai/`, `.config/openai/`, `.anthropic/`, `.claude.json`, `.claude/settings.local.json`, `.gemini/settings.json`, `.config/gemini/settings.json`
- `.postman/`, `.config/Postman/`, `.insomnia/`, `.config/Insomnia/`, `.httpie/`, `.config/httpie/`, `.bruno/`
- `.cursor/mcp.json`, `.cursor/settings.json`, `.continue/config.json`, `.aider.conf.yml`, `.aider.env`, `.codeium/config.json`, `.config/Codeium/config.json`
- `.aws/`, `.gcloud/`, `.config/gcloud/application_default_credentials.json`, `.config/gcloud/credentials.db`, `.config/gcloud/access_tokens.db`, `.config/gcloud/legacy_credentials/`, `clouds.yaml`, `secure.yaml`, `.config/openstack/clouds.yaml`, `.config/openstack/secure.yaml`, `rclone.conf`, `.config/rclone/rclone.conf`, `.azure/`, `.kube/`, `.oci/`, `.oraclebmc/`, `kubeconfig`, `kube.config`
- `credentials.json`, `application_default_credentials.json`, `client_secret*.json`, `service-account*.json`, `firebase-adminsdk*.json`, `google-credentials*.json`
- `*.key`, `*.pem`, `*.crt`, `*.cer`, `*.der`, `*.csr`, `*.p7b`, `*.p7c`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.truststore`
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ecdsa_sk`, `id_ed25519`, `id_ed25519_sk`
- `data/local_ai.sqlite3`
- `data/*.sqlite3`, `data/*.sqlite3-*`, `data/*.sqlite`, `data/*.sqlite-*`, `data/*.db`, `data/*.db-*`
- `data/chroma/`
- `data/uploads/`
- `data/logs/`
- `logs/`, `*.log`
- `data/*.jsonl`
- `*.tfstate`, `*.tfstate.*`
- `Pulumi.*.yaml`, `Pulumi.*.json`
- `.vault_pass`, `.vault_password`, `*.vault`
- 개인 문서 원문
- API key, token, password, private key, certificate, credential

## 검증 기준

공개 전 아래 명령이 통과해야 한다.

```bash
.venv/bin/pytest
.venv/bin/python -m compileall app cli scripts
.venv/bin/python scripts/public_release_check.py --root . --json
git diff --check
.venv/bin/python scripts/local_ci_check.py --root .
```

현재 검증 상태:

- `.venv/bin/pytest`: `551 passed`
- `.venv/bin/python -m compileall app cli scripts`: 성공
- `.venv/bin/python scripts/public_release_check.py --root . --json`: `ok=true`, finding 없음
- `git diff --check`: 성공
- `.venv/bin/python scripts/local_ci_check.py --root .`: 성공

## 명확한 한계

- 브라우저 클릭/입력/전송 자동화는 지원하지 않는다.
- 실제 shell 실행은 지원하지 않고 dry-run 정책 판단만 제공한다.
- 파일 생성/수정/삭제 자동화는 지원하지 않는다.
- Chroma/SQLite repair는 `repair-preview`만 제공하며 실제 repair/delete/rebuild는 수행하지 않는다.
- 운영 배포, 클라우드 리소스 생성, Oracle 리소스 연결은 수행하지 않았다.
- DB migration, 운영 데이터 변경, 비용이 발생할 수 있는 리소스 사용은 수행하지 않았다.
- 다중 사용자 auth/RBAC, HTTPS termination은 제공하지 않는다.

## 공개 후 다음 개선 경계

Codex가 바로 이어서 할 수 있는 안전한 개선:

1. README, API 문서, UI bridge 문서의 endpoint/response field 계약 테스트와 runtime endpoint count drift check 유지
2. README/Project Summary Runtime Contract Snapshot 값을 실제 API/CLI/smoke flow inventory와 비교하는 계약 유지
3. 승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary가 민감 정보 없이 유지되는지 검증
4. 대용량 색인 job/status API progress response schema preview-only 계약을 기준으로 실제 queue 활성화 조건 문서 유지
5. Chroma 누락 vector 재생성 preview-only endpoint를 기준으로 실제 rebuild 활성화 조건 문서 유지
6. assistant bridge smoke expected output과 UI 수동 QA 체크리스트를 최신 preview endpoint 표시 기준과 함께 유지
7. PDF OCR fallback mock coverage와 `/documents/supported-types`의 `pdf_ocr` 계약 유지

별도 승인 또는 보안 리뷰가 필요한 개선:

1. 실제 repair/delete/rebuild 실행 명령
2. 실제 브라우저 click/fill/submit 자동화
3. 실제 shell 실행 또는 파일 생성/수정/삭제 자동화
4. JavaScript 렌더링, 외부 URL 크롤링, pdf2image/poppler 기반 page rendering OCR 확장
5. 운영 배포, HTTPS termination, 다중 사용자 권한 관리, 분산 rate limit
6. DB migration, 운영 데이터 변경, 비용이 발생할 수 있는 cloud/Oracle 리소스 사용

## 공개 전 마지막 확인

- [ ] `docs/RELEASE_CHECKLIST.md` 확인
- [ ] `SECURITY.md` 확인
- [ ] `README.md`의 배포 상태가 로컬 실행 기준으로 표시되어 있는지 확인
- [ ] README와 Project Summary의 기능 경계 표가 현재 구현과 맞는지 확인
- [ ] README, Project Summary, Public Release Summary의 다음 개선 경계가 서로 맞는지 확인
- [ ] `.venv/bin/python scripts/public_release_check.py --root . --json` 결과 확인
- [ ] 민감 파일이 staging되지 않았는지 `git status --short`로 확인
