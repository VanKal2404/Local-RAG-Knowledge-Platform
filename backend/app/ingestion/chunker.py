from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int


def chunk_text(
    text: str,
    chunk_size: int = 900,
    overlap: int = 180
) -> list[TextChunk]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    cleaned = " ".join(text.split())

    chunks: list[TextChunk] = []

    start = 0
    index = 0

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))

        chunk = cleaned[start:end].strip()

        if chunk:
            chunks.append(
                TextChunk(
                    text=chunk,
                    chunk_index=index
                )
            )

            index += 1

        if end == len(cleaned):
            break

        start += chunk_size - overlap

    return chunks