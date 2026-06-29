"""
Central configuration for the Monika G Cafe backend.
Reads values from the .env file so secrets never get hard-coded.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from the backend folder
env_file = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "monika_g_cafe"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_VERIFY_SERVICE_SID: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "Monika G Cafe"

    # Frontend
    FRONTEND_URL: str = "http://localhost:5500"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_file_encoding='utf-8',
        extra="ignore"
    )

# Print debug info
print(f"[CONFIG] Loading .env from: {env_file}")
print(f"[CONFIG] .env exists: {env_file.exists()}")

settings = Settings()

# Debug: Print loaded config (without password)
print(f"[CONFIG] DB_HOST: {settings.DB_HOST}")
print(f"[CONFIG] DB_USER: {settings.DB_USER}")
print(f"[CONFIG] DB_NAME: {settings.DB_NAME}")
print(f"[CONFIG] DB_PASSWORD: {'*' * len(settings.DB_PASSWORD) if settings.DB_PASSWORD else 'EMPTY'}")