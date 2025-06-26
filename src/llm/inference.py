def get_model_response(prompt: str, model: str) -> tuple[str, float]:
    model = model.lower()

    if model == "groq":
        from src.llm.groq_inference import get_groq_response
        return get_groq_response(prompt)

    elif model == "llama":
        from src.llm.llama_inference import get_llm_response
        return get_llm_response(prompt)

    else:
        raise ValueError(f"❌ Unsupported model: {model}")
