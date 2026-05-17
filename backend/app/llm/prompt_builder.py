def build_rag_prompt(question: str, contexts: list[dict]) -> str:
    context_text = ""

    for item in contexts:
        context_text += (
            f"\nPAGE {item['page']}\n"
            f"{item['text']}\n"
        )

    return f"""
You are a strict document-grounded assistant.

Rules:
1. Answer ONLY using the provided document text
2. NEVER use outside knowledge
3. NEVER invent information
4. If the answer is not directly supported by the sources, respond ONLY with:
"I could not find this in the uploaded documents."
5. Keep answers concise and professional
6. Maximum answer length: 120 words
7. ALWAYS include inline citations using this exact format:
[p.X]

Example:
The system supports offline operation through encrypted local storage [p.10].

Question:
{question}

Document text:
{context_text}

Answer:
"""