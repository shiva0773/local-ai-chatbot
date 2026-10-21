# local-ai-chatbot
A local AI chatbot built with Python and Ollama

# Local AI Chatbot with RAG

A local AI chatbot built with Python, Streamlit, Ollama, ChromaDB, and SQLite. It can answer questions about uploaded documents using Retrieval-Augmented Generation (RAG).

## Features

- Local AI responses using Ollama.
- Document upload: PDF, TXT, Markdown, and Word (`.docx`).
- Text extraction and chunking.
- Embeddings generated using `nomic-embed-text`.
- Semantic search using ChromaDB.
- Chat history stored in SQLite.
- Source and page citations in document-based answers.

## Prerequisites

Install these before setting up the project:

1. **Git:** https://git-scm.com/downloads
2. **Python:** https://www.python.org/downloads/
3. **Ollama:** https://ollama.com/download

During Python installation on Windows, enable **Add Python to PATH** if that option is shown.

## Setup on Windows

### 1. Clone the repository

Open PowerShell or the VS Code terminal:

```powershell
git clone https://github.com/shiva0773/local-ai-chatbot.git
cd local-ai-chatbot
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 3. Install Python dependencies

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Download the Ollama models

Make sure Ollama is installed and running. Then run:

```powershell
ollama pull qwen2.5-coder:3b
ollama pull nomic-embed-text
```

The Qwen model generates responses, while Nomic generates embeddings for semantic search.

These models are downloaded separately on each computer and require disk space.

### 5. Start the chatbot

From the project root, run:

```powershell
streamlit run app.py
```

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open that URL in your browser.

## Using the chatbot

1. Open the Streamlit application.
2. Select one or more PDF, TXT, Markdown, or DOCX files from your computer.
3. Click **Index selected documents**.
4. Wait for indexing to finish.
5. Ask questions about the indexed documents.

The chatbot extracts text, splits it into chunks, creates embeddings, and stores them in ChromaDB. Retrieved passages are used to generate document-grounded answers.

## Local data and persistence

The following are local files or folders and are intentionally excluded from Git:

- `.venv/` — Python virtual environment.
- `chroma_db/` — generated vector index and document embeddings.
- `chat_history.db` — local chat history.
- `documents/` — local documents, which may contain private information.
- `.env` — local environment variables and secrets.

These items are not automatically restored by cloning the repository onto another computer.

After setting up on a new device, upload and index your documents again. Chat history from another computer is not automatically transferred.

**Important:** Keep private documents, API keys, passwords, and personal chat history out of GitHub.

## Project structure

```text
local-ai-chatbot/
├── app.py
├── chatbot.py
├── database.py
├── document_loader.py
├── embedding_demo.py
├── ingest.py
├── search_documents.py
├── semantic_search.py
├── test_database.py
├── test_document_loader.py
├── requirements.txt
├── README.md
├── documents/       # Local documents; not committed
├── chroma_db/       # Generated vector index; not committed
└── chat_history.db  # Local SQLite database; not committed
```

## Troubleshooting

### Ollama command not found

Confirm Ollama is installed and reopen the terminal. Check:

```powershell
ollama --version
```

### Model not found

Download the required models:

```powershell
ollama pull qwen2.5-coder:3b
ollama pull nomic-embed-text
```

### Python package missing

Activate `.venv` and reinstall dependencies:

```powershell
python -m pip install -r requirements.txt
```

### No documents indexed

Upload a supported document and click **Index selected documents** before asking questions.

### Port 8501 is already in use

Start Streamlit on another port:

```powershell
streamlit run app.py --server.port 8502
```

## Development notes

- `app.py` — Streamlit chatbot interface and RAG workflow.
- `database.py` — SQLite conversation and message persistence.
- `document_loader.py` — document extraction and text chunking.
- `ingest.py` — command-line document indexing.
- `search_documents.py` — command-line semantic search.
- `semantic_search.py` and `embedding_demo.py` — learning and experimentation.
- `test_database.py` and `test_document_loader.py` — tests.

## License

Add a license file if you intend to distribute or reuse this project publicly.
