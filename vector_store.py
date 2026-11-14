
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings


VECTOR_STORE_FOLDER = Path("vector_store")

embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def create_vector_store(chunks, embeddings):

    # Prepare text and metadata separately
    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_name": chunk["document_name"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"]
        }
        for chunk in chunks
    ]

    # Pair each text with its already-generated embedding
    text_embeddings = list(zip(texts, embeddings))

    # Create LangChain FAISS vector store
    vector_store = FAISS.from_embeddings(
        text_embeddings=text_embeddings,
        embedding=embeddings_model,
        metadatas=metadatas,
        normalize_L2=True,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
    )

    # Save vector store locally
    VECTOR_STORE_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store.save_local(
        str(VECTOR_STORE_FOLDER)
    )

    print("\nLangChain FAISS vector store created!")

    print("Total vectors stored:", vector_store.index.ntotal)

    print(
        "Vector dimensions:",
        vector_store.index.d
    )

    return vector_store
