# OCR Integration Plan

## 목적

- PDF 페이지 중 텍스트가 추출되지 않는, 이미지 기반 페이지에 대해 fallback OCR을 적용해 텍스트를 얻는다.
- 외부 LLM API 또는 cloud OCR 서비스는 사용하지 않는다. 금지 대상에는 GPT, Claude, Gemini, Vision API, Google Cloud Vision, AWS Textract 같은 외부 서비스가 포함된다.
- OCR은 로컬 `tesseract` binary와 Python wrapper만 사용한다.

## 의존성 정책

- Python dependency는 optional extras로만 추가한다.
  - `pyproject.toml`에 `[ocr]` extra를 추가한다.
  - 포함 후보는 `pytesseract`, `Pillow`다.
  - 개발 환경에서는 `pip install -e ".[dev,documents,ocr]"` 형태로 설치 가능해야 한다.
- 시스템 dependency는 자동 설치하지 않는다.
  - macOS 예시: `brew install tesseract`
  - Ubuntu/Debian 예시: `sudo apt install tesseract-ocr`
- 한국어 OCR이 필요하면 language pack을 사용자가 별도로 설치한다.
  - macOS/Homebrew 환경은 설치 방식이 환경별로 다를 수 있으므로 `tesseract --list-langs`로 `kor` 지원 여부를 확인하게 안내한다.
  - Ubuntu/Debian 예시: `sudo apt install tesseract-ocr-kor`
- `tesseract` binary가 없으면 서버 import, 문서 타입 조회, 일반 문서 업로드는 계속 동작해야 한다.
- `tesseract` 미설치 또는 Python OCR dependency 미설치 상태에서는 `/documents/supported-types`에 `pdf_ocr=false`를 표시한다.
- OCR이 필요한 업로드에서 OCR dependency 또는 binary가 없으면 조용히 실패하지 않고, 명확한 설치 안내 메시지와 skip reason을 반환한다.

## 동작 범위

- 일반 PDF 텍스트 추출이 비어 있거나 매우 짧은 페이지에만 OCR fallback을 적용한다.
- PyPDF가 충분한 텍스트를 추출한 페이지는 OCR을 수행하지 않는다.
- OCR 입력은 PDF 내부에서 PyPDF로 추출 가능한 image XObject로 제한한다.
- 이번 phase에서는 `pdf2image`, `poppler`, headless browser, cloud OCR fallback을 추가하지 않는다.
- PyPDF로 이미지 추출이 불가능한 PDF는 명확하게 skip하고 reason을 기록한다.
- 자동 fallback chain을 길게 만들지 않는다. PyPDF image XObject 기반 OCR이 실패하면 해당 페이지 OCR은 종료한다.
- OCR 결과 텍스트는 일반 PDF 텍스트와 동일한 흐름으로 처리한다.
  - chunking
  - embedding 생성
  - SQLite `documents`, `document_chunks` 저장
  - Chroma vector 저장
  - RAG 검색과 답변 source로 사용

## 안전 경계

- OCR 처리 중 이미지 자체는 저장하지 않는다.
- PIL `Image` 객체는 메모리에서만 사용한다.
- OCR 결과 텍스트만 SQLite `document_chunks`에 저장한다.
- 원본 image bytes, 중간 PNG/JPEG 파일, 렌더링된 page image는 저장하지 않는다.
- OCR은 외부 통신을 하지 않는다. `tesseract`는 로컬 binary로만 실행한다.
- 일시적 OCR 실패는 자동 재시도하지 않는다.
- OCR 실패는 페이지 단위로 skip하고 `skipped_file_details` 또는 loader metadata에 reason을 남긴다.
- 시스템 패키지인 `tesseract`, `poppler` 등은 자동 설치하지 않는다.
- README에는 사용자가 직접 시스템 패키지를 설치해야 한다고 명시한다.
- OCR이 활성화된 환경에서도 기본 PDF 텍스트 추출이 우선이다.
- OCR은 fallback이며, 정상 텍스트 추출 페이지를 재처리하지 않는다.

## 한계

- OCR 정확도는 원본 이미지 품질, 해상도, 회전 상태, 글꼴, 배경 노이즈, tesseract 언어 모델에 의존한다.
- OCR 품질 저하는 검색 recall과 RAG 답변 품질에 직접 영향을 줄 수 있다.
- 페이지 수가 많은 PDF에서는 처리 시간이 길어질 수 있다.
- 큰 PDF는 사용자가 직접 분할한 뒤 업로드하는 방식을 권장한다.
- 한국어 OCR은 별도 language pack 설치가 필요하다.
- PyPDF가 image XObject를 추출하지 못하는 스캔 PDF는 현재 범위 밖이다.
- flat scan PDF, 복잡한 압축 이미지, page rendering이 필요한 PDF는 이번 phase에서 처리하지 않는다.
- `pdf2image`와 `poppler` 기반 page rendering fallback은 별도 phase에서 보안/운영 검토 후 결정한다.

## 코드 변경 범위

- `pyproject.toml`
  - optional dependency `[ocr]`를 추가한다.
  - `pytesseract`, `Pillow`를 OCR extra에 둔다.
- `app/services/document_loader.py`
  - PDF loader에 OCR fallback 함수를 추가한다.
  - 일반 PDF 텍스트 추출을 먼저 수행한다.
  - 페이지 텍스트가 비어 있거나 threshold보다 짧은 경우에만 image XObject OCR을 시도한다.
  - `pytesseract` import 실패, `Pillow` import 실패, `tesseract` binary 미설치, image 추출 실패를 graceful skip으로 처리한다.
  - skip reason은 테스트 가능한 구조로 반환하거나 loader error message에 포함한다.
- `app/services/document_service.py` 또는 supported types service
  - OCR dependency와 binary 사용 가능 여부를 판단한다.
  - `/documents/supported-types`에서 OCR 가능 여부를 표시할 수 있게 한다.
- `app/api/documents.py`
  - `/documents/supported-types` 응답에 `pdf_ocr` 필드를 추가한다.
- `cli/`
  - `local-ai document-types` 출력에 OCR 상태를 표시한다.
  - CLI는 백엔드 응답을 그대로 보여주며 OCR 판정 로직을 중복 구현하지 않는다.
- 테스트
  - `tests/test_document_loader.py`
    - `pytesseract` import 실패 시 graceful skip을 검증한다.
    - `tesseract` binary 미설치 시 graceful skip을 검증한다.
    - OCR 성공 mock에서 PDF 텍스트 fallback 결과가 loader output에 포함되는지 검증한다.
    - PDF 페이지 텍스트가 정상 추출되면 OCR이 호출되지 않는지 검증한다.
    - PDF 페이지 텍스트가 비어 있고 image XObject 추출이 불가능하면 skip reason이 남는지 검증한다.
  - `tests/test_api_contracts.py` 또는 새 test file
    - `/documents/supported-types` 응답에 `pdf_ocr` 필드가 항상 포함되는지 검증한다.
    - OCR 미설치 환경에서도 endpoint가 실패하지 않는지 검증한다.
- 문서
  - `README.md`
    - "문서 업로드"에 OCR optional extra와 시스템 설치 안내를 추가한다.
    - "현재 한계"에 PyPDF image XObject 범위와 flat scan PDF 한계를 명시한다.
    - "Capability Boundary Matrix"에 OCR fallback 범위와 외부 OCR 금지를 명시한다.
  - `docs/API.md`
    - `/documents/supported-types` 응답 필드에 `pdf_ocr`를 추가한다.
  - `docs/PROJECT_SUMMARY.md`
    - "구현된 문서 타입" 또는 문서 지원 범위에 OCR fallback 상태를 추가한다.
  - `SECURITY.md`
    - "파일 업로드와 폴더 색인"에 OCR은 로컬 binary만 사용하고 이미지 bytes를 저장하지 않는다는 안전 기준을 추가한다.

## 테스트 계획

- `pytesseract` import 실패
  - loader가 서버 import를 깨지 않는다.
  - OCR 필요한 페이지는 graceful skip된다.
  - skip reason에는 Python OCR dependency 설치 안내가 포함된다.
- `tesseract` binary 없음
  - `/documents/supported-types`는 `pdf_ocr=false`를 반환한다.
  - OCR 필요한 업로드는 명확한 설치 안내 메시지를 제공한다.
- PDF 페이지 텍스트 정상 추출
  - 기존 PDF 텍스트 추출 결과를 사용한다.
  - OCR 함수는 호출되지 않는다.
- PDF 페이지 텍스트 빈 값 또는 threshold 이하, image XObject 추출 가능
  - OCR 함수가 호출된다.
  - OCR 결과 텍스트가 일반 텍스트와 같은 loader output으로 합쳐진다.
  - 이후 chunking, embedding, SQLite/Chroma 저장 경로는 기존 document pipeline을 그대로 사용한다.
- PDF 페이지 텍스트 빈 값 또는 threshold 이하, image XObject 추출 불가
  - 해당 페이지 OCR은 graceful skip된다.
  - skip reason이 `skipped_file_details` 또는 loader metadata에 남는다.

## Stage 3 진행 조건

- 이 문서가 commit/push된 뒤 사용자에게 구현 진행 승인을 받는다.
- 승인 전에는 `pyproject.toml`, loader, API, CLI, 테스트 코드를 변경하지 않는다.
- 승인 후 구현 단계마다 아래 검증을 실행한다.
  - `.venv/bin/pytest`
  - `.venv/bin/python scripts/local_ci_check.py --root .`
  - `git diff --check`
- 구현 완료 후 `docs/WORKLOG.md`, `docs/NEXT_CHAT_HANDOFF.md`, `docs/TASKS.md`를 갱신한다.

## 금지 사항

- 외부 LLM API 추가
- OpenAI, Claude, Gemini, cloud OCR, cloud vector DB 추가
- LangChain 추가
- Google Cloud Vision, AWS Textract 같은 cloud OCR 추가
- `pdf2image` 또는 `poppler` 의존성 추가
- 시스템 패키지 자동 설치
- shell, browser, file-write 실제 실행 활성화
- `AGENT_EXECUTION_ENABLED`, `AGENT_WEB_FETCH_ENABLED` 기본값 변경
- 운영 배포, cloud, Oracle 리소스 변경
- secret, API key, DB password 출력
