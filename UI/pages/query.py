import streamlit as st

st.subheader("💬 Ask a Question")

doc_selected = st.selectbox("Select Document", ["RFP-2025-01.pdf"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Your question", placeholder="e.g. What is the submission deadline?")
if st.button("Ask Question"):
    if user_input:
        answer = "The submission deadline for this RFP is July 15, 2025 at 5:00 PM EST."
        sources = [
            "Page 3, Section 2.1: 'All responses must be submitted by 5:00 PM EST on July 15, 2025.'",
            "Page 12, Section 6.4: 'The deadline will not be extended.'"
        ]
        st.session_state.chat_history.append((user_input, answer, sources))

# Render chat history
for q, a, s in reversed(st.session_state.chat_history):
    st.markdown(f"**🧑 You:** {q}")
    st.markdown(f"**🤖 TenderIQ:** {a}")
    with st.expander("📄 Sources"):
        for src in s:
            st.markdown(f"- {src}")
    st.markdown("---")
