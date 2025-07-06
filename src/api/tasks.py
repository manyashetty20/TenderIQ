from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import re
import time 
import traceback
from typing import List, Dict, Any
from datetime import datetime, timedelta
from typing import Union 

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

# A. sentences with must/shall
REQ_RE = re.compile(r"[A-Z][^.]*\b(?:must|shall)\b[^.]*\.", re.IGNORECASE)

# B. sentences with by/before/within + date
DEADLINE_SENT_RE = re.compile(
    r"[A-Z][^.]*\b(?:before|by|within)\b[^.]*\.", re.IGNORECASE)

# C. date finder
DATE_ANY_RE = re.compile(
    rf"(\d{{4}}-\d{{2}}-\d{{2}}"                       # 2025-08-12
    rf"|\d{{1,2}}\s+(?:{MONTH_RE})"                    # 12 August
    rf"|(?:{MONTH_RE})\s+\d{{1,2}}"                    # August 12
    rf"|\d{{1,4}}\s*(?:days?|weeks?))",                # 30 days
    re.IGNORECASE,
)

# ---------------------- Date parsing ----------------------
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
    """
    Convert a matched date phrase to an absolute datetime for sorting.
    Returns None if the phrase can't be parsed.
    """
    text = text.strip().lower()

    # ISO yyyy-mm-dd
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return datetime.fromisoformat(text)
    except ValueError:
        pass

    # NN days / weeks
    m = re.fullmatch(r"(\d{1,4})\s*(days?|weeks?)", text)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        delta = timedelta(days=num) if "day" in unit else timedelta(weeks=num)
        return datetime.now() + delta

    # 12 August  (DD Month)
    m = re.fullmatch(r"(\d{1,2})\s+(" + MONTH_RE + ")", text)
    if m:
        day = int(m.group(1))
        month = MONTH_TO_NUM[m.group(2)[:3]]
        year = datetime.now().year
        return datetime(year, month, day)

    # August 12  (Month DD)
    m = re.fullmatch(r"(" + MONTH_RE + r")\s+(\d{1,2})", text)
    if m:
        month = MONTH_TO_NUM[m.group(1)[:3]]
        day = int(m.group(2))
        year = datetime.now().year
        return datetime(year, month, day)

    return None

# ---------------------- Extractors ----------------------
def extract_regex_tasks(all_text: str) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []

    # Requirement sentences
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

    # Deadline sentences
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
        # high priority first; then earliest deadline; then keep original order
        pr = 0 if t.get("priority") == "high" else 1
        dt = t.get("deadline_parsed") or datetime.max
        return (pr, dt)
    return sorted(tasks, key=key)

# ---------------------- Endpoint ----------------------
@router.post("/")
async def generate_tasks(req: TaskRequest):
    try:
        timings = {}
        total_start = time.perf_counter()

        safe_proj = req.project.replace(" ", "_").replace("/", "_")
        index_path = f"data/vector_stores/{safe_proj}"

        # 1. Load chunks
        start = time.perf_counter()
        _, chunks = load_index_and_chunks(index_path)
        timings["retrieval"] = round(time.perf_counter() - start, 3)
        full_text = "\n".join(chunks)

        # 2. Regex tasks
        regex_tasks = extract_regex_tasks(full_text)

        # 3. LLM tasks
        prompt = build_task_prompt(chunks)
        llm_ans, llm_time = get_model_response(prompt, model=req.model)
        timings["llm"] = round(llm_time, 3)

        try:
            match = re.search(r"\[\s*{.*?}\s*\]", llm_ans, re.DOTALL)
            llm_tasks = json.loads(match.group()) if match else []
        except json.JSONDecodeError:
            llm_tasks = [{"task": "⚠️ Parse error", "priority": "normal"}]

        llm_tasks = tag_llm_tasks(llm_tasks)

        # 4. Merge & sort
        tasks = sort_tasks(regex_tasks + llm_tasks)

        # 5. Clean up helper field before saving
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

