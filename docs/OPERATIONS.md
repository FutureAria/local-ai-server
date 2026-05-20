# Operations Guide

이 문서는 `local-ai-server`를 로컬 PC 또는 개인 서버에서 운영할 때의 로그, 저장공간, 백업, 점검 기준을 정리한다. 실제 클라우드 배포, 시스템 서비스 등록, 로그 삭제 자동화는 이 문서에서 실행하지 않는다.

## 운영 원칙

- 기본 bind 주소는 `127.0.0.1`을 권장한다.
- 런타임 LLM과 embedding은 Ollama local API만 사용한다.
- OpenAI, Claude, Gemini 같은 외부 LLM API를 운영 경로에 추가하지 않는다.
- `LOCAL_API_KEY`를 설정한 경우 보호 endpoint에는 `X-API-Key`를 사용한다.
- `LOCAL_RATE_LIMIT_PER_MINUTE`로 보호 endpoint의 process-local in-memory rate limit을 조정한다. 기본값은 `120`이고, `0`이면 비활성화된다.
- `.env`, API key, DB password, 개인 문서 원문, 운영 로그 파일은 Git에 올리지 않는다.
- 원본 색인 대상 폴더의 파일은 수정하거나 삭제하지 않는다.

## 저장 위치

| 항목 | 기본 위치 | 성격 | Git 포함 여부 |
|---|---|---|---|
| SQLite DB | `data/local_ai.sqlite3` | 문서 메타데이터, chunk, chat log, feedback | 제외 |
| Chroma index | `data/chroma/` | vector search 저장소 | 제외 |
| 업로드 파일 | `data/uploads/` | 사용자가 업로드한 원본 파일 copy | 제외 |
| SFT export | `data/*.jsonl` | fine-tuning 후보 데이터 | 제외 |
| 운영 로그 파일 | `data/logs/` | 서버 stdout/stderr 또는 운영 로그 | 제외 |

## 로그 정책

현재 애플리케이션은 별도 파일 logger를 강제로 생성하지 않는다. 기본 운영은 `uvicorn`의 stdout/stderr 로그를 사용한다.

권장 로그 원칙:

- 요청 body 전체를 access log나 application log에 남기지 않는다.
- 질문, 답변, 문서 원문은 SQLite의 기능 데이터로만 관리하고 일반 운영 로그에 중복 저장하지 않는다.
- `LOCAL_API_KEY`, 환경변수, secret 값을 로그에 출력하지 않는다.
- 장애 분석에는 `request_id`, endpoint, status code, 오류 메시지 수준만 사용한다.
- 장기 운영 시 로그 파일은 `data/logs/` 아래에 두고 Git에서 제외한다.

로컬 파일 로그가 필요하면 shell redirection으로 시작할 수 있다.

```bash
mkdir -p data/logs
uvicorn app.main:app --host 127.0.0.1 --port 8000 >> data/logs/server.log 2>&1
```

## 수동 로그 rotation 예시

아래 명령은 예시다. 실제 운영 중인 서버 로그 파일을 회전하기 전에 서버 실행 방식과 파일 핸들을 확인해야 한다.

```bash
mkdir -p data/logs/archive
cp data/logs/server.log "data/logs/archive/server-$(date +%Y%m%d-%H%M%S).log"
: > data/logs/server.log
```

주의:

- 이 명령은 로그 파일을 비우므로 필요한 경우 먼저 archive copy를 확인한다.
- 운영 중인 프로세스가 파일 핸들을 계속 잡고 있으면 서비스 재시작이 필요할 수 있다.
- 사용자 승인 없이 자동 삭제 작업을 추가하지 않는다.

## 저장공간 점검

정기적으로 아래 명령을 확인한다.

```bash
du -sh data
du -sh data/uploads data/chroma data/logs 2>/dev/null
local-ai stats
local-ai integrity
local-ai repair-preview
```

공개 전 로컬 데이터와 secret 후보를 점검한다.

```bash
python scripts/public_release_check.py --root .
```

점검 기준:

- `data/uploads/`: 업로드 파일이 계속 쌓인다.
- `data/chroma/`: 색인한 chunk 수에 따라 증가한다.
- `data/local_ai.sqlite3`: chat log, chunk, feedback 누적에 따라 증가한다.
- `data/logs/`: shell redirection 또는 운영 환경 설정에 따라 증가한다.

## 백업 기준

백업 대상:

- `data/local_ai.sqlite3`
- `data/uploads/`
- `data/chroma/`

SFT export 파일은 재생성 가능하지만, 학습 데이터 후보로 관리한다면 별도 백업한다.

```bash
mkdir -p backups
cp data/local_ai.sqlite3 "backups/local_ai-$(date +%Y%m%d-%H%M%S).sqlite3"
```

주의:

- 서버가 쓰기 중일 때 DB 파일을 복사하면 일관성이 깨질 수 있다.
- 안전한 백업은 서버를 잠시 멈춘 뒤 수행하는 것을 권장한다.
- 운영 DB migration, 복구, 삭제는 사용자 승인 후 진행한다.

## 장애 점검 순서

1. 서버 상태 확인

```bash
curl http://127.0.0.1:8000/health
```

2. Ollama/model 준비 상태 확인

```bash
local-ai doctor
```

3. 저장소 상태 확인

```bash
local-ai stats
local-ai integrity
local-ai repair-preview
```

4. 최근 chat log 확인

```bash
local-ai logs --limit 10 --offset 0
```

5. 필요하면 서버 stdout/stderr 또는 `data/logs/server.log` 확인

```bash
tail -n 100 data/logs/server.log
```

## 운영 한계

- 자동 로그 rotation은 아직 구현하지 않았다.
- 서비스 매니저 설정(systemd, launchd 등)은 제공하지 않는다.
- 실제 repair/rebuild/delete 명령은 read-only preview까지만 제공한다.
- 클라우드 배포, Oracle DB, Oracle Object Storage, 외부 LLM API는 사용하지 않는다.
