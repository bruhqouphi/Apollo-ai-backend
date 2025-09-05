"""
Apollo AI FastAPI Backend
Main application with modular architecture, authentication, and database integration.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import our custom modules
from app.config.settings import settings
from app.models.schemas import HealthResponse, ErrorResponse
from app.database.database import init_database, check_database_connection
from app.api.routers import (
    auth_router, upload_router, analysis_router,
    visualization_router, insights_router, files_router
)
from app.api.routers.enhanced_analysis import router as enhanced_analysis_router
from app.api.endpoints.visualization import router as smart_visualization_router

# Configure logging
try:
    # Try to create log file in the project directory
    log_file_path = Path(__file__).parent.parent / 'apollo_ai.log'
    file_handler = logging.FileHandler(log_file_path)
    handlers = [file_handler, logging.StreamHandler()]
except PermissionError:
    # Fallback to console-only logging if file permissions fail
    print("Warning: Cannot write to log file. Using console logging only.")
    handlers = [logging.StreamHandler()]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Intelligent no-code platform for data analysis and visualization",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (permissive for demo to fix preflight issues)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Trusted Host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # TODO: Configure with your actual domain in production
)

# Create required directories
for directory in [settings.UPLOAD_DIR, settings.EXPORT_DIR, settings.STATIC_DIR]:
    Path(directory).mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Include all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(enhanced_analysis_router, prefix="/api/v1")
app.include_router(visualization_router, prefix="/api/v1")  # Chart.js based - RE-ENABLED (uses matplotlib now)
# app.include_router(smart_visualization_router, prefix="/api/v1")  # Matplotlib based - DISABLED (conflicts with old router)
app.include_router(insights_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")

# Simple health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "message": "Apollo AI Backend is running",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        logger.info("Starting Apollo AI Backend...")
        
        # Initialize database
        init_database()
        
        # Check database connection
        if not check_database_connection():
            logger.error("Database connection failed")
            raise Exception("Database connection failed")
        
        logger.info("Apollo AI Backend started successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/api/v1/health")

@app.get("/api/v1/health", response_model=HealthResponse)
async def api_health_check():
    """API health check endpoint."""
    try:
        db_healthy = check_database_connection()
        return HealthResponse(
            status="healthy" if db_healthy else "unhealthy",
            message="Apollo AI Backend is running" if db_healthy else "Database connection failed",
            version=settings.VERSION,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            version=settings.VERSION,
            timestamp=datetime.now().isoformat()
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )