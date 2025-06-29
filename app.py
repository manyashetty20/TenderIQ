import streamlit as st
import requests
import os
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="TenderIQ", layout="wide")

<<<<<<< HEAD
# ---------------------- Project Management -------------------------
def get_projects():
    try:
        res = requests.get(f"{API_BASE}/projects/")
        return res.json().get("projects", [])
    except Exception as e:
        st.error(f"Failed to fetch projects: {e}")
        return []

def add_project(name):
    try:
        res = requests.post(f"{API_BASE}/projects/", json={"project": name})
        if res.ok:
            return True
        st.sidebar.error(f"Error: {res.status_code} - {res.text}")
        return False
    except Exception as e:
        st.sidebar.error(f"Request failed: {e}")
        return False

# ---------------------- Sidebar -------------------------
st.sidebar.title("TenderIQ")

# Model Selector
st.sidebar.subheader("Model Selection")
model_choice = st.sidebar.radio("Choose a model", ["LLaMA", "Groq"])
selected_model = model_choice.lower()  # Ensure "llama"/"groq" lowercase for backend

# Project Selector
st.sidebar.subheader("Project Management")

if "show_input" not in st.session_state:
    st.session_state.show_input = False

if st.sidebar.button("➕ Add New Project"):
    st.session_state.show_input = True

if st.session_state.show_input:
    new_project = st.sidebar.text_input("Enter Project Name", key="new_project")
    if new_project:
        if add_project(new_project):
            st.sidebar.success(f"Project '{new_project}' added!")
            st.session_state.show_input = False
            st.rerun()

project_names = get_projects()
=======
# ---------------------- Sidebar: Project Selection -------------------------
st.sidebar.title("TenderIQ")
st.sidebar.subheader("Project Management")

# Dummy list of projects (replace with backend API call)
project_names = ["Metro Rail Expansion", "Hospital Equipment Supply"]
>>>>>>> project-a-branch
selected_project = st.sidebar.selectbox("Select Tender Project", project_names)
st.sidebar.markdown(f"**Selected:** `{selected_project}`")

# ---------------------- Main Tabs -------------------------
tab1, tab2, tab3 = st.tabs(["📁 Upload", "💬 Chat", "📋 Tasks"])

# ---------------------- Tab 1: Upload -------------------------
with tab1:
    st.header("📁 Upload Tender Document")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
<<<<<<< HEAD

=======
    
>>>>>>> project-a-branch
    doc_type = st.selectbox("Document Type", ["Main", "Amendment", "Clarification", "Q&A"])
    version = st.text_input("Version (e.g., 1 or 2)", "1")

    if uploaded_file and st.button("Upload Document"):
<<<<<<< HEAD
        with st.spinner("Uploading to backend..."):
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                }
                data = {
                    "project": selected_project,
                    "doc_type": doc_type,
                    "version": version
                }
                response = requests.post(f"{API_BASE}/upload/", files=files, data=data)

                if response.status_code == 200:
                    st.success("✅ Document uploaded and processed successfully.")
                    st.json(response.json())
                else:
                    st.error(f"❌ Upload failed with status code {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")
=======
        with st.spinner("Processing document..."):
            # Simulate backend call (replace with requests.post or function call)
            file_path = f"./data/uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            st.success("Document uploaded and processed!")
>>>>>>> project-a-branch

# ---------------------- Tab 2: Chat Interface -------------------------
with tab2:
    st.header("💬 Ask Questions")
    st.markdown("Ask anything about the selected tender document.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your question")

    if st.button("Ask"):
        if user_input:
<<<<<<< HEAD
            with st.spinner("🧠 Processing your query..."):
                try:
                    data = {
                        "project": selected_project,
                        "question": user_input,
                        "model": selected_model
                    }
                    res = requests.post(f"{API_BASE}/ask/", json=data)
                except Exception as e:
                    res = None
                    st.session_state.chat_history.append(
                        (user_input, f"❌ Request failed: {e}", [], {})
                    )

            if res and res.status_code == 200:
                response = res.json()
                answer = response.get("answer", "No answer returned.")
                sources = response.get("chunks", [])
                timings = response.get("timings", {})

                st.session_state.chat_history.append((user_input, answer, sources, timings))
            elif res:
                error_msg = f"❌ Error from backend: {res.status_code}"
                st.session_state.chat_history.append((user_input, error_msg, [], {}))

    for q, a, s, t in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 TenderIQ:** {a}")

        if t:
            with st.expander("🕒 Processing Breakdown"):
                st.markdown(f"- 🧠 **Embedding**: `{t.get('embedding', 'N/A')}s`")
                st.markdown(f"- 🔍 **Retrieval**: `{t.get('retrieval', 'N/A')}s`")
                st.markdown(f"- ✍️ **LLM Inference**: `{t.get('llm', 'N/A')}s`")
                st.markdown(f"- ⏱️ **Total Time**: `{t.get('total', 'N/A')}s`")

        if s:
            for i, chunk in enumerate(s, 1):
                preview = chunk[:120].replace("\n", " ") + ("…" if len(chunk) > 120 else "")
                with st.expander(f"📄 Source {i}: {preview}"):
                    st.markdown(chunk)
        else:
            st.markdown("_No relevant sources found._")

=======
            try:
                data = {
                    "project": selected_project,
                    "question": user_input
                }
                res = requests.post(f"{API_BASE}/ask/", json=data)
                if res.status_code == 200:
                    response = res.json()
                    answer = response.get("answer", "No answer returned.")
                    sources = response.get("chunks", [])
                else:
                    answer = f"❌ Error from backend: {res.status_code}"
                    sources = []
            except Exception as e:
                answer = f"❌ Request failed: {e}"
                sources = []

            st.session_state.chat_history.append((user_input, answer, sources))



    for q, a, s in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 TenderIQ:** {a}")
        st.markdown("**📄 Sources:**")
        for src in s:
            st.markdown(f"- {src}")
>>>>>>> project-a-branch
        st.markdown("---")

# ---------------------- Tab 3: Task Extraction -------------------------
with tab3:
    st.header("📋 Extracted Tasks")

    if st.button("🔍 Extract Tasks"):
<<<<<<< HEAD
        try:
            with st.spinner("Extracting tasks from document..."):
                headers = {"Content-Type": "application/json"}
                payload = {
                    "project": selected_project,
                    "model": selected_model
                }

                response = requests.post(f"{API_BASE}/tasks/", json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.tasks = data.get("tasks", [])
                    st.session_state.task_timings = data.get("timings", {})
                    
                    if not st.session_state.tasks:
                        st.warning("✅ Extraction completed but returned no tasks.")
                else:
                    st.error(f"❌ Task extraction failed: {response.status_code}")
                    st.text(response.text)

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Display timing and tasks if available
    if "tasks" in st.session_state and st.session_state.tasks:
        timings = st.session_state.get("task_timings", {})

        if timings:
            with st.expander("🕒 Task Extraction Breakdown"):
                st.markdown(f"- 🔍 **Retrieval**: `{timings.get('retrieval', 'N/A')}s`")
                st.markdown(f"- ✍️ **LLM Inference**: `{timings.get('llm', 'N/A')}s`")
                st.markdown(f"- ⏱️ **Total Time**: `{timings.get('total', 'N/A')}s`")

        for i, task in enumerate(st.session_state.tasks):
            st.markdown(f"### 📝 Task {i+1}")
            st.markdown(f"- 📄 **Description**: {task.get('task', 'N/A')}")
            st.markdown(f"- 📅 **Deadline**: {task.get('deadline', 'TBD')}")
            st.markdown(f"- ✅ **Status**: {task.get('status', 'Pending')}")
            st.markdown("---")
    else:
        st.info("No tasks extracted yet.")
=======
        # Simulate backend call (replace with actual function)
        tasks = [
            {"task": "Submit company profile", "deadline": "July 10", "status": "Pending"},
            {"task": "Attach ISO Certificate", "deadline": "July 12", "status": "Pending"},
        ]
        st.session_state.tasks = tasks

    if "tasks" in st.session_state:
        for i, task in enumerate(st.session_state.tasks):
            st.markdown(f"**Task {i+1}**")
            st.markdown(f"- 📄 **Description**: {task['task']}")
            st.markdown(f"- 📅 **Deadline**: {task['deadline']}")
            st.markdown(f"- ✅ **Status**: {task['status']}")
            st.markdown("---")

# ---------------------- FastAPI Backend (for uvicorn) -------------------------
try:
    from fastapi import FastAPI
    from src.api.routes import router as api_router

    app = FastAPI()
    app.include_router(api_router)
    print("✅ FastAPI initialized successfully")

except Exception as e:
    print("❌ FastAPI failed to load:", e)
    app = None

>>>>>>> project-a-branch
