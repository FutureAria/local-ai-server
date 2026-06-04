from pathlib import Path


def test_next_chat_handoff_keeps_codex_tasks_safe() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert "브라우저 조작 없이" in text
    assert "Codex가 바로 이어서 할 수 있는 안전 작업" in text
    assert "사용자 수동 확인 또는 별도 승인 후에만 진행할 작업" in text
    assert "실제 브라우저 렌더링 확인" in text
    assert "사용자 승인 또는 수동 확인 전 진행 불가" in text


def test_next_chat_handoff_includes_current_verification_gates() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert ".venv/bin/pytest" in text
    assert "668 passed, 1 warning" in text
    assert ".venv/bin/python -m compileall app cli scripts" in text
    assert ".venv/bin/python scripts/public_release_check.py --root . --json" in text
    assert ".venv/bin/python scripts/local_ci_check.py --root ." in text
    assert "git diff --check" in text
    assert "source .venv/bin/activate" not in text
    assert "\npytest\n" not in text
    assert "\npython -m compileall app cli scripts\n" not in text
    assert "read-only-result-wrapper" in text
    assert "message(auto/status intent)" in text
    assert "message(status)" not in text


def test_next_chat_handoff_tracks_stage15_to_24_doc_contracts() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    for phrase in [
        "24차 Production Hardening 이후 계약 유지",
        "15차 NEXT_CHAT_HANDOFF와 Decision Required sync",
        "16차 Claude/Sonnet handoff and final report sync",
        "17차 public docs Decision Required link contract",
        "18차",
        "19차",
        "20차",
        "21차",
        "22차",
        "23차",
        "24차",
        "Production Hardening",
        "capabilities honesty",
        "tests/test_public_docs_contract.py::test_public_docs_surface_decision_required_link_set",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "668 passed, 1 warning",
    ]:
        assert phrase in text


def test_next_chat_handoff_links_release_and_ui_docs() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    for doc in [
        "docs/UI_BRIDGE_EXAMPLES.md",
        "docs/UI_CONNECT_GUIDE.md",
        "docs/UI_CONTRACT_CHEATSHEET.md",
        "docs/UI_QA_CHECKLIST.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/PUBLIC_RELEASE_SUMMARY.md",
        "docs/TASKS.md",
        "docs/USER_DOCUMENT_E2E_PLAN.md",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
    ]:
        assert doc in text


def test_next_chat_handoff_links_task_board_boundaries() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert "safe-next" in text
    assert "manual-check" in text
    assert "review-required" in text
    assert "blocked 작업 경계" in text


def test_next_chat_handoff_tracks_completed_real_user_document_e2e() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    assert "실제 사용자 문서 E2E는 완료됨" in text
    assert "완료된 실제 사용자 문서 E2E summary 정합성 유지" in text
    assert "추가 사용자 문서로 재검증이 필요하면 사용자 승인과 실제 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 경로를 받은 뒤 실행" in text


def test_next_chat_handoff_tracks_stage9_to_14_locked_preview_contracts() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    for phrase in [
        "9차 approval store",
        "10차 no-op dispatcher",
        "11차 read-only boundary preview",
        "12차 read-only adapter execution Decision Required",
        "13차 result wrapper schema",
        "14차 UI/smoke expected output",
        "assistant.action_loop.read_only_result_wrapper.v1",
        "raw content/approval-like JSON/next step mutation 승격 금지",
        "would_dispatch=false",
        "would_read=false",
        "would_fetch=false",
        "would_execute=false",
        "would_apply=false",
        "would_interact=false",
        "execution_enabled=false",
        "approval_consume_mode=validate-only",
    ]:
        assert phrase in text


def test_next_chat_handoff_tracks_runtime_snapshot_guard_tests() -> None:
    text = Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8")

    for phrase in [
        "README와 Project Summary의 `Runtime Contract Snapshot` 값을 실제 API/CLI/smoke flow inventory와 비교한다",
        "tests/test_tasks_doc.py",
        "tests/test_public_release_summary.py",
        "tests/test_portfolio_docs_contract.py",
        "tests/test_next_chat_handoff.py",
        "Runtime Contract Snapshot guard가 task board, release summary, portfolio docs, handoff에 남아 있는지 검증한다",
    ]:
        assert phrase in text


def test_next_chat_handoff_boundaries_match_task_board_and_public_docs() -> None:
    docs = {
        "README.md": Path("README.md").read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": Path("docs/PROJECT_SUMMARY.md").read_text(encoding="utf-8"),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8"),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(encoding="utf-8"),
    }

    shared_safe_terms = [
        "endpoint/response field 계약 테스트",
        "runtime endpoint count drift check",
        "README/Project Summary Runtime Contract Snapshot",
        "API/CLI/smoke flow inventory",
        "assistant bridge smoke expected output",
        "UI 수동 QA 체크리스트",
        "PDF OCR fallback",
        "`/documents/supported-types`",
    ]
    shared_manual_or_review_terms = [
        "실제 repair/delete/rebuild",
        "브라우저 click/fill/submit",
        "shell 실행",
        "파일 생성",
        "JavaScript 렌더링",
        "pdf2image/poppler",
        "운영 배포",
        "HTTPS termination",
        "다중 사용자",
        "분산 rate limit",
    ]

    for path, text in docs.items():
        for term in shared_safe_terms + shared_manual_or_review_terms:
            assert term in text, f"{path} missing shared boundary term: {term}"

    assert "사용자 승인 또는 Opus 리뷰가 필요한 작업" in docs["docs/NEXT_CHAT_HANDOFF.md"]
    assert "## 사용자 수동 확인 작업" in docs["docs/TASKS.md"]
    assert "## 별도 승인 또는 보안 리뷰가 필요한 작업" in docs["docs/TASKS.md"]
