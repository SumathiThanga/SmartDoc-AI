
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

from retriever import search_documents
from answer_generator import generate_answer

app = FastAPI(
    title="SmartDoc AI API",
    description="Backend API for SmartDoc AI",
    version="1.0.0"
)

# Allow the React development server to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.31.129:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


@app.get("/")
def home():
    return {
        "message": "Welcome to SmartDoc AI API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/documents")
def get_documents():
    documents_folder = Path("Documents")

    documents_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    files = [
        file.name
        for file in documents_folder.glob("*.pdf")
    ]

    return {
        "total_documents": len(files),
        "documents": files
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    index_path = Path("vector_store/faiss.index")

    chunks_path = Path("vector_store/chunks.json")

    if not index_path.exists() or not chunks_path.exists():
        raise HTTPException(
            status_code=400,
            detail="Vector database not found. Please index your PDFs first."
        )

    try:
        # Step 1: Retrieve relevant document chunks
        retrieved_chunks = search_documents(
            question,
            top_k=request.top_k
        )

        if not retrieved_chunks:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }

        # Step 2: Generate GPT answer
        answer = generate_answer(
            question,
            retrieved_chunks
        )

        # Step 3: Return answer and references
        sources = [
            {
                "document_name": item["document_name"],
                "page_number": item["page_number"],
                "chunk_id": item["chunk_id"],
                "similarity_score": item["similarity_score"],
                "text": item["text"]
            }
            for item in retrieved_chunks
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Question processing failed: {str(error)}"
        )
