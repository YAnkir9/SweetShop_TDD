from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api", tags=["sweets"])

@router.get("/sweets", status_code=status.HTTP_200_OK)
async def get_sweets(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "message": "Successfully authenticated",
        "user_id": current_user.id,
        "user_email": current_user.email,
        "sweets": []
    }
