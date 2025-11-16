from fastapi import APIRouter, Depends
from ..models import ContextRetrieveRequest, ContextRetrieveResponse
from ..auth import get_user_id
from ..gemini_service import gemini_service

router = APIRouter(tags=["context"])


@router.post("/context/retrieve", response_model=ContextRetrieveResponse)
async def retrieve_context(
    request: ContextRetrieveRequest,
    user_id: str = Depends(get_user_id)
):
    """Retrieve relevant context for a prompt using Gemini File Search."""
    try:
        result = gemini_service.retrieve_context(
            user_id=user_id,
            prompt=request.prompt,
            model=request.model
        )
        
        return ContextRetrieveResponse(
            enhanced_context=result["enhanced_context"],
            relevant_traces=result["relevant_traces"],
            suggestions=result["suggestions"]
        )
    except Exception as e:
        # Return empty context on error
        return ContextRetrieveResponse(
            enhanced_context=request.prompt,
            relevant_traces=[],
            suggestions={"error": str(e)}
        )

