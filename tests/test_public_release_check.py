import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

from scripts.public_release_check import PUBLIC_RELEASE_PRIVATE_DATA, main, run_public_release_check


@pytest.mark.parametrize(
    ("relative_path", "content"),
    [
        (".env", "LOCAL_API_KEY=" + "a" * 24),
        (".env.local", "LOCAL_API_KEY=" + "a" * 24),
        (".env.production", "LOCAL_API_KEY=" + "a" * 24),
        (".ENV", "LOCAL_API_KEY=" + "a" * 24),
        (".envrc", "export LOCAL_API_KEY=" + "a" * 24),
        (".npmrc", "//registry.npmjs.org/:_authToken=" + "a" * 24),
        (".yarnrc", "npmAuthToken: " + "a" * 24),
        (".yarnrc.yml", "npmAuthToken: " + "a" * 24),
        (".pnpmrc", "//registry.npmjs.org/:_authToken=" + "a" * 24),
        (".pypirc", "password=" + "a" * 24),
        ("pip.conf", "index-url = https://user:" + "a" * 24 + "@example.test/simple"),
        (".config/pip/pip.conf", "index-url = https://user:" + "a" * 24 + "@example.test/simple"),
        (".config/pypoetry/auth.toml", 'password = "' + "a" * 24 + '"'),
        ("pypoetry/auth.toml", 'password = "' + "a" * 24 + '"'),
        (".netrc", "machine example.test login user password " + "a" * 24),
        (".git-credentials", "https://user:token@example.test"),
        (".boto", "[Credentials]"),
        (".s3cfg", "[default]"),
        (".pgpass", "localhost:5432:*:user:password"),
        (".sentryclirc", "[auth]\ntoken=" + "a" * 24),
        ("auth.json", '{"github-oauth": {"github.com": "' + "a" * 24 + '"}}'),
        (".terraformrc", 'credentials "app.terraform.io" { token = "' + "a" * 24 + '" }'),
        ("terraform.rc", 'credentials "app.terraform.io" { token = "' + "a" * 24 + '" }'),
        ("secrets/notes.txt", "secret notes"),
        (".secrets/token.txt", "secret notes"),
        (".ssh/config", "Host local"),
        (".gnupg/private-keys-v1.d/keygrip.key", "key"),
        (".password-store/example.gpg", "gpg"),
        (".vault-token", "hvs." + "a" * 24),
        (".config/doppler/config.yaml", "token: " + "a" * 24),
        (".config/infisical/infisical-config.json", '{"token": "' + "a" * 24 + '"}'),
        (".config/op/config", "session: " + "a" * 24),
        (".config/1Password/credentials.json", '{"token": "' + "a" * 24 + '"}'),
        (".config/sops/age/keys.txt", "AGE-SECRET-KEY-EXAMPLE"),
        (".docker/config.json", "{}"),
        (".config/containers/auth.json", '{"auths": {"registry.example.test": {"auth": "' + "a" * 24 + '"}}}'),
        (".config/helm/registry/config.json", '{"auths": {"registry.example.test": {"auth": "' + "a" * 24 + '"}}}'),
        (".config/helm/repositories.yaml", "password: " + "a" * 24),
        (".config/hub", "oauth_token: " + "a" * 24),
        (".config/gh/hosts.yml", "oauth_token: " + "a" * 24),
        (".config/gh/hosts.yaml", "oauth_token: " + "a" * 24),
        (".config/doctl/config.yaml", "access-token: " + "a" * 24),
        (".config/doctl/config.yml", "access-token: " + "a" * 24),
        (".vercel/auth.json", '{"token": "' + "a" * 24 + '"}'),
        (".netlify/config.json", '{"token": "' + "a" * 24 + '"}'),
        (".fly/config.yml", "access_token: " + "a" * 24),
        (".fly/config.yaml", "access_token: " + "a" * 24),
        (".openai/auth.json", '{"api_key": "sk-' + "a" * 24 + '"}'),
        (".config/openai/auth.json", '{"api_key": "sk-' + "a" * 24 + '"}'),
        (".anthropic/config.json", '{"api_key": "sk-ant-' + "a" * 32 + '"}'),
        (".claude.json", '{"apiKey": "sk-ant-' + "a" * 32 + '"}'),
        (".claude/settings.local.json", '{"apiKey": "sk-ant-' + "a" * 32 + '"}'),
        (".gemini/settings.json", '{"api_key": "AIza' + "A" * 35 + '"}'),
        (".config/gemini/settings.json", '{"api_key": "AIza' + "A" * 35 + '"}'),
        (".postman/environments/local.json", '{"token": "' + "a" * 24 + '"}'),
        (".config/Postman/environments/local.json", '{"token": "' + "a" * 24 + '"}'),
        (".insomnia/Environment/local.yml", "token: " + "a" * 24),
        (".config/Insomnia/Environment/local.yml", "token: " + "a" * 24),
        (".httpie/sessions/local.json", '{"auth": "' + "a" * 24 + '"}'),
        (".config/httpie/sessions/local.json", '{"auth": "' + "a" * 24 + '"}'),
        (".bruno/environments/local.bru", "token: " + "a" * 24),
        (".cursor/mcp.json", '{"env": {"API_KEY": "' + "a" * 24 + '"}}'),
        (".cursor/settings.json", '{"apiKey": "' + "a" * 24 + '"}'),
        (".continue/config.json", '{"apiKey": "' + "a" * 24 + '"}'),
        (".aider.conf.yml", "api-key: " + "a" * 24),
        (".aider.env", "OPENAI_API_KEY=sk-" + "a" * 24),
        (".codeium/config.json", '{"token": "' + "a" * 24 + '"}'),
        (".config/Codeium/config.json", '{"token": "' + "a" * 24 + '"}'),
        (".gem/credentials", ":rubygems_api_key: " + "a" * 24),
        (".cargo/credentials", "token = \"" + "a" * 24 + "\""),
        (".cargo/credentials.toml", "token = \"" + "a" * 24 + "\""),
        (".composer/auth.json", '{"github-oauth": {"github.com": "' + "a" * 24 + '"}}'),
        (".config/composer/auth.json", '{"github-oauth": {"github.com": "' + "a" * 24 + '"}}'),
        (".condarc", "token: " + "a" * 24),
        (".config/conda/condarc", "token: " + "a" * 24),
        (".continuum/anaconda-client/tokens", "token: " + "a" * 24),
        (".dbt/profiles.yml", "password: " + "a" * 24),
        (".databrickscfg", "token = " + "a" * 24),
        (".config/databricks/credentials", "token = " + "a" * 24),
        (".snowsql/config", "password = " + "a" * 24),
        (".config/snowflake/config.toml", 'password = "' + "a" * 24 + '"'),
        (".huggingface/token", "hf_" + "a" * 30),
        (".cache/huggingface/token", "hf_" + "a" * 30),
        (".cache/huggingface/stored_tokens", "hf_" + "a" * 30),
        (".config/huggingface/token", "hf_" + "a" * 30),
        (".kaggle/kaggle.json", '{"key": "' + "a" * 24 + '"}'),
        (".config/kaggle/kaggle.json", '{"key": "' + "a" * 24 + '"}'),
        (".wandb/settings", "api_key = " + "a" * 24),
        (".config/wandb/settings", "api_key = " + "a" * 24),
        (".gradle/gradle.properties", "repoPassword=" + "a" * 24),
        (".m2/settings.xml", "<password>" + "a" * 24 + "</password>"),
        ("NuGet.Config", "<add key=\"ClearTextPassword\" value=\"" + "a" * 24 + "\" />"),
        ("nuget.config", "<add key=\"ClearTextPassword\" value=\"" + "a" * 24 + "\" />"),
        (".nuget/NuGet/NuGet.Config", "<add key=\"ClearTextPassword\" value=\"" + "a" * 24 + "\" />"),
        (".pulumi/credentials.json", '{"accessTokens": {"api.pulumi.com": "' + "a" * 24 + '"}}'),
        (".aws/credentials", "aws_access_key_id=" + "A" * 20),
        (".gcloud/application_default_credentials.json", "{}"),
        (".config/gcloud/application_default_credentials.json", "{}"),
        (".config/gcloud/credentials.db", "sqlite"),
        (".config/gcloud/access_tokens.db", "sqlite"),
        (".config/gcloud/legacy_credentials/user@example.test/adc.json", "{}"),
        ("clouds.yaml", "clouds: {}"),
        ("secure.yaml", "clouds: {}"),
        (".config/openstack/clouds.yaml", "clouds: {}"),
        (".config/openstack/secure.yaml", "clouds: {}"),
        ("rclone.conf", "[remote]\ntype = s3"),
        (".config/rclone/rclone.conf", "[remote]\ntype = s3"),
        (".azure/accessTokens.json", "{}"),
        (".kube/config", "apiVersion: v1"),
        (".oci/config", "[DEFAULT]"),
        (".oraclebmc/config", "[DEFAULT]"),
        ("kubeconfig", "apiVersion: v1"),
        ("kube.config", "apiVersion: v1"),
        ("credentials.json", "{}"),
        ("application_default_credentials.json", "{}"),
        ("client_secret_local.json", "{}"),
        ("service-account-local.json", "{}"),
        ("firebase-adminsdk-local.json", "{}"),
        ("google-credentials-local.json", "{}"),
        ("secrets/local.key", "key"),
        ("secrets/local.pem", "pem"),
        ("secrets/LOCAL.PEM", "pem"),
        ("secrets/local.crt", "crt"),
        ("secrets/local.cer", "cer"),
        ("secrets/local.der", "der"),
        ("secrets/local.csr", "csr"),
        ("secrets/local.p7b", "p7b"),
        ("secrets/local.p7c", "p7c"),
        ("secrets/local.p12", "p12"),
        ("secrets/local.pfx", "pfx"),
        ("secrets/local.jks", "jks"),
        ("secrets/local.keystore", "keystore"),
        ("secrets/local.truststore", "truststore"),
        ("secrets/id_rsa", "ssh"),
        ("secrets/id_dsa", "ssh"),
        ("secrets/id_ecdsa", "ssh"),
        ("secrets/id_ecdsa_sk", "ssh"),
        ("secrets/ID_RSA", "ssh"),
        ("secrets/id_ed25519", "ssh"),
        ("secrets/id_ed25519_sk", "ssh"),
        ("data/local_ai.sqlite3", "sqlite"),
        ("data/local_ai.sqlite3-wal", "wal"),
        ("data/cache.sqlite3", "sqlite"),
        ("data/cache.sqlite3-shm", "shm"),
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
        ("terraform.tfstate", "{}"),
        ("terraform.tfstate.backup", "{}"),
        ("Pulumi.dev.yaml", "config: {}"),
        ("Pulumi.prod.json", "{}"),
        (".vault_pass", "password"),
        (".vault_password", "password"),
        ("prod.vault", "$ANSIBLE_VAULT"),
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


def test_public_release_check_json_cli_reports_failure_without_secret_value(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    secret_value = "a" * 24
    (tmp_path / "docs.md").write_text("LOCAL_API_KEY=" + secret_value, encoding="utf-8")

    with patch("sys.argv", ["public_release_check.py", "--root", str(tmp_path), "--json"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exc_info.value.code == 1
    assert captured.err == ""
    assert payload["ok"] is False
    assert payload["findings"][0]["path"] == "docs.md"
    assert secret_value not in captured.out


def test_public_release_check_human_cli_reports_failure_without_secret_value(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    secret_value = "a" * 24
    (tmp_path / "docs.md").write_text("LOCAL_API_KEY=" + secret_value, encoding="utf-8")

    with patch("sys.argv", ["public_release_check.py", "--root", str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert captured.err == ""
    assert "ok=False" in captured.out
    assert "[high] docs.md:" in captured.out
    assert secret_value not in captured.out


def test_public_release_check_json_cli_reports_success(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text("# ok", encoding="utf-8")

    with patch("sys.argv", ["public_release_check.py", "--root", str(tmp_path), "--json"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exc_info.value.code == 0
    assert captured.err == ""
    assert payload["ok"] is True
    assert payload["findings"] == []
    assert payload["scanned_files"] == 1


def test_public_release_check_human_cli_reports_success(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text("# ok", encoding="utf-8")

    with patch("sys.argv", ["public_release_check.py", "--root", str(tmp_path)]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.err == ""
    assert captured.out == "ok=True scanned_files=1\n"


def test_public_release_check_reports_sensitive_path_once(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    env_findings = [finding for finding in result["findings"] if finding["path"] == ".env"]
    assert result["ok"] is False
    assert len(env_findings) == 1
    assert "민감 경로" in env_findings[0]["message"]


def test_public_release_check_does_not_count_sensitive_paths_as_scanned_text(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["scanned_files"] == 0


@pytest.mark.parametrize(
    "content",
    [
        "OPENAI_API_KEY=" + "sk-" + "a" * 24,
        '"api_key": "' + "a" * 24 + '"',
        '"credential": "' + "a" * 24 + '"',
        "token: " + "a" * 24,
        "Authorization: Bearer " + "a" * 24,
        "telegram bot token " + "123456789:" + "a" * 35,
        "discord bot token " + "a" * 24 + "." + "b" * 6 + "." + "c" * 27,
        "anthropic key " + "sk-ant-" + "a" * 32,
        "github token " + "ghp_" + "a" * 36,
        "github oauth token " + "gho_" + "a" * 36,
        "github user token " + "ghu_" + "a" * 36,
        "github app token " + "ghs_" + "a" * 36,
        "github refresh token " + "ghr_" + "a" * 36,
        "github fine-grained token " + "github_pat_" + "a" * 36,
        "gitlab token " + "glpat-" + "a" * 20,
        "huggingface token " + "hf_" + "a" * 30,
        "npm token " + "npm_" + "a" * 36,
        "slack token " + "xoxb-" + "a" * 24,
        "google api key " + "AIza" + "A" * 35,
        "aws key " + "AKIA" + "A" * 16,
        "sendgrid key " + "SG." + "a" * 22 + "." + "b" * 43,
        "stripe secret key " + "sk_live_" + "a" * 24,
        "stripe restricted key " + "rk_test_" + "a" * 24,
        "-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END " + "PRIVATE KEY-----",
        "-----BEGIN ENCRYPTED " + "PRIVATE KEY-----\nabc\n-----END ENCRYPTED " + "PRIVATE KEY-----",
    ],
)
def test_public_release_check_flags_secret_text_patterns(tmp_path: Path, content: str) -> None:
    (tmp_path / "docs.md").write_text(content, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == "docs.md"
    assert "secret" in result["findings"][0]["message"]


def test_public_release_check_reports_secret_text_file_once(tmp_path: Path) -> None:
    (tmp_path / "docs.md").write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=sk-" + "a" * 24,
                "Authorization: Bearer " + "b" * 24,
                "github token ghp_" + "c" * 36,
            ]
        ),
        encoding="utf-8",
    )

    result = run_public_release_check(tmp_path)

    docs_findings = [finding for finding in result["findings"] if finding["path"] == "docs.md"]
    assert result["ok"] is False
    assert len(docs_findings) == 1
    assert "secret" in docs_findings[0]["message"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "setup.sh",
        "settings.ini",
        "app.conf",
        "app.config",
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


def test_public_release_check_flags_real_secret_inside_gitkeep(tmp_path: Path) -> None:
    uploads = tmp_path / "data" / "uploads"
    uploads.mkdir(parents=True)
    (uploads / ".gitkeep").write_text("token=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == "data/uploads/.gitkeep"
    assert "secret" in result["findings"][0]["message"]


def test_public_release_check_allows_env_example(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text("LOCAL_API_KEY=\n", encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["findings"] == []


def test_public_release_check_flags_real_secret_inside_env_example(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == ".env.example"
    assert "secret" in result["findings"][0]["message"]


def test_public_release_check_counts_allowed_path_exceptions_as_scanned_text(tmp_path: Path) -> None:
    uploads = tmp_path / "data" / "uploads"
    uploads.mkdir(parents=True)
    (uploads / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / ".env.example").write_text("LOCAL_API_KEY=\n", encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["scanned_files"] == 2


def test_public_release_check_flags_tracked_sensitive_file_even_when_ignored(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "-f", ".env"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = run_public_release_check(tmp_path)

    paths = {finding["path"] for finding in result["findings"]}
    assert result["ok"] is False
    assert ".env" in paths


def test_public_release_check_allows_ignored_untracked_sensitive_file(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is True
    assert result["findings"] == []


def test_public_release_check_fallback_flags_sensitive_files_outside_git(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("LOCAL_API_KEY=" + "a" * 24, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    paths = {finding["path"] for finding in result["findings"]}
    assert result["ok"] is False
    assert ".env" in paths


def test_public_release_private_data_has_no_duplicate_entries() -> None:
    assert len(PUBLIC_RELEASE_PRIVATE_DATA) == len(set(PUBLIC_RELEASE_PRIVATE_DATA))


def test_public_release_private_data_entries_are_scanner_enforced(tmp_path: Path) -> None:
    for index, item in enumerate(PUBLIC_RELEASE_PRIVATE_DATA):
        relative_path = _sample_private_data_path(item)
        root = tmp_path / f"case_{index}"
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("token=" + "a" * 24, encoding="utf-8")

        result = run_public_release_check(root)

        flagged_paths = {finding["path"] for finding in result["findings"]}
        assert result["ok"] is False
        assert relative_path in flagged_paths


def _sample_private_data_path(pattern: str) -> str:
    if pattern == ".env.*":
        return ".env.local"
    if pattern.endswith("/"):
        return f"{pattern}private.txt"
    if "*" in pattern:
        return pattern.replace("*", "local")
    return pattern


def test_public_release_private_data_is_documented_and_ignored() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    security = Path("SECURITY.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    public_summary = Path("docs/PUBLIC_RELEASE_SUMMARY.md").read_text(encoding="utf-8")

    gitignore_coverage = {
        ".env": [".env"],
        ".env.*": [".env.*", "!.env.example"],
        ".envrc": [".envrc"],
        ".npmrc": [".npmrc"],
        ".yarnrc": [".yarnrc"],
        ".yarnrc.yml": [".yarnrc.yml"],
        ".pnpmrc": [".pnpmrc"],
        ".pypirc": [".pypirc"],
        "pip.conf": ["pip.conf"],
        ".config/pip/pip.conf": [".config/pip/pip.conf"],
        ".config/pypoetry/auth.toml": [".config/pypoetry/auth.toml"],
        "pypoetry/auth.toml": ["pypoetry/auth.toml"],
        ".netrc": [".netrc"],
        ".git-credentials": [".git-credentials"],
        ".boto": [".boto"],
        ".s3cfg": [".s3cfg"],
        ".pgpass": [".pgpass"],
        ".sentryclirc": [".sentryclirc"],
        "auth.json": ["auth.json"],
        ".terraformrc": [".terraformrc"],
        "terraform.rc": ["terraform.rc"],
        "secrets/": ["secrets/"],
        ".secrets/": [".secrets/"],
        ".ssh/": [".ssh/"],
        ".gnupg/": [".gnupg/"],
        ".password-store/": [".password-store/"],
        ".vault-token": [".vault-token"],
        ".config/doppler/config.yaml": [".config/doppler/config.yaml"],
        ".config/infisical/infisical-config.json": [".config/infisical/infisical-config.json"],
        ".config/op/config": [".config/op/config"],
        ".config/1Password/credentials.json": [".config/1Password/credentials.json"],
        ".config/sops/age/keys.txt": [".config/sops/age/keys.txt"],
        ".docker/": [".docker/"],
        ".config/containers/auth.json": [".config/containers/auth.json"],
        ".config/helm/registry/config.json": [".config/helm/registry/config.json"],
        ".config/helm/repositories.yaml": [".config/helm/repositories.yaml"],
        ".config/hub": [".config/hub"],
        ".config/gh/hosts.yml": [".config/gh/hosts.yml"],
        ".config/gh/hosts.yaml": [".config/gh/hosts.yaml"],
        ".config/doctl/config.yaml": [".config/doctl/config.yaml"],
        ".config/doctl/config.yml": [".config/doctl/config.yml"],
        ".vercel/auth.json": [".vercel/auth.json"],
        ".netlify/config.json": [".netlify/config.json"],
        ".fly/config.yml": [".fly/config.yml"],
        ".fly/config.yaml": [".fly/config.yaml"],
        ".openai/": [".openai/"],
        ".config/openai/": [".config/openai/"],
        ".anthropic/": [".anthropic/"],
        ".claude.json": [".claude.json"],
        ".claude/settings.local.json": [".claude/settings.local.json"],
        ".gemini/settings.json": [".gemini/settings.json"],
        ".config/gemini/settings.json": [".config/gemini/settings.json"],
        ".postman/": [".postman/"],
        ".config/Postman/": [".config/Postman/"],
        ".insomnia/": [".insomnia/"],
        ".config/Insomnia/": [".config/Insomnia/"],
        ".httpie/": [".httpie/"],
        ".config/httpie/": [".config/httpie/"],
        ".bruno/": [".bruno/"],
        ".cursor/mcp.json": [".cursor/mcp.json"],
        ".cursor/settings.json": [".cursor/settings.json"],
        ".continue/config.json": [".continue/config.json"],
        ".aider.conf.yml": [".aider.conf.yml"],
        ".aider.env": [".aider.env"],
        ".codeium/config.json": [".codeium/config.json"],
        ".config/Codeium/config.json": [".config/Codeium/config.json"],
        ".gem/credentials": [".gem/credentials"],
        ".cargo/credentials": [".cargo/credentials"],
        ".cargo/credentials.toml": [".cargo/credentials.toml"],
        ".composer/auth.json": [".composer/auth.json"],
        ".config/composer/auth.json": [".config/composer/auth.json"],
        ".condarc": [".condarc"],
        ".config/conda/condarc": [".config/conda/condarc"],
        ".continuum/anaconda-client/tokens": [".continuum/anaconda-client/tokens"],
        ".dbt/profiles.yml": [".dbt/profiles.yml"],
        ".databrickscfg": [".databrickscfg"],
        ".config/databricks/credentials": [".config/databricks/credentials"],
        ".snowsql/config": [".snowsql/config"],
        ".config/snowflake/config.toml": [".config/snowflake/config.toml"],
        ".huggingface/token": [".huggingface/token"],
        ".cache/huggingface/token": [".cache/huggingface/token"],
        ".cache/huggingface/stored_tokens": [".cache/huggingface/stored_tokens"],
        ".config/huggingface/token": [".config/huggingface/token"],
        ".kaggle/kaggle.json": [".kaggle/kaggle.json"],
        ".config/kaggle/kaggle.json": [".config/kaggle/kaggle.json"],
        ".wandb/settings": [".wandb/settings"],
        ".config/wandb/settings": [".config/wandb/settings"],
        ".gradle/gradle.properties": [".gradle/gradle.properties"],
        ".m2/settings.xml": [".m2/settings.xml"],
        "NuGet.Config": ["NuGet.Config"],
        "nuget.config": ["nuget.config"],
        ".nuget/NuGet/NuGet.Config": [".nuget/NuGet/NuGet.Config"],
        ".pulumi/credentials.json": [".pulumi/credentials.json"],
        ".aws/": [".aws/"],
        ".gcloud/": [".gcloud/"],
        ".config/gcloud/application_default_credentials.json": [
            ".config/gcloud/application_default_credentials.json"
        ],
        ".config/gcloud/credentials.db": [".config/gcloud/credentials.db"],
        ".config/gcloud/access_tokens.db": [".config/gcloud/access_tokens.db"],
        ".config/gcloud/legacy_credentials/": [".config/gcloud/legacy_credentials/"],
        "clouds.yaml": ["clouds.yaml"],
        "secure.yaml": ["secure.yaml"],
        ".config/openstack/clouds.yaml": [".config/openstack/clouds.yaml"],
        ".config/openstack/secure.yaml": [".config/openstack/secure.yaml"],
        "rclone.conf": ["rclone.conf"],
        ".config/rclone/rclone.conf": [".config/rclone/rclone.conf"],
        ".azure/": [".azure/"],
        ".kube/": [".kube/"],
        ".oci/": [".oci/"],
        ".oraclebmc/": [".oraclebmc/"],
        "kubeconfig": ["kubeconfig"],
        "kube.config": ["kube.config"],
        "credentials.json": ["credentials.json"],
        "application_default_credentials.json": ["application_default_credentials.json"],
        "client_secret*.json": ["client_secret*.json"],
        "service-account*.json": ["service-account*.json"],
        "firebase-adminsdk*.json": ["firebase-adminsdk*.json"],
        "google-credentials*.json": ["google-credentials*.json"],
        "*.key": ["*.key"],
        "*.pem": ["*.pem"],
        "*.crt": ["*.crt"],
        "*.cer": ["*.cer"],
        "*.der": ["*.der"],
        "*.csr": ["*.csr"],
        "*.p7b": ["*.p7b"],
        "*.p7c": ["*.p7c"],
        "*.p12": ["*.p12"],
        "*.pfx": ["*.pfx"],
        "*.jks": ["*.jks"],
        "*.keystore": ["*.keystore"],
        "*.truststore": ["*.truststore"],
        "id_rsa": ["id_rsa"],
        "id_dsa": ["id_dsa"],
        "id_ecdsa": ["id_ecdsa"],
        "id_ecdsa_sk": ["id_ecdsa_sk"],
        "id_ed25519": ["id_ed25519"],
        "id_ed25519_sk": ["id_ed25519_sk"],
        "data/local_ai.sqlite3": ["data/*.sqlite3", "data/*.sqlite3-*"],
        "data/*.sqlite3": ["data/*.sqlite3"],
        "data/*.sqlite3-*": ["data/*.sqlite3-*"],
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
        "*.tfstate": ["*.tfstate"],
        "*.tfstate.*": ["*.tfstate.*"],
        "Pulumi.*.yaml": ["Pulumi.*.yaml"],
        "Pulumi.*.json": ["Pulumi.*.json"],
        ".vault_pass": [".vault_pass"],
        ".vault_password": [".vault_password"],
        "*.vault": ["*.vault"],
    }

    assert set(PUBLIC_RELEASE_PRIVATE_DATA) == set(gitignore_coverage)
    security_mirrored_private_data = PUBLIC_RELEASE_PRIVATE_DATA[
        : PUBLIC_RELEASE_PRIVATE_DATA.index("*.key")
    ]
    for item in security_mirrored_private_data:
        assert item in security
    for item in [
        "data/local_ai.sqlite3",
        "data/*.sqlite3",
        "data/*.sqlite3-*",
        "data/chroma/",
        "data/uploads/",
        "data/logs/",
        "data/*.jsonl",
    ]:
        assert item in security
    for item in PUBLIC_RELEASE_PRIVATE_DATA:
        assert item in release_checklist
        assert item in public_summary
        for ignored_pattern in gitignore_coverage[item]:
            assert ignored_pattern in gitignore
