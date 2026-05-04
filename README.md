# Research Assistant

A Streamlit-based research assistant with a FastAPI backend. It uses OpenAI for both embeddings and responses, supports PDF-to-RAG chat, and provides topic research with Wikipedia, YouTube, and Semantic Scholar tools. Files are stored locally (no AWS).

## Features

- Research topic assistant with tool-augmented summaries.
- PDF upload and chat (RAG with hybrid retrieval).
- Local storage for uploads in the `uploads/` directory.
- OpenAI embeddings and chat completions.

## Tech Stack

- Python 3.11
- Streamlit (UI)
- FastAPI (backend)
- LangChain (agents and RAG)
- OpenAI API
- FAISS (vector store)
- Docling (PDF conversion)

## Project Structure

- `app.py` - Streamlit navigation and entry point
- `pages/` - UI pages (API key, research assistant, chat bot)
- `service.py` - FastAPI app
- `services/` - RAG pipeline and ingestion
- `routers/` - API routes
- `uploads/` - Local file storage

## Setup

### 1) Create and activate a virtual environment (Windows)

```
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` in the project root (do not commit it):

```
OPENAI_API_KEY=your_openai_api_key
```

Optional:

```
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-large
UPLOAD_DIR=uploads
```

## Run

### Start the backend

```
python service.py
```

### Start the Streamlit app

```
streamlit run app.py
```

## Usage

1. Open the Streamlit app.
2. Go to the API Key page and enter your OpenAI key.
3. Use Research Assistant for topic exploration.
4. Use Chat Bot to upload a PDF and ask questions.

## Notes

- Large PDFs can require significant memory. If you see Docling memory errors, reduce PDF size or pages.
- If you want to change the embedding model, set `OPENAI_EMBEDDINGS_MODEL` in `.env`.

## License

MIT. See LICENSE.
