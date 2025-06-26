import time
from llama_cpp import Llama

# Load LLaMA model globally once
llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6,
    verbose=False
)

def get_llm_response(prompt: str) -> tuple[str, float]:
    chat_format_prompt = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that responds using ONLY the provided context.\n"
                "Return your answers in correct format as requested by the prompt.\n"
                "Avoid adding any extra information."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        start = time.perf_counter()
        response_text = ""

        for chunk in llm.create_chat_completion(
            messages=chat_format_prompt,
            max_tokens=512,
            temperature=0.3,
            top_p=0.95,
            stream=True,
            stop=["</s>"]
        ):
            if 'choices' in chunk:
                delta = chunk['choices'][0].get('delta', {})
                content = delta.get('content')
                if content:
                    response_text += content

        duration = round(time.perf_counter() - start, 3)
        return response_text.strip(), duration

    except Exception as e:
        return f"⚠️ LLaMA Error: {str(e)}", 0.0
