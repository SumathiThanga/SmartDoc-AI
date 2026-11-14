import os
from typing import TypedDict, List, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

from vector_store import load_vector_store

load_dotenv()


class RAGState(TypedDict, total=False):
    question: str
    top_k: int
    documents: List[Document]
    answer: str


llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant.
Answer using ONLY the information in the supplied context.
If the context does not contain enough information, say so clearly.
Cite document names and page numbers in your answer.

Context:
{context}""",
    ),
    ("human", "{question}"),
])


def retrieve_node(state: RAGState):
    vector_store = load_vector_store()
    if vector_store is None:
        raise RuntimeError("Vector store not found. Upload a PDF first.")

    results = vector_store.similarity_search_with_score(
        state["question"],
        k=state.get("top_k", 5),
    )

    documents = []
    for document, score in results:
        document.metadata["similarity_score"] = float(score)
        documents.append(document)

    return {"documents": documents}


def generate_answer_node(state: RAGState):
    context_parts = []
    for document in state.get("documents", []):
        context_parts.append(
            f"Document: {document.metadata.get('document_name', 'Unknown')}\n"
            f"Page: {document.metadata.get('page_number', 'Unknown')}\n"
            f"Content: {document.page_content}"
        )

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "question": state["question"],
        "context": "\n\n---\n\n".join(context_parts),
    })
    return {"answer": answer}


builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve_node)
builder.add_node("generate_answer", generate_answer_node)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate_answer")
builder.add_edge("generate_answer", END)

rag_graph = builder.compile()


def generate_rag_answer(question, top_k=5):
    """Workflow 2: retrieve relevant chunks and generate an answer."""
    result = rag_graph.invoke({
        "question": question,
        "top_k": top_k,
    })

    sources = []
    for document in result.get("documents", []):
        sources.append({
            "document_name": document.metadata.get("document_name"),
            "page_number": document.metadata.get("page_number"),
            "chunk_id": document.metadata.get("chunk_id"),
            "similarity_score": document.metadata.get("similarity_score"),
            "text": document.page_content,
        })

    return {
        "answer": result["answer"],
        "sources": sources,
    }
