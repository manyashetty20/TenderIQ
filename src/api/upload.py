from fastapi import APIRouter, UploadFile, File, Form
import os
<<<<<<< HEAD
import json
from datetime import datetime
=======
>>>>>>> project-a-branch
from src.processing.parser import extract_text
from src.processing.chunker import split_into_chunks
from src.embedding.model import get_embedder
from src.embedding.index import save_index

router = APIRouter()

UPLOAD_DIR = "data/uploads"
<<<<<<< HEAD
METADATA_PATH = os.path.join(UPLOAD_DIR, "file_versions.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load existing version metadata or initialize
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, "r") as f:
        version_tracker = json.load(f)
else:
    version_tracker = {}

=======
os.makedirs(UPLOAD_DIR, exist_ok=True)

>>>>>>> project-a-branch
@router.post("/")
def upload_document(
    file: UploadFile = File(...),
    project: str = Form(...),
    doc_type: str = Form(...),
    version: str = Form(...)
):
    try:
<<<<<<< HEAD
        project_dir = os.path.join(UPLOAD_DIR, project.replace(" ", "_"))
        os.makedirs(project_dir, exist_ok=True)

        version_filename = f"{doc_type}_v{version}_{file.filename}"
        file_path = os.path.join(project_dir, version_filename)

        # Save uploaded file
        with open(file_path, "wb") as f_out:
            f_out.write(file.file.read())
        print(f"📁 File saved to: {file_path}")
=======
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())
>>>>>>> project-a-branch

        # Extract text
        text = extract_text(file_path)
        if not text.strip():
<<<<<<< HEAD
            print("❌ Extracted text is empty.")
            return {"error": "File is empty or could not extract text."}
        print(f"📄 Extracted {len(text)} characters of text.")

        # Split into chunks
        chunks = split_into_chunks(text)
        if not chunks:
            print("❌ No chunks generated.")
            return {"error": "No valid chunks generated."}
        print(f"🔹 Total chunks: {len(chunks)}")

        # Generate embeddings
        embedder = get_embedder()
        embeddings = embedder.encode(chunks)
        print(f"🧠 Total embeddings: {len(embeddings)}")

        # Save index and chunks
        print(f"✅ About to save index for project: {project}")
        safe_project = project.replace(" ", "_").replace("/", "_")
        save_index(embeddings, chunks, safe_project)

        print(f"✅ Finished saving index for: {project}")

        # Update metadata with latest version info
        version_tracker[project] = version_tracker.get(project, {})
        version_tracker[project][doc_type] = {
            "latest_version": version,
            "filename": version_filename,
            "uploaded_at": datetime.now().isoformat()
        }
        with open(METADATA_PATH, "w") as f:
            json.dump(version_tracker, f, indent=2)
=======
            return {"error": "File text could not be extracted or is empty."}

        # Chunk the text
        chunks = split_into_chunks(text)

        # Embed chunks
        embedder = get_embedder()
        embeddings = embedder.encode(chunks).tolist()

        # Save index + metadata
        save_index(embeddings, chunks, project)
>>>>>>> project-a-branch

        return {
            "project": project,
            "doc_type": doc_type,
            "version": version,
            "num_chunks": len(chunks),
            "message": "Upload and processing successful."
        }

    except Exception as e:
<<<<<<< HEAD
        print(f"❌ Exception: {e}")
        return {"error": str(e)}
=======
        return {"error": str(e)}
>>>>>>> project-a-branch
