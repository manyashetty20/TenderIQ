from fastapi import APIRouter, UploadFile, File, Form
import os
import json
from datetime import datetime
from src.processing.parser import extract_text
from src.processing.chunker import split_into_chunks
from src.embedding.model import get_embedder
from src.embedding.index import save_index, load_index_and_chunks, build_general_index
import shutil
import tempfile
from fastapi.responses import JSONResponse

router = APIRouter()

UPLOAD_DIR = "data/uploads"
METADATA_PATH = os.path.join(UPLOAD_DIR, "file_versions.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load or init metadata
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH) as f:
        version_tracker = json.load(f)
else:
    version_tracker = {}


# ---------- helper: merge amendment text with existing main ----------
def merge_texts(main_txt: str, amend_txt: str) -> str:
    return amend_txt.strip() + "\n\n" + main_txt.strip()


@router.post("/")
def upload_document(
    file: UploadFile = File(...),
    project: str = Form(...),
    doc_type: str = Form(...),
    version: str = Form(...)
):
    try:
        # ----- 1. Save file -----------------------------------------------------
        project_dir = os.path.join(UPLOAD_DIR, project.replace(" ", "_"))
        os.makedirs(project_dir, exist_ok=True)

        version_filename = f"{doc_type}_v{version}_{file.filename}"
        file_path = os.path.join(project_dir, version_filename)

        with open(file_path, "wb") as f_out:
            f_out.write(file.file.read())
        print(f"📁 Saved: {file_path}")

        # ----- 2. Extract text --------------------------------------------------
        new_text = extract_text(file_path)
        if not new_text.strip():
            return {"error": "Could not extract text from file."}

        # ----- 3. Decide *effective* text to embed -----------------------------
        safe_project = project.replace(" ", "_").replace("/", "_")
        base_index_path = f"data/vector_stores/{safe_project}"

        if doc_type.lower().startswith("amendment") and os.path.exists(base_index_path + ".index"):
            main_meta = version_tracker.get(project, {}).get("Main")
            if not main_meta:
                merged_text = new_text
            else:
                main_file_path = os.path.join(project_dir, main_meta["filename"])
                main_text = extract_text(main_file_path)
                merged_text = merge_texts(main_text, new_text)
        else:
            merged_text = new_text

        # ----- 4. Chunk + embed -------------------------------------------------
        chunks = split_into_chunks(merged_text)
        embedder = get_embedder()
        embeddings = embedder.encode(chunks)

        # ----- 5. Save / overwrite base index -----------------------------------
        save_index(embeddings, chunks, safe_project)
        print(f"✅ Effective index updated for: {project}")

        # ✅ ----- 6. Rebuild the general index ----------------------------------
        print("🔄 Rebuilding general project index...")
        try:
            build_general_index()
            print("✅ General index rebuild triggered successfully from upload.")
        except Exception as e:
            print(f"❌ Error while rebuilding general index: {e}")

        # ----- 7. Update metadata ----------------------------------------------
        version_tracker.setdefault(project, {})
        version_tracker[project][doc_type] = {
            "latest_version": version,
            "filename": version_filename,
            "uploaded_at": datetime.now().isoformat(),
        }
        with open(METADATA_PATH, "w") as f:
            json.dump(version_tracker, f, indent=2)

        return {
            "project": project,
            "doc_type": doc_type,
            "version": version,
            "num_chunks": len(chunks),
            "message": "Upload merged and index rebuilt (including general).",
        }

    except Exception as e:
        print(e)
        return {"error": str(e)}

@router.get("/list_files/{project}")
def list_uploaded_files(project: str):
    safe_project = project.replace(" ", "_")
    project_path = os.path.join(UPLOAD_DIR, safe_project)

    if not os.path.exists(project_path):
        return JSONResponse(content={"files": []})

    files = os.listdir(project_path)
    return JSONResponse(content={"files": files})