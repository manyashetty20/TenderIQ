import fitz
import docx

def parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    all_text = []

    for i, page in enumerate(doc):
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1]), round(b[0])))
        page_text = "\n".join(b[4].strip() for b in blocks if b[4].strip())
        print(f"[Page {i+1}] Extracted {len(page_text)} characters, {len(blocks)} blocks")
        all_text.append(page_text)

    combined = "\n\n".join(all_text)
    return clean_text(combined)

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

def clean_text(text: str) -> str:
    import re
    lines = text.splitlines()
    seen = set()
    cleaned = []

    for line in lines:
        norm = line.strip()
        if norm:
            # Remove common page footer like "Page X of Y"
            if re.match(r"(?i)^page \\d+ of \\d+", norm):
                continue
            if norm not in seen:
                seen.add(norm)
                cleaned.append(norm)

    return "\n".join(cleaned)
