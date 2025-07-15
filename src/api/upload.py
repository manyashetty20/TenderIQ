from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import json
import traceback
import numpy as np

from src.processing.parser import extract_text
from src.processing.chunker import split_into_chunks
from src.embedding.model import get_embedder
from src.embedding.index import save_index, load_index_and_chunks, build_general_index

router = APIRouter()

UPLOAD_DIR = "data/uploads"
METADATA_PATH = os.path.join(UPLOAD_DIR, "file_versions.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load or initialize metadata
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH) as f:
        version_tracker = json.load(f)
else:
    version_tracker = {}

# ---------- Helper: Merge amendment with main ----------
def merge_texts(main_txt: str, amend_txt: str) -> str:
    return amend_txt.strip() + "\n\n" + main_txt.strip()

@router.post("/")
def upload_document(
    file: UploadFile = File(...),
    project: str = Form(...),
    doc_type: str = Form(...),  # e.g. "main", "amendment"
    version: str = Form(...)
):
    try:
        # 1. Normalize names
        safe_project = project.replace(" ", "_").replace("/", "_").lower()
        doc_type = doc_type.lower()
        doc_key = f"{safe_project}_{doc_type}"

        # 2. Save uploaded file
        project_dir = os.path.join(UPLOAD_DIR, safe_project)
        os.makedirs(project_dir, exist_ok=True)
        version_filename = f"{doc_type}_v{version}_{file.filename}"
        file_path = os.path.join(project_dir, version_filename)

        with open(file_path, "wb") as f_out:
            f_out.write(file.file.read())
        print(f"📁 Saved: {file_path}")

        # 3. Extract text
        new_text = extract_text(file_path)
        if not new_text.strip():
            return {"error": "Could not extract text from file."}

        # 4. Merge with main if amendment
        if doc_type.startswith("amendment"):
            main_meta = version_tracker.get(project, {}).get("main")
            if main_meta:
                main_file_path = os.path.join(project_dir, main_meta["filename"])
                main_text = extract_text(main_file_path)
                merged_text = merge_texts(main_text, new_text)
            else:
                merged_text = new_text
        else:
            merged_text = new_text

        # 5. Chunk and deduplicate
        new_chunks = split_into_chunks(merged_text)
        print(f"✂️ Split into {len(new_chunks)} chunks")

        # 6. Load existing chunks (if present)
        existing_chunks = []
        index_path = os.path.join("data/vector_stores", doc_key)
        if os.path.exists(index_path + ".index") and os.path.exists(index_path + ".chunks.pkl"):
            try:
                _, old_chunks = load_index_and_chunks(doc_key)
                existing_chunks = old_chunks
                print(f"📦 Loaded {len(old_chunks)} old chunks for merging")
            except Exception as e:
                print(f"⚠️ Could not load existing chunks: {e}")

        # 7. Combine + dedup chunks
        all_chunks = existing_chunks + new_chunks
        seen = set()
        dedup_chunks = []
        for chunk in all_chunks:
            norm = chunk.strip()
            if norm and norm not in seen:
                seen.add(norm)
                dedup_chunks.append(norm)

        print(f"🧹 Deduplicated to {len(dedup_chunks)} chunks")

        # 8. Embed and save (overwrite mode)
        embedder = get_embedder()
        embeddings = embedder.encode(dedup_chunks)
        vectors_np = np.array(embeddings, dtype=np.float32)

        save_index(vectors_np, dedup_chunks, safe_project, doc_type, overwrite=True)
        print(f"✅ Index updated and saved: {doc_key}")

        # 9. Update version metadata
        version_tracker.setdefault(project, {})
        version_tracker[project][doc_type] = {
            "latest_version": version,
            "filename": version_filename,
            "uploaded_at": datetime.now().isoformat()
        }
        with open(METADATA_PATH, "w") as f:
            json.dump(version_tracker, f, indent=2)

        # 10. Rebuild general index
        print("🔄 Rebuilding general index...")
        try:
            build_general_index()
            print("✅ General index rebuilt")
        except Exception as e:
            print(f"❌ Failed to rebuild general index: {e}")

        return {
            "project": project,
            "doc_type": doc_type,
            "version": version,
            "num_chunks": len(new_chunks),
            "message": "Upload successful, index updated, and general index rebuilt"
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


@router.get("/list_files/{project}")
def list_uploaded_files(project: str):
    safe_project = project.replace(" ", "_").lower()
    project_path = os.path.join(UPLOAD_DIR, safe_project)

    if not os.path.exists(project_path):
        return JSONResponse(content={"files": []})

    files = os.listdir(project_path)
    return JSONResponse(content={"files": files})
