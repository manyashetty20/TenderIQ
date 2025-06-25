import streamlit as st
import requests
import os
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="TenderIQ", layout="wide")

# ---------------------- New: Dynamic Projects -------------------------
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

# ---------------------- Sidebar: Project Selection -------------------------
st.sidebar.title("TenderIQ")
st.sidebar.subheader("Project Management")

# Handle project input toggle
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
selected_project = st.sidebar.selectbox("Select Tender Project", project_names)
st.sidebar.markdown(f"**Selected:** `{selected_project}`")

# ---------------------- Main Tabs -------------------------
tab1, tab2, tab3 = st.tabs(["\U0001F4C1 Upload", "\U0001F4AC Chat", "\U0001F4CB Tasks"])

# ---------------------- Tab 1: Upload -------------------------
with tab1:
    st.header("\U0001F4C1 Upload Tender Document")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

    doc_type = st.selectbox("Document Type", ["Main", "Amendment", "Clarification", "Q&A"])
    version = st.text_input("Version (e.g., 1 or 2)", "1")

    if uploaded_file and st.button("Upload Document"):
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
                    st.success("\u2705 Document uploaded and processed successfully.")
                    st.json(response.json())
                else:
                    st.error(f"\u274C Upload failed with status code {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"\u274C Upload failed: {e}")

# ---------------------- Tab 2: Chat Interface -------------------------
with tab2:
    st.header("\U0001F4AC Ask Questions")
    st.markdown("Ask anything about the selected tender document.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your question")

    if st.button("Ask"):
        if user_input:
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
                    answer = f"\u274C Error from backend: {res.status_code}"
                    sources = []
            except Exception as e:
                answer = f"\u274C Request failed: {e}"
                sources = []

            st.session_state.chat_history.append((user_input, answer, sources))

    
    for q, a, s in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 TenderIQ:** {a}")

        if s:
            # one expander per chunk
            for i, chunk in enumerate(s, 1):
                preview = chunk[:120].replace("\n", " ") + ("…" if len(chunk) > 120 else "")
                with st.expander(f"📄 Source {i}: {preview}"):
                    st.markdown(chunk)
        else:
            st.markdown("_No relevant sources found._")

        st.markdown("---")


# ---------------------- Tab 3: Task Extraction -------------------------
with tab3:
    st.header("\U0001F4CB Extracted Tasks")

    if st.button("\U0001F50D Extract Tasks"):
        tasks = [
            {"task": "Submit company profile", "deadline": "July 10", "status": "Pending"},
            {"task": "Attach ISO Certificate", "deadline": "July 12", "status": "Pending"},
        ]
        st.session_state.tasks = tasks

    if "tasks" in st.session_state:
        for i, task in enumerate(st.session_state.tasks):
            st.markdown(f"**Task {i+1}**")
            st.markdown(f"- \U0001F4C4 **Description**: {task['task']}")
            st.markdown(f"- \U0001F4C5 **Deadline**: {task['deadline']}")
            st.markdown(f"- \u2705 **Status**: {task['status']}")
            st.markdown("---")

# ---------------------- FastAPI Backend (for uvicorn) -------------------------
try:
    from fastapi import FastAPI
    from src.api.routes import router as api_router

    app = FastAPI()
    app.include_router(api_router)
    print("\u2705 FastAPI initialized successfully")

except Exception as e:
    print("\u274C FastAPI failed to load:", e)
    app = None
