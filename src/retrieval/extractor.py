def build_task_prompt(chunks: list[str]) -> str:
    context = "\n\n".join(chunks[:5])  # Limit to first 5 chunks to stay within LLM context window
    return f"""
You are an assistant extracting action items from tender documents.

Based on the following tender content, extract actionable tasks (like submission steps, forms to attach, deadlines, etc.).

✅ Please return a JSON array like this:
[
  {{
    "task": "Submit application with required forms",
    "deadline": "July 10, 2025 or TBD",
    "status": "Pending"
  }},
  ...
]

Only return the JSON — no other text.

Tender Content:
{context}
""".strip()
