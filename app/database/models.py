"""
Database Models
SQLAlchemy models for the Apollo AI application.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")

class File(Base):
    """File model for uploaded data files."""
    __tablename__ = "files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    rows_count = Column(Integer, nullable=False)
    columns_count = Column(Integer, nullable=False)
    columns = Column(JSON, nullable=False)  # List of column names
    file_type = Column(String(10), nullable=False)  # csv, xls, xlsx
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="files")
    analyses = relationship("Analysis", back_populates="file", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="file", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="file", cascade="all, delete-orphan")

class Analysis(Base):
    """Analysis model for storing analysis results."""
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # comprehensive, statistical, etc.
    summary = Column(JSON, nullable=False)  # DatasetSummary
    analysis_results = Column(JSON, nullable=False)  # Full analysis results
    processing_time = Column(Integer, nullable=False)  # Seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="analyses")
    user = relationship("User", back_populates="analyses")

class Visualization(Base):
    """Visualization model for storing chart data."""
    __tablename__ = "visualizations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    chart_type = Column(String(50), nullable=False)
    chart_data = Column(JSON, nullable=False)  # Chart.js compatible data
    chart_options = Column(JSON, nullable=True)  # Chart options
    chart_metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="visualizations")
    user = relationship("User", back_populates="visualizations")

class Insight(Base):
    """Insight model for storing AI-generated insights."""
    __tablename__ = "insights"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    llm_provider = Column(String(50), nullable=False)  # groq, openai, etc.
    insights_data = Column(JSON, nullable=False)  # InsightResult
    processing_time = Column(Integer, nullable=False)  # Seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="insights")
    user = relationship("User", back_populates="insights") 