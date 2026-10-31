import pdf_processor
from vector_store import create_vector_store

from embedding_generator import generate_embeddings
pages = pdf_processor.extract_all_pdfs(pdf_processor.docfolder)
chunks = pdf_processor.create_chunks(pages)
print("Total chunks:", len(chunks))
# Generate embeddings
embeddings = generate_embeddings(chunks)

print("Total embeddings:", len(embeddings))

print("First embedding dimensions:", len(embeddings[0]))

print("First 5 vector values:", embeddings[0][:5])

# Create FAISS vector store
index = create_vector_store(chunks, embeddings)