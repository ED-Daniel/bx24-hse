"""
Модуль для кеширования справочных данных

Кеширует:
- Опросные формы (по poll_id)
- Образовательные программы (по названию)
- Контакты (по email)
"""

import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Менеджер кеша для справочных данных

    Использует простой in-memory словарь с TTL.
    Для production рекомендуется использовать Redis.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Инициализация менеджера кеша

        Args:
            default_ttl: TTL по умолчанию в секундах (5 минут)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"CacheManager инициализирован с TTL={default_ttl}s")

    def _make_key(self, category: str, identifier: str) -> str:
        """Создает ключ кеша"""
        return f"{category}:{identifier}"

    def get(self, category: str, identifier: str) -> Optional[Any]:
        """
        Получить значение из кеша

        Args:
            category: Категория данных (poll_form, educational_program, contact)
            identifier: Идентификатор (poll_id, program_name, email)

        Returns:
            Закешированное значение или None если не найдено/истекло
        """
        key = self._make_key(category, str(identifier))

        if key not in self._cache:
            logger.debug(f"Cache MISS: {key}")
            return None

        entry = self._cache[key]

        # Проверяем TTL
        if time.time() > entry["expires_at"]:
            logger.debug(f"Cache EXPIRED: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache HIT: {key}")
        return entry["value"]

    def set(self, category: str, identifier: str, value: Any, ttl: Optional[int] = None):
        """
        Сохранить значение в кеш

        Args:
            category: Категория данных
            identifier: Идентификатор
            value: Значение для кеширования
            ttl: TTL в секундах (если None - используется default_ttl)
        """
        key = self._make_key(category, str(identifier))
        ttl = ttl or self.default_ttl

        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
        }

        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")

    def invalidate(self, category: str, identifier: Optional[str] = None):
        """
        Инвалидировать кеш

        Args:
            category: Категория данных
            identifier: Идентификатор (если None - инвалидирует всю категорию)
        """
        if identifier:
            key = self._make_key(category, str(identifier))
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cache INVALIDATED: {key}")
        else:
            # Инвалидируем всю категорию
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{category}:")]
            for key in keys_to_delete:
                del self._cache[key]
            logger.info(f"Cache INVALIDATED: {category}:* ({len(keys_to_delete)} entries)")

    def clear(self):
        """Очистить весь кеш"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEARED: {count} entries removed")

    def stats(self) -> Dict[str, Any]:
        """Получить статистику кеша"""
        categories = {}
        total = len(self._cache)

        for key in self._cache.keys():
            category = key.split(":")[0]
            categories[category] = categories.get(category, 0) + 1

        return {"total_entries": total, "categories": categories, "default_ttl": self.default_ttl}


def cached(category: str, key_param: str = "poll_id", ttl: Optional[int] = None):
    """
    Декоратор для кеширования результатов функций

    Args:
        category: Категория кеша
        key_param: Имя параметра функции, который используется как ключ кеша
        ttl: TTL в секундах

    Example:
        @cached(category="poll_form", key_param="poll_id", ttl=600)
        def find_poll_form(self, poll_id: int):
            # ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем значение параметра для ключа кеша
            # Сначала пробуем из kwargs
            identifier = kwargs.get(key_param)

            # Если нет в kwargs, пробуем из args
            if identifier is None:
                # Получаем индекс параметра из сигнатуры функции
                import inspect

                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                if key_param in param_names:
                    param_index = param_names.index(key_param)
                    # Учитываем self (индекс 0)
                    if param_index < len(args):
                        identifier = args[param_index]

            if identifier is None:
                # Не можем определить ключ - выполняем функцию без кеширования
                logger.warning(
                    f"Cached decorator: не удалось определить {key_param}, пропускаем кеширование"
                )
                return func(self, *args, **kwargs)

            # Проверяем кеш
            cache_mgr = getattr(self, "cache", cache_manager)
            cached_value = cache_mgr.get(category, identifier)

            if cached_value is not None:
                return cached_value

            # Выполняем функцию
            result = func(self, *args, **kwargs)

            # Кешируем результат
            cache_mgr.set(category, identifier, result, ttl)

            return result

        return wrapper

    return decorator


# Глобальный экземпляр менеджера кеша
cache_manager = CacheManager()
