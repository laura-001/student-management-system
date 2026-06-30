#Core Configuration
#Loads all Environment Variables from .env

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    #Database
    DATABASE_URL: str = ""

    #JWT Authentication
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #APP
    APP_NAME: str = "Student Course Registration System "
    DEBUG : bool = False
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

#single instance used across the app
settings = Settings()
