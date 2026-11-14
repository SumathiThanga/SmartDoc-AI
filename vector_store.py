from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

VECTOR_STORE_FOLDER = Path("vector_store")
INDEX_FILE = VECTOR_STORE_FOLDER / "index.faiss"
METADATA_FILE = VECTOR_STORE_FOLDER / "index.pkl"

load_dotenv()

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")


def _to_documents(chunks):
    return [
        Document(
            page_content=chunk["text"],
            metadata={
                "document_name": chunk["document_name"],
                "page_number": chunk["page_number"],
                "chunk_id": chunk["chunk_id"],
            },
        )
        for chunk in chunks
    ]


def vector_store_exists():
    return INDEX_FILE.exists() and METADATA_FILE.exists()


def load_vector_store():
    if not vector_store_exists():
        return None

    return FAISS.load_local(
        str(VECTOR_STORE_FOLDER),
        embeddings_model,
        allow_dangerous_deserialization=True,
    )


def add_chunks_to_vector_store(chunks):
    """Embed and add only the supplied (new) chunks."""
    if not chunks:
        raise ValueError("No chunks were supplied for indexing.")

    documents = _to_documents(chunks)
    vector_store = load_vector_store()

    if vector_store is None:
        vector_store = FAISS.from_documents(
            documents,
            embeddings_model,
            normalize_L2=True,
            distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
        )
    else:
        vector_store.add_documents(documents)

    VECTOR_STORE_FOLDER.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(VECTOR_STORE_FOLDER))
    return vector_store


def rebuild_vector_store(chunks):
    """Rebuild the index. Intended for document deletion/recovery, not uploads."""
    VECTOR_STORE_FOLDER.mkdir(parents=True, exist_ok=True)

    if not chunks:
        INDEX_FILE.unlink(missing_ok=True)
        METADATA_FILE.unlink(missing_ok=True)
        return None

    documents = _to_documents(chunks)
    vector_store = FAISS.from_documents(
        documents,
        embeddings_model,
        normalize_L2=True,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )
    vector_store.save_local(str(VECTOR_STORE_FOLDER))
    return vector_store


def clear_vector_store():
    INDEX_FILE.unlink(missing_ok=True)
    METADATA_FILE.unlink(missing_ok=True)
