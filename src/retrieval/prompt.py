from typing import Tuple, List

def count_tokens(text: str) -> int:
    """
    Approximates token count for LLaMA .gguf models.
    LLaMA typically uses ~3.5 characters per token.
    """
    return int(len(text) / 3.5)

def build_prompt(question: str, context_chunks: List[str]) -> str:
    """
    Builds a prompt with the question and selected context chunks.
    """
    prompt = "You are TenderIQ, a helpful assistant for tender-related queries. Use the following tender document excerpts to answer the user's question.\n\n"
    for i, chunk in enumerate(context_chunks):
        prompt += f"[Context {i+1}]:\n{chunk.strip()}\n\n"
    prompt += f"Question: {question.strip()}\nAnswer:"
    return prompt

def build_stat_prompt(question: str, chunks: List[str]) -> str:
    """
    Builds a prompt specifically for statistical reasoning or analysis over tender documents.
    """
    prompt = "You are a statistical assistant analyzing tender documents. Use the data below to answer the question as accurately as possible.\n\n"
    for i, chunk in enumerate(chunks):
        prompt += f"[Data {i+1}]:\n{chunk.strip()}\n\n"
    prompt += f"Question: {question.strip()}\nAnswer:"
    return prompt

def get_full_document_chunks(text: str, max_words: int = 1500, overlap: int = 200) -> List[str]:
    """
    Splits the full text of a document into overlapping word chunks to preserve context.
    
    Args:
        text (str): Full document text.
        max_words (int): Maximum words per chunk.
        overlap (int): Number of overlapping words between chunks.
    
    Returns:
        List[str]: List of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(len(words), start + max_words)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # maintain overlap

    return chunks

def build_prompt_from_full_doc(question: str, full_text: str) -> Tuple[str, List[str]]:
    """
    Decides whether to send the whole document or chunked parts, based on token count.
    
    Args:
        question (str): The user question.
        full_text (str): The entire text of the PDF document.
    
    Returns:
        Tuple[str, List[str]]: The final prompt and the list of chunks used (for logging).
    """
    estimated_tokens = count_tokens(full_text)

    if estimated_tokens < 2500:
        chunks = [full_text]  # send as one block
    else:
        chunks = get_full_document_chunks(full_text)

    prompt = build_prompt(question, chunks)
    return prompt, chunks
