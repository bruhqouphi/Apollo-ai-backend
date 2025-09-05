"""
Upload Service
Handles file upload processing, validation, and database storage.
"""

import logging
import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
import pandas as pd

from app.database.database import get_database
from app.database.models import File, User
from app.core.validation import validate_file_upload
from app.core.security import sanitize_filename
from app.config.settings import settings
from app.models.schemas import FileInfo

logger = logging.getLogger(__name__)

class UploadService:
    """Service for handling file upload operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def process_upload(self, file: UploadFile, user_id: str) -> FileInfo:
        """Process file upload and store in database."""
        try:
            # Validate file
            validation_result = validate_file_upload(file)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation_result["error"]
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix.lower()
            safe_filename = sanitize_filename(file.filename)
            unique_filename = f"{file_id}{file_ext}"
            
            # Create file path
            file_path = settings.UPLOAD_DIR / unique_filename
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Read file to get metadata
            df = await self._read_file(file_path, file_ext)
            
            # Store in database
            db_file = File(
                id=file_id,
                user_id=user_id,
                filename=unique_filename,
                original_filename=safe_filename,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                rows_count=len(df),
                columns_count=len(df.columns),
                columns=df.columns.tolist(),
                file_type=file_ext[1:]  # Remove the dot
            )
            
            self.db.add(db_file)
            self.db.commit()
            self.db.refresh(db_file)
            
            logger.info(f"File uploaded successfully: {safe_filename} ({len(df)} rows, {len(df.columns)} columns)")
            
            return FileInfo(
                file_id=db_file.id,
                filename=db_file.original_filename,
                file_size=self._format_file_size(db_file.file_size),
                file_size_bytes=db_file.file_size,
                rows_count=db_file.rows_count,
                columns_count=db_file.columns_count,
                columns=db_file.columns,
                upload_time=db_file.upload_time,
                user_id=db_file.user_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up file if it was created
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            
            self.db.rollback()
            logger.error(f"File upload processing failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload processing failed"
            )
    
    async def _read_file(self, file_path: Path, file_ext: str) -> pd.DataFrame:
        """Read file and return DataFrame."""
        try:
            if file_ext == '.csv':
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not read CSV file with any encoding")
                    
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Basic validation
            if df.empty:
                raise ValueError("File is empty")
            
            if len(df.columns) < settings.MIN_COLUMNS:
                raise ValueError(f"File must have at least {settings.MIN_COLUMNS} columns")
            
            if len(df) > settings.MAX_ROWS:
                logger.warning(f"File has {len(df)} rows, limiting to {settings.MAX_ROWS}")
                df = df.head(settings.MAX_ROWS)
            
            return df
            
        except Exception as e:
            logger.error(f"File reading failed: {str(e)}")
            raise ValueError(f"Failed to read file: {str(e)}")
    
    async def get_user_files(self, user_id: str) -> List[FileInfo]:
        """Get all files for a user."""
        try:
            files = self.db.query(File).filter(File.user_id == user_id).order_by(File.upload_time.desc()).all()
            
            return [
                FileInfo(
                    file_id=file.id,
                    filename=file.original_filename,
                    file_size=self._format_file_size(file.file_size),
                    file_size_bytes=file.file_size,
                    rows_count=file.rows_count,
                    columns_count=file.columns_count,
                    columns=file.columns,
                    upload_time=file.upload_time,
                    user_id=file.user_id
                )
                for file in files
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user files: {str(e)}")
            return []
    
    async def get_file_info(self, file_id: str, user_id: str) -> Optional[FileInfo]:
        """Get file information by ID."""
        try:
            file = self.db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            if not file:
                return None
            
            return FileInfo(
                file_id=file.id,
                filename=file.original_filename,
                file_size=self._format_file_size(file.file_size),
                file_size_bytes=file.file_size,
                rows_count=file.rows_count,
                columns_count=file.columns_count,
                columns=file.columns,
                upload_time=file.upload_time,
                user_id=file.user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return None
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file from database and disk."""
        try:
            file = self.db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Delete from disk
            file_path = Path(file.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            self.db.delete(file)
            self.db.commit()
            
            logger.info(f"File deleted: {file.original_filename}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"File deletion failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File deletion failed"
            )
    
    async def verify_file_ownership(self, file_id: str, user_id: str) -> bool:
        """Verify that a file belongs to a user."""
        try:
            file = self.db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            return file is not None
            
        except Exception as e:
            logger.error(f"File ownership verification failed: {str(e)}")
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}" 