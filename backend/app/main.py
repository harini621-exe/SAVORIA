"""
SAVORIA FastAPI Application Entry Point
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import get_settings
from app.rag.retriever import recipe_rag

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup: pre-load FAISS index."""
    logger.info("SAVORIA backend starting up...")

    # Ensure data directory exists relative to backend root
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Pre-build/load FAISS index at startup for fast first request
    try:
        recipe_rag.ensure_loaded()
        logger.info(f"RAG index ready: {len(recipe_rag.recipes)} recipes loaded")
    except Exception as e:
        logger.error(f"Failed to load RAG index at startup: {e}")

    if not settings.IBM_API_KEY or not settings.IBM_PROJECT_ID:
        logger.warning(
            "IBM watsonx.ai credentials not configured. "
            "Set IBM_API_KEY and IBM_PROJECT_ID in .env to enable AI generation. "
            "RAG-based fallback recipes are still available."
        )
    else:
        logger.info("IBM watsonx.ai credentials detected.")

    yield
    logger.info("SAVORIA backend shutting down.")


app = FastAPI(
    title="SAVORIA API",
    description="AI-Powered RAG-Based Intelligent Recipe Preparation Agent",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React frontend, Vite dev server, and file:// (null origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "null",  # file:// origin used when opening the HTML file directly
    ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount all API routes under /api
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "SAVORIA API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }
