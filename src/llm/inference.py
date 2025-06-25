from llama_cpp import Llama
import time

# Load the model once (globally)
llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6,  # Use 6 threads for a good balance of speed and system usability
    verbose=False
)


def get_llm_response(prompt: str) -> tuple[str, float]:
    chat_format_prompt = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that answers questions "
                "strictly using the given context. Keep responses accurate, clear, "
                "and under 3 sentences. Do not add extra information."
            )
        },
        {"role": "user", "content": prompt}
    ]

    try:
        start_time = time.time()

        # Streaming to measure accurate time but return full response
        response_text = ""
        for chunk in llm.create_chat_completion(
            messages=chat_format_prompt,
            max_tokens=512,
            temperature=0.5,
            top_p=0.9,
            stop=["</s>"],
            stream=True
        ):
            if 'choices' in chunk and chunk['choices'][0]['delta'].get('content'):
                response_text += chunk['choices'][0]['delta']['content']

        end_time = time.time()
        generation_time = end_time - start_time

        return response_text.strip(), generation_time

    except Exception as e:
        return f"[LLM Error] {str(e)}", 0.0
