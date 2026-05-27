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
    ".envrc",
    ".npmrc",
    ".yarnrc",
    ".yarnrc.yml",
    ".pnpmrc",
    ".pypirc",
    "pip.conf",
    ".config/pip/pip.conf",
    ".config/pypoetry/auth.toml",
    "pypoetry/auth.toml",
    ".netrc",
    ".git-credentials",
    ".boto",
    ".s3cfg",
    ".pgpass",
    ".sentryclirc",
    "auth.json",
    ".terraformrc",
    "terraform.rc",
    "secrets/",
    ".secrets/",
    ".ssh/",
    ".gnupg/",
    ".password-store/",
    ".vault-token",
    ".config/doppler/config.yaml",
    ".config/infisical/infisical-config.json",
    ".config/op/config",
    ".config/1Password/credentials.json",
    ".config/sops/age/keys.txt",
    ".docker/",
    ".config/containers/auth.json",
    ".config/helm/registry/config.json",
    ".config/helm/repositories.yaml",
    ".config/hub",
    ".config/gh/hosts.yml",
    ".config/gh/hosts.yaml",
    ".config/doctl/config.yaml",
    ".config/doctl/config.yml",
    ".vercel/auth.json",
    ".netlify/config.json",
    ".fly/config.yml",
    ".fly/config.yaml",
    ".openai/",
    ".config/openai/",
    ".anthropic/",
    ".claude.json",
    ".claude/settings.local.json",
    ".gemini/settings.json",
    ".config/gemini/settings.json",
    ".postman/",
    ".config/Postman/",
    ".insomnia/",
    ".config/Insomnia/",
    ".httpie/",
    ".config/httpie/",
    ".bruno/",
    ".cursor/mcp.json",
    ".cursor/settings.json",
    ".continue/config.json",
    ".aider.conf.yml",
    ".aider.env",
    ".codeium/config.json",
    ".config/Codeium/config.json",
    ".gem/credentials",
    ".cargo/credentials",
    ".cargo/credentials.toml",
    ".composer/auth.json",
    ".config/composer/auth.json",
    ".condarc",
    ".config/conda/condarc",
    ".continuum/anaconda-client/tokens",
    ".dbt/profiles.yml",
    ".databrickscfg",
    ".config/databricks/credentials",
    ".snowsql/config",
    ".config/snowflake/config.toml",
    ".huggingface/token",
    ".cache/huggingface/token",
    ".cache/huggingface/stored_tokens",
    ".config/huggingface/token",
    ".kaggle/kaggle.json",
    ".config/kaggle/kaggle.json",
    ".wandb/settings",
    ".config/wandb/settings",
    ".gradle/gradle.properties",
    ".m2/settings.xml",
    "NuGet.Config",
    "nuget.config",
    ".nuget/NuGet/NuGet.Config",
    ".pulumi/credentials.json",
    ".aws/",
    ".gcloud/",
    ".config/gcloud/application_default_credentials.json",
    ".config/gcloud/credentials.db",
    ".config/gcloud/access_tokens.db",
    ".config/gcloud/legacy_credentials/",
    "clouds.yaml",
    "secure.yaml",
    ".config/openstack/clouds.yaml",
    ".config/openstack/secure.yaml",
    "rclone.conf",
    ".config/rclone/rclone.conf",
    ".azure/",
    ".kube/",
    ".oci/",
    ".oraclebmc/",
    "kubeconfig",
    "kube.config",
    "credentials.json",
    "application_default_credentials.json",
    "client_secret*.json",
    "service-account*.json",
    "firebase-adminsdk*.json",
    "google-credentials*.json",
    "*.key",
    "*.pem",
    "*.crt",
    "*.cer",
    "*.der",
    "*.csr",
    "*.p7b",
    "*.p7c",
    "*.p12",
    "*.pfx",
    "*.jks",
    "*.keystore",
    "*.truststore",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ecdsa_sk",
    "id_ed25519",
    "id_ed25519_sk",
    "data/local_ai.sqlite3",
    "data/*.sqlite3",
    "data/*.sqlite3-*",
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
    "*.tfstate",
    "*.tfstate.*",
    "Pulumi.*.yaml",
    "Pulumi.*.json",
    ".vault_pass",
    ".vault_password",
    "*.vault",
)

SENSITIVE_PATH_PATTERNS = [
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"(^|/)\.envrc$", re.IGNORECASE),
    re.compile(r"(^|/)\.npmrc$", re.IGNORECASE),
    re.compile(r"(^|/)\.yarnrc$", re.IGNORECASE),
    re.compile(r"(^|/)\.yarnrc\.yml$", re.IGNORECASE),
    re.compile(r"(^|/)\.pnpmrc$", re.IGNORECASE),
    re.compile(r"(^|/)\.pypirc$", re.IGNORECASE),
    re.compile(r"(^|/)pip\.conf$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/pip/pip\.conf$", re.IGNORECASE),
    re.compile(r"(^|/)(\.config/)?pypoetry/auth\.toml$", re.IGNORECASE),
    re.compile(r"(^|/)\.netrc$", re.IGNORECASE),
    re.compile(r"(^|/)\.git-credentials$", re.IGNORECASE),
    re.compile(r"(^|/)\.boto$", re.IGNORECASE),
    re.compile(r"(^|/)\.s3cfg$", re.IGNORECASE),
    re.compile(r"(^|/)\.pgpass$", re.IGNORECASE),
    re.compile(r"(^|/)\.sentryclirc$", re.IGNORECASE),
    re.compile(r"(^|/)auth\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.terraformrc$", re.IGNORECASE),
    re.compile(r"(^|/)terraform\.rc$", re.IGNORECASE),
    re.compile(r"(^|/)secrets/"),
    re.compile(r"(^|/)\.secrets/"),
    re.compile(r"(^|/)\.ssh/"),
    re.compile(r"(^|/)\.gnupg/"),
    re.compile(r"(^|/)\.password-store/"),
    re.compile(r"(^|/)\.vault-token$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/doppler/config\.yaml$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/infisical/infisical-config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/op/config$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/1Password/credentials\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/sops/age/keys\.txt$", re.IGNORECASE),
    re.compile(r"(^|/)\.docker/"),
    re.compile(r"(^|/)\.config/containers/auth\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/helm/registry/config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/helm/repositories\.yaml$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/hub$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/gh/hosts\.ya?ml$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/doctl/config\.ya?ml$", re.IGNORECASE),
    re.compile(r"(^|/)\.vercel/auth\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.netlify/config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.fly/config\.ya?ml$", re.IGNORECASE),
    re.compile(r"(^|/)\.openai/"),
    re.compile(r"(^|/)\.config/openai/"),
    re.compile(r"(^|/)\.anthropic/"),
    re.compile(r"(^|/)\.claude\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.claude/settings\.local\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.gemini/settings\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/gemini/settings\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.postman/"),
    re.compile(r"(^|/)\.config/Postman/", re.IGNORECASE),
    re.compile(r"(^|/)\.insomnia/"),
    re.compile(r"(^|/)\.config/Insomnia/", re.IGNORECASE),
    re.compile(r"(^|/)\.httpie/"),
    re.compile(r"(^|/)\.config/httpie/", re.IGNORECASE),
    re.compile(r"(^|/)\.bruno/"),
    re.compile(r"(^|/)\.cursor/(mcp|settings)\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.continue/config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.aider\.conf\.yml$", re.IGNORECASE),
    re.compile(r"(^|/)\.aider\.env$", re.IGNORECASE),
    re.compile(r"(^|/)\.codeium/config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/Codeium/config\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.gem/credentials$", re.IGNORECASE),
    re.compile(r"(^|/)\.cargo/credentials(\.toml)?$", re.IGNORECASE),
    re.compile(r"(^|/)(\.config/)?composer/auth\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.condarc$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/conda/condarc$", re.IGNORECASE),
    re.compile(r"(^|/)\.continuum/anaconda-client/tokens$", re.IGNORECASE),
    re.compile(r"(^|/)\.dbt/profiles\.yml$", re.IGNORECASE),
    re.compile(r"(^|/)\.databrickscfg$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/databricks/credentials$", re.IGNORECASE),
    re.compile(r"(^|/)\.snowsql/config$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/snowflake/config\.toml$", re.IGNORECASE),
    re.compile(r"(^|/)\.(cache/|config/)?huggingface/(token|stored_tokens)$", re.IGNORECASE),
    re.compile(r"(^|/)\.(config/)?kaggle/kaggle\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.(config/)?wandb/settings$", re.IGNORECASE),
    re.compile(r"(^|/)\.gradle/gradle\.properties$", re.IGNORECASE),
    re.compile(r"(^|/)\.m2/settings\.xml$", re.IGNORECASE),
    re.compile(r"(^|/)(\.nuget/NuGet/)?NuGet\.Config$", re.IGNORECASE),
    re.compile(r"(^|/)\.pulumi/credentials\.json$", re.IGNORECASE),
    re.compile(r"(^|/)\.aws/"),
    re.compile(r"(^|/)\.gcloud/"),
    re.compile(
        r"(^|/)\.config/gcloud/(application_default_credentials\.json|credentials\.db|access_tokens\.db)$",
        re.IGNORECASE,
    ),
    re.compile(r"(^|/)\.config/gcloud/legacy_credentials/"),
    re.compile(r"(^|/)clouds\.yaml$", re.IGNORECASE),
    re.compile(r"(^|/)secure\.yaml$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/openstack/(clouds|secure)\.yaml$", re.IGNORECASE),
    re.compile(r"(^|/)rclone\.conf$", re.IGNORECASE),
    re.compile(r"(^|/)\.config/rclone/rclone\.conf$", re.IGNORECASE),
    re.compile(r"(^|/)\.azure/"),
    re.compile(r"(^|/)\.kube/"),
    re.compile(r"(^|/)\.oci/"),
    re.compile(r"(^|/)\.oraclebmc/"),
    re.compile(r"(^|/)kube\.?config$", re.IGNORECASE),
    re.compile(r"(^|/)credentials\.json$", re.IGNORECASE),
    re.compile(r"(^|/)application_default_credentials\.json$", re.IGNORECASE),
    re.compile(r"(^|/)client_secret[^/]*\.json$", re.IGNORECASE),
    re.compile(r"(^|/)service-account[^/]*\.json$", re.IGNORECASE),
    re.compile(r"(^|/)firebase-adminsdk[^/]*\.json$", re.IGNORECASE),
    re.compile(r"(^|/)google-credentials[^/]*\.json$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.key$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.pem$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.crt$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.cer$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.der$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.csr$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.p7b$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.p7c$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.p12$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.pfx$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.jks$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.keystore$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.truststore$", re.IGNORECASE),
    re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ecdsa_sk|ed25519|ed25519_sk)$", re.IGNORECASE),
    re.compile(r"(^|/)data/local_ai\.sqlite3($|[-\w.])"),
    re.compile(r"(^|/)data/.*\.(sqlite3|sqlite|db)($|[-\w.])", re.IGNORECASE),
    re.compile(r"(^|/)data/chroma/"),
    re.compile(r"(^|/)data/uploads/"),
    re.compile(r"(^|/)data/logs/.*(?<!\.gitkeep)$"),
    re.compile(r"(^|/)logs/.*(?<!\.gitkeep)$"),
    re.compile(r"(^|/)[^/]+\.log$", re.IGNORECASE),
    re.compile(r"(^|/)data/.*\.jsonl$"),
    re.compile(r"(^|/)[^/]+\.tfstate($|\.)", re.IGNORECASE),
    re.compile(r"(^|/)Pulumi\.[^/]+\.(yaml|json)$"),
    re.compile(r"(^|/)\.vault_pass$", re.IGNORECASE),
    re.compile(r"(^|/)\.vault_password$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]+\.vault$", re.IGNORECASE),
]

SECRET_TEXT_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*=\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)['\"]?\s*:\s*['\"][A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?im)^\s*(api[_-]?key|secret|token|password|credential)\s*:\s*[A-Za-z0-9_\-]{16,}\s*$"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35,}\b"),
    re.compile(r"\b[A-Za-z0-9_\-]{24}\.[A-Za-z0-9_\-]{6}\.[A-Za-z0-9_\-]{27,}\b"),
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    re.compile(r"gh[ousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{30,}"),
    re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\bSG\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b[rs]k_(live|test)_[A-Za-z0-9]{20,}"),
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
            continue

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
        ".config",
        ".conf",
        ".env",
        ".example",
        ".gradle",
        ".gql",
        ".graphql",
        ".hcl",
        ".http",
        ".ini",
        ".ipynb",
        ".json",
        ".kts",
        ".lock",
        ".md",
        ".bat",
        ".cmd",
        ".csv",
        ".properties",
        ".ps1",
        ".py",
        ".rest",
        ".sh",
        ".sql",
        ".tf",
        ".tfvars",
        ".toml",
        ".tsv",
        ".txt",
        ".xml",
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
            break
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
