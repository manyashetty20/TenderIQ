import streamlit as st
import datetime
import pandas as pd
import json

# -------------------- Data Mock (Replace with DB in real version) --------------------
PROJECTS = [
    {"name": "Network Upgrade", "status": "Active", "last_updated": "2025-06-10", "created": "2025-06-03", "description": "Network infrastructure upgrade tender."},
    {"name": "Data Center", "status": "Completed", "last_updated": "2025-05-27", "created": "2025-05-01", "description": "New data center construction."},
    {"name": "Cloud Services", "status": "Active", "last_updated": "2025-06-12", "created": "2025-06-01", "description": "Tender for cloud infra and deployment."}
]

TASKS = [
    {"task": "Submit company profile", "deadline": "2025-06-30", "priority": "High", "status": "Pending", "source": "Page 5, Section 3.2"},
    {"task": "Register", "deadline": "2025-06-20", "priority": "Medium", "status": "Done", "source": "Page 2"},
    {"task": "Sign NDA", "deadline": "2025-06-25", "priority": "Low", "status": "Pending", "source": "Page 6"},
]

# -------------------- Layout: Tabs --------------------
st.set_page_config(page_title="TenderIQ", layout="wide")
st.title("📂 TenderIQ – Tender Intelligence System")

tabs = st.tabs(["📁 Projects", "📤 Upload", "💬 Chat", "✅ Tasks"])

# -------------------- Tab 1: Projects --------------------
with tabs[0]:
    st.subheader("Project Management")

    st.markdown("### Your Projects")
    df = pd.DataFrame(PROJECTS)
    st.dataframe(df[["name", "status", "last_updated"]].rename(columns={
        "name": "Name", "status": "Status", "last_updated": "Last Updated"
    }), use_container_width=True)

    st.markdown("### Project Detail View")
    selected_project = st.selectbox("Select Project", [p["name"] for p in PROJECTS])
    project_data = next((p for p in PROJECTS if p["name"] == selected_project), None)

    if project_data:
        st.write(f"**Project:** {project_data['name']}")
        st.write(f"**Status:** {project_data['status']} | **Created:** {project_data['created']}")
        st.write(f"**Description:** {project_data['description']}")

# -------------------- Tab 2: Upload --------------------
with tabs[1]:
    st.subheader("Upload Tender Document")

    selected_project_upload = st.selectbox("Upload to Project", [p["name"] for p in PROJECTS])
    doc_type = st.selectbox("Document Type", ["Main Document", "Amendment", "Clarification"])
    version = st.selectbox("Version", [1, 2, 3])

    uploaded_file = st.file_uploader("Drop or select file", type=["pdf", "docx"])
    if uploaded_file and st.button("📤 Upload Document"):
        st.success(f"Uploaded {uploaded_file.name} to {selected_project_upload}")
        # Normally: send to backend for processing

# -------------------- Tab 3: Chat --------------------
with tabs[2]:
    st.subheader("Ask a Question")

    doc_selected = st.selectbox("Select Document", ["RFP-2025-01.pdf"])
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Your question", placeholder="e.g. What is the submission deadline?")
    if st.button("Ask Question"):
        if user_input:
            # Simulated response
            answer = "The submission deadline for this RFP is July 15, 2025 at 5:00 PM EST."
            sources = [
                "Page 3, Section 2.1: 'All responses must be submitted by 5:00 PM EST on July 15, 2025.'",
                "Page 12, Section 6.4: 'The deadline will not be extended.'"
            ]
            st.session_state.chat_history.append((user_input, answer, sources))

    for q, a, s in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 TenderIQ:** {a}")
        with st.expander("📄 Sources"):
            for src in s:
                st.markdown(f"- {src}")
        st.markdown("---")

# -------------------- Tab 4: Tasks --------------------
with tabs[3]:
    st.subheader("Tasks Extracted from Document")

    # Filter + Sort
    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Done"])
    priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

    filtered_tasks = TASKS
    if status_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status_filter]
    if priority_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority_filter]

    # Show tasks
    for t in filtered_tasks:
        st.markdown(f"""
        **🔖 Task:** {t['task']}  
        ⏰ **Deadline:** {t['deadline']}  
        ⚡ **Priority:** {t['priority']}  
        ✅ **Status:** {t['status']}  
        📄 **Source:** {t['source']}  
        ---""")

    # Export to CSV
    if st.button("📤 Export Tasks to CSV"):
        df_tasks = pd.DataFrame(filtered_tasks)
        st.download_button("Download CSV", df_tasks.to_csv(index=False), "tasks.csv", "text/csv")

    # Manual task entry (optional)
    with st.expander("➕ Add Manual Task"):
        manual_task = st.text_input("Task")
        manual_deadline = st.date_input("Deadline", datetime.date(2025, 6, 30))
        manual_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        if st.button("Add Task"):
            TASKS.append({
                "task": manual_task,
                "deadline": manual_deadline.strftime("%Y-%m-%d"),
                "priority": manual_priority,
                "status": "Pending",
                "source": "Manual Entry"
            })
            st.success("Task added.")

