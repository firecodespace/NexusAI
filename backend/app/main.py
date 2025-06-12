"""
FastAPI Application Entrypoint

This module serves as the main entry point for the FastAPI application:
- Application initialization
- Middleware configuration
- Route registration
- Error handling setup
- API documentation configuration

Author: Shared
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.v1.endpoints.invoices import router as invoices_router

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NexusAI API",
    description="AI-powered finance automation platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoices_router, prefix="/api/v1/invoices", tags=["Invoices"])

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {
        "message": "Welcome to NexusAI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/test")
async def test():
    logger.debug("Test endpoint called")
    return {"status": "API is working"}