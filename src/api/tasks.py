from fastapi import APIRouter
from pydantic import BaseModel
import os
import json

from src.embedding.index import load_index_and_chunks
from src.llm.inference import get_model_response
from src.retrieval.extractor import build_task_prompt  # This should build the task-specific prompt

# ---------------------- Setup ----------------------
TASK_DIR = "data/tasks"
os.makedirs(TASK_DIR, exist_ok=True)

router = APIRouter()

# ---------------------- Request Schema ----------------------
class TaskRequest(BaseModel):
    project: str
    model: str = "llama"  # Optional field, defaults to llama if not specified

# ---------------------- POST /tasks/ ----------------------
@router.post("/")
async def generate_tasks(req: TaskRequest):
    try:
        safe_project = req.project.replace(" ", "_").replace("/", "_")
        index_path = f"data/vector_stores/{safe_project}"

        # Load FAISS index and chunks
        index, chunks = load_index_and_chunks(index_path)

        # Build task-extraction prompt
        prompt = build_task_prompt(chunks)

        # Get response from selected model
        result, _ = get_model_response(prompt, model=req.model)

        # Parse result as JSON (expecting list of tasks)
        try:
            tasks = json.loads(result) if result.strip().startswith("[") else []
        except json.JSONDecodeError:
            tasks = [{"task": "⚠️ Failed to parse tasks", "status": "Error"}]

        # Save tasks to file
        task_file = os.path.join(TASK_DIR, f"{safe_project}.json")
        with open(task_file, "w") as f:
            json.dump(tasks, f, indent=2)

        return {
            "project": req.project,
            "tasks": tasks,
            "model_used": req.model
        }

    except Exception as e:
        return {"error": str(e)}

# ---------------------- GET /tasks/{project_name} ----------------------
@router.get("/{project_name}")
async def get_tasks(project_name: str):
    safe_project = project_name.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(TASK_DIR, f"{safe_project}.json")

    if not os.path.exists(file_path):
        return {"project": project_name, "tasks": []}
    
    with open(file_path, "r") as f:
        tasks = json.load(f)

    return {"project": project_name, "tasks": tasks}
