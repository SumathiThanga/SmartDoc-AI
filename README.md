# SmartDoc AI

SmartDoc AI is a PDF-based question-answering application built using **Retrieval-Augmented Generation (RAG)**. It allows users to upload PDF documents and ask questions based on their contents.

The application uses **LangChain, LangGraph, OpenAI, and FAISS** to process documents, generate embeddings, retrieve relevant information, and generate context-aware answers.

## Features

- Upload PDF documents through FastAPI.
- Extract text and page information using PyMuPDF.
- Split extracted text into chunks using LangChain's `RecursiveCharacterTextSplitter`.
- Generate embeddings using OpenAI's `text-embedding-3-small`.
- Store and retrieve document embeddings using FAISS.
- Use LangGraph to orchestrate document ingestion and RAG question answering.
- Add newly uploaded documents incrementally without reprocessing existing PDFs.
- Generate context-aware answers using `ChatOpenAI`.
- Return source references, including document names and page numbers.
- Delete documents and rebuild the vector store using the remaining PDFs.
- Explore API endpoints through FastAPI Swagger UI.

## Architecture

SmartDoc AI separates document processing and question answering into two independent workflows.

### Workflow 1: Document Ingestion

This workflow processes newly uploaded PDF documents and adds their embeddings to the existing FAISS vector store.

```text
PDF Upload
    |
    v
PDF Text Extraction (PyMuPDF)
    |
    v
Text Splitting (LangChain)
    |
    v
Generate Embeddings (OpenAIEmbeddings)
    |
    v
Add Documents to Existing FAISS Index
    |
    v
Persist Updated Vector Store
```

**Incremental ingestion:** Only the newly uploaded PDF is extracted, split, and embedded. Previously uploaded documents are not reprocessed during normal uploads.

### Workflow 2: RAG Question Answering

This workflow retrieves relevant document chunks and generates an answer to the user's question.

```text
User Question
    |
    v
Retrieve Relevant Chunks
    |
    v
FAISS Similarity Search
    |
    v
Generate Context-Aware Answer
    |
    v
Return Answer + Source References
```

LangGraph manages the retrieval and answer-generation steps as a state-based workflow.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| LangChain | Document processing, prompts, and integrations |
| LangGraph | Workflow orchestration |
| OpenAIEmbeddings | Text embedding generation |
| ChatOpenAI | Answer generation |
| FAISS | Vector similarity search |
| PyMuPDF | PDF text extraction |
| RecursiveCharacterTextSplitter | Text chunking |
| OpenAI API | Embedding and language-model services |

## Project Structure

```text
SmartDoc-AI/
│
├── Documents/                 # Uploaded PDF documents
│
├── vector_store/              # Persisted FAISS index
│   ├── index.faiss
│   └── index.pkl
│
├── api.py                     # FastAPI application and endpoints
├── pdf_processor.py           # PDF extraction and text splitting
├── ingestion.py               # Document ingestion workflow
├── rag_graph.py               # LangGraph RAG workflow
├── vector_store.py            # FAISS vector-store operations
│
├── Requirements.txt           # Python dependencies
├── .env                       # Environment variables (not committed)
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.10 or later (use a Python version supported by all installed dependencies).
- OpenAI API key.
- Git.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/SumathiThanga/SmartDoc-AI.git
cd SmartDoc-AI
```

Checkout the LangGraph implementation branch:

```bash
git checkout feature/langgraph-two-workflows
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r Requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your actual OpenAI API key.

The application uses `python-dotenv` to load environment variables. LangChain's OpenAI integrations automatically read `OPENAI_API_KEY`, so the key does not need to be explicitly passed when initializing `OpenAIEmbeddings` or `ChatOpenAI`.

**Security:** Never commit your `.env` file or expose your API key in source code.

## Run the Application

From the project root:

```bash
python -m uvicorn api:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Using the API

Open Swagger UI at `http://127.0.0.1:8000/docs`.

### 1. Upload a PDF

Use the `POST /upload` endpoint to upload a PDF document.

The ingestion workflow:

1. Validates and saves the PDF.
2. Extracts text from the uploaded PDF.
3. Splits the extracted text into chunks.
4. Generates embeddings for the new chunks.
5. Adds the new embeddings to the existing FAISS index.

Existing documents are not reprocessed during normal uploads.

### 2. Ask a Question

Use the `POST /ask` endpoint.

Example request:

```json
{
  "question": "What are the types of emulsion?",
  "top_k": 5
}
```

`top_k` specifies the number of relevant chunks to retrieve.

The RAG workflow returns:

- `answer`: Generated answer based on retrieved document content.
- `sources`: Relevant source chunks and their metadata, including document name, page number, chunk ID, similarity score, and text.

### 3. List Uploaded Documents

Use:

```text
GET /documents
```

Returns the uploaded PDF filenames and total document count.

### 4. Delete a PDF

Use:

```text
DELETE /documents/{filename}
```

When a PDF is deleted, the vector store is rebuilt using the remaining PDF documents to ensure that deleted document content is no longer available through retrieval.

If no PDFs remain, the persisted FAISS index files are removed.

## LangGraph Implementation

The application separates responsibilities into independent modules.

| Module | Responsibility |
|---|---|
| `api.py` | FastAPI endpoints and request handling |
| `pdf_processor.py` | PDF extraction and text chunking |
| `ingestion.py` | Document ingestion and incremental indexing |
| `rag_graph.py` | LangGraph retrieval and answer-generation workflow |
| `vector_store.py` | FAISS creation, loading, updating, and rebuilding |

### Benefits of This Architecture

- **Separation of concerns:** Ingestion and question answering are independent workflows.
- **Incremental processing:** New uploads do not require re-embedding existing documents.
- **Workflow orchestration:** LangGraph organizes retrieval and answer generation into distinct nodes.
- **Maintainability:** Each module has a clearly defined responsibility.
- **Source traceability:** Answers include references to the original PDF documents and pages.

## FAISS Vector Store

The persisted LangChain FAISS vector store contains:

```text
vector_store/
├── index.faiss
└── index.pkl
```

- `index.faiss`: Stores the FAISS vector index.
- `index.pkl`: Stores the document store and associated metadata.

The vector store is updated when new PDFs are uploaded and rebuilt when documents are deleted.

Only load trusted FAISS index files because LangChain's local FAISS loading can use pickle deserialization.

## Docker

The project includes Docker configuration for running the application in containers.

If dependencies change, rebuild the Docker image:

```bash
docker compose up --build
```

Ensure that the OpenAI API key is supplied securely and that the `Documents/` and `vector_store/` directories are persisted if data must survive container replacement.

## Security Considerations

- Keep API keys in `.env`.
- Ensure `.env` is included in `.gitignore`.
- Do not commit private PDFs, virtual environments, or generated vector-store data.
- Validate uploaded filenames, file types, and file sizes.
- Load only trusted FAISS index files.
- Avoid exposing internal exception details in production responses.

## License

Add the license and usage terms applicable to this repository before distributing it publicly.
