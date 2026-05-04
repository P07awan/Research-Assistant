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
BACKEND_URL=http://127.0.0.1:8000
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

## Deployment

### Backend on Render

1. Create a new Web Service from your repo.
2. Set the build command:
   
	```
	pip install -r requirements.txt
	```
3. Set the start command:
   
	```
	uvicorn service:app --host 0.0.0.0 --port $PORT
	```
4. Add env vars (Render):
	- `UPLOAD_DIR=uploads`
	- Optional: `OPENAI_EMBEDDINGS_MODEL=text-embedding-3-large`

Note: Render disks are ephemeral. Uploads are not guaranteed to persist across deploys.

### Frontend on Streamlit

1. Deploy `app.py` on Streamlit Community Cloud.
2. Set env vars in Streamlit settings:
	- `BACKEND_URL=https://<your-render-service>.onrender.com`
3. Provide your OpenAI API key inside the app (API Key page).

## Notes

- Large PDFs can require significant memory. If you see Docling memory errors, reduce PDF size or pages.
- If you want to change the embedding model, set `OPENAI_EMBEDDINGS_MODEL` in `.env`.

## License

MIT. See LICENSE.
