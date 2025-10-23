# Pydantic Схемы для Интеграции с Bitrix24

Этот модуль содержит все Pydantic схемы для валидации входящих и исходящих данных в системе интеграции с Bitrix24.

## Структура

```
schemas/
├── __init__.py          # Экспорт всех схем
├── webhook.py           # Схемы для входящих webhook от системы опросов
├── integration.py       # Схемы для API эндпоинтов /postPoll и /postAnswer
├── bitrix.py           # Схемы для работы с Bitrix24 API
└── README.md           # Этот файл
```

## 📦 webhook.py - Входящие данные от опросов

### Основные модели

#### `WebhookPayload`
Главная модель для валидации входящих webhook запросов.

**Пример использования:**
```python
from app.schemas import WebhookPayload

# В роутере
@router.post("/postAnswer")
async def post_answer(payload: WebhookPayload):
    # Данные автоматически валидируются
    poll_id = payload.header_data.poll_id
    email = payload.data.email
    programs = payload.data.educational_program_1  # List[str] или None
```

**Структура:**
```python
{
    "header_data": HeaderData,  # Служебная информация
    "data": WebhookData         # Данные из формы
}
```

#### `HeaderData`
Служебные данные о форме и ответе.

**Поля:**
- `poll_id: int` - ID опросной формы
- `answer_id: int` - ID ответа
- `create_time: datetime` - Время создания (ISO формат)
- `form_kind: Optional[int]` - Вид формы (1=консультация, 2=регистрация)
- `gid: Optional[str]` - ID группы контактов
- `analytics: Analytics` - Аналитические данные

#### `Analytics`
Аналитическая информация о посетителе.

**Поля:**
- `url: str` - URL страницы опроса
- `params: UTMParams` - UTM параметры
- `cookies: Cookies` - Cookies посетителя
- `ip: str` - IP адрес
- `date: str` - Дата отправки
- `timeZone: str` - Часовой пояс
- `mailingListSubscription: Optional[bool]` - Согласие на рассылку

#### `WebhookData`
Данные из полей формы опроса.

**Основные поля:**
- `firstname: Optional[str]` - Имя
- `lastname: Optional[str]` - Фамилия
- `middlename: Optional[str]` - Отчество
- `email: Optional[EmailStr]` - Email (используется для поиска контакта)
- `telephone: Optional[str]` - Телефон
- `educational_program_1: Optional[List[str]]` - Список образовательных программ

**Важно:**
- Модель использует `extra = "allow"`, поэтому принимает любые дополнительные поля
- `educational_program_1` автоматически конвертируется в список, даже если пришла строка

**Пример:**
```python
data = WebhookData(
    firstname="Иван",
    lastname="Иванов",
    email="ivan@example.com",
    educational_program_1=["Цифровой юрист", "Античность"],
    additionalfield1="Учащийся 9-10 классов"
)
```

## 📤 integration.py - API Ответы

### Модели для /postPoll

#### `PostPollRequest`
Входящий запрос для регистрации опроса.

**Поля:**
- `poll_id: int` - ID опросной формы
- `poll_name: str` - Название формы
- `poll_language: str` - Язык ('ru' или 'en')
- `employee_email: EmailStr` - Email сотрудника

**Пример:**
```python
from app.schemas import PostPollRequest

request = PostPollRequest(
    poll_id=123,
    poll_name="Какой у вас вопрос по ОП",
    poll_language="ru",
    employee_email="somebody@hse.ru"
)
```

#### `PostPollResponse`
Ответ на запрос регистрации опроса.

**Поля:**
- `status: str` - "success" или "error"
- `message: str` - Краткое сообщение
- `description: Optional[str]` - Подробное описание
- `poll_id: int` - ID опросной формы
- `is_successful: bool` - Флаг успешности

**Хелперы:**
```python
from app.schemas import create_success_poll_response, create_error_poll_response

# Успешный ответ
response = create_success_poll_response(poll_id=123)

# Ответ с ошибкой
response = create_error_poll_response(
    poll_id=123,
    message="Опросная форма не создана",
    description="Недостаточно прав у пользователя"
)
```

### Модели для /postAnswer

#### `PostAnswerResponse`
Ответ на запрос сохранения ответа.

**Поля:**
- `status: str` - "success" или "error"
- `message: str` - Краткое сообщение
- `description: Optional[str]` - Подробное описание
- `poll_id: int` - ID опросной формы
- `answer_id: int` - ID ответа
- `is_successful: bool` - Флаг успешности

**Хелперы:**
```python
from app.schemas import create_success_answer_response, create_error_answer_response

# Успешный ответ
response = create_success_answer_response(poll_id=123, answer_id=345)

# Ответ с ошибкой
response = create_error_answer_response(
    poll_id=123,
    answer_id=345,
    message="Не удалось сохранить ответ",
    description="Образовательная программа не найдена"
)
```

## 🔧 bitrix.py - Работа с Bitrix24

### Модели для контактов

#### `BitrixContactCreate`
Создание нового контакта.

**Обязательные поля:**
- `NAME: str` - Имя
- `LAST_NAME: str` - Фамилия

**Пример:**
```python
from app.schemas import BitrixContactCreate, BitrixMultifield

contact = BitrixContactCreate(
    NAME="Иван",
    LAST_NAME="Иванов",
    SECOND_NAME="Иванович",
    EMAIL=[BitrixMultifield(VALUE="ivan@example.com", VALUE_TYPE="WORK")],
    PHONE=[BitrixMultifield(VALUE="+79991234567", VALUE_TYPE="MOBILE")],
    UTM_SOURCE="direct",
    UTM_MEDIUM="direct"
)
```

#### `BitrixContactUpdate`
Обновление существующего контакта (все поля опциональные).

### Модели для сделок

#### `BitrixDealCreate`
Создание новой сделки.

**Обязательные поля:**
- `TITLE: str` - Название сделки

**Пример:**
```python
from app.schemas import BitrixDealCreate

deal = BitrixDealCreate(
    TITLE="Регистрация на программу 'Цифровой юрист'",
    CONTACT_IDS=[123],
    UF_CRM_1755626160=456,  # ID образовательной программы
    UF_CRM_1755626174="8467460",  # Roistat ID
    UTM_SOURCE="direct",
    COMMENTS='{"cookies": {"roistat_visit": "8467460"}}'
)
```

#### `BitrixDealUpdate`
Обновление существующей сделки (все поля опциональные).

### Модели для универсальных списков

#### `BitrixListElementCreate`
Создание элемента в универсальном списке.

**Пример для создания опросной формы:**
```python
from app.schemas import BitrixListElementCreate

element = BitrixListElementCreate(
    IBLOCK_TYPE_ID="lists",
    IBLOCK_ID=17,  # Опросные формы
    FIELDS={
        "NAME": "Опрос по образовательным программам",
        "PROPERTY_64": "123",  # POLL_ID
        "PROPERTY_65": "https://portal.hse.ru/polls/123.html",  # POLL_URL
        "PROPERTY_66": "user:123"  # REPONSIBLE_EMPLOYEE_ID
    }
)
```

#### `BitrixListElementFilter`
Фильтр для поиска элементов списка.

**Пример поиска опросной формы:**
```python
from app.schemas import BitrixListElementFilter

filter_query = BitrixListElementFilter(
    IBLOCK_TYPE_ID="lists",
    IBLOCK_ID=17,
    FILTER={
        "=PROPERTY_64": "123"  # Поиск по POLL_ID
    }
)
```

### Вспомогательные модели

#### `BitrixMultifield`
Множественное поле (EMAIL, PHONE, WEB, IM).

**Поля:**
- `VALUE: str` - Значение
- `VALUE_TYPE: str` - Тип (WORK, HOME, MOBILE, etc.)

#### `BitrixApiResponse`
Базовая структура ответа от Bitrix24 API.

**Методы:**
- `is_success() -> bool` - Проверка успешности запроса

## 💡 Примеры использования в роутерах

### Обработка входящего webhook

```python
from fastapi import APIRouter, HTTPException
from app.schemas import WebhookPayload, create_success_answer_response

router = APIRouter()

@router.post("/postAnswer")
async def post_answer(payload: WebhookPayload):
    try:
        # Валидация происходит автоматически
        poll_id = payload.header_data.poll_id
        answer_id = payload.header_data.answer_id

        # Получаем данные
        email = payload.data.email
        if not email:
            raise ValueError("Email обязателен")

        # Обрабатываем образовательные программы
        programs = payload.data.educational_program_1 or []

        # ... бизнес-логика ...

        return create_success_answer_response(poll_id, answer_id)

    except Exception as e:
        return create_error_answer_response(
            poll_id=payload.header_data.poll_id,
            answer_id=payload.header_data.answer_id,
            description=str(e)
        )
```

### Создание контакта в Bitrix24

```python
from app.schemas import BitrixContactCreate, BitrixMultifield
from app.services.bitrix24_client import bitrix24_client

def create_contact_from_form(data: WebhookData) -> int:
    """Создать контакт из данных формы"""

    contact = BitrixContactCreate(
        NAME=data.firstname or "",
        LAST_NAME=data.lastname or "",
        SECOND_NAME=data.middlename,
        EMAIL=[BitrixMultifield(VALUE=data.email)] if data.email else None,
        PHONE=[BitrixMultifield(VALUE=data.telephone)] if data.telephone else None
    )

    # Конвертируем в dict для API
    result = bitrix24_client.create_contact(contact.model_dump(exclude_none=True))

    return result["result"]
```

## 📝 Важные замечания

1. **Email валидация**: Используется `EmailStr` из Pydantic для автоматической валидации email
2. **Дополнительные поля**: `WebhookData` использует `extra = "allow"` для приема любых полей из формы
3. **Списки**: `educational_program_1` автоматически конвертируется в список
4. **None значения**: Используйте `exclude_none=True` при конвертации в dict для API
5. **Multifield формат**: EMAIL и PHONE всегда передаются как список объектов с VALUE и VALUE_TYPE

## 🧪 Тестирование схем

```python
import pytest
from app.schemas import WebhookPayload

def test_webhook_payload_validation():
    """Тест валидации входящих данных"""

    data = {
        "header_data": {
            "poll_id": 123,
            "answer_id": 345,
            "create_time": "2023-02-15T10:16:22.652Z",
            "form_kind": 2,
            "analytics": {
                "url": "https://example.com",
                "params": {"utm_source": "direct"},
                "cookies": {},
                "ip": "127.0.0.1",
                "date": "2023-02-15 13:16",
                "timeZone": "Europe/Moscow"
            }
        },
        "data": {
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.com"
        }
    }

    payload = WebhookPayload(**data)
    assert payload.header_data.poll_id == 123
    assert payload.data.firstname == "Иван"
```
