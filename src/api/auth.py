from fastapi import Header, HTTPException, Depends
from typing import Optional
from .database import db


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> dict:
    """Verify API key from header and return user info."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    user_info = db.verify_api_key(x_api_key)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return user_info


def get_user_id(user_info: dict = Depends(verify_api_key)) -> str:
    """Extract user_id from verified API key."""
    return user_info["user_id"]

