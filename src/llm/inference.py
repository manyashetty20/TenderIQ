from llama_cpp import Llama

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
