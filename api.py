from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ingestion import ingest_pdf, rebuild_index_from_folder
from rag_graph import generate_rag_answer
from vector_store import clear_vector_store


app = FastAPI(
    title="SmartDoc AI API",
    description="Backend API for SmartDoc AI",
    version="1.0.0",
)

DOCUMENTS_FOLDER = Path("Documents")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

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
    return {"message": "Welcome to SmartDoc AI API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/documents")
def get_documents():
    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)
    files = [file.name for file in DOCUMENTS_FOLDER.glob("*.pdf")]
    return {"total_documents": len(files), "documents": files}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    filename = Path(file.filename).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)
    file_path = DOCUMENTS_FOLDER / filename

    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="A document with this filename already exists.",
        )

    try:
        contents = await file.read(MAX_FILE_SIZE + 1)

        if not contents:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds the 25 MB limit.")
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

        file_path.write_bytes(contents)

        # Incremental ingestion: process and embed this PDF only.
        result = ingest_pdf(file_path)

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": filename,
            "total_documents": len(list(DOCUMENTS_FOLDER.glob("*.pdf"))),
            "total_pages": result["total_pages"],
            "total_chunks": result["total_chunks"],
            "total_vectors": result["total_vectors"],
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as error:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {error}")
    finally:
        await file.close()


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    if (
        filename != Path(filename).name
        or "/" in filename
        or "\\" in filename
        or not filename.lower().endswith(".pdf")
    ):
        raise HTTPException(status_code=400, detail="Invalid PDF filename.")

    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)
    file_path = DOCUMENTS_FOLDER / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    backup_path = DOCUMENTS_FOLDER / f".{filename}.deleting"

    try:
        file_path.replace(backup_path)

        # Deletion rebuilds the index from remaining PDFs.
        # Normal uploads do NOT take this path.
        result = rebuild_index_from_folder(DOCUMENTS_FOLDER)

        backup_path.unlink(missing_ok=True)

        return {
            "message": "Document deleted successfully.",
            "filename": filename,
            "total_documents": len(list(DOCUMENTS_FOLDER.glob("*.pdf"))),
            "total_chunks": result["total_chunks"],
        }

    except Exception as error:
        # Restore the PDF and attempt to restore a matching vector index.
        if backup_path.exists():
            backup_path.replace(file_path)
            try:
                rebuild_index_from_folder(DOCUMENTS_FOLDER)
            except Exception as restore_error:
                print("WARNING: Vector index restoration failed:", restore_error)

        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {error}",
        )


@app.post("/ask")
def ask_question(request: QuestionRequest):
    index_path = Path("vector_store/index.faiss")
    metadata_path = Path("vector_store/index.pkl")

    if not index_path.exists() or not metadata_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Vector store not found. Please upload a PDF first.",
        )

    try:
        result = generate_rag_answer(
            question=request.question,
            top_k=request.top_k,
        )
        return {"answer": result["answer"], "sources": result["sources"]}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
