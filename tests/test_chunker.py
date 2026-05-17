from backend.app.ingestion.chunker import chunk_text


def test_chunk_text_creates_chunks():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert all(chunk.text for chunk in chunks)


def test_chunk_text_rejects_bad_overlap():
    try:
        chunk_text("hello", chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
