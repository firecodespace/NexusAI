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
from app.api.v1.endpoints.invoice_upload import router as invoice_upload_router

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NexusAI API",
    description="AI-powered finance automation platform",
    version="1.0.0"
)

app.include_router(invoice_upload_router, prefix="/invoices", tags=["Invoices"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include router
try:
    from .api.gst import router as gst_router
    logger.debug("Successfully imported GST router")
    app.include_router(gst_router)
    logger.debug("Successfully included GST router")
except Exception as e:
    logger.error(f"Error importing or including router: {str(e)}")

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {
        "message": "Welcome to NexusAI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Add a test endpoint
@app.get("/test")
async def test():
    logger.debug("Test endpoint called")
    return {"status": "API is working"}