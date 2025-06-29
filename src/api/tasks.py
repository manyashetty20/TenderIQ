from fastapi import APIRouter
<<<<<<< HEAD
from pydantic import BaseModel
import os
import json
import re
import time
import traceback

from src.embedding.index import load_index_and_chunks
from src.llm.inference import get_model_response
from src.retrieval.extractor import build_task_prompt  # Builds prompt from chunks

# ---------------------- Setup ----------------------
TASK_DIR = "data/tasks"
os.makedirs(TASK_DIR, exist_ok=True)

router = APIRouter()

# ---------------------- Request Schema ----------------------
class TaskRequest(BaseModel):
    project: str
    model: str = "llama"  # Default to LLaMA

# ---------------------- POST /tasks/ ----------------------
@router.post("/")
async def generate_tasks(req: TaskRequest):
    try:
        timings = {}
        total_start = time.perf_counter()

        # Format project name safely for file paths
        safe_project = req.project.replace(" ", "_").replace("/", "_")
        index_path = f"data/vector_stores/{safe_project}"

        # 🔍 Load index and build task prompt
        retrieval_start = time.perf_counter()
        index, chunks = load_index_and_chunks(index_path)
        prompt = build_task_prompt(chunks)
        timings["retrieval"] = round(time.perf_counter() - retrieval_start, 3)

        # ✍️ Run LLM
        answer, llm_time = get_model_response(prompt, model=req.model)
        timings["llm"] = round(llm_time, 3)

        # 🧩 Parse tasks from LLM result
        try:
            match = re.search(r"\[\s*{.*?}\s*\]", answer, re.DOTALL)
            if match:
                tasks = json.loads(match.group())
            else:
                tasks = [{"task": "⚠️ No valid JSON array found", "status": "Error"}]
        except json.JSONDecodeError:
            tasks = [{"task": "⚠️ Failed to parse tasks", "status": "Error"}]

        # 💾 Save tasks to file
        task_file = os.path.join(TASK_DIR, f"{safe_project}.json")
        with open(task_file, "w") as f:
            json.dump(tasks, f, indent=2)

        timings["total"] = round(time.perf_counter() - total_start, 3)

        return {
            "project": req.project,
            "tasks": tasks,
            "model_used": req.model,
            "timings": timings
        }

    except Exception as e:
        print("❌ Task extraction error:")
        traceback.print_exc()
        return {"error": str(e)}
=======
import json
import os

TASK_DIR = "data/tasks"

router = APIRouter()

@router.get("/{project_name}")
async def get_tasks(project_name: str):
    file_path = os.path.join(TASK_DIR, f"{project_name}.json")
    if not os.path.exists(file_path):
        return {"tasks": []}
    
    with open(file_path, "r") as f:
        tasks = json.load(f)
    
    return {"project": project_name, "tasks": tasks}
>>>>>>> project-a-branch
