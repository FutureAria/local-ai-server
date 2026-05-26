from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.public_release_check import PUBLIC_RELEASE_PRIVATE_DATA, run_public_release_check


@pytest.mark.parametrize(
    ("relative_path", "content"),
    [
        (".env", "LOCAL_API_KEY=" + "a" * 24),
        (".env.local", "LOCAL_API_KEY=" + "a" * 24),
        (".env.production", "LOCAL_API_KEY=" + "a" * 24),
        (".ENV", "LOCAL_API_KEY=" + "a" * 24),
        (".envrc", "export LOCAL_API_KEY=" + "a" * 24),
        (".npmrc", "//registry.npmjs.org/:_authToken=" + "a" * 24),
        (".pypirc", "password=" + "a" * 24),
        (".netrc", "machine example.test login user password " + "a" * 24),
        (".aws/credentials", "aws_access_key_id=" + "A" * 20),
        (".gcloud/application_default_credentials.json", "{}"),
        (".azure/accessTokens.json", "{}"),
        (".kube/config", "apiVersion: v1"),
        ("secrets/local.key", "key"),
        ("secrets/local.pem", "pem"),
        ("secrets/LOCAL.PEM", "pem"),
        ("secrets/local.crt", "crt"),
        ("secrets/local.cer", "cer"),
        ("secrets/local.p12", "p12"),
        ("secrets/local.pfx", "pfx"),
        ("secrets/id_rsa", "ssh"),
        ("secrets/ID_RSA", "ssh"),
        ("secrets/id_ed25519", "ssh"),
        ("data/local_ai.sqlite3", "sqlite"),
        ("data/local_ai.sqlite3-wal", "wal"),
        ("data/local_ai.sqlite", "sqlite"),
        ("data/local_ai.sqlite-wal", "wal"),
        ("data/local_ai.sqlite-shm", "shm"),
        ("data/local_ai.db", "db"),
        ("data/local_ai.db-journal", "journal"),
        ("data/chroma/index.bin", "vector"),
        ("data/uploads/private.md", "notes"),
        ("data/logs/app.log", "log"),
        ("logs/app.log", "log"),
        ("app.log", "log"),
        ("data/sft_dataset.jsonl", "{}\n"),
    ],
)
def test_public_release_check_flags_all_private_data_patterns(
    tmp_path: Path,
    relative_path: str,
    content: str,
) -> None:
    target = tmp_path / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    paths = {finding["path"] for finding in result["findings"]}
    assert relative_path in paths


def test_public_release_check_flags_local_data_and_secret_candidate(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# ok", encoding="utf-8")
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "local_ai.sqlite3").write_text("sqlite", encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    paths = {finding["path"] for finding in result["findings"]}
    assert ".env" in paths
    assert "data/local_ai.sqlite3" in paths


@pytest.mark.parametrize(
    "content",
    [
        "OPENAI_API_KEY=" + "sk-" + "a" * 24,
        '"api_key": "' + "a" * 24 + '"',
        '"credential": "' + "a" * 24 + '"',
        "token: " + "a" * 24,
        "Authorization: Bearer " + "a" * 24,
        "github token " + "ghp_" + "a" * 36,
        "gitlab token " + "glpat-" + "a" * 20,
        "huggingface token " + "hf_" + "a" * 30,
        "slack token " + "xoxb-" + "a" * 24,
        "google api key " + "AIza" + "A" * 35,
        "aws key " + "AKIA" + "A" * 16,
        "-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END " + "PRIVATE KEY-----",
    ],
)
def test_public_release_check_flags_secret_text_patterns(tmp_path: Path, content: str) -> None:
    (tmp_path / "docs.md").write_text(content, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == "docs.md"
    assert "secret" in result["findings"][0]["message"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "setup.sh",
        "settings.ini",
        "app.conf",
        "app.properties",
        "settings.xml",
        "build.gradle",
        "build.gradle.kts",
        "query.gql",
        "query.graphql",
        "poetry.lock",
        "schema.sql",
        "main.tf",
        "terraform.tfvars",
        "terragrunt.hcl",
        "setup.ps1",
        "setup.bat",
        "setup.cmd",
        "export.csv",
        "export.tsv",
        "request.http",
        "request.rest",
        "analysis.ipynb",
    ],
)
def test_public_release_check_scans_common_config_and_script_files(
    tmp_path: Path,
    relative_path: str,
) -> None:
    (tmp_path / relative_path).write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == relative_path


def test_public_release_check_flags_unreadable_text_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# ok", encoding="utf-8")

    with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
        result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == "README.md"
    assert "읽을 수 없습니다" in result["findings"][0]["message"]


def test_public_release_check_allows_documentation_placeholders(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "X-API-Key: <LOCAL_API_KEY>",
                "Authorization: Bearer <LOCAL_API_KEY>",
                "LOCAL_AI_SERVER_URL=http://127.0.0.1:8000",
            ]
        ),
        encoding="utf-8",
    )

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["findings"] == []


def test_public_release_check_allows_gitkeep_files(tmp_path: Path) -> None:
    uploads = tmp_path / "data" / "uploads"
    uploads.mkdir(parents=True)
    (uploads / ".gitkeep").write_text("", encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["findings"] == []


def test_public_release_check_allows_env_example(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text("LOCAL_API_KEY=\n", encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["findings"] == []


def test_public_release_private_data_is_documented_and_ignored() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    release_checklist = Path("docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    public_summary = Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(encoding="utf-8")

    gitignore_coverage = {
        ".env": [".env"],
        ".env.*": [".env.*", "!.env.example"],
        ".envrc": [".envrc"],
        ".npmrc": [".npmrc"],
        ".pypirc": [".pypirc"],
        ".netrc": [".netrc"],
        ".aws/": [".aws/"],
        ".gcloud/": [".gcloud/"],
        ".azure/": [".azure/"],
        ".kube/": [".kube/"],
        "*.key": ["*.key"],
        "*.pem": ["*.pem"],
        "*.crt": ["*.crt"],
        "*.cer": ["*.cer"],
        "*.p12": ["*.p12"],
        "*.pfx": ["*.pfx"],
        "id_rsa": ["id_rsa"],
        "id_ed25519": ["id_ed25519"],
        "data/local_ai.sqlite3": ["data/*.sqlite3", "data/*.sqlite3-*"],
        "data/*.sqlite": ["data/*.sqlite"],
        "data/*.sqlite-*": ["data/*.sqlite-*"],
        "data/*.db": ["data/*.db"],
        "data/*.db-*": ["data/*.db-*"],
        "data/chroma/": ["data/chroma/*", "!data/chroma/.gitkeep"],
        "data/uploads/": ["data/uploads/*", "!data/uploads/.gitkeep"],
        "data/logs/": ["data/logs/*", "!data/logs/.gitkeep"],
        "logs/": ["logs/*", "!logs/.gitkeep"],
        "*.log": ["*.log"],
        "data/*.jsonl": ["data/*.jsonl"],
    }

    assert set(PUBLIC_RELEASE_PRIVATE_DATA) == set(gitignore_coverage)
    for item in PUBLIC_RELEASE_PRIVATE_DATA:
        assert item in release_checklist
        assert item in public_summary
        for ignored_pattern in gitignore_coverage[item]:
            assert ignored_pattern in gitignore
