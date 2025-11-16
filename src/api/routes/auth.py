from fastapi import APIRouter, HTTPException
from ..models import CreateAPIKeyRequest, CreateAPIKeyResponse
from ..database import db

router = APIRouter(tags=["auth"])


@router.post("/auth/create-key", response_model=CreateAPIKeyResponse)
async def create_api_key(request: CreateAPIKeyRequest):
    """Create a new API key for a user. Creates user if they don't exist."""
    try:
        # Get or create user
        user = db.get_or_create_user(request.email)
        
        # Create API key
        api_key, _ = db.create_api_key(user["id"])
        
        return CreateAPIKeyResponse(
            api_key=api_key,
            user_id=user["id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")

