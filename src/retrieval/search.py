from typing import List, Tuple
from src.embedding.model import get_embedder  # your embedder
from src.embedding.index import load_index_and_chunks  # your vector DB

def get_relevant_chunks(question: str, k: int = 8, min_score: float = 0.5) -> List[str]:
    """
    1. Embed question
    2. Do similarity search
    3. Filter by score threshold
    4. Return top relevant chunk texts
    """
    embedder = get_embedder()
    index, chunks = load_index_and_chunks()

    # 1️⃣ Embed question
    question_embedding = embedder.embed_query(question)

    # 2️⃣ Similarity search with score
    hits: List[Tuple] = index.similarity_search_with_score_by_vector(
        question_embedding, k=k
    )

    # 3️⃣ Filter chunks by similarity
    relevant_chunks = []
    for doc, score in hits:
        if score >= min_score:
            relevant_chunks.append(doc.page_content.strip())

    return relevant_chunks
