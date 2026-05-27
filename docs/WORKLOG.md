# WORKLOG

## 2026-05-27 14:34 KST

### Public release API client credential guard

- `scripts/public_release_check.py`가 API client credential 후보 `.postman/`, `.config/Postman/`, `.insomnia/`, `.config/Insomnia/`, `.httpie/`, `.config/httpie/`, `.bruno/`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 Postman/Insomnia/HTTPie/Bruno credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `511 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `232 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `511 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:30 KST

### Public release external LLM credential guard

- `scripts/public_release_check.py`가 외부 LLM credential 후보 `.openai/`, `.config/openai/`, `.anthropic/`, `.claude.json`, `.claude/settings.local.json`, `.gemini/settings.json`, `.config/gemini/settings.json`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 OpenAI/Anthropic/Claude/Gemini credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `504 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `225 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `504 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:25 KST

### Public release AI/ML hub credential guard

- `scripts/public_release_check.py`가 AI/ML hub credential 후보 `.huggingface/token`, `.cache/huggingface/token`, `.cache/huggingface/stored_tokens`, `.config/huggingface/token`, `.kaggle/kaggle.json`, `.config/kaggle/kaggle.json`, `.wandb/settings`, `.config/wandb/settings`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 Hugging Face/Kaggle/W&B credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `497 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `218 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `497 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:20 KST

### Public release data platform credential guard

- `scripts/public_release_check.py`가 data platform credential 후보 `.dbt/profiles.yml`, `.databrickscfg`, `.config/databricks/credentials`, `.snowsql/config`, `.config/snowflake/config.toml`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 DBT/Databricks/SnowSQL/Snowflake credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `489 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `210 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `489 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:16 KST

### Public release Composer and Conda credential guard

- `scripts/public_release_check.py`가 Composer/Conda credential 후보 `.composer/auth.json`, `.config/composer/auth.json`, `.condarc`, `.config/conda/condarc`, `.continuum/anaconda-client/tokens`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 Composer/Conda credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `484 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `205 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `484 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:12 KST

### Public release JVM and NuGet credential guard

- `scripts/public_release_check.py`가 JVM/.NET package credential 후보 `.gradle/gradle.properties`, `.m2/settings.xml`, `NuGet.Config`, `nuget.config`, `.nuget/NuGet/NuGet.Config`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 파일 경로와 내용만으로 JVM/NuGet credential 후보 탐지를 검증한다.
- `.config` 확장자를 공개 전 텍스트 스캔 대상에 추가해 config 파일 안의 secret 후보도 탐지되도록 했다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `479 passed` 기준으로 맞췄다.
- 외부 LLM API 추가, 시스템 의존성 설치, 운영 배포, Oracle 리소스 연결, 브라우저 조작, shell 실행 활성화, 파일 write/delete 실행 기능 활성화는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `200 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `479 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:06 KST

### Public release OCI credential guard

- `scripts/public_release_check.py`가 Oracle/OCI credential 후보 `.oci/`, `.oraclebmc/`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 OCI credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic config 경로만으로 OCI credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `473 passed` 기준으로 맞췄다.
- Oracle 리소스 연결, credential 사용/출력, 운영 배포, 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `194 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `473 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:04 KST

### Public release SOPS age key guard

- `scripts/public_release_check.py`가 SOPS age identity 후보 `.config/sops/age/keys.txt`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 SOPS age key 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 key 없이 synthetic 경로만으로 SOPS age key 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `471 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `192 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `471 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 14:01 KST

### Public release local secret store guard

- `scripts/public_release_check.py`가 local secret store 후보 `.gnupg/`, `.password-store/`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 local secret store 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 secret 없이 synthetic 경로만으로 GnuPG/pass password-store 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `470 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `191 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `470 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:59 KST

### Public release rclone config guard

- `scripts/public_release_check.py`가 cloud/storage credential 후보 `rclone.conf`, `.config/rclone/rclone.conf`를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 rclone config 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic config 경로만으로 rclone config 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `468 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `189 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `468 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:51 KST

### Public release OpenStack credential guard

- `scripts/public_release_check.py`가 OpenStack credential 후보 `clouds.yaml`, `secure.yaml`, `.config/openstack/clouds.yaml`, `.config/openstack/secure.yaml`을 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 OpenStack credential 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic YAML 경로만으로 OpenStack credential 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `466 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `187 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `466 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:48 KST

### Public release gcloud legacy credentials guard

- `scripts/public_release_check.py`가 `.config/gcloud/legacy_credentials/` 디렉터리를 공개 전 private data 목록과 sensitive path regex에서 다루도록 보강했다.
- `.gitignore`, `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 gcloud legacy credentials 제외 경계를 반영했다.
- `tests/test_public_release_check.py`가 실제 credential 없이 synthetic 경로 `.config/gcloud/legacy_credentials/user@example.test/adc.json` 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `462 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `183 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `462 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:46 KST

### Public release sqlite3 variant guard

- `scripts/public_release_check.py`가 `data/*.sqlite3`와 `data/*.sqlite3-*` 변형을 공개 전 private data 목록과 sensitive path regex에서 명시적으로 다루도록 보강했다.
- `tests/test_public_release_check.py`가 generic `data/cache.sqlite3`와 sidecar `data/cache.sqlite3-shm` 경로를 검증하고, `.gitignore`, `SECURITY.md`, release docs mirror 계약도 함께 확인한다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 SQLite/DB 공개 제외 문구를 `.gitignore`와 맞췄다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `461 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` | `182 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `461 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:44 KST

### Public release GitHub alternate token prefix guard

- `tests/test_public_release_check.py`가 GitHub OAuth/User/App/refresh token prefix 후보(`gho_`, `ghu_`, `ghs_`, `ghr_`)를 synthetic 문자열로 각각 검증하도록 보강했다.
- `scripts/public_release_check.py`의 기존 GitHub alternate token regex가 특정 prefix 하나에만 기대지 않는지 테스트 계약으로 고정했다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `459 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `173 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `459 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:26 KST

### Public release GitHub app token candidate guard

- `scripts/public_release_check.py`가 GitHub OAuth/App/refresh token 후보(`gho_`, `ghu_`, `ghs_`, `ghr_`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 GitHub App token 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `456 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `170 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `456 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:21 KST

### Public release GitHub fine-grained token candidate guard

- `scripts/public_release_check.py`가 GitHub fine-grained PAT 후보(`github_pat_...`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 GitHub fine-grained PAT 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `455 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `169 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `455 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:18 KST

### Public release npm token candidate guard

- `scripts/public_release_check.py`가 npm token 후보(`npm_...`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 npm token 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `454 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `168 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `454 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:15 KST

### Public release Discord token candidate guard

- `scripts/public_release_check.py`가 Discord-style bot token 후보(`segment.segment.segment`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 Discord bot token 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `453 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `167 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `453 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:10 KST

### Public release Telegram token candidate guard

- `scripts/public_release_check.py`가 Telegram bot token 후보(`digits:secret-segment`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 Telegram bot token 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `452 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `166 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `452 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:06 KST

### Public release Anthropic token candidate guard

- `scripts/public_release_check.py`가 Anthropic-style token 후보(`sk-ant-...`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 Anthropic-style key 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `451 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `165 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `451 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 13:03 KST

### Public release SendGrid token candidate guard

- `scripts/public_release_check.py`가 SendGrid-style API key 후보(`SG.<segment>.<segment>`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 SendGrid key 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `450 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `164 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `450 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:24 KST

### Public release Stripe token candidate guard

- `scripts/public_release_check.py`가 Stripe-style secret/restricted key 후보(`sk_live_...`, `sk_test_...`, `rk_live_...`, `rk_test_...`)를 공개 전 secret text candidate로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값 없이 synthetic 문자열 조립 방식으로 Stripe secret/restricted key 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `449 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `163 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `449 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:22 KST

### Public release private data duplicate guard

- `tests/test_public_release_check.py`가 `PUBLIC_RELEASE_PRIVATE_DATA`에 중복 항목이 없는지 검증하도록 보강했다.
- public release scanner private data 목록이 커져도 중복으로 `.gitignore`, `SECURITY.md`, release docs mirror 계약이 흐려지지 않게 했다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `447 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `168 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `447 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:19 KST

### Public release security docs mirror guard

- `tests/test_public_release_check.py`가 `PUBLIC_RELEASE_PRIVATE_DATA`의 credential mirror 항목이 `SECURITY.md`에도 남아 있는지 검증하도록 보강했다.
- 같은 테스트가 `SECURITY.md`의 grouped local data 항목(`data/local_ai.sqlite3`, `data/chroma/`, `data/uploads/`, `data/logs/`, `data/*.jsonl`)도 계속 확인한다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`, `.gitignore` 전체 mirror 검증은 기존 계약 그대로 유지했다.
- 테스트 개수 변화는 없어서 공개/최종/handoff 문서의 최신 pytest 수치 `446 passed`는 유지했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `152 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `446 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:16 KST

### Public release hub CLI credential guard

- `.gitignore`가 legacy hub CLI auth 파일 후보(`.config/hub`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 hub CLI config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/hub` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `446 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `167 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `446 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:14 KST

### Local CI public release contract guard

- `tests/test_local_ci_check.py`가 `scripts/local_ci_check.py` 실행 시 project root를 `cwd`로 고정하고 stdout/stderr capture, text mode, non-raising subprocess policy를 유지하는지 검증하도록 보강했다.
- 같은 테스트가 public release check 명령이 resolved project root와 `--json`을 포함하고, 마지막 단계가 `git diff --check`인지 확인한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `445 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_local_ci_check.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `25 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `445 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:12 KST

### Public release Sentry CLI credential guard

- `.gitignore`가 Sentry CLI auth 파일 후보(`.sentryclirc`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Sentry CLI config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.sentryclirc` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `444 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `166 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `444 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:09 KST

### Public release Helm credential guard

- `.gitignore`가 Helm credential/config 파일 후보(`.config/helm/registry/config.json`, `.config/helm/repositories.yaml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Helm config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/helm/registry/config.json`, `.config/helm/repositories.yaml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `443 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `165 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `443 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:06 KST

### Public release containers auth credential guard

- `.gitignore`가 container registry auth 파일 후보(`.config/containers/auth.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 containers auth filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/containers/auth.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `441 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `163 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `441 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 11:02 KST

### Public release Fly CLI credential guard

- `.gitignore`가 Fly.io CLI auth 파일 후보(`.fly/config.yml`, `.fly/config.yaml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Fly.io CLI config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.fly/config.yml`, `.fly/config.yaml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `440 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `162 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `440 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 10:58 KST

### Public release deploy CLI credential guard

- `.gitignore`가 deploy CLI auth 파일 후보(`.vercel/auth.json`, `.netlify/config.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Vercel/Netlify auth filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.vercel/auth.json`, `.netlify/config.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `438 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `160 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `438 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 10:54 KST

### Public release DigitalOcean CLI credential guard

- `.gitignore`가 DigitalOcean CLI credential 파일 후보(`.config/doctl/config.yaml`, `.config/doctl/config.yml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 doctl config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/doctl/config.yaml`, `.config/doctl/config.yml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `436 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `158 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `436 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 10:50 KST

### Public release Kubernetes config guard

- `.gitignore`가 Kubernetes config 파일 후보(`kubeconfig`, `kube.config`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Kubernetes config filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `kubeconfig`, `kube.config` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `434 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `156 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `434 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:22 KST

### Public release gcloud config credential guard

- `.gitignore`가 gcloud config credential 파일 후보(`.config/gcloud/application_default_credentials.json`, `.config/gcloud/credentials.db`, `.config/gcloud/access_tokens.db`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 gcloud config credential filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/gcloud/application_default_credentials.json`, `.config/gcloud/credentials.db`, `.config/gcloud/access_tokens.db` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `432 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `154 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `432 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:18 KST

### Public release pip and Poetry credential guard

- `.gitignore`가 pip/Poetry credential 파일 후보(`.config/pip/pip.conf`, `.config/pypoetry/auth.toml`, `pypoetry/auth.toml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 pip/Poetry credential filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/pip/pip.conf`, `.config/pypoetry/auth.toml`, `pypoetry/auth.toml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `429 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `151 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `429 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:15 KST

### Public release GitHub CLI credential guard

- `.gitignore`가 GitHub CLI credential 파일 후보(`.config/gh/hosts.yml`, `.config/gh/hosts.yaml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 GitHub CLI hosts filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.config/gh/hosts.yml`, `.config/gh/hosts.yaml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `426 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `148 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `426 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:12 KST

### Public release IaC credential guard

- `.gitignore`가 IaC credential 파일 후보(`.terraformrc`, `terraform.rc`, `.pulumi/credentials.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Terraform/Pulumi credential filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.terraformrc`, `terraform.rc`, `.pulumi/credentials.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `424 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `146 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `424 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:08 KST

### Public release ecosystem credential guard

- `.gitignore`가 ecosystem credential 파일 후보(`auth.json`, `.gem/credentials`, `.cargo/credentials`, `.cargo/credentials.toml`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 ecosystem credential filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `auth.json`, `.gem/credentials`, `.cargo/credentials`, `.cargo/credentials.toml` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `421 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `143 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `421 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 09:04 KST

### Public release package manager credential guard

- `.gitignore`가 package manager credential 파일 후보(`.yarnrc`, `.yarnrc.yml`, `.pnpmrc`, `pip.conf`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 package manager credential filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.yarnrc`, `.yarnrc.yml`, `.pnpmrc`, `pip.conf` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `417 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `139 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `417 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 01:05 KST

### Public release Ansible vault guard

- `.gitignore`가 Ansible vault 파일 후보(`.vault_pass`, `.vault_password`, `*.vault`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Ansible vault filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.vault_pass`, `.vault_password`, `prod.vault` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `413 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `135 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `413 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 01:01 KST

### Public release Pulumi stack guard

- `.gitignore`가 Pulumi stack 파일 후보(`Pulumi.*.yaml`, `Pulumi.*.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Pulumi stack filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `Pulumi.dev.yaml`, `Pulumi.prod.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `410 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `132 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `410 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:59 KST

### Public release Terraform state guard

- `.gitignore`가 Terraform state 파일 후보(`*.tfstate`, `*.tfstate.*`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 Terraform state filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `terraform.tfstate`, `terraform.tfstate.backup` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `408 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `130 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `408 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:57 KST

### Public release certificate container filename guard

- `.gitignore`가 certificate container filename 후보(`*.der`, `*.csr`, `*.p7b`, `*.p7c`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 certificate container filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 key/certificate 파일 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `secrets/local.der`, `secrets/local.csr`, `secrets/local.p7b`, `secrets/local.p7c` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `406 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `128 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `406 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:54 KST

### Public release Java keystore filename guard

- `.gitignore`가 Java keystore/truststore filename 후보(`*.jks`, `*.keystore`, `*.truststore`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 keystore/truststore filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 key/certificate 파일 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `secrets/local.jks`, `secrets/local.keystore`, `secrets/local.truststore` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `402 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `124 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `402 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:52 KST

### Public release OpenSSH security key filename guard

- `.gitignore`가 OpenSSH security key filename 후보(`id_ecdsa_sk`, `id_ed25519_sk`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 OpenSSH security key filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 key/certificate 파일 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `secrets/id_ecdsa_sk`, `secrets/id_ed25519_sk` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `399 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `121 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `399 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:50 KST

### Public release SSH key filename contract guard

- `.gitignore`가 standalone SSH private key filename 후보(`id_dsa`, `id_ecdsa`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`의 공개 전 비공개 파일 목록이 기존 path regex의 `id_dsa`, `id_ecdsa` 탐지 범위와 일치하도록 맞췄다.
- `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 key/certificate 파일 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `secrets/id_dsa`, `secrets/id_ecdsa` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `397 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `119 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `397 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:48 KST

### Public release secrets directory guard

- `.gitignore`가 project-local secret directory 후보(`secrets/`, `.secrets/`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 secret directory 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `secrets/notes.txt`, `.secrets/token.txt` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `395 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `117 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `395 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:46 KST

### Public release credential dotfile expansion guard

- `.gitignore`가 standalone credential dotfile 후보(`.git-credentials`, `.boto`, `.s3cfg`, `.pgpass`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 credential dotfile filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.git-credentials`, `.boto`, `.s3cfg`, `.pgpass` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `393 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `115 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `393 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:43 KST

### Public release provider credential JSON filename guard

- `.gitignore`가 standalone provider credential JSON 후보(`application_default_credentials.json`, `firebase-adminsdk*.json`, `google-credentials*.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 provider credential JSON filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `application_default_credentials.json`, `firebase-adminsdk-local.json`, `google-credentials-local.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `389 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `111 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `389 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:41 KST

### Public release credential JSON filename guard

- `.gitignore`가 project-local credential JSON 후보(`credentials.json`, `client_secret*.json`, `service-account*.json`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 credential JSON filename 패턴을 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `credentials.json`, `client_secret_local.json`, `service-account-local.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `386 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `108 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `386 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:37 KST

### Public release SSH and Docker credential directory guard

- `.gitignore`가 project-local credential 디렉터리(`.ssh/`, `.docker/`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 credential 디렉터리 경로를 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.ssh/config`, `.docker/config.json` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `383 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `105 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `383 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:31 KST

### Public release cloud credential directory guard

- `.gitignore`가 project-local cloud credential 디렉터리(`.aws/`, `.gcloud/`, `.azure/`, `.kube/`)를 제외하도록 보강했다.
- `scripts/public_release_check.py`가 같은 credential 디렉터리 경로를 공개 전 high finding으로 감지하도록 보강했다.
- `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 비공개 파일/경로 목록을 `.gitignore`와 scanner 계약에 맞췄다.
- `tests/test_public_release_check.py`가 `.aws/credentials`, `.gcloud/application_default_credentials.json`, `.azure/accessTokens.json`, `.kube/config` 경로를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `381 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` | `103 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `381 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:27 KST

### Public release GraphQL text scan guard

- `scripts/public_release_check.py`가 GraphQL request/schema 파일(`.gql`, `.graphql`)도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 `query.gql`, `query.graphql` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `377 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `71 passed, 1 warning` |
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py` | `92 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `377 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:15 KST

### Public release API client and notebook text scan guard

- `scripts/public_release_check.py`가 API client 파일(`.http`, `.rest`)과 notebook 파일(`.ipynb`)도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 `request.http`, `request.rest`, `analysis.ipynb` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `375 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `69 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `375 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:10 KST

### Public release tabular text scan guard

- `scripts/public_release_check.py`가 `.csv`, `.tsv` 데이터성 텍스트 파일도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 `export.csv`, `export.tsv` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `372 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `66 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `372 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:07 KST

### Public release Windows script text scan guard

- `scripts/public_release_check.py`가 Windows script 파일인 `.ps1`, `.bat`, `.cmd`도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 `setup.ps1`, `setup.bat`, `setup.cmd` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `370 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `64 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `370 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:04 KST

### Public release Terraform text scan guard

- `scripts/public_release_check.py`가 Terraform/HCL 설정 파일인 `.tf`, `.tfvars`, `.hcl`도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 `main.tf`, `terraform.tfvars`, `terragrunt.hcl` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `367 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `61 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `367 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-27 00:01 KST

### Public release lock and SQL text scan guard

- `scripts/public_release_check.py`가 `.lock`, `.sql` 파일도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 dependency lock 파일(`poetry.lock`)과 SQL 파일(`schema.sql`) 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `364 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `58 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `364 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:59 KST

### Public release build config text scan guard

- `scripts/public_release_check.py`가 `.xml`, `.gradle`, `.kts` 빌드/설정 파일도 secret text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 Maven `settings.xml`, Gradle `build.gradle`, Gradle Kotlin DSL `build.gradle.kts` 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `362 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py` | `56 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `362 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:57 KST

### Public release credential dotfile guard

- `.gitignore`, `scripts/public_release_check.py`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`, `SECURITY.md`가 `.envrc`, `.npmrc`, `.pypirc`, `.netrc` credential dotfile을 GitHub 공개 전 제외 대상으로 함께 다루도록 맞췄다.
- `tests/test_public_release_check.py`가 direnv, npm, PyPI, netrc credential 파일 후보를 high finding으로 감지하고 `.gitignore`/release checklist/public summary 문서 계약과 일치하는지 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `359 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `66 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `359 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:54 KST

### Public release provider and certificate guard

- `.gitignore`, `scripts/public_release_check.py`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`가 `.crt`, `.cer` certificate 파일 변형을 GitHub 공개 전 제외 대상으로 함께 다루도록 맞췄다.
- `scripts/public_release_check.py`가 GitLab personal access token 후보(`glpat-...`), Slack token 후보(`xox...`), Google API key 후보(`AIza...`)를 secret 후보로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값을 넣지 않고 synthetic 문자열 조립 방식으로 provider token 후보와 certificate 파일 후보 탐지를 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `355 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `62 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `355 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:51 KST

### Public release env variant and bearer guard

- `.gitignore`, `scripts/public_release_check.py`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`, `SECURITY.md`가 `.env.*` 환경 파일 변형을 GitHub 공개 전 제외 대상으로 함께 다루도록 맞췄다.
- `scripts/public_release_check.py`가 `credential` key-value 후보와 긴 `Authorization: Bearer ...` token 후보를 secret 후보로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 `.env.local`, `.env.production`, `credential`, Bearer token 후보 탐지와 `.env.example` 허용 계약을 검증한다.
- 공개/최종/handoff 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `350 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `57 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `350 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:46 KST

### Public release Hugging Face token guard

- `scripts/public_release_check.py`가 Hugging Face token 후보(`hf_...`)를 GitHub 공개 전 secret 후보로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값을 넣지 않고 synthetic 문자열 조립 방식으로 Hugging Face token 후보 탐지를 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `346 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_local_ci_check.py` | `43 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `346 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:44 KST

### Public release provider token guard

- `scripts/public_release_check.py`가 GitHub token 후보(`ghp_...`)와 AWS access key id 후보(`AKIA...`)를 GitHub 공개 전 secret 후보로 감지하도록 보강했다.
- `tests/test_public_release_check.py`가 실제 token 값을 넣지 않고 synthetic 문자열 조립 방식으로 provider token 후보 탐지를 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `345 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_local_ci_check.py` | `42 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `345 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:39 KST

### Public release unreadable file guard

- `scripts/public_release_check.py`가 text scan 대상 파일을 권한 문제 등으로 읽을 수 없을 때 조용히 넘기지 않고 high finding으로 반환하도록 보강했다.
- binary-ish 파일의 `UnicodeDecodeError`는 기존처럼 skip하되, `PermissionError` 같은 `OSError`는 공개 전 확인 대상이 되도록 분리했다.
- `tests/test_public_release_check.py`가 unreadable text file을 high finding으로 감지하는지 mock 기반으로 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `343 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_local_ci_check.py` | `40 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `343 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:37 KST

### Public release log file guard

- `.gitignore`와 `scripts/public_release_check.py`가 `logs/`와 `*.log`도 GitHub 공개 전 민감 로그 경로로 다루도록 보강했다.
- `tests/test_public_release_check.py`가 `logs/app.log`와 root `app.log` 후보를 high finding으로 감지하고, release checklist/public summary에도 같은 제외 항목이 남아 있는지 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `342 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_security_docs_contract.py` | `49 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `342 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:35 KST

### Public release SQLite sidecar guard

- `.gitignore`와 `scripts/public_release_check.py`가 `data/*.sqlite-*`, `data/*.db-*` 같은 SQLite WAL/SHM/journal sidecar 파일도 GitHub 공개 전 민감 경로로 다루도록 보강했다.
- `tests/test_public_release_check.py`가 `data/local_ai.sqlite-wal`, `data/local_ai.sqlite-shm`, `data/local_ai.db-journal` 후보를 high finding으로 감지하고, release checklist/public summary에도 같은 제외 항목이 남아 있는지 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `340 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_security_docs_contract.py` | `47 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `340 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:30 KST

### Public release DB filename variant guard

- `.gitignore`와 `scripts/public_release_check.py`가 `data/*.sqlite`, `data/*.db` 같은 SQLite/DB 파일명 변형도 GitHub 공개 전 민감 경로로 다루도록 보강했다.
- `tests/test_public_release_check.py`가 `data/local_ai.sqlite`, `data/local_ai.db` 후보를 high finding으로 감지하고, release checklist/public summary에도 같은 제외 항목이 남아 있는지 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `337 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_security_docs_contract.py` | `44 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `337 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:28 KST

### Public release text scan extension guard

- `scripts/public_release_check.py`가 `.sh`, `.ini`, `.conf`, `.properties` 같은 일반 설정/스크립트 파일도 text scan 대상으로 포함하도록 보강했다.
- `tests/test_public_release_check.py`가 해당 확장자 파일 안의 `LOCAL_API_KEY=...` 후보를 high finding으로 감지하는지 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `335 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_local_ci_check.py` | `32 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `335 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:26 KST

### Public release key filename case guard

- `scripts/public_release_check.py`가 `.ENV`, `.PEM`, `ID_RSA`처럼 대소문자가 바뀐 env/key/certificate 파일명도 GitHub 공개 전 민감 경로로 감지하도록 보강했다.
- `.env.example`은 대소문자 비교 기준으로 계속 허용해 문서용 예시 파일 계약을 유지한다.
- `tests/test_public_release_check.py`가 대소문자 변형 민감 파일명 후보를 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `331 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `38 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `331 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:06 KST

### Public release key file guard

- `.gitignore`와 `scripts/public_release_check.py`가 `.key`, `.pem`, `.p12`, `.pfx`, `id_rsa`, `id_ed25519` 같은 key/certificate 파일을 GitHub 공개 전 민감 경로로 다루도록 보강했다.
- `tests/test_public_release_check.py`가 key/certificate 파일 경로 후보를 high finding으로 감지하고, `docs/RELEASE_CHECKLIST.md`와 `docs/PUBLIC_RELEASE_SUMMARY.md`에 같은 비공개 항목이 남아 있는지 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `328 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `35 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `328 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 23:00 KST

### Public release JSON and YAML secret guard

- `scripts/public_release_check.py`가 `.env` 형식뿐 아니라 JSON/YAML의 quoted `api_key`, unquoted `token`, `secret`, `password` 후보도 감지하도록 보강했다.
- 코드 변수명인 `requires_api_key` 같은 일반 문자열을 오탐하지 않도록 colon 기반 패턴은 quoted JSON 값 또는 한 줄 YAML 값으로 제한했다.
- `tests/test_public_release_check.py`가 JSON/YAML secret 후보와 placeholder 허용 계약을 함께 검증한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `322 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_local_ci_check.py` | `19 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `322 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:56 KST

### Public release placeholder guard

- `tests/test_public_release_check.py`가 공개 문서에서 쓰는 `X-API-Key: <LOCAL_API_KEY>`와 `Authorization: Bearer <LOCAL_API_KEY>` placeholder를 secret 후보로 오탐하지 않는지 검증하도록 보강했다.
- 실제 긴 token, API key, private key 후보는 계속 high finding으로 감지하는 기존 계약을 유지한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `320 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_public_release_summary.py` | `27 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `320 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:47 KST

### Public release secret pattern guard

- `tests/test_public_release_check.py`가 `sk-...` 형태의 API key 후보와 PEM private key 후보를 public release scanner가 high finding으로 감지하는지 검증하도록 보강했다.
- 로컬 데이터 경로뿐 아니라 파일 내용 안의 secret 후보 탐지도 공개 전 안전장치로 유지한다.
- fake secret 문자열이 public release scanner에 걸리지 않도록 테스트 소스에서는 민감 패턴을 조각내서 조립한다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `319 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_check.py tests/test_security_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py` | `41 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `319 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:42 KST

### Local CI public release JSON guard

- `tests/test_local_ci_check.py`가 `scripts/local_ci_check.py` 내부 public release check 단계에 `--json`이 유지되는지 직접 검증하도록 보강했다.
- 이는 문서 표기뿐 아니라 실제 local CI 실행 경로도 machine-readable public release check를 계속 사용하게 하는 안전 가드다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_local_ci_check.py tests/test_operations_runbook.py` | `8 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `317 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:38 KST

### Final report verification command guard

- `tests/test_portfolio_docs_contract.py`가 `docs/PROJECT_SUMMARY.md`와 `docs/FINAL_REPORT.md`의 테스트 실행 방법 코드블록에 같은 baseline 검증 명령 세트가 남아 있는지 함께 검증하도록 보강했다.
- `docs/FINAL_REPORT.md`의 번호 포함 heading과 `docs/PROJECT_SUMMARY.md`의 일반 heading을 각각 인식하도록 테스트를 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_portfolio_docs_contract.py` | `8 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `317 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:25 KST

### Project summary verification block guard

- `docs/PROJECT_SUMMARY.md`의 테스트 실행 방법 코드블록을 최종 보고/공개 요약 문서와 같은 baseline 검증 명령 세트로 맞췄다.
- `tests/test_portfolio_docs_contract.py`가 Project Summary의 테스트 실행 블록에 pytest, compileall, public release check, git diff check, local CI 명령이 모두 남아 있는지 검증하도록 보강했다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `317 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py tests/test_public_docs_contract.py` | `37 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `317 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:21 KST

### Claude handoff verification sync

- `docs/CLAUDE_REVIEW_HANDOFF.md`의 현재 검증 상태에 public release check와 local CI 결과를 추가해 공개 요약 문서들과 같은 검증 표면을 갖도록 정리했다.
- `tests/test_portfolio_docs_contract.py`가 Claude review handoff에서도 `--json` public release check 명령을 유지하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_portfolio_docs_contract.py` | `7 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `316 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:15 KST

### Public release check command guard

- `README.md`의 GitHub 공개 전 보안 점검 예시에서 `--json` 없는 public release check 명령을 제거했다.
- `docs/PROJECT_SUMMARY.md`의 공개 전 점검 명령도 `.venv/bin/python scripts/public_release_check.py --root . --json` 기준으로 정리했다.
- `tests/test_portfolio_docs_contract.py`가 README, PROJECT_SUMMARY, FINAL_REPORT, SECURITY에서 `--json` 없는 public release check 명령 드리프트를 잡도록 보강했다.
- 공개 요약 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `316 passed` 기준으로 맞췄다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py tests/test_public_docs_contract.py` | `36 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `316 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:11 KST

### Final verification command cleanup

- `README.md`의 단독 테스트 명령을 `.venv/bin/pytest` 기준으로 정리했다.
- `docs/USER_DOCUMENT_E2E_PLAN.md`의 승인 전 local CI 명령을 `.venv/bin/python scripts/local_ci_check.py --root .` 기준으로 정리했다.
- `docs/OPERATIONS.md`의 공개 전 public release check 명령에 `--json`을 명시했다.
- 관련 문서 테스트가 bare local CI 명령과 public release check 명령 drift를 잡도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_user_document_e2e_plan.py tests/test_operations_runbook.py tests/test_public_docs_contract.py` | `35 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `315 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:07 KST

### Security release checklist guard

- `SECURITY.md`의 공개 전 자동 점검 명령을 `.venv/bin/python scripts/public_release_check.py --root . --json` 기준으로 정리했다.
- `tests/test_security_docs_contract.py`가 `SECURITY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 public release check 명령 표기를 교차 검증하도록 보강했다.
- 새 테스트 추가에 따라 공개/최종/handoff 문서의 최신 pytest 수치를 `315 passed`로 갱신했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_public_docs_contract.py tests/test_operations_runbook.py tests/test_next_chat_handoff.py tests/test_portfolio_docs_contract.py` | `47 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `315 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 22:02 KST

### Handoff boundary verification guard

- `docs/NEXT_CHAT_HANDOFF.md`의 검증 명령을 `.venv/bin/...` 직접 실행 기준으로 정리했다.
- `tests/test_next_chat_handoff.py`가 legacy `source .venv/bin/activate`, bare `pytest`, bare `python -m compileall` 표기가 handoff 검증 블록에 남지 않도록 보강했다.
- `tests/test_next_chat_handoff.py`가 `docs/PUBLIC_RELEASE_SUMMARY.md`도 task board/public docs/handoff 경계 교차 검증에 포함하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_tasks_doc.py tests/test_public_release_summary.py tests/test_public_docs_contract.py` | `32 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 21:58 KST

### Operations verification command guard

- `docs/OPERATIONS.md`의 public release check와 local CI 예시를 `.venv/bin/python` 기준으로 정리했다.
- `tests/test_operations_runbook.py`가 README/release/public summary와 같은 `.venv/bin/python` 기반 local CI 단계 계약을 유지하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_operations_runbook.py tests/test_readme_quick_start.py tests/test_public_release_summary.py tests/test_public_docs_contract.py` | `38 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 21:55 KST

### Smoke summary example guard

- `scripts/smoke_test_api.py`의 document/RAG upload summary에 `chunks_count`를 추가해 paste-safe summary 예시와 실제 출력 필드가 맞도록 정리했다.
- `docs/SMOKE_SUMMARY_EXAMPLES.md`의 assistant bootstrap 예시에 실제 sanitizer 출력 필드인 `ui_ready`를 반영했다.
- `tests/test_smoke_summary_examples.py`가 문서 예시 JSON과 `build_sanitized_smoke_summary()`로 만든 대표 출력이 정확히 일치하는지 검증하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_smoke_summary_examples.py tests/test_smoke_script.py` | `18 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 21:52 KST

### README/API verification command guard

- `README.md`, `docs/API.md`, `docs/PROJECT_SUMMARY.md`의 local CI/public release check 예시를 `.venv/bin/python` 기준으로 정리했다.
- `tests/test_readme_quick_start.py`와 `tests/test_public_docs_contract.py`가 README/release checklist에 `.venv/bin/python` 기반 검증 명령을 유지하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py` | `46 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 21:48 KST

### Release verification command guard

- `docs/PUBLIC_RELEASE_SUMMARY.md`, `docs/RELEASE_CHECKLIST.md`, `docs/NEXT_CHAT_HANDOFF.md`의 최종 검증 명령에서 `scripts/local_ci_check.py` 실행 예시를 `.venv/bin/python` 기준으로 통일했다.
- `tests/test_public_release_summary.py`와 `tests/test_next_chat_handoff.py`가 release/handoff 문서에 `.venv/bin/python scripts/local_ci_check.py --root .`를 유지하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_public_release_summary.py tests/test_next_chat_handoff.py tests/test_tasks_doc.py tests/test_operations_runbook.py tests/test_public_docs_contract.py` | `37 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-26 21:45 KST

### UI QA checklist contract guard

- `docs/UI_QA_CHECKLIST.md`의 UI contract 항목에 refresh/message flow의 method+path 조합을 명시했다.
- `tests/test_ui_qa_checklist.py`가 `AssistantService().ui_contract()`의 `startup_sequence`, `refresh_endpoints`, `message_flow` 항목을 method+path 기준으로 검증하도록 보강했다.
- 브라우저 조작, shell 실행 활성화, 파일 write/delete 활성화, 운영 배포, 외부 LLM API 추가는 하지 않았다.

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/pytest tests/test_ui_qa_checklist.py tests/test_ui_connect_guide.py tests/test_ui_bridge_examples.py` | `18 passed, 1 warning` |
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공, 내부 pytest `314 passed, 1 warning`, compileall 성공, public release check 성공, git diff check 성공 |

## 2026-05-20

### 완료

- `AGENTS.md` 프로젝트 규칙 작성
- FastAPI 백엔드 구조 생성
- Ollama local chat API client 구현
- Ollama local embedding API client 구현
- SQLite DB 모델 및 초기화 구현
- Chroma vector store 구현
- `.txt`, `.md` 문서 로더 구현
- 표준 라이브러리 기반 `.html`, `.htm` 문서 로더 구현
- optional dependency 기반 `.pdf`, `.docx` 문서 로더 구현
- optional dependency 설치 후 실제 PDF/DOCX 업로드, 검색, RAG 검증 완료
- 문서 업로드 중 SQLite write lock을 줄이도록 embedding을 DB write 전에 수행하게 개선
- `EMBEDDING_BATCH_SIZE` 설정과 Ollama `/api/embed` batch 호출 기반 대용량 문서 embedding 개선
- `EMBEDDING_MAX_RETRIES` 기반 embedding batch 재시도 추가
- Chroma `PersistentClient`를 service dependency에서 singleton으로 공유해 동시 첫 요청 500 오류 수정
- DB/Chroma 저장 단계 실패 시 SQLite rollback과 명확한 `DocumentIndexingError` 반환 추가
- character-based chunking 구현
- 문서 업로드, 문서 목록, 문서 상세, 문서 삭제 API 구현
- 로컬 폴더 색인 API 구현
- 로컬 폴더 색인 응답에 파일별 성공/스킵 상세 추가
- search API 구현
- RAG ask API 구현
- feedback API 구현
- Typer CLI 구현
- SFT JSONL export 스크립트 구현
- Ollama 준비 상태 점검용 `/health/ollama`와 `local-ai doctor` 추가
- SQLite/Chroma 상태 점검용 `/documents/stats`와 `local-ai stats` 추가
- SQLite/Chroma 정합성 dry-run 점검용 `/documents/integrity`와 `local-ai integrity` 추가
- SQLite/Chroma repair 후보 미리보기용 `/documents/repair-preview`와 `local-ai repair-preview` 추가
- 실제 저장 전 폴더 색인 read-only preview용 `/documents/index-folder-preview`와 `local-ai index-preview` 추가
- 폴더 색인 preview 응답에 예상 embedding batch 수 추가
- 문서 타입/optional dependency 점검용 `/documents/supported-types`와 `local-ai document-types` 추가
- 문서 chunk 페이지 조회용 `/documents/{document_id}/chunks`와 `local-ai chunks` 추가
- chat log 조회용 `/chat-logs`, `/chat-logs/{chat_log_id}`와 `local-ai logs`, `local-ai log` 추가
- feedback 목록 조회용 `GET /feedback`와 `local-ai feedbacks` 추가
- 문서 목록 필터용 `/documents?source_type=&file_type=&query=`와 `local-ai docs --source-type --file-type --query` 추가
- API 계약 문서 `docs/API.md` 추가
- 운영 로그/저장공간/백업 기준 문서 `docs/OPERATIONS.md` 추가
- 최종/포트폴리오 요약 문서 `docs/PROJECT_SUMMARY.md` 추가
- Claude Sonnet 문서 정합성 리뷰용 handoff `docs/CLAUDE_REVIEW_HANDOFF.md` 추가
- 로컬 운영/공개 전 보안 기준 문서 `SECURITY.md` 추가
- `data/logs/` 운영 로그 디렉터리와 `.gitignore` 로그 제외 규칙 추가
- README 실행 문서와 포트폴리오용 개발 배경/기술 선택/핵심 구현 포인트 정리
- pytest 테스트 추가

### 검증

| 명령 | 결과 |
|---|---|
| `.venv/bin/python scripts/local_ci_check.py --root .` | 성공 |
| `.venv/bin/pytest` | `266 passed` |
| `.venv/bin/python -m compileall app cli scripts` | 성공 |
| `test -f docs/API.md` | API 문서 존재 확인 |
| `test -f docs/CLAUDE_REVIEW_HANDOFF.md` | Claude 리뷰 handoff 문서 존재 확인 |
| `test -f docs/OPERATIONS.md` | 운영 문서 존재 확인 |
| `test -f docs/PROJECT_SUMMARY.md` | 프로젝트 요약 문서 존재 확인 |
| `test -f SECURITY.md` | 보안 문서 존재 확인 |
| `.venv/bin/pip install -e '.[dev,documents]'` | 성공 |
| `curl http://127.0.0.1:8000/health` | `200 OK` |
| `curl http://127.0.0.1:8000/health/ollama` | Ollama/model readiness 확인 가능 |
| `curl -X POST /ask` | Ollama `llama3.2` 실제 호출 성공 |
| `.venv/bin/local-ai health` | 성공 |
| `.venv/bin/local-ai doctor` | Ollama/model readiness 확인 가능 |
| `.venv/bin/local-ai docs` | 성공 |
| `.venv/bin/local-ai stats` | SQLite/Chroma 상태 확인 성공 |
| `.venv/bin/local-ai integrity` | SQLite/Chroma 정합성 dry-run 확인 성공 |
| `.venv/bin/local-ai repair-preview` | repair action 미리보기 성공 |
| `.venv/bin/local-ai document-types` | 문서 타입별 사용 가능 여부 확인 성공 |
| `curl http://127.0.0.1:8000/documents/supported-types` | 문서 타입별 사용 가능 여부 확인 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-documents/jwt-docx-notes.docx` | DOCX 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-documents/jwt-pdf-notes.pdf` | PDF 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "DOCX Authorization header" --top-k 5` | DOCX chunk 검색 성공 |
| `.venv/bin/local-ai search "PDF refresh token local ai server" --top-k 5` | PDF chunk 검색 성공 |
| `.venv/bin/local-ai ask-docs "내 문서 기준으로 access token 전달 방식..." --top-k 3` | DOCX/PDF source 포함 RAG 답변 성공 |
| `CHUNK_SIZE=120 CHUNK_OVERLAP=20 EMBEDDING_BATCH_SIZE=2 .venv/bin/uvicorn ...` | batch embedding 검증 서버 실행 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-batch/batch-notes.txt` | 22개 chunk 업로드, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "batch Authorization header access token" --top-k 5` | batch 업로드 문서 검색 성공 |
| `.venv/bin/local-ai stats` | `documents_count=4`, `chunks_count=25`, `chroma_vectors_count=25` |
| `.venv/bin/local-ai integrity` | `status=ok` |
| `search/stats/integrity 동시 호출` | Chroma singleton 적용 후 모두 성공 |
| `tests/test_document_service.py` | vector store 실패 시 SQLite document/chunk rollback 확인 |
| `.venv/bin/local-ai index-preview /tmp/local-ai-preview` | read-only preview 성공, `files_count=2`, `chunks_estimated=2`, stats 변경 없음 |
| `curl -X POST /documents/index-folder-preview` | read-only preview endpoint 성공 |
| `tests/test_document_service.py` | preview의 `embedding_batch_size`, `embedding_batches_estimated` 계산 확인 |
| `tests/test_document_service.py` | 실제 폴더 색인 응답의 `indexed_files`, `skipped_file_details` 확인 |
| `tests/test_api_contracts.py` | `/documents/index-folder` 파일별 상세 응답 contract 확인 |
| `.venv/bin/local-ai chunks 1 --limit 5 --offset 0` | chunk 페이지 조회 성공 |
| `.venv/bin/local-ai logs --limit 2 --offset 0` | chat log 목록 조회 성공 |
| `.venv/bin/local-ai logs --mode rag --query JWT --limit 3 --offset 0` | chat log 필터 조회 성공 |
| `.venv/bin/local-ai log 9` | chat log 상세 조회 성공 |
| `.venv/bin/local-ai feedbacks --limit 5 --offset 0` | feedback 목록 조회 성공 |
| `curl 'http://127.0.0.1:8000/documents?source_type=upload&file_type=md&query=backend'` | 문서 목록 필터 조회 성공 |
| `.venv/bin/local-ai docs --source-type upload --file-type md --query backend` | 문서 목록 필터 조회 성공 |
| `.venv/bin/local-ai upload /tmp/local-ai-smoke/backend-notes.md` | 문서 업로드, SQLite 저장, embedding, Chroma 저장 성공 |
| `.venv/bin/local-ai search "JWT 인증 흐름"` | Chroma 검색 결과 반환 성공 |
| `.venv/bin/local-ai ask-docs "내 문서 기준으로 JWT 인증 흐름..."` | RAG 답변 및 sources 반환 성공 |

### 확인한 로컬 Ollama 상태

- Ollama server: 실행 중
- 사용 가능 모델:
  - `llama3.2:latest`
  - `codellama:latest`
  - `nomic-embed-text:latest`
- `local-ai doctor` 기준:
  - `llm_model_ready=true`
  - `embedding_model_ready=true`

### 남은 작업

- 실제 사용자 문서로 upload/search/ask-with-docs 검증
- 필요하면 OCR loader 추가
- 필요하면 HTML JavaScript 렌더링/크롤링 범위 결정
- Chroma/SQLite 실제 복구 명령 추가. 단 실제 repair/delete/rebuild는 사용자 승인 필요
- 필요하면 자동 로그 rotation 구현. 단 실제 삭제/압축 자동화 정책은 사용자 승인 후 진행

### RAG 품질 보강

- `llama3.2`가 문서 밖 코드, 링크, 보안 세부사항을 만들 수 있어 RAG prompt를 강화함.
- 코드 블록, 외부 URL, 문서에 없는 보안 키워드, 추측성 표현이 감지되면 보수적인 문서 기반 fallback 답변으로 대체하는 guard를 추가함.
- 관련 테스트를 `tests/test_rag_service.py`에 추가함.

### Integrity dry-run

- `/documents/integrity`는 read-only 점검만 수행한다.
- 실제 repair/delete는 수행하지 않는다.
- 확인 항목:
  - 저장 파일 누락
  - SQLite chunk는 있지만 Chroma vector가 없는 항목
  - Chroma vector는 있지만 SQLite chunk가 없는 orphan vector

### Repair preview

- `/documents/repair-preview`는 integrity 결과를 기반으로 필요한 action 후보만 반환한다.
- 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않는다.
- 현재 로컬 상태에서는 `actions_count=0`이다.

### Folder index preview

- `/documents/index-folder-preview`는 실제 색인 전에 대상 파일, skip 파일, 예상 chunk 수, token estimate를 read-only로 반환한다.
- 전체 응답에는 `embedding_batch_size`, `embedding_batches_estimated`를 포함한다.
- 각 file 항목에는 파일별 `embedding_batches_estimated`를 포함한다.
- CLI는 `local-ai index-preview <folder>`를 제공한다.
- 원본 파일 수정, SQLite 저장, Ollama embedding 생성, Chroma 저장은 수행하지 않는다.
- `LOCAL_API_KEY`가 설정되어 있으면 실제 색인 API와 동일하게 `X-API-Key` 보호를 적용한다.

### Folder index result details

- `/documents/index-folder` 응답에 `indexed_files`와 `skipped_file_details`를 추가했다.
- `indexed_files`는 `path`, `document_id`, `filename`, `file_type`, `chunks_created`를 반환한다.
- `skipped_file_details`는 `path`, `filename`, `reason`을 반환한다.
- 기존 `indexed_documents`, `skipped_files`, `chunks_created`, `document_ids` 필드는 유지한다.

### Chat log 조회

- `/chat-logs`는 질문/답변 preview 중심의 목록을 반환한다.
- `/chat-logs`는 `mode=direct|rag`, `query=<keyword>` 필터를 지원한다.
- `/chat-logs/{chat_log_id}`는 전체 질문/답변/source를 반환한다.
- CLI는 `local-ai logs`, `local-ai log <id>`를 제공한다.

### Feedback 조회

- `GET /feedback`는 feedback preview 목록을 반환한다.
- `rating=good|bad|neutral`, `chat_log_id=<id>` 필터를 지원한다.
- CLI는 `local-ai feedbacks`를 제공한다.

### 문서 목록 필터

- `GET /documents`는 `source_type=upload|folder`, `file_type=txt|md|pdf|docx|html`, `query=<keyword>` 필터를 지원한다.
- `query`는 filename과 stored path 기준으로 검색한다.
- CLI는 `local-ai docs --source-type upload --file-type md --query backend`를 제공한다.

### PDF/DOCX loader

- `.pdf`, `.docx` 확장자를 문서 업로드와 폴더 색인 대상에 포함했다.
- `pypdf`, `python-docx`는 optional dependency로 분리했다.
- optional dependency가 없으면 명확한 `pip install -e '.[documents]'` 안내 메시지를 반환한다.
- `/documents/supported-types`와 `local-ai document-types`로 현재 환경의 문서 타입별 사용 가능 여부를 확인할 수 있다.
- 현재 venv에는 `pypdf`, `python-docx`, `lxml` 설치 완료 상태다.
- 실제 DOCX/PDF 샘플 업로드, 검색, RAG source 반환을 확인했다.
- 스캔 이미지 기반 PDF OCR은 지원하지 않는다.

### HTML/HTM loader

- `.html`, `.htm` 확장자를 문서 업로드와 폴더 색인 대상에 포함했다.
- Python 표준 라이브러리 `html.parser` 기반으로 UTF-8 HTML에서 본문 텍스트를 추출한다.
- `head`, `script`, `style`, `noscript` 내용은 색인 대상에서 제외한다.
- `.htm`과 `.html`은 SQLite `file_type=html`로 정규화한다.
- JavaScript 렌더링 결과, 외부 페이지 fetch, 브라우저 interaction은 지원하지 않는다.

### SQLite write lock / embedding batch 개선

- 기존에는 DB flush 이후 Ollama embedding 호출을 수행해 SQLite write transaction이 길어질 수 있었다.
- 업로드가 겹치면 `sqlite3.OperationalError: database is locked`가 발생할 수 있어, embedding을 DB write 전에 생성하도록 순서를 조정했다.
- DB write 구간은 document/chunk insert와 Chroma 기록 직전 commit으로 짧게 유지한다.
- `EMBEDDING_BATCH_SIZE` 기본값은 `8`이다.
- `EMBEDDING_MAX_RETRIES` 기본값은 `2`이다.
- 여러 chunk embedding은 batch 단위로 Ollama `/api/embed`에 요청한다.
- 일시적인 `OllamaError`는 batch 단위로 재시도하고, 재시도 소진 시 명확한 오류를 반환한다.
- `CHUNK_SIZE=120`, `CHUNK_OVERLAP=20`, `EMBEDDING_BATCH_SIZE=2` 조건에서 22개 chunk 업로드와 검색을 확인했다.
- 동시 첫 요청에서 Chroma client를 여러 개 만들면 `default_tenant`/`bindings` 관련 500 오류가 발생할 수 있어, service dependency가 단일 `VectorStore`를 공유하도록 수정했다.
- DB/Chroma 저장 단계 실패 시 `db.rollback()`을 명시적으로 호출하고 `DocumentIndexingError`를 반환한다.
- vector store 실패 시 SQLite `documents`, `document_chunks`가 남지 않는 테스트를 추가했다.

### 로컬 저장소 / 배포 상태

- 현재 배포: 로컬 실행 기준
- 외부 클라우드 배포: 진행하지 않음
- 외부 LLM API: 사용하지 않음
- 외부 credential: 사용하지 않음
- 로컬 저장 위치:
  - SQLite: `data/local_ai.sqlite3`
  - Chroma: `data/chroma/`
  - 업로드 파일: `data/uploads/`
  - 운영 로그 파일: `data/logs/`

### 운영 로그 / 저장공간 문서

- `docs/OPERATIONS.md`에 로컬 운영 원칙, 저장 위치, 로그 정책, 수동 rotation 예시, 저장공간 점검, 백업 기준, 장애 점검 순서를 정리했다.
- 애플리케이션 코드가 파일 logger를 강제로 만들지는 않는다.
- 파일 로그가 필요하면 `uvicorn ... >> data/logs/server.log 2>&1` 형태로 시작할 수 있게 문서화했다.
- `data/logs/*`는 Git 제외 대상이고, 디렉터리 보존용 `.gitkeep`만 유지한다.

### API 문서

- `docs/API.md`에 endpoint별 요청 예시, 응답 핵심 필드, 보호 endpoint, CLI 대응 관계를 정리했다.
- 실제 repair/delete/rebuild가 수행되지 않는 read-only preview endpoint를 명확히 구분했다.
- CLI는 FastAPI API를 호출하고 비즈니스 로직을 중복 구현하지 않는다는 원칙을 문서화했다.

### Security 문서

- `SECURITY.md`에 로컬 전용 보안 원칙, API key 보호 endpoint, 데이터 저장 위치, 로그 정책, 파일 업로드/색인 보안 기준, RAG 안전 기준, 공개 전 체크리스트를 정리했다.
- 외부 LLM API, 외부 크롤링, browser interaction, 실제 repair/delete/rebuild, Oracle 실제 리소스 작업은 사용자 승인 전 진행하지 않는 고위험 작업으로 명시했다.

### README 포트폴리오 정리

- README 앞부분에 개발 배경, 포트폴리오 관점의 핵심 목표, 기술 선택 이유, 핵심 구현 포인트를 추가했다.
- 구현된 기능과 미구현 기능이 섞이지 않도록 현재 한계와 배포 상태는 별도 섹션으로 유지했다.

### Project summary 문서

- `docs/PROJECT_SUMMARY.md`에 한 줄 소개, 만든 것, 핵심 설계, endpoint 목록, CLI 목록, 실행/테스트 방법, 보안/운영 기준, 현재 한계, 다음 추천 개선을 정리했다.
- 최종 보고나 포트폴리오 제출 시 빠르게 확인할 수 있는 요약 문서 역할을 한다.

### Claude Review Handoff 문서

- `docs/CLAUDE_REVIEW_HANDOFF.md`에 Claude Sonnet이 문서 정합성만 리뷰할 수 있도록 리뷰 목표, 읽을 파일, P0/P1/P2 기준, 금지사항, 출력 형식을 정리했다.
- 이 handoff는 리뷰용이며 코드 수정, 파일 생성, 실제 배포, 외부 API 활성화를 지시하지 않는다.

### 문서 self-check 반영

- `docs/API.md`의 CLI 대응 목록에 `local-ai document-types`를 추가했다.
- README 현재 한계 섹션에 rate limit과 HTTPS termination 미지원 상태를 명시했다.
- `docs/NEXT_CHAT_HANDOFF.md`의 다음 작업을 이미 완료된 README/docs 정합성 점검이 아니라 실제 사용자 문서 E2E 검증과 선택형 개선 후보 중심으로 갱신했다.
- CLI가 FastAPI 백엔드를 호출하는 계약을 mock 기반으로 검증하는 `tests/test_cli.py`를 추가했다.
- `tests/test_security.py`를 확장해 `/ask`, `/ask-with-docs`, `/search`, `/documents/upload`, `/documents/index-folder-preview`, `/documents/index-folder`, `DELETE /documents/{document_id}`, `/feedback` 전체가 `LOCAL_API_KEY` 설정 시 `X-API-Key`를 요구하는지 확인했다.
- `LOCAL_RATE_LIMIT_PER_MINUTE` 기반 process-local in-memory rate limit을 보호 endpoint에 적용했다.
- `tests/test_rate_limiter.py`를 추가해 rate limiter window, 비활성화, API key hash identity를 검증했다.
- `scripts/smoke_test_api.py`를 추가해 실행 중인 서버 기준 `health → upload → search → ask-with-docs → feedback → stats` smoke test를 수행할 수 있게 했다.
- `tests/test_smoke_script.py`를 추가해 smoke script의 API 호출 순서를 mock으로 검증했다.
- `scripts/public_release_check.py`를 추가해 GitHub 공개 전 로컬 데이터와 secret 후보를 read-only로 점검할 수 있게 했다.
- `tests/test_public_release_check.py`를 추가해 `.env`, SQLite, `.env.example`, `.gitkeep` 처리 기준을 검증했다.
- 현재 실제 워크스페이스에서 `python scripts/public_release_check.py --root . --json`는 로컬 SQLite, Chroma, uploads 파일을 공개 전 제외 대상 finding으로 탐지한다. 삭제는 수행하지 않았다.
- 실행형 Agent 계획 API를 추가했다. `/agent/plan`, `/agent/runs`, `/agent/runs/{run_id}`는 요청을 위험도와 승인 필요 action으로 분류/저장/조회한다.
- agent plan 승인/거절 상태 전환 API `/agent/runs/{run_id}/approve`, `/agent/runs/{run_id}/reject`를 추가했다. 승인되어도 실제 실행은 수행하지 않는다.
- agent 실행 엔진 v1과 `/agent/runs/{run_id}/execute`를 추가했다.
- `AGENT_EXECUTION_ENABLED=false` 기본값에서는 실제 실행을 차단한다.
- `AGENT_EXECUTION_ENABLED=true`에서도 v1 실행 엔진은 허용 root 안의 폴더 목록 조회, 텍스트 파일 내용 preview, 명시 URL read-only fetch만 지원한다.
- file preview는 민감 파일, binary 파일, 대용량 파일, 허용되지 않은 확장자를 차단한다.
- `AGENT_WEB_FETCH_MAX_BYTES`로 URL fetch 응답 크기를 제한한다.
- 2차 실행 엔진 A단계로 `/agent/runs/{run_id}/dry-run`, `/agent/runs/{run_id}/actions`를 추가했다.
- dry-run은 실제 파일 내용 읽기, URL fetch, shell 실행, 브라우저 조작 없이 action별 정책 판단만 기록한다.
- `local-ai agent-actions`, `local-ai agent-dry-run`, `local-ai agent-shell` CLI 명령을 추가했다.
- 문서 기반 로컬 비서용 `local-ai assist`와 통합 REPL `local-ai assistant`를 추가했다.
- 차수/다음 작업/Recommended Next Model을 확인하는 `/project/status`, `/project/next`, `local-ai status`, `local-ai next`를 추가했다.
- `local-ai agent-plan`, `local-ai agent-runs`, `local-ai agent-run`, `local-ai agent-results`, `local-ai agent-approve`, `local-ai agent-reject`, `local-ai agent-execute` CLI 명령을 추가했다.
- `tests/test_agent_service.py`, `tests/test_agent_api.py`를 추가했고, `tests/test_security.py`와 `tests/test_cli.py`를 Agent endpoint/CLI까지 확장했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.

### Assistant automation safeguard polish

- assistant REPL에 `/summary`, `/status`, `/next`, `/roots`, `/shell-policy`, `/shell-dry-run <command>` 흐름을 추가했다.
- `local-ai roots`, `local-ai shell-policy`, `local-ai shell-dry-run "pwd"` CLI 명령을 추가했다.
- `/project/shell-policy`와 `/project/shell-dry-run` API를 추가해 shell 실행 전 dry-run 정책 판단만 제공하도록 했다.
- shell dry-run은 allowlist/blocked token 기반으로 `allowed_preview` 또는 `blocked`를 반환하며 실제 명령은 실행하지 않는다.
- `/project/status` 차수를 4차 완료, 5차 수동 로컬 QA/운영 polish 단계로 갱신했다.
- README, `docs/API.md`, `SECURITY.md`, `docs/OPERATIONS.md`, `docs/PROJECT_SUMMARY.md`를 실제 동작과 맞게 갱신했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### Local UI Bearer token 호환

- `LOCAL_API_KEY` 보호 endpoint가 기존 `X-API-Key`와 함께 `Authorization: Bearer <LOCAL_API_KEY>`도 허용하도록 했다.
- 브라우저 기반 로컬 UI의 `Bearer token` 입력칸에 같은 로컬 키를 넣어 붙일 수 있게 했다.
- `tests/test_security.py`에 Bearer header 허용 테스트를 추가했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### UI Bridge Assistant API

- `/assistant/capabilities`, `/assistant/sessions`, `/assistant/sessions/{session_id}`, `/assistant/message`, `/assistant/project-root/validate`를 추가했다.
- `assistant_sessions`, `assistant_messages` SQLite 테이블을 추가해 UI 대화 세션과 메시지를 저장한다.
- `/assistant/message`는 `mode=auto` 기준으로 RAG 답변, 검색, folder index preview, agent plan, shell dry-run으로 안전 분기한다.
- assistant API에서는 실제 폴더 색인 대신 preview만 수행하고, shell은 실제 실행 없이 dry-run 정책 판단만 반환한다.
- `local-ai assistant-capabilities`, `local-ai assistant-session`, `local-ai assistant-message`, `local-ai assistant-root` CLI 명령을 추가했다.
- 테스트 격리를 위해 `tests/conftest.py`에서 로컬 `.env`의 `LOCAL_API_KEY`가 일반 테스트를 오염시키지 않도록 처리했다.

### Browser UI integration support

- `LOCAL_CORS_ORIGINS` 설정을 추가하고 기본값으로 `http://127.0.0.1:5173,http://localhost:5173`을 허용했다.
- FastAPI `CORSMiddleware`를 추가해 로컬 브라우저 UI가 `Authorization`, `Content-Type`, `X-API-Key` header로 API를 호출할 수 있게 했다.
- `GET /assistant/sessions`와 `local-ai assistant-sessions`를 추가해 UI가 최근 대화 세션 목록을 조회할 수 있게 했다.
- `GET /assistant/status`와 `local-ai assistant-status`를 추가해 UI 첫 화면용 문서/세션/integrity/안전 상태를 한 번에 조회할 수 있게 했다.
- CORS preflight와 assistant session list 테스트를 추가했다.
- self-check 이후 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`도 성공했다.
- `scripts/public_release_check.py --root . --json` 결과는 `ok=true`, finding 없음이다.

### UI bootstrap contract

- `POST /assistant/bootstrap`를 추가해 브라우저 UI가 시작 시 capabilities, status, project root 검증, 최근 session 목록, UI 힌트를 한 번에 받을 수 있게 했다.
- `local-ai assistant-bootstrap --project-root /Users/juyoung/local-ai-server` CLI 명령을 추가했다.
- `/assistant/message` 응답에 `ui.response_type`, `ui.severity`, `ui.primary_text`, `ui.display` 힌트를 추가했다.
- shell 실행, 파일 수정/삭제, 브라우저 interaction은 계속 비활성/보호 상태로 유지했다.
- `/project/status` 차수를 8차 UI bootstrap contract 완료, 9차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `61 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### UI readiness helper APIs

- `GET /assistant/ping`을 추가해 브라우저 UI가 token/header/server 연결 상태를 가볍게 확인할 수 있게 했다.
- `GET /assistant/config`를 추가해 CORS origin, allowed roots, 모델명, 저장소, 안전 설정, rate limit을 secret 없이 조회할 수 있게 했다.
- `GET /assistant/dashboard`를 추가해 문서/세션/integrity/연결 상태 카드와 최근 세션을 UI 카드 구조로 반환한다.
- `local-ai assistant-ping`, `local-ai assistant-config`, `local-ai assistant-dashboard` CLI 명령을 추가했다.
- `/project/status` 차수를 9차 UI readiness helper APIs 완료, 10차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `67 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant message paging

- `GET /assistant/sessions/{session_id}/messages`를 추가해 UI가 긴 대화 기록을 paging으로 조회할 수 있게 했다.
- `local-ai assistant-messages <session_id> --limit 50 --offset 0` CLI 명령을 추가했다.
- `/project/status` 차수를 10차 Assistant message paging 완료, 11차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `68 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant action preview

- `POST /assistant/action-preview`를 추가해 UI가 메시지 전송 전 intent, 추천 endpoint, 위험도, 필요한 입력값을 preview할 수 있게 했다.
- 이 endpoint는 DB 저장, Ollama 호출, Chroma 검색, shell 실행, browser interaction을 수행하지 않는다.
- `local-ai assistant-action-preview "브라우저 열어줘" --project-root /Users/juyoung/local-ai-server` CLI 명령을 추가했다.
- `/project/status` 차수를 11차 Assistant action preview 완료, 12차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `70 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant UI contract

- `GET /assistant/ui-contract`를 추가해 UI 시작 순서, 메시지 흐름, 응답 타입, 차단 기능, 인증 header 계약을 한 번에 조회할 수 있게 했다.
- 이 endpoint는 read-only 계약 요약이며 실제 실행 기능을 활성화하지 않는다.
- `local-ai assistant-ui-contract` CLI 명령을 추가했다.
- `/project/status` 차수를 12차 Assistant UI contract 완료, 13차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_assistant_api.py tests/test_cli.py tests/test_security.py tests/test_api_contracts.py` 결과는 `72 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `148 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`와 `scripts/public_release_check.py --root . --json`도 성공했다.

### Assistant startup snapshot

- `GET /assistant/startup`를 추가해 UI 첫 로딩에 필요한 `ping`, `config`, `dashboard`, `ui_contract`를 read-only snapshot으로 한 번에 조회할 수 있게 했다.
- `/assistant/ui-contract`의 `startup_sequence`를 `/assistant/startup` 우선 흐름으로 정리하고, 개별 조회 endpoint는 `refresh_endpoints`로 분리했다.
- `docs/UI_BRIDGE_EXAMPLES.md`를 추가해 startup, ui-contract, assistant message 예시 payload를 안전한 placeholder로 문서화했다.
- `docs/UI_BRIDGE_EXAMPLES.md`에 `/assistant/message` 응답 타입별 예시를 추가했다.
- `docs/UI_QA_CHECKLIST.md`를 추가해 실제 브라우저 조작 없이 확인할 수 있는 수동 QA 기준과 stop condition을 문서화했다.
- README에 브라우저 UI를 붙이는 기본 순서 `startup -> bootstrap -> action-preview -> message -> messages paging`를 추가했다.
- README/API/PROJECT_SUMMARY 핵심 endpoint, CLI, 공개 문서 링크가 서로 맞는지 확인하는 public docs contract 테스트를 추가했다.
- `docs/RELEASE_CHECKLIST.md`를 추가해 GitHub 공개 전 코드, 문서, 보안, 실행 경계, stop condition을 한 곳에서 확인할 수 있게 했다.
- 이 endpoint는 상태/계약 조회만 수행하며 shell 실행, 파일 수정/삭제, 브라우저 조작을 활성화하지 않는다.
- `local-ai assistant-startup` CLI 명령을 추가했다.
- `/project/status` 차수를 13차 Assistant startup snapshot 완료, 14차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `5 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `164 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Next chat handoff safety polish

- `docs/NEXT_CHAT_HANDOFF.md`의 다음 작업을 실제 브라우저 조작으로 오해되지 않도록 API 계약/문서 QA 보강 중심으로 수정했다.
- Codex가 바로 할 수 있는 안전 작업과 사용자 수동 확인 또는 별도 승인 후에만 진행할 작업을 분리했다.
- `tests/test_next_chat_handoff.py`를 추가해 handoff 문서가 브라우저 조작 없이 진행하는 안전 작업, 최신 검증 gate, UI/release 문서 링크를 유지하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_public_docs_contract.py tests/test_ui_qa_checklist.py tests/test_readme_ui_bridge.py` 결과는 `11 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `167 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Assistant/project docs contract polish

- README `Continuation Status` 섹션에 `GET /project/status`, `GET /project/next`, `GET /project/shell-policy`, `POST /project/shell-dry-run` endpoint와 CLI 대응을 명시했다.
- `tests/test_public_docs_contract.py`를 확장해 assistant endpoint 전체, assistant CLI 전체, project continuation endpoint/CLI가 README, API 문서, PROJECT_SUMMARY에 모두 포함되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `8 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `168 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### UI bridge schema example validation

- `docs/UI_BRIDGE_EXAMPLES.md`의 `/assistant/ui-contract` 예시에 `message_flow`, `safety`, `notes`를 추가했다.
- `docs/UI_BRIDGE_EXAMPLES.md`의 `/assistant/startup` 예시에 `ui_contract`와 top-level `safety`를 추가해 실제 `AssistantStartupResponse` schema와 맞췄다.
- `tests/test_ui_bridge_examples.py`를 확장해 UI bridge 예시 JSON이 `AssistantUiContractResponse`, `AssistantStartupResponse`, `AssistantMessageRequest`, `AssistantMessageResponse`로 validate되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py` 결과는 `4 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `169 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### API docs payload schema validation

- `tests/test_api_docs_payloads.py`를 추가해 `docs/API.md`의 curl `-d` JSON payload 예시를 추출하고 실제 request schema로 validate한다.
- 검증 대상은 assistant, ask, ask-with-docs, folder index preview/index, search, feedback, agent plan, project shell dry-run request payload다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py` 결과는 `1 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `172 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Security docs contract validation

- `tests/test_security_docs_contract.py`를 추가해 README와 SECURITY의 보호 endpoint 목록이 같은지 검증한다.
- README, SECURITY, RELEASE_CHECKLIST가 외부 LLM API, shell 실행, browser interaction, 파일 생성/수정/삭제, 운영 배포, cloud/Oracle stop condition을 공유하는지 검증한다.
- RELEASE_CHECKLIST에 `LOCAL_API_KEY=` 형태의 secret-like 예시가 들어가지 않는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_security_docs_contract.py` 결과는 `3 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `174 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Portfolio docs polish

- README에 `포트폴리오 포인트` 섹션을 추가해 담당 범위, 학습 포인트, 안전 설계, 문서 품질 관리를 명시했다.
- `docs/PROJECT_SUMMARY.md`에도 포트폴리오 관점의 담당 범위, 설계 포인트, 안정성 포인트, 검증 포인트, 한계 명시를 추가했다.
- `tests/test_portfolio_docs_contract.py`를 추가해 포트폴리오 설명이 빠지거나 배포 완료처럼 과장되지 않도록 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py` 결과는 `2 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `174 passed, 1 warning`이고, `.venv/bin/python -m compileall app cli scripts`, `.venv/bin/python scripts/public_release_check.py --root . --json`, `git diff --check`도 성공했다.

### Public release summary polish

- `docs/PUBLIC_RELEASE_SUMMARY.md`를 추가해 GitHub/포트폴리오 공개 시 현재 공개 가능 범위, 비공개 로컬 데이터, 검증 명령, 명확한 한계를 한 곳에서 확인할 수 있게 했다.
- README, `docs/PROJECT_SUMMARY.md`, `docs/NEXT_CHAT_HANDOFF.md`에서 공개 상태 요약 문서를 참조하도록 연결했다.
- `tests/test_public_release_summary.py`를 추가해 공개 요약 문서가 local-only/Ollama-only 경계, private data 제외, 검증 명령, 미구현 위험 기능을 계속 명시하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py` 결과는 `13 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `176 passed, 1 warning`이다.

### Project API inventory

- `GET /project/api-inventory`를 추가해 현재 FastAPI endpoint 목록, HTTP method, tag, API key 보호 여부를 read-only로 조회할 수 있게 했다.
- `local-ai api-inventory`와 assistant REPL `/api-inventory`를 추가해 CLI와 세션 안에서도 같은 정보를 확인할 수 있게 했다.
- `/project/status` 차수를 14차 Project API inventory 완료, 15차 Live browser UI QA 다음 단계로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_contracts.py tests/test_cli.py tests/test_security.py tests/test_public_docs_contract.py` 결과는 `72 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `178 passed, 1 warning`이다.

### Assistant bridge smoke test

- `scripts/smoke_test_api.py --assistant-bridge-only` 옵션을 추가해 브라우저 조작 없이 assistant startup, project api inventory, bootstrap, action preview, status message, sessions, messages API 흐름을 확인할 수 있게 했다.
- 이 smoke flow는 업로드/RAG/Ollama 답변 생성을 피하지만 `/assistant/message` 확인 때문에 SQLite에 assistant session/message 기록은 추가한다.
- `tests/test_smoke_script.py`를 확장해 문서/RAG smoke와 assistant bridge smoke의 API 호출 순서를 mock으로 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py` 결과는 `15 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `179 passed, 1 warning`이다.

### Local CI check script

- `scripts/local_ci_check.py`를 추가해 `pytest`, `compileall`, public release check, `git diff --check`를 순서대로 실행하는 로컬 검증 진입점을 제공했다.
- 실패가 발생하면 해당 단계에서 중단하고, 시스템 의존성 설치, 운영 배포, 외부 API 활성화는 수행하지 않는다.
- `tests/test_local_ci_check.py`를 추가해 고정 검증 명령 순서와 실패 시 중단 동작을 mock으로 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_local_ci_check.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py` 결과는 `16 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `182 passed, 1 warning`이다.

### Operations runbook

- `docs/OPERATIONS.md`에 로컬 운영 Runbook을 추가해 정적 검증, 서버 시작, assistant bridge smoke, 문서/RAG smoke, 점검 결과 정리 순서를 명확히 했다.
- Runbook은 브라우저 클릭/입력/전송 자동화, shell 실제 실행, 파일 생성/수정/삭제 자동화, 운영 배포를 포함하지 않는다.
- `tests/test_operations_runbook.py`를 추가해 runbook 명령 순서와 위험 작업 제외 문구가 유지되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_operations_runbook.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `13 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `184 passed, 1 warning`이다.

### README quick start polish

- README 상단에 `Quick Start`, `Verification`, `Safe Boundaries`, `Key Docs`를 추가해 첫 진입자가 실행 방법, 검증 명령, 안전 경계를 바로 확인할 수 있게 했다.
- 기존 README 앞부분의 흩어진 문서 링크를 `Key Docs` 목록으로 정리했다.
- `tests/test_readme_quick_start.py`를 추가해 README 상단 onboarding 섹션, 핵심 명령, 안전 경계, 공개 문서 링크가 유지되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `189 passed, 1 warning`이다.

### UI bridge API inventory docs

- `docs/UI_BRIDGE_EXAMPLES.md`에 read-only `GET /project/api-inventory` 예시를 추가해 UI 개발자가 현재 route 목록, method, tag, API key 보호 여부를 확인할 수 있게 했다.
- `docs/UI_QA_CHECKLIST.md`에 API inventory 확인 항목과 수동 curl 예시를 추가했다.
- `tests/test_ui_bridge_examples.py`, `tests/test_ui_qa_checklist.py`를 보강해 UI bridge 문서가 `/project/api-inventory`를 계속 포함하도록 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py tests/test_ui_qa_checklist.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `17 passed, 1 warning`이다.

### UI connect guide

- `docs/UI_CONNECT_GUIDE.md`를 추가해 별도 로컬 UI가 입력해야 할 API base URL, API key header, project root, startup 호출 순서, 안전 상태, troubleshooting을 한 곳에 정리했다.
- `docs/UI_CONNECT_GUIDE.md`에 copy-ready 환경값 블록과 browser `fetch` 예시를 추가해 UI 코드에서 바로 연결 흐름을 가져갈 수 있게 했다.
- README `Key Docs`와 handoff 문서에서 UI 연결 가이드를 참조하도록 연결했다.
- `tests/test_ui_connect_guide.py`를 추가해 연결값, startup flow, 안전 경계가 문서에 유지되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `15 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `193 passed, 1 warning`이다.

### UI contract cheatsheet

- `docs/UI_CONTRACT_CHEATSHEET.md`를 추가해 UI가 endpoint별로 읽어야 할 핵심 응답 필드, message response type 매핑, safety/error 표시 규칙을 얇게 정리했다.
- README `Key Docs`, handoff, PROJECT_SUMMARY에서 UI field cheatsheet를 참조하도록 연결했다.
- `tests/test_ui_contract_cheatsheet.py`를 추가해 endpoint, response type, safety/error 계약이 문서에 유지되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_contract_cheatsheet.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py tests/test_readme_quick_start.py` 결과는 `19 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `196 passed, 1 warning`이다.

### UI smoke preflight docs

- 현재 세션에서 `127.0.0.1:8000`은 응답 중이었지만 `/assistant/startup`이 `404`를 반환해 assistant bridge smoke test는 실행하지 않았다.
- `scripts/smoke_test_api.py --assistant-bridge-preflight`를 추가해 `/health`, `/assistant/startup`, `/project/api-inventory`를 read-only로 점검하고 다른 서버가 base URL을 사용 중인 상황을 명확히 표시한다.
- `docs/UI_QA_CHECKLIST.md`에 backend identity preflight를 추가해 `/health` 성공만으로 같은 서버라고 판단하지 않고 `/assistant/startup`, `/project/api-inventory`까지 확인하도록 했다.
- `docs/UI_CONNECT_GUIDE.md` troubleshooting에 `/health`는 성공하지만 `/assistant/startup`이 `404`인 경우 다른 서버가 `127.0.0.1:8000`을 사용 중일 수 있다고 명시하고, `8010` 대체 포트 검증 예시를 추가했다.
- `tests/test_ui_qa_checklist.py`, `tests/test_ui_connect_guide.py`를 보강해 assistant bridge smoke command와 포트 점유 경고가 유지되는지 검증한다.
- `tests/test_smoke_script.py`를 보강해 preflight 성공과 wrong-server 감지를 mock 기반으로 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_ui_qa_checklist.py tests/test_ui_connect_guide.py` 결과는 `10 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `198 passed, 1 warning`이다.

### Assistant bridge smoke bugfix

- 실제 `127.0.0.1:8010` 임시 서버에서 assistant bridge preflight와 smoke를 실행했다.
- 서버는 임시 로컬 API key와 `/tmp` SQLite/Chroma/uploads 경로, `AGENT_ALLOWED_ROOTS=/Users/juyoung/local-ai-server`로 실행했다. 실제 secret 값은 문서에 기록하지 않았다.
- `GET /assistant/sessions`에서 마지막 메시지 preview helper 누락으로 `500`이 발생하던 문제를 수정했다.
- `scripts/smoke_test_api.py --assistant-bridge-only`가 `mode=auto`와 상태 질문으로 status intent를 확인하도록 계약을 맞췄다.
- `tests/test_assistant_service.py`를 추가해 실제 service `list_sessions`가 `last_message_preview`를 반환하는지 검증한다.
- 실제 smoke 결과:
  - `--assistant-bridge-preflight`: `ok=true`
  - `--assistant-bridge-only --project-root /Users/juyoung/local-ai-server`: `ok=true`, `endpoints_count=49`, `protected_endpoints_count=34`, `sessions_count=1`, `total_messages=2`
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_assistant_service.py` 결과는 `5 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `199 passed, 1 warning`이다.

### UI connect guide mode contract

- `docs/UI_CONNECT_GUIDE.md`의 `/assistant/message` curl 예시를 실제 `AssistantMode` schema에 맞춰 `mode=auto`로 수정했다.
- 상태 질문은 `mode=auto`에서 status intent로 분기하므로 별도 `mode=status` 요청값을 사용하지 않는다.
- `tests/test_ui_connect_guide.py`에 `mode=auto` 예시 유지와 `mode=status` 예시 금지 검증을 추가했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_readme_quick_start.py tests/test_public_docs_contract.py` 결과는 `17 passed, 1 warning`이다.

### UI contract cheatsheet session fields

- `docs/UI_CONTRACT_CHEATSHEET.md`의 `GET /assistant/sessions` 표시 필드를 실제 `AssistantSessionListResponse`에 맞춰 `sessions`, `limit`, `offset`, `sessions[].messages_count`, `sessions[].last_message_preview`로 수정했다.
- `GET /assistant/sessions/{session_id}/messages` 표시 필드를 실제 `AssistantMessageListResponse`에 맞춰 `total_messages`로 수정했다.
- `tests/test_ui_contract_cheatsheet.py`가 실제 assistant session/message list schema 필드명과 cheatsheet 문구를 함께 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_contract_cheatsheet.py tests/test_ui_bridge_examples.py tests/test_public_docs_contract.py` 결과는 `16 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `200 passed, 1 warning`이다.

### UI bridge API inventory fields

- `docs/UI_BRIDGE_EXAMPLES.md`의 `GET /project/api-inventory` 예시를 실제 런타임 응답 필드인 `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count`, `endpoints[].requires_api_key` 기준으로 수정했다.
- `docs/UI_CONTRACT_CHEATSHEET.md`도 `routes[].protected` 대신 `endpoints[].requires_api_key`를 보도록 수정했다.
- `tests/test_ui_bridge_examples.py`에 `build_api_inventory(app.routes)`와 예시 JSON의 핵심 필드명이 일치하는지 검증하는 테스트를 추가했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py tests/test_ui_qa_checklist.py tests/test_public_docs_contract.py` 결과는 `19 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `201 passed, 1 warning`이다.

### UI smoke summary fields

- `docs/UI_QA_CHECKLIST.md`의 API inventory 확인 항목을 실제 응답 필드인 `endpoints`, `requires_api_key`, `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count` 기준으로 수정했다.
- assistant bridge smoke 확인 항목에 `sessions_count`, `total_messages`, `response_type=status`를 명시했다.
- `docs/NEXT_CHAT_HANDOFF.md`의 assistant bridge smoke 흐름을 `message(auto/status intent)`로 갱신했다.
- `tests/test_smoke_script.py`가 assistant bridge smoke 요약 출력의 `endpoints_count`, `protected_endpoints_count`, `sessions_count`, `total_messages`를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_ui_qa_checklist.py tests/test_next_chat_handoff.py` 결과는 `9 passed, 1 warning`이다.

### Public capability boundary matrix

- README 상단에 `Capability Boundary Matrix`를 추가해 가능한 기능, 조건부 read-only 기능, 금지 기능을 한눈에 구분했다.
- `docs/PROJECT_SUMMARY.md`에 `실행 가능 기능과 금지 기능` 표를 추가해 포트폴리오 설명에서 Agent 기능을 과대해석하지 않도록 정리했다.
- `Agent execution v1`은 기본 차단이며, 활성화해도 허용 root 폴더 목록 조회, 텍스트 preview, 명시 URL 단건 read-only fetch만 지원한다고 명시했다.
- shell은 dry-run only, 브라우저 클릭/입력, 폴더 UI 열기, 파일 생성/수정/삭제, 운영 배포, 외부 LLM API/cloud vector DB는 금지 또는 범위 밖으로 명시했다.
- `tests/test_readme_quick_start.py`, `tests/test_portfolio_docs_contract.py`를 보강해 공개 문서의 safe boundary matrix가 유지되도록 했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py tests/test_public_release_summary.py` 결과는 `17 passed, 1 warning`이다.

### Public release final self-check wording

- `docs/PUBLIC_RELEASE_SUMMARY.md`에 `기능 경계 요약` 표를 추가해 공개 가능한 기능, 조건부 read-only 기능, 금지 기능을 구분했다.
- `docs/RELEASE_CHECKLIST.md` 실행 경계에 Agent execution v1의 조건부 read-only 범위와 폴더 UI 열기 미지원 항목을 추가했다.
- `tests/test_public_release_summary.py`를 보강해 공개 요약과 릴리즈 체크리스트가 기능 경계 self-check 문구를 계속 포함하도록 했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_security_docs_contract.py tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py` 결과는 `16 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `202 passed, 1 warning`이다.

### Public markdown link self-check

- `tests/test_public_docs_contract.py`에 공개 Markdown 문서의 상대 링크가 실제 파일로 해석되는지 검증하는 테스트를 추가했다.
- README 루트 기준 링크와 `docs/*.md` 내부 상대 링크를 각각 source file 기준으로 해석한다.
- external URL, mailto, page anchor는 파일 존재 검증 대상에서 제외한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_public_release_summary.py` 결과는 `17 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `203 passed, 1 warning`이다.

### FastAPI route and Typer command documentation self-check

- README에 실제 FastAPI endpoint 전체를 그룹별로 볼 수 있는 `API endpoint inventory` 섹션을 추가했다.
- `tests/test_public_docs_contract.py`가 `app.main.app.routes`에서 실제 FastAPI endpoint 목록을 읽어 README, `docs/API.md`, `docs/PROJECT_SUMMARY.md`에 모두 문서화되어 있는지 검증하도록 보강했다.
- 같은 테스트 파일에서 Typer command 목록을 실제 `cli.main.app`에서 읽어 README, `docs/API.md`, `docs/PROJECT_SUMMARY.md`에 모두 문서화되어 있는지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `11 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `205 passed, 1 warning`이다.

### Protected endpoint runtime documentation self-check

- `tests/test_security_docs_contract.py`가 `build_api_inventory(app.routes)`의 `requires_api_key=true` 목록을 기준으로 README, `SECURITY.md`, `docs/API.md`의 보호 endpoint 목록이 모두 일치하는지 검증하도록 보강했다.
- 보호 endpoint parser는 `GET`, `POST`, `PUT`, `PATCH`, `DELETE`로 시작하는 bullet만 endpoint로 인정해 일반 필드 목록과 혼동하지 않게 했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_security_docs_contract.py tests/test_security.py tests/test_public_docs_contract.py` 결과는 `52 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `206 passed, 1 warning`이다.

### API response schema documentation self-check

- `tests/test_api_docs_payloads.py`가 `docs/API.md`의 `응답 핵심 필드` 목록을 실제 FastAPI `response_model`의 Pydantic field와 대조하도록 보강했다.
- `cards.documents`, `actions[].tool`, `status=planned` 같은 문서 표현은 최상위 response field로 정규화해 검증한다.
- response model이 없는 read-only project metadata endpoint는 schema field 대조에서 제외한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py` 결과는 `2 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `207 passed, 1 warning`이다.

### CLI HTTP route matrix self-check

- `tests/test_cli.py`에 직접 HTTP backend를 호출하는 CLI 명령의 method/path matrix를 추가했다.
- `local-ai health`, `doctor`, `ask`, `ask-docs`, `search`, documents, assistant bridge, project, agent 명령이 기대한 FastAPI endpoint를 호출하는지 한 번에 검증한다.
- REPL 명령과 로컬 파일 export처럼 backend HTTP 호출이 아닌 명령은 기존 별도 테스트와 기능 범위에 맡긴다.
- targeted self-check에서 `.venv/bin/pytest tests/test_cli.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `208 passed, 1 warning`이다.

### Local CI docs command self-check

- README와 `docs/OPERATIONS.md`에 `scripts/local_ci_check.py` 내부 실행 단계인 `python -m pytest`, `python -m compileall app cli scripts`, `python scripts/public_release_check.py --root . --json`, `git diff --check`를 명시했다.
- `tests/test_operations_runbook.py`가 `scripts.local_ci_check.build_check_commands()`의 실제 단계 이름을 기준으로 README, `docs/OPERATIONS.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 검증 명령 문구를 대조하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_operations_runbook.py tests/test_local_ci_check.py tests/test_readme_quick_start.py` 결과는 `11 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 당시 내부 `pytest` 결과는 `209 passed, 1 warning`이다.

### Smoke flow documentation self-check

- `scripts/smoke_test_api.py`에 document/RAG smoke, assistant bridge preflight, assistant bridge smoke 순서를 상수로 분리했다.
- `tests/test_smoke_script.py`가 실제 smoke flow 상수와 README, `docs/OPERATIONS.md`의 smoke 설명이 일치하는지 검증하도록 보강했다.
- `docs/OPERATIONS.md`의 문서/RAG smoke 설명에 `health → upload → search → ask-with-docs → feedback → stats` 순서를 명시했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_operations_runbook.py tests/test_readme_quick_start.py` 결과는 `13 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `210 passed, 1 warning`이다.

### Public release private data self-check

- `scripts/public_release_check.py`에 GitHub 공개 제외 대상인 로컬 private data 목록을 `PUBLIC_RELEASE_PRIVATE_DATA`로 분리했다.
- `tests/test_public_release_check.py`가 `.env`, SQLite DB/WAL, Chroma index, uploads, logs, JSONL export 예시를 모두 high finding으로 감지하는지 검증하도록 보강했다.
- 같은 테스트가 `PUBLIC_RELEASE_PRIVATE_DATA` 기준으로 `.gitignore`, `docs/RELEASE_CHECKLIST.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`의 제외 경로 문서화가 일치하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_check.py tests/test_public_release_summary.py tests/test_security_docs_contract.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `218 passed, 1 warning`이다.

### Local assistant quick flow self-check

- README 상단에 `Local Assistant Quick Flow`를 추가해 `local-ai doctor → index-preview → index → ask-docs → assistant` 순서로 내 문서/내 폴더 기준 로컬 비서를 바로 확인할 수 있게 했다.
- `local-ai assistant` 안에서 자주 쓰는 `/search JWT`, `/docs`, `/status`, `/next`, `/summary` 명령과 위험 작업이 preview/dry-run에 머문다는 경계를 함께 명시했다.
- `tests/test_readme_quick_start.py`가 quick flow 섹션의 위치와 핵심 명령/안전 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py` 결과는 `19 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `219 passed, 1 warning`이다.

### CLI assistant help documentation self-check

- `cli/main.py`의 assistant/agent REPL 도움말을 각각 `ASSISTANT_REPL_HELP_LINES`, `AGENT_REPL_HELP_LINES` 상수로 분리했다.
- README의 `local-ai assistant` 명령 목록에 실제 도움말에 있던 `/api-inventory`, `/capabilities`, `/root <project_root>` 누락을 반영했다.
- `tests/test_readme_quick_start.py`가 `ASSISTANT_REPL_HELP_LINES` 기준으로 README의 assistant REPL 명령 목록이 빠짐없이 문서화되는지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `36 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `220 passed, 1 warning`이다.

### API section order self-check

- `docs/API.md`에서 빈 `## Ask` 섹션이 `## Assistant` 앞에 보이던 흐름을 정리하고, 실제 `/ask`, `/ask-with-docs` 설명이 `## Ask` 아래에 오도록 수정했다.
- `tests/test_api_docs_payloads.py`가 top-level API 섹션 순서와 `Ask` 섹션의 endpoint 배치를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_public_docs_contract.py tests/test_api_contracts.py` 결과는 `24 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `221 passed, 1 warning`이다.

### Public limitation boundary self-check

- `tests/test_portfolio_docs_contract.py`가 README, `docs/PROJECT_SUMMARY.md`, `SECURITY.md`의 현재 한계/금지 기능 핵심 표현을 함께 검증하도록 보강했다.
- 교차 검증 항목은 외부 LLM API, cloud vector DB, 브라우저 클릭, 파일 수정, shell 실행, 운영 배포, Oracle, OCR, HTTPS, rate limit, 다중 사용자 한계다.
- README와 `docs/PROJECT_SUMMARY.md`에는 `배포 완료` 같은 과장 표현이 없는지도 함께 검증한다. `SECURITY.md`의 공개 전 체크리스트 문구는 예외로 둔다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py tests/test_security_docs_contract.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `222 passed, 1 warning`이다.

### Verification storage impact self-check

- README 상단 `Verification` 섹션에 local CI, assistant bridge smoke, document/RAG smoke의 서버 필요 여부, Ollama 필요 여부, 저장 영향을 표로 추가했다.
- `docs/OPERATIONS.md`의 로컬 운영 Runbook에도 같은 저장 영향 요약을 추가했다.
- `tests/test_readme_quick_start.py`와 `tests/test_operations_runbook.py`가 smoke 명령의 read-only 여부와 SQLite/Chroma/uploads 저장 영향 설명을 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_operations_runbook.py tests/test_public_docs_contract.py` 결과는 `23 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `224 passed, 1 warning`이다.

### README highlights self-check

- README 첫 화면에 `Highlights` 섹션을 추가해 로컬 Ollama, 문서 기반 RAG, SQLite source of truth, Chroma vector search, Typer/FastAPI 재사용, preview/dry-run/approval/read-only 안전 경계를 압축해서 보여준다.
- `tests/test_readme_quick_start.py`가 Highlights 섹션의 핵심 프로젝트 요약 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py` 결과는 `23 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `225 passed, 1 warning`이다.

### Runtime docs inventory self-check

- `tests/test_public_docs_contract.py`가 FastAPI runtime API inventory의 모든 endpoint가 `docs/API.md`에 문서화되어 있는지 검증하도록 보강했다.
- 같은 테스트가 Typer runtime CLI command 전체가 README와 `docs/API.md`에 빠짐없이 노출되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_api_docs_payloads.py tests/test_readme_quick_start.py` 결과는 `25 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `227 passed, 1 warning`이다.

### UI contract refresh endpoint self-check

- `/assistant/ui-contract` 실제 service 응답의 refresh endpoint에 read-only `GET /project/api-inventory`를 포함해 UI bridge 예시와 맞췄다.
- `tests/test_ui_bridge_examples.py`가 UI contract 예시의 response type, refresh endpoint, blocked action 목록이 실제 `AssistantService().ui_contract()`와 같은지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py tests/test_assistant_api.py tests/test_ui_contract_cheatsheet.py tests/test_smoke_script.py` 결과는 `27 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `228 passed, 1 warning`이다.

### UI QA checklist contract self-check

- `docs/UI_QA_CHECKLIST.md`에 `GET /assistant/ui-contract` 수동 QA 섹션을 추가해 startup sequence, refresh endpoint, message flow, response type, blocked action, secret 반환 금지 확인을 명시했다.
- `tests/test_ui_qa_checklist.py`가 UI contract runtime shape에 필요한 endpoint, response type, blocked action 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_qa_checklist.py tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py tests/test_ui_connect_guide.py` 결과는 `17 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `229 passed, 1 warning`이다.

### UI connect response field self-check

- `docs/UI_CONNECT_GUIDE.md`에 `GET /assistant/startup`과 `POST /assistant/bootstrap` 응답에서 UI가 읽어야 할 핵심 필드 표를 추가했다.
- `tests/test_ui_connect_guide.py`가 `AssistantStartupResponse`, `AssistantBootstrapResponse`의 top-level 필드와 주요 nested field 문서화를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_ui_qa_checklist.py tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `230 passed, 1 warning`이다.

### Assistant bridge expected output self-check

- `docs/UI_CONNECT_GUIDE.md`에 `--assistant-bridge-preflight`와 `--assistant-bridge-only` 실행 후 확인할 expected JSON summary field를 표로 추가했다.
- `tests/test_smoke_script.py`가 assistant bridge smoke flow 상수와 expected output 문구가 UI 연결 가이드에 유지되는지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_ui_connect_guide.py tests/test_ui_qa_checklist.py tests/test_operations_runbook.py tests/test_readme_quick_start.py` 결과는 `27 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `231 passed, 1 warning`이다.

### Current limits and next improvements self-check

- README에 `다음 추천 개선` 섹션을 추가해 Codex가 바로 이어서 할 수 있는 안전 개선과 별도 승인/보안 리뷰가 필요한 개선을 분리했다.
- `docs/PROJECT_SUMMARY.md`의 `다음 추천 개선`도 README와 같은 최신 API 상태, UI bridge smoke, preview-only repair, 브라우저/shell/file/deploy 금지 경계로 맞췄다.
- `tests/test_portfolio_docs_contract.py`가 README와 PROJECT_SUMMARY의 다음 개선 경계가 함께 유지되는지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_public_release_summary.py` 결과는 `29 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `232 passed, 1 warning`이다.

### Public release next-improvement boundary self-check

- `docs/PUBLIC_RELEASE_SUMMARY.md`에 공개 후 다음 개선 경계를 추가해 README/PROJECT_SUMMARY와 같은 안전 개선, 승인 필요 개선을 표시했다.
- `docs/RELEASE_CHECKLIST.md`에 공개 후 다음 개선 경계 확인 항목을 추가했다.
- `tests/test_public_release_summary.py`가 RELEASE_CHECKLIST와 PUBLIC_RELEASE_SUMMARY의 다음 개선 경계가 함께 유지되는지 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_security_docs_contract.py` 결과는 `25 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `233 passed, 1 warning`이다.

### Markdown/Text document RAG smoke self-check

- `scripts/smoke_test_api.py`의 문서/RAG smoke가 `smoke-backend-notes.md`와 `smoke-architecture-notes.txt`를 모두 업로드하도록 확장했다.
- smoke summary에 `sample_documents`, 업로드된 문서 목록, 문서 수를 포함해 실제 서버에서 어떤 샘플이 들어갔는지 확인할 수 있게 했다.
- README, `docs/OPERATIONS.md`, `docs/API.md`에 문서/RAG smoke가 `.md`와 `.txt`를 함께 검증한다는 점을 명시했다.
- `tests/test_smoke_script.py`가 Markdown/Text sample 업로드, content type, 문서 안내 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_operations_runbook.py tests/test_readme_quick_start.py tests/test_api_docs_payloads.py` 결과는 `22 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `233 passed, 1 warning`이다.

### Index folder job/status preview schema self-check

- `POST /documents/index-folder-job-preview`를 추가해 대용량 폴더 색인 job/status API의 progress response schema를 preview-only로 확인할 수 있게 했다.
- 이 endpoint는 기존 folder preview 결과를 바탕으로 `job_id=preview-only`, `status=planned`, `would_enqueue=false`, `dry_run=true`, `progress`를 반환하며 queue 생성, SQLite 저장, embedding 생성, Chroma 저장을 수행하지 않는다.
- README, `SECURITY.md`, `docs/API.md`, `docs/PROJECT_SUMMARY.md`의 endpoint 목록과 보호 endpoint 목록을 갱신했다.
- `tests/test_api_contracts.py`, `tests/test_security.py`, `tests/test_api_docs_payloads.py`를 보강해 endpoint response contract, API key 보호, request/response field 문서 계약을 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_contracts.py tests/test_api_docs_payloads.py tests/test_public_docs_contract.py tests/test_security.py tests/test_security_docs_contract.py` 결과는 `69 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `235 passed, 1 warning`이다.

### Vector rebuild preview self-check

- `GET /documents/vector-rebuild-preview`를 추가해 Chroma vector가 누락된 SQLite chunk만 대상으로 재생성 후보를 read-only로 확인할 수 있게 했다.
- `local-ai vector-rebuild-preview` CLI 명령을 추가했다.
- 이 기능은 실제 Ollama embedding 생성, Chroma vector 재생성, DB 수정을 수행하지 않는다.
- README, `docs/API.md`, `docs/PROJECT_SUMMARY.md`, `docs/OPERATIONS.md`, `docs/RELEASE_CHECKLIST.md`에 endpoint와 CLI 명령을 문서화했다.
- `tests/test_repair_preview.py`, `tests/test_document_stats.py`, `tests/test_cli.py`, `tests/test_public_docs_contract.py`를 보강해 service preview, endpoint contract, CLI route, public docs 계약을 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_repair_preview.py tests/test_document_stats.py tests/test_cli.py tests/test_api_docs_payloads.py tests/test_public_docs_contract.py tests/test_operations_runbook.py` 결과는 `44 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `237 passed, 1 warning`이다.

### Assistant bridge latest preview endpoint UI docs self-check

- `docs/UI_QA_CHECKLIST.md`에 `/documents/index-folder-job-preview`와 `/documents/vector-rebuild-preview` 표시 기준을 추가했다.
- `docs/UI_CONNECT_GUIDE.md`의 assistant bridge smoke 기대 출력 아래에 최신 preview endpoint의 UI 표시 기준과 금지 동작을 추가했다.
- `docs/UI_BRIDGE_EXAMPLES.md`의 `GET /project/api-inventory` 예시를 현재 runtime count인 `endpoints_count=51`, `protected_endpoints_count=35`, `public_endpoints_count=16` 기준으로 갱신하고 최신 preview endpoint 예시를 포함했다.
- `docs/UI_CONTRACT_CHEATSHEET.md`에 두 preview endpoint의 UI 목적과 표시 필드를 추가했다.
- `tests/test_ui_qa_checklist.py`, `tests/test_ui_connect_guide.py`, `tests/test_ui_bridge_examples.py`, `tests/test_ui_contract_cheatsheet.py`, `tests/test_smoke_script.py`를 보강해 최신 preview endpoint 문서 계약을 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_qa_checklist.py tests/test_ui_connect_guide.py tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py tests/test_smoke_script.py` 결과는 `24 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `237 passed, 1 warning`이다.

### Next improvement roadmap refresh self-check

- README, `docs/PROJECT_SUMMARY.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`, `docs/RELEASE_CHECKLIST.md`의 다음 개선 목록을 최신 preview endpoint 완료 상태에 맞게 갱신했다.
- 다음 개선은 새 기능 구현처럼 표현하지 않고, endpoint/response field 계약 테스트 확장, runtime endpoint count drift check, 실제 사용자 문서 기반 upload/search/ask-with-docs end-to-end 재검증, sanitized smoke summary 기록, preview-only 계약 기준 queue/rebuild 활성화 조건 문서 유지로 정리했다.
- 위험 작업 경계는 실제 repair/delete/rebuild, 브라우저 click/fill/submit 자동화, 실제 shell 실행, 파일 생성/수정/삭제 자동화, OCR/JavaScript 렌더링/외부 URL 크롤링, 운영 배포/HTTPS termination/다중 사용자 권한/분산 rate limit로 유지했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `237 passed, 1 warning`이다.

### Sanitized smoke summary self-check

- `scripts/smoke_test_api.py`에 `--sanitized-summary` 옵션과 `build_sanitized_smoke_summary()`를 추가했다.
- sanitized smoke summary는 `safe_to_paste=true`, `mode`, step별 status/count, sample document 이름, `excluded_fields`를 남기고 질문/답변 원문, request id, header, 로컬 project root, stored path를 제외한다.
- README, `docs/API.md`, `docs/OPERATIONS.md`, `docs/RELEASE_CHECKLIST.md`에 작업 기록용 paste-safe smoke 결과 생성 방법을 추가했다.
- `tests/test_smoke_script.py`를 보강해 document/RAG smoke와 assistant bridge smoke의 sanitized summary가 secret, request id, document id, local project root를 출력하지 않는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_operations_runbook.py tests/test_readme_quick_start.py tests/test_api_docs_payloads.py tests/test_public_release_summary.py` 결과는 `29 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `240 passed, 1 warning`이다.

### Runtime endpoint count drift check self-check

- `tests/test_ui_bridge_examples.py`가 `docs/UI_BRIDGE_EXAMPLES.md`의 `GET /project/api-inventory` 예시 count와 실제 `build_api_inventory(app.routes)`의 `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count`를 비교하도록 보강했다.
- `docs/UI_BRIDGE_EXAMPLES.md`와 `docs/API.md`에 runtime endpoint count drift check 기준을 명시했다.
- README, `docs/PROJECT_SUMMARY.md`, `docs/PUBLIC_RELEASE_SUMMARY.md`, `docs/RELEASE_CHECKLIST.md`의 다음 개선 문구를 "확장"에서 "유지"로 바꿔 이미 반영된 상태와 맞췄다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_api_docs_payloads.py tests/test_readme_quick_start.py` 결과는 `26 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `240 passed, 1 warning`이다.

### Release checklist final-pass contract self-check

- `docs/RELEASE_CHECKLIST.md`에 sanitized smoke summary 계약, runtime endpoint count drift check, public/security docs contract를 최종 공개 전 회귀 기준으로 추가했다.
- 최종 공개 판단 섹션을 추가해 공개 범위가 로컬 백엔드 API, CLI, 문서, 테스트 코드로 한정되고 실제 `.env`, SQLite DB, Chroma index, 업로드 문서, 로그, SFT JSONL은 공개하지 않는다는 점을 명시했다.
- release checklist final pass 후에도 실제 배포, repair/delete/rebuild, browser interaction, shell/file 자동 실행을 진행하지 않는다고 명시했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_public_release_summary.py tests/test_security_docs_contract.py tests/test_smoke_script.py tests/test_ui_bridge_examples.py` 결과는 `36 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `240 passed, 1 warning`이다.

### README public status snapshot self-check

- README 상단에 `Current Status Snapshot`을 추가해 구현됨, preview-only, 하지 않음 상태를 첫 화면에서 구분했다.
- 로컬 API 서버, 문서 기반 RAG, CLI 로컬 비서는 구현됨으로 표시하고 Agent 실행 엔진은 preview-only, 운영 배포/브라우저 조작/파일 자동 수정/삭제/외부 LLM API 연결은 하지 않음으로 표시했다.
- `tests/test_readme_quick_start.py`가 README 첫 화면의 상태 구분 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py tests/test_public_release_summary.py` 결과는 `31 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `241 passed, 1 warning`이다.

### Public docs link-set self-check

- `tests/test_public_docs_contract.py`의 `PUBLIC_DOC_LINKS`에 `docs/OPERATIONS.md`를 추가해 README/PROJECT_SUMMARY가 참조하는 공개 문서 링크 세트와 테스트 기준을 맞췄다.
- 기존 markdown link resolver가 README, SECURITY, API, PROJECT_SUMMARY, OPERATIONS, RELEASE_CHECKLIST, PUBLIC_RELEASE_SUMMARY, UI 문서, handoff/worklog 내부 링크가 실제 파일로 resolve되는지 계속 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_operations_runbook.py` 결과는 `27 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `241 passed, 1 warning`이다.

### Public release status snapshot self-check

- `docs/PUBLIC_RELEASE_SUMMARY.md`에 README와 같은 공개용 상태 스냅샷을 추가해 구현됨, preview-only, 하지 않음 상태를 구분했다.
- `tests/test_public_release_summary.py`가 로컬 API 서버, 문서 기반 RAG, CLI 로컬 비서, Agent 실행 엔진, 배포/외부 자동화 상태 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_readme_quick_start.py tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py` 결과는 `32 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `242 passed, 1 warning`이다.

### Final report self-check

- `docs/FINAL_REPORT.md`를 추가해 무엇을 만들었는지, endpoint 목록, CLI 명령어 목록, 서버 실행 방법, 테스트 실행 방법, 현재 한계, 다음 추천 개선 사항을 한 문서에 정리했다.
- README `Key Docs`와 public docs link contract에 `docs/FINAL_REPORT.md`를 추가했다.
- `tests/test_portfolio_docs_contract.py`가 `docs/FINAL_REPORT.md`의 최종 보고 섹션, 주요 endpoint/CLI/검증 명령, 현재 한계, 다음 개선, 과장 금지 문구를 검증하도록 보강했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_public_release_summary.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `243 passed, 1 warning`, public release check는 `scanned_files=111`, finding 없음이다.

### Assistant UI contract inventory guard

- `tests/test_api_contracts.py`에 `/assistant/ui-contract`의 `startup_sequence`, `refresh_endpoints`, `message_flow`가 실제 `/project/api-inventory` route 목록과 일치하는지 검증하는 테스트를 추가했다.
- assistant endpoint는 API inventory에서 `requires_api_key=true`, read-only `/project/api-inventory`는 `requires_api_key=false`로 유지되는지 함께 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_contracts.py tests/test_ui_bridge_examples.py tests/test_ui_qa_checklist.py` 결과는 `21 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `244 passed, 1 warning`, public release check는 finding 없음이다.

### Safe task board

- `docs/TASKS.md`를 추가해 완료된 핵심 작업, Codex가 바로 할 수 있는 안전 작업, 사용자 수동 확인 작업, 보안 리뷰/승인이 필요한 작업, stop condition을 한 파일에 정리했다.
- README `Key Docs`와 `docs/PROJECT_SUMMARY.md` 관련 문서 목록에 `docs/TASKS.md`를 연결했다.
- `tests/test_tasks_doc.py`를 추가해 task board가 safe-next/manual-check/review-required 경계를 유지하고 공개 문서에서 링크되는지 검증한다.
- `tests/test_public_docs_contract.py`의 공개 문서 링크/markdown 링크 검사 대상에도 `docs/TASKS.md`를 포함했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_tasks_doc.py tests/test_public_docs_contract.py` 결과는 `15 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `246 passed, 1 warning`, public release check는 `scanned_files=113`, finding 없음이다.

### Handoff task board link

- `docs/NEXT_CHAT_HANDOFF.md`의 먼저 읽을 파일과 현재 상태에 `docs/TASKS.md`를 추가해 다음 세션이 task board의 safe-next/manual-check/review-required 경계를 먼저 확인하도록 했다.
- `tests/test_next_chat_handoff.py`를 보강해 handoff가 task board와 작업 경계 문구를 계속 포함하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_tasks_doc.py` 결과는 `6 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `247 passed, 1 warning`, public release check는 `scanned_files=113`, finding 없음이다.

### Sanitized smoke summary examples

- `docs/SMOKE_SUMMARY_EXAMPLES.md`를 추가해 document/RAG smoke와 assistant bridge smoke의 paste-safe summary 예시를 기록했다.
- 예시는 `safe_to_paste=true`, `excluded_fields`, step별 status/count만 포함하고 질문/답변 원문, request id, header, API key, 로컬 project root, stored path를 제외한다.
- README `Key Docs`, `docs/PROJECT_SUMMARY.md`, public docs link contract에 `docs/SMOKE_SUMMARY_EXAMPLES.md`를 연결했다.
- `tests/test_smoke_summary_examples.py`를 추가해 예시 JSON이 document-rag와 assistant-bridge mode를 모두 포함하고, secret/local path/prompt/answer/content를 본문에 포함하지 않는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_summary_examples.py tests/test_public_docs_contract.py tests/test_tasks_doc.py` 결과는 `17 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `249 passed, 1 warning`, public release check는 `scanned_files=115`, finding 없음이다.

### Smoke summary runtime count guard

- `tests/test_smoke_summary_examples.py`를 보강해 `docs/SMOKE_SUMMARY_EXAMPLES.md`의 assistant bridge `api-inventory` count가 실제 `build_api_inventory(app.routes)` 결과와 일치하는지 검증한다.
- `docs/TASKS.md`의 runtime endpoint count drift check 항목을 완료 상태로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_summary_examples.py tests/test_tasks_doc.py` 결과는 `5 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `250 passed, 1 warning`, public release check는 `scanned_files=115`, finding 없음이다.

### Preview activation policy

- `docs/PREVIEW_ACTIVATION_POLICY.md`를 추가해 `index-folder-job-preview`, `vector-rebuild-preview`, `repair-preview`의 현재 preview-only 계약과 실제 queue/rebuild/repair 활성화 전 조건을 분리해 문서화했다.
- README `Key Docs`, `docs/PROJECT_SUMMARY.md`, public docs link contract에 `docs/PREVIEW_ACTIVATION_POLICY.md`를 연결했다.
- `docs/TASKS.md`의 preview-only queue/rebuild 계약 유지 항목을 완료 상태로 갱신했다.
- `tests/test_preview_activation_policy.py`를 추가해 preview-only 필드, 활성화 gate, stop condition, 공개 문서 링크를 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_preview_activation_policy.py tests/test_public_docs_contract.py tests/test_tasks_doc.py tests/test_repair_preview.py tests/test_document_stats.py` 결과는 `24 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `253 passed, 1 warning`, public release check는 `scanned_files=117`, finding 없음이다.

### Safe task board completion state

- `docs/TASKS.md`에서 자동 테스트로 이미 유지 중인 안전 항목을 완료 상태로 갱신했다.
- 완료 처리한 항목은 endpoint/response field 계약, runtime endpoint count drift, assistant bridge smoke expected output/UI QA checklist, sanitized smoke summary, preview-only queue/rebuild activation policy, handoff/task boundary 정합성이다.
- 실제 사용자 `.md`/`.txt` 문서 기반 E2E 재검증은 SQLite/Chroma/uploads 저장 영향이 있어 미완료 상태로 유지했다.
- `tests/test_tasks_doc.py`를 보강해 자동화된 safe contract 항목은 완료 상태, 실제 사용자 문서 E2E는 미완료 상태로 유지되는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_tasks_doc.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `20 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `254 passed, 1 warning`, public release check는 `scanned_files=117`, finding 없음이다.

### User document E2E smoke plan

- `docs/USER_DOCUMENT_E2E_PLAN.md`를 추가해 실제 사용자 `.md`/`.txt` 문서 기준 upload/search/ask-with-docs E2E 실행 전 승인 조건, 저장 영향, paste-safe summary 기준, stop condition을 문서화했다.
- 실제 사용자 문서 E2E는 SQLite, Chroma, `data/uploads/`에 테스트 데이터를 추가할 수 있으므로 `docs/TASKS.md`에서는 미완료 상태를 유지했다.
- README `Key Docs`, `docs/PROJECT_SUMMARY.md`, public docs link contract에 `docs/USER_DOCUMENT_E2E_PLAN.md`를 연결했다.
- `tests/test_user_document_e2e_plan.py`를 추가해 승인 조건, 저장 영향, `--sanitized-summary`, secret 미노출, TASKS 미완료 유지 계약을 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_user_document_e2e_plan.py tests/test_public_docs_contract.py tests/test_tasks_doc.py` 결과는 `19 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `257 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.

### Next handoff E2E approval boundary

- `docs/NEXT_CHAT_HANDOFF.md`에 `docs/USER_DOCUMENT_E2E_PLAN.md`를 먼저 읽을 파일과 현재 상태에 추가했다.
- 실제 사용자 문서 E2E는 사용자 승인과 실제 `.md`/`.txt` 경로가 있을 때만 실행하고, 승인 전에는 문서/테스트/API 계약 polish만 진행하도록 handoff 문구를 정리했다.
- `tests/test_next_chat_handoff.py`를 보강해 실제 사용자 문서 E2E가 승인/경로/저장 영향/paste-safe summary 조건을 요구하는지 검증한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_user_document_e2e_plan.py tests/test_public_docs_contract.py` 결과는 `21 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `258 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.

### Approved user document E2E smoke

- `scripts/smoke_test_api.py`에 `--document` 옵션을 추가해 승인된 실제 `.md`/`.txt` 문서로 document/RAG smoke를 실행할 수 있게 했다.
- `--document` 실행의 sanitized summary는 `document_source=user-provided`, `user_documents_count`만 남기고 로컬 경로와 파일명은 제외한다.
- 사용자 승인 후 공개용 프로젝트 문서인 `docs/PROJECT_SUMMARY.md`를 대상으로 `upload → search → ask-with-docs → feedback → stats` E2E를 실행했다.
- 첫 실행은 `LOCAL_API_KEY` header 누락으로 `401 Unauthorized`가 발생했고, 키 값을 출력하지 않은 채 로컬 `.env`를 로드해 재실행했다.
- 실제 E2E 실행은 SQLite, Chroma, `data/uploads/`에 테스트 데이터를 추가했다. 원본 문서는 삭제하거나 수정하지 않았다.
- paste-safe summary:

```json
{
  "ok": true,
  "mode": "document-rag",
  "base_url": "http://127.0.0.1:8000",
  "steps": [
    {"step": "health", "status": 200},
    {"step": "upload", "status": 200, "documents_count": 1, "documents": [{"chunks_created": 11}]},
    {"step": "search", "status": 200, "results_count": 3},
    {"step": "ask-with-docs", "status": 200, "sources_count": 3},
    {"step": "feedback", "status": 200, "feedback_id": 1},
    {"step": "stats", "status": 200, "documents_count": 5, "chunks_count": 36}
  ],
  "safe_to_paste": true,
  "excluded_fields": ["answer", "content", "headers", "note", "project_root", "question", "request_id", "stored_path"],
  "document_source": "user-provided",
  "user_documents_count": 1
}
```

- `docs/TASKS.md`의 실제 사용자 문서 E2E 항목을 완료 상태로 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_user_document_e2e_plan.py tests/test_tasks_doc.py tests/test_next_chat_handoff.py tests/test_portfolio_docs_contract.py tests/test_readme_quick_start.py` 결과는 `37 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `260 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.

### Opus safety polish follow-up

- Agent file dry-run 응답에서 `would_execute=false`를 고정하고, 실제 execute 단계에서 현재 설정상 read-only 후보가 될 수 있는지는 `execute_phase_would_run`으로 분리했다.
- `LOCAL_API_KEY`가 없으면 startup stderr warning을 출력하고, `LOCAL_API_KEY_WARN=false`로 의도적인 local demo 경고를 끌 수 있게 했다.
- Agent read-only web fetch 실행 전 hostname을 IP로 해석해 private, loopback, link-local 주소를 차단하고, redirect 응답은 자동으로 따라가지 않도록 명시 처리했다.
- CORS credential 허용 여부를 `LOCAL_CORS_ALLOW_CREDENTIALS`로 분리하고 기본값을 `false`로 유지했다.
- README, API, OPERATIONS, USER_DOCUMENT_E2E_PLAN, `.env.example`에 host allowlist 미구현, CORS credentials 기본값, SQLite `.backup`, 수동 cleanup 예시를 문서화했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_agent_service.py tests/test_security.py tests/test_config.py tests/test_operations_runbook.py tests/test_readme_quick_start.py tests/test_api_docs_payloads.py tests/test_user_document_e2e_plan.py tests/test_portfolio_docs_contract.py` 결과는 `83 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `266 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.

### Public release next-step wording sync

- `docs/PUBLIC_RELEASE_SUMMARY.md`, `docs/FINAL_REPORT.md`, `docs/RELEASE_CHECKLIST.md`에서 이미 완료된 실제 사용자 문서 E2E를 "남은 재검증"처럼 표현하던 문구를 정리했다.
- 다음 개선 문구는 README/PROJECT_SUMMARY와 맞춰 "승인된 실제 사용자 `.md`/`.txt` 문서 E2E smoke summary가 민감 정보 없이 유지되는지 검증"으로 통일했다.
- `tests/test_public_release_summary.py`도 같은 계약을 검증하도록 갱신했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_readme_quick_start.py tests/test_public_docs_contract.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `266 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.

### 응답 형식 업데이트

- 실제 배포/클라우드/DB migration 작업이 없으면 배포 여부 섹션을 반복하지 않기로 정리함.
- 최종 보고는 `Recommended Next Model` 섹션 중심으로 다음 작업을 이어갈 수 있게 작성함.

### Opus safety polish replay verification

- 2026-05-26 14:58 KST 기준으로 Claude Opus safety polish prompt를 재확인했다.
- 요청 항목은 기존 `371290c Apply Opus safety polish`와 `43f856c Sync public release next steps` 상태에 이미 반영되어 있었다.
- 재확인 범위는 Agent file dry-run `would_execute=false`, `execute_phase_would_run`, `LOCAL_API_KEY_WARN`, private/loopback/link-local web fetch 차단, redirect 자동 follow 비활성화, `LOCAL_CORS_ALLOW_CREDENTIALS`, README/API/OPERATIONS/USER_DOCUMENT_E2E_PLAN 문서 반영이다.
- 추가 위험 기능 활성화는 하지 않았다. 외부 LLM API, shell/browser/file-write 실행 활성화, agent 기본값 변경, 운영 배포, cloud/Oracle 변경, secret 출력, 시스템 패키지 설치는 수행하지 않았다.
- replay self-check에서 `.venv/bin/pytest` 결과는 `266 passed, 1 warning`이다.
- replay local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `266 passed, 1 warning`, public release check는 `scanned_files=119`, finding 없음이다.
- replay whitespace check에서 `git diff --check` 결과는 통과했다.

### PDF OCR fallback implementation

- 2026-05-26 15:19 KST 기준으로 Claude Opus가 P1(go)로 분류한 OCR 범위 중 Stage 3 구현을 완료했다.
- `pyproject.toml`에 `[ocr]` optional extra를 추가했고, `pytesseract`, `Pillow`는 optional dependency로만 둔다.
- `app/services/document_loader.py`에 PDF OCR fallback을 추가했다. 기본 PDF 텍스트 추출이 충분하면 OCR을 호출하지 않고, 텍스트가 비어 있거나 매우 짧은 페이지에서만 PyPDF image XObject OCR을 시도한다.
- `tesseract` binary 또는 OCR Python dependency가 없으면 서버 import와 일반 문서 업로드는 유지하고, OCR 필요한 페이지는 명확한 설치 안내 reason으로 skip한다.
- OCR 이미지는 저장하지 않는다. PIL image 객체는 메모리에서만 사용하고, OCR 결과 텍스트만 기존 chunking, SQLite, Chroma pipeline으로 들어간다.
- `GET /documents/supported-types` 응답에 `pdf_ocr`, `pdf_ocr_install_hint`를 추가했다. `local-ai document-types`는 백엔드 응답을 그대로 출력하므로 별도 로직 중복 없이 OCR 상태를 표시한다.
- README, API, PROJECT_SUMMARY, SECURITY, release docs, TASKS, NEXT_CHAT_HANDOFF를 PDF OCR fallback의 현재 범위와 남은 page rendering 확장 경계에 맞춰 갱신했다.
- 금지 범위는 지켰다. 외부 LLM API, cloud OCR, LangChain, pdf2image/poppler, 시스템 패키지 자동 설치, shell/browser/file-write 실행 활성화, agent 기본값 변경, 운영 배포, cloud/Oracle 변경, secret 출력은 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_document_loader.py tests/test_api_contracts.py tests/test_api_docs_payloads.py tests/test_readme_quick_start.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_tasks_doc.py tests/test_next_chat_handoff.py tests/test_security_docs_contract.py` 결과는 `62 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `271 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `271 passed, 1 warning`, public release check는 `scanned_files=120`, finding 없음이다.
- whitespace check에서 `git diff --check` 결과는 통과했다.

### OCR smoke document type contract

- `scripts/smoke_test_api.py --document`가 승인된 실제 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서를 받을 수 있게 확장했다.
- PDF OCR fallback 검증도 같은 `--document /path/to/approved-scan.pdf --sanitized-summary` 흐름으로 실행할 수 있게 README, API, OPERATIONS, USER_DOCUMENT_E2E_PLAN을 갱신했다.
- 실제 PDF 업로드나 OCR 실행은 수행하지 않았다. SQLite, Chroma, `data/uploads/`에 새 smoke 데이터는 추가하지 않았다.
- sanitized summary는 기존과 같이 사용자 제공 문서의 filename, local path, request id, 질문/답변 원문, header 값을 제외한다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_user_document_e2e_plan.py tests/test_tasks_doc.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `272 passed, 1 warning`이다.

### OCR supported-types polish

- PDF supported type 설명을 현재 구현에 맞춰 `Text-based PDF with optional OCR fallback for PyPDF image XObjects.`로 정리했다.
- optional dependency availability 체크에서 `importlib.util.find_spec` 예외를 `DocumentLoader._module_available`로 흡수하도록 정리했다.
- `pdf_ocr_status()`의 missing dependency와 available 상태를 직접 검증하는 unit test를 추가했다.
- `docs/NEXT_CHAT_HANDOFF.md`에서 `/documents/supported-types`와 `local-ai document-types`가 `pdf_ocr` 준비 상태까지 보여준다고 명시했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_document_loader.py tests/test_api_contracts.py tests/test_next_chat_handoff.py` 결과는 `34 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `274 passed, 1 warning`이다.

### OCR supported-types service contract

- `DocumentService.get_supported_types()`가 loader의 `pdf_ocr_status()` 결과를 그대로 `pdf_ocr`, `pdf_ocr_install_hint`에 반영하는지 unit test를 추가했다.
- mock API contract뿐 아니라 service layer contract도 함께 고정해 `/documents/supported-types` 응답 드리프트를 줄였다.
- targeted self-check에서 `.venv/bin/pytest tests/test_document_service.py tests/test_document_loader.py tests/test_api_contracts.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `275 passed, 1 warning`이다.

### OCR document-types CLI contract

- `local-ai document-types`가 `/documents/supported-types` 백엔드 응답의 `pdf_ocr`, `pdf_ocr_install_hint`, PDF OCR fallback 설명을 그대로 출력하는지 CLI mock test를 추가했다.
- CLI 안에 OCR readiness 판단 로직을 중복 구현하지 않고, 백엔드 응답을 JSON으로 출력하는 기존 구조를 유지했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_cli.py tests/test_document_service.py tests/test_document_loader.py` 결과는 `40 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `276 passed, 1 warning`이다.

### OCR plan public doc link

- `docs/OCR_INTEGRATION_PLAN.md`를 README Key Docs와 `docs/PROJECT_SUMMARY.md` 관련 문서 목록에 추가했다.
- public docs link contract와 README key docs test에 OCR plan 문서 링크를 포함해 누락 드리프트를 방지했다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_portfolio_docs_contract.py` 결과는 `28 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `276 passed, 1 warning`이다.

### OCR status snapshot wording sync

- 2026-05-26 18:27 KST 기준으로 README와 public release summary의 첫 상태표가 PDF OCR fallback 범위를 같은 문구로 설명하도록 정리했다.
- `README.md`의 `Current Status Snapshot`과 `docs/PUBLIC_RELEASE_SUMMARY.md`의 공개용 상태 스냅샷에 `[ocr]` extra, 로컬 `tesseract`, PyPDF image XObject 범위를 명시했다.
- `tests/test_readme_quick_start.py`와 `tests/test_public_release_summary.py`에 `PDF OCR fallback`, `PyPDF image XObject` 계약 문구를 추가해 첫 화면 문서 드리프트를 막았다.
- 기능 활성화나 시스템 패키지 설치는 하지 않았다. 외부 LLM API, cloud OCR, pdf2image/poppler, shell/browser/file-write 실행, 운영 배포, secret 출력은 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_release_summary.py` 결과는 `15 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `276 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `276 passed, 1 warning`, public release check는 `scanned_files=120`, finding 없음이다.

### Index job preview CLI contract

- 2026-05-26 18:33 KST 기준으로 preview-only 대용량 색인 job/status endpoint에 대응하는 `local-ai index-job-preview` 명령을 추가했다.
- CLI는 백엔드 비즈니스 로직을 중복하지 않고 `POST /documents/index-folder-job-preview`를 HTTP로 호출한다.
- README, API reference, PROJECT_SUMMARY의 CLI 목록에 `local-ai index-job-preview`를 추가해 `docs/PREVIEW_ACTIVATION_POLICY.md`의 명령 표와 맞췄다.
- `tests/test_cli.py`와 `tests/test_public_docs_contract.py`가 새 CLI 명령의 endpoint mapping과 공개 문서 노출을 검증한다.
- 실제 queue 생성, SQLite 저장, embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_cli.py tests/test_public_docs_contract.py tests/test_readme_quick_start.py` 결과는 `42 passed, 1 warning`이다.

### Index job preview response schema examples

- 2026-05-26 18:38 KST 기준으로 `POST /documents/index-folder-job-preview`의 preview-only response example을 API reference와 UI bridge examples에 추가했다.
- 예시는 `job_id=preview-only`, `status=planned`, `dry_run=true`, `would_enqueue=false`, `progress.total_files`, `progress.embedding_batches_total`, `progress.percent=0`을 명시한다.
- UI_CONNECT_GUIDE와 UI_CONTRACT_CHEATSHEET도 같은 progress 표시 필드를 강조하도록 갱신했다.
- `tests/test_api_docs_payloads.py`와 `tests/test_ui_bridge_examples.py`가 문서 JSON 예시를 `IndexFolderJobPreviewResponse` schema로 직접 검증한다.
- 실제 queue 생성, SQLite 저장, embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_ui_bridge_examples.py tests/test_ui_connect_guide.py tests/test_ui_contract_cheatsheet.py tests/test_api_contracts.py` 결과는 `32 passed, 1 warning`이다.

### Vector rebuild preview response schema examples

- 2026-05-26 18:42 KST 기준으로 `GET /documents/vector-rebuild-preview`의 read-only response example을 API reference와 UI bridge examples에 추가했다.
- 예시는 `status=needs_rebuild`, `dry_run=true`, `chunks_missing_vectors_count`, `embedding_batches_estimated`, `actions[].action=rebuild_vector`, `actions[].requires_user_approval=true`를 명시한다.
- UI_CONNECT_GUIDE와 UI_CONTRACT_CHEATSHEET도 같은 read-only rebuild preview 표시 필드를 강조하도록 갱신했다.
- `tests/test_api_docs_payloads.py`와 `tests/test_ui_bridge_examples.py`가 문서 JSON 예시를 `DocumentVectorRebuildPreviewResponse` schema로 직접 검증한다.
- 실제 Ollama embedding 생성, Chroma vector 재생성, DB 수정, repair/delete/rebuild 실행, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_ui_bridge_examples.py tests/test_ui_connect_guide.py tests/test_ui_contract_cheatsheet.py tests/test_repair_preview.py tests/test_document_stats.py` 결과는 `28 passed, 1 warning`이다.

### Repair preview response schema examples

- 2026-05-26 18:46 KST 기준으로 `GET /documents/repair-preview`의 read-only response example을 API reference와 UI bridge examples에 추가했다.
- 예시는 `status=needs_repair`, `dry_run=true`, `actions_count`, `actions[].action`, `actions[].requires_user_approval=true`를 명시한다.
- `review_missing_file`, `rebuild_vector`, `review_orphan_vector` 후보를 모두 보여주되 실제 파일 삭제, DB 수정, Chroma 수정은 수행하지 않는다고 문서화했다.
- UI_CONNECT_GUIDE와 UI_CONTRACT_CHEATSHEET도 같은 repair preview 표시 필드를 강조하도록 갱신했다.
- `tests/test_api_docs_payloads.py`와 `tests/test_ui_bridge_examples.py`가 문서 JSON 예시를 `DocumentRepairPreviewResponse` schema로 직접 검증한다.
- 실제 repair/delete/rebuild, DB 수정, Chroma write/delete, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_ui_bridge_examples.py tests/test_ui_connect_guide.py tests/test_ui_contract_cheatsheet.py tests/test_repair_preview.py tests/test_document_stats.py tests/test_preview_activation_policy.py` 결과는 `33 passed, 1 warning`이다.

### Document stats and integrity response schema examples

- 2026-05-26 18:49 KST 기준으로 `GET /documents/stats`와 `GET /documents/integrity`의 read-only response example을 API reference에 추가했다.
- stats 예시는 SQLite/Chroma count와 `missing_stored_files` 목록을 포함한다.
- integrity 예시는 `status=needs_attention`, missing stored file, missing vector, orphan vector, `repair_available=false`를 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `DocumentStatsResponse`, `DocumentIntegrityResponse` schema로 직접 검증한다.
- 실제 repair/delete/rebuild, DB 수정, Chroma write/delete, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_document_stats.py tests/test_operations_runbook.py tests/test_public_docs_contract.py` 결과는 `29 passed, 1 warning`이다.

### Supported document types response schema example

- 2026-05-26 18:52 KST 기준으로 `GET /documents/supported-types` response example을 API reference에 추가했다.
- 예시는 기본 `.txt`, `.md`, optional `.html`, `.pdf`, `.docx`와 `pdf_ocr=false`, `pdf_ocr_install_hint`를 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `SupportedDocumentTypesResponse` schema로 직접 검증한다.
- 실제 OCR 실행, 시스템 패키지 설치, 외부 OCR/cloud OCR, pdf2image/poppler 추가는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_cli.py tests/test_document_service.py tests/test_document_loader.py` 결과는 `61 passed, 1 warning`이다.

### Index folder preview response schema example

- 2026-05-26 18:56 KST 기준으로 `POST /documents/index-folder-preview` response example을 API reference에 추가했다.
- 예시는 `files_count`, `skipped_files_count`, `chunks_estimated`, `embedding_batch_size`, `embedding_batches_estimated`, file별 preview, skipped file reason을 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `IndexFolderPreviewResponse` schema로 직접 검증한다.
- 실제 파일 수정, SQLite 저장, Ollama embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_document_service.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `58 passed, 1 warning`이다.

### Index folder response schema example

- 2026-05-26 18:59 KST 기준으로 `POST /documents/index-folder` response example을 API reference에 추가했다.
- 예시는 `indexed_documents`, `skipped_files`, `chunks_created`, `document_ids`, `indexed_files`, `skipped_file_details`를 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `IndexFolderResponse` schema로 직접 검증한다.
- 실제 폴더 색인, SQLite 저장, Ollama embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_document_service.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `59 passed, 1 warning`이다.

### Document upload response schema example

- 2026-05-26 19:02 KST 기준으로 `POST /documents/upload` response example의 핵심 필드 목록을 API reference에 추가했다.
- 기존 upload response example을 `DocumentUploadResponse` schema로 직접 검증하는 테스트를 추가했다.
- 실제 파일 업로드, SQLite 저장, Ollama embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `56 passed, 1 warning`이다.

### Document list detail chunks response schema examples

- 2026-05-26 19:05 KST 기준으로 `GET /documents`, `GET /documents/{document_id}`, `GET /documents/{document_id}/chunks` response example을 API reference에 추가했다.
- 예시는 문서 목록의 summary field, 상세 조회의 chunk 목록, chunk paging 응답의 `limit`/`offset`/`total_chunks`를 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `DocumentSummary`, `DocumentDetail`, `DocumentChunksResponse` schema로 직접 검증한다.
- 실제 DB 조회, 파일 읽기, embedding 생성, Chroma write, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `59 passed, 1 warning`이다.

### Search chat logs feedback response schema examples

- 2026-05-26 19:10 KST 기준으로 `POST /search`, `GET /chat-logs`, `GET /chat-logs/{chat_log_id}`, `POST /feedback`, `GET /feedback` response example을 API reference에 추가했다.
- 예시는 search result, chat log preview/detail, feedback create/list의 paging/filter field를 포함한다.
- `tests/test_api_docs_payloads.py`가 문서 JSON 예시를 `SearchResponse`, `ChatLogListResponse`, `ChatLogDetail`, `FeedbackResponse`, `FeedbackListResponse` schema로 직접 검증한다.
- 실제 Ollama embedding, Chroma search, DB 조회/쓰기, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_api_contracts.py tests/test_chat_logs.py tests/test_feedback_list.py tests/test_search_service.py tests/test_public_docs_contract.py` 결과는 `53 passed, 1 warning`이다.

### CLI documented command drift guard

- 2026-05-26 19:14 KST 기준으로 README/API/PROJECT_SUMMARY/NEXT_CHAT_HANDOFF에 적힌 `local-ai <command>` 예시가 실제 Typer command에 존재하는지 검증하는 public docs contract를 추가했다.
- 기존 검사는 runtime command가 문서에 누락되지 않는 방향이었다. 이번 검사는 반대로 문서에 stale CLI command 예시가 남는 경우를 잡는다.
- 실제 backend 호출, shell/browser/file-write 실행 활성화, 외부 API 호출은 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_cli.py tests/test_readme_quick_start.py` 결과는 `43 passed, 1 warning`이다.

### Smoke summary example shape guard

- 2026-05-26 19:18 KST 기준으로 `docs/SMOKE_SUMMARY_EXAMPLES.md`의 assistant bridge step 이름을 실제 script 출력인 `assistant-action-preview`와 맞췄다.
- `tests/test_smoke_summary_examples.py`가 document/RAG와 assistant bridge 예시의 step 순서를 script 상수와 직접 비교하고, sanitized summary top-level/step field shape를 고정하도록 보강했다.
- `SANITIZED_SUMMARY_EXCLUDED_FIELDS`에는 `api_key`, `document_id`, `chunk_id`도 명시해 예시 문서와 script 출력 계약을 일치시켰다.
- 실제 smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_summary_examples.py tests/test_smoke_script.py tests/test_tasks_doc.py tests/test_public_docs_contract.py` 결과는 `33 passed, 1 warning`이다.

### Supported document E2E next-improvement wording

- 2026-05-26 19:22 KST 기준으로 README, PROJECT_SUMMARY, PUBLIC_RELEASE_SUMMARY, FINAL_REPORT, RELEASE_CHECKLIST, NEXT_CHAT_HANDOFF의 실제 사용자 문서 E2E smoke next-improvement 문구를 현재 지원 타입인 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 기준으로 맞췄다.
- 관련 contract test도 같은 지원 타입 문구를 확인하도록 갱신했다.
- 실제 smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_tasks_doc.py tests/test_next_chat_handoff.py tests/test_user_document_e2e_plan.py` 결과는 `21 passed, 1 warning`이다.

### Handoff task boundary drift guard

- 2026-05-26 19:26 KST 기준으로 `docs/NEXT_CHAT_HANDOFF.md`의 safe/manual/review 경계 문구를 README, PROJECT_SUMMARY, TASKS와 같은 핵심 용어로 맞췄다.
- `tests/test_next_chat_handoff.py`가 endpoint/response field 계약, runtime endpoint count drift, assistant bridge smoke, PDF OCR, repair/browser/shell/file/deploy/auth/rate-limit 경계가 네 문서에 같이 남아 있는지 검증한다.
- 실제 브라우저 UI 확인, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_tasks_doc.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py` 결과는 `19 passed, 1 warning`이다.

### Public release contract snapshot

- 2026-05-26 19:30 KST 기준으로 `docs/PUBLIC_RELEASE_SUMMARY.md`에 FastAPI endpoint 수, 보호/public endpoint 수, Typer CLI command 수, smoke/preflight step 수를 한 표로 정리했다.
- `tests/test_public_release_summary.py`가 release snapshot의 count를 runtime `build_api_inventory(app.routes)`, Typer command registry, smoke flow 상수와 직접 비교한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_public_docs_contract.py tests/test_ui_bridge_examples.py tests/test_smoke_summary_examples.py` 결과는 `33 passed, 1 warning`이다.

### Public verification count wording sync

- 2026-05-26 19:36 KST 기준으로 공개 전 최종 pass 문서의 pytest 검증 수치를 현재 `301 passed` 상태로 맞췄다.
- `docs/PUBLIC_RELEASE_SUMMARY.md`, `docs/PROJECT_SUMMARY.md`, `docs/FINAL_REPORT.md`, `docs/NEXT_CHAT_HANDOFF.md`, `docs/CLAUDE_REVIEW_HANDOFF.md`의 최신 검증 수치 문구를 동기화했다.
- `tests/test_public_release_summary.py`, `tests/test_portfolio_docs_contract.py`, `tests/test_next_chat_handoff.py`가 `301 passed` 문구를 직접 확인하도록 보강했다.
- 과거 WORKLOG의 `276 passed` 항목은 당시 실행 기록이라 수정하지 않았다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `18 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `301 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `301 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### README Key Docs link contract

- 2026-05-26 19:41 KST 기준으로 README `Key Docs` 목록이 공개 핵심 문서 전체를 포함하는지 직접 검증하는 테스트를 보강했다.
- `tests/test_readme_quick_start.py`가 `docs/TASKS.md`, `docs/USER_DOCUMENT_E2E_PLAN.md`, `docs/SMOKE_SUMMARY_EXAMPLES.md`, `docs/PREVIEW_ACTIVATION_POLICY.md`, `docs/UI_CONNECT_GUIDE.md`, `docs/UI_CONTRACT_CHEATSHEET.md`까지 README `Key Docs` 섹션에 남아 있는지 확인한다.
- README `Key Docs` 섹션의 markdown link target이 실제 파일로 존재하는지도 확인한다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `302 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `43 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `302 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `302 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### API response field coverage drift guard

- 2026-05-26 19:46 KST 기준으로 `docs/API.md`의 응답 핵심 필드 표가 실제 Pydantic response model top-level field를 누락하지 않도록 테스트를 보강했다.
- `tests/test_api_docs_payloads.py`가 문서에 적힌 응답 필드가 schema에 존재하는지뿐 아니라, schema의 top-level field가 문서 응답 핵심 필드에 모두 포함되는지도 확인한다.
- `docs/API.md`의 assistant, agent plan, index-folder-preview 응답 핵심 필드에 누락된 `service`, `local_only`, `safety`, `note` 등 top-level field를 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `303 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py` 결과는 `21 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_api_docs_payloads.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `39 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `303 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `303 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Release stop condition contract guard

- 2026-05-26 19:51 KST 기준으로 release checklist, README, SECURITY, PUBLIC_RELEASE_SUMMARY, PROJECT_SUMMARY의 고위험 stop condition 문구가 서로 빠지지 않도록 테스트를 보강했다.
- `tests/test_security_docs_contract.py`가 각 공개 문서에 외부 LLM API, 실제 shell 실행, 브라우저 자동화, 파일 생성/수정/삭제, 운영 배포, Oracle, DB migration, 비용 경계가 남아 있는지 확인한다.
- `docs/PUBLIC_RELEASE_SUMMARY.md`, `README.md`, `docs/PROJECT_SUMMARY.md`에 DB migration, 운영 데이터 변경, 비용 발생 가능 리소스 사용이 별도 승인/보안 리뷰 대상임을 명시했다.
- `SECURITY.md` 고위험 작업 목록에 `실제 shell 실행`, `파일 생성/수정/삭제 자동화` 표현을 명확히 추가했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `305 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_security_docs_contract.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `24 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `305 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `305 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Smoke sanitized summary excluded-field guard

- 2026-05-26 19:57 KST 기준으로 `scripts/smoke_test_api.py --sanitized-summary`의 paste-safe 계약을 더 촘촘히 검증하도록 테스트를 보강했다.
- `tests/test_smoke_script.py`가 raw summary에 포함된 `question`, `answer`, `content`, `headers`, `note`, `api_key`, `project_root`, `request_id`, `stored_path`, `document_id`, `chunk_id` key와 민감 값이 sanitized summary 본문에서 재귀적으로 제거되는지 확인한다.
- `tests/test_smoke_summary_examples.py`가 `docs/SMOKE_SUMMARY_EXAMPLES.md` 사용 규칙에 `SANITIZED_SUMMARY_EXCLUDED_FIELDS` 전체 목록이 문서화되어 있는지 확인한다.
- `docs/SMOKE_SUMMARY_EXAMPLES.md`의 사용 규칙을 script 상수와 같은 excluded field 목록 기준으로 명확히 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `307 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_smoke_summary_examples.py` 결과는 `18 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_smoke_script.py tests/test_smoke_summary_examples.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `36 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `307 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `307 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Assistant UI runtime contract drift guard

- 2026-05-26 20:03 KST 기준으로 assistant UI 문서가 실제 `AssistantService().ui_contract()`의 startup sequence, refresh endpoint, message flow, response type, blocked action, safety 값을 놓치지 않도록 테스트를 보강했다.
- `docs/UI_CONTRACT_CHEATSHEET.md`에 `GET /assistant/ui-contract`의 `refresh_endpoints` 표를 추가했다.
- `docs/UI_CONNECT_GUIDE.md`에 refresh endpoint 목록, 전체 `response_types` 렌더링 표, `shell_dry_run`, `folder_index` safety 값을 추가했다.
- `docs/UI_QA_CHECKLIST.md`에 `safety.shell_dry_run`과 `safety.folder_index` 확인 항목을 추가했다.
- `tests/test_ui_connect_guide.py`, `tests/test_ui_qa_checklist.py`, `tests/test_ui_contract_cheatsheet.py`가 실제 service contract를 기준으로 문서 drift를 확인한다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `309 passed` 기준으로 맞췄다.
- 실제 브라우저 조작, 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_ui_qa_checklist.py tests/test_ui_contract_cheatsheet.py tests/test_ui_bridge_examples.py` 결과는 `23 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_ui_qa_checklist.py tests/test_ui_contract_cheatsheet.py tests/test_ui_bridge_examples.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `41 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `309 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `309 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Local CI command order contract guard

- 2026-05-26 20:08 KST 기준으로 README와 운영/release 문서의 `local_ci_check.py` 내부 실행 순서가 실제 `scripts/local_ci_check.py`의 `build_check_commands()` 순서와 맞는지 테스트를 보강했다.
- `README.md`의 Verification 섹션에 `python scripts/local_ci_check.py --root .`가 실행하는 내부 단계 `pytest`, `compileall`, public release check, `git diff --check` 순서를 명시했다.
- `tests/test_operations_runbook.py`가 README, OPERATIONS, RELEASE_CHECKLIST, PUBLIC_RELEASE_SUMMARY의 local CI 명령 순서를 script contract와 비교한다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `310 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_operations_runbook.py tests/test_local_ci_check.py tests/test_readme_quick_start.py` 결과는 `19 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_operations_runbook.py tests/test_local_ci_check.py tests/test_readme_quick_start.py tests/test_public_release_summary.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `37 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `310 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `310 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### README and Project Summary runtime snapshot guard

- 2026-05-26 20:16 KST 기준으로 README와 `docs/PROJECT_SUMMARY.md`에 `Runtime Contract Snapshot` 표를 추가했다.
- 표에는 FastAPI endpoint 수, protected/public endpoint 수, Typer CLI command 수, Document/RAG smoke step 수, Assistant bridge smoke/preflight step 수를 기록했다.
- `tests/test_public_docs_contract.py`가 README와 Project Summary의 snapshot 값을 실제 `build_api_inventory(app.routes)`, Typer command inventory, smoke flow 상수와 비교하도록 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `311 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py` 결과는 `15 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_next_chat_handoff.py` 결과는 `33 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `311 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `311 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### TASKS runtime snapshot guard tracking

- 2026-05-26 20:19 KST 기준으로 `docs/TASKS.md`의 안전 작업 완료 목록에 README와 `docs/PROJECT_SUMMARY.md`의 `Runtime Contract Snapshot` 검증 유지 항목을 추가했다.
- `tests/test_tasks_doc.py`가 해당 항목을 확인하도록 보강해 task board가 최신 문서 drift guard를 놓치지 않게 했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_tasks_doc.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `24 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `311 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `311 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### Release checklist runtime snapshot guard tracking

- 2026-05-26 20:23 KST 기준으로 `docs/RELEASE_CHECKLIST.md` 자동 검증 항목에 README/Project Summary `Runtime Contract Snapshot` 값과 실제 API/CLI/smoke flow inventory 비교를 추가했다.
- `docs/PUBLIC_RELEASE_SUMMARY.md`의 공개 후 안전 개선 경계에도 같은 snapshot guard 유지 항목을 추가했다.
- `tests/test_public_docs_contract.py`와 `tests/test_public_release_summary.py`가 release checklist와 public release summary의 해당 문구를 확인하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_public_release_summary.py` 결과는 `21 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `311 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `311 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### Handoff runtime snapshot guard alignment

- 2026-05-26 20:28 KST 기준으로 README, `docs/PROJECT_SUMMARY.md`, `docs/FINAL_REPORT.md`, `docs/NEXT_CHAT_HANDOFF.md`의 다음 추천 개선에 README/Project Summary `Runtime Contract Snapshot`과 실제 API/CLI/smoke flow inventory 비교 계약을 추가했다.
- `docs/TASKS.md`의 같은 항목도 동일한 표기인 `README/Project Summary Runtime Contract Snapshot`으로 맞췄다.
- `tests/test_next_chat_handoff.py`, `tests/test_portfolio_docs_contract.py`, `tests/test_tasks_doc.py`가 해당 문구를 확인하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py tests/test_tasks_doc.py` 결과는 `21 passed, 1 warning`이다.
- full self-check에서 `.venv/bin/pytest` 결과는 `311 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `311 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### Handoff recent-test snapshot guard note

- 2026-05-26 20:31 KST 기준으로 `docs/NEXT_CHAT_HANDOFF.md`의 최근 테스트 보강 목록에 Runtime Contract Snapshot guard 관련 테스트 설명을 추가했다.
- `tests/test_next_chat_handoff.py`가 `tests/test_public_docs_contract.py`, `tests/test_tasks_doc.py`, `tests/test_public_release_summary.py`, `tests/test_portfolio_docs_contract.py`, `tests/test_next_chat_handoff.py`의 snapshot guard 역할 설명이 handoff에 남아 있는지 검증하도록 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `312 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py` 결과는 `7 passed, 1 warning`이다.
- targeted contract self-check에서 `.venv/bin/pytest tests/test_next_chat_handoff.py tests/test_portfolio_docs_contract.py tests/test_public_release_summary.py` 결과는 `19 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### README onboarding snapshot heading guard

- 2026-05-26 20:34 KST 기준으로 `tests/test_readme_quick_start.py`가 README 상단 온보딩 섹션에 `Runtime Contract Snapshot` heading이 남아 있는지 확인하도록 보강했다.
- 이 guard는 README 첫 진입자가 quick start, verification, assistant flow, safe boundaries, runtime snapshot, key docs를 같은 상단 흐름에서 볼 수 있게 유지한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_public_docs_contract.py tests/test_next_chat_handoff.py` 결과는 `33 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### Claude handoff verification count guard

- 2026-05-26 20:36 KST 기준으로 `tests/test_portfolio_docs_contract.py`가 `docs/CLAUDE_REVIEW_HANDOFF.md`의 최신 pytest 검증 수치도 함께 확인하도록 보강했다.
- 이 guard는 Project Summary, Final Report, Claude Review Handoff의 최신 검증 수치가 서로 어긋나지 않게 유지한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_portfolio_docs_contract.py tests/test_public_docs_contract.py` 결과는 `21 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
- `git diff --check` 결과는 성공이다.

### Project status safety boundary contract guard

- 2026-05-26 20:40 KST 기준으로 `tests/test_api_contracts.py`의 `/project/status` 계약 테스트가 `blocked_until_review`와 `recommended_next_model.user_action_required`의 고위험 작업 경계를 검증하도록 보강했다.
- 이 guard는 unrestricted shell, file write/delete/patch apply, browser click/fill/submit/login, deployment/cloud changes, automatic fine-tuning이 안전 작업처럼 보이지 않게 유지한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_api_contracts.py tests/test_tasks_doc.py tests/test_public_docs_contract.py` 결과는 `30 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### UI contract API inventory count field guard

- 2026-05-26 20:44 KST 기준으로 `docs/UI_CONTRACT_CHEATSHEET.md`의 `GET /project/api-inventory` 표시 필드에 `mode`, `local_only`, `endpoints_count`, `protected_endpoints_count`, `public_endpoints_count`, `safety`를 명시했다.
- `tests/test_ui_contract_cheatsheet.py`가 해당 top-level count/safety 필드가 cheatsheet에 남아 있는지 검증하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_contract_cheatsheet.py tests/test_ui_connect_guide.py tests/test_public_docs_contract.py` 결과는 `26 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### UI bridge safety example runtime guard

- 2026-05-26 20:47 KST 기준으로 `docs/UI_BRIDGE_EXAMPLES.md`의 `/assistant/ui-contract` 예시 `safety` 값을 실제 `AssistantService().ui_contract()` 응답과 같은 필드/값으로 맞췄다.
- `tests/test_ui_bridge_examples.py`가 예시의 `safety` dict 전체가 runtime contract와 동일한지 검증하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py tests/test_ui_connect_guide.py` 결과는 `20 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### README assistant REPL help ordering guard

- 2026-05-26 21:14 KST 기준으로 `tests/test_readme_quick_start.py`가 README의 `local-ai assistant` REPL command block 순서와 `cli.main.ASSISTANT_REPL_HELP_LINES`의 실제 help 순서가 정확히 같은지 검증하도록 보강했다.
- 이 guard는 CLI REPL help가 바뀌었을 때 README 명령 목록이 누락, 추가, 순서 drift 없이 함께 갱신되도록 한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_readme_quick_start.py tests/test_cli.py tests/test_public_docs_contract.py` 결과는 `45 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `312 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### API reference CLI block runtime guard

- 2026-05-26 21:19 KST 기준으로 `tests/test_public_docs_contract.py`가 `docs/API.md`의 `## CLI 대응` bash block에 적힌 `local-ai` command set과 실제 Typer command set이 정확히 같은지 검증하도록 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `313 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_readme_quick_start.py tests/test_cli.py` 결과는 `46 passed, 1 warning`이다.
- targeted docs-count self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py tests/test_readme_quick_start.py tests/test_cli.py` 결과는 `65 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `313 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### API reference public endpoint inventory guard

- 2026-05-26 21:22 KST 기준으로 `docs/API.md`의 public read-only endpoint 설명을 실제 `/project/api-inventory` 기준 public endpoint 16개와 맞췄다.
- `tests/test_public_docs_contract.py`가 API reference의 public read-only 문장이 runtime inventory에서 `requires_api_key=false`인 endpoint 전체를 포함하는지 검증하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_security.py tests/test_api_contracts.py` 결과는 `70 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `313 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Public endpoint snapshot cross-check guard

- 2026-05-26 21:26 KST 기준으로 `tests/test_public_docs_contract.py`가 API reference public read-only endpoint 문장의 endpoint set이 runtime inventory의 public endpoint set과 정확히 같은지 검증하도록 보강했다.
- 같은 테스트가 README와 `docs/PROJECT_SUMMARY.md`의 `Public endpoints` snapshot 값이 API reference public endpoint 문장 개수와도 일치하는지 확인한다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_security.py tests/test_api_contracts.py` 결과는 `70 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `313 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### Protected endpoint inventory security guard

- 2026-05-26 21:31 KST 기준으로 `tests/test_security.py`의 보호 endpoint 호출 사례를 `PROTECTED_ENDPOINT_CASES` 상수로 분리했다.
- `tests/test_security.py`가 `PROTECTED_ENDPOINT_CASES`의 method/path set과 `/project/api-inventory`의 `requires_api_key=true` endpoint set 및 `protected_endpoints_count`가 정확히 같은지 검증하도록 보강했다.
- 공개 문서의 최신 pytest 수치 문구를 새 전체 테스트 개수인 `314 passed` 기준으로 맞췄다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_security.py tests/test_public_docs_contract.py tests/test_api_contracts.py` 결과는 `71 passed, 1 warning`이다.
- targeted docs-count self-check에서 `.venv/bin/pytest tests/test_security.py tests/test_public_docs_contract.py tests/test_api_contracts.py tests/test_portfolio_docs_contract.py tests/test_next_chat_handoff.py tests/test_public_release_summary.py` 결과는 `90 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `314 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### API inventory safety summary guard

- 2026-05-26 21:36 KST 기준으로 `docs/API.md`의 `GET /project/api-inventory` 핵심 필드에 `safety.external_llm_api=disabled`, `safety.shell_execution=dry-run-only`, `safety.browser_interaction=disabled`, `safety.file_write_delete=disabled`를 명시했다.
- `tests/test_public_docs_contract.py`가 runtime API inventory `safety` dict의 모든 key/value가 API reference에 같은 `safety.<key>=<value>` 형태로 남아 있는지 검증하도록 보강했다.
- `tests/test_ui_bridge_examples.py`가 `docs/UI_BRIDGE_EXAMPLES.md`의 `/project/api-inventory` 예시 `safety` dict 전체가 runtime inventory와 동일한지 검증하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_public_docs_contract.py tests/test_ui_bridge_examples.py tests/test_ui_contract_cheatsheet.py tests/test_api_contracts.py` 결과는 `42 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `314 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.

### UI connect guide request schema guard

- 2026-05-26 21:40 KST 기준으로 `docs/UI_CONNECT_GUIDE.md`의 copy-ready fetch 예시가 `POST /assistant/bootstrap` 요청에 `project_root`, `include_sessions`, `sessions_limit`을 명시하도록 보강했다.
- 같은 예시가 `POST /assistant/message` 요청에 `message`, `session_id`, `project_root`, `mode`, `top_k`, `temperature`를 명시하도록 보강했다.
- `tests/test_ui_connect_guide.py`가 `AssistantBootstrapRequest`와 `AssistantMessageRequest`의 field 이름이 copy-ready fetch 예시에 남아 있는지 검증하도록 보강했다.
- 실제 서버 실행, smoke 실행, 문서 업로드, SQLite/Chroma 쓰기, Ollama 호출, shell/browser/file-write 실행 활성화는 수행하지 않았다.
- targeted self-check에서 `.venv/bin/pytest tests/test_ui_connect_guide.py tests/test_api_docs_payloads.py tests/test_assistant_api.py` 결과는 `39 passed, 1 warning`이다.
- full local CI에서 `.venv/bin/python scripts/local_ci_check.py --root .` 결과는 성공이며, 내부 `pytest` 결과는 `314 passed, 1 warning`, compileall 성공, public release check `ok=true`, `scanned_files=120`, finding 없음, `git diff --check` 성공이다.
