from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Request/Response Models

class ContextRetrieveRequest(BaseModel):
    """Request model for context retrieval."""
    prompt: str
    system_prompt: Optional[str] = None
    provider: str  # e.g., "openai", "anthropic"
    model: str  # e.g., "gpt-4", "claude-3-5-sonnet"


class ContextRetrieveResponse(BaseModel):
    """Response model for context retrieval."""
    enhanced_context: str
    relevant_traces: List[Dict[str, Any]]
    suggestions: Dict[str, Any]


class TraceInput(BaseModel):
    """Input data for a trace."""
    prompt: str
    system_prompt: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TraceOutput(BaseModel):
    """Output data from a trace."""
    text: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None


class TraceMetadata(BaseModel):
    """Metadata for a trace."""
    provider: str
    model: str
    success: bool = True
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class TraceStoreRequest(BaseModel):
    """Request model for storing a trace."""
    input: TraceInput
    output: TraceOutput
    metadata: TraceMetadata


class TraceStoreResponse(BaseModel):
    """Response model for trace storage."""
    trace_id: str
    stored: bool


class CreateAPIKeyRequest(BaseModel):
    """Request model for creating an API key."""
    email: str


class CreateAPIKeyResponse(BaseModel):
    """Response model for API key creation."""
    api_key: str
    user_id: str

