from fastapi import APIRouter
from pydantic import BaseModel
from ..retrieval.extractor import extract_tasks

router = APIRouter()

class TaskRequest(BaseModel):
    project: str

@router.post("/")
def get_tasks(req: TaskRequest):
    tasks = extract_tasks(req.project)
    return {"tasks": tasks}
