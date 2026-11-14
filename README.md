# SmartDoc AI

SmartDoc AI is a document question-answering application that uses
Retrieval-Augmented Generation (RAG) to answer questions from uploaded
PDF documents.

The application extracts text from PDFs, splits the text into smaller
chunks, creates embeddings, stores them in a FAISS vector store, and
retrieves relevant content when a user asks a question. LangChain
coordinates the retrieval and answer-generation workflow, while FastAPI
exposes the functionality through REST API endpoints.

## Features

-   Upload PDF documents through the API.
-   Extract text and page information from PDFs.
-   Split extracted text into chunks using LangChain's
    `RecursiveCharacterTextSplitter`.
-   Generate document embeddings using OpenAI embeddings through
    LangChain.
-   Store and search embeddings using LangChain's FAISS vector store.
-   Generate context-based answers using `ChatOpenAI`.
-   Use `ChatPromptTemplate` to guide answer generation.
-   Return source information with answers, including document names and
    page numbers.
-   Delete documents and rebuild the vector store from the remaining
    PDFs.
-   Explore and test endpoints through FastAPI Swagger UI.

## RAG architecture

``` text
PDF Upload
    |
    v
PDF Text Extraction (PyMuPDF)
    |
    v
Text Splitting (RecursiveCharacterTextSplitter)
    |
    v
Embeddings (OpenAIEmbeddings)
    |
    v
LangChain FAISS Vector Store
    |
    v
User Question
    |
    v
Question Embedding and Similarity Search
    |
    v
Relevant Document Chunks
    |
    v
ChatPromptTemplate + ChatOpenAI
    |
    v
Answer + Source References
```

## Technology stack

-   **Python** -- application language
-   **FastAPI** -- REST API framework
-   **Uvicorn** -- ASGI server
-   **LangChain** -- RAG orchestration, prompts, and document processing
-   **LangChain OpenAI integration** -- embeddings and chat model
-   **FAISS** -- vector similarity search
-   **PyMuPDF** -- PDF text extraction
-   **OpenAI API** -- embedding and language-model services

## Project structure

The main application files are organized as follows. Your local project
may contain additional files such as tests, Docker configuration, or
frontend code.

``` text
SmartDoc-AI/
│
├── Documents/                 # Uploaded PDF documents
│
├── vector_store/              # Persisted LangChain FAISS index
│   ├── index.faiss
│   └── index.pkl
│
├── api.py                     # FastAPI application and API endpoints
├── pdf_processor.py           # PDF extraction and text splitting
├── embedding_generator.py     # OpenAI embeddings via LangChain
├── vector_store.py            # FAISS vector-store creation and saving
├── rag_chain.py               # Complete LangChain RAG pipeline
├── test_rag.py                # RAG pipeline test
│
├── Requirements.txt           # Python dependencies
├── .env                       # Local environment variables (not committed)
├── .gitignore
└── README.md
```

## Prerequisites

-   Python installed on your machine.
-   An OpenAI API key.
-   Git, if you want to clone and contribute to the repository.

## Setup

### 1. Clone the repository

``` bash
git clone https://github.com/SumathiThanga/SmartDoc-AI.git
cd SmartDoc-AI
```

If you are working on the LangChain migration branch:

``` bash
git checkout feature/langchain-rag
```

### 2. Create and activate a virtual environment

**Windows:**

``` bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

``` bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r Requirements.txt
```

Make sure the requirements file includes the packages used by the
application, including the LangChain integrations, FAISS, FastAPI,
PyMuPDF, and `python-dotenv`.

### 4. Configure environment variables

Create a `.env` file in the project root:

``` env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1
```

Replace `your_openai_api_key` with your own API key.

Do not commit `.env` or expose your API key in source code, screenshots,
logs, or public repositories.

## Run the application

From the project root, with the virtual environment activated:

``` bash
python -m uvicorn api:app --reload
```

The API will be available at:

-   API base URL: `http://127.0.0.1:8000`
-   Swagger UI: `http://127.0.0.1:8000/docs`
-   ReDoc: `http://127.0.0.1:8000/redoc`
-   OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

FastAPI generates the Swagger UI and OpenAPI schema automatically from
the routes and Pydantic models defined in `api.py`.

## Using the API

Open Swagger UI at `http://127.0.0.1:8000/docs` to view the available
endpoints and try them interactively.

### 1. Upload a PDF

Use the PDF upload endpoint shown in Swagger UI to upload a PDF file.

The application processes the PDFs in the `Documents/` directory,
creates text chunks and embeddings, and builds the FAISS vector store.

### 2. Ask a question

Use the `POST /ask` endpoint. Example request:

``` json
{
  "question": "What are the types of emulsion?",
  "top_k": 5
}
```

The `question` field contains the user's question. `top_k` controls how
many relevant chunks are retrieved.

The response contains:

-   `answer` -- the generated answer.
-   `sources` -- retrieved source chunks and their metadata, such as
    document name, page number, chunk ID, similarity score, and text.

Example response structure (the answer, score values, and source content
will vary):

``` json
{
  "answer": "The types of emulsion are ...",
  "sources": [
    {
      "document_name": "example.pdf",
      "page_number": 2,
      "chunk_id": 10,
      "similarity_score": 0.60,
      "text": "Relevant text extracted from the PDF..."
    }
  ]
}
```

### 3. Delete a PDF

Use the document deletion endpoint shown in Swagger UI. The application
temporarily moves the selected PDF, rebuilds the vector store from the
remaining PDFs, and removes the backup after successful processing.

If no PDFs remain, the persisted LangChain FAISS index files are
removed.

## LangChain implementation

The RAG pipeline is separated into modules:

  -----------------------------------------------------------------------
  Module                              Responsibility
  ----------------------------------- -----------------------------------
  `pdf_processor.py`                  Extracts PDF text and splits it
                                      into chunks

  `embedding_generator.py`            Generates embeddings with
                                      `OpenAIEmbeddings`

  `vector_store.py`                   Creates and saves the LangChain
                                      FAISS vector store

  `rag_chain.py`                      Retrieves relevant documents and
                                      generates answers

  `api.py`                            Exposes document and
                                      question-answering endpoints
  -----------------------------------------------------------------------

The persisted LangChain FAISS store uses:

-   `vector_store/index.faiss` -- FAISS vector index
-   `vector_store/index.pkl` -- document store and metadata

The vector store should be generated by the application's current
LangChain implementation. Do not mix it with index files created by the
previous custom FAISS implementation.

## Run the RAG test

If `test_rag.py` is configured to use the current vector store, run:

``` bash
python test_rag.py
```

This tests the RAG pipeline independently of the FastAPI endpoints.

## Important security notes

-   Keep API keys in `.env` and ensure `.env` is listed in `.gitignore`.
-   Do not commit private PDFs, uploaded documents, virtual
    environments, or generated vector-store data unless you
    intentionally want to publish them.
-   LangChain FAISS loading may use pickle deserialization. Only load
    index files that you created or otherwise fully trust.
-   Validate uploaded filenames and file types, and enforce upload size
    limits.
-   Avoid returning internal exception details to public clients in a
    production deployment; log diagnostic details on the server instead.

## Notes

-   The exact upload and delete route paths and request fields are
    defined by `api.py`; use `/docs` as the source of truth.
-   The example commands above assume the application is run from the
    project root.
-   If you deploy with Docker, ensure the container installs the
    dependencies from `Requirements.txt`, receives `OPENAI_API_KEY`
    securely, and persists the `Documents/` and `vector_store/`
    directories if uploaded files and indexes must survive container
    replacement.

## License

Add the license and usage terms applicable to this repository before
distributing it publicly.
