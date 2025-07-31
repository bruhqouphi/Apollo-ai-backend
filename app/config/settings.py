 
# app/config/settings.py
"""
Apollo AI Backend Configuration
Handles app settings, file validation rules, and environment configuration.
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Centralized configuration for Apollo AI backend.
    Manages file validation, storage paths, and app settings.
    """
    
    # === APP CONFIGURATION ===
    APP_NAME: str = "Apollo AI Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # === AI API KEYS ===
    # OpenAI API key for LLM integration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Groq API key (FREE - 1000 requests/day, very fast)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Anthropic API key (FREE tier available)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # HuggingFace API key (FREE tier)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    
    # === DIRECTORY PATHS ===
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    EXPORT_DIR: Path = BASE_DIR / "exports" 
    STATIC_DIR: Path = BASE_DIR / "static"
    
    # === FILE VALIDATION SETTINGS ===
    # Allowed file extensions
    ALLOWED_EXTENSIONS: List[str] = [".csv"]
    
    # Maximum file size (in bytes) - 50MB default
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Maximum number of rows to process
    MAX_ROWS: int = 100000
    
    # Required CSV columns (minimum)
    MIN_COLUMNS: int = 2
    
    # === API CONFIGURATION ===
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server  
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # API rate limiting (requests per minute)
    RATE_LIMIT: int = 100
    
    # === DATA PROCESSING SETTINGS ===
    # Statistical significance level
    SIGNIFICANCE_LEVEL: float = 0.05
    
    # Maximum categories for categorical analysis
    MAX_CATEGORIES: int = 50
    
    # Outlier detection method ('iqr' or 'zscore')
    OUTLIER_METHOD: str = "iqr"
    
    # === AI PROVIDER SETTINGS ===
    # Default AI provider for insights
    DEFAULT_AI_PROVIDER: str = "groq"  # Groq is free and very fast
    
    # AI provider priority list (fallback order)
    AI_PROVIDER_PRIORITY: List[str] = [
        "groq",        # FREE - 1000 requests/day, fastest
        "anthropic",   # FREE tier available, very good quality
        "openai",      # Paid but reliable
        "huggingface", # FREE tier, open source models
        "ollama",      # FREE - runs locally
        "fallback"     # Rule-based fallback
    ]
    
    # Missing value threshold (% of missing values to flag column)
    MISSING_VALUE_THRESHOLD: float = 0.5  # 50%
    
    def __init__(self):
        """Initialize settings and create necessary directories."""
        self.create_directories()
    
    def create_directories(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [self.UPLOAD_DIR, self.EXPORT_DIR, self.STATIC_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate_file_extension(self, filename: str) -> bool:
        """
        Validate if file has allowed extension.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            bool: True if extension is allowed
        """
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.ALLOWED_EXTENSIONS
    
    def validate_file_size(self, file_size: int) -> bool:
        """
        Validate if file size is within limits.
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            bool: True if file size is acceptable
        """
        return file_size <= self.MAX_FILE_SIZE
    
    def get_upload_path(self, filename: str) -> Path:
        """
        Get full path for uploaded file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Path: Full path where file should be stored
        """
        return self.UPLOAD_DIR / filename
    
    def get_export_path(self, filename: str) -> Path:
        """
        Get full path for exported file.
        
        Args:
            filename: Name of the export file
            
        Returns:
            Path: Full path where export should be stored
        """
        return self.EXPORT_DIR / filename
    
    @property
    def file_size_mb(self) -> float:
        """Get maximum file size in MB for user display."""
        return self.MAX_FILE_SIZE / (1024 * 1024)


# === GLOBAL SETTINGS INSTANCE ===
settings = Settings()


# === UTILITY FUNCTIONS ===
def format_file_size(size_bytes: int) -> str:
    """
    Convert file size from bytes to human readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "2.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def is_valid_csv_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
    """
    Comprehensive CSV file validation.
    
    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check extension
    if not settings.validate_file_extension(filename):
        return False, f"Invalid file type. Only {', '.join(settings.ALLOWED_EXTENSIONS)} files are allowed."
    
    # Check file size
    if not settings.validate_file_size(file_size):
        return False, f"File too large. Maximum size is {settings.file_size_mb:.1f} MB."
    
    # Check filename
    if not filename or len(filename.strip()) == 0:
        return False, "Filename cannot be empty."
    
    return True, None