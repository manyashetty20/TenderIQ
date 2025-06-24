import streamlit as st
import datetime
import pandas as pd

# Simulated tasks list
TASKS = [
    {"task": "Submit company profile", "deadline": "2025-06-30", "priority": "High", "status": "Pending", "source": "Page 5, Section 3.2"},
    {"task": "Register", "deadline": "2025-06-20", "priority": "Medium", "status": "Done", "source": "Page 2"},
    {"task": "Sign NDA", "deadline": "2025-06-25", "priority": "Low", "status": "Pending", "source": "Page 6"},
]

st.subheader("✅ Tasks Extracted from Document")

status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Done"])
priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

filtered_tasks = TASKS
if status_filter != "All":
    filtered_tasks = [t for t in filtered_tasks if t["status"] == status_filter]
if priority_filter != "All":
    filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority_filter]

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

# Add manual task
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
