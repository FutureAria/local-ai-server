from pathlib import Path

import pytest

from scripts.public_release_check import PUBLIC_RELEASE_PRIVATE_DATA, run_public_release_check


@pytest.mark.parametrize(
    ("relative_path", "content"),
    [
        (".env", "LOCAL_API_KEY=" + "a" * 24),
        ("data/local_ai.sqlite3", "sqlite"),
        ("data/local_ai.sqlite3-wal", "wal"),
        ("data/chroma/index.bin", "vector"),
        ("data/uploads/private.md", "notes"),
        ("data/logs/app.log", "log"),
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
        "-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END " + "PRIVATE KEY-----",
    ],
)
def test_public_release_check_flags_secret_text_patterns(tmp_path: Path, content: str) -> None:
    (tmp_path / "docs.md").write_text(content, encoding="utf-8")

    result = run_public_release_check(tmp_path)

    assert result["ok"] is False
    assert result["findings"][0]["path"] == "docs.md"
    assert "secret" in result["findings"][0]["message"]


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
        "data/local_ai.sqlite3": ["data/*.sqlite3", "data/*.sqlite3-*"],
        "data/chroma/": ["data/chroma/*", "!data/chroma/.gitkeep"],
        "data/uploads/": ["data/uploads/*", "!data/uploads/.gitkeep"],
        "data/logs/": ["data/logs/*", "!data/logs/.gitkeep"],
        "data/*.jsonl": ["data/*.jsonl"],
    }

    assert set(PUBLIC_RELEASE_PRIVATE_DATA) == set(gitignore_coverage)
    for item in PUBLIC_RELEASE_PRIVATE_DATA:
        assert item in release_checklist
        assert item in public_summary
        for ignored_pattern in gitignore_coverage[item]:
            assert ignored_pattern in gitignore
