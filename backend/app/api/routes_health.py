from fastapi import APIRouter
from app.core.config import get_settings
from app.retrieval.vector_store import collection_count

router = APIRouter()


@router.get("/")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "indexed_chunks": collection_count(),
    }
