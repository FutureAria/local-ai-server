from pathlib import Path
from types import SimpleNamespace
import builtins

import pytest

from app.services.document_loader import DocumentLoader, DocumentLoaderError
from app.utils.file_utils import iter_supported_files


def test_document_loader_txt(tmp_path: Path) -> None:
    path = tmp_path / "note.txt"
    path.write_text("hello txt", encoding="utf-8")
    assert DocumentLoader().load_text(path) == "hello txt"


def test_document_loader_md(tmp_path: Path) -> None:
    path = tmp_path / "note.md"
    path.write_text("# hello md", encoding="utf-8")
    assert DocumentLoader().load_text(path) == "# hello md"


def test_document_loader_html_extracts_visible_text(tmp_path: Path) -> None:
    path = tmp_path / "note.html"
    path.write_text(
        """
        <html>
          <head>
            <title>ignored title</title>
            <style>.hidden { display: none; }</style>
            <script>console.log("ignore me")</script>
          </head>
          <body>
            <h1>JWT Notes</h1>
            <p>Access tokens go in the Authorization header.</p>
            <ul><li>Refresh token stays server-side.</li></ul>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    assert DocumentLoader().load_text(path) == (
        "JWT Notes\nAccess tokens go in the Authorization header.\nRefresh token stays server-side."
    )


def test_document_loader_htm_extracts_visible_text(tmp_path: Path) -> None:
    path = tmp_path / "note.htm"
    path.write_text("<main><h1>Local AI</h1><p>HTML files are supported.</p></main>", encoding="utf-8")

    assert DocumentLoader().load_text(path) == "Local AI\nHTML files are supported."


def test_document_loader_pdf_with_optional_dependency(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "note.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [
                SimpleNamespace(extract_text=lambda: "first page"),
                SimpleNamespace(extract_text=lambda: "second page"),
            ]

    monkeypatch.setitem(__import__("sys").modules, "pypdf", SimpleNamespace(PdfReader=FakePdfReader))

    assert DocumentLoader().load_text(path) == "first page\n\nsecond page"


def test_document_loader_docx_with_optional_dependency(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "note.docx"
    path.write_bytes(b"fake docx")

    class FakeDocument:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.paragraphs = [SimpleNamespace(text="paragraph one"), SimpleNamespace(text="")]
            self.tables = [
                SimpleNamespace(
                    rows=[
                        SimpleNamespace(
                            cells=[SimpleNamespace(text="cell a"), SimpleNamespace(text="cell b")]
                        )
                    ]
                )
            ]

    monkeypatch.setitem(__import__("sys").modules, "docx", SimpleNamespace(Document=FakeDocument))

    assert DocumentLoader().load_text(path) == "paragraph one\ncell a | cell b"


def test_document_loader_pdf_missing_dependency_returns_clear_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "note.pdf"
    path.write_bytes(b"%PDF fake")

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pypdf":
            raise ImportError("missing pypdf")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(DocumentLoaderError, match=r"pip install -e '.\[documents\]'"):
        DocumentLoader().load_text(path)


def test_document_loader_docx_missing_dependency_returns_clear_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "note.docx"
    path.write_bytes(b"fake docx")

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "docx":
            raise ImportError("missing docx")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(DocumentLoaderError, match=r"pip install -e '.\[documents\]'"):
        DocumentLoader().load_text(path)


def test_supported_types_report_optional_dependency_availability() -> None:
    types = {item["extension"]: item for item in DocumentLoader().supported_types()}

    assert types[".txt"]["available"] is True
    assert types[".md"]["available"] is True
    assert types[".html"]["available"] is True
    assert types[".htm"]["file_type"] == "html"
    assert types[".pdf"]["optional_dependency"] == "pypdf"
    assert types[".docx"]["optional_dependency"] == "python-docx"


def test_iter_supported_files_includes_pdf_docx_and_html(tmp_path: Path) -> None:
    for name in ["note.txt", "note.md", "note.pdf", "note.docx", "note.html", "note.htm", "ignored.png"]:
        (tmp_path / name).write_text("content", encoding="utf-8")

    discovered = {path.name for path in iter_supported_files(tmp_path)}

    assert discovered == {"note.txt", "note.md", "note.pdf", "note.docx", "note.html", "note.htm"}
