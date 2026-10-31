from retriever import search_documents


question = "What products and solutions does Siemens Digital Industries offer?"

results = search_documents(question, top_k=5)


print("\nUser Question:", question)

print("\nRetrieved Results:")

for result in results:

    print("\n--------------------------------")

    print("Similarity:", result["similarity_score"])

    print("Document:", result["document_name"])

    print("Page:", result["page_number"])

    print("Chunk ID:", result["chunk_id"])

    print("Text:", result["text"])