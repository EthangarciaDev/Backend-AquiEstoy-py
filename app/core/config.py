# app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración global de la aplicación"""
    
    # General
    APP_NAME: str = "Backend-AquiEstoy"
    DEBUG: bool = True
    
    # AWS
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-2")
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "")
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = 'ignore'

settings = Settings()
