from fastapi import APIRouter, HTTPException
from app.llm.ollama_client import OllamaUnavailableError, query_ollama
from app.llm.prompt_builder import build_rag_prompt
from app.retrieval.retriever import retrieve_context
from app.schemas.chat import ChatRequest, ChatResponse, SourceReference

router = APIRouter()


def build_sources(contexts: list[dict]) -> list[SourceReference]:
    return [
        SourceReference(
            document=item["document"],
            page=item["page"],
            chunk=item["chunk"],
            score=item.get("score"),
        )
        for item in contexts
    ]


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Full RAG mode:
    Retrieval + Ollama answer generation.
    Better written answers, but slower on low-RAM machines.
    """
    contexts = retrieve_context(request.question, request.top_k)

    if not contexts:
        return ChatResponse(
            answer="No indexed documents were found. Upload a document first.",
            sources=[],
        )

    prompt = build_rag_prompt(request.question, contexts)

    try:
        answer = query_ollama(prompt)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        answer=answer,
        sources=build_sources(contexts),
    )