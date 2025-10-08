from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    # Application Settings
    APP_NAME: str = "FastAPI Project"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fastapi_db"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/fastapi_db"

    # Security
    SECRET_KEY: str = "change-this-secret-key"

    # Bitrix24 Settings
    BITRIX24_WEBHOOK_URL: str = "https://your-domain.bitrix24.ru/rest/1/your-webhook-token/"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()
