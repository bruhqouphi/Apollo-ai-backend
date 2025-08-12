# app/config/settings.py
"""
Apollo AI Backend Configuration
Handles app settings, file validation rules, and environment configuration.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict

from pydantic_settings import BaseSettings

# Load environment variables from .env file
# load_dotenv() # This line is removed as per the new_code, as the dotenv import is removed.

class Settings(BaseSettings):
    # === APPLICATION SETTINGS ===
    APP_NAME: str = "Apollo AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # === SECURITY CONFIGURATION ===
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "apollo-ai-demo-secret-key-2024-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server  
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # API rate limiting (requests per minute)
    RATE_LIMIT: int = 100
    
    # Security headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # === DATABASE CONFIGURATION ===
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # === DIRECTORY PATHS ===
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    EXPORT_DIR: Path = BASE_DIR / "exports" 
    STATIC_DIR: Path = BASE_DIR / "static"
    
    # === FILE UPLOAD SETTINGS ===
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    file_size_mb: float = MAX_FILE_SIZE / (1024 * 1024)
    MAX_ROWS: int = 100000
    MIN_COLUMNS: int = 2
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xls", ".xlsx"]
    
    # === AI PROVIDER API KEYS ===
    # OpenAI API key
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Anthropic API key
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Groq API key (FREE tier - recommended)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # HuggingFace API key (FREE tier)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    
    # === DATA PROCESSING SETTINGS ===
    # Default analysis settings
    DEFAULT_CONFIDENCE_LEVEL: float = 0.95
    DEFAULT_OUTLIER_METHOD: str = "iqr"
    SIGNIFICANCE_LEVEL: float = 0.05
    
    # Chart generation settings
    DEFAULT_CHART_BINS: int = 20
    DEFAULT_CHART_TOP_N: int = 10
    MAX_CATEGORIES: int = 50  # Maximum number of categories for categorical analysis
    
    # AI insight settings
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_LLM_PROVIDER: str = "groq"  # Free and fast
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    # === METHODS ===
    def validate_file_extension(self, filename: str) -> bool:
        from pathlib import Path as _Path
        return _Path(filename).suffix.lower() in set(self.ALLOWED_EXTENSIONS)

    def validate_file_size(self, file_size: int) -> bool:
        return int(file_size) <= int(self.MAX_FILE_SIZE)

# Create settings instance
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