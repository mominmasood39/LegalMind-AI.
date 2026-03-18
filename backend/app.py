"""LegalMind-AI FastAPI application."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.config import settings
from backend.models.schemas import (
    LegalQueryRequest,
    LegalQueryResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    CaseResearchRequest,
    CaseResearchResponse,
    HealthResponse,
)
from backend.services.legal_assistant import get_legal_answer
from backend.services.document_analyzer import analyse_document
from backend.services.case_researcher import research_case

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered legal assistance platform for the LegalMind FYP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Return API health status."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        demo_mode=settings.demo_mode,
    )


# ---------------------------------------------------------------------------
# Legal Q&A
# ---------------------------------------------------------------------------


@app.post("/api/legal-query", response_model=LegalQueryResponse, tags=["Legal AI"])
async def legal_query(request: LegalQueryRequest):
    """Answer a legal question using the AI assistant."""
    result = await get_legal_answer(
        query=request.query,
        history=[m.model_dump() for m in request.history],
        jurisdiction=request.jurisdiction,
    )
    return LegalQueryResponse(**result)


# ---------------------------------------------------------------------------
# Document analysis
# ---------------------------------------------------------------------------


@app.post("/api/analyse-document", response_model=DocumentAnalysisResponse, tags=["Documents"])
async def analyse_document_endpoint(request: DocumentAnalysisRequest):
    """Analyse a legal document provided as text."""
    result = await analyse_document(
        document_text=request.document_text,
        analysis_type=request.analysis_type,
    )
    return DocumentAnalysisResponse(**result)


@app.post("/api/upload-document", response_model=DocumentAnalysisResponse, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """Upload and analyse a legal document (TXT, PDF text extraction)."""
    max_bytes = settings.max_document_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_document_size_mb} MB.",
        )

    filename = file.filename or ""
    if filename.endswith(".pdf"):
        try:
            import io
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Failed to read PDF: {exc}")
    elif filename.endswith(".docx"):
        try:
            import io
            from docx import Document

            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Failed to read DOCX: {exc}")
    else:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

    if not text.strip():
        raise HTTPException(status_code=422, detail="Document appears to be empty or unreadable.")

    result = await analyse_document(document_text=text, analysis_type="general")
    return DocumentAnalysisResponse(**result)


# ---------------------------------------------------------------------------
# Case research
# ---------------------------------------------------------------------------


@app.post("/api/case-research", response_model=CaseResearchResponse, tags=["Research"])
async def case_research(request: CaseResearchRequest):
    """Perform legal case research for a given query."""
    result = await research_case(
        query=request.query,
        jurisdiction=request.jurisdiction or "general",
        case_type=request.case_type or "all",
    )
    return CaseResearchResponse(**result)


# ---------------------------------------------------------------------------
# Serve frontend static files (production mode)
# ---------------------------------------------------------------------------

_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(_frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "LegalMind-AI API is running. See /docs for API documentation."}
