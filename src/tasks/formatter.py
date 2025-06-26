import re
from typing import List, Dict

def format_tasks(raw_text: str) -> List[Dict[str, str]]:
    """
    Parse raw LLM response to structured task entries.

    Args:
        raw_text (str): The full text returned by the LLM.

    Returns:
        List[Dict[str, str]]: A list of task dicts with keys: task, deadline, status.
    """
    tasks = []

    # Split by lines
    lines = raw_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove common leading symbols like bullet points or numbers
        line = re.sub(r"^\s*[-*\d.\)]*\s*", "", line)

        # Try to extract a deadline (e.g., July 10, 2025 or 10 July)
        deadline_pattern = r"\b(?:\d{1,2}\s)?(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:,?\s\d{4})?"
        deadline_match = re.search(deadline_pattern, line, re.IGNORECASE)
        deadline = deadline_match.group() if deadline_match else "TBD"

        task = line

        tasks.append({
            "task": task,
            "deadline": deadline,
            "status": "Pending"
        })

    return tasks
