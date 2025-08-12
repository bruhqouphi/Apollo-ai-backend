"""
Files Router
Handles general file operations and management.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import FileInfo
from app.services.file_service import FileService
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["File Management"])

DEFAULT_USER_ID = "default-user-id"

@router.get("/", response_model=List[FileInfo])
async def list_files(
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """List all files for the current user."""
    try:
        file_service = FileService()
        files = await file_service.get_user_files(DEFAULT_USER_ID)
        
        logger.info(f"Retrieved {len(files)} files for default user")
        return files
        
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve files"
        )

@router.get("/{file_id}", response_model=FileInfo)
async def get_file(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get specific file information."""
    try:
        file_service = FileService()
        file_info = await file_service.get_file(file_id, DEFAULT_USER_ID)
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file"
        )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Delete a specific file."""
    try:
        file_service = FileService()
        await file_service.delete_file(file_id, DEFAULT_USER_ID)
        
        logger.info(f"File {file_id} deleted by default user")
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@router.get("/{file_id}/metadata")
async def get_file_metadata(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get detailed metadata for a file."""
    try:
        file_service = FileService()
        metadata = await file_service.get_file_metadata(file_id, DEFAULT_USER_ID)
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file metadata for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file metadata"
        ) 