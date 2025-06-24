import fitz
import docx

def parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    all_text = []
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"[Page {i+1}] Extracted {len(text)} characters")
        all_text.append(text)
    return "\n".join(all_text)

def parse_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    print(f"[DOCX] Extracted {len(paragraphs)} non-empty paragraphs")
    for i, p in enumerate(paragraphs[:3]):
        print(f"  Preview {i+1}: {p[:100]}...")
    return "\n".join(paragraphs)

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return parse_pdf(file_path)
    elif file_path.endswith(".docx"):
        return parse_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
