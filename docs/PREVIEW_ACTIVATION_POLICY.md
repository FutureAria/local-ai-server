# PREVIEW_ACTIVATION_POLICY

이 문서는 preview-only 기능을 실제 실행 기능으로 바꾸기 전에 필요한 조건을 정리한다.

현재 `local-ai-server`의 대용량 색인 job/status와 Chroma vector rebuild 관련 기능은 미리보기 계약이다. 이 문서는 실제 queue, 실제 rebuild, 실제 repair/delete를 활성화하지 않는다.

## 현재 Preview-Only 기능

| 기능 | Endpoint | CLI | 현재 동작 |
|---|---|---|---|
| 대용량 폴더 색인 job preview | `POST /documents/index-folder-job-preview` | `local-ai index-job-preview` | `dry_run=true`, `would_enqueue=false`, `job_id=preview-only`, `progress.percent=0` |
| Chroma 누락 vector rebuild preview | `GET /documents/vector-rebuild-preview` | `local-ai vector-rebuild-preview` | `dry_run=true`, `embedding_batches_estimated`, `actions`만 반환 |
| SQLite/Chroma repair preview | `GET /documents/repair-preview` | `local-ai repair-preview` | 필요한 action 후보만 반환하고 실제 repair/delete/rebuild는 수행하지 않음 |

## 실제 Queue 활성화 전 조건

`POST /documents/index-folder-job-preview`를 실제 queue/job API로 확장하려면 아래 조건이 먼저 필요하다.

- [ ] 별도 endpoint를 추가하고 preview endpoint의 의미를 바꾸지 않는다.
- [ ] job 상태 저장소를 정의한다. SQLite 테이블 또는 별도 queue storage를 명확히 선택한다.
- [ ] `job_id`, `status`, `progress`, `error`, `created_at`, `updated_at` schema를 문서화한다.
- [ ] 중복 job, 취소, 재시도, 실패 복구 정책을 정한다.
- [ ] 업로드/색인 대상 원본 파일을 수정하지 않는다는 invariant를 테스트한다.
- [ ] embedding batch 실패 시 SQLite/Chroma 부분 저장 rollback 또는 재시도 정책을 명확히 한다.
- [ ] `LOCAL_API_KEY` 보호와 rate limit을 유지한다.
- [ ] queue worker가 외부 LLM API를 호출하지 않고 Ollama local API만 사용하는지 검증한다.
- [ ] `docs/RELEASE_CHECKLIST.md`와 `SECURITY.md`에 실제 저장 영향과 stop condition을 갱신한다.
- [ ] 사용자 승인 또는 보안 리뷰 후에만 실제 enqueue를 허용한다.

## 실제 Rebuild 활성화 전 조건

`GET /documents/vector-rebuild-preview`를 실제 Chroma vector rebuild 명령으로 확장하려면 아래 조건이 먼저 필요하다.

- [ ] preview endpoint와 실제 실행 endpoint를 분리한다.
- [ ] 실제 실행 endpoint는 `LOCAL_API_KEY` 보호를 유지한다.
- [ ] rebuild 대상 chunk id, document id, chunk index를 실행 전에 다시 조회해 SQLite를 source of truth로 사용한다.
- [ ] Ollama embedding model과 `EMBEDDING_BATCH_SIZE`, `EMBEDDING_MAX_RETRIES`를 로그와 응답에 민감 정보 없이 남긴다.
- [ ] Chroma write 실패 시 재시도/부분 실패/재실행 가능성을 문서화한다.
- [ ] orphan vector delete는 rebuild와 분리하고, 별도 승인 없이는 삭제하지 않는다.
- [ ] dry-run 결과와 실제 실행 결과를 비교할 수 있는 테스트를 추가한다.
- [ ] 실제 embedding 생성과 Chroma write가 발생한다는 저장 영향을 README와 운영 문서에 명확히 표시한다.
- [ ] 사용자 승인 또는 보안 리뷰 후에만 실제 rebuild를 허용한다.

## 실제 Repair/Delete 활성화 전 조건

`GET /documents/repair-preview`의 action 후보를 실제 repair/delete 명령으로 바꾸려면 아래 조건이 필요하다.

- [ ] preview와 실제 실행 endpoint를 분리한다.
- [ ] 실제 delete는 대상 document/chunk/vector id를 명시적으로 다시 확인한다.
- [ ] 삭제 전 backup 또는 export 전략을 문서화한다.
- [ ] orphan vector 삭제는 SQLite source of truth와 비교한 뒤 별도 승인으로만 수행한다.
- [ ] 실행 결과에 삭제 수량, 실패 수량, skipped 수량을 기록한다.
- [ ] `.env`, SQLite DB, Chroma index, uploads, logs, SFT JSONL이 Git에 포함되지 않는지 public release check를 유지한다.

## Stop Conditions

아래 중 하나라도 필요하면 Codex는 구현을 멈추고 `Decision Required` 또는 Claude Opus 보안/아키텍처 리뷰로 넘긴다.

- 실제 repair/delete/rebuild 실행
- 실제 queue worker 또는 background worker 도입
- 실제 Chroma write/delete 자동화
- 실제 파일 생성, 수정, 삭제 자동화
- workspace 밖 파일 접근
- 외부 LLM API 또는 외부 embedding API 활성화
- 운영 배포, 클라우드/Oracle 리소스 변경, 비용 또는 저장공간 영향

## 검증 명령

```bash
.venv/bin/pytest tests/test_preview_activation_policy.py tests/test_repair_preview.py tests/test_document_stats.py
.venv/bin/python scripts/local_ci_check.py --root .
```
