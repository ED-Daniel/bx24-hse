"""
Утилиты для CRM Integration Service
"""

from .cache import cache_manager
from .retry import retry_on_error

__all__ = ["cache_manager", "retry_on_error"]
