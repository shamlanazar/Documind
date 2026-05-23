import streamlit as st
import os
from dotenv import load_dotenv
from core.loader import load_and_split
from core.embedder import store_chunks
from core.retriever import answer_question
import tempfile

load_dotenv()

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
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                collection_name = (
                    uploaded_file.name
                    .replace(".pdf", "")
                    .replace(" ", "_")
                    .lower()
                )

                chunks = load_and_split(tmp_path)
                store_chunks(chunks, collection_name=collection_name)
                os.unlink(tmp_path)

                st.session_state.uploaded_docs[uploaded_file.name] = collection_name
                st.session_state.active_collection = collection_name
                st.session_state.messages = []
                st.success(f"Ready — {len(chunks)} chunks indexed")

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

    st.divider()
    st.markdown(
        "Built with LangChain · ChromaDB · Groq · Streamlit",
        help="RAG pipeline with semantic search and source grounding"
    )

if not st.session_state.active_collection:
    st.info("⬅ Upload a PDF in the sidebar to get started.")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📥 Upload**")
        st.caption("Upload any PDF document — textbooks, reports, contracts, research papers")
    with col2:
        st.markdown("**🔍 Ask**")
        st.caption("Ask natural language questions about your document's content")
    with col3:
        st.markdown("**📌 Cited answers**")
        st.caption("Every answer comes with exact source page references")
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

                answer, sources = answer_question(
                    question=question,
                    collection_name=st.session_state.active_collection,
                    chat_history=history_to_send
                )

                st.markdown(answer)
                if sources:
                    st.caption(f"Sources: {', '.join(sources)}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })