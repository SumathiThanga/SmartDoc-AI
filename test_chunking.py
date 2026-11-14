from pdf_processor import extract_all_pdfs
from pdf_processor import create_chunks
from pdf_processor import docfolder

# Extract PDF pages
pages = extract_all_pdfs(docfolder)

print("Total pages:", len(pages))

# Generate LangChain chunks
chunks = create_chunks(pages)

print("Total chunks:", len(chunks))

# Inspect first 5 chunks
for chunk in chunks[:5]:

    print("\n------------------------")

    print("Document:", chunk["document_name"])
    print("Page:", chunk["page_number"])
    print("Chunk ID:", chunk["chunk_id"])
    print("Characters:", len(chunk["text"]))
    print("Text:", chunk["text"][:200])