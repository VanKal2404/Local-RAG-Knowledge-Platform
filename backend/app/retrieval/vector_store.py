import logging
import chromadb
from chromadb.errors import DuplicateIDError
from app.core.config import get_settings
from app.retrieval.embeddings import embed_texts

logger = logging.getLogger(__name__)


def get_collection():
    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    return client.get_or_create_collection(name=settings.collection_name)


def add_chunks(chunks: list[dict]) -> None:
    if not chunks:
        logger.warning("No chunks supplied to vector store")
        return

    collection = get_collection()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts)

    ids = [chunk["id"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Chroma does not upsert in all versions, so delete any existing ids first.
    try:
        collection.delete(ids=ids)
    except Exception:
        pass

    try:
        collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    except DuplicateIDError:
        logger.exception("Duplicate ids detected during Chroma add")
        raise

    logger.info("Indexed %s chunks", len(chunks))


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    collection = get_collection()
    query_embedding = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        score = 1 - float(distance) if distance is not None else None
        formatted.append({
            "text": text,
            "document": metadata.get("document"),
            "page": int(metadata.get("page", 0)),
            "chunk": int(metadata.get("chunk", 0)),
            "score": score,
        })

    return formatted


def collection_count() -> int:
    return get_collection().count()
