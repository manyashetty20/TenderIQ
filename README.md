# 🤖 TenderIQ

**TenderIQ** is an intelligent document understanding platform for tenders. It helps teams extract, search, and query large tender documents using modern LLMs.

---

## 👋 Overview

TenderIQ lets you:

- 📄 Upload tender PDFs or TXT files per project
- 🧾 Parse and chunk large documents into manageable blocks
- 🤖 Embed using **Groq** or **LLaMA** for vector similarity search
- 💬 Ask natural language questions and receive context-rich answers
- 🗂 Organize and reuse processing results project-wise

The platform combines a **Streamlit frontend** with a **FastAPI backend**, along with PyMuPDF-based parsing and LLM-powered embeddings.

---

## 🚀 Quickstart Setup

```bash
# 1. Clone the repo
git clone https://github.com/manyashetty20/TenderIQ.git
cd TenderIQ

# 2. Create & activate virtual environment
python3 -m venv env
source env/bin/activate  # or env\Scripts\activate (Windows)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Groq API key
cp .env.example .env
# Edit .env and add GROQ_API_KEY=your_key

# 🤖 TenderIQ

**TenderIQ** is an intelligent document understanding platform for tenders. It helps teams extract, search, and query large tender documents using modern LLMs.
```
## 🧠 Model Requirements

If using the **LLaMA model** locally, download the appropriate weights from Hugging Face:

🔗 [Llama-2-7B-Chat-GGUF](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf)

After downloading, configure to the model path.


## 🗝️ Environment Variables
| Variable        | Description              |
|-----------------|--------------------------|
| `GROQ_API_KEY`  | API key for Groq cloud   |
| `LLAMA_MODEL`   | (optional) Path/ID of local LLaMA checkpoint |
---

## 💽 Running the App

### Start FastAPI Backend
```bash
uvicorn src.api.main:app --reload
```

### Start Streamlit Frontend
```bash
streamlit run app.py
```

Visit [http://localhost:8501](http://localhost:8501) to start using TenderIQ.

---

## 🧠 Usage Guide

1. **Project Selection**
   - Select or create a new tender project from the sidebar

2. **Upload Document**
   - Upload `.pdf` or `.txt` file (stored locally)

3. **Choose Model**
   - Use sidebar radio buttons:
     - 🧠 **Groq** (cloud)
     - 🦙 **LLaMA** (local)

4. **Process Document**
   - 🔍 `Parse` → extract raw text
   - 🧩 `Chunk` → split into overlapping text blocks
   - 🧠 `Embed` → generate embeddings
   - 💾 `Save Index`

5. **Ask Questions**
   - Type any question related to the uploaded document
   - See LLM-based answers powered by your selected model

6. **Extract Tasks**
   - Get all tasks from documents

---

## 🗂 Project Structure

```
TenderIQ/
│
├── app.py                     # Streamlit frontend entry-point
├── requirements.txt
├── README.md
│
├── data/
│   ├── uploads/               # Uploaded files per project
│   └── projects.json          # Metadata about all projects
│
├── src/
│   ├── api/                   # FastAPI routes for processing 
│   │   ├── main.py
│   │   ├── upload.py
│   │   ├── parse.py
│   │   ├── chunk.py
│   │   ├── embed.py
│   │   └── query.py
│   │
│   ├── processing/
│   │   ├── parser.py          # PDF/TXT parsing using PyMuPDF
│   │   └── chunker.py
│   │
│   ├── embedding/
│   │   ├── model.py           # Handles embedding via LLaMA/Groq
│   │   └── index.py           # Save/load embedding index
│   │
│   └── utils/
│       └── config.py
│
└── tests/
    └── test_api.py
```


## 🛠️ Tech Stack
| Layer        | Technology |
|--------------|------------|
| Frontend     | Streamlit  |
| Backend      | FastAPI    |
| Parsing      | PyMuPDF    |
| LLMs         | Groq, LLaMA|
| Embeddings   | FAISS‑style store |
| Language     | Python 3.9+|



---

## 📌 Notes

- Text extraction uses **PyMuPDF** for precise layout-based parsing
- Embeddings are stored per project for reuse and efficiency
- LLMs are modular – add your own with minor changes in `embedding/model.py`

---

## 📤 Artifacts & Docs

| Dataset Uploads | Embedding Index | Models      | Docs              |
|-----------------|------------------|-------------|-------------------|
| `data/uploads`  | `data/index/`    | Groq, LLaMA | 📄 User Guide (TBD)|

---

## 🙌 Contributions

We welcome ideas and feedback! Please open issues or pull requests for:

- Model integrations
- UI/UX improvements
- Vector store enhancements


---

## 👩‍💻 Author

**Manya Shetty** |
**Riddhi Samitha** | 
**Md Kalim**   
Intern @ United Telecoms Ltd.  
GitHub: [@manyashetty20](https://github.com/manyashetty20)
