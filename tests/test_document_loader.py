from pathlib import Path
from types import SimpleNamespace
import builtins
import sys

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


def test_document_loader_pdf_text_page_does_not_call_ocr(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "note.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [SimpleNamespace(extract_text=lambda: "this page already has enough text")]

    def fail_ocr(*args, **kwargs):
        raise AssertionError("OCR should not run when PDF text extraction succeeds")

    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=FakePdfReader))
    monkeypatch.setattr(DocumentLoader, "_ocr_pdf_page_images", fail_ocr)

    assert DocumentLoader().load_text(path) == "this page already has enough text"


def test_document_loader_pdf_ocr_dependency_import_failure_is_clear(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "scan.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [SimpleNamespace(extract_text=lambda: "", images=[b"fake image"])]

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pypdf":
            return SimpleNamespace(PdfReader=FakePdfReader)
        if name == "pytesseract":
            raise ImportError("missing pytesseract")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(DocumentLoader, "pdf_ocr_status", lambda self: {"available": True, "install_hint": None})

    with pytest.raises(DocumentLoaderError, match=r"PDF OCR.*pip install -e '.\[ocr\]'"):
        DocumentLoader().load_text(path)


def test_document_loader_pdf_ocr_tesseract_binary_missing_is_clear(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "scan.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [SimpleNamespace(extract_text=lambda: "", images=[b"fake image"])]

    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=FakePdfReader))
    monkeypatch.setattr(
        DocumentLoader,
        "pdf_ocr_status",
        lambda self: {"available": False, "install_hint": "install local tesseract"},
    )

    with pytest.raises(DocumentLoaderError, match=r"OCR fallback skipped: page 1: install local tesseract"):
        DocumentLoader().load_text(path)


def test_document_loader_pdf_ocr_success_with_mock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "scan.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [SimpleNamespace(extract_text=lambda: "", images=[SimpleNamespace(data=b"fake image")])]

    class FakeImage:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    class FakeImageModule:
        @staticmethod
        def open(_bytes):
            return FakeImage()

    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pypdf":
            return SimpleNamespace(PdfReader=FakePdfReader)
        if name == "pytesseract":
            return SimpleNamespace(image_to_string=lambda image: "OCR extracted text")
        if name == "PIL":
            return SimpleNamespace(Image=FakeImageModule)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(DocumentLoader, "pdf_ocr_status", lambda self: {"available": True, "install_hint": None})

    assert DocumentLoader().load_text(path) == "OCR extracted text"


def test_document_loader_pdf_ocr_skips_when_pypdf_images_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "scan.pdf"
    path.write_bytes(b"%PDF fake")

    class FakePdfReader:
        def __init__(self, file_path: str):
            self.file_path = file_path
            self.pages = [SimpleNamespace(extract_text=lambda: "")]

    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=FakePdfReader))
    monkeypatch.setattr(DocumentLoader, "pdf_ocr_status", lambda self: {"available": True, "install_hint": None})

    with pytest.raises(DocumentLoaderError, match=r"PyPDF로 추출 가능한 image XObject가 없습니다"):
        DocumentLoader().load_text(path)


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
