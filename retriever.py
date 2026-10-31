import faiss
import json
import numpy as np
import os

from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Load API configuration
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

VECTOR_STORE_FOLDER = Path("vector_store")

def search_documents(question,top_k=5):
    index = faiss.read_index(str(VECTOR_STORE_FOLDER / "faiss.index"))
    with open(VECTOR_STORE_FOLDER / "chunks.json",
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)
    response = client.embeddings.create(model = "text-embedding-3-small",input=question)
    query_embedding = response.data[0].embedding
    query_vector = np.array([query_embedding],dtype=np.float32)
    faiss.normalize_L2(query_vector)
    scores,indices = index.search(query_vector,top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):

        # FAISS returns -1 if no result is available
        if idx == -1:
            continue

        chunk = chunks[idx]

        results.append({
            "similarity_score": float(score),
            "document_name": chunk["document_name"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"]
        })
    return results