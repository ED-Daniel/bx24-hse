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

    # Bitrix24 Retry Settings
    BITRIX24_RETRY_MAX_ATTEMPTS: int = 3
    BITRIX24_RETRY_DELAY: float = 1.0
    BITRIX24_RETRY_BACKOFF: float = 2.0

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_POLL_FORMS: int = 600  # 10 минут
    CACHE_TTL_EDUCATIONAL_PROGRAMS: int = 600  # 10 минут
    CACHE_TTL_CONTACTS: int = 300  # 5 минут
    CACHE_TTL_DEALS: int = 60  # 1 минута

    # Batch Operations Settings
    BATCH_ENABLED: bool = True
    BATCH_SIZE: int = 50  # Максимальный размер batch запроса к Bitrix24

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()
