import streamlit as st
import requests
import os
import json

API_BASE = "http://localhost:8000"
st.set_page_config(page_title="TenderIQ", layout="wide")

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

st.sidebar.subheader("Model Selection")
model_choice = st.sidebar.radio("Choose a model", ["LLaMA", "Groq"])
selected_model = model_choice.lower()

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
selected_project = st.sidebar.selectbox("Select Tender Project", project_names)
st.sidebar.markdown(f"**Selected:** `{selected_project}`")

# ---------------------- Main Tabs -------------------------
tab1, tab2, tab3 = st.tabs(["📁 Upload", "💬 Chat", "📋 Tasks"])

# ---------------------- Tab 1: Upload -------------------------
with tab1:
    st.header("📁 Upload Tender Document")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
    doc_type = st.selectbox("Document Type", ["Main", "Amendment"])
    version = st.text_input("Version (e.g., 1 or 2)", "1")

    if uploaded_file and st.button("Upload Document"):
        with st.spinner("Uploading to backend..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                data = {"project": selected_project, "doc_type": doc_type, "version": version}
                response = requests.post(f"{API_BASE}/upload/", files=files, data=data)
                if response.status_code == 200:
                    st.success("✅ Document uploaded and processed successfully.")
                    st.json(response.json())
                else:
                    st.error(f"❌ Upload failed with status code {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

# ---------------------- Tab 2: Chat Interface -------------------------
with tab2:
    st.header("💬 Ask Questions")
    st.markdown("Ask anything about the selected tender document.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your question")
    if st.button("Ask"):
        if user_input:
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
                    st.session_state.chat_history.append((user_input, f"❌ Request failed: {e}", [], {}))

            if res and res.status_code == 200:
                response = res.json()
                answer = response.get("answer", "No answer returned.")
                sources = response.get("chunks", [])
                timings = response.get("timings", {})
                st.session_state.chat_history.append((user_input, answer, sources, timings))
            elif res:
                st.session_state.chat_history.append((user_input, f"❌ Error: {res.status_code}", [], {}))

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
        st.markdown("---")

# ---------------------- Tab 3: Task Extraction -------------------------
with tab3:
    st.header("📋 Extracted Tasks")

    completed_key = f"{selected_project}_completed_tasks"
    if completed_key not in st.session_state:
        st.session_state[completed_key] = []

    if st.button("🔍 Extract Tasks"):
        try:
            with st.spinner("Extracting tasks from document..."):
                headers = {"Content-Type": "application/json"}
                payload = {"project": selected_project, "model": selected_model}
                response = requests.post(f"{API_BASE}/tasks/", json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.tasks = data.get("tasks", [])
                    st.session_state.task_timings = data.get("timings", {})
                    st.session_state[completed_key] = []
                else:
                    st.error(f"❌ Task extraction failed: {response.status_code}")
                    st.text(response.text)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    timings = st.session_state.get("task_timings", {})
    if timings:
        with st.expander("🕒 Task Extraction Breakdown"):
            st.markdown(f"- 🔍 **Retrieval**: `{timings.get('retrieval', 'N/A')}s`")
            st.markdown(f"- ✍️ **LLM Inference**: `{timings.get('llm', 'N/A')}s`")
            st.markdown(f"- ⏱️ **Total Time**: `{timings.get('total', 'N/A')}s`")

    tasks = st.session_state.get("tasks", [])
    completed = st.session_state[completed_key]
    pending = [t for t in tasks if t not in completed]
    done = [t for t in tasks if t in completed]

    # -------- Pending Task Cards --------
    with st.expander("📌 Pending Tasks", expanded=True):
        if not pending:
            st.success("✅ No pending tasks!")
        for i, task in enumerate(pending, 1):
            task_id = f"{selected_project}_task_{i}"
            with st.container():
                st.markdown(f"### 📝 Task {i}")
                st.markdown(f"**📄 Description:** {task.get('task', 'N/A')}")
                st.markdown(f"**📅 Deadline:** {task.get('deadline', 'TBD')}")
                st.markdown(f"**✅ Status:** Pending")
                with st.form(key=f"form_{task_id}"):
                    submitted = st.form_submit_button("✅ Mark as Done")
                    if submitted:
                        if task not in st.session_state[completed_key]:
                            st.session_state[completed_key].append(task)
                            st.rerun()

    # -------- Completed Task Cards --------
    with st.expander("✅ Completed Tasks", expanded=False):
        if not done:
            st.info("No tasks completed yet.")
        for i, task in enumerate(done, 1):
            task_id = f"{selected_project}_completed_{i}"
            with st.container():
                st.markdown(f"### ✅ Task {i}")
                st.markdown(f"**📄 Description:** {task.get('task', 'N/A')}")
                st.markdown(f"**📅 Deadline:** {task.get('deadline', 'TBD')}")
                st.markdown(f"**✅ Status:** Completed")

                with st.form(key=f"form_completed_{task_id}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.checkbox("Completed", value=True, disabled=True, key=f"{task_id}_readonly")
                    with col2:
                        unmark = st.form_submit_button("🔄 Mark as Pending")
                        if unmark:
                            if task in st.session_state[completed_key]:
                                st.session_state[completed_key].remove(task)
                                st.rerun()
