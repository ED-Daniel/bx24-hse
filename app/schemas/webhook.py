"""
Pydantic модели для входящих webhook запросов от системы опросов

Структура основана на INTEGRATION.md и INTEGRATION_TASK.md
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ==================== Analytics Models ====================

class UTMParams(BaseModel):
    """UTM параметры для отслеживания источника трафика"""

    utm_source: str = Field(default="direct", description="Рекламная система")
    utm_medium: str = Field(default="direct", description="Тип трафика")
    utm_campaign: str = Field(default="direct", description="Обозначение рекламной кампании")
    utm_term: str = Field(default="direct", description="Условие поиска кампании")
    utm_content: str = Field(default="direct", description="Содержание кампании")

    # Дополнительные параметры, которые могут приходить
    gclid: Optional[str] = Field(None, description="Google Click ID")
    yclid: Optional[str] = Field(None, description="Yandex Click ID")
    fbclid: Optional[str] = Field(None, description="Facebook Click ID")

    class Config:
        extra = "allow"  # Разрешаем дополнительные поля


class Cookies(BaseModel):
    """Cookies для аналитики"""

    # Основные cookies
    tracking: Optional[str] = Field(None, description="Tracking cookie портала")
    ym_uid: Optional[str] = Field(None, alias="_ym_uid", description="Yandex Metrica UID")
    ga: Optional[str] = Field(None, alias="_ga", description="Google Analytics")
    rete_uid: Optional[str] = Field(None, description="Rete User ID")
    roistat_visit: Optional[str] = Field(None, description="Roistat Visit ID")

    class Config:
        extra = "allow"  # Разрешаем дополнительные cookies
        populate_by_name = True  # Позволяет использовать alias для полей с подчеркиванием


class Analytics(BaseModel):
    """Аналитические данные о посетителе"""

    url: str = Field(..., description="URL страницы, где ответил на опрос")
    params: UTMParams = Field(..., description="UTM параметры")
    cookies: Cookies = Field(..., description="Cookies посетителя")
    ip: str = Field(..., description="IP адрес посетителя")
    date: str = Field(..., description="Дата отправки ответа (формат: 'YYYY-MM-DD HH:MM')")
    timeZone: str = Field(..., description="Часовой пояс")
    mailingListSubscription: Optional[bool] = Field(
        None,
        description="Разрешение на рассылку рекламных материалов"
    )


# ==================== Header Data Models ====================

class HeaderData(BaseModel):
    """Служебные данные о форме и ответе"""

    poll_id: int = Field(..., description="Уникальный ID опросной формы")
    answer_id: int = Field(..., description="Уникальный ID ответа")
    create_time: datetime = Field(..., description="Дата и время создания ответа (ISO формат)")
    form_kind: Optional[int] = Field(
        None,
        description="Вид формы: null - не указано, 1 - консультация, 2 - регистрация"
    )
    gid: Optional[str] = Field(
        None,
        description="Сквозной ID группы контактов для внутренней группировки в CRM"
    )
    analytics: Analytics = Field(..., description="Аналитические данные")

    @field_validator('form_kind')
    @classmethod
    def validate_form_kind(cls, v: Optional[int]) -> Optional[int]:
        """Проверка значения form_kind"""
        if v is not None and v not in [1, 2]:
            raise ValueError('form_kind должен быть null, 1 (консультация) или 2 (регистрация)')
        return v


# ==================== Form Data Models ====================

class WebhookData(BaseModel):
    """
    Данные из формы опроса

    Содержит поля с проставленными кодами:
    - Типовые поля (firstname, lastname, email, telephone)
    - Additional fields (additionalfield1, additionalfield2, ...)
    - Question fields (вопросы из формы)
    """

    # Основные типовые поля
    firstname: Optional[str] = Field(None, description="Имя")
    lastname: Optional[str] = Field(None, description="Фамилия")
    middlename: Optional[str] = Field(None, description="Отчество")
    email: Optional[EmailStr] = Field(None, description="Email (используется для поиска контакта)")
    telephone: Optional[str] = Field(None, description="Телефон")

    # Дополнительные типовые поля
    birthdate: Optional[str] = Field(None, description="Дата рождения")
    address: Optional[str] = Field(None, description="Адрес")
    city: Optional[str] = Field(None, description="Город")
    country: Optional[str] = Field(None, description="Страна")

    # Специфичные поля для образовательных программ
    educational_program_1: Optional[List[str]] = Field(
        None,
        description="Список выбранных образовательных программ"
    )

    # Additional fields (могут быть любыми)
    additionalfield1: Optional[str] = Field(None, description="Дополнительное поле 1")
    additionalfield2: Optional[str] = Field(None, description="Дополнительное поле 2")
    additionalfield3: Optional[str] = Field(None, description="Дополнительное поле 3")
    additionalfield4: Optional[str] = Field(None, description="Дополнительное поле 4")
    additionalfield5: Optional[str] = Field(None, description="Дополнительное поле 5")

    # Специфичные поля
    hse_school: Optional[str] = Field(None, description="Школа HSE")

    class Config:
        extra = "allow"  # Разрешаем дополнительные поля (question fields и другие)

    @field_validator('educational_program_1', mode='before')
    @classmethod
    def ensure_list(cls, v):
        """Убеждаемся, что educational_program_1 всегда список"""
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        return v


# ==================== Main Webhook Payload ====================

class WebhookPayload(BaseModel):
    """
    Полная структура входящего webhook от системы опросов

    Пример:
    {
        "header_data": {
            "poll_id": 430131691,
            "answer_id": 814573981,
            "create_time": "2023-02-15T10:16:22.652Z",
            "form_kind": 2,
            "analytics": {...}
        },
        "data": {
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.com",
            ...
        }
    }
    """

    header_data: HeaderData = Field(..., description="Служебные данные о форме и ответе")
    data: WebhookData = Field(..., description="Данные из полей формы опроса")

    class Config:
        json_schema_extra = {
            "example": {
                "header_data": {
                    "poll_id": 430131691,
                    "answer_id": 814573981,
                    "create_time": "2023-02-15T10:16:22.652Z",
                    "analytics": {
                        "url": "https://ba.hse.ru/polls/430131691.html",
                        "params": {
                            "utm_source": "direct",
                            "utm_medium": "direct",
                            "utm_campaign": "direct",
                            "utm_term": "direct",
                            "utm_content": "direct"
                        },
                        "cookies": {
                            "_ym_uid": "1607603521955414288",
                            "tracking": "ZEsUBF/Yq9OBi6j1G3IiAg",
                            "_ga": "GA1.2.564819297.1608023318",
                            "rete_uid": "a33d94e4-1da7-458d-89db-3cfadc6d687c",
                            "roistat_visit": "8467460"
                        },
                        "ip": "185.117.121.169",
                        "date": "2023-02-15 13:16",
                        "timeZone": "Europe/Moscow",
                        "mailingListSubscription": True
                    },
                    "form_kind": 2,
                    "gid": None
                },
                "data": {
                    "lastname": "Services TEST",
                    "firstname": "CRM TEST",
                    "email": "crmservices_server_test@test.test",
                    "telephone": "+79104061652",
                    "additionalfield1": "Учащийся 9-10 классов",
                    "additionalfield3": "Москва",
                    "hse_school": "52",
                    "educational_program_1": [
                        "Цифровой юрист",
                        "Античность"
                    ],
                    "middlename": "52"
                }
            }
        }
