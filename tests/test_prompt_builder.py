from backend.app.llm.prompt_builder import build_rag_prompt


def test_prompt_contains_question_and_sources():
    prompt = build_rag_prompt(
        "What is this about?",
        [{"document": "demo.pdf", "page": 1, "chunk": 0, "text": "Demo text"}],
    )
    assert "What is this about?" in prompt
    assert "[SOURCE 1]" in prompt
    assert "demo.pdf" in prompt
