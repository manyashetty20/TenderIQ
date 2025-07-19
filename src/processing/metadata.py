import re
import os
from src.processing.parser import extract_text

def extract_metadata(file_path: str) -> dict:
    meta = {
        "filename": os.path.basename(file_path),
        "extension": os.path.splitext(file_path)[1],
        "size_kb": os.path.getsize(file_path) // 1024,
    }

    try:
        text = extract_text(file_path)

        # ✅ CORRECT: normalize ALL whitespace
        clean_text = re.sub(r"\s+", " ", text).strip()

        match = re.search(
            r"Tender\s*Ref[^:]*No[^:]*[:\-]?\s*([A-Z0-9/\-]+)",
            clean_text,
            re.IGNORECASE
        )
        if match:
            meta["tender_ref"] = match.group(1)

        print("📌 Extracted metadata:", meta)

    except Exception as e:
        print(f"⚠️ Metadata extraction failed: {e}")

    return meta
