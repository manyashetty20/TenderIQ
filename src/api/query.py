from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import traceback
import os
import json
import time
import numpy as np
import faiss
import re

from src.embedding.index import load_index_and_chunks
from src.embedding.model import get_embedder
from src.retrieval.prompt import build_prompt, build_stat_prompt
from src.llm.inference import get_model_response

router = APIRouter()
VECTOR_STORE_DIR = "data/vector_stores"
UPLOAD_METADATA = "data/uploads/file_versions.json"


class QueryRequest(BaseModel):
    project: str
    question: str
    model: str = "llama"

# ✅ Detect statistical question
def is_stat_query(q):
    keywords = ["average", "mean", "total", "sum", "range", "maximum", "minimum", "max", "min", "how many", "quantity", "number of", "count", "percent", "percentage", "duration"]
    return any(k in q.lower() for k in keywords)

# ✅ Detect numeric chunks
def is_statistical_chunk(text):
    return bool(re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', text))  # e.g. 1,234.56 or 1234


def get_combined_index_and_chunks(project: str):
    safe_project = project.replace(" ", "_").replace("/", "_").lower()

    if safe_project == "general":
        print("✅ Using general index")
        return load_index_and_chunks("general")

    amend_key = f"{safe_project}_amendment"
    main_key = f"{safe_project}_main"

    all_vectors = []
    all_chunks = []

    for key in [amend_key, main_key]:
        index_path = os.path.join(VECTOR_STORE_DIR, key + ".index")
        chunk_path = os.path.join(VECTOR_STORE_DIR, key + ".chunks.pkl")

        if os.path.exists(index_path) and os.path.exists(chunk_path):
            try:
                index, chunks = load_index_and_chunks(key)
                for i in range(index.ntotal):
                    vec = index.reconstruct(i)
                    all_vectors.append(vec)
                all_chunks.extend(chunks)
                print(f"✅ Loaded {len(chunks)} chunks from {key}")
            except Exception as e:
                print(f"⚠️ Failed to load {key}: {e}")

    if not all_vectors:
        raise FileNotFoundError(f"No index found for project '{project}'.")

    dim = len(all_vectors[0])
    merged_index = faiss.IndexFlatL2(dim)
    merged_index.add(np.array(all_vectors, dtype=np.float32))

    return merged_index, all_chunks


@router.post("/")
def ask_question(req: QueryRequest):
    try:
        total_start = time.perf_counter()
        safe_project = req.project.replace("/", "_").replace(" ", "_").lower()

        # Log question
        log_path = f"data/chunks/{safe_project}_questions.json"
        os.makedirs("data/chunks", exist_ok=True)
        entry = {"timestamp": datetime.now().isoformat(), "question": req.question}
        try:
            with open(log_path) as f:
                log_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log_data = []
        log_data.append(entry)
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        # Embed question
        embedder = get_embedder()
        embed_start = time.perf_counter()
        q_vector = embedder.encode([req.question]).astype("float32")
        embed_time = time.perf_counter() - embed_start

        # Load merged index and chunks
        index, chunks = get_combined_index_and_chunks(req.project)

        # Retrieve top chunks
        retr_start = time.perf_counter()
        score_threshold = 0.0
        D, I = index.search(q_vector, index.ntotal)

        chunk_scores = [(chunks[idx], 1 - D[0][rank]) for rank, idx in enumerate(I[0]) if idx < len(chunks)]
        seen_text = set()
        relevant = []

        print("\n🔍 Sorted top retrieved chunks and similarity scores:")
        for chunk, score in chunk_scores:
            if chunk not in seen_text and score >= score_threshold:
                seen_text.add(chunk)
                relevant.append(chunk)
                preview = chunk[:120].replace("\n", " ").strip()
                print(f" • Similarity: {score:.3f} | {preview}")
                if len(relevant) >= 30:
                    break

        # Fallback
        if not relevant:
            print("⚠️ No chunks passed the score threshold. Triggering fallback.")
            fallback_count = 3
            for idx in I[0][:fallback_count]:
                if idx < len(chunks):
                    text = chunks[idx].strip()
                    if text not in seen_text:
                        seen_text.add(text)
                        relevant.append(text)

        retr_time = time.perf_counter() - retr_start


        # ✅ Inject numeric chunks if stat query
        if is_stat_query(req.question) and len(relevant) < 10:
            numeric_chunks = [c for c in chunks if is_statistical_chunk(c)]
            for c in numeric_chunks:
                if c not in seen_text:
                    relevant.append(c)
                    seen_text.add(c)
                if len(relevant) >= 30:
                    break

        # Prompt selection
        if is_stat_query(req.question):
            from src.retrieval.prompt import build_stat_prompt
            prompt = build_stat_prompt(req.question, relevant)
        else:
            prompt = build_prompt(req.question, relevant)

        # LLM
        answer, llm_time = get_model_response(prompt, req.model)

        if not answer.strip():
            raise HTTPException(status_code=404, detail="LLM returned no meaningful answer.")

        total_time = time.perf_counter() - total_start
        return {
            "question": req.question,
            "answer": answer,
            "chunks": relevant,
            "timings": {
                "embedding": round(embed_time, 3),
                "retrieval": round(retr_time, 3),
                "llm": round(llm_time, 3),
                "total": round(total_time, 3)
            }
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
