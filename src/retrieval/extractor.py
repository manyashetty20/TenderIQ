def build_task_prompt(chunks: list[str]) -> str:
    context = "\n\n".join(chunks[:5])  # Use only top 5 chunks
    prompt = (
        "You are an assistant that extracts actionable items.\n"
        "From the below context, extract all actionable tasks, deadlines, or requirements in a structured JSON list:\n\n"
        f"{context}\n\n"
        "Respond in this JSON format:\n"
        '[{"task": "...", "deadline": "...", "status": "Pending"}, ...]'
    )
    return prompt
