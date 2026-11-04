from fastapi import APIRouter, Depends, HTTPException

from .. import models, schemas
from ..auth import get_current_user
from ..services import ai_matcher

router = APIRouter(prefix="/matcher", tags=["matcher"])


@router.post("", response_model=schemas.MatchResult)
def match(
    data: schemas.MatchRequest,
    user: models.User = Depends(get_current_user),
):
    try:
        result = ai_matcher.analyze_match(data.job_description, data.resume_text)
        return schemas.MatchResult(**result)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="AI service is not configured")
    except Exception:
        raise HTTPException(status_code=502, detail="AI service failed, please try again")