import subprocess
from pathlib import Path

from app.main import app


README = Path("README.md")
PROJECT_SUMMARY = Path("docs/PROJECT_SUMMARY.md")
FINAL_REPORT = Path("docs/FINAL_REPORT.md")
SECURITY = Path("SECURITY.md")
CLAUDE_REVIEW_HANDOFF = Path("docs/CLAUDE_REVIEW_HANDOFF.md")
CODEX_IMPLEMENTATION_NOTES = Path("docs/CODEX_IMPLEMENTATION_NOTES.md")


def test_readme_includes_portfolio_story_without_overclaiming() -> None:
    text = README.read_text(encoding="utf-8")

    assert "## 포트폴리오 포인트" in text
    for phrase in [
        "백엔드 API 설계",
        "로컬 RAG 파이프라인 구현",
        "SQLite/Chroma 저장소 분리",
        "Typer CLI",
        "테스트/문서/보안 기준",
        "외부 LLM API 없이",
        "preview, dry-run, approval",
    ]:
        assert phrase in text

    assert "배포 완료" not in text
    assert "브라우저 클릭" in text


def test_project_summary_includes_portfolio_points_and_limits() -> None:
    text = PROJECT_SUMMARY.read_text(encoding="utf-8")

    assert "## 포트폴리오 포인트" in text
    assert "## 실행 가능 기능과 금지 기능" in text
    for phrase in [
        "담당 범위",
        "설계 포인트",
        "안정성 포인트",
        "검증 포인트",
        "한계 명시",
        "외부 LLM API",
        "운영 배포",
        "Agent execution v1",
        "조건부 read-only",
        "허용 root 폴더 목록 조회",
        "텍스트 preview",
        "명시 URL 단건 read-only fetch",
        "dry-run only",
        "브라우저 클릭/입력",
        "파일 생성/수정/삭제",
    ]:
        assert phrase in text


def test_project_summary_and_final_report_show_current_pytest_count() -> None:
    for path in [PROJECT_SUMMARY, FINAL_REPORT, CLAUDE_REVIEW_HANDOFF]:
        text = path.read_text(encoding="utf-8")
        assert "815 passed, 1 warning" in text
        assert "814 passed, 1 warning" not in text
        assert "813 passed, 1 warning" not in text
        assert "812 passed, 1 warning" not in text
        assert "811 passed, 1 warning" not in text
        assert "810 passed, 1 warning" not in text
        assert "809 passed, 1 warning" not in text
        assert "808 passed, 1 warning" not in text
        assert "807 passed, 1 warning" not in text
        assert "806 passed, 1 warning" not in text
        assert "805 passed, 1 warning" not in text
        assert "804 passed, 1 warning" not in text
        assert "803 passed, 1 warning" not in text
        assert "802 passed, 1 warning" not in text
        assert "801 passed, 1 warning" not in text
        assert "800 passed, 1 warning" not in text
        assert "791 passed, 1 warning" not in text
        assert "790 passed, 1 warning" not in text
        assert "789 passed, 1 warning" not in text
        assert "780 passed, 1 warning" not in text
        assert "778 passed, 1 warning" not in text
        assert "776 passed, 1 warning" not in text
        assert "774 passed, 1 warning" not in text
        assert "772 passed, 1 warning" not in text
        assert "770 passed, 1 warning" not in text
        assert "768 passed, 1 warning" not in text
        assert "767 passed, 1 warning" not in text
        assert "766 passed, 1 warning" not in text
        assert "765 passed, 1 warning" not in text
        assert "623 passed, 1 warning" not in text
        assert "596 passed" not in text
        assert "276 passed" not in text
        assert "298 passed" not in text


def test_summary_and_final_report_test_commands_match_baseline() -> None:
    required_commands = [
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
        ".venv/bin/python scripts/local_ci_check.py --root .",
    ]

    for path in [PROJECT_SUMMARY, FINAL_REPORT]:
        text = path.read_text(encoding="utf-8")
        marker = "## 테스트 실행 방법" if path == PROJECT_SUMMARY else "## 5. 테스트 실행 방법"
        test_section = text.split(marker, 1)[1].split("현재 검증 상태:", 1)[0]
        for command in required_commands:
            assert command in test_section, f"{path} missing verification command: {command}"


def test_public_docs_use_json_public_release_check_command() -> None:
    for path in [README, PROJECT_SUMMARY, FINAL_REPORT, SECURITY, CLAUDE_REVIEW_HANDOFF]:
        text = path.read_text(encoding="utf-8")
        assert ".venv/bin/python scripts/public_release_check.py --root . --json" in text
        assert ".venv/bin/python scripts/public_release_check.py --root .`" not in text
        assert ".venv/bin/python scripts/public_release_check.py --root .:" not in text


def test_claude_review_handoff_separates_sonnet_and_opus_review_scope() -> None:
    text = CLAUDE_REVIEW_HANDOFF.read_text(encoding="utf-8")

    for phrase in [
        "Claude Sonnet",
        "문서 정합성 리뷰",
        "Claude Opus Escalation Prompt",
        "Claude Opus 보안/아키텍처 리뷰어",
        "실제 action-loop dispatch",
        "read-only adapter execution",
        "approval consume mode",
        "shell/patch/browser 실행",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "P0/P1/P2 findings",
        "Decision Required",
        "Codex Follow-up Prompt",
        "Recommended Next Model",
        "execution_enabled=false",
    ]:
        assert phrase in text


def test_codex_implementation_notes_capture_stage9_to_18_self_review() -> None:
    text = CODEX_IMPLEMENTATION_NOTES.read_text(encoding="utf-8")

    for phrase in [
        "9-18차 locked/preview 작업",
        "Codex self-review",
        "서버 발급 approval store",
        "no-op dispatcher",
        "read-only dispatch boundary preview",
        "read-only result wrapper schema",
        "public docs Decision Required link contract",
        "NEXT_CHAT_HANDOFF를 17차 최신 상태",
        "실제 action-loop dispatch는 활성화하지 않았다",
        "실제 read-only adapter execution",
        "실제 shell subprocess 실행은 활성화하지 않았다",
        "실제 patch apply",
        "실제 browser/app interaction은 활성화하지 않았다",
        "would_dispatch=false",
        "would_read=false",
        "would_fetch=false",
        "would_execute=false",
        "would_apply=false",
        "would_interact=false",
        "execution_enabled=false",
        "client-supplied approval-like JSON",
        "raw content",
        "623 passed, 1 warning",
        "Commit-Ready Diff Review",
        "Assistant service/API/schema",
        "CLI/REPL",
        "Decision docs",
        "Handoff/review docs",
        "UI docs",
        "git diff --check",
        "scanned_files=127",
        "untracked docs 4개는 의도된 신규 문서",
        "commit message는 locked/preview 안전 계약",
        "Commit Message Draft",
        "Harden assistant locked-preview safety contracts",
        "keep shell, patch, browser/app, dispatch, read-only adapter execution, and external API activation disabled",
        "Staging 전 체크리스트",
        "사용자에게 staging/commit 진행 의사를 확인",
        "Decision Required",
        "Claude Opus 보안/아키텍처 리뷰",
    ]:
        assert phrase in text


def test_codex_implementation_notes_capture_stage50_commit_readiness_review() -> None:
    text = CODEX_IMPLEMENTATION_NOTES.read_text(encoding="utf-8")

    for phrase in [
        "50차 Full Automation Commit-readiness / Cumulative Diff Review",
        "1~49차 누적 변경",
        "runtime/API route",
        "schema/config",
        "service layer",
        "CLI/REPL",
        "smoke/public release scripts",
        "tests",
        "public/security docs",
        "Decision Required docs",
        "handoff/review docs",
        "UI/smoke docs",
        "untracked docs 5개는 의도된 신규 문서",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/CODEX_IMPLEMENTATION_NOTES.md",
        "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "external provider 확장",
        "git reset/bulk restore",
        "755 passed, 1 warning",
        "scanned_files=128",
        "git diff --check",
        "local CI",
        "Commit-readiness conclusion",
    ]:
        assert phrase in text


def test_stage51_final_docs_sync_freezes_latest_public_verification_snapshot() -> None:
    docs = {
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "docs/FINAL_REPORT.md": FINAL_REPORT.read_text(encoding="utf-8"),
        "docs/CLAUDE_REVIEW_HANDOFF.md": CLAUDE_REVIEW_HANDOFF.read_text(encoding="utf-8"),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(encoding="utf-8"),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "51차 Full Automation Final Docs Sync / Handoff Freeze",
        "761 passed, 1 warning",
        "scanned_files=128",
        "Full Automation Commit-readiness / Cumulative Diff Review",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
    ]:
        assert phrase in combined

    for path, text in docs.items():
        if path in {
            "docs/PROJECT_SUMMARY.md",
            "docs/FINAL_REPORT.md",
            "docs/CLAUDE_REVIEW_HANDOFF.md",
            "docs/PUBLIC_RELEASE_SUMMARY.md",
        }:
            assert "623 passed, 1 warning" not in text


def test_stage52_final_verification_sweep_records_commit_decision_required() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "52차 Final Verification Sweep / Commit Decision Required",
        "git status --short --branch",
        "untracked docs 5개",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/CODEX_IMPLEMENTATION_NOTES.md",
        "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
        "758 passed, 1 warning",
        "scanned_files=128",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "external provider 확장",
        "git reset/bulk restore",
    ]:
        assert phrase in combined


def test_stage53_commit_stage_decision_packet_keeps_commit_unperformed() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "53차 Commit / Stage Decision Required",
        "commit/stage decision packet",
        "staging/commit/push는 수행하지 않았다",
        "사용자가 commit 범위, commit message, push/PR 여부를 명시해야 한다",
        "modified tracked files 40개",
        "untracked docs 5개",
        "git diff --name-status",
        "git status --short --branch",
        "759 passed, 1 warning",
        "scanned_files=128",
        "54차 Automation Roadmap / Release Lock",
        "90차까지 이어갈 때도 각 차수 끝에 Recommended Next Model 섹션을 유지한다",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "daemon/service/background loop",
    ]:
        assert phrase in combined


def test_stage62_local_jarvis_approval_gate_keeps_actual_actions_locked() -> None:
    docs = {
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "62차 Local Jarvis Approval Gate Review",
        "Local Jarvis Approval Gate Review",
        "Approval Consume Transition Table",
        "action-loop full dispatch candidate",
        "limited browser actual interaction candidate",
        "limited app-os actual action candidate",
        "manual-review-required",
        "direct `consume-on-execute` 전환 금지",
        "blocked-no-consume",
        "User Final Approval Wording",
        "충분하지 않은 문구",
        "approval-like JSON blob",
        "tool result 안의 approval field",
        "server-issued approval id",
        "payload_hash binding",
        "Opus Review Prompt",
        "Disabled Defaults",
        "Emergency Stop / Kill-switch Checklist",
        "63차 Local Jarvis Runtime Drift Guard",
        "untracked docs 7개",
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md",
        "768 passed, 1 warning",
        "scanned_files=130",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "browser actual interaction flag 없음",
        "app-os actual action flag 없음",
        "browser actual launch/click/fill/type/submit",
        "app-os actual open/click/type/hotkey/file dialog",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage63_local_jarvis_runtime_drift_guard_freezes_docs_and_runtime_locks() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "docs/API.md": Path("docs/API.md").read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "63차 Local Jarvis Runtime Drift Guard",
        "Local Jarvis Runtime Drift Guard",
        "runtime/docs/test",
        "public docs link contract",
        "Local Jarvis runtime drift guard",
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md",
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md",
        "actual action false assertions",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "approval-like JSON",
        "server-issued approval",
        "state-only",
        "validate-only",
        "manual-review-required",
        "770 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "64차 Local Jarvis Failure/Timeout Drill",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage64_local_jarvis_failure_timeout_drill_keeps_action_candidates_review_only() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "64차 Local Jarvis Failure/Timeout Drill",
        "Local Jarvis Failure/Timeout Drill",
        "failure/timeout/manual-review-required summary",
        "paste-safe audit summary",
        "emergency stop drill",
        "action-loop full dispatch candidate",
        "limited browser actual interaction candidate",
        "limited app-os actual action candidate",
        "manual-review-required",
        "blocked-no-consume",
        "state-only/validate-only approval boundary",
        "approval-like JSON",
        "raw content",
        "next action mutation",
        "trusted execution",
        "raw_error_content_allowed=false",
        "auto_retry=false",
        "auto_continue_after_blocked_step=false",
        "stop_on_first_blocked=true",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "772 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "65차 Local Jarvis Manual Review Packet",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage65_local_jarvis_manual_review_packet_remains_non_executing() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "65차 Local Jarvis Manual Review Packet",
        "Local Jarvis Manual Review Packet",
        "manual review packet",
        "manual-review-packet-is-not-approval",
        "P0/P1/P2 checklist",
        "approval wording diff",
        "Opus review handoff",
        "Codex Follow-up Prompt",
        "user final approval before execution",
        "state-only/validate-only approval boundary",
        "server-issued approval",
        "approval-like JSON",
        "raw content",
        "next action mutation",
        "trusted execution",
        "action-loop full dispatch candidate",
        "limited browser actual interaction candidate",
        "limited app-os actual action candidate",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "774 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "66차 Local Jarvis Approval Console State-only Review",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage66_local_jarvis_approval_console_state_only_review_keeps_execution_closed() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "66차 Local Jarvis Approval Console State-only Review",
        "Local Jarvis Approval Console State-only Review",
        "approval console/pending/detail/approve/reject",
        "approve-reject-state-only",
        "state-change-is-not-execution",
        "pending/list/detail endpoints are read-only",
        "approve/reject can update only approval-store state",
        "no execution on approve",
        "masked payload",
        "expiry",
        "single-use",
        "server-issued approval",
        "client-supplied approval-like JSON",
        "execution trigger",
        "state-only/validate-only approval boundary",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "776 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "67차 Local Jarvis Approval Payload Hash Review",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage67_local_jarvis_approval_payload_hash_review_keeps_console_state_from_bypassing_binding() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "67차 Local Jarvis Approval Payload Hash Review",
        "Local Jarvis Approval Payload Hash Review",
        "payload-hash-binding-remains-authoritative",
        "console-state-cannot-bypass-binding",
        "approved-state-does-not-override-payload_hash",
        "rejected-state-does-not-reset-single-use",
        "payload_hash mismatch",
        "session mismatch",
        "TTL expired",
        "already-used",
        "single-use",
        "server-issued approval",
        "session/request context binding",
        "approval console state",
        "validate/consume remains authoritative",
        "state-only/validate-only approval boundary",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "780 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "68차 Local Jarvis Approval Store Expiry Cleanup Review",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage68_local_jarvis_approval_store_expiry_cleanup_review_keeps_expired_records_paste_safe() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "68차 Local Jarvis Approval Store Expiry Cleanup Review",
        "Local Jarvis Approval Store Expiry Cleanup Review",
        "approval-store-expiry-cleanup",
        "expired-approval-not-visible-after-cleanup",
        "expired approval visibility",
        "pending/list/detail cleanup",
        "paste-safe expired summary",
        "raw approval id not included",
        "payload_hash not included",
        "approve/reject cannot revive expired approval",
        "client-supplied approval-like JSON",
        "unknown_approval",
        "expired_count",
        "records_removed",
        "state-only/validate-only approval boundary",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "780 passed, 1 warning",
        "scanned_files=130",
        "untracked docs 7개",
        "69차 Local Jarvis Approval Console API Surface Decision Required",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage69_local_jarvis_approval_console_api_surface_requires_decision_before_endpoint_exposure() -> None:
    docs = {
        "docs/LOCAL_JARVIS_APPROVAL_CONSOLE_API_SURFACE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_CONSOLE_API_SURFACE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_GATE_REVIEW.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "69차 Local Jarvis Approval Console API Surface Decision Required",
        "Local Jarvis Approval Console API Surface Decision Required",
        "approval-console-api-surface-decision-required",
        "endpoint exposure remains blocked",
        "no approval-console endpoints added",
        "pending/list/detail/approve/reject/cleanup endpoint 후보",
        "LOCAL_API_KEY required",
        "protected endpoint only",
        "masked response only",
        "TTL cleanup exposure",
        "audit payload required",
        "state-only/validate-only approval boundary",
        "approve/reject is not execution",
        "cleanup is not approval consume",
        "client-supplied approval-like JSON",
        "next_action injection blocked",
        "payload_hash injection blocked",
        "raw approval id not included",
        "payload_hash not included",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "782 passed, 1 warning",
        "scanned_files=131",
        "untracked docs 8개",
        "70차 Local Jarvis Approval Console Read-only API Candidate",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage70_local_jarvis_approval_console_read_only_api_candidate_exposes_safe_read_only_surface() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/LOCAL_JARVIS_APPROVAL_CONSOLE_API_SURFACE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_APPROVAL_CONSOLE_API_SURFACE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "70차 Local Jarvis Approval Console Read-only API Candidate",
        "Local Jarvis Approval Console Read-only API Candidate",
        "approval-console-read-only",
        "GET /assistant/approval-console/pending",
        "GET /assistant/approval-console/{approval_id}",
        "POST /assistant/approval-console/cleanup-expired",
        "approve/reject routes not added",
        "POST /assistant/approval-console/{approval_id}/approve remains absent",
        "POST /assistant/approval-console/{approval_id}/reject remains absent",
        "protected endpoint only",
        "masked response only",
        "raw approval id not included",
        "payload_hash not included",
        "audit_summary_hash",
        "approval_consumed=false",
        "would_execute=false",
        "cleanup is not approval consume",
        "read-only pending/list/detail/cleanup",
        "FastAPI endpoints 93",
        "protected endpoints 77",
        "public endpoints 16",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "788 passed, 1 warning",
        "scanned_files=131",
        "untracked docs 8개",
        "71차 Durable Automation v2 Candidate Decision Required",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage71_durable_automation_v2_candidate_requires_decision_before_worker_or_replay() -> None:
    docs = {
        "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "71차 Durable Automation v2 Candidate Decision Required",
        "Durable Automation v2 Candidate Decision Required",
        "durable-automation-v2-candidate-decision-required",
        "persistence/recovery/replay boundary",
        "approval/audit lock",
        "durable task persistence",
        "replay queue",
        "recovery checkpoint",
        "decision-required",
        "no durable worker started",
        "no scheduler started",
        "no daemon/service/background loop",
        "no automatic replay",
        "no autonomous recovery",
        "replay_candidate is dry-run first",
        "replay_does_not_consume_approval",
        "replay_does_not_dispatch_connector",
        "manual_review_required=true",
        "stop_on_first_blocked=true",
        "would_start_worker=false",
        "would_schedule=false",
        "would_replay=false",
        "would_recover=false",
        "would_dispatch=false",
        "approval_consumed=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "server-issued approval id",
        "single-use",
        "TTL",
        "session/request context binding",
        "payload_hash binding",
        "client-supplied approval-like JSON rejected",
        "approval console state cannot override payload_hash",
        "cleanup is not approval consume",
        "789 passed, 1 warning",
        "scanned_files=132",
        "untracked docs 9개",
        "72차 Durable State Preview Schema Candidate",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage72_durable_state_preview_schema_candidate_remains_schema_only() -> None:
    docs = {
        "docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md": Path(
            "docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md"
        ).read_text(encoding="utf-8"),
        "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/DURABLE_AUTOMATION_V2_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "72차 Durable State Preview Schema Candidate",
        "Durable State Preview Schema Candidate",
        "durable-state-preview-schema-candidate",
        "proposal-only contract",
        "schema-only",
        "state_schema_version=durable_state_preview.v1",
        "preview_state_id",
        "state_status=candidate-preview",
        "owner/session/request context binding",
        "payload_hash binding",
        "masked params only",
        "no raw secrets",
        "no raw approval id",
        "payload_hash not included",
        "audit_summary_hash",
        "no durable storage migration",
        "no durable table created",
        "no queue worker started",
        "no scheduler started",
        "no daemon/service/background loop",
        "no automatic replay",
        "no autonomous recovery",
        "state_preview_is_not_execution",
        "state_preview_does_not_consume_approval",
        "state_preview_does_not_mutate_queue",
        "would_persist=false",
        "would_start_worker=false",
        "would_schedule=false",
        "would_replay=false",
        "would_recover=false",
        "would_dispatch=false",
        "approval_consumed=false",
        "manual_review_required=true",
        "stop_on_first_blocked=true",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "client-supplied approval-like JSON rejected",
        "approval console state cannot override payload_hash",
        "cleanup is not approval consume",
        "790 passed, 1 warning",
        "scanned_files=133",
        "untracked docs 10개",
        "73차 Durable State Preview API Surface Decision Required",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage73_durable_state_preview_api_surface_requires_decision_before_endpoint_exposure() -> None:
    docs = {
        "docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md": Path(
            "docs/DURABLE_STATE_PREVIEW_API_SURFACE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md": Path(
            "docs/DURABLE_STATE_PREVIEW_SCHEMA_CANDIDATE.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "73차 Durable State Preview API Surface Decision Required",
        "Durable State Preview API Surface Decision Required",
        "durable-state-preview-api-surface-decision-required",
        "endpoint exposure remains blocked",
        "no durable-state-preview endpoints added",
        "POST /assistant/durable-state-preview/preview",
        "GET /assistant/durable-state-preview/{preview_state_id}",
        "POST /assistant/durable-state-preview/cleanup-expired",
        "POST /assistant/durable-state-preview/preview remains absent",
        "GET /assistant/durable-state-preview/{preview_state_id} remains absent",
        "GET /assistant/durable-state-preview remains absent",
        "POST /assistant/durable-state-preview/cleanup-expired remains absent",
        "LOCAL_API_KEY required",
        "protected endpoint only",
        "read-only/schema-only response",
        "masked response only",
        "raw approval id not included",
        "payload_hash not included",
        "audit_summary_hash required",
        "state_schema_version=durable_state_preview.v1",
        "state_status=candidate-preview",
        "owner/session/request context binding",
        "payload_hash binding",
        "state_preview_is_not_execution",
        "state_preview_does_not_consume_approval",
        "state_preview_does_not_mutate_queue",
        "endpoint_candidate_is_not_exposure",
        "route_absence_is_required",
        "would_expose_endpoint=false",
        "would_persist=false",
        "would_start_worker=false",
        "would_schedule=false",
        "would_replay=false",
        "would_recover=false",
        "would_dispatch=false",
        "approval_consumed=false",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "client-supplied approval-like JSON rejected",
        "approval console state cannot override payload_hash",
        "cleanup is not approval consume",
        "791 passed, 1 warning",
        "scanned_files=134",
        "untracked docs 11개",
        "74차 Durable State Preview Read-only API Candidate",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined

    route_paths = {getattr(route, "path", "") for route in app.routes}
    for path in [
        "/assistant/durable-state-preview/{preview_state_id}",
        "/assistant/durable-state-preview",
        "/assistant/durable-state-preview/cleanup-expired",
    ]:
        assert path not in route_paths


def test_stage74_durable_state_preview_read_only_api_candidate_is_response_only() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
        "docs/API.md": Path("docs/API.md").read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "74차 Durable State Preview Read-only API Candidate",
        "Durable State Preview Read-only API Candidate",
        "POST /assistant/durable-state-preview/preview",
        "durable-state-preview-read-only",
        "response-only/read-only/schema-only",
        "state_schema_version=durable_state_preview.v1",
        "state_status=candidate-preview",
        "protected endpoint only",
        "LOCAL_API_KEY",
        "masked response only",
        "raw approval id not included",
        "payload_hash not included",
        "audit_summary_hash",
        "stored preview lookup/list/cleanup remain Decision Required",
        "GET /assistant/durable-state-preview/{preview_state_id} remains absent",
        "GET /assistant/durable-state-preview remains absent",
        "POST /assistant/durable-state-preview/cleanup-expired remains absent",
        "stored_preview_lookup_connected=false",
        "stored_preview_list_connected=false",
        "stored_preview_cleanup_connected=false",
        "would_execute=false",
        "would_persist=false",
        "would_dispatch=false",
        "approval_consumed=false",
        "durable_storage_migration_connected=false",
        "durable_table_created=false",
        "persistence_mutation_connected=false",
        "queue_mutation_connected=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "untracked docs 11개",
        "75차 Durable State Preview API Regression Guard",
        "staging/commit/push",
    ]:
        assert phrase in combined

    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/assistant/durable-state-preview/preview" in route_paths
    for path in [
        "/assistant/durable-state-preview/{preview_state_id}",
        "/assistant/durable-state-preview",
        "/assistant/durable-state-preview/cleanup-expired",
    ]:
        assert path not in route_paths


def test_stage75_durable_state_preview_api_regression_guard_locks_route_and_redaction_drift() -> None:
    docs = {
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
        "docs/API.md": Path("docs/API.md").read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "75차 Durable State Preview API Regression Guard",
        "Durable State Preview API Regression Guard",
        "route inventory drift",
        "nested sensitive key redaction",
        "candidate_steps",
        "metadata",
        "approval_id",
        "approval_payload_hash",
        "payload_hash",
        "token",
        "password",
        "[REDACTED]",
        "raw value",
        "absent stored preview routes",
        "no persistence mutation",
        "no approval consume",
        "no queue mutation",
        "POST /assistant/durable-state-preview/preview",
        "GET /assistant/durable-state-preview/{preview_state_id}",
        "GET /assistant/durable-state-preview",
        "POST /assistant/durable-state-preview/cleanup-expired",
        "stored_preview_lookup_connected=false",
        "stored_preview_list_connected=false",
        "stored_preview_cleanup_connected=false",
        "persistence_mutation_connected=false",
        "queue_mutation_connected=false",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "76차 Durable State Preview Docs/API Drift Guard",
        "action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "staging/commit/push",
    ]:
        assert phrase in combined

    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/assistant/durable-state-preview/preview" in route_paths
    for path in [
        "/assistant/durable-state-preview/{preview_state_id}",
        "/assistant/durable-state-preview",
        "/assistant/durable-state-preview/cleanup-expired",
    ]:
        assert path not in route_paths


def test_stage76_durable_state_preview_docs_api_drift_guard_locks_public_docs_contract() -> None:
    docs = {
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
        "docs/API.md": Path("docs/API.md").read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "76차 Durable State Preview Docs/API Drift Guard",
        "Durable State Preview Docs/API Drift Guard",
        "API docs response fields",
        "public docs endpoint listing",
        "security boundary",
        "release summary",
        "handoff",
        "AssistantDurableStatePreviewResponse",
        "POST /assistant/durable-state-preview/preview",
        "protected endpoint only",
        "response-only/read-only/schema-only",
        "stored preview lookup/list/cleanup route",
        "stored preview lookup/list/cleanup route absent",
        "no persistence mutation",
        "no approval consume",
        "no queue mutation",
        "nested sensitive key redaction",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "77차 Durable State Preview Release-lock Guard",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage77_durable_state_preview_release_lock_guard_freezes_cumulative_diff_and_verification() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "77차 Durable State Preview Release-lock Guard",
        "Durable State Preview Release-lock Guard",
        "74~76차 durable-state-preview 누적 diff",
        "release-lock",
        "POST /assistant/durable-state-preview/preview",
        "stored preview lookup/list/cleanup route",
        "route absent",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "802 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "staging/commit/push 미수행",
        "durable storage migration",
        "queue worker",
        "automatic replay",
        "action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "78차 Durable State Preview Final Verification Sweep",
    ]:
        assert phrase in combined


def test_stage78_durable_state_preview_final_verification_sweep_freezes_release_lock_status() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "78차 Durable State Preview Final Verification Sweep",
        "Durable State Preview Final Verification Sweep",
        "74~77차 durable-state-preview release-lock 구간",
        "final verification sweep",
        "POST /assistant/durable-state-preview/preview",
        "stored preview lookup/list/cleanup route",
        "route는 계속 absent",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "803 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "78차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "durable storage migration",
        "queue worker",
        "automatic replay",
        "action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "79차 Durable State Preview Handoff/Commit Readiness Packet",
    ]:
        assert phrase in combined


def test_stage79_durable_state_preview_handoff_commit_readiness_packet_freezes_stage_decision() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "79차 Durable State Preview Handoff/Commit Readiness Packet",
        "Durable State Preview Handoff/Commit Readiness Packet",
        "74~78차 durable-state-preview 누적 변경",
        "commit-readiness packet",
        "route/API/schema/service/docs/tests 영향 범위",
        "변경 파일 inventory",
        "runtime route/API/service/schema",
        "public/security/API docs",
        "release/handoff/task/worklog docs",
        "regression tests",
        "existing untracked Decision Required/schema docs",
        "POST /assistant/durable-state-preview/preview",
        "stored preview lookup/list/cleanup route",
        "route는 계속 absent",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "804 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "79차에서 새 untracked doc은 추가하지 않았다",
        "stage/commit/push Decision Required",
        "staging/commit/push는 수행하지 않았다",
        "검증 완료, stage/commit/push는 Decision Required",
        "durable storage migration",
        "queue worker",
        "automatic replay",
        "action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "80차 Durable Automation v2 Release-lock Final Decision Packet",
    ]:
        assert phrase in combined


def test_stage80_durable_automation_v2_release_lock_final_decision_packet_freezes_boundary() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "80차 Durable Automation v2 Release-lock Final Decision Packet",
        "Durable Automation v2 Release-lock Final Decision Packet",
        "71~79차 Durable Automation v2 Candidate 구간",
        "release-lock final decision packet",
        "durable automation v2 candidate",
        "durable state preview schema/API/read-only endpoint",
        "API regression guard",
        "docs/API drift guard",
        "release-lock guard",
        "final verification sweep",
        "handoff/commit-readiness packet",
        "opened scope",
        "POST /assistant/durable-state-preview/preview",
        "protected response-only/read-only/schema-only endpoint 하나",
        "blocked scope",
        "stored preview lookup/list/cleanup route",
        "route는 계속 absent",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "805 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "80차에서 새 untracked doc은 추가하지 않았다",
        "Durable Automation v2는 release-lock 완료, actual durable execution은 Decision Required",
        "staging/commit/push는 수행하지 않았다",
        "durable storage migration",
        "queue worker",
        "automatic replay",
        "action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "81차 Personal Automation Hardening Candidate Entry Decision",
    ]:
        assert phrase in combined


def test_stage81_personal_automation_hardening_entry_decision_freezes_actual_action_gate() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "81차 Personal Automation Hardening Candidate Entry Decision",
        "Personal Automation Hardening Candidate Entry Decision",
        "81~90차 Personal Automation Hardening Candidate 구간",
        "entry decision",
        "personal automation hardening candidate",
        "user final approval gate",
        "Opus review gate",
        "actual action prohibition",
        "safe-next/review-required/blocked boundary",
        "candidate/Decision Required 단계",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "external provider expansion",
        "persistent browser profile/session mutation",
        "file dialog/download/upload",
        "payment/login/delete/sensitive input",
        "app-os connector dispatch",
        "review-required 또는 blocked",
        "docs/test drift guard",
        "release summary sync",
        "public release scanner clean",
        "endpoint count drift check",
        "paste-safe audit wording",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "806 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "81차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "82차 Personal Automation Approval/Opus Gate Matrix",
    ]:
        assert phrase in combined


def test_stage82_personal_automation_approval_opus_gate_matrix_freezes_connector_gates() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "82차 Personal Automation Approval/Opus Gate Matrix",
        "Personal Automation Approval/Opus Gate Matrix",
        "user final approval gate",
        "Opus review gate",
        "connector별 blocked/review-required matrix",
        "사용자 명시 승인",
        "범위",
        "connector",
        "payload",
        "rollback/stop 조건",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "external provider expansion",
        "persistent profile/session mutation",
        "payment/login/delete/sensitive input",
        "shell/patch/rollback/task/browser/external/app-os/action-loop full dispatch",
        "blocked 또는 review-required",
        "docs/test drift guard",
        "release summary sync",
        "public release scanner clean",
        "endpoint count drift check",
        "approval-like JSON",
        "approved console state",
        "manual review packet",
        "execution approval로 승격할 수 없다",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "807 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "82차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "83차 Personal Automation Failure/Stop Hardening Matrix",
    ]:
        assert phrase in combined


def test_stage83_personal_automation_failure_stop_hardening_matrix_freezes_stop_policy() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "83차 Personal Automation Failure/Stop Hardening Matrix",
        "Personal Automation Failure/Stop Hardening Matrix",
        "stop-on-first-blocked",
        "emergency stop",
        "timeout/failure paste-safe summary",
        "auto_retry=false",
        "raw_error_content_allowed=false",
        "approval revive blocked",
        "connector 재실행 금지",
        "validation failure",
        "approval mismatch",
        "timeout",
        "wrapper trust failure",
        "blocked connector",
        "review-required connector",
        "secret masking",
        "path masking",
        "approval id masking",
        "payload_hash not included",
        "raw tool output not included",
        "approval-like JSON",
        "approved console state",
        "manual review packet",
        "execution approval로 승격할 수 없다",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "808 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "83차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "84차 Personal Automation Audit/Observability Hardening",
    ]:
        assert phrase in combined


def test_stage84_personal_automation_audit_observability_hardening_freezes_reporting_boundary() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "84차 Personal Automation Audit/Observability Hardening",
        "Personal Automation Audit/Observability Hardening",
        "audit_summary_hash",
        "masked audit event",
        "observability redaction",
        "operator-facing paste-safe reporting",
        "raw approval id",
        "raw payload_hash",
        "raw command",
        "raw selector",
        "raw URL query",
        "raw file path",
        "event_type",
        "connector_category",
        "decision",
        "blocked_reason_code",
        "safety_flags",
        "elapsed_ms",
        "retry_allowed=false",
        "approval_consumed=false",
        "secret redaction",
        "local path redaction",
        "URL query redaction",
        "selector/value redaction",
        "approval id redaction",
        "payload hash redaction",
        "user_action_required",
        "next_safe_step",
        "review_required_reason",
        "stop_condition",
        "opened_scope",
        "still_disabled_scope",
        "raw tool output",
        "raw stderr/stdout",
        "raw exception",
        "raw payload",
        "execution approval",
        "approval consume",
        "connector dispatch",
        "durable persistence mutation",
        "queue mutation",
        "browser/app-os actual action",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "809 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "84차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "85차 Personal Automation Session/Context Binding Review",
    ]:
        assert phrase in combined


def test_stage85_personal_automation_session_context_binding_review_freezes_context_boundary() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "85차 Personal Automation Session/Context Binding Review",
        "Personal Automation Session/Context Binding Review",
        "session/request context binding",
        "operator-visible context boundary",
        "cross-session approval reuse blocked",
        "session_id",
        "request_id",
        "operator_context_id",
        "payload_summary_hash",
        "approval",
        "payload",
        "audit event",
        "candidate step",
        "durable state preview",
        "approval id",
        "approval-like JSON",
        "approved console state",
        "manual review packet",
        "unknown_or_mismatched_context",
        "raw session token",
        "raw request body",
        "raw approval id",
        "raw payload_hash",
        "raw local path",
        "raw browser profile/session identifier",
        "paste-safe context summary",
        "masked_session_ref",
        "masked_request_ref",
        "operator_context_label",
        "context_binding_status",
        "context_mismatch_reason",
        "next_safe_step",
        "context mismatch",
        "approval consume",
        "connector dispatch",
        "durable persistence mutation",
        "queue mutation",
        "browser actual interaction",
        "app-os actual action",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "810 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "85차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "86차 Personal Automation Operator Confirmation Boundary",
    ]:
        assert phrase in combined


def test_stage86_personal_automation_operator_confirmation_boundary_freezes_human_action_gate() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "86차 Personal Automation Operator Confirmation Boundary",
        "Personal Automation Operator Confirmation Boundary",
        "operator confirmation wording",
        "final human action boundary",
        "confirmation-is-not-execution",
        "확인했습니다",
        "승인합니다",
        "진행해도 됩니다",
        "검토 상태 전환",
        "browser actual click/fill/type/submit/login/payment/delete/download/upload/file dialog",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "external provider expansion",
        "staging/commit/push",
        "confirmation state",
        "approval consume",
        "connector dispatch",
        "durable persistence mutation",
        "queue mutation",
        "browser actual interaction",
        "operator-facing confirmation summary",
        "confirmation_label",
        "confirmation_scope",
        "human_final_action_required",
        "review_required_before_execution",
        "blocked_actual_action_scope",
        "next_safe_step",
        "raw approval id",
        "raw payload_hash",
        "raw command",
        "raw selector",
        "raw local path",
        "raw browser session/profile identifier",
        "raw external provider credential",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "811 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "86차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "87차 Personal Automation Manual Review Packet Finalization",
    ]:
        assert phrase in combined


def test_stage87_personal_automation_manual_review_packet_finalization_freezes_packet_boundary() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "87차 Personal Automation Manual Review Packet Finalization",
        "Personal Automation Manual Review Packet Finalization",
        "manual review packet 최종 형식",
        "escalation boundary",
        "packet-is-not-approval",
        "packet_id",
        "packet_schema_version",
        "risk_summary",
        "requested_scope",
        "connector_scope",
        "approval_requirements",
        "opus_review_required",
        "operator_confirmation_required",
        "final_human_action_required",
        "blocked_actual_action_scope",
        "next_safe_step",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "external provider expansion",
        "persistent browser profile/session mutation",
        "payment/login/delete/sensitive input",
        "staging/commit/push",
        "user final approval",
        "Opus review",
        "approval-like JSON",
        "approved console state",
        "confirmation state",
        "audit event",
        "context mismatch",
        "execution approval로 승격할 수 없다",
        "approval consume",
        "connector dispatch",
        "durable persistence mutation",
        "queue mutation",
        "raw approval id",
        "raw payload_hash",
        "raw command",
        "raw selector",
        "raw local path",
        "raw browser session/profile identifier",
        "raw external provider credential",
        "POST /assistant/durable-state-preview/preview",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "812 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "87차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "88차 Personal Automation Release-lock Drift Guard",
    ]:
        assert phrase in combined


def test_stage88_personal_automation_release_lock_drift_guard_freezes_cumulative_boundary() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "88차 Personal Automation Release-lock Drift Guard",
        "Personal Automation Release-lock Drift Guard",
        "81~87차 Personal Automation Hardening 누적 경계",
        "release-lock drift guard",
        "Personal Automation Hardening Candidate Entry Decision",
        "Approval/Opus Gate Matrix",
        "Failure/Stop Hardening Matrix",
        "Audit/Observability Hardening",
        "Session/Context Binding Review",
        "Operator Confirmation Boundary",
        "Manual Review Packet Finalization",
        "user final approval gate",
        "Opus review gate",
        "connector별 blocked/review-required matrix",
        "stop-on-first-blocked",
        "emergency stop",
        "timeout/failure paste-safe summary",
        "audit_summary_hash",
        "masked audit event",
        "session/request context binding",
        "final human action boundary",
        "packet-is-not-approval",
        "POST /assistant/durable-state-preview/preview",
        "still-disabled actual action",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable storage migration/table/worker/replay/recovery",
        "external provider expansion",
        "staging/commit/push",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "813 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "88차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        "89차 Personal Automation Final Verification Sweep",
    ]:
        assert phrase in combined


def test_stage89_personal_automation_final_verification_sweep_freezes_final_sweep_results() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "89차 Personal Automation Final Verification Sweep",
        "Personal Automation Final Verification Sweep",
        "81~88차 Personal Automation Hardening 구간",
        "final verification sweep",
        "user final approval gate",
        "Opus review gate",
        "failure/stop",
        "audit/observability",
        "session/context binding",
        "operator confirmation",
        "manual review packet",
        "release-lock",
        "POST /assistant/durable-state-preview/preview",
        "still-disabled scope",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable storage migration/table/worker/replay/recovery",
        "external provider expansion",
        "staging/commit/push",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "814 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "89차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
        ".venv/bin/python scripts/local_ci_check.py --root .",
        "git status --short --branch",
        "90차 Personal Automation Release-lock Final Decision Packet",
    ]:
        assert phrase in combined


def test_stage90_to_stage158_release_lock_commit_boundary_and_jarvis_honesty_guards() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
        "docs/PUBLIC_RELEASE_SUMMARY.md": Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "90차 Personal Automation Release-lock Final Decision Packet",
        "Personal Automation Release-lock Final Decision Packet",
        "81~89차 Personal Automation Hardening 구간",
        "release-lock final decision packet",
        "final decision/stage boundary",
        "Personal Automation Hardening은 release-lock 완료",
        "actual personal automation execution은 Decision Required",
        "entry decision",
        "approval/Opus gate matrix",
        "failure/stop hardening",
        "audit/observability hardening",
        "session/context binding",
        "operator confirmation boundary",
        "manual review packet",
        "release-lock drift guard",
        "final verification sweep",
        "POST /assistant/durable-state-preview/preview",
        "blocked/review-required scope",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable storage migration/table/worker/replay/recovery",
        "external provider expansion",
        "persistent browser profile/session mutation",
        "payment/login/delete/sensitive input",
        "staging/commit/push",
        "FastAPI endpoints 94",
        "protected endpoints 78",
        "public endpoints 16",
        "815 passed, 1 warning",
        "scanned_files=134",
        "modified tracked files 40개",
        "untracked docs 11개",
        "90차에서 새 untracked doc은 추가하지 않았다",
        "staging/commit/push는 수행하지 않았다",
        ".venv/bin/pytest",
        ".venv/bin/python -m compileall app cli scripts",
        ".venv/bin/python scripts/public_release_check.py --root . --json",
        "git diff --check",
        ".venv/bin/python scripts/local_ci_check.py --root .",
        "git status --short --branch",
        "91차 Commit / Stage Decision Required",
        "Commit / Stage Decision Required packet",
        "1~90차 누적 diff",
        "stage/commit/push decision boundary",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "사용자 최종 승인 필요",
        "modified tracked files 40개",
        "untracked docs 11개",
        "stage/commit/push는 수행하지 않았다",
        "staging/commit/push는 사용자 명시 승인 전 수행하지 않는다",
        "git status --short --branch",
        "815 passed, 1 warning",
        "scanned_files=134",
        "public release finding 없음",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable storage migration/table/worker/replay/recovery",
        "FULL_AUTOMATION_DISPATCH_ENABLED=false",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "92차 Commit Approval or Jarvis v1 Safe Planning",
        "92차 Commit Approval or Jarvis v1 Safe Planning",
        "멈추지 말고 해줘",
        "git 작업 명시 승인으로 해석하지 않는다",
        "Jarvis v1 Safe Planning",
        "120차 Jarvis v1 실사용형 목표까지 28차 남음",
        "150차 Jarvis v2 완성권까지 58차 남음",
        "commit approval flow는 사용자 명시 승인 전 blocked",
        "safe planning only",
        "docs/test/review-required 중심",
        "actual action 없이",
        "93차 Jarvis v1 Safe Roadmap Drift Guard",
        "93차 Jarvis v1 Safe Roadmap Drift Guard",
        "Jarvis v1 Safe Roadmap Drift Guard",
        "93~120차 Jarvis v1 실사용형 구간",
        "safe-next/review-required/blocked 경계",
        "roadmap drift guard",
        "120차 Jarvis v1 실사용형 목표까지 27차 남음",
        "150차 Jarvis v2 완성권까지 57차 남음",
        "actual action으로 새지 않게",
        "94차 Jarvis v1 Capability Honesty Guard",
        "94차 Jarvis v1 Capability Honesty Guard",
        "Jarvis v1 Capability Honesty Guard",
        "capability honesty guard",
        "실제 열린 기능",
        "env opt-in 기능",
        "blocked 기능",
        "이미 열린 기능처럼 과장하지 않게",
        "Jarvis v1은 실행형 완성 제품이 아니라 safe-local assistant boundary",
        "120차 Jarvis v1 실사용형 목표까지 26차 남음",
        "150차 Jarvis v2 완성권까지 56차 남음",
        "95차 Jarvis v1 Manual UX Contract Guard",
        "95차 Jarvis v1 Manual UX Contract Guard",
        "Manual UX Contract Guard",
        "수동 UX",
        "approval wording",
        "blocked state",
        "approval 상태 변경은 실행 승인으로 오해되면 안 된다",
        "manual UX는 operator review surface",
        "120차 Jarvis v1 실사용형 목표까지 25차 남음",
        "150차 Jarvis v2 완성권까지 55차 남음",
        "96차 Jarvis v1 Evidence Packet Guard",
        "96차 Jarvis v1 Evidence Packet Guard",
        "Evidence Packet Guard",
        "증거 패킷",
        "actual verification results",
        "disabled boundary",
        "remaining Decision Required",
        "실행하지 않은 검증/빌드/배포/실제 action",
        "완료처럼 표현하지 않는다",
        "120차 Jarvis v1 실사용형 목표까지 24차 남음",
        "150차 Jarvis v2 완성권까지 54차 남음",
        "97차 Jarvis v1 Decision Required Packet Guard",
        "97차 Jarvis v1 Decision Required Packet Guard",
        "Decision Required Packet Guard",
        "commit/browser/app-os/action-loop/durable activation Decision Required",
        "증거 패킷과 handoff",
        "사용자 최종 승인이나 Opus review가 필요한 항목",
        "safe-next 작업으로 오분류하지 않는다",
        "commit approval flow는 사용자 명시 승인 전 blocked",
        "browser actual/app-os actual/action-loop full dispatch/durable execution activation",
        "120차 Jarvis v1 실사용형 목표까지 23차 남음",
        "150차 Jarvis v2 완성권까지 53차 남음",
        "98차 Jarvis v1 Approval Wording Drift Guard",
        "98차 Jarvis v1 Approval Wording Drift Guard",
        "Approval Wording Drift Guard",
        "approval wording이 실행 승인, 상태 변경, 검증 완료, Decision Required를 혼동하지 않는다",
        "approval 상태 변경, approved console state, confirmation state",
        "execution approval로 승격되지 않는다",
        "approval-wording-is-not-execution-approval",
        "state-change-is-not-execution-approval",
        "verification-pass-is-not-activation-approval",
        "120차 Jarvis v1 실사용형 목표까지 22차 남음",
        "150차 Jarvis v2 완성권까지 52차 남음",
        "99차 Jarvis v1 Release-lock Drift Guard",
        "99차 Jarvis v1 Release-lock Drift Guard",
        "Release-lock Drift Guard",
        "92~98차 Jarvis v1 safe guard 누적 경계",
        "stage/commit/push 미수행 상태",
        "다시 열리지 않았는지 guard",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable execution",
        "modified tracked files 40개",
        "untracked docs 11개",
        "staged diff 없음",
        "120차 Jarvis v1 실사용형 목표까지 21차 남음",
        "150차 Jarvis v2 완성권까지 51차 남음",
        "100차 Jarvis v1 Final Verification Sweep",
        "100차 Jarvis v1 Final Verification Sweep",
        "Final Verification Sweep",
        "92~99차 Jarvis v1 safe guard 구간",
        "full pytest",
        "compileall",
        "public release check",
        "git diff check",
        "local CI",
        "git status",
        "815 passed, 1 warning",
        "scanned_files=134",
        "finding 없음",
        "modified tracked files 40개",
        "untracked docs 11개",
        "staged diff 없음",
        "120차 Jarvis v1 실사용형 목표까지 20차 남음",
        "150차 Jarvis v2 완성권까지 50차 남음",
        "101차 Jarvis v1 Commit Readiness Packet",
        "101차 Jarvis v1 Commit Readiness Packet",
        "Commit Readiness Packet",
        "92~100차 Jarvis v1 safe guard 구간",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "Decision Required",
        "사용자 최종 승인 필요",
        "stage/commit/push는 수행하지 않았다",
        "staged diff 없음",
        "120차 Jarvis v1 실사용형 목표까지 19차 남음",
        "150차 Jarvis v2 완성권까지 49차 남음",
        "102차 Jarvis v1 Handoff Freeze",
        "102차 Jarvis v1 Handoff Freeze",
        "Handoff Freeze",
        "92~101차 Jarvis v1 safe guard 구간",
        "다음 handoff와 검증 프롬프트",
        "Ready-to-send prompt",
        "1~101차 완료 상태",
        "disabled boundaries",
        "stage101/stage102 docs contract",
        "103차 Jarvis v1 Release Candidate Prep",
        "120차 Jarvis v1 실사용형 목표까지 18차 남음",
        "150차 Jarvis v2 완성권까지 48차 남음",
        "103차 Jarvis v1 Release Candidate Prep",
        "Release Candidate Prep",
        "92~102차 Jarvis v1 safe guard 구간",
        "release candidate readiness",
        "남은 Decision Required",
        "stage/commit/push 사용자 최종 승인 필요 상태",
        "staged diff 없음 guard",
        "104차 Jarvis v1 Final RC Verification",
        "120차 Jarvis v1 실사용형 목표까지 17차 남음",
        "150차 Jarvis v2 완성권까지 47차 남음",
        "104차 Jarvis v1 Final RC Verification",
        "Final RC Verification",
        "92~103차 Jarvis v1 safe guard 구간",
        "full verification",
        "RC boundary",
        "`815 passed, 1 warning`",
        "public release check `ok=true`",
        "`scanned_files=134`",
        "105차 Jarvis v1 Final Stage Decision Packet",
        "120차 Jarvis v1 실사용형 목표까지 16차 남음",
        "150차 Jarvis v2 완성권까지 46차 남음",
        "105차 Jarvis v1 Final Stage Decision Packet",
        "Final Stage Decision Packet",
        "Jarvis v1 RC 구간",
        "stage/commit/push 최종 Decision Required",
        "commit scope, commit message, push/PR 여부",
        "사용자 최종 승인 필요 상태",
        "stage/commit/push는 수행하지 않았다",
        "106차 Jarvis v1 Public Release Guard",
        "120차 Jarvis v1 실사용형 목표까지 15차 남음",
        "150차 Jarvis v2 완성권까지 45차 남음",
        "106차 Jarvis v1 Public Release Guard",
        "Public Release Guard",
        "public release scanner",
        "공개 문서의 Jarvis v1 안전 경계",
        "public release check `ok=true`",
        "`scanned_files=134`",
        "finding 없음",
        "107차 Jarvis v1 Evidence Freeze",
        "107차 Jarvis v1 Evidence Freeze",
        "Evidence Freeze",
        "Jarvis v1 RC 증거 패킷",
        "검증 수치",
        "actual action 없이 docs/test/review-required 중심",
        "stage/commit/push는 수행하지 않았다",
        "108차 Jarvis v1 Release Lock Refresh",
        "120차 Jarvis v1 실사용형 목표까지 14차 남음",
        "150차 Jarvis v2 완성권까지 44차 남음",
        "120차 Jarvis v1 실사용형 목표까지 13차 남음",
        "150차 Jarvis v2 완성권까지 43차 남음",
        "108차 Jarvis v1 Release Lock Refresh",
        "108차 Jarvis v1 Release Lock Refresh",
        "Release Lock Refresh",
        "92~107차 Jarvis v1 RC 구간",
        "release lock",
        "남은 Decision Required",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "stage/commit/push는 수행하지 않았다",
        "109차 Jarvis v1 Final Handoff Refresh",
        "120차 Jarvis v1 실사용형 목표까지 12차 남음",
        "150차 Jarvis v2 완성권까지 42차 남음",
        "109차 Jarvis v1 Final Handoff Refresh",
        "Final Handoff Refresh",
        "108차 release lock 결과",
        "110차 다음 작업 프롬프트",
        "handoff refresh",
        "docs/NEXT_CHAT_HANDOFF.md",
        "actual action 없이 docs/test/review-required 중심",
        "stage/commit/push는 수행하지 않았다",
        "110차 Jarvis v1 Verification Refresh",
        "120차 Jarvis v1 실사용형 목표까지 11차 남음",
        "150차 Jarvis v2 완성권까지 41차 남음",
        "110차 Jarvis v1 Verification Refresh",
        "Verification Refresh",
        "Jarvis v1 RC 구간의 최신 검증 수치",
        "public release scanner 기준",
        "public release check `ok=true`",
        "`scanned_files=134`",
        "finding 없음",
        "111차 Jarvis v1 Commit Boundary Refresh",
        "120차 Jarvis v1 실사용형 목표까지 10차 남음",
        "150차 Jarvis v2 완성권까지 40차 남음",
        "111차 Jarvis v1 Commit Boundary Refresh",
        "Commit Boundary Refresh",
        "commit scope/message/push/PR 사용자 최종 승인 경계",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "사용자 최종 승인 필요 상태",
        "stage/commit/push는 사용자 명시 승인 전 수행하지 않는다",
        "staged diff 없음 guard",
        "modified tracked files 40개",
        "untracked docs 11개",
        "112차 Jarvis v1 Final Verification Packet",
        "120차 Jarvis v1 실사용형 목표까지 9차 남음",
        "150차 Jarvis v2 완성권까지 39차 남음",
        "112차 Jarvis v1 Final Verification Packet",
        "Final Verification Packet",
        "Jarvis v1 RC 구간의 최종 검증 packet",
        "남은 Decision Required",
        "actual verification results",
        "disabled boundary",
        "remaining Decision Required",
        "stage/commit/push approval boundary",
        "stage/commit/push는 수행하지 않았다",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "사용자 최종 승인 필요 상태",
        "modified tracked files 40개",
        "untracked docs 11개",
        "staged diff 없음",
        "외부 LLM API, 운영 배포, Oracle/cloud 리소스, credential 출력/저장",
        "113차 Jarvis v1 Release Readiness Closure",
        "120차 Jarvis v1 실사용형 목표까지 8차 남음",
        "150차 Jarvis v2 완성권까지 38차 남음",
        "113차 Jarvis v1 Release Readiness Closure",
        "Release Readiness Closure",
        "release readiness",
        "commit 전 닫힘 상태",
        "public release check clean",
        "full pytest green",
        "compileall green",
        "git diff check green",
        "local CI green",
        "staged diff 없음",
        "commit scope, commit message, push/PR 여부",
        "사용자 최종 승인 필요 상태",
        "stage/commit/push가 미수행",
        "modified tracked files 40개",
        "untracked docs 11개",
        "external provider expansion",
        "persistent browser profile/session mutation",
        "file dialog/download/upload",
        "payment/login/delete/sensitive input",
        "app-os connector dispatch",
        "114차 Jarvis v1 Commit Approval Decision Packet",
        "120차 Jarvis v1 실사용형 목표까지 7차 남음",
        "150차 Jarvis v2 완성권까지 37차 남음",
        "114차 Jarvis v1 Commit Approval Decision Packet",
        "Commit Approval Decision Packet",
        "commit approval 전 사용자 최종 승인 필요 항목",
        "commit scope, commit message, push/PR 여부는 Decision Required",
        "사용자 최종 승인 필요 상태",
        "stage/commit/push는 수행하지 않았고 사용자 명시 승인 전 수행하지 않는다",
        "`git diff --cached --quiet` 기준 staged diff 없음",
        "modified tracked files 40개",
        "untracked docs 11개",
        "release readiness는 public release check clean",
        "full pytest green",
        "compileall green",
        "git diff check green",
        "local CI green",
        "browser actual interaction",
        "app-os actual action",
        "action-loop full dispatch",
        "daemon/service/background loop",
        "durable execution",
        "115차 Jarvis v1 Pre-120 Remaining Scope Plan",
        "120차 Jarvis v1 실사용형 목표까지 6차 남음",
        "150차 Jarvis v2 완성권까지 36차 남음",
        "115차 Jarvis v1 Pre-120 Remaining Scope Plan",
        "Pre-120 Remaining Scope Plan",
        "120차 Jarvis v1 실사용형 목표까지 남은 safe-next 범위",
        "115~120차 남은 작업",
        "docs/test/review-required 중심",
        "116차는 Pre-120 Verification Matrix",
        "117차는 Pre-120 Handoff Sync",
        "118차는 Pre-120 Final Evidence Refresh",
        "119차는 Jarvis v1 Readiness Freeze",
        "120차는 Jarvis v1 실사용형 목표 Decision Packet",
        "docs contract",
        "public release summary count guard",
        "local CI 유지",
        "stage/commit/push 미수행 guard",
        "disabled boundary guard",
        "review-required 범위",
        "durable execution activation",
        "116차 Jarvis v1 Pre-120 Verification Matrix",
        "120차 Jarvis v1 실사용형 목표까지 5차 남음",
        "150차 Jarvis v2 완성권까지 35차 남음",
        "116차 Jarvis v1 Pre-120 Verification Matrix",
        "Pre-120 Verification Matrix",
        "116~120차 남은 safe-next 검증 matrix",
        "stage contract",
        "docs bundle",
        "full pytest",
        "compileall",
        "public release check",
        "git diff --check",
        "local CI",
        "git status",
        "staged diff 없음 guard",
        "117~120차는 매 차수",
        "modified tracked files 40개",
        "untracked docs 11개",
        "stage/commit/push 사용자 최종 승인 필요 상태",
        "commit scope/message/push/PR Decision Required",
        "actual action 활성화 승인으로 해석하지 않는다",
        "117차 Jarvis v1 Pre-120 Handoff Sync",
        "120차 Jarvis v1 실사용형 목표까지 4차 남음",
        "150차 Jarvis v2 완성권까지 34차 남음",
        "117차 Jarvis v1 Pre-120 Handoff Sync",
        "Pre-120 Handoff Sync",
        "118차 다음 handoff와 검증 프롬프트",
        "116차 검증 matrix가 NEXT_CHAT_HANDOFF, TASKS, WORKLOG, PUBLIC_RELEASE_SUMMARY에 남아",
        "118차 다음 작업은 Jarvis v1 Pre-120 Final Evidence Refresh",
        "stage117 contract",
        "docs bundle",
        "full pytest",
        "compileall",
        "public release check",
        "git diff --check",
        "local CI",
        "git status",
        "staged diff 없음 guard",
        "118차 Jarvis v1 Pre-120 Final Evidence Refresh",
        "120차 Jarvis v1 실사용형 목표까지 3차 남음",
        "150차 Jarvis v2 완성권까지 33차 남음",
        "118차 Jarvis v1 Pre-120 Final Evidence Refresh",
        "Pre-120 Final Evidence Refresh",
        "120차 직전 evidence 기준",
        "evidence 기준은 full pytest, public release check, local CI, staged diff 없음, modified tracked files 40개, untracked docs 11개",
        "compileall 성공",
        "git diff --check 성공",
        "local CI 성공",
        "stage/commit/push는 수행하지 않았고 사용자 명시 승인 전 수행하지 않는다",
        "commit scope, commit message, push/PR 여부는 사용자 최종 승인 필요 상태",
        "119차 Jarvis v1 Readiness Freeze",
        "120차 Jarvis v1 실사용형 목표까지 2차 남음",
        "150차 Jarvis v2 완성권까지 32차 남음",
        "119차 Jarvis v1 Readiness Freeze",
        "Readiness Freeze",
        "120차 Jarvis v1 실사용형 목표 진입 직전 상태",
        "readiness freeze 기준",
        "evidence 기준, disabled boundary, remaining Decision Required, stage/commit/push 미수행",
        "readiness freeze는 activation approval이 아니며",
        "durable storage migration/table/worker/replay/recovery는 열지 않았다",
        "compileall 성공",
        "git diff --check 성공",
        "local CI 성공",
        "120차 권장 작업은 Jarvis v1 실사용형 목표 Decision Packet",
        "120차 Jarvis v1 실사용형 목표까지 1차 남음",
        "150차 Jarvis v2 완성권까지 31차 남음",
        "120차 Jarvis v1 실사용형 목표 Decision Packet",
        "safe-local 실사용형 경계와 남은 Decision Required",
        "실제 열린 기능, env opt-in 기능, blocked 기능, remaining Decision Required",
        "120차 Jarvis v1 실사용형 목표 Decision Packet",
        "Jarvis v1 실사용형 목표는 실행형 완성 제품이 아니라 safe-local assistant boundary 완성권",
        "safe-local 실사용형 경계는 실제 열린 기능, env opt-in 기능, blocked 기능, remaining Decision Required를 구분한다",
        "실제 열린 기능은 로컬 RAG/assistant bridge",
        "protected approval-console read-only API",
        "durable-state-preview read-only API 하나",
        "env opt-in 기능은 read-only adapter, read-only action-loop dispatch, allowlist shell",
        "browser observe metadata",
        "browser limited candidate validation",
        "external web search provider 단건 search",
        "blocked 기능은 browser actual interaction, app-os actual action, action-loop full dispatch",
        "durable execution, durable storage migration/table/worker/replay/recovery",
        "Jarvis v1 Decision Packet은 activation approval이 아니며",
        "commit/browser/app-os/action-loop/durable activation은 remaining Decision Required",
        "120차 Jarvis v1 실사용형 목표 Decision Packet까지 완료",
        "150차 Jarvis v2 완성권까지 30차 남음",
        "121차 권장 작업은 Jarvis v2 Entry Scope Plan",
        "121차 Jarvis v2 Entry Scope Plan",
        "121~150차 v2 완성권 범위",
        "121차 Jarvis v2 Entry Scope Plan",
        "121~150차 v2 완성권 범위를 safe-next/review-required/blocked 경계로 분류",
        "safe-next 범위는 docs contract, public release summary guard, local CI 유지",
        "runtime/docs drift guard",
        "capability honesty guard",
        "approval wording guard",
        "evidence packet refresh",
        "handoff sync",
        "review-required 범위는 commit approval, browser actual interaction candidate",
        "app-os actual action candidate",
        "action-loop full dispatch candidate",
        "durable execution candidate",
        "외부 provider 확장",
        "Oracle/cloud/cost 영향 작업",
        "blocked 범위는 사용자 최종 승인과 Opus review 전 browser actual interaction",
        "durable storage migration/table/worker/replay/recovery, autonomous replay/recovery",
        "actual action activation roadmap이 아니라 safe-local hardening roadmap",
        "122~130차는 v2 safety/contract hardening",
        "131~140차는 v2 evidence/release-lock hardening",
        "141~150차는 v2 final decision/release-lock packet",
        "150차 Jarvis v2 완성권까지 29차 남음",
        "122차 권장 작업은 Jarvis v2 Safety Contract Matrix",
        "122차 Jarvis v2 Safety Contract Matrix",
        "122차 Jarvis v2 Safety Contract Matrix",
        "v2 안전 계약은 safe-next, review-required, blocked boundary를 matrix로 유지하는 guard",
        "safe-next matrix 항목은 docs contract, public release summary guard, local CI 유지",
        "runtime/docs drift guard, capability honesty guard, approval wording guard",
        "evidence packet refresh, handoff sync",
        "review-required matrix 항목은 commit approval, browser actual interaction candidate",
        "app-os actual action candidate, action-loop full dispatch candidate, durable execution candidate",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work",
        "blocked matrix 항목은 사용자 최종 승인과 Opus review 전 browser actual interaction",
        "daemon/service/background loop, durable storage migration/table/worker/replay/recovery",
        "autonomous replay/recovery",
        "disabled boundary matrix는 `FULL_AUTOMATION_DISPATCH_ENABLED=false`",
        "`action_loop_full_dispatch_connected=false`",
        "`browser_actual_interaction_connected=false`",
        "`app_os_actual_action_connected=false`",
        "`durable_execution_connected=false`",
        "v2 safety matrix는 activation approval이 아니며",
        "approval 상태 변경, manual review packet, confirmation wording, passing verification",
        "execution approval로 승격하지 않는다",
        "150차 Jarvis v2 완성권까지 28차 남음",
        "123차 권장 작업은 Jarvis v2 Runtime Docs Drift Guard",
        "123차 Jarvis v2 Runtime Docs Drift Guard",
        "123차 Jarvis v2 Runtime Docs Drift Guard",
        "runtime/docs drift guard는 `/assistant/capabilities`, README, SECURITY, PUBLIC_RELEASE_SUMMARY, NEXT_CHAT_HANDOFF",
        "disabled boundary wording이 서로 어긋나지 않게 유지",
        "capability honesty 기준은 실제 열린 기능, env opt-in 기능, blocked 기능, remaining Decision Required를 구분",
        "`/assistant/capabilities`와 문서는 browser actual interaction, app-os actual action, action-loop full dispatch",
        "daemon/service/background loop, durable execution을 enabled로 광고하지 않는다",
        "v2 drift guard는 `FULL_AUTOMATION_DISPATCH_ENABLED=false`",
        "`action_loop_full_dispatch_connected=false`",
        "`browser_actual_interaction_connected=false`",
        "`app_os_actual_action_connected=false`",
        "`durable_execution_connected=false`를 유지한다",
        "passing verification이 activation approval이 아니며 stage/commit/push approval도 아님",
        "route/API/schema/service 변경 없이 docs/test/review-required 중심",
        "150차 Jarvis v2 완성권까지 27차 남음",
        "124차 권장 작업은 Jarvis v2 Capability Honesty Refresh",
        "124차 Jarvis v2 Capability Honesty Refresh",
        "124차 Jarvis v2 Capability Honesty Refresh",
        "Capability Honesty Refresh",
        "실제 열린 기능, env opt-in 기능, blocked 기능, remaining Decision Required 문구를 재동기화",
        "실제 열린 기능은 로컬 RAG/assistant bridge",
        "preview/dry-run/read-only/state-only endpoint",
        "protected approval-console read-only API",
        "durable-state-preview read-only API 하나",
        "env opt-in 기능은 read-only adapter, read-only action-loop dispatch, allowlist shell",
        "single-file patch",
        "single-file rollback",
        "one-shot task queue",
        "browser observe metadata",
        "browser limited candidate validation",
        "external web search provider 단건 search",
        "blocked 기능은 browser actual interaction, app-os actual action, action-loop full dispatch",
        "durable execution, durable storage migration/table/worker/replay/recovery, autonomous replay/recovery",
        "remaining Decision Required는 commit approval, browser actual/app-os actual/action-loop full dispatch/durable execution activation",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work",
        "Jarvis v2 wording은 actual action 제품으로 과장하지 않고 safe-local hardening roadmap",
        "150차 Jarvis v2 완성권까지 26차 남음",
        "125차 권장 작업은 Jarvis v2 Approval Wording Guard",
        "125차 Jarvis v2 Approval Wording Guard",
        "125차 Jarvis v2 Approval Wording Guard",
        "Approval Wording Guard",
        "approval/confirmation/verification wording이 execution approval로 승격되지 않게",
        "approval state, approved console state, operator confirmation, passing verification, manual review packet은 actual connector dispatch approval이 아니다",
        "approval 상태 변경은 execution approval이 아니며 approval 상태만으로 connector execution",
        "approval consume, browser actual interaction, app-os actual action, action-loop full dispatch, durable execution을 시작할 수 없다",
        "operator confirmation wording은 final human action boundary를 설명할 수 있지만 local server actual action authorization으로 해석하지 않는다",
        "passing verification은 activation approval이 아니며 public release check green",
        "full pytest green, compileall green, local CI green은 stage/commit/push approval도 아니다",
        "manual review packet과 evidence packet은 remaining Decision Required를 보여 주는 review artifact",
        "execution approval이나 production readiness approval이 아니다",
        "approval-wording-is-not-execution-approval",
        "confirmation-is-not-execution-approval",
        "verification-pass-is-not-activation-approval",
        "150차 Jarvis v2 완성권까지 25차 남음",
        "126차 권장 작업은 Jarvis v2 Evidence Packet Refresh",
        "126차 Jarvis v2 Evidence Packet Refresh",
        "126차 Jarvis v2 Evidence Packet Refresh",
        "Evidence Packet Refresh",
        "actual verification results, disabled boundary, remaining Decision Required 증거 패킷을 함께 갱신",
        "actual verification results는 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`",
        "finding 없음, compileall 성공, git diff check 성공, local CI 성공",
        "evidence packet은 실행하지 않은 검증/빌드/배포/실제 action을 완료처럼 표현하지 않는다",
        "disabled boundary는 browser actual interaction, app-os actual action, action-loop full dispatch",
        "durable execution, durable storage migration/table/worker/replay/recovery, autonomous replay/recovery가 열리지 않았음을 포함",
        "remaining Decision Required는 commit approval, browser actual/app-os actual/action-loop full dispatch/durable execution activation",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work",
        "evidence packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "public release check clean, full pytest green, compileall green, git diff check green, local CI green, staged diff 없음",
        "150차 Jarvis v2 완성권까지 24차 남음",
        "127차 권장 작업은 Jarvis v2 Handoff Sync",
        "127차 Jarvis v2 Handoff Sync",
        "127차 Jarvis v2 Handoff Sync",
        "Handoff Sync",
        "126차 evidence packet과 다음 검증 프롬프트를 `docs/NEXT_CHAT_HANDOFF.md`에 동기화",
        "Ready-to-send prompt는 1~126차 완료 상태, actual verification results, disabled boundary, remaining Decision Required, stage/commit/push 미수행을 포함",
        "Ready-to-send prompt는 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`",
        "modified tracked files 40개, untracked docs 11개, staged diff 없음 기준을 포함",
        "다음 검증 프롬프트는 stage126/stage127 docs contract, docs bundle, full pytest",
        "compileall, public release check, git diff --check, local CI, git status, staged diff 없음 guard를 포함",
        "handoff sync는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "browser actual interaction, app-os actual action, action-loop full dispatch, daemon/service/background loop, durable execution",
        "durable storage migration/table/worker/replay/recovery는 계속 disabled boundary에 남긴다",
        "150차 Jarvis v2 완성권까지 23차 남음",
        "128차 권장 작업은 Jarvis v2 Release-lock Drift Guard",
        "128차 Jarvis v2 Release-lock Drift Guard",
        "128차 Jarvis v2 Release-lock Drift Guard",
        "Release-lock Drift Guard",
        "121~127차 v2 safe guard 누적 경계와 stage/commit/push 미수행 상태를 재확인",
        "121~127차 v2 safe guard는 entry scope plan, safety contract matrix, runtime/docs drift guard",
        "capability honesty refresh, approval wording guard, evidence packet refresh, handoff sync",
        "v2 safe guard 누적 경계는 actual action activation roadmap이 아니라 safe-local hardening roadmap",
        "browser actual interaction, app-os actual action, action-loop full dispatch, daemon/service/background loop, durable execution은 다시 열리지 않았다",
        "durable storage migration/table/worker/replay/recovery, autonomous replay/recovery, external provider expansion",
        "production deployment, Oracle/cloud/cost impact work는 remaining Decision Required",
        "`FULL_AUTOMATION_DISPATCH_ENABLED=false`",
        "`action_loop_full_dispatch_connected=false`",
        "`browser_actual_interaction_connected=false`",
        "`app_os_actual_action_connected=false`",
        "`durable_execution_connected=false`",
        "150차 Jarvis v2 완성권까지 22차 남음",
        "129차 권장 작업은 Jarvis v2 Final Verification Sweep",
        "129차 Jarvis v2 Final Verification Sweep",
        "129차 Jarvis v2 Final Verification Sweep",
        "Final Verification Sweep",
        "121~128차 v2 safe guard 구간의 full verification과 release-lock boundary를 재확인",
        "full verification은 stage129 docs contract, docs bundle, full pytest, compileall",
        "public release check, git diff --check, local CI, git status, staged diff 없음 guard를 포함",
        "최신 검증 기준은 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`, finding 없음",
        "compileall 성공, git diff --check 성공, local CI 성공, staged diff 없음 기준을 유지",
        "release-lock boundary는 121~128차 v2 safe guard가 actual action activation roadmap이 아니라 safe-local hardening roadmap",
        "browser actual interaction, app-os actual action, action-loop full dispatch, daemon/service/background loop, durable execution",
        "durable storage migration/table/worker/replay/recovery는 열리지 않았다",
        "durable storage migration/table/worker/replay/recovery, autonomous replay/recovery, external provider expansion",
        "`FULL_AUTOMATION_DISPATCH_ENABLED=false`",
        "`action_loop_full_dispatch_connected=false`",
        "`browser_actual_interaction_connected=false`",
        "`app_os_actual_action_connected=false`",
        "`durable_execution_connected=false`",
        "modified tracked files 40개",
        "untracked docs 11개",
        "staged diff 없음",
        "150차 Jarvis v2 완성권까지 21차 남음",
        "130차 권장 작업은 Jarvis v2 Commit Readiness Packet",
        "130차 Jarvis v2 Commit Readiness Packet",
        "121~129차 v2 safe guard 구간의 commit scope/message/push/PR Decision Required",
        "130차 Jarvis v2 Commit Readiness Packet",
        "Commit Readiness Packet",
        "121~129차 v2 safe guard 구간의 commit scope/message/push/PR Decision Required를 정리",
        "commit scope 후보는 121~129차 v2 safe guard 문서/테스트 갱신",
        "runtime route/API/schema/service 변경을 새로 열지 않는다",
        "commit message 후보는 `Document Jarvis v2 safe guard readiness packet`",
        "최종 commit message는 사용자 승인 필요 상태",
        "push/PR 여부는 사용자 최종 승인 필요 상태",
        "Codex가 임의로 push/PR을 만들지 않는다",
        "stage/commit/push는 수행하지 않았고 staged diff 없음 기준을 유지",
        "release readiness는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "modified tracked files 40개",
        "untracked docs 11개",
        "staged diff 없음",
        "150차 Jarvis v2 완성권까지 20차 남음",
        "131차 권장 작업은 Jarvis v2 Evidence Lock Refresh",
        "131차 Jarvis v2 Evidence Lock Refresh",
        "121~130차 v2 safe guard 구간의 evidence/release readiness 기준",
        "131차 Jarvis v2 Evidence Lock Refresh",
        "Evidence Lock Refresh",
        "121~130차 v2 safe guard 구간의 evidence/release readiness 기준을 재확인",
        "evidence lock은 actual verification results, disabled boundary, remaining Decision Required, commit readiness boundary를 함께 포함",
        "actual verification results는 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`",
        "finding 없음, compileall 성공, git diff --check 성공, local CI 성공",
        "disabled boundary는 browser actual interaction, app-os actual action, action-loop full dispatch",
        "durable execution, durable storage migration/table/worker/replay/recovery가 열리지 않았음을 포함",
        "remaining Decision Required는 commit approval, browser actual/app-os actual/action-loop full dispatch/durable execution activation",
        "commit readiness boundary는 commit scope 후보, commit message 후보, push/PR 여부가 사용자 최종 승인 필요 상태",
        "release readiness는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "150차 Jarvis v2 완성권까지 19차 남음",
        "132차 권장 작업은 Jarvis v2 Release Readiness Drift Guard",
        "132차 Jarvis v2 Release Readiness Drift Guard",
        "121~131차 v2 safe guard 구간의 release readiness 문구가 activation approval",
        "132차 Jarvis v2 Release Readiness Drift Guard",
        "Release Readiness Drift Guard",
        "121~131차 v2 safe guard 구간의 release readiness 문구가 activation approval로 새지 않게 재확인",
        "release readiness는 public release check clean, full pytest green, compileall green",
        "git diff check green, local CI green, staged diff 없음 기준을 의미",
        "release readiness는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "release readiness는 browser actual interaction, app-os actual action, action-loop full dispatch, durable execution activation approval로 해석하지 않는다",
        "`815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`, finding 없음 기준을 유지",
        "stage/commit/push는 수행하지 않았고 사용자 명시 승인 전 수행하지 않는다",
        "150차 Jarvis v2 완성권까지 18차 남음",
        "133차 권장 작업은 Jarvis v2 Public Release Evidence Refresh",
        "133차 Jarvis v2 Public Release Evidence Refresh",
        "공개 릴리스 evidence 기준과 disabled boundary",
        "133차 Jarvis v2 Public Release Evidence Refresh",
        "Public Release Evidence Refresh",
        "public release evidence는 public release check clean, `scanned_files=134`, finding 없음",
        "private data exclusion, disabled actual action boundary를 함께 포함",
        "public release evidence는 production deployment approval, external provider expansion approval, stage/commit/push approval이 아니다",
        "private data exclusion은 `.env`, credential, local DB, Chroma data, uploads/logs",
        "raw private documents, API key/token/password/private key를 공개하지 않는 기준",
        "disabled actual action boundary는 browser actual interaction, app-os actual action, action-loop full dispatch",
        "daemon/service/background loop, durable execution, durable storage migration/table/worker/replay/recovery를 계속 열지 않는 기준",
        "150차 Jarvis v2 완성권까지 17차 남음",
        "134차 권장 작업은 Jarvis v2 Disabled Boundary Evidence Guard",
        "134차 Jarvis v2 Disabled Boundary Evidence Guard",
        "disabled actual action boundary와 remaining Decision Required",
        "134차 Jarvis v2 Disabled Boundary Evidence Guard",
        "Disabled Boundary Evidence Guard",
        "disabled actual action boundary와 remaining Decision Required를 재확인",
        "disabled actual action boundary는 browser actual interaction, app-os actual action, action-loop full dispatch",
        "daemon/service/background loop, durable execution, durable storage migration/table/worker/replay/recovery를 계속 열지 않는 기준",
        "remaining Decision Required는 commit approval, browser actual/app-os actual/action-loop full dispatch/durable execution activation",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work",
        "disabled boundary evidence는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "`FULL_AUTOMATION_DISPATCH_ENABLED=false`",
        "`action_loop_full_dispatch_connected=false`",
        "`browser_actual_interaction_connected=false`",
        "`app_os_actual_action_connected=false`",
        "`durable_execution_connected=false`",
        "150차 Jarvis v2 완성권까지 16차 남음",
        "135차 권장 작업은 Jarvis v2 Remaining Decision Required Sync",
        "135차 Jarvis v2 Remaining Decision Required Sync",
        "remaining Decision Required 항목과 handoff/public release evidence",
        "135차 Jarvis v2 Remaining Decision Required Sync",
        "Remaining Decision Required Sync",
        "remaining Decision Required 항목과 handoff/public release evidence를 재동기화",
        "handoff/public release evidence는 actual verification results, disabled boundary, remaining Decision Required, stage/commit/push 미수행을 함께 포함",
        "commit approval remains Decision Required",
        "browser actual/app-os actual/action-loop full dispatch/durable execution activation remains Decision Required",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work remains Decision Required",
        "remaining Decision Required sync는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "150차 Jarvis v2 완성권까지 15차 남음",
        "136차 권장 작업은 Jarvis v2 Release Evidence Consistency Guard",
        "136차 Jarvis v2 Release Evidence Consistency Guard",
        "release evidence와 remaining Decision Required 문구의 정합성",
        "136차 Jarvis v2 Release Evidence Consistency Guard",
        "Release Evidence Consistency Guard",
        "release evidence와 remaining Decision Required 문구의 정합성을 재확인",
        "release evidence는 actual verification results, disabled boundary, remaining Decision Required, public release check clean, staged diff 없음, stage/commit/push 미수행을 함께 포함",
        "release evidence consistency는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "release evidence wording must not imply activation approval, production readiness approval, external provider approval, or git approval",
        "150차 Jarvis v2 완성권까지 14차 남음",
        "137차 권장 작업은 Jarvis v2 Pre-final Evidence Freeze",
        "137차 Jarvis v2 Pre-final Evidence Freeze",
        "141~150차 final decision 구간 전 evidence 기준을 동결",
        "137차 Jarvis v2 Pre-final Evidence Freeze",
        "Pre-final Evidence Freeze",
        "frozen evidence 기준은 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`",
        "finding 없음, modified tracked files 40개, untracked docs 11개, staged diff 없음",
        "frozen evidence는 activation approval, production readiness approval, stage/commit/push approval, external provider approval이 아니다",
        "pre-final evidence freeze는 final decision approval이 아니라 141~150차 final decision 구간 전 evidence baseline",
        "150차 Jarvis v2 완성권까지 13차 남음",
        "138차 권장 작업은 Jarvis v2 Final Decision Prep Boundary Guard",
        "138차 Jarvis v2 Final Decision Prep Boundary Guard",
        "final decision 준비 문구가 approval로 새지 않게",
        "138차 Jarvis v2 Final Decision Prep Boundary Guard",
        "Final Decision Prep Boundary Guard",
        "final decision 준비 문구가 activation approval, production readiness approval, stage/commit/push approval로 새지 않게",
        "final decision prep은 141~150차 final decision 구간을 준비하는 문서/테스트 guard이며 actual activation이 아니다",
        "final decision prep is not approval, final decision prep is not production readiness, final decision prep is not git approval",
        "150차 Jarvis v2 완성권까지 12차 남음",
        "139차 권장 작업은 Jarvis v2 Final Decision Readiness Matrix",
        "139차 Jarvis v2 Final Decision Readiness Matrix",
        "readiness matrix는 evidence ready, disabled boundary ready, remaining Decision Required ready, git approval blocked, activation approval blocked를 구분",
        "139차 Jarvis v2 Final Decision Readiness Matrix",
        "Final Decision Readiness Matrix",
        "141~150차 final decision 구간 진입 전 readiness matrix를 고정",
        "readiness matrix는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "readiness matrix ready 상태는 실제 activation, production deployment, external provider expansion, stage/commit/push 승인으로 해석하지 않는다",
        "150차 Jarvis v2 완성권까지 11차 남음",
        "140차 권장 작업은 Jarvis v2 Pre-final Verification Refresh",
        "140차 Jarvis v2 Pre-final Verification Refresh",
        "141~150차 final decision 구간 전 검증 기준을 재확인",
        "140차 Jarvis v2 Pre-final Verification Refresh",
        "Pre-final Verification Refresh",
        "검증 기준은 `815 passed, 1 warning`, public release check `ok=true`, `scanned_files=134`, finding 없음, compileall 성공, git diff --check 성공, local CI 성공, staged diff 없음",
        "pre-final verification refresh는 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "pre-final verification refresh는 141~150차 final decision 구간 전 검증 기준 재확인이며 actual activation이 아니다",
        "browser actual/app-os actual/action-loop full dispatch/durable execution activation remains Decision Required",
        "external provider expansion, production deployment, Oracle/cloud/cost impact work remains Decision Required",
        "browser actual interaction/app-os actual action/git reset/bulk restore/daemon/service/운영 배포 blocked",
        "150차 Jarvis v2 완성권까지 10차 남음",
        "141차 권장 작업은 Jarvis v2 Final Decision Entry Packet",
        "141차 Jarvis v2 Final Decision Entry Packet",
        "141차 Jarvis v2 Final Decision Entry Packet",
        "Final Decision Entry Packet",
        "141~150차 final decision 구간 진입 packet을 정리",
        "final decision entry packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "final decision entry packet은 actual activation, production deployment, external provider expansion, stage/commit/push 승인으로 해석하지 않는다",
        "final decision entry packet은 141~150차 final decision 구간 진입 상태를 정리하는 review packet이며 execution packet이 아니다",
        "final decision entry packet keeps commit approval blocked and activation approval blocked",
        "final decision entry packet keeps evidence ready, disabled boundary ready, remaining Decision Required ready",
        "150차 Jarvis v2 완성권까지 9차 남음",
        "142차 권장 작업은 Jarvis v2 Final Decision Approval Boundary Packet",
        "142차 Jarvis v2 Final Decision Approval Boundary Packet",
        "142차 Jarvis v2 Final Decision Approval Boundary Packet",
        "Final Decision Approval Boundary Packet",
        "final decision approval boundary를 정리",
        "final decision approval boundary는 user approval, Opus review, production readiness, stage/commit/push approval을 서로 분리",
        "approval boundary packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "approval boundary packet은 user approval request를 execution approval로 승격하지 않는다",
        "approval boundary packet keeps git approval separate from activation approval",
        "approval boundary packet keeps Opus review gate separate from user final approval",
        "production readiness remains separate from public release evidence",
        "150차 Jarvis v2 완성권까지 8차 남음",
        "143차 권장 작업은 Jarvis v2 Final Decision Evidence Packet",
        "143차 Jarvis v2 Final Decision Evidence Packet",
        "143차 Jarvis v2 Final Decision Evidence Packet",
        "Final Decision Evidence Packet",
        "final decision 구간 evidence packet을 정리",
        "evidence packet은 actual verification results, disabled boundary, remaining Decision Required, approval boundary를 함께 포함",
        "final decision evidence packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "final decision evidence packet은 user approval request나 Opus review gate를 execution approval로 승격하지 않는다",
        "final decision evidence packet keeps approval boundary separate from verification evidence",
        "final decision evidence packet keeps commit approval blocked and activation approval blocked",
        "150차 Jarvis v2 완성권까지 7차 남음",
        "144차 권장 작업은 Jarvis v2 Final Decision Release Lock Packet",
        "144차 Jarvis v2 Final Decision Release Lock Packet",
        "144차 Jarvis v2 Final Decision Release Lock Packet",
        "Final Decision Release Lock Packet",
        "final decision release lock을 정리",
        "release lock은 actual verification results, disabled boundary, remaining Decision Required, approval boundary, stage/commit/push 미수행을 함께 포함",
        "final decision release lock은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "final decision release lock keeps verification evidence separate from activation approval",
        "final decision release lock keeps git approval blocked and activation approval blocked",
        "release lock은 user final approval, Opus review gate, production readiness, git approval을 서로 대체하지 않는다",
        "150차 Jarvis v2 완성권까지 6차 남음",
        "145차 권장 작업은 Jarvis v2 Final Decision Commit Boundary Packet",
        "145차 Jarvis v2 Final Decision Commit Boundary Packet",
        "145차 Jarvis v2 Final Decision Commit Boundary Packet",
        "Final Decision Commit Boundary Packet",
        "final decision commit boundary를 정리",
        "commit boundary는 commit scope, commit message, push/PR 여부, staged diff 없음, stage/commit/push 미수행을 함께 포함",
        "commit boundary packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "commit boundary packet keeps commit approval blocked until explicit user approval",
        "commit boundary packet keeps staged diff empty and stage/commit/push unperformed",
        "commit boundary packet keeps git approval separate from release readiness",
        "150차 Jarvis v2 완성권까지 5차 남음",
        "146차 권장 작업은 Jarvis v2 Final Decision Verification Packet",
        "146차 Jarvis v2 Final Decision Verification Packet",
        "146차 Jarvis v2 Final Decision Verification Packet",
        "Final Decision Verification Packet",
        "final decision verification 기준을 정리",
        "verification packet은 full pytest, compileall, public release check, git diff --check, local CI, git status, staged diff 없음 guard를 함께 포함",
        "verification packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "verification packet keeps test evidence separate from activation approval",
        "verification packet keeps public release evidence separate from production deployment approval",
        "verification packet keeps staged diff empty and stage/commit/push unperformed",
        "150차 Jarvis v2 완성권까지 4차 남음",
        "147차 권장 작업은 Jarvis v2 Final Decision Status Freeze Packet",
        "147차 Jarvis v2 Final Decision Status Freeze Packet",
        "147차 Jarvis v2 Final Decision Status Freeze Packet",
        "Final Decision Status Freeze Packet",
        "final decision status를 동결",
        "status freeze는 completed stages, remaining stages, disabled boundary, remaining Decision Required, staged diff 없음, stage/commit/push 미수행을 함께 포함",
        "status freeze packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "status freeze packet keeps completed stages separate from activation approval",
        "status freeze packet keeps remaining stages visible and not approved",
        "status freeze packet keeps staged diff empty and stage/commit/push unperformed",
        "completed stages는 1~147차 docs/test/review-required 중심 guard 완료 상태",
        "remaining stages는 148~150차 final decision closure prep, final packet, final handoff",
        "150차 Jarvis v2 완성권까지 3차 남음",
        "148차 권장 작업은 Jarvis v2 Final Decision Closure Prep Packet",
        "148차 Jarvis v2 Final Decision Closure Prep Packet",
        "148차 Jarvis v2 Final Decision Closure Prep Packet",
        "Final Decision Closure Prep Packet",
        "final decision closure prep을 정리",
        "closure prep은 completed stages, remaining stages, final verification evidence, commit boundary, status freeze를 함께 포함",
        "closure prep packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "closure prep packet keeps closure preparation separate from activation approval",
        "closure prep packet keeps final verification evidence separate from production deployment approval",
        "closure prep packet keeps commit boundary and status freeze visible",
        "completed stages는 1~148차 docs/test/review-required 중심 guard 완료 상태",
        "remaining stages는 149~150차 final packet, final handoff",
        "150차 Jarvis v2 완성권까지 2차 남음",
        "149차 권장 작업은 Jarvis v2 Final Decision Final Packet",
        "149차 Jarvis v2 Final Decision Final Packet",
        "149차 Jarvis v2 Final Decision Final Packet",
        "Final Decision Final Packet",
        "final decision final packet을 정리",
        "final packet은 completed stages, final verification evidence, release lock, commit boundary, status freeze, remaining Decision Required를 함께 포함",
        "final packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "final packet keeps final decision evidence separate from activation approval",
        "final packet keeps release lock separate from production deployment approval",
        "final packet keeps commit approval blocked and stage/commit/push unperformed",
        "completed stages는 1~149차 docs/test/review-required 중심 guard 완료 상태",
        "remaining stage는 150차 final handoff",
        "150차 Jarvis v2 완성권까지 1차 남음",
        "150차 권장 작업은 Jarvis v2 Final Handoff Packet",
        "150차 Jarvis v2 Final Handoff Packet",
        "150차 Jarvis v2 Final Handoff Packet",
        "Jarvis v2 완성권 final handoff를 정리",
        "Final Handoff Packet",
        "final handoff는 1~150차 completed stages, final verification evidence, disabled boundary, remaining Decision Required, commit/stage Decision Required, next human decision을 함께 포함",
        "final handoff packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "final handoff keeps Jarvis v2 completion separate from activation approval",
        "final handoff keeps final verification evidence separate from production deployment approval",
        "final handoff keeps commit/stage Decision Required as the next human decision",
        "completed stages는 1~150차 docs/test/review-required 중심 guard 완료 상태",
        "150차 Jarvis v2 완성권 완료",
        "next human decision은 commit scope, commit message, push/PR 여부 승인",
        "stage/commit/push remains unperformed after Jarvis v2 final handoff",
        "151차 Commit / Stage Final Decision Required Packet",
        "Commit / Stage Final Decision Required Packet",
        "final handoff 이후 commit/stage/push 승인 경계를 최종 Decision Required로 재고정",
        "151차는 stage/commit/push 실행 단계가 아니다",
        "151차 packet은 activation approval, production readiness approval, stage/commit/push approval이 아니다",
        "commit scope는 사용자 최종 승인 필요",
        "commit message는 사용자 최종 승인 필요",
        "push/PR 여부는 사용자 최종 승인 필요",
        "staged diff 없음은 계속 유지",
        "stage/commit/push remains unperformed after stage151 decision packet",
        "멈추지 말고 해줘는 git stage/commit/push 명시 승인으로 해석하지 않는다",
        "next human decision remains commit scope, commit message, push/PR approval",
        "152차 Post-151 Commit Decision Hold Guard",
        "Post-151 Commit Decision Hold Guard",
        "151차 이후 사용자 승인 대기 상태를 유지",
        "152차는 commit hold guard이며 stage/commit/push 실행 단계가 아니다",
        "commit hold guard keeps staged diff empty",
        "commit hold guard keeps worktree unstaged until explicit approval",
        "commit hold guard keeps user approval separate from continue instruction",
        "commit hold guard keeps public release evidence separate from production deployment approval",
        "stage/commit/push remains unperformed after stage152 hold guard",
        "next human decision remains explicit commit scope, commit message, push/PR approval",
        "153차 Explicit Approval Awaiting Packet",
        "Explicit Approval Awaiting Packet",
        "사용자 최종 승인 대기 상태를 명시적으로 유지",
        "153차는 approval awaiting packet이며 stage/commit/push 실행 단계가 아니다",
        "explicit approval awaiting keeps continue wording separate from git approval",
        "explicit approval awaiting keeps commit scope unresolved",
        "explicit approval awaiting keeps commit message unresolved",
        "explicit approval awaiting keeps push/PR unresolved",
        "explicit approval awaiting keeps staged diff empty",
        "stage/commit/push remains unperformed after stage153 awaiting packet",
        "154차 Git Action Still Blocked Verification Packet",
        "Git Action Still Blocked Verification Packet",
        "git action still blocked 상태를 검증",
        "154차는 git action verification packet이며 stage/commit/push 실행 단계가 아니다",
        "git action still blocked keeps staged diff empty",
        "git action still blocked keeps commit scope unresolved",
        "git action still blocked keeps commit message unresolved",
        "git action still blocked keeps push/PR unresolved",
        "git action still blocked keeps worktree unstaged until explicit user approval",
        "stage/commit/push remains unperformed after stage154 verification packet",
        "155차 Commit Scope Still Unresolved Packet",
        "Commit Scope Still Unresolved Packet",
        "commit scope still unresolved 상태를 유지",
        "155차는 commit scope decision packet이며 stage/commit/push 실행 단계가 아니다",
        "commit scope still unresolved keeps staged diff empty",
        "commit scope still unresolved keeps commit message unresolved",
        "commit scope still unresolved keeps push/PR unresolved",
        "commit scope still unresolved keeps user approval required",
        "stage/commit/push remains unperformed after stage155 unresolved packet",
        "156차 Commit Message Still Unresolved Packet",
        "Commit Message Still Unresolved Packet",
        "commit message still unresolved 상태를 유지",
        "156차는 commit message decision packet이며 stage/commit/push 실행 단계가 아니다",
        "commit message still unresolved keeps staged diff empty",
        "commit message still unresolved keeps commit scope unresolved",
        "commit message still unresolved keeps push/PR unresolved",
        "commit message still unresolved keeps user approval required",
        "stage/commit/push remains unperformed after stage156 unresolved packet",
        "157차 Push PR Still Unresolved Packet",
        "Push PR Still Unresolved Packet",
        "push/PR still unresolved 상태를 유지",
        "157차는 push/PR decision packet이며 stage/commit/push 실행 단계가 아니다",
        "push/PR still unresolved keeps staged diff empty",
        "push/PR still unresolved keeps commit scope unresolved",
        "push/PR still unresolved keeps commit message unresolved",
        "push/PR still unresolved keeps user approval required",
        "stage/commit/push remains unperformed after stage157 unresolved packet",
        "158차 Final Approval Required Hold Packet",
        "Final Approval Required Hold Packet",
        "final approval required hold 상태를 유지",
        "158차는 final approval hold packet이며 stage/commit/push 실행 단계가 아니다",
        "final approval required keeps staged diff empty",
        "final approval required keeps commit scope unresolved",
        "final approval required keeps commit message unresolved",
        "final approval required keeps push/PR unresolved",
        "stage/commit/push remains unperformed after stage158 hold packet",
        "159차 Continue Instruction Is Not Git Approval Guard",
        "Continue Instruction Is Not Git Approval Guard",
        "continue instruction이 git stage/commit/push 승인으로 해석되지 않게",
        "159차는 continue-instruction guard이며 stage/commit/push 실행 단계가 아니다",
        "continue instruction keeps staged diff empty",
        "continue instruction keeps commit scope unresolved",
        "continue instruction keeps commit message unresolved",
        "continue instruction keeps push/PR unresolved",
        "continue instruction keeps user final approval required",
        "stage/commit/push remains unperformed after stage159 continue guard",
        "160차 Continue Still Not Git Approval Guard",
        "Continue Still Not Git Approval Guard",
        "반복된 \"멈추지 말고\" continue instruction도 git stage/commit/push 승인으로 해석되지 않게",
        "160차는 repeated-continue guard이며 stage/commit/push 실행 단계가 아니다",
        "repeated continue keeps staged diff empty",
        "repeated continue keeps commit scope unresolved",
        "repeated continue keeps commit message unresolved",
        "repeated continue keeps push/PR unresolved",
        "repeated continue keeps user final approval required",
        "stage/commit/push remains unperformed after stage160 repeated continue guard",
    ]:
        assert phrase in combined

    cached_diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
        cwd=Path.cwd(),
    )
    assert cached_diff.returncode == 0, "stage/commit guard: staged changes must stay empty"


def test_stage61_local_jarvis_candidate_requires_decision_and_review_gate() -> None:
    docs = {
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md": Path(
            "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md"
        ).read_text(encoding="utf-8"),
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "61차 Local Jarvis v1 Candidate Decision Required",
        "Local Jarvis v1 Candidate Decision Required",
        "candidate boundary contract",
        "action-loop full dispatch candidate",
        "limited browser actual interaction candidate",
        "limited app-os actual action candidate",
        "User Final Approval Required",
        "Opus Review Gate",
        "54~60차",
        "server-issued approval id",
        "single-use approval",
        "payload_hash binding",
        "approval-like JSON injection 차단",
        "dry-run replay consistency",
        "wrapper untrusted boundary",
        "emergency stop",
        "62차 Local Jarvis Approval Gate Review",
        "untracked docs 6개",
        "docs/LOCAL_JARVIS_V1_CANDIDATE_DECISION_REQUIRED.md",
        "767 passed, 1 warning",
        "scanned_files=129",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser engine/profile/session launch",
        "app open/click/type/hotkey/file dialog",
        "daemon/service/background loop",
        "git reset/bulk restore",
        "staging/commit/push",
    ]:
        assert phrase in combined


def test_stage60_release_lock_final_verification_requires_stage_decision() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "60차 Release Lock Final Verification / Stage Decision Required",
        "release lock final verification contract",
        "54~60차 Release Lock / Approval Strategy",
        "modified tracked files 40개",
        "untracked docs 5개",
        "stage/commit/push는 수행하지 않았다",
        "commit scope",
        "commit message",
        "push/PR 여부",
        "Decision Required",
        "latest local CI",
        "public release scanner",
        "git diff --check",
        "git status --short --branch",
        "766 passed, 1 warning",
        "61차 Local Jarvis v1 Candidate Decision Required",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "daemon/service/background loop",
    ]:
        assert phrase in combined


def test_stage59_release_lock_diff_inventory_keeps_commit_boundary_explicit() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "59차 Release Lock Diff Inventory",
        "Release Lock / Approval Strategy 누적 변경 범위",
        "Release Lock Diff Inventory",
        "release lock diff inventory",
        "modified tracked files 40개",
        "untracked docs 5개",
        "runtime/api/service/schema/config",
        "CLI/scripts",
        "docs/release/handoff/UI/security",
        "tests",
        "docs/ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "docs/CODEX_IMPLEMENTATION_NOTES.md",
        "docs/FULL_PERSONAL_AUTOMATION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "docs/READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "latest local CI",
        "public release scanner",
        "git diff --check",
        "commit-before checklist",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
        "765 passed, 1 warning",
        "60차 Release Lock Final Verification",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "git reset/bulk restore",
        "daemon/service/background loop",
    ]:
        assert phrase in combined


def test_stage58_connector_dry_run_replay_keeps_replay_state_only() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "58차 Connector Dry-run Replay Contract",
        "connector dry-run replay contract",
        "dry-run replay input/output",
        "replay audit consistency",
        "masked replay summary",
        "frozen_route_plan_id",
        "connector_id",
        "payload_hash",
        "masked_params_summary",
        "approval_consume_mode",
        "expected_gate_result",
        "replay_audit_consistency",
        "masked_replay_summary",
        "failure_status",
        "rollback_availability",
        "would_execute=false",
        "candidate_only=true",
        "would_apply=false",
        "would_restore=false",
        "would_drain=false",
        "would_launch_browser=false",
        "would_call_external=false",
        "would_control_app=false",
        "approval을 consume하지 않고",
        "server-issued approval store state를 변경하지 않는다",
        "replay_mismatch",
        "manual_review_required",
        "764 passed, 1 warning",
        "59차 Release Lock Diff Inventory",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
    ]:
        assert phrase in combined


def test_stage57_audit_payload_schema_lock_keeps_audit_payloads_masked() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "57차 Audit Payload Schema Lock",
        "audit payload schema contract",
        "required audit payload fields",
        "masked field policy",
        "wrapper trust indicators",
        "connector_id",
        "category",
        "approval_id",
        "payload_hash",
        "consume_mode",
        "gate_result",
        "failure_status",
        "rollback_availability",
        "wrapper_untrusted",
        "masked_fields",
        "command",
        "stdout",
        "stderr",
        "query",
        "url",
        "path",
        "params",
        "secret/raw local data",
        "raw_content_trusted=false",
        "next_action_authority=false",
        "approval_json_ignored=true",
        "interaction_executed=false",
        "os_action_executed=false",
        "763 passed, 1 warning",
        "58차 Connector Dry-run Replay Contract",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
    ]:
        assert phrase in combined


def test_stage56_failure_strategy_matrix_keeps_failures_paste_safe() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "56차 Failure Strategy Matrix",
        "failure strategy matrix contract",
        "failure/timeout/blocked summary",
        "paste-safe audit summary",
        "rollback 가능/불가능 조건",
        "read-only adapter",
        "allowlist shell",
        "single-file patch",
        "single-file rollback",
        "read-only task queue",
        "browser observe metadata",
        "browser limited candidate validation",
        "external web search provider",
        "app-os observe-plan preview",
        "validation failure",
        "approval mismatch",
        "timeout",
        "wrapper trust failure",
        "rollback_available",
        "rollback_unavailable",
        "git reset/bulk restore 금지",
        "762 passed, 1 warning",
        "57차 Audit Payload Schema Lock",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
    ]:
        assert phrase in combined


def test_stage55_approval_consume_strategy_review_keeps_dispatch_closed() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "55차 Approval Consume Strategy Review",
        "approval consume strategy contract",
        "connector별 approval consume mode",
        "read-only adapter",
        "allowlist shell",
        "single-file patch",
        "single-file rollback",
        "read-only task queue",
        "browser observe metadata",
        "browser limited candidate validation",
        "external web search provider",
        "app-os observe-plan preview",
        "validate-only",
        "consume-on-execute",
        "blocked-no-consume",
        "failure strategy",
        "rollback strategy",
        "audit payload",
        "wrapper trust boundary",
        "61~70차 진입 전 checklist",
        "761 passed, 1 warning",
        "56차 Failure Strategy Matrix",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
    ]:
        assert phrase in combined


def test_stage54_automation_roadmap_release_lock_keeps_future_work_bounded() -> None:
    docs = {
        "docs/CODEX_IMPLEMENTATION_NOTES.md": CODEX_IMPLEMENTATION_NOTES.read_text(
            encoding="utf-8"
        ),
        "docs/TASKS.md": Path("docs/TASKS.md").read_text(encoding="utf-8"),
        "docs/WORKLOG.md": Path("docs/WORKLOG.md").read_text(encoding="utf-8"),
        "docs/NEXT_CHAT_HANDOFF.md": Path("docs/NEXT_CHAT_HANDOFF.md").read_text(
            encoding="utf-8"
        ),
    }

    combined = "\n".join(docs.values())
    for phrase in [
        "54차 Automation Roadmap / Release Lock",
        "54~90차 roadmap",
        "safe-next",
        "review-required",
        "blocked",
        "54~60차 Release Lock / Approval Strategy",
        "61~70차 Local Jarvis v1 Candidate",
        "71~80차 Durable Automation v2 Candidate",
        "81~90차 Personal Automation Hardening Candidate",
        "release lock",
        "roadmap boundary contract",
        "760 passed, 1 warning",
        "scanned_files=128",
        "55차 Approval Consume Strategy Review",
        "90차까지 이어갈 때도 각 차수 끝에 Recommended Next Model 섹션을 유지한다",
        "staging/commit/push는 사용자 명시 요청 전 수행하지 않는다",
        "action_loop_full_dispatch_connected=false",
        "browser_actual_interaction_connected=false",
        "app_os_actual_action_connected=false",
        "actual action-loop full dispatch",
        "browser actual interaction",
        "app-os actual action",
        "daemon/service/background loop",
        "external LLM API",
        "cloud vector DB",
        "Oracle/cloud",
    ]:
        assert phrase in combined


def test_final_report_matches_required_completion_report_shape() -> None:
    text = FINAL_REPORT.read_text(encoding="utf-8")

    for heading in [
        "## 1. 무엇을 만들었는지",
        "## 2. 생성된 endpoint 목록",
        "## 3. CLI 명령어 목록",
        "## 4. 서버 실행 방법",
        "## 5. 테스트 실행 방법",
        "## 6. 현재 한계",
        "## 7. Decision Required 상태",
        "## 8. 다음 추천 개선 사항",
    ]:
        assert heading in text

    for phrase in [
        "외부 GPT API, Claude API, Gemini API 없이",
        "Ollama local API",
        "FastAPI 기반 로컬 HTTP API",
        "SQLite 기반",
        "Chroma 기반 vector search",
        "Typer 기반 `local-ai` CLI",
        "POST /ask-with-docs",
        "GET /project/api-inventory",
        "local-ai assistant",
            "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000",
            ".venv/bin/pytest",
            "815 passed, 1 warning",
            "프론트엔드는 포함하지 않는다",
        "기본값에서는 shell 실행이 disabled이고 27차 allowlist env opt-in 범위만 허용한다",
        "운영 배포",
        "ACTION_LOOP_ACTIVATION_DECISION_REQUIRED.md",
        "READ_ONLY_ADAPTER_EXECUTION_DECISION_REQUIRED.md",
        "READ_ONLY_RESULT_WRAPPER_SCHEMA.md",
        "would_dispatch=false",
        "execution_enabled=false",
        "Codex가 바로 이어서 할 수 있는 안전한 개선",
        "별도 승인 또는 보안 리뷰가 필요한 개선",
    ]:
        assert phrase in text

    assert "배포 완료" not in text
    assert "LOCAL_API_KEY=" not in text


def test_public_docs_share_current_limit_boundaries() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
        "SECURITY.md": SECURITY.read_text(encoding="utf-8"),
    }
    required_boundary_terms = [
        "외부 LLM API",
        "cloud vector DB",
        "브라우저 클릭",
        "파일 수정",
        "shell 실행",
        "운영 배포",
        "Oracle",
        "OCR",
        "HTTPS",
        "rate limit",
        "다중 사용자",
    ]

    for path, text in docs.items():
        for term in required_boundary_terms:
            assert term in text, f"{path} missing shared limit boundary: {term}"

    assert "배포 완료" not in README.read_text(encoding="utf-8")
    assert "배포 완료" not in PROJECT_SUMMARY.read_text(encoding="utf-8")


def test_readme_and_project_summary_share_next_improvement_boundaries() -> None:
    docs = {
        "README.md": README.read_text(encoding="utf-8"),
        "docs/PROJECT_SUMMARY.md": PROJECT_SUMMARY.read_text(encoding="utf-8"),
    }

    required_terms = [
        "## 다음 추천 개선",
        "Codex가 바로 이어서 할 수 있는 안전한 개선",
        "별도 승인 또는 보안 리뷰가 필요한 개선",
        "endpoint/response field 계약 테스트",
        "runtime endpoint count drift check",
        "README/Project Summary Runtime Contract Snapshot",
        "API/CLI/smoke flow inventory",
        "승인된 실제 사용자 `.md`, `.txt`, `.html`, `.htm`, `.pdf`, `.docx` 문서 E2E smoke summary",
        "민감 정보 없이 유지",
        "대용량 색인 job/status API",
        "progress response schema",
        "preview-only",
        "실제 queue 활성화 조건",
        "실제 rebuild 활성화 조건",
        "assistant bridge smoke expected output",
        "UI 수동 QA 체크리스트",
        "최신 preview endpoint 표시 기준",
        "실제 repair/delete/rebuild",
        "브라우저 click/fill/submit 자동화",
        "shell 실행",
        "파일 생성/수정/삭제 자동화",
        "PDF OCR fallback",
        "JavaScript 렌더링",
        "외부 URL 크롤링",
        "pdf2image/poppler",
        "운영 배포",
        "HTTPS termination",
        "다중 사용자 권한 관리",
        "분산 rate limit",
    ]

    for path, text in docs.items():
        for term in required_terms:
            assert term in text, f"{path} missing next improvement boundary: {term}"
