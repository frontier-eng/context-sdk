from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .gemini_service import gemini_service
from .routes import context, traces, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    # Initialize Gemini File Search store
    gemini_service.initialize()
    yield
    # Cleanup if needed


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(context.router, prefix=settings.api_prefix)
app.include_router(traces.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Context API",
        "status": "healthy",
        "version": settings.api_version
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

