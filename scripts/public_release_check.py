import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "local_ai_server.egg-info",
    "node_modules",
    "venv",
}

PUBLIC_RELEASE_PRIVATE_DATA = (
    ".env",
    ".env.*",
    "*.key",
    "*.pem",
    "*.crt",
    "*.cer",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    "data/local_ai.sqlite3",
    "data/*.sqlite",
    "data/*.sqlite-*",
    "data/*.db",
    "data/*.db-*",
    "data/chroma/",
    "data/uploads/",
    "data/logs/",
    "logs/",
    "*.log",
    "data/*.jsonl",
)

SENSITIVE_PATH_PATTERNS = [
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.key$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.pem$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.crt$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.cer$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.p12$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.pfx$", re.IGNORECASE),
    re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$", re.IGNORECASE),
    re.compile(r"(^|/)data/local_ai\.sqlite3($|[-\w.])"),
    re.compile(r"(^|/)data/.*\.(sqlite|db)($|[-\w.])", re.IGNORECASE),
    re.compile(r"(^|/)data/chroma/"),
    re.compile(r"(^|/)data/uploads/"),
    re.compile(r"(^|/)data/logs/.*(?<!\.gitkeep)$"),
    re.compile(r"(^|/)logs/.*(?<!\.gitkeep)$"),
    re.compile(r"(^|/)[^/]+\.log$", re.IGNORECASE),
    re.compile(r"(^|/)data/.*\.jsonl$"),
]

SECRET_TEXT_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*=\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)['\"]?\s*:\s*['\"][A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?im)^\s*(api[_-]?key|secret|token|password|credential)\s*:\s*[A-Za-z0-9_\-]{16,}\s*$"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{30,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY"),
]


@dataclass
class Finding:
    severity: str
    path: str
    message: str


def run_public_release_check(root: Path) -> dict:
    root = root.resolve()
    findings: list[Finding] = []
    scanned_files = 0

    for path in _iter_files(root):
        relative = path.relative_to(root).as_posix()
        path_finding = _check_sensitive_path(relative)
        if path_finding is not None:
            findings.append(path_finding)

        if _should_scan_text(path):
            scanned_files += 1
            findings.extend(_scan_text_file(root, path))

    return {
        "ok": not findings,
        "root": str(root),
        "scanned_files": scanned_files,
        "findings": [asdict(finding) for finding in findings],
    }


def _iter_files(root: Path):
    git_files = _git_visible_files(root)
    if git_files is not None:
        for relative in git_files:
            path = root / relative
            if path.is_file():
                yield path
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in DEFAULT_EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def _git_visible_files(root: Path) -> list[Path] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    files = []
    for line in result.stdout.splitlines():
        if line.strip():
            files.append(Path(line.strip()))
    return files


def _check_sensitive_path(relative: str) -> Finding | None:
    if relative.lower() == ".env.example":
        return None
    if relative.endswith(".gitkeep"):
        return None
    for pattern in SENSITIVE_PATH_PATTERNS:
        if pattern.search(relative):
            return Finding(
                severity="high",
                path=relative,
                message="GitHub 공개 전 제외해야 하는 로컬 데이터 또는 민감 경로입니다.",
            )
    return None


def _should_scan_text(path: Path) -> bool:
    return path.suffix.lower() in {
        "",
        ".cfg",
        ".conf",
        ".env",
        ".example",
        ".ini",
        ".json",
        ".md",
        ".properties",
        ".py",
        ".sh",
        ".toml",
        ".txt",
        ".yml",
        ".yaml",
    }


def _scan_text_file(root: Path, path: Path) -> list[Finding]:
    relative = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    except OSError as exc:
        return [
            Finding(
                severity="high",
                path=relative,
                message=f"공개 전 점검에서 파일을 읽을 수 없습니다: {exc.__class__.__name__}",
            )
        ]

    findings = []
    for pattern in SECRET_TEXT_PATTERNS:
        if pattern.search(text):
            findings.append(
                Finding(
                    severity="high",
                    path=relative,
                    message="secret, token, password, private key로 보이는 문자열 후보가 있습니다.",
                )
            )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only GitHub/public release safety check.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()
    result = run_public_release_check(Path(args.root))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok={result['ok']} scanned_files={result['scanned_files']}")
        for finding in result["findings"]:
            print(f"[{finding['severity']}] {finding['path']}: {finding['message']}")

    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
