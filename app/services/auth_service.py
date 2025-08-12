"""
Authentication Service
Handles user authentication, registration, and JWT token management.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database.database import get_database
from app.database.models import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.validation import validate_email, validate_password
from app.models.schemas import UserCreate, UserLogin

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user account."""
        try:
            # Validate email
            if not validate_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            # Validate password
            password_validation = validate_password(user_data.password)
            if not password_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password validation failed: {'; '.join(password_validation['errors'])}"
                )
            
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created successfully: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"User creation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is disabled"
                )
            
            logger.info(f"User authenticated successfully: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        try:
            from app.core.security import verify_token
            email = verify_token(token)
            if email is None:
                return None
            
            user = await self.get_user_by_email(email)
            return user
            
        except Exception as e:
            logger.error(f"Failed to get current user: {str(e)}")
            return None
    
    async def refresh_token(self, token: str) -> str:
        """Refresh JWT token."""
        try:
            from app.core.security import verify_token
            email = verify_token(token)
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Create new token
            new_token = create_access_token(data={"sub": email})
            return new_token
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    async def logout(self, token: str) -> bool:
        """Logout user (invalidate token)."""
        try:
            # In a production environment, you would add the token to a blacklist
            # For now, we'll just log the logout event
            from app.core.security import verify_token
            email = verify_token(token)
            if email:
                logger.info(f"User logged out: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
    
    async def update_user_profile(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user profile information."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Update allowed fields
            if "full_name" in kwargs:
                user.full_name = kwargs["full_name"]
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User profile updated: {user.email}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Profile update failed: {str(e)}")
            return None
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                return False
            
            # Validate new password
            password_validation = validate_password(new_password)
            if not password_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password validation failed: {'; '.join(password_validation['errors'])}"
                )
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            self.db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Password change failed: {str(e)}")
            return False 