from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Initialize embedding model
embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def generate_embeddings(chunks):

    # Extract text from chunks
    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # Generate embeddings using LangChain
    embeddings = embeddings_model.embed_documents(
        texts
    )

    return embeddings