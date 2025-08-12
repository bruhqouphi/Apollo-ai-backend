"""
Security Module
Handles JWT token management, password hashing, and security utilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user email."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        email = verify_token(credentials.credentials)
        if email is None:
            raise credentials_exception
        
        # Import here to avoid circular imports
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        user = await auth_service.get_user_by_email(email)
        
        if user is None:
            raise credentials_exception
        return user
        
    except JWTError:
        raise credentials_exception

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    import re
    # Remove any path separators and dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def validate_file_path(file_path: str) -> bool:
    """Validate file path to prevent path traversal attacks."""
    import os
    from pathlib import Path
    
    try:
        # Resolve the path to get absolute path
        resolved_path = Path(file_path).resolve()
        # Check if path is within allowed directory
        allowed_dir = Path(settings.UPLOAD_DIR).resolve()
        return str(resolved_path).startswith(str(allowed_dir))
    except Exception:
        return False

def rate_limit_key(request) -> str:
    """Generate rate limiting key based on client IP."""
    client_ip = request.client.host
    return f"rate_limit:{client_ip}"

def log_security_event(event_type: str, details: str, user_id: Optional[str] = None):
    """Log security-related events."""
    logger.warning(f"SECURITY_EVENT: {event_type} - {details} - User: {user_id or 'Unknown'}") 