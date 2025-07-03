**TenderIQ** **User** **Documentation**

**Project** **Name:** **TenderIQ**

**Table** **of** **Contents**

> 1\. <u>Introduction</u>
>
> 2\. <u>System Requirements</u> 3. <u>Installation & Setup</u>
>
> 4\. <u>Getting Started</u>
>
> 5\. <u>Project Management</u>
>
> 6\. <u>Document Upload & Processing</u> 7. <u>Question Answering</u>
>
> 8\. <u>LLM Model Buttons & Tasks</u>
>
> 9\. <u>Error Handling & Troubleshooting</u> 10. <u>FAQs</u>
>
> 11\. <u>Support & Contact</u>

**Introduction**

**TenderIQ** is an AI-powered web application that helps users analyze
tender documents by enabling easy upload, processing, and querying of
documents. Users can ask questions about the documents and get
AI-generated answers using advanced language models and document
embeddings.

**System** **Requirements**

**For** **Local** **Deployment:**

> ● **Operating** **System**: macOS/Linux/Windows
>
> ● **Python**: 3.9 or higher
>
> ● **Browsers** **Supported**: Chrome, Firefox, Edge

**Required** **Libraries/Tools:**

> ● Python packages: streamlit, fastapi, uvicorn, requests, pydantic,
> etc.
>
> ● Local server access to http://localhost:8000 (FastAPI backend)
>
> ● JSON files and uploads stored in data/ folder

**Installation** **&** **Setup**

**1.** **Clone** **the** **Repository**

git clone https://github.com/manyashetty20/TenderIQ.git

cd TenderIQ

**2.** **Create** **Virtual** **Environment**

python -m venv env

source env/bin/activate

env\Scripts\activate

\# macOS/Linux

\# Windows

**3.** **Install** **Dependencies**

pip install -r requirements.txt

**4.** **Start** **Backend** **(FastAPI)**

uvicorn src.api.main:app --reload

**5.** **Start** **Frontend** **(Streamlit)**

streamlit run app.py

**Getting** **Started**

When you visit the Streamlit web UI, you’ll be presented with a sidebar
and a main workspace.

**Sidebar** **Contains:**

> ● **TenderIQ** **Logo** **and** **Title**
>
> ● **Dropdown** **Menu** for Project Selection
>
> ● **Buttons** to Create or Select Projects
>
> ● **Radio** **Button** to select the LLM model (LLaMA or Groq)
>
> ○ LLaMA: Offline, Local or small-scale inference
>
> ○ Groq: High-speed cloud inference
>
> ● Selected model is used for embedding and question-answering tasks

**Project** **Management**

🔹 **Create** **a** **New** **Project**

> 1\. Go to the sidebar.
>
> 2\. Type the project name.
>
> 3\. Click **Create** or **Select**.
>
> 📂 Project data is stored in data/projects.json.

🔹 **Switch** **Projects**

> ● Use the dropdown menu to switch between existing projects.
>
> ● Each project stores its own documents and indexes.

**Document** **Upload** **&** **Processing**

**Step-by-Step:**

> 1\. Go to the **Upload** section on the main page.
>
> 2\. Select or drag a document file (e.g., .pdf or .txt).
>
> 3\. Choose the relevant **project**.
>
> 4\. Click **Upload**.

**Internal** **Workflow:**

> ● Document is saved in data/uploads/{project}/
>
> ● Text is extracted using a custom parser
>
> ● Text is chunked into small parts
>
> ● Each chunk is embedded (using LLMs)
>
> ● Embeddings are saved as an index

**Question** **Answering**

**How** **to** **Ask:**

> 1\. Navigate to **Ask** **a** **Question**.
>
> 2\. Enter a question about the uploaded documents.
>
> 3\. Click **Submit**.

**LLM** **Model** **Buttons** **&** **Tasks**

The TenderIQ interface includes interactive buttons to perform tasks
using LLMs such as:

> ● **Parse** **Document**: Extracts raw text from the uploaded file.
>
> ● **Chunk** **Document**: Splits the text into smaller logical
> segments.
>
> ● **Embed** **Document**: Generates vector embeddings from the chunks
> using a language model.
>
> ● **Save** **Index**: Saves the embeddings to a searchable index file.
>
> ● **Ask**: Allows the user to enter a question and fetches the most
> relevant answer from the indexed chunks.

**Error** **Handling** **&** **Troubleshooting**

> **Problem**
>
> Upload fails
>
> No answer returned
>
> Project not saving
>
> Server not starting
>
> Parsing errors
>
> **Cause**

File too large or unsupported

Irrelevant or unclear question

Corrupt projects.json

Port conflict / missing package

Poor document formatting

> **Solution**

Use .pdf or .txt under 10MB

Rephrase the question clearly

Delete and regenerate manually

Use another port / reinstall packages

Convert PDF to .txt and retry

**FAQs**

**Q:** **Can** **I** **upload** **multiple** **documents** **to**
**one** **project?**

> Yes. All uploaded documents are processed and indexed together under
> the same project.

**Q:** **Can** **I** **delete** **a** **project?**

Not via the UI. You can manually delete it from data/projects.json and
the relevant upload folder.

**Q:** **Are** **my** **files** **stored** **permanently?**

> Yes, they are saved locally in data/uploads/{project}/ unless deleted
> manually.

**Support** **&** **Contact**

> ● **Developer**: Manya Shetty, Riddhi Samitha, Md Kalim
>
> ●
> **Email**<u>:</u>[<u>shettymanya18@gmail.com</u>](mailto:shettymanya18@gmail.com)
> , [<u>samithariddhi@gmail.com</u>](mailto:samithariddhi@gmail.com) ,
> [<u>kalimmd0205@gmail.com</u>](mailto:kalimmd0205@gmail.com)
>
> ● **GitHub**:
> [<u>https://github.com/manyashetty20/TenderIQ</u>](https://github.com/manyashetty20/TenderIQ)
