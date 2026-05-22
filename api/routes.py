from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os
from core.loader import load_and_split
from core.embedder import store_chunks
from core.retriever import answer_question

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory registry of loaded collections
loaded_collections: dict[str, str] = {}

class QuestionRequest(BaseModel):
    question: str
    collection: str = "documind"
    chat_history: list[dict] = []

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    collection: str

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    collection_name = (
        file.filename
        .replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )

    chunks = load_and_split(save_path)
    store_chunks(chunks, collection_name=collection_name)

    loaded_collections[collection_name] = file.filename

    return {
        "message": f"Successfully ingested '{file.filename}'",
        "chunks_created": len(chunks),
        "collection": collection_name,
        "filename": file.filename
    }

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer, sources = answer_question(
        question=request.question,
        collection_name=request.collection,
        chat_history=request.chat_history
    )

    return AnswerResponse(
        answer=answer,
        sources=sources,
        collection=request.collection
    )

@router.get("/collections")
async def list_collections():
    return {
        "collections": [
            {"collection": k, "filename": v}
            for k, v in loaded_collections.items()
        ]
    }

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "DocuMind API"}