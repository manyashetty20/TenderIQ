<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
=======
from fastapi import APIRouter
>>>>>>> project-a-branch
from pydantic import BaseModel
from src.embedding.index import load_index_and_chunks
from src.embedding.model import get_embedder
from src.retrieval.prompt import build_prompt
<<<<<<< HEAD
from src.llm.inference import get_model_response
from datetime import datetime
import traceback
import os
import json
import time
=======
from src.llm.inference import get_llm_response
import numpy as np
import os
import json
from datetime import datetime
>>>>>>> project-a-branch

router = APIRouter()

class QueryRequest(BaseModel):
    project: str
    question: str
<<<<<<< HEAD
    model: str = "llama"  # Default model if not specified
=======
>>>>>>> project-a-branch

@router.post("/")
def ask_question(req: QueryRequest):
    try:
<<<<<<< HEAD
        total_start = time.perf_counter()

        # Format project name safely for file paths
        safe_project = req.project.replace("/", "_").replace(" ", "_")
        filepath = f"data/chunks/{safe_project}_questions.json"
        os.makedirs("data/chunks", exist_ok=True)

        # Save question to JSON log
=======
        # Save question to backend disk under chunks folder
        os.makedirs("data/chunks", exist_ok=True)
        safe_project = req.project.replace("/", "_").replace(" ", "_")
        filepath = f"data/chunks/{safe_project}_questions.json"
>>>>>>> project-a-branch
        question_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": req.question
        }

<<<<<<< HEAD
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data.append(question_entry)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Load FAISS index and chunks
        index_path = f"data/vector_stores/{safe_project}"
        index, chunks = load_index_and_chunks(index_path)

        # Embedding the question
        embed_start = time.perf_counter()
        embedder = get_embedder()
        q_vector = embedder.encode([req.question]).astype("float32")
        embed_time = time.perf_counter() - embed_start

        # Retrieval step
        retrieval_start = time.perf_counter()
        D, I = index.search(q_vector, k=5)
        relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
        retrieval_time = time.perf_counter() - retrieval_start

        print(f"🔍 Found {len(relevant_chunks)} relevant chunks")

        if not relevant_chunks:
            return {
                "question": req.question,
                "answer": "No relevant content found in document to answer the question.",
                "chunks": [],
                "timings": {}
            }

        # Build prompt and call model
        prompt = build_prompt(req.question, relevant_chunks)
        answer, llm_time = get_model_response(prompt, req.model)

        total_time = time.perf_counter() - total_start
=======
        data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

        data.append(question_entry)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Load FAISS index + chunks
        index_path = f"data/vector_stores/{req.project}"
        index, chunks = load_index_and_chunks(index_path)

        # Get embedding for the question
        embedder = get_embedder()
        q_vector = embedder.encode([req.question]).astype("float32")

        # Search for top 5 relevant chunks
        D, I = index.search(q_vector, k=5)
        relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]

        # Build prompt
        prompt = build_prompt(req.question, relevant_chunks)

        # Get answer (stubbed or real)
        answer = get_llm_response(prompt)
>>>>>>> project-a-branch

        return {
            "question": req.question,
            "answer": answer,
<<<<<<< HEAD
            "chunks": relevant_chunks,
            "timings": {
                "embedding": round(embed_time, 3),
                "retrieval": round(retrieval_time, 3),
                "llm": round(llm_time, 3),
                "total": round(total_time, 3)
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ Exception during query:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
=======
            "chunks": relevant_chunks
        }
    except Exception as e:
        return {"error": str(e)}
>>>>>>> project-a-branch
