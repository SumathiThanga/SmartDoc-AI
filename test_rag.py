
from retriever import search_documents
from answer_generator import generate_answer

question = "What products and solutions does Siemens Digital Industries offer?"

# Step 1: Retrieve relevant chunks
retrieved_chunks = search_documents(question, top_k=5)

# Step 2: Generate answer using GPT
answer = generate_answer(question, retrieved_chunks)

# Step 3: Display final answer
print("\nUser Question:")
print(question)

print("\nGPT Generated Answer:")
print(answer)
