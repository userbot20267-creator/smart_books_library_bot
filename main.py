"""
Main FastAPI Application Module
Entry point for the Smart Books Library Bot Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config.settings import settings
from app.database import init_db
from app.api import books_router, users_router, search_router, reviews_router, points_router
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Smart Books Library Bot Backend")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Books Library Bot Backend")


# Create FastAPI application
app = FastAPI(
    title="Smart Books Library Bot",
    description="API for Smart Books Library Bot on Telegram",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(books_router)
app.include_router(users_router)
app.include_router(search_router)
app.include_router(reviews_router)
app.include_router(points_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Smart Books Library Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Books Library Bot",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
        log_level=settings.log_level.lower()
    )
