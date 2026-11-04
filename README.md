# SmartDoc AI – Intelligent Document Question Answering System

SmartDoc AI is an AI-powered document assistant that allows users to upload PDF documents, manage their files, and ask questions using natural language.

It retrieves relevant information from uploaded documents and generates context-aware answers with source references using Retrieval-Augmented Generation (RAG).

The application is built with React and FastAPI and supports containerized deployment using Docker and Docker Compose.

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
- Run frontend and backend services using Docker containers.
- Persist uploaded documents and vector data using Docker volume mappings.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| API Testing | Swagger UI |
| PDF Processing | PyMuPDF |
| AI Integration | OpenAI API |
| Vector Database | FAISS |
| Embeddings | Embedding generation module |
| Architecture | Retrieval-Augmented Generation (RAG) |
| Containerization | Docker |
| Container Orchestration | Docker Compose |
| Web Server | Nginx |

## Project Structure

```text
SmartDoc-AI/
│
├── Documents/                 # Uploaded PDF documents
├── vector_store/              # FAISS index and vector data
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
│
├── api.py                     # FastAPI application
├── app.py
├── pdf_processor.py
├── embedding_generator.py
├── vector_store.py
├── retriever.py
├── answer_generator.py
├── Requirements.txt
│
├── Dockerfile                 # Backend Docker configuration
├── compose.yaml               # Docker Compose configuration
├── .dockerignore
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SumathiThanga/SmartDoc-AI.git
cd SmartDoc-AI
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your OpenAI API configuration:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1
```

Replace `your_openai_api_key` with your own OpenAI API key.

**Important:** Never commit your `.env` file or expose your API key on GitHub.

### 3. Run Using Docker (Recommended)

Make sure Docker and Docker Compose are installed.

Build the Docker images and start the application:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

The Docker Compose setup runs two services:

- **Backend:** FastAPI application running on port 8000 inside the Docker network.
- **Frontend:** React application served by Nginx on port 80 inside the frontend container.

The frontend Nginx server forwards `/api/` requests to the FastAPI backend.

The frontend is exposed on host port **8080**.

Open the application:

```text
http://localhost:8080
```

For an EC2 deployment, access it using:

```text
http://<EC2-PUBLIC-IP>:8080
```

Ensure the EC2 security group permits access to port 8080 from your intended client IP addresses.

### 4. Data Persistence

Docker Compose maps the following folders from the host machine into the backend container:

| Host Folder | Container Folder | Purpose |
|---|---|---|
| `Documents/` | `/app/Documents/` | Uploaded PDF documents |
| `vector_store/` | `/app/vector_store/` | FAISS index and vector data |

This allows uploaded documents and vector data to remain on the host when containers are restarted or recreated.

### 5. Run Locally Without Docker (Development)

#### Backend Setup

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

Backend endpoints:

- Application: http://localhost:8000
- Swagger documentation: http://localhost:8000/docs

#### Frontend Setup

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

## Docker Architecture

```text
             User / Browser
                    |
                    v
             Frontend (Nginx)
                Port 8080
                    |
                    | /api/
                    v
             Backend (FastAPI)
                Port 8000
                    |
          ---------------------
          |                   |
          v                   v
      Documents            FAISS
       Folder           Vector Store
          |
          v
       OpenAI API
```

The frontend and backend communicate through the Docker Compose network. The backend is not directly published to the host.

## Deployment

The application has been containerized and deployed on an AWS EC2 Ubuntu instance.

Deployment components:

- AWS EC2 – Application hosting.
- Docker – Containerization.
- Docker Compose – Service management.
- Nginx – Frontend serving and API reverse proxy.
- FastAPI – Backend API.
- React – Frontend interface.

The current EC2 deployment uses port 8080 for frontend access.

For unrestricted public production deployment, configure HTTPS, user authentication, and appropriate document access controls before making the application publicly accessible.

## Future Enhancements

- Domain-based deployment with HTTPS.
- User authentication and authorization.
- Document-level access control for multiple users.
- Improved document processing and indexing.
- Enhanced error handling and upload validation.
- Production monitoring and scalability.

## Author

**Sumathi Thangaraj**

GitHub: https://github.com/SumathiThanga/SmartDoc-AI