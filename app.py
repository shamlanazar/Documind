import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="DocuMind",
    page_icon="📄",
    layout="wide"
)

st.title("📄 DocuMind")
st.caption("Intelligent document Q&A with source grounding")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_collection" not in st.session_state:
    st.session_state.active_collection = None

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}

with st.sidebar:
    st.header("Documents")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload one or more PDFs"
    )

    if uploaded_file:
        if uploaded_file.name not in st.session_state.uploaded_docs:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                response = requests.post(
                    f"{API_BASE}/upload",
                    files={"file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/pdf"
                    )}
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.uploaded_docs[uploaded_file.name] = (
                        data["collection"]
                    )
                    st.session_state.active_collection = data["collection"]
                    st.session_state.messages = []
                    st.success(f"Ready — {data['chunks_created']} chunks indexed")
                else:
                    st.error("Upload failed. Is the API server running?")

    if st.session_state.uploaded_docs:
        st.divider()
        st.markdown("**Switch document**")
        selected = st.radio(
            "Active document",
            options=list(st.session_state.uploaded_docs.keys()),
            label_visibility="collapsed"
        )
        new_collection = st.session_state.uploaded_docs[selected]
        if new_collection != st.session_state.active_collection:
            st.session_state.active_collection = new_collection
            st.session_state.messages = []
            st.rerun()

    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.active_collection:
    st.info("Upload a PDF in the sidebar to get started.")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(f"Sources: {', '.join(message['sources'])}")

    if question := st.chat_input("Ask anything about your document..."):
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching document..."):
                history_to_send = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

                response = requests.post(
                    f"{API_BASE}/ask",
                    json={
                        "question": question,
                        "collection": st.session_state.active_collection,
                        "chat_history": history_to_send
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    st.markdown(data["answer"])
                    if data["sources"]:
                        st.caption(f"Sources: {', '.join(data['sources'])}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data["sources"]
                    })
                else:
                    st.error("Something went wrong. Try again.")