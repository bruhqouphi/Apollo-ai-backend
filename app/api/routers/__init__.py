"""
API Routers Package
Contains all FastAPI router modules for organized endpoint management.
"""

from .auth import router as auth_router
from .upload import router as upload_router
from .analysis import router as analysis_router
from .visualization import router as visualization_router
from .insights import router as insights_router
from .files import router as files_router

__all__ = [
    "auth_router",
    "upload_router", 
    "analysis_router",
    "visualization_router",
    "insights_router",
    "files_router"
] 