"""
Validation Module
Handles input validation, sanitization, and security checks.
"""

import logging
import re
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from pathlib import Path

from app.config.settings import settings
from app.core.security import sanitize_filename

logger = logging.getLogger(__name__)

def validate_file_upload(file: UploadFile) -> Dict[str, Any]:
    """
    Comprehensive file upload validation.
    
    Returns:
        Dict with 'valid' boolean and 'error' string if invalid
    """
    try:
        # Check if file is provided
        if not file:
            return {"valid": False, "error": "No file provided"}
        
        # Validate filename
        if not file.filename or len(file.filename.strip()) == 0:
            return {"valid": False, "error": "Invalid filename"}
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(file.filename)
        if sanitized_filename != file.filename:
            return {"valid": False, "error": "Filename contains invalid characters"}
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return {
                "valid": False, 
                "error": f"File type {file_ext} not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            }
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            return {
                "valid": False, 
                "error": f"File too large. Maximum size is {settings.file_size_mb:.1f} MB"
            }
        
        # Check for empty file
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        # Check content type for basic validation
        if file.content_type:
            allowed_content_types = [
                "text/csv",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/octet-stream"  # Some systems send this for CSV
            ]
            if file.content_type not in allowed_content_types:
                logger.warning(f"Unexpected content type: {file.content_type} for file {file.filename}")
        
        return {"valid": True, "error": None}
        
    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        return {"valid": False, "error": "File validation failed"}

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def sanitize_string(input_string: str, max_length: int = 1000) -> str:
    """Sanitize string input to prevent XSS and injection attacks."""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_file_id(file_id: str) -> bool:
    """Validate file ID format."""
    # UUID format validation
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, file_id, re.IGNORECASE))

def validate_chart_type(chart_type: str) -> bool:
    """Validate chart type."""
    allowed_types = [
        "histogram", "boxplot", "bar", "scatter", "heatmap", 
        "line", "pie", "area", "doughnut"
    ]
    return chart_type.lower() in allowed_types

def validate_column_names(columns: list) -> bool:
    """Validate column names for security."""
    if not columns:
        return False
    
    for column in columns:
        if not isinstance(column, str):
            return False
        if len(column) > 100:  # Reasonable limit
            return False
        # Check for potentially dangerous patterns
        if re.search(r'[<>"\']', column):
            return False
    
    return True

def validate_analysis_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate analysis request parameters."""
    errors = []
    
    # Check required fields
    if not request_data.get("file_id"):
        errors.append("file_id is required")
    
    # Validate file_id format
    if request_data.get("file_id") and not validate_file_id(request_data["file_id"]):
        errors.append("Invalid file_id format")
    
    # Validate boolean fields
    boolean_fields = ["include_correlation", "include_outliers", "include_statistical_tests"]
    for field in boolean_fields:
        if field in request_data and not isinstance(request_data[field], bool):
            errors.append(f"{field} must be a boolean")
    
    # Validate confidence level
    confidence = request_data.get("confidence_level")
    if confidence is not None:
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append("confidence_level must be between 0 and 1")
    
    # Validate target columns
    target_columns = request_data.get("target_columns")
    if target_columns is not None:
        if not isinstance(target_columns, list):
            errors.append("target_columns must be a list")
        elif not validate_column_names(target_columns):
            errors.append("Invalid column names in target_columns")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def log_validation_error(validation_type: str, details: str, user_id: Optional[str] = None):
    """Log validation errors for security monitoring."""
    logger.warning(f"VALIDATION_ERROR: {validation_type} - {details} - User: {user_id or 'Unknown'}") 