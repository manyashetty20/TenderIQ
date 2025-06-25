from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json

router = APIRouter()

PROJECTS_FILE = "data/projects.json"
os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)

# 📦 Pydantic model for request body
class ProjectInput(BaseModel):
    project: str

# 🔽 Load from file
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r") as f:
            return json.load(f).get("projects", [])
    return []

# 🔼 Save to file
def save_projects(projects):
    with open(PROJECTS_FILE, "w") as f:
        json.dump({"projects": projects}, f)

# 🔍 Get all projects
@router.get("/projects/")
def get_projects():
    return {"projects": load_projects()}

# ➕ Add new project (JSON input)
@router.post("/projects/")
def add_project(data: ProjectInput):
    name = data.project.strip()
    print("📥 Received project name:", name)

    if not name:
        raise HTTPException(status_code=400, detail="Project name is required.")

    projects = load_projects()
    print("📄 Existing projects:", projects)

    if name in projects:
        raise HTTPException(status_code=400, detail="Project already exists.")

    projects.append(name)
    print("✅ Appending new project:", name)
    save_projects(projects)
    print("📁 Saved updated list to projects.json")

    # Create folders
    base_dirs = [
        f"data/uploads/{name}",
        f"data/vector_stores/{name}",
        f"data/chunks/{name}",
        f"data/tasks/{name}"
    ]
    for dir_path in base_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print("📂 Created folder:", dir_path)

    return {"status": "success", "project": name}
