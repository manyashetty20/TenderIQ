import streamlit as st

# Simulated project list
PROJECTS = ["Network Upgrade", "Data Center", "Cloud Services"]

st.subheader("📤 Upload Tender Document")

selected_project_upload = st.selectbox("Upload to Project", PROJECTS)
doc_type = st.selectbox("Document Type", ["Main Document", "Amendment", "Clarification"])
version = st.selectbox("Version", [1, 2, 3])

uploaded_file = st.file_uploader("Drop or select file", type=["pdf", "docx"])
if uploaded_file and st.button("📤 Upload Document"):
    st.success(f"Uploaded {uploaded_file.name} to {selected_project_upload}")
