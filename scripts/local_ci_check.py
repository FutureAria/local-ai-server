import argparse
import json
import subprocess
import sys
from pathlib import Path


def build_check_commands(root: Path) -> list[dict]:
    python = sys.executable
    return [
        {
            "name": "pytest",
            "command": [python, "-m", "pytest"],
        },
        {
            "name": "compileall",
            "command": [python, "-m", "compileall", "app", "cli", "scripts"],
        },
        {
            "name": "public-release-check",
            "command": [python, "scripts/public_release_check.py", "--root", str(root), "--json"],
        },
        {
            "name": "git-diff-check",
            "command": ["git", "diff", "--check"],
        },
    ]


def run_local_ci_check(root: Path) -> dict:
    root = root.resolve()
    steps = []
    for item in build_check_commands(root):
        result = subprocess.run(
            item["command"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        steps.append(
            {
                "name": item["name"],
                "command": item["command"],
                "returncode": result.returncode,
                "ok": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.returncode != 0:
            break

    return {
        "ok": all(step["ok"] for step in steps),
        "root": str(root),
        "steps": steps,
    }


def _print_human(result: dict) -> None:
    print(f"ok={result['ok']} root={result['root']}")
    for step in result["steps"]:
        status = "ok" if step["ok"] else "failed"
        print(f"[{status}] {step['name']}: {' '.join(step['command'])}")
        if step["stdout"].strip():
            print(step["stdout"].rstrip())
        if step["stderr"].strip():
            print(step["stderr"].rstrip(), file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local CI checks for local-ai-server.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = run_local_ci_check(Path(args.root))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human(result)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
