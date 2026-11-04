
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

from retriever import search_documents
from answer_generator import generate_answer

# Existing document-processing modules
from pdf_processor import extract_all_pdfs, create_chunks
from embedding_generator import generate_embeddings
from vector_store import create_vector_store


app = FastAPI(
    title="SmartDoc AI API",
    description="Backend API for SmartDoc AI",
    version="1.0.0"
)

# Configuration
DOCUMENTS_FOLDER = Path("Documents")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

# Allow React frontend to communicate with FastAPI
# Allow React frontend to communicate with FastAPI
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
    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

    files = [
        file.name
        for file in DOCUMENTS_FOLDER.glob("*.pdf")
    ]

    return {
        "total_documents": len(files),
        "documents": files
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    filename = Path(file.filename).name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

    file_path = DOCUMENTS_FOLDER / filename

    # Prevent accidental overwriting
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="A document with this filename already exists."
        )

    try:
        # Read uploaded file
        contents = await file.read(MAX_FILE_SIZE + 1)

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 25 MB limit."
            )

        # Check PDF file signature
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid PDF."
            )

        # Save PDF
        file_path.write_bytes(contents)

        # Step 1: Extract text from all PDFs
        pages = extract_all_pdfs(DOCUMENTS_FOLDER)

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No extractable PDF text found."
            )

        # Step 2: Create text chunks
        chunks = create_chunks(pages)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks could be created."
            )

        # Step 3: Generate embeddings
        embeddings = generate_embeddings(chunks)

        if not embeddings:
            raise HTTPException(
                status_code=500,
                detail="Embedding generation returned no results."
            )

        # Step 4: Rebuild FAISS index using all PDFs
        create_vector_store(chunks, embeddings)

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": filename,
            "total_documents": len(list(DOCUMENTS_FOLDER.glob("*.pdf"))),
            "total_pages": len(pages),
            "total_chunks": len(chunks)
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise

    except Exception as error:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )

    finally:
        await file.close()


@app.delete("/documents/{filename}")
def delete_document(filename: str):

    # Validate filename to prevent deleting files outside Documents
    if (
        filename != Path(filename).name
        or "/" in filename
        or "\\" in filename
        or not filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename."
        )

    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

    file_path = DOCUMENTS_FOLDER / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Temporarily move the PDF out of the folder.
    # extract_all_pdfs() will therefore skip this document.
    backup_path = DOCUMENTS_FOLDER / f".{filename}.deleting"

    try:
        file_path.replace(backup_path)

        remaining_files = list(DOCUMENTS_FOLDER.glob("*.pdf"))

        index_path = Path("vector_store/faiss.index")
        chunks_path = Path("vector_store/chunks.json")

        if remaining_files:

            # Rebuild index using the remaining PDFs
            pages = extract_all_pdfs(DOCUMENTS_FOLDER)

            if not pages:
                raise RuntimeError(
                    "No extractable text found in remaining PDFs."
                )

            chunks = create_chunks(pages)

            if not chunks:
                raise RuntimeError(
                    "No chunks could be created from remaining PDFs."
                )

            embeddings = generate_embeddings(chunks)

            if embeddings is None or len(embeddings) == 0:
                raise RuntimeError(
                    "Embedding generation failed."
                )

            create_vector_store(chunks, embeddings)

        else:
            # No documents remain: remove the old index
            index_path.unlink(missing_ok=True)
            chunks_path.unlink(missing_ok=True)

        # Delete the temporary backup after successful reindexing
        backup_path.unlink(missing_ok=True)

        return {
            "message": "Document deleted successfully.",
            "filename": filename,
            "total_documents": len(
                list(DOCUMENTS_FOLDER.glob("*.pdf"))
            )
        }

    except Exception as error:

        # Restore the PDF if deletion/reindexing fails
        if backup_path.exists():
            backup_path.replace(file_path)

            # Try to restore the vector index too
            try:
                restored_pages = extract_all_pdfs(DOCUMENTS_FOLDER)

                if restored_pages:
                    restored_chunks = create_chunks(restored_pages)
                    restored_embeddings = generate_embeddings(restored_chunks)

                    if restored_chunks and restored_embeddings is not None:
                        create_vector_store(
                            restored_chunks,
                            restored_embeddings
                        )

            except Exception as restore_error:
                print(
                    "WARNING: Vector index restoration failed:",
                    restore_error
                )

        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {str(error)}"
        )


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
        retrieved_chunks = search_documents(
            question,
            top_k=request.top_k
        )

        if not retrieved_chunks:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }

        answer = generate_answer(
            question,
            retrieved_chunks
        )

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
