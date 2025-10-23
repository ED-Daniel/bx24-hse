"""
Pydantic схемы для валидации данных

Модули:
- webhook: Схемы для входящих webhook запросов от системы опросов
- integration: Схемы для API эндпоинтов /postPoll и /postAnswer
- bitrix: Схемы для работы с Bitrix24 API
"""

# Bitrix24 schemas
from .bitrix import (
    BitrixApiResponse,
    BitrixContactCreate,
    BitrixContactUpdate,
    BitrixDealCreate,
    BitrixDealUpdate,
    BitrixListElementCreate,
    BitrixListElementFilter,
    BitrixMultifield,
)

# Integration schemas
from .integration import (
    PostAnswerResponse,
    PostPollRequest,
    PostPollResponse,
    create_error_answer_response,
    create_error_poll_response,
    create_success_answer_response,
    create_success_poll_response,
)

# Webhook schemas
from .webhook import (
    Analytics,
    Cookies,
    HeaderData,
    UTMParams,
    WebhookData,
    WebhookPayload,
)

__all__ = [
    # Webhook
    "UTMParams",
    "Cookies",
    "Analytics",
    "HeaderData",
    "WebhookData",
    "WebhookPayload",
    # Integration
    "PostPollRequest",
    "PostPollResponse",
    "PostAnswerResponse",
    "create_success_poll_response",
    "create_error_poll_response",
    "create_success_answer_response",
    "create_error_answer_response",
    # Bitrix24
    "BitrixMultifield",
    "BitrixContactCreate",
    "BitrixContactUpdate",
    "BitrixDealCreate",
    "BitrixDealUpdate",
    "BitrixListElementCreate",
    "BitrixListElementFilter",
    "BitrixApiResponse",
]
