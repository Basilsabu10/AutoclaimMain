"""
Configuration settings for the AutoClaim server.
Loads environment variables and provides centralized settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Application settings loaded from environment variables."""
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "basil")  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/autoclaim.db")
    
    # AI Services
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Groq model (LLaMA 4 Scout Vision)
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    
    # Upload directory
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]


# Singleton settings instance
settings = Settings()
