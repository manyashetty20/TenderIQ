def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks).strip()

    # Detect if it's a task-related question
    is_task_query = any(keyword in question.lower() for keyword in [
        "task", "tasks", "actionable", "deliverables", "deadlines", "milestone", "responsibilities"
    ])

    if is_task_query:
        # 🎯 Task Extraction Prompt
        prompt = f"""
You are an AI assistant that extracts actionable tasks, deliverables, and deadlines from tender documents.

Only use the CONTEXT below to generate the task list. Do NOT add summaries, explanations, or make assumptions.

---

📚 CONTEXT:
{context}

---

🎯 INSTRUCTIONS:
List specific, standalone tasks mentioned in the context.

- Include deadlines if available.
- Keep tasks practical and clearly worded.
- Exclude vague, redundant, or generic information.

✅ Example Format:
1. Submit the tender application by June 30.
2. Upload signed agreements to the portal by July 10.
3. Finalize technical specifications before project kickoff.

---

📝 Now extract tasks for this prompt:
"{question}"
""".strip()
    else:
        # 💬 Q&A Prompt
        prompt = f"""
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
""".strip()

    return prompt
