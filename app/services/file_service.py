"""
File Service
Handles general file operations and management.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pathlib import Path

from app.database.database import get_database
from app.database.models import File, User
from app.models.schemas import FileInfo

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling general file operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def get_user_files(self, user_id: str) -> List[FileInfo]:
        """Get all files for a user."""
        try:
            files = self.db.query(File).filter(
                File.user_id == user_id
            ).order_by(File.upload_time.desc()).all()
            
            return [
                FileInfo(
                    file_id=file.id,
                    filename=file.original_filename,
                    file_size=self._format_file_size(file.file_size),
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
    
    async def get_file(self, file_id: str, user_id: str) -> Optional[FileInfo]:
        """Get specific file information."""
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
                rows_count=file.rows_count,
                columns_count=file.columns_count,
                columns=file.columns,
                upload_time=file.upload_time,
                user_id=file.user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to get file: {str(e)}")
            return None
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a specific file."""
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
    
    async def get_file_metadata(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a file."""
        try:
            file = self.db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            if not file:
                return None
            
            # Check if file exists on disk
            file_path = Path(file.file_path)
            file_exists = file_path.exists()
            
            return {
                "file_id": file.id,
                "filename": file.original_filename,
                "file_size": self._format_file_size(file.file_size),
                "file_type": file.file_type,
                "rows_count": file.rows_count,
                "columns_count": file.columns_count,
                "columns": file.columns,
                "upload_time": file.upload_time,
                "file_exists": file_exists,
                "file_path": str(file_path) if file_exists else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {str(e)}")
            return None
    
    async def get_file_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get file statistics for a user."""
        try:
            files = self.db.query(File).filter(File.user_id == user_id).all()
            
            if not files:
                return {
                    "total_files": 0,
                    "total_size": "0 B",
                    "total_rows": 0,
                    "file_types": {},
                    "average_columns": 0
                }
            
            total_files = len(files)
            total_size_bytes = sum(file.file_size for file in files)
            total_rows = sum(file.rows_count for file in files)
            
            # Count file types
            file_types = {}
            for file in files:
                file_type = file.file_type
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # Calculate average columns
            total_columns = sum(file.columns_count for file in files)
            average_columns = total_columns / total_files if total_files > 0 else 0
            
            return {
                "total_files": total_files,
                "total_size": self._format_file_size(total_size_bytes),
                "total_rows": total_rows,
                "file_types": file_types,
                "average_columns": round(average_columns, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get file statistics: {str(e)}")
            return {
                "total_files": 0,
                "total_size": "0 B",
                "total_rows": 0,
                "file_types": {},
                "average_columns": 0
            }
    
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