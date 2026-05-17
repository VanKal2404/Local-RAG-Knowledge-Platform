import logging
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.ingestion.loaders import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import process_document
from app.retrieval.vector_store import add_chunks
from app.schemas.documents import UploadResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    settings = get_settings()
    filename = Path(file.filename or "uploaded_file").name
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = Path(settings.upload_dir) / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = file_path.stat().st_size / (1024 * 1024)

    if file_size_mb > settings.max_upload_mb:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_mb} MB limit",
        )

    try:
        chunks = process_document(str(file_path), filename)
        add_chunks(chunks)
    except Exception as exc:
        logger.exception("Failed to ingest document")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return UploadResponse(
        message="Document uploaded and indexed successfully",
        filename=filename,
        chunks_created=len(chunks),
    )


@router.delete("/clear")
def clear_documents():
    """
    Clears uploaded documents and the local vector index.

    Use this when starting a new workspace so old documents do not affect
    future retrieval results.
    """
    settings = get_settings()

    try:
        if os.path.exists(settings.upload_dir):
            shutil.rmtree(settings.upload_dir)

        if os.path.exists(settings.chroma_dir):
            shutil.rmtree(settings.chroma_dir)

        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.chroma_dir, exist_ok=True)

    except Exception as exc:
        logger.exception("Failed to clear documents")
        raise HTTPException(
            status_code=500,
            detail="Could not clear documents and index.",
        ) from exc

    return {
        "message": "Documents and vector index cleared successfully.",
    }