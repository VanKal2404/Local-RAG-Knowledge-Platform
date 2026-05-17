import logging
from pathlib import Path
import fitz

logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def extract_pdf_text(file_path: str) -> list[dict]:
    pages: list[dict] = []
    path = Path(file_path)
    logger.info("Extracting PDF text from %s", path.name)

    with fitz.open(file_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text and text.strip():
                pages.append({"page": page_number, "text": text.strip()})

    return pages


def extract_plain_text(file_path: str) -> list[dict]:
    path = Path(file_path)
    logger.info("Extracting plain text from %s", path.name)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [{"page": 1, "text": text.strip()}] if text.strip() else []


def extract_text(file_path: str) -> list[dict]:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)
    if extension in {".txt", ".md"}:
        return extract_plain_text(file_path)

    raise ValueError(f"Unsupported file type: {extension}. Supported: {sorted(SUPPORTED_EXTENSIONS)}")
