# test_process_file.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from processing.parser import parse_pdf, parse_docx
from processing.chunker import chunk_text
from processing.metadata import extract_metadata
from embedding.model import load_embedder
from embedding.index import build_and_save_index

import os
import uuid

def process_and_index(file_path):
    print("📄 File:", file_path)

    # 1. Parse
    if file_path.endswith(".pdf"):
        text = parse_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = parse_docx(file_path)
    else:
        raise Exception("Unsupported format")

    print("✅ Parsed text length:", len(text))

    # 2. Chunk
    chunks = chunk_text(text)
    print("🧩 Chunks:", len(chunks))

    # 3. Embed
    embedder = load_embedder()
    vectors = embedder.encode(chunks)
    print("📐 Embeddings shape:", vectors.shape)

    # 4. Save to FAISS
    file_id = f"{uuid.uuid4().hex}_{os.path.basename(file_path)}"
    vector_path = os.path.join("data/vector_stores", file_id)
    os.makedirs("data/vector_stores", exist_ok=True)

    build_and_save_index(vectors, chunks, vector_path)
    print(f"✅ Vector index saved to: {vector_path}.index")

    return vector_path

# 👇 Change this to test your file
if __name__ == "__main__":
    test_file = "../data/uploads/sample.pdf"

    process_and_index(test_file)
