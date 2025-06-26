from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.embedding.index import load_index_and_chunks
from src.embedding.model import get_embedder
from src.retrieval.prompt import build_prompt
from src.llm.inference import get_model_response
from datetime import datetime
import traceback
import os
import json
import time

router = APIRouter()

class QueryRequest(BaseModel):
    project: str
    question: str
    model: str = "llama"  # default model

@router.post("/")
def ask_question(req: QueryRequest):
    try:
        total_start = time.time()

        # Safe project name for file paths
        safe_project = req.project.replace("/", "_").replace(" ", "_")
        filepath = f"data/chunks/{safe_project}_questions.json"
        os.makedirs("data/chunks", exist_ok=True)

        # Log the question
        question_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": req.question
        }
        data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass
        data.append(question_entry)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Load FAISS index and chunks
        index_path = f"data/vector_stores/{safe_project}"
        index, chunks = load_index_and_chunks(index_path)

        # Embed question
        embed_start = time.time()
        embedder = get_embedder()
        q_vector = embedder.encode([req.question]).astype("float32")
        embed_time = time.time() - embed_start

        # Retrieve relevant chunks
        retrieval_start = time.time()
        D, I = index.search(q_vector, k=5)
        relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
        retrieval_time = time.time() - retrieval_start

        print(f"🔍 Found {len(relevant_chunks)} relevant chunks")

        if not relevant_chunks:
            return {
                "question": req.question,
                "answer": "No relevant content found in document to answer the question.",
                "chunks": [],
                "timings": {}
            }

        # Build LLM prompt
        prompt = build_prompt(req.question, relevant_chunks)

        # Get model response
        answer, llm_time = get_model_response(prompt, req.model)

        total_time = time.time() - total_start

        return {
            "question": req.question,
            "answer": answer,
            "chunks": relevant_chunks,
            "timings": {
                "embedding": round(embed_time, 2),
                "retrieval": round(retrieval_time, 2),
                "llm": round(llm_time, 2),
                "total": round(total_time, 2)
            }
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        print("❌ Exception during query:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
