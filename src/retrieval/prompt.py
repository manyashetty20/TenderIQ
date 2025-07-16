def count_tokens(text: str) -> int:
    """
    Approximates token count for LLaMA .gguf models.
    LLaMA typically uses ~3.5 characters per token.
    """
    return int(len(text) / 3.5)


def build_prompt(question: str, context_chunks: list[str]) -> str:
    reserved_output_tokens = 512
    max_ctx = 2048  # Context window for LLaMA 2 7B (adjust if using different model)

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

def build_stat_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)

    return f"""You are an intelligent assistant designed to analyze numeric/statistical information from tender documents.

---

📚 CONTEXT:
{context}

---

❓ QUESTION:
{question}

📌 INSTRUCTIONS:
- Extract all numbers and their relevant labels (e.g., Tender Name, Item Type).
- Identify tender-wise values clearly (e.g., Bid Validity for Tender A = 150 days).
- Aggregate across tenders (sum, average, max, min, etc.) where applicable.
- Provide **step-by-step reasoning** followed by the **final numeric answer**.
- If information is missing for one or more tenders, mention it clearly.
- If the answer can't be computed due to missing values, say: "The information is not available in the document."
"""
