"""from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=8  # Adjust based on your CPU
)

def get_llm_response(prompt: str) -> str:
    chat_format_prompt = [
        {"role": "system", "content": "You are a helpful assistant that answers based on the context."},
        {"role": "user", "content": prompt}
    ]
    
    output = llm.create_chat_completion(
        messages=chat_format_prompt,
        max_tokens=300,
        temperature=0.7
    )
    
    return output["choices"][0]["message"]["content"].strip()
"""
from llama_cpp import Llama

# Load the model once (globally)
llm = Llama(
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6,  # Use 6 threads for a good balance of speed and system usability
    verbose=False
)


def get_llm_response(prompt: str) -> str:
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
        output = llm.create_chat_completion(
            messages=chat_format_prompt,
            max_tokens=150,        # Reduced from 300 for speed
            temperature=0.5,       # Lowered for more deterministic factual answers
            top_p=0.9,
            stop=["</s>"]
        )

        return output["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"[LLM Error] {str(e)}"