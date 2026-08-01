from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.auth import require_api_key
from app.schemas import ParseResumeResponse
from app.services.resume_parser import ResumeParsingError, parse_resume_text
from app.services.text_extractor import TextExtractionError, extract_text

router = APIRouter(prefix="/api", tags=["resume"], dependencies=[Depends(require_api_key)])


@router.post("/parse-resume", response_model=ParseResumeResponse)
async def parse_resume(file: UploadFile):
    data = await file.read()

    try:
        text = extract_text(data, file.filename or "")
    except TextExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc

    try:
        result = parse_resume_text(text)
    except ResumeParsingError as exc:
        raise HTTPException(502, str(exc)) from exc

    return ParseResumeResponse(**result)
