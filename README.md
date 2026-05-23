# 📄 DocuMind — Intelligent Document Q&A

> Ask natural language questions across your PDF documents.
> Get precise answers grounded in exact source pages — no hallucination.

🔗 **Live demo:** [documindassistant.streamlit.app](https://documindassistant.streamlit.app)

---

## What it Does

Upload any PDF — a research paper, contract, textbook, or report.  
Ask questions in plain English. DocuMind retrieves the most relevant sections semantically and generates a grounded answer with page citations.  

## Architecture
PDF Upload  
↓  
Text Chunking (RecursiveCharacterTextSplitter, 500 chars, 50 overlap)  
↓  
Sentence Embeddings (all-MiniLM-L6-v2, runs locally)  
↓  
ChromaDB Vector Store (persistent, per-document collections)  
↓  
Semantic Retrieval (top-4 chunks by cosine similarity)  
↓  
Groq LLaMA 3.1 (grounded generation with citation enforcement)  
↓  
Cited Answer + Source Pages  

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq API (LLaMA 3.1 8B) |
| Framework | LangChain |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Language | Python 3.11 |

## Key Features

- Multi-document support with per-document collections  
- Conversation memory — follow-up questions work naturally  
- Source page citations on every answer  
- REST API with Swagger docs at `/docs`  
- Runs fully locally or deploys to Streamlit Cloud  

## Run Locally

```bash
git clone https://github.com/shamlanazar/documind
cd documind
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Terminal 1 — API server
python server.py

# Terminal 2 — UI
streamlit run app.py
```

## What I learned building this

- How RAG pipelines work end-to-end — chunking strategy matters more than model choice  
- Why chunk overlap prevents answer truncation at boundaries  
- How to enforce source grounding via prompt design rather than post-processing  
- How conversation memory integrates with retrieval chains  