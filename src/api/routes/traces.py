from fastapi import APIRouter, Depends
from ..models import TraceStoreRequest, TraceStoreResponse
from ..auth import get_user_id
from ..gemini_service import gemini_service
from ..database import db
import uuid

router = APIRouter(tags=["traces"])


@router.post("/traces/store", response_model=TraceStoreResponse)
async def store_trace(
    request: TraceStoreRequest,
    user_id: str = Depends(get_user_id)
):
    """Store a trace in Gemini File Search and Supabase."""
    try:
        # Prepare trace data
        trace_data = {
            "input": request.input.dict(),
            "output": request.output.dict(),
            "metadata": request.metadata.dict()
        }
        
        # Store in Gemini File Search
        trace_id = gemini_service.store_trace(user_id, trace_data)
        
        # Store metadata in Supabase
        db.store_trace_metadata(
            user_id=user_id,
            trace_id=trace_id,
            metadata={
                "provider": request.metadata.provider,
                "model": request.metadata.model,
                "success": request.metadata.success,
                "tokens_used": request.output.tokens_used,
                "latency_ms": request.metadata.latency_ms
            }
        )
        
        return TraceStoreResponse(
            trace_id=trace_id,
            stored=True
        )
    except Exception as e:
        # Return error response
        return TraceStoreResponse(
            trace_id=str(uuid.uuid4()),
            stored=False
        )

