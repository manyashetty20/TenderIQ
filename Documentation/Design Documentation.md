**TenderIQ** **–** **Detailed** **Design** **Documentation**

**Repository**[**:**
**<u>github.com/manyashetty20/TenderIQ</u>**](https://github.com/manyashetty20/TenderIQ)

**Table** **of** **Contents**

> 1\. <u>Overview</u>
>
> 2\. <u>Architecture Diagram</u>
>
> 3\. <u>Technology Stack</u>
>
> 4\. <u>Component Design</u>
>
> 5\. <u>Backend API Design</u>
>
> 6\. <u>Frontend (Streamlit) Design</u>
>
> 7\. <u>Data Flow</u>
>
> 8\. <u>LLM Model Handling</u>
>
> 9\. <u>File Structure</u>
>
> 10\. <u>Design Decisions</u>
>
> 11\. <u>Future Enhancements</u>

**1.** **Overview**

**TenderIQ** is an AI-powered contract analysis platform for tender
documents. It allows users to upload tender documents, process them
using language models, and ask contextual questions to retrieve relevant
answers.

**2.** **Architecture** **Diagram**

> ┌────────────┐
>
> │ Streamlit UI │
>
> └──────┬─────┘
>
> │ (requests)
>
> ▼
>
> ┌─────────────┐
>
> │ FastAPI Backend │
>
> └──────┬──────┘
>
> │
>
> ▼
>
> ┌───────────────────────────────┐
>
> │ Processing Layer (Parser, Chunker, Embedder) │
>
> └──────┬────────────────────────┘
>
> │
>
> ▼
>
> ┌─────────────────────────────────┐
>
> │ Embedding & Index Store (in-memory or file-based) │
>
> └─────────────────────────────────┘

**3.** **Technology** **Stack**

> **Layer**
>
> Frontend
>
> Backend
>
> Embedding
>
> Text Parsing
>
> Storage
>
> Virtualization

**Tool/Tech**

Streamlit

FastAPI

LLaMA/Groq (LLMs)

PyMuPDF

JSON, Local FS

Python venv

**4.** **Component** **Design**

**1.** **Frontend** **(Streamlit)**

> ● Project selection
>
> ● File upload
>
> ● Button-triggered document pipeline (parse → chunk → embed → index)
>
> ● Model selection (radio: LLaMA or Groq)
>
> ● Ask a Question input

**2.** **API** **(FastAPI)**

> ● Routes:
>
> ○ /upload/: Upload and store document
>
> ○ /parse/: Extract text from documents
>
> ○ /chunk/: Split text into sections
>
> ○ /embed/: Generate vector embeddings
>
> ○ /index/: Save embeddings
>
> ○ /ask/: Accepts a question and returns the most relevant answer

These buttons are linked to FastAPI routes using requests.post() in the
Streamlit frontend, allowing interactive end-to-end document processing.

**3.** **Processing** **Layer**

> ● parser.py: Extracts clean text from uploaded PDF/TXT
>
> ● chunker.py: Splits content into overlapping text chunks
>
> ● model.py: Interfaces with selected LLM (Groq API or LLaMA)
>
> ● index.py: Saves and loads indexed embeddings for search

**5.** **Backend** **API** **Design**

> **Endpoint**
>
> /upload/
>
> /parse/
>
> **Method** **Description**

POST Uploads a document

POST Extracts text

> /chunk/ POST
>
> /embed/ POST
>
> /index/ POST
>
> /ask/ POST
>
> /project GET
>
> s/

Splits text into chunks

Generates embeddings

Saves index

Returns answer based on query

Fetch all projects from JSON store

**6.Frontend** **(Streamlit)** **Design**

**Sidebar** **Elements:**

> ● TenderIQ Title
>
> ● Dropdown: Select project
>
> ● Input + Button: Create new project
>
> ● Radio button: Select model (LLaMA or Groq)

**Main** **Area:**

> ● Upload interface
>
> ● Buttons: Parse, Chunk, Embed, Save Index
>
> ● Ask a Question textbox
>
> ● Answer display area

Each button triggers a specific API route using requests.post().

**7.** **Data** **Flow**

> 1\. User selects a project
>
> 2\. Uploads a PDF file
>
> 3\. Presses buttons in order:
>
> ○ Parse → Chunk → Embed → Save Index
>
> 4\. Selects LLM backend (LLaMA or Groq)
>
> 5\. Asks a question → API performs similarity search → Answer returned

**8.** **LLM** **Model** **Handling**

**Model** **Selection** **(via** **Sidebar):**

> ● LLaMA → Local inference (planned or basic testing)
>
> ● Groq → Remote inference using hosted LLM APIs

**Tasks** **where** **model** **is** **used:**

> ● **Embedding**: Each chunk is passed to the model for vector
> generation
>
> ● **Ask**: User’s query is embedded and compared against indexed
> vectors

**Dynamic** **Behavior:**

> ● Streamlit frontend sends selected model as part of the request
> payload
>
> ● FastAPI backend dynamically routes to the appropriate LLM engine

**9.** **File** **Structure**

TenderIQ/

│

├── app.py \# Streamlit entry‑point

├── requirements.txt

├── README.md

├── .env.example \# env‑var template (API keys, ports, etc.)

│

├── data/

│ ├── uploads/ \# ⇢ uploaded PDFs / TXTs (per‑project sub‑dirs)

│ │ └── .gitkeep

│ └── projects.json \# ⇢ project metadata & settings

│

├── src/

│ ├── api/ \# FastAPI layer

│ │ ├── \_\_init\_\_.py

│ │ ├── main.py

│ │ ├── upload.py

\# includes router registration

> \# /upload – store file

│ │ ├── parse.py \# /parse – run parser

│ │ ├── chunk.py \# /chunk – run chunker

│ │ ├── embed.py \# /embed – generate embeddings

│ │ ├── index.py \# /index – save index

│ │ └── query.py \# /ask – answer questions

│ │

│ ├── processing/ \# traditional NLP pipeline

│ │ ├── \_\_init\_\_.py

│ │ ├── parser.py

│ │ └── chunker.py

\# text extraction

> \# split into overlapping windows

│ │

│ ├── embedding/ \# model wrappers & vector store

│ │ ├── \_\_init\_\_.py

│ │ ├── model.py

│ │ └── index.py

> \# Groq / LLaMA inference helpers

\# save / load FAISS‑like index

│ │

│ ├── models/ \# optional local checkpoints

│ │ └── llama/

│ │ └── .gitkeep

│ │

│ └── utils/

│ └── config.py \# paths, constants, helper funcs

│

└── tests/

> └── test_api.py \# pytest smoke tests

**10.Design** **Decisions**

> ● **Why** **Streamlit**: Lightweight, easy to prototype internal tools
>
> ● **Why** **FastAPI**: Fast, async-ready backend with automatic
> OpenAPI docs
>
> ● **Why** **Chunking**: Improves model context understanding
>
> ● **Groq** **vs** **LLaMA**: Flexibility between speed (Groq) and
> control (LLaMA)
>
> ● **JSON** **Storage**: Simpler than DB for MVP/demo scale

**11.Future** **Enhancements**

> ● Add user authentication & role-based access
>
> ● Integrate vector DB (e.g., FAISS, Weaviate)
>
> ● Model upload option (custom fine-tuned models)
>
> ● Improve PDF parsing robustness
>
> ● Save user query history
>
> ● UI theming for production use
>
> ● Dockerize the app for deployment
