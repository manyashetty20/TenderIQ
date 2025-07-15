from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import re
import time
import traceback
from typing import List, Dict, Any, Union
from datetime import datetime, timedelta

from src.embedding.index import load_index_and_chunks
from src.llm.inference import get_model_response
from src.retrieval.extractor import build_task_prompt  # Builds prompt from chunks

# ---------------------- Paths & router ----------------------
TASK_DIR = "data/tasks"
os.makedirs(TASK_DIR, exist_ok=True)

router = APIRouter()

# ---------------------- Request Schema ----------------------
class TaskRequest(BaseModel):
    project: str
    model: str = "llama"

# ---------------------- Regex helpers ----------------------
MONTH_RE = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

REQ_RE = re.compile(r"[A-Z][^.]*\b(?:must|shall)\b[^.]*\.", re.IGNORECASE)
DEADLINE_SENT_RE = re.compile(r"[A-Z][^.]*\b(?:before|by|within)\b[^.]*\.", re.IGNORECASE)

DATE_ANY_RE = re.compile(
    rf"(\d{{4}}-\d{{2}}-\d{{2}}|"
    rf"\d{{1,2}}\s+(?:{MONTH_RE})|"
    rf"(?:{MONTH_RE})\s+\d{{1,2}}|"
    rf"\d{{1,4}}\s*(?:days?|weeks?))", re.IGNORECASE
)

MONTH_TO_NUM = {
    m: i for i, names in enumerate(
        [("jan", "january"), ("feb", "february"), ("mar", "march"),
         ("apr", "april"), ("may",), ("jun", "june"), ("jul", "july"),
         ("aug", "august"), ("sep", "sept", "september"),
         ("oct", "october"), ("nov", "november"), ("dec", "december")],
        start=1)
    for m in names
}

def parse_deadline(text: str) -> Union[datetime, None]:
    text = text.strip().lower()

    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return datetime.fromisoformat(text)
    except ValueError:
        pass

    m = re.fullmatch(r"(\d{1,4})\s*(days?|weeks?)", text)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        delta = timedelta(days=num) if "day" in unit else timedelta(weeks=num)
        return datetime.now() + delta

    m = re.fullmatch(r"(\d{1,2})\s+(" + MONTH_RE + ")", text)
    if m:
        day = int(m.group(1))
        month = MONTH_TO_NUM[m.group(2)[:3]]
        return datetime(datetime.now().year, month, day)

    m = re.fullmatch(r"(" + MONTH_RE + r")\s+(\d{1,2})", text)
    if m:
        month = MONTH_TO_NUM[m.group(1)[:3]]
        day = int(m.group(2))
        return datetime(datetime.now().year, month, day)

    return None

def extract_regex_tasks(all_text: str) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []

    for m in REQ_RE.finditer(all_text):
        sent = m.group(0).strip()
        date_match = DATE_ANY_RE.search(sent)
        deadline_str = date_match.group(0) if date_match else ""
        tasks.append({
            "task": sent,
            "deadline": deadline_str,
            "priority": "high" if deadline_str else "normal",
            "deadline_parsed": parse_deadline(deadline_str) if deadline_str else None,
            "source": "regex",
            "category": "requirement"
        })

    for m in DEADLINE_SENT_RE.finditer(all_text):
        sent = m.group(0).strip()
        date_match = DATE_ANY_RE.search(sent)
        deadline_str = date_match.group(0) if date_match else ""
        tasks.append({
            "task": sent,
            "deadline": deadline_str,
            "priority": "high",
            "deadline_parsed": parse_deadline(deadline_str) if deadline_str else None,
            "source": "regex",
            "category": "deadline"
        })

    return tasks

def tag_llm_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for t in tasks:
        if not isinstance(t, dict):
            continue
        text = json.dumps(t)
        date_match = DATE_ANY_RE.search(text)
        if date_match:
            dstr = date_match.group(0)
            t["deadline"] = t.get("deadline", dstr)
            t["priority"] = "high"
            t["deadline_parsed"] = parse_deadline(dstr)
        else:
            t.setdefault("deadline", "")
            t.setdefault("priority", "normal")
            t["deadline_parsed"] = None
    return tasks

def sort_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key(t):
        pr = 0 if t.get("priority") == "high" else 1
        dt = t.get("deadline_parsed") or datetime.max
        return (pr, dt)
    return sorted(tasks, key=key)

@router.post("/")
async def generate_tasks(req: TaskRequest):
    try:
        timings = {}
        total_start = time.perf_counter()

        safe_proj = req.project.replace(" ", "_").replace("/", "_").lower()
        base_path = os.path.join("data", "vector_stores")

        amend_key = f"{safe_proj}_amendment"
        main_key = f"{safe_proj}_main"

        chunks = []

        amend_index_path = os.path.join(base_path, f"{amend_key}.index")
        amend_chunk_path = os.path.join(base_path, f"{amend_key}.chunks.pkl")

        if os.path.exists(amend_index_path) and os.path.exists(amend_chunk_path):
            _, amend_chunks = load_index_and_chunks(amend_key)
            chunks.extend(amend_chunks)
            print(f"✅ Loaded {len(amend_chunks)} amendment chunks")

        main_index_path = os.path.join(base_path, f"{main_key}.index")
        main_chunk_path = os.path.join(base_path, f"{main_key}.chunks.pkl")

        if os.path.exists(main_index_path) and os.path.exists(main_chunk_path):
            _, main_chunks = load_index_and_chunks(main_key)
            chunks.extend(main_chunks)
            print(f"✅ Loaded {len(main_chunks)} main chunks")

        if not chunks:
            raise FileNotFoundError(f"No index found for project '{req.project}'")

        timings["retrieval"] = round(time.perf_counter() - total_start, 3)
        full_text = "\n".join(chunks)

        regex_tasks = extract_regex_tasks(full_text)

        prompt = build_task_prompt(chunks)
        llm_ans, llm_time = get_model_response(prompt, model=req.model)
        timings["llm"] = round(llm_time, 3)

        try:
            match = re.search(r"\[\s*{.*?}\s*\]", llm_ans, re.DOTALL)
            llm_tasks = json.loads(match.group()) if match else []
        except json.JSONDecodeError:
            llm_tasks = [{"task": "⚠️ Parse error", "priority": "normal"}]

        llm_tasks = tag_llm_tasks(llm_tasks)
        tasks = sort_tasks(regex_tasks + llm_tasks)

        for t in tasks:
            t.pop("deadline_parsed", None)

        with open(os.path.join(TASK_DIR, f"{safe_proj}.json"), "w") as f:
            json.dump(tasks, f, indent=2)

        timings["total"] = round(time.perf_counter() - total_start, 3)

        return {
            "project": req.project,
            "tasks": tasks,
            "timings": timings,
            "model_used": req.model
        }

    except Exception as e:
        print("❌ Task extraction error:")
        traceback.print_exc()
        return {"error": str(e)}
