
import streamlit as st

from retriever import search_documents
from answer_generator import generate_answer


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="SmartDoc AI",
    page_icon="📚",
    layout="wide"
)


# --------------------------------
# Application Header
# --------------------------------

st.title("📚 SmartDoc AI")

st.subheader("Intelligent PDF Question Answering")

st.write(
    "Ask questions about your PDF documents "
    "and get AI-generated answers using RAG."
)

st.divider()


# --------------------------------
# User Input
# --------------------------------

question = st.text_input(
    "Enter your question",
    placeholder="What products does Siemens Digital Industries offer?"
)

top_k = st.slider(
    "Number of relevant chunks to retrieve",
    min_value=1,
    max_value=10,
    value=5
)


# --------------------------------
# Ask Question
# --------------------------------

if st.button("Ask SmartDoc AI", type="primary"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner("Searching documents..."):

                # Step 1: Retrieve relevant chunks
                retrieved_chunks = search_documents(
                    question,
                    top_k=top_k
                )

            if not retrieved_chunks:

                st.warning(
                    "No relevant information was retrieved."
                )

            else:

                with st.spinner("Generating AI answer..."):

                    # Step 2: Generate answer
                    answer = generate_answer(
                        question,
                        retrieved_chunks
                    )

                # --------------------------------
                # Display Answer
                # --------------------------------

                st.divider()

                st.subheader("🤖 Generated Answer")

                st.markdown(answer)

                # --------------------------------
                # Display Retrieved Sources
                # --------------------------------

                st.divider()

                st.subheader("📄 Retrieved Sources")

                for i, result in enumerate(
                    retrieved_chunks,
                    start=1
                ):

                    with st.expander(
                        f"Source {i} - {result['document_name']} "
                        f"(Page {result['page_number']})"
                    ):

                        st.write(
                            "**Similarity Score:**",
                            round(
                                result["similarity_score"],
                                4
                            )
                        )

                        st.write(
                            "**Chunk ID:**",
                            result["chunk_id"]
                        )

                        st.write("**Retrieved Text:**")

                        st.write(result["text"])

        except Exception as e:

            st.error(f"An error occurred: {e}")


# --------------------------------
# Footer
# --------------------------------

st.divider()

st.caption(
    "SmartDoc AI | Powered by OpenAI, FAISS and Streamlit"
)
