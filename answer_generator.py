
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_answer(question, retrieved_chunks):

    # Combine retrieved chunks into context
    context = ""

    for chunk in retrieved_chunks:
        context += f"""
        Document: {chunk['document_name']}
        Page: {chunk['page_number']}
        Content: {chunk['text']}
        """

    # Create prompt
    prompt = f"""
    You are a helpful AI assistant.
    Answer the user's question using ONLY the
    information provided in the context.

    If the context does not contain enough
    information, clearly say that you do not
    have sufficient information.

    Include document names and page numbers
    as references in your answer.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    # Send prompt to GPT
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        input=prompt
    )

    return response.output_text
