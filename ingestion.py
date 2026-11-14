from pathlib import Path

from pdf_processor import extract_pdf, extract_all_pdfs, create_chunks
from vector_store import add_chunks_to_vector_store, rebuild_vector_store


DOCUMENTS_FOLDER = Path("Documents")


def ingest_pdf(pdf_path):
    """
    Workflow 1: process one newly uploaded PDF only.
    Existing PDFs are not extracted, chunked, or embedded again.
    """
    pages = extract_pdf(pdf_path)
    if not pages:
        raise ValueError("No extractable text found in the uploaded PDF.")

    chunks = create_chunks(pages)
    if not chunks:
        raise ValueError("No text chunks could be created from the uploaded PDF.")

    vector_store = add_chunks_to_vector_store(chunks)

    return {
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "total_vectors": vector_store.index.ntotal,
    }


def rebuild_index_from_folder(folder=DOCUMENTS_FOLDER):
    """
    Rebuild all remaining PDFs. Used after deletion or index recovery,
    not during normal uploads.
    """
    pages = extract_all_pdfs(folder)
    chunks = create_chunks(pages) if pages else []
    rebuild_vector_store(chunks)
    return {
        "total_pages": len(pages),
        "total_chunks": len(chunks),
    }
