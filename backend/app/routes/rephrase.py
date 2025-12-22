"""rephrase_routes"""

from fastapi import APIRouter, HTTPException
from app.schemas.rephrase import RephraseRequest, RephraseResponse
from app.services.rephrase import rephrase_service, ValidationError

router = APIRouter()

@router.post("/rephrase", response_model=RephraseResponse)
async def rephrase_endpoint(req: RephraseRequest):
    try:
        return await rephrase_service(req)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")