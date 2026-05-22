import sys
from core.loader import load_and_split
from core.embedder import store_chunks
from core.retriever import answer_question

def ingest(pdf_path: str):
    print(f"\nIngesting: {pdf_path}")
    chunks = load_and_split(pdf_path)
    store_chunks(chunks)
    print("Ingestion complete.\n")

def ask(question: str):
    print(f"\nQuestion: {question}")
    answer, sources = answer_question(question)
    print(f"\nAnswer:\n{answer}")
    print(f"\nSources: {', '.join(sources)}\n")

if __name__ == "__main__":
    if sys.argv[1] == "ingest":
        ingest(sys.argv[2])
    elif sys.argv[1] == "ask":
        ask(" ".join(sys.argv[2:]))