from pathlib import Path

from scripts.public_release_check import run_public_release_check


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
