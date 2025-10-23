from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for application startup and shutdown"""
    # Startup
    print("🚀 Starting HAA-Gaia Backend...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")

    yield

    # Shutdown
    print("👋 Shutting down HAA-Gaia Backend...")


app = FastAPI(
    title="HAA-Gaia API",
    description="Modular Virtualization Orchestration Suite - API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "HAA-Gaia",
        "version": "0.1.0",
        "description": "Modular Virtualization Orchestration Suite",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HAA-Gaia Backend"
    }
