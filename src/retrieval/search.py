from typing import List
from src.prompt.prompt import get_full_document_chunks
from src.embedding.index import load_index_and_chunks  # Reuse to get stored chunks

MAX_TOKEN_LIMIT = 1800  # Adjust based on your model's context window

def count_tokens(text: str) -> int:
    """
    Approximates token count based on LLaMA models.
    """
    return int(len(text) / 3.5)


def get_relevant_chunks(question: str = "", k: int = 8, min_score: float = 0.5) -> List[str]:
    """
    Returns full document or chunks depending on token length.
    Ignores vector similarity search; only uses full content from vector DB.
    """
    _, stored_chunks = load_index_and_chunks()

    # Reconstruct full doc from stored chunks
    full_doc = "\n".join([chunk.page_content.strip() for chunk in stored_chunks])

    if count_tokens(full_doc) > MAX_TOKEN_LIMIT:
        return get_full_document_chunks(full_doc)
    else:
        return [full_doc]
