# SmartDoc AI – Intelligent Document Question Answering System

SmartDoc AI is an AI-powered document assistant that allows users to upload PDF documents, manage their files, and ask questions using natural language. It retrieves relevant information from uploaded documents and generates context-aware answers with source references.

## Features

- Upload and manage PDF documents.
- Delete unwanted documents.
- Refresh the document list.
- Extract and process PDF content.
- Split documents into searchable chunks.
- Generate vector embeddings.
- Store and retrieve document vectors using FAISS.
- Ask questions in natural language.
- Generate AI-powered answers using Retrieval-Augmented Generation (RAG).
- Display relevant document sources with answers.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| API Testing | Swagger UI |
| PDF Processing | Python PDF processing libraries |
| Embeddings | Embedding generation module |
| Vector Database | FAISS |
| Architecture | Retrieval-Augmented Generation (RAG) |
| Deployment | Docker (planned) |

## Project Structure

```text
SmartDoc-AI/
│
├── Documents/
├── vector_store/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── api.py
├── app.py
├── pdf_processor.py
├── embedding_generator.py
├── vector_store.py
├── retriever.py
├── answer_generator.py
├── Requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/SumathiThanga/SmartDoc-AI.git
cd SmartDoc-AI
```

### 2. Backend Setup

Create and activate a Python virtual environment.

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r Requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Backend API:

- Application: http://localhost:8000
- Swagger documentation: http://localhost:8000/docs

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend:

http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome message |
| GET | `/health` | Health check |
| GET | `/documents` | List uploaded documents |
| POST | `/upload` | Upload PDF documents |
| POST | `/ask` | Ask questions about documents |
| DELETE | `/documents/{filename}` | Delete a document |

## Application Workflow

1. User uploads PDF documents through the React interface.
2. FastAPI receives and processes the uploaded documents.
3. PDF content is extracted and divided into chunks.
4. Embeddings are generated for the chunks.
5. FAISS stores the vectors for similarity search.
6. User submits a question through the chat interface.
7. Relevant document chunks are retrieved.
8. The AI generates an answer with supporting source references.

## Future Enhancements

- Docker-based deployment.
- Improved document processing and indexing.
- Enhanced error handling and upload validation.
- Production deployment and scalability.

## Author

**Sumathi Thangaraj**

GitHub: https://github.com/SumathiThanga/SmartDoc-AI
