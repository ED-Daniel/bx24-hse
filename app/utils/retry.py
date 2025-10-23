"""
Модуль для retry-логики запросов к Bitrix24 API

Автоматически повторяет запросы при временных ошибках.
"""

import time
import logging
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps

logger = logging.getLogger(__name__)


class RetryException(Exception):
    """Исключение для ошибок retry-логики"""
    pass


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Декоратор для автоматического повтора при ошибках

    Args:
        max_attempts: Максимальное количество попыток (default: 3)
        delay: Начальная задержка между попытками в секундах (default: 1.0)
        backoff: Множитель для увеличения задержки (default: 2.0)
        exceptions: Типы исключений для retry (default: все Exception)
        on_retry: Callback функция, вызываемая перед каждой повторной попыткой

    Example:
        @retry_on_error(max_attempts=5, delay=2.0, backoff=2.0)
        def make_api_request():
            # код запроса
            pass

    Retry strategy:
        - Attempt 1: Immediate
        - Attempt 2: delay (1s)
        - Attempt 3: delay * backoff (2s)
        - Attempt 4: delay * backoff^2 (4s)
        - etc.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    # Пытаемся выполнить функцию
                    result = func(*args, **kwargs)

                    # Если не первая попытка - логируем успех
                    if attempt > 1:
                        logger.info(
                            f"✅ {func.__name__} успешно выполнена с попытки {attempt}/{max_attempts}"
                        )

                    return result

                except exceptions as e:
                    last_exception = e

                    # Последняя попытка - не ретраим
                    if attempt == max_attempts:
                        logger.error(
                            f"❌ {func.__name__} провалена после {max_attempts} попыток. "
                            f"Последняя ошибка: {str(e)}"
                        )
                        break

                    # Логируем ошибку и ретрай
                    logger.warning(
                        f"⚠️ {func.__name__} попытка {attempt}/{max_attempts} провалена: {str(e)}. "
                        f"Повтор через {current_delay:.1f}s..."
                    )

                    # Вызываем callback если есть
                    if on_retry:
                        try:
                            on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Ошибка в on_retry callback: {callback_error}")

                    # Ждем перед следующей попыткой
                    time.sleep(current_delay)

                    # Увеличиваем задержку для следующей попытки
                    current_delay *= backoff

            # Если все попытки провалились - поднимаем последнее исключение
            raise last_exception

        return wrapper
    return decorator


def retry_on_network_error(max_attempts: int = 3, delay: float = 1.0):
    """
    Специализированный декоратор для сетевых ошибок

    Повторяет только при:
    - ConnectionError
    - TimeoutError
    - httpx.RequestError
    - httpx.HTTPStatusError (500, 502, 503, 504)

    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками
    """
    import httpx

    # Исключения для retry
    network_exceptions = (
        ConnectionError,
        TimeoutError,
        httpx.RequestError,
    )

    def should_retry_http_error(e: Exception) -> bool:
        """Проверяет нужно ли делать retry для HTTP ошибки"""
        if isinstance(e, httpx.HTTPStatusError):
            # Retry только для server errors (5xx)
            return 500 <= e.response.status_code < 600
        return False

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except network_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"❌ {func.__name__} Network error после {max_attempts} попыток: {str(e)}"
                        )
                        break

                    logger.warning(
                        f"⚠️ {func.__name__} Network error (попытка {attempt}/{max_attempts}): {str(e)}. "
                        f"Повтор через {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= 2

                except httpx.HTTPStatusError as e:
                    last_exception = e

                    # Retry только для 5xx
                    if not should_retry_http_error(e):
                        logger.error(f"❌ {func.__name__} HTTP {e.response.status_code}: не будем делать retry")
                        raise

                    if attempt == max_attempts:
                        logger.error(
                            f"❌ {func.__name__} HTTP {e.response.status_code} после {max_attempts} попыток"
                        )
                        break

                    logger.warning(
                        f"⚠️ {func.__name__} HTTP {e.response.status_code} (попытка {attempt}/{max_attempts}). "
                        f"Повтор через {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= 2

                except Exception as e:
                    # Другие исключения - не делаем retry
                    logger.error(f"❌ {func.__name__} Unexpected error (без retry): {str(e)}")
                    raise

            # Если все попытки провалились
            raise last_exception

        return wrapper
    return decorator


class RetryConfig:
    """
    Конфигурация retry-логики из переменных окружения

    Загружается из .env:
        BITRIX24_RETRY_MAX_ATTEMPTS=3
        BITRIX24_RETRY_DELAY=1.0
        BITRIX24_RETRY_BACKOFF=2.0
    """

    def __init__(self):
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.max_attempts = int(os.getenv("BITRIX24_RETRY_MAX_ATTEMPTS", "3"))
        self.delay = float(os.getenv("BITRIX24_RETRY_DELAY", "1.0"))
        self.backoff = float(os.getenv("BITRIX24_RETRY_BACKOFF", "2.0"))

        logger.info(
            f"RetryConfig загружена: max_attempts={self.max_attempts}, "
            f"delay={self.delay}s, backoff={self.backoff}"
        )


# Глобальный экземпляр конфигурации
retry_config = RetryConfig()
