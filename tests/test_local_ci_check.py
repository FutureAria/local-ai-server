import subprocess
import sys
from pathlib import Path

import scripts.local_ci_check as local_ci


def test_build_check_commands_are_fixed_safe_project_checks() -> None:
    commands = local_ci.build_check_commands(Path("."))

    assert [item["name"] for item in commands] == [
        "pytest",
        "compileall",
        "public-release-check",
        "git-diff-check",
    ]
    assert commands[0]["command"] == [sys.executable, "-m", "pytest"]
    assert commands[1]["command"] == [sys.executable, "-m", "compileall", "app", "cli", "scripts"]
    assert commands[2]["command"][:2] == [sys.executable, "scripts/public_release_check.py"]
    assert "--json" in commands[2]["command"]
    assert commands[3]["command"] == ["git", "diff", "--check"]


def test_run_local_ci_check_stops_on_first_failure(monkeypatch, tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(
            args=command,
            returncode=1 if command[:3] == [sys.executable, "-m", "compileall"] else 0,
            stdout="out",
            stderr="err" if command[:3] == [sys.executable, "-m", "compileall"] else "",
        )

    monkeypatch.setattr(local_ci.subprocess, "run", fake_run)

    result = local_ci.run_local_ci_check(tmp_path)

    assert result["ok"] is False
    assert [step["name"] for step in result["steps"]] == ["pytest", "compileall"]
    assert calls == [
        [sys.executable, "-m", "pytest"],
        [sys.executable, "-m", "compileall", "app", "cli", "scripts"],
    ]


def test_run_local_ci_check_returns_all_steps_when_success(monkeypatch, tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(local_ci.subprocess, "run", fake_run)

    result = local_ci.run_local_ci_check(tmp_path)

    assert result["ok"] is True
    assert [step["name"] for step in result["steps"]] == [
        "pytest",
        "compileall",
        "public-release-check",
        "git-diff-check",
    ]
    assert len(calls) == 4


def test_run_local_ci_check_uses_project_root_and_captures_output(monkeypatch, tmp_path) -> None:
    observed_kwargs = []

    def fake_run(command, **kwargs):
        observed_kwargs.append(kwargs)
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="safe", stderr="")

    monkeypatch.setattr(local_ci.subprocess, "run", fake_run)

    result = local_ci.run_local_ci_check(tmp_path)

    public_release_step = result["steps"][2]
    assert public_release_step["name"] == "public-release-check"
    assert public_release_step["command"] == [
        sys.executable,
        "scripts/public_release_check.py",
        "--root",
        str(tmp_path.resolve()),
        "--json",
    ]
    assert result["steps"][3]["command"] == ["git", "diff", "--check"]
    assert all(kwargs["cwd"] == tmp_path.resolve() for kwargs in observed_kwargs)
    assert all(kwargs["capture_output"] is True for kwargs in observed_kwargs)
    assert all(kwargs["text"] is True for kwargs in observed_kwargs)
    assert all(kwargs["check"] is False for kwargs in observed_kwargs)
