"""
Authentication Router
Handles user authentication, JWT token management, and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from app.models.schemas import User, UserCreate, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token, verify_password
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        auth_service = AuthService()
        user = await auth_service.create_user(user_data)
        access_token = create_access_token(data={"sub": user.email})
        
        logger.info(f"User registered successfully: {user.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email may already be registered."
        )

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Authenticate user and return JWT token."""
    try:
        auth_service = AuthService()
        user = await auth_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email})
        
        logger.info(f"User logged in successfully: {user.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.get("/me", response_model=User)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current authenticated user information."""
    try:
        auth_service = AuthService()
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Refresh JWT token."""
    try:
        auth_service = AuthService()
        new_token = await auth_service.refresh_token(credentials.credentials)
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and invalidate token."""
    try:
        auth_service = AuthService()
        await auth_service.logout(credentials.credentials)
        logger.info("User logged out successfully")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        ) 