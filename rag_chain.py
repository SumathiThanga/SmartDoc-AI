
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate
)

from langchain_core.runnables import RunnableLambda

from langchain_classic.chains.retrieval import create_retrieval_chain

from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain
)

load_dotenv()

VECTOR_STORE_FOLDER = Path("vector_store")


# Initialize embedding model
embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# Initialize LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
    temperature=0
)


# Main RAG function
def generate_rag_answer(question, top_k=5):

    # Load FAISS vector store
    vector_store = FAISS.load_local(
        str(VECTOR_STORE_FOLDER),
        embeddings_model,
        allow_dangerous_deserialization=True
    )

    # Retrieve relevant documents and preserve similarity scores
    def retrieve(inputs):

        results = vector_store.similarity_search_with_score(
            inputs["input"],
            k=top_k
        )

        documents = []

        for document, score in results:

            document.metadata["similarity_score"] = float(score)

            documents.append(document)

        return documents

    retriever = RunnableLambda(retrieve)

    # Prompt for answering
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful AI assistant.

Answer the user's question using ONLY
the information provided in the context.

If the context does not contain enough
information, clearly say that you do not
have sufficient information.

Include document names and page numbers
as references in your answer.

Context:
{context}"""
        ),
        (
            "human",
            "{input}"
        )
    ])

    # Format each retrieved document
    document_prompt = PromptTemplate.from_template(
        """Document: {document_name}
Page: {page_number}
Content: {page_content}"""
    )

    # Create document combination chain
    question_answer_chain = create_stuff_documents_chain(
        llm,
        prompt,
        document_prompt=document_prompt
    )

    # Create complete retrieval chain
    rag_chain = create_retrieval_chain(
        retriever,
        question_answer_chain
    )

    # Execute the chain
    response = rag_chain.invoke({
        "input": question
    })

    # Convert retrieved documents into existing API format
    sources = []

    for document in response["context"]:

        sources.append({
            "document_name": document.metadata["document_name"],
            "page_number": document.metadata["page_number"],
            "chunk_id": document.metadata["chunk_id"],
            "similarity_score": document.metadata["similarity_score"],
            "text": document.page_content
        })

    return {
        "answer": response["answer"],
        "sources": sources
    }
