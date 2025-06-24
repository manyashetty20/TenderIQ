from fastapi import APIRouter
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
