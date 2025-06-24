import faiss
import pickle
import os
import numpy as np

VECTOR_DIM = 384  # MiniLM output dimension

def build_and_save_index(vectors, chunks, save_path: str):
    vectors_np = np.array(vectors).astype("float32")
    print(f"📐 Vector shape: {vectors_np.shape}")
    
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(vectors_np)

    # Save index
    faiss.write_index(index, f"{save_path}.index")
    print(f"💾 FAISS index saved: {save_path}.index")

    # Save chunk metadata
    with open(f"{save_path}.chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    print(f"📝 Chunk metadata saved: {save_path}.chunks.pkl")

def load_index_and_chunks(save_path: str):
    import faiss
    import pickle
    index = faiss.read_index(f"{save_path}.index")
    with open(f"{save_path}.chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def save_index(vectors, chunks, project_name):
    safe_name = project_name.replace(" ", "_").replace("/", "_")
    os.makedirs("data/vector_stores", exist_ok=True)
    save_path = os.path.join("data/vector_stores", safe_name)
    print(f"📦 Project safe name: {safe_name}")
    build_and_save_index(vectors, chunks, save_path)
    print(f"🧠 Saving FAISS index to: {save_path}.index")

