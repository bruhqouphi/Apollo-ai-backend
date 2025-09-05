"""
Upload Router
Handles file upload operations with validation and security.
"""

import logging
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse

from app.models.schemas import UploadResponse, FileInfo
from app.services.upload_service import UploadService
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.config.settings import settings
from app.core.validation import validate_file_upload
from app.database.models import File

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["File Upload"])

DEFAULT_USER_ID = "default-user-id"

@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Upload a CSV/Excel file for analysis."""
    try:
        # Validate file
        validation_result = validate_file_upload(file)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["error"]
            )
        
        # Process upload
        upload_service = UploadService()
        # Use a default user ID for now (you can implement proper auth later)
        user_id = DEFAULT_USER_ID  # current_user.id if current_user else DEFAULT_USER_ID
        file_info = await upload_service.process_upload(file, user_id)
        
        logger.info(f"File uploaded successfully: {file_info.filename}")
        
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            timestamp=datetime.now(),
            file_id=file_info.file_id,
            filename=file_info.filename,
            file_size=file_info.file_size,
            file_size_bytes=file_info.file_size_bytes,
            rows_count=file_info.rows_count,
            columns_count=file_info.columns_count,
            columns=file_info.columns
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed. Please try again."
        )

@router.get("/files", response_model=List[FileInfo])
async def list_user_files(
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """List all files uploaded by the current user."""
    try:
        upload_service = UploadService()
        files = await upload_service.get_user_files(DEFAULT_USER_ID)
        
        logger.info(f"Retrieved {len(files)} files for default user")
        return files
        
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve files"
        )

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Delete a specific file."""
    try:
        upload_service = UploadService()
        await upload_service.delete_file(file_id, DEFAULT_USER_ID)
        
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

@router.get("/files/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get information about a specific file."""
    try:
        upload_service = UploadService()
        file_info = await upload_service.get_file_info(file_id, DEFAULT_USER_ID)
        return file_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file info for {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file information"
        )

@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Download a specific file."""
    try:
        upload_service = UploadService()

        # Verify file exists and belongs to user
        file_info = await upload_service.get_file_info(file_id, DEFAULT_USER_ID)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Get the actual file from database to get the file path
        from app.database.database import get_database
        db = next(get_database())
        file_record = db.query(File).filter(
            File.id == file_id,
            File.user_id == DEFAULT_USER_ID
        ).first()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )

        logger.info(f"File downloaded: {file_record.original_filename}")

        # Return file as response
        return FileResponse(
            path=file_path,
            filename=file_record.original_filename,
            media_type='text/csv'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        ) 