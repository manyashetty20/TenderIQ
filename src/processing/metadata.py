import os

def extract_metadata(file_path: str) -> dict:
    return {
        "filename": os.path.basename(file_path),
        "extension": os.path.splitext(file_path)[1],
        "size_kb": os.path.getsize(file_path) // 1024
    }
