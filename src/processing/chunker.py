from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_into_chunks(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


def chunk_full_text_for_llm(text: str, max_words=1500, overlap=200):
    """
    Break full document into sequential chunks for LLM input.
    Each chunk overlaps to maintain continuity.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + max_words)
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "id": len(chunks),
            "text": chunk_text
        })
        start = end - overlap
    return chunks
