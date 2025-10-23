"""
Pydantic модели для работы с Bitrix24 API

Схемы для контактов, сделок, списков и других сущностей Bitrix24
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

# ==================== Multifield Schemas ====================


class BitrixMultifield(BaseModel):
    """
    Множественное поле в Bitrix24 (EMAIL, PHONE, WEB, IM)

    Пример:
    {
        "VALUE": "+79991234567",
        "VALUE_TYPE": "WORK"
    }
    """

    VALUE: str = Field(..., description="Значение поля")
    VALUE_TYPE: str = Field(default="WORK", description="Тип значения: WORK, HOME, MOBILE, etc.")

    class Config:
        json_schema_extra = {
            "examples": [
                {"VALUE": "test@example.com", "VALUE_TYPE": "WORK"},
                {"VALUE": "+79991234567", "VALUE_TYPE": "MOBILE"},
            ]
        }


# ==================== Contact Schemas ====================


class BitrixContactCreate(BaseModel):
    """
    Поля для создания контакта в Bitrix24

    Минимально необходимые поля согласно документации:
    - NAME (обязательное)
    - LAST_NAME (обязательное)
    - SECOND_NAME (обязательное)
    """

    NAME: str = Field(..., description="Имя")
    LAST_NAME: str = Field(..., description="Фамилия")
    SECOND_NAME: Optional[str] = Field(None, description="Отчество")

    # Контактная информация
    EMAIL: Optional[List[BitrixMultifield]] = Field(None, description="Email адреса")
    PHONE: Optional[List[BitrixMultifield]] = Field(None, description="Телефоны")

    # Дополнительные поля
    BIRTHDATE: Optional[str] = Field(None, description="Дата рождения (YYYY-MM-DD)")
    TYPE_ID: Optional[str] = Field(None, description="Тип контакта")
    SOURCE_ID: Optional[str] = Field(None, description="Источник")
    COMMENTS: Optional[str] = Field(None, description="Комментарий")

    # UTM метки
    UTM_SOURCE: Optional[str] = Field(None, description="Рекламная система")
    UTM_MEDIUM: Optional[str] = Field(None, description="Тип трафика")
    UTM_CAMPAIGN: Optional[str] = Field(None, description="Обозначение рекламной кампании")
    UTM_CONTENT: Optional[str] = Field(None, description="Содержание кампании")
    UTM_TERM: Optional[str] = Field(None, description="Условие поиска кампании")

    # Системные поля
    ASSIGNED_BY_ID: Optional[int] = Field(None, description="Ответственный")

    class Config:
        json_schema_extra = {
            "example": {
                "NAME": "Иван",
                "LAST_NAME": "Иванов",
                "SECOND_NAME": "Иванович",
                "EMAIL": [{"VALUE": "ivan@example.com", "VALUE_TYPE": "WORK"}],
                "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "MOBILE"}],
                "UTM_SOURCE": "direct",
                "UTM_MEDIUM": "direct",
            }
        }


class BitrixContactUpdate(BaseModel):
    """Поля для обновления контакта в Bitrix24 (все поля опциональные)"""

    NAME: Optional[str] = Field(None, description="Имя")
    LAST_NAME: Optional[str] = Field(None, description="Фамилия")
    SECOND_NAME: Optional[str] = Field(None, description="Отчество")
    EMAIL: Optional[List[BitrixMultifield]] = Field(None, description="Email адреса")
    PHONE: Optional[List[BitrixMultifield]] = Field(None, description="Телефоны")
    COMMENTS: Optional[str] = Field(None, description="Комментарий")

    # UTM метки
    UTM_SOURCE: Optional[str] = Field(None, description="Рекламная система")
    UTM_MEDIUM: Optional[str] = Field(None, description="Тип трафика")
    UTM_CAMPAIGN: Optional[str] = Field(None, description="Обозначение рекламной кампании")
    UTM_CONTENT: Optional[str] = Field(None, description="Содержание кампании")
    UTM_TERM: Optional[str] = Field(None, description="Условие поиска кампании")


# ==================== Deal Schemas ====================


class BitrixDealCreate(BaseModel):
    """
    Поля для создания сделки в Bitrix24

    Обязательные поля зависят от настроек воронки,
    но обычно требуется только TITLE
    """

    TITLE: str = Field(..., description="Название сделки")

    # Основные поля
    STAGE_ID: Optional[str] = Field(None, description="Стадия сделки")
    CONTACT_IDS: Optional[List[int]] = Field(None, description="ID контактов")
    COMPANY_ID: Optional[int] = Field(None, description="ID компании")
    OPPORTUNITY: Optional[float] = Field(None, description="Сумма сделки")
    CURRENCY_ID: Optional[str] = Field(None, description="Валюта (по умолчанию RUB)")

    # Источник
    SOURCE_ID: Optional[str] = Field(None, description="Источник")
    COMMENTS: Optional[str] = Field(None, description="Комментарий")

    # UTM метки
    UTM_SOURCE: Optional[str] = Field(None, description="Рекламная система")
    UTM_MEDIUM: Optional[str] = Field(None, description="Тип трафика")
    UTM_CAMPAIGN: Optional[str] = Field(None, description="Обозначение рекламной кампании")
    UTM_CONTENT: Optional[str] = Field(None, description="Содержание кампании")
    UTM_TERM: Optional[str] = Field(None, description="Условие поиска кампании")

    # Кастомные поля
    UF_CRM_1755626160: Optional[int] = Field(
        None, description="Образовательная программа (ID элемента списка IBLOCK_ID=18)"
    )
    UF_CRM_1755626174: Optional[str] = Field(None, description="ID Roistat")

    # Системные поля
    ASSIGNED_BY_ID: Optional[int] = Field(None, description="Ответственный")
    BEGINDATE: Optional[str] = Field(None, description="Дата начала (YYYY-MM-DD)")
    CLOSEDATE: Optional[str] = Field(None, description="Дата завершения (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "TITLE": "Регистрация на программу 'Цифровой юрист'",
                "CONTACT_IDS": [123],
                "UF_CRM_1755626160": 456,
                "UF_CRM_1755626174": "8467460",
                "UTM_SOURCE": "direct",
                "COMMENTS": '{"cookies": {"roistat_visit": "8467460", "_ga": "GA1.2.564819297"}}',
            }
        }


class BitrixDealUpdate(BaseModel):
    """Поля для обновления сделки в Bitrix24 (все поля опциональные)"""

    TITLE: Optional[str] = Field(None, description="Название сделки")
    STAGE_ID: Optional[str] = Field(None, description="Стадия сделки")
    CONTACT_IDS: Optional[List[int]] = Field(None, description="ID контактов")
    COMMENTS: Optional[str] = Field(None, description="Комментарий")

    # UTM метки
    UTM_SOURCE: Optional[str] = Field(None, description="Рекламная система")
    UTM_MEDIUM: Optional[str] = Field(None, description="Тип трафика")
    UTM_CAMPAIGN: Optional[str] = Field(None, description="Обозначение рекламной кампании")
    UTM_CONTENT: Optional[str] = Field(None, description="Содержание кампании")
    UTM_TERM: Optional[str] = Field(None, description="Условие поиска кампании")

    # Кастомные поля
    UF_CRM_1755626160: Optional[int] = Field(None, description="Образовательная программа")
    UF_CRM_1755626174: Optional[str] = Field(None, description="ID Roistat")


# ==================== Universal List Schemas ====================


class BitrixListElementCreate(BaseModel):
    """
    Создание элемента универсального списка

    Используется для создания записей в списках:
    - Опросные формы (IBLOCK_ID=17)
    - Образовательные программы (IBLOCK_ID=18)
    """

    IBLOCK_TYPE_ID: str = Field(default="lists", description="Тип инфоблока")
    IBLOCK_ID: int = Field(..., description="ID списка")
    ELEMENT_CODE: Optional[str] = Field(None, description="Символьный код элемента")
    FIELDS: Dict[str, Any] = Field(..., description="Поля элемента")

    class Config:
        json_schema_extra = {
            "example": {
                "IBLOCK_TYPE_ID": "lists",
                "IBLOCK_ID": 17,
                "FIELDS": {
                    "NAME": "Опрос по образовательным программам",
                    "PROPERTY_64": "123",  # POLL_ID
                    "PROPERTY_65": "https://portal.hse.ru/polls/123.html",  # POLL_URL
                },
            }
        }


class BitrixListElementFilter(BaseModel):
    """Фильтр для поиска элементов списка"""

    IBLOCK_TYPE_ID: str = Field(default="lists", description="Тип инфоблока")
    IBLOCK_ID: int = Field(..., description="ID списка")
    FILTER: Dict[str, Any] = Field(..., description="Фильтр поиска")

    class Config:
        json_schema_extra = {
            "example": {
                "IBLOCK_TYPE_ID": "lists",
                "IBLOCK_ID": 17,
                "FILTER": {"=PROPERTY_64": "123"},  # Поиск по POLL_ID
            }
        }


# ==================== Response Schemas ====================


class BitrixApiResponse(BaseModel):
    """Базовая структура ответа от Bitrix24 API"""

    result: Optional[Any] = Field(None, description="Результат запроса")
    error: Optional[str] = Field(None, description="Код ошибки")
    error_description: Optional[str] = Field(None, description="Описание ошибки")
    time: Optional[Dict[str, Any]] = Field(None, description="Информация о времени выполнения")

    def is_success(self) -> bool:
        """Проверка успешности запроса"""
        return self.error is None and self.result is not None
