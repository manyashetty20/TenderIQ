from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import traceback
import os
import json
import time

from src.embedding.index import load_index_and_chunks
from src.embedding.model import get_embedder
from src.retrieval.prompt import build_prompt
from src.llm.inference import get_model_response

router = APIRouter()

UPLOAD_METADATA = "data/uploads/file_versions.json"

# ---------- Request schema ----------
class QueryRequest(BaseModel):
    project: str
    question: str
    model: str = "llama"   # default model

# ---------- Helper: doc‑type priority ----------
def version_order(project: str) -> list[str]:
    """
    Return doc_types (Amendment, Clarification, QnA, Main…) in the order we
    should try them, based on file_versions.json.
    """
    try:
        with open(UPLOAD_METADATA) as f:
            meta = json.load(f)
    except FileNotFoundError:
        return ["Main"]

    proj_meta = meta.get(project, {})
    if not proj_meta:
        return ["Main"]

    # 1️⃣  Amendments in DESC version order
    amds = [
        (k, int(v.get("latest_version", "0")))
        for k, v in proj_meta.items()
        if k.lower().startswith("amendment")
    ]
    amds_sorted = [k for k, _ in sorted(amds, key=lambda x: x[1], reverse=True)]

    order = amds_sorted
    for t in ("Clarification", "QnA", "Main"):
        if t in proj_meta and t not in order:
            order.append(t)

    return order or ["Main"]

# ---------- Helper: detect “no answer” responses ----------
def looks_empty(txt: str) -> bool:
    if not txt or not txt.strip():
        return True
    low = txt.lower().strip()
    non = [
        "not found",
        "could not",
        "couldn't",
        "no information",
        "not specified",
        "unknown",
        "n/a",
        "no answer",
        "the information is not available in the document."
    ]
    return any(k in low for k in non)

# ---------- FastAPI route ----------
@router.post("/")
def ask_question(req: QueryRequest):
    try:
        total_start = time.perf_counter()

        # -- 1. Log the question ----------------------------------------------
        safe_project = req.project.replace("/", "_").replace(" ", "_")
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

        # -- 2. Embed question ------------------------------------------------
        embedder = get_embedder()
        embed_start = time.perf_counter()
        q_vector = embedder.encode([req.question]).astype("float32")
        embed_time = time.perf_counter() - embed_start

        # -- 3. Load single merged index --------------------------------------
        index_path = f"data/vector_stores/{safe_project}"
        index, chunks = load_index_and_chunks(index_path)

        # -- 4. Search for relevant chunks -------------------------------------
        retr_start = time.perf_counter()

        # ✅ Tunable k & threshold
        k = 30  # How many to pull
        score_threshold = 0.0  # Allow very weak matches!

        D, I = index.search(q_vector, k=k)

        seen_text = set()
        relevant = []

        print("\n🔍 Top retrieved chunks and scores:")
        for distance, idx in zip(D[0], I[0]):
            if idx < len(chunks):
                similarity = 1 - distance
                preview = chunks[idx][:120].replace("\n", " ").strip()
                print(f" • Chunk #{idx} | Similarity: {similarity:.3f} | {preview}")

                if similarity >= score_threshold:
                    text = chunks[idx].strip()
                    if text not in seen_text:
                        seen_text.add(text)
                        relevant.append(text)

        # ✅ Fallback: if *all* chunks too weak, take top 3 anyway
        if not relevant:
            fallback_count = 3
            print(f"\n⚠️ Fallback triggered: using top {fallback_count} chunks anyway.")
            for idx in I[0][:fallback_count]:
                if idx < len(chunks):
                    text = chunks[idx].strip()
                    if text not in seen_text:
                        seen_text.add(text)
                        relevant.append(text)

        retr_time = time.perf_counter() - retr_start

        # -- 5. Generate response from LLM -------------------------------------
        prompt = build_prompt(req.question, relevant)
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

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
