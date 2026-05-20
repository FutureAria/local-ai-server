from pathlib import Path
from uuid import uuid4


IGNORED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "target"}
SUPPORTED_DOCUMENT_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}


def safe_upload_name(filename: str) -> str:
    original = Path(filename).name
    return f"{uuid4().hex}_{original}"


def iter_supported_files(folder: Path, recursive: bool = True):
    pattern = "**/*" if recursive else "*"
    for path in folder.glob(pattern):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS or part.startswith(".") for part in path.parts):
            continue
        if path.suffix.lower() in SUPPORTED_DOCUMENT_EXTENSIONS:
            yield path
