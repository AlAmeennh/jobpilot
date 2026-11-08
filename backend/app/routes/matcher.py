import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from .. import models, schemas
from ..auth import get_current_user
from ..services import ai_matcher, pdf_reader

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/matcher", tags=["matcher"])

MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB


def run_match(job_description: str, resume_text: str) -> schemas.MatchResult:
    try:
        result = ai_matcher.analyze_match(job_description, resume_text)
        return schemas.MatchResult(**result)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="AI service is not configured")
    except Exception:
        logger.exception("Matcher failed")
        raise HTTPException(status_code=502, detail="AI service failed, please try again")


@router.post("", response_model=schemas.MatchResult)
def match(
    data: schemas.MatchRequest,
    user: models.User = Depends(get_current_user),
):
    return run_match(data.job_description, data.resume_text)


@router.post("/upload", response_model=schemas.MatchResult)
def match_pdf(
    job_description: str = Form(..., min_length=30),
    resume: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
):
    content = resume.file.read(MAX_PDF_BYTES + 1)
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF is too large (max 5 MB)")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    try:
        resume_text = pdf_reader.extract_text(content)
    except pdf_reader.PdfReadError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return run_match(job_description, resume_text)