import os
import re
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from services.ingestion import DoclingPDFLoader
from services.rag_service import rag_service
from handlers.exceptions import ChunkingError, EmbeddingError
from config import settings
import logging

# Initialize logger
logger = logging.getLogger("pdf_router")
logger.setLevel(logging.INFO)

# Create a router for PDF-related endpoints
router = APIRouter(tags=["PDF"])

@router.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...), api_key: str = Form(...)):
    """
    Endpoint to process an uploaded PDF and store it in RAG service.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="file is required")
    if not api_key.strip():
        raise HTTPException(status_code=400, detail="api_key cannot be empty")

    try:
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
        file_id = str(uuid.uuid4())
        upload_dir = settings.UPLOAD_DIR or "uploads"
        file_dir = os.path.join(upload_dir, file_id)
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, safe_name)

        logger.info(f"Saving uploaded PDF: {file_path}")
        try:
            content = await file.read()
            with open(file_path, "wb") as out_file:
                out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

        # Load PDF content
        try:
            extract_text = DoclingPDFLoader(file_path=file_path).load()[0].page_content
        except Exception as e:
            raise ChunkingError(f"PDF chunking failed: {e}")

        # Process PDF using RAG service
        try:
            rag_service.process_pdf(extract_text, api_key)
        except Exception as e:
            raise EmbeddingError(f"RAG processing failed: {e}")

        return {"status": "success", "message": "PDF processed successfully."}

    except (ChunkingError, EmbeddingError) as e:
        # These will be caught by your FastAPI exception handlers
        raise e
    except Exception as e:
        # Generic fallback
        raise HTTPException(status_code=500, detail=f"Error processing the PDF: {str(e)}")
