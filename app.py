import streamlit as st
import requests
import os
import json

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="TenderIQ", layout="wide")

# ---------------------- Sidebar: Project Selection -------------------------
st.sidebar.title("TenderIQ")
st.sidebar.subheader("Project Management")

# Dummy list of projects (replace with backend API call)
project_names = ["Metro Rail Expansion", "Hospital Equipment Supply"]
selected_project = st.sidebar.selectbox("Select Tender Project", project_names)
st.sidebar.markdown(f"**Selected:** `{selected_project}`")

# ---------------------- Main Tabs -------------------------
tab1, tab2, tab3 = st.tabs(["📁 Upload", "💬 Chat", "📋 Tasks"])

# ---------------------- Tab 1: Upload -------------------------
with tab1:
    st.header("📁 Upload Tender Document")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
    
    doc_type = st.selectbox("Document Type", ["Main", "Amendment", "Clarification", "Q&A"])
    version = st.text_input("Version (e.g., 1 or 2)", "1")

    if uploaded_file and st.button("Upload Document"):
        with st.spinner("Processing document..."):
            # Simulate backend call (replace with requests.post or function call)
            file_path = f"./data/uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            st.success("Document uploaded and processed!")

# ---------------------- Tab 2: Chat Interface -------------------------
with tab2:
    st.header("💬 Ask Questions")
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
        st.markdown("---")

# ---------------------- Tab 3: Task Extraction -------------------------
with tab3:
    st.header("📋 Extracted Tasks")

    if st.button("🔍 Extract Tasks"):
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

