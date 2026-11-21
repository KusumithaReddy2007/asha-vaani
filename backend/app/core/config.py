import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    APP_NAME: str = "ASHA-VAANI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    SECRET_KEY: str = "asha_vaani_super_secret_hackathon_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite:///./asha_vaani.db"

    # Official Gnani API Platform
    GNANI_API_KEY: Optional[str] = None
    GNANI_STT_MODEL: str = "Prisma-v3.0"
    GNANI_TTS_MODEL: str = "Timbre-v3.0"
    GNANI_WS_URL: str = "wss://api.gnani.ai/v3/speech/stream"
    GNANI_TTS_URL: str = "https://api.gnani.ai/v3/speech/synthesize"
    GNANI_LANGUAGE_CODE: str = "en-IN"

    # AI Extraction
    LLM_PROVIDER: str = "local"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    # Privacy Policy
    AUDIO_RETENTION_ENABLED: bool = False
    AUDIO_RETENTION_DAYS: int = 0
    LOG_AUDIO_METRICS: bool = True

settings = Settings()
