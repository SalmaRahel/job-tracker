from fastapi import HTTPException, APIRouter, Depends
from .schemas import JDExtraction, JDExtractionRequest
from .service import extract_jd
from ..database import get_db    
from sqlalchemy.orm import Session
from ..auth.models import User
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/jd-analysis", tags=["jd-analysis"])

@router.post("", response_model=JDExtraction, status_code=201)
def create_jd_extraction(request: JDExtractionRequest, user: User=Depends(get_current_user)):
    try:
        extracted_jd = extract_jd(request.jd_text)
    except ValueError as e:
        raise HTTPException(422, detail=str(e))
    return extracted_jd
    