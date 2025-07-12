import tiktoken

def count_tokens(text: str) -> int:
    # Use approximate: 1 token ~= 4 chars in English
    return len(text) // 4

def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = ""
    reserved_output_tokens = 512
    max_ctx = 2048

    static_template = """
You are an AI assistant answering questions strictly using the provided CONTEXT.

---

📚 CONTEXT:
{context}

---

❓ QUESTION:
{question}

📌 INSTRUCTIONS:
- Use only the given context to answer.
- Be accurate, short, and avoid adding your own knowledge.
- If the answer isn't present, reply: "The information is not available in the document."
"""

    static_overhead = count_tokens(static_template) + count_tokens(question)

    used_tokens = static_overhead
    selected_chunks = []

    for chunk in context_chunks:
        chunk_tokens = count_tokens(chunk)
        if used_tokens + chunk_tokens + reserved_output_tokens < max_ctx:
            selected_chunks.append(chunk)
            used_tokens += chunk_tokens
        else:
            break

    context = "\n\n".join(selected_chunks).strip()

    prompt = static_template.format(context=context, question=question)

    return prompt
