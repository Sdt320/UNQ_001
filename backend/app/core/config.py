"""Application configuration settings using Pydantic Settings."""

import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FieldMind AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & Tokens
    SECRET_KEY: str = "fieldmind_super_secret_jwt_and_encryption_key_change_in_prod_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INTERNAL_SERVICE_KEY: str = "fieldmind_internal_microservice_secret_token_2026"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fieldmind_user:fieldmind_secure_password_2026@localhost:5432/fieldmind_db"
    DATABASE_URL_SYNC: str = "postgresql://fieldmind_user:fieldmind_secure_password_2026@localhost:5432/fieldmind_db"

    # Redis Cache & Mutex
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery Task Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # OpenAI & LLM Services
    OPENAI_API_KEY: str = "sk-fake-fieldmind-openai-key-for-local-demo"
    OPENAI_MODEL: str = "gpt-4o-mini"
    WHISPER_MODEL: str = "whisper-1"

    # WhatsApp Cloud API
    WHATSAPP_API_TOKEN: str = "EAAG_fake_whatsapp_meta_token_fieldmind"
    WHATSAPP_PHONE_NUMBER_ID: str = "109283746592837"
    WHATSAPP_VERIFY_TOKEN: str = "FIELDMIND_SECURE_TOKEN_2026"
    WHATSAPP_API_VERSION: str = "v20.0"

    # Stripe Connect & Escrow
    STRIPE_SECRET_KEY: str = "sk_test_fake_fieldmind_stripe_secret_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_fake_fieldmind_stripe_webhook_secret"
    PLATFORM_FEE_PERCENTAGE: float = 15.0
    TECHNICIAN_PAYOUT_PERCENTAGE: float = 85.0

    # MinIO / S3 Storage
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "fieldmind-invoices"
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
