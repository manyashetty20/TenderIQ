from fastapi import APIRouter, UploadFile, Form
import os
import uuid
from processing.parser import parse_pdf, parse_docx
from processing.chunker import chunk_text
from processing.metadata import extract_metadata
from embedding.model import load_embedder
from embedding.index import build_and_save_index

router = APIRouter()

UPLOAD_DIR = "data/uploads/"
VECTOR_DIR = "data/vector_stores/"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

embedder = load_embedder()

@router.post("/")
async def upload_file(
    project: str = Form(...),
    doc_type: str = Form(...),
    version: int = Form(...),
    file: UploadFile = Form(...)
):
    # 1. Save uploaded file
    file_id = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, file_id)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # 2. Parse file
    if file.filename.endswith(".pdf"):
        text = parse_pdf(save_path)
    elif file.filename.endswith(".docx"):
        text = parse_docx(save_path)
    else:
        return {"error": "Unsupported file type."}

    # 3. Chunk text
    chunks = chunk_text(text)

    # 4. Embed chunks
    vectors = embedder.encode(chunks)

    # 5. Save to FAISS vector DB
    vector_path = os.path.join(VECTOR_DIR, file_id)
    build_and_save_index(vectors, chunks, vector_path)

    return {
        "message": "Uploaded and indexed successfully ✅",
        "chunks": len(chunks)
    }
