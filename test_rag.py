from rag_chain import generate_rag_answer

question = "What are the types of emulsion?"

result = generate_rag_answer(
    question,
    top_k=5
)

print("\nGPT Generated Answer:\n")
print(result["answer"])

print("\nSources:\n")

for source in result["sources"]:

    print("Document:", source["document_name"])
    print("Page:", source["page_number"])
    print("Chunk ID:", source["chunk_id"])
    print("Similarity:", source["similarity_score"])
    print("--------------------------")