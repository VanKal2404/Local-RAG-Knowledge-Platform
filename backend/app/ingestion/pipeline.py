import hashlib
import logging
from pathlib import Path
from app.core.config import get_settings
from app.ingestion.chunker import chunk_text
from app.ingestion.loaders import extract_text

logger = logging.getLogger(__name__)


def stable_document_id(document_name: str) -> str:
    return hashlib.sha256(document_name.encode("utf-8")).hexdigest()[:12]


def process_document(file_path: str, document_name: str) -> list[dict]:
    settings = get_settings()
    pages = extract_text(file_path)
    document_id = stable_document_id(document_name)
    processed_chunks: list[dict] = []

    logger.info("Processing document=%s pages=%s", document_name, len(pages))

    for page in pages:
        chunks = chunk_text(page["text"], settings.chunk_size, settings.chunk_overlap)
        for chunk in chunks:
            chunk_id = f"{document_id}_p{page['page']}_c{chunk.chunk_index}"
            processed_chunks.append({
                "id": chunk_id,
                "text": chunk.text,
                "metadata": {
                    "document_id": document_id,
                    "document": Path(document_name).name,
                    "page": page["page"],
                    "chunk": chunk.chunk_index,
                },
            })

    logger.info("Created %s chunks for document=%s", len(processed_chunks), document_name)
    return processed_chunks
