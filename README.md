
# SmartDoc AI – Intelligent PDF Question Answering using RAG

SmartDoc AI is a Retrieval-Augmented Generation (RAG) application that enables users to ask natural-language questions about PDF documents and receive context-aware answers generated using Large Language Models (LLMs).

The application extracts information from multiple PDF documents, converts the extracted text into vector embeddings, stores them in a FAISS vector database, and retrieves relevant information to generate grounded responses using GPT.

## Key Features

- Extract text from multiple PDF documents.
- Split extracted text into manageable chunks with overlapping context.
- Generate semantic embeddings using OpenAI embedding models.
- Store and search document embeddings using FAISS.
- Retrieve the most relevant document chunks based on user queries.
- Generate context-aware answers using GPT.
- Preserve document names and page numbers for source references.

## Architecture

PDF Documents
     |
     v
PDF Text Extraction (PyMuPDF)
     |
     v
Text Chunking
     |
     v
Embedding Generation
(OpenAI text-embedding-3-small)
     |
     v
FAISS Vector Database
     |
     v
User Question
     |
     v
Query Embedding
     |
     v
Semantic Search and Retrieval
     |
     v
Retrieved Context + User Question
     |
     v
GPT Answer Generation
     |
     v
Context-Aware Answer with References

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| LLM | OpenAI GPT |
| Embedding Model | text-embedding-3-small |
| PDF Processing | PyMuPDF |
| Vector Database | FAISS |
| Numerical Processing | NumPy |
| Environment Management | python-dotenv |
| Version Control | Git, GitHub |

## RAG Implementation

### 1. Document Processing
Extracts text from PDF documents while preserving document names and page numbers.

### 2. Text Chunking
Splits extracted text into smaller chunks with configurable chunk size and overlap to maintain contextual continuity.

### 3. Embedding Generation
Converts text chunks into numerical vector representations using OpenAI embeddings.

### 4. Vector Storage
Stores embeddings in a FAISS index using normalized vectors and inner-product similarity search.

### 5. Semantic Retrieval
Converts user queries into embeddings and retrieves the top-K most semantically similar document chunks.

### 6. Answer Generation
Passes the retrieved document context and user question to GPT to generate a natural-language response grounded in the retrieved information.

## Project Structure

SmartDoc-AI/
│
├── Documents/                 # Input PDF documents (not committed)
├── vector_store/              # Generated FAISS index and metadata (not committed)
│
├── pdf_processor.py           # PDF extraction and text chunking
├── embedding_generator.py     # OpenAI embedding generation
├── vector_store.py             # FAISS index creation and storage
├── retriever.py                # Semantic search and retrieval
├── answer_generator.py         # GPT-based answer generation
│
├── test_embeddings.py          # Embedding generation test
├── test_retriever.py           # Retrieval test
├── test_rag.py                 # End-to-end RAG test
│
├── requirements.txt
├── .gitignore
└── README.md

## Setup and Installation

### 1. Clone the repository

git clone https://github.com/SumathiThanga/SmartDoc-AI.git

cd SmartDoc-AI

### 2. Create a virtual environment

python -m venv .venv

### 3. Activate the environment

Windows:

.venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure API Key

Create a `.env` file in the project root:

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1

Never commit your API key to GitHub.

### 6. Add PDF documents

Create a `Documents` folder and place your PDF files inside it.

### 7. Build the vector store

Run:

python test_embeddings.py

This extracts document text, creates chunks, generates embeddings, and builds the FAISS index.

### 8. Test semantic retrieval

python test_retriever.py

### 9. Run the RAG pipeline

python test_rag.py

## Sample Query

**Question:**

What products and solutions does Siemens Digital Industries offer?

**Generated Answer:**

Siemens Digital Industries offers factory automation systems, process control systems, drives, inverters, sensors, PLM software, EDA solutions, Mendix low-code development, and digital services.

The system also retrieves relevant information about AI-enhanced EDA tools and Siemens Industrial Edge, with document and page references.

## Current Implementation Status

- [x] PDF text extraction
- [x] Text chunking with overlap
- [x] OpenAI embedding generation
- [x] FAISS vector index creation
- [x] Semantic search and retrieval
- [x] GPT-based answer generation
- [ ] Improved source-based citations
- [ ] Retrieval quality evaluation
- [ ] Streamlit user interface

## Future Enhancements

- Streamlit-based interactive document Q&A interface.
- Source-grounded citations with document and page references.
- Hybrid search combining semantic and keyword retrieval.
- Similarity thresholding and reranking.
- Support for tables, images, and multimodal PDF content.
- Conversation history and multi-turn question answering.

## Author

**Sumathi Thangara**

GitHub: https://github.com/SumathiThanga

LinkedIn: https://www.linkedin.com/in/sumathi-thangaraj-73535136
