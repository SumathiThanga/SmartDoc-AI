import pymupdf
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_pdf(pdf_path):
    """Extract non-empty pages from one PDF."""
    pdf_path = Path(pdf_path)
    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text()
            if page_text.strip():
                pages.append({
                    "document_name": pdf_path.name,
                    "page_number": page_number,
                    "text": page_text,
                })

    return pages


def extract_all_pdfs(folder):
    """Extract pages from every PDF in a folder."""
    all_pages = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        all_pages.extend(extract_pdf(pdf_path))
    return all_pages


def create_chunks(pages, chunk_size=700, overlap=100):
    """Split extracted pages into LangChain-compatible chunk dictionaries."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []
    for page in pages:
        for text in splitter.split_text(page["text"]):
            chunks.append({
                "document_name": page["document_name"],
                "page_number": page["page_number"],
                "chunk_id": len(chunks),
                "text": text,
            })
    return chunks
