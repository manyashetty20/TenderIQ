import os
import pickle
import faiss
import numpy as np

CHUNK_STORE_DIR = "data/vector_stores"

def save_index(vectors: np.ndarray, new_chunks: list[str], project_name: str, doc_type: str = "", overwrite=False):
    """
    Save a FAISS index and associated chunks.
    - For 'general', always overwrite.
    - For others:
        - If overwrite=True: replace index and chunks with provided data.
        - If overwrite=False: append to existing chunks and vectors, with deduplication.
    """
    os.makedirs(CHUNK_STORE_DIR, exist_ok=True)

    # Build the file key
    if project_name == "general":
        key = "general"
    else:
        key = f"{project_name}_{doc_type.lower()}" if doc_type else project_name

    index_path = os.path.join(CHUNK_STORE_DIR, f"{key}.index")
    chunk_path = os.path.join(CHUNK_STORE_DIR, f"{key}.chunks.pkl")

    # If not overwriting, merge with existing
    existing_chunks = []
    existing_vectors = []

    if project_name != "general" and not overwrite and os.path.exists(chunk_path) and os.path.exists(index_path):
        print(f"📂 Loading existing index/chunks for {key}...")
        with open(chunk_path, "rb") as f:
            existing_chunks = pickle.load(f)

        old_index = faiss.read_index(index_path)
        dim = old_index.d
        for i in range(old_index.ntotal):
            vec = old_index.reconstruct(i)
            existing_vectors.append(vec)
    else:
        dim = vectors.shape[1]

    if overwrite:
        print(f"✏️ Overwriting existing index/chunks for {key}")
        dedup_chunks = list(dict.fromkeys([chunk.strip() for chunk in new_chunks]))
        dedup_vectors = vectors[:len(dedup_chunks)]
    else:
        # Combine and deduplicate
        all_chunks = existing_chunks + new_chunks
        all_vectors = existing_vectors + vectors.tolist()
        seen = set()
        dedup_chunks = []
        dedup_vectors = []
        for chunk, vec in zip(all_chunks, all_vectors):
            norm_chunk = chunk.strip()
            if norm_chunk not in seen:
                seen.add(norm_chunk)
                dedup_chunks.append(norm_chunk)
                dedup_vectors.append(vec)
        dedup_vectors = np.array(dedup_vectors, dtype=np.float32)

    # Final FAISS index
    if overwrite:
        dedup_vectors_np = vectors[:len(dedup_chunks)]
    else:
        dedup_vectors_np = np.array(dedup_vectors, dtype=np.float32)

    index = faiss.IndexFlatL2(dim)
    index.add(dedup_vectors_np)
    faiss.write_index(index, index_path)

    # Save updated chunks
    with open(chunk_path, "wb") as f:
        pickle.dump(dedup_chunks, f)

    print(f"💾 Saved index: {index_path}")
    print(f"💾 Saved {len(dedup_chunks)} chunks: {chunk_path}")
    if not overwrite:
        print(f"🧮 Merged: {len(existing_chunks)} existing + {len(new_chunks)} new")
        print(f"🧹 Deduplicated: {len(existing_chunks) + len(new_chunks) - len(dedup_chunks)} duplicate chunks removed")
    else:
        print(f"🧼 Overwrite mode: Stored exactly {len(dedup_chunks)} new chunks")


def load_index_and_chunks(key: str):
    index_path = os.path.join(CHUNK_STORE_DIR, f"{key}.index")
    chunk_path = os.path.join(CHUNK_STORE_DIR, f"{key}.chunks.pkl")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found: {index_path}")
    if not os.path.exists(chunk_path):
        raise FileNotFoundError(f"Chunk file not found: {chunk_path}")

    index = faiss.read_index(index_path)
    with open(chunk_path, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def build_general_index():
    print("🔍 Scanning for all project indexes...")
    all_vectors = []
    all_chunks = []

    for fname in os.listdir(CHUNK_STORE_DIR):
        if fname.endswith(".chunks.pkl") and not fname.startswith("general"):
            key = fname.replace(".chunks.pkl", "")
            try:
                index, chunks = load_index_and_chunks(key)
                for i in range(index.ntotal):
                    vec = index.reconstruct(i)
                    all_vectors.append(vec)
                all_chunks.extend(chunks)
                print(f"✅ Included {len(chunks)} chunks from {key}")
            except Exception as e:
                print(f"⚠️ Skipped {key}: {e}")

    if not all_vectors:
        print("⚠️ No chunks found to build general index.")
        return

    vectors_np = np.array(all_vectors, dtype=np.float32)
    save_index(vectors_np, all_chunks, "general", overwrite=True)
