from pydantic import BaseModel, Field
from typing import List


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["What are the main risks described in this document?"])
    top_k: int = Field(default=5, ge=1, le=20)


class SourceReference(BaseModel):
    document: str
    page: int
    chunk: int
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
