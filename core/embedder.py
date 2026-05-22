# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

def get_embedding_function():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def store_chunks(chunks, collection_name: str = "documind"):
    embedding_fn = get_embedding_function()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_fn,
        persist_directory=CHROMA_PATH,
        collection_name=collection_name
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB collection: '{collection_name}'")
    return vectorstore

def load_vectorstore(collection_name: str = "documind"):
    embedding_fn = get_embedding_function()

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_fn,
        collection_name=collection_name
    )

    return vectorstore