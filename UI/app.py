import streamlit as st
import pandas as pd
import requests

# Sample data
PROJECTS = [
    {
        "name": "Network Upgrade",
        "status": "Active",
        "last_updated": "2025-06-10",
        "created": "2025-06-03",
        "description": "Network infrastructure upgrade tender."
    },
    {
        "name": "Data Center",
        "status": "Completed",
        "last_updated": "2025-05-27",
        "created": "2025-05-01",
        "description": "New data center construction."
    },
    {
        "name": "Cloud Services",
        "status": "Active",
        "last_updated": "2025-06-12",
        "created": "2025-06-01",
        "description": "Tender for cloud infra and deployment."
    }
]

# Streamlit page config
st.set_page_config(page_title="TenderIQ", layout="wide")
st.title("📂 TenderIQ – Tender Intelligence System")

st.markdown("Use the left sidebar to navigate: [📁 Projects], [📤 Upload], [💬 Chat], or [✅ Tasks].")

# ----------------------------------
# Existing Projects Table + Details
# ----------------------------------
st.markdown("### Your Projects")
df = pd.DataFrame(PROJECTS)
st.dataframe(
    df[["name", "status", "last_updated"]].rename(columns={
        "name": "Name", "status": "Status", "last_updated": "Last Updated"
    }),
    use_container_width=True
)

st.markdown("### Project Detail View")
selected_project = st.selectbox("Select Project", [p["name"] for p in PROJECTS])
project_data = next((p for p in PROJECTS if p["name"] == selected_project), None)

if project_data:
    st.write(f"**Project:** {project_data['name']}")
    st.write(f"**Status:** {project_data['status']} | **Created:** {project_data['created']}")
    st.write(f"**Description:** {project_data['description']}")

# ----------------------------------
# Task Viewer Section (Backend Integration)
# ----------------------------------
API_BASE = "http://localhost:8000"  # FastAPI backend URL

st.markdown("### 📋 View Extracted Tasks for This Project")
if selected_project:
    with st.spinner("Fetching tasks..."):
        try:
            project_encoded = selected_project.replace(" ", "%20")
            res = requests.get(f"{API_BASE}/tasks/{project_encoded}")
            if res.status_code == 200:
                tasks = res.json().get("tasks", [])
                if tasks:
                    task_df = pd.DataFrame(tasks)
                    st.dataframe(task_df)
                else:
                    st.info("No tasks extracted yet for this project.")
            else:
                st.error("Failed to fetch tasks from backend.")
        except Exception as e:
            st.error(f"Error: {e}")
