
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
    temperature=0
)

prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant.

Answer the user's question using ONLY the
information provided in the context.

If the context does not contain enough
information, clearly say that you do not
have sufficient information.

Include document names and page numbers
as references in your answer."""
    ),
    (
        "human",
        """Context:
{context}

Question:
{question}"""
    )
])


def generate_answer(question, retrieved_chunks):

    context = ""

    for chunk in retrieved_chunks:
        context += f"""
Document: {chunk['document_name']}
Page: {chunk['page_number']}
Content: {chunk['text']}
"""

    # Fill the prompt template
    formatted_prompt = prompt_template.invoke({
        "context": context,
        "question": question
    })

    # Generate answer
    response = llm.invoke(formatted_prompt)

    return response.content
