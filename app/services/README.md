## Сервисы для работы с Bitrix24

Этот модуль содержит сервисы для интеграции с Bitrix24 CRM.

## Структура

```
services/
├── __init__.py                 # Экспорт сервисов
├── bitrix24_client.py         # Низкоуровневый клиент для Bitrix24 API
├── integration_service.py     # Бизнес-логика интеграции опросов
└── README.md                  # Этот файл
```

---

## 🔧 bitrix24_client.py

Низкоуровневый клиент для работы с Bitrix24 REST API.

### Класс: `Bitrix24Client`

**Основные методы:**

#### Контакты
- `get_contacts(filter, select, start)` - Получить список контактов
- `get_contact(contact_id)` - Получить контакт по ID
- `create_contact(fields)` - Создать новый контакт
- `update_contact(contact_id, fields)` - Обновить контакт
- `delete_contact(contact_id)` - Удалить контакт

#### Лиды
- `get_leads(filter, select, start)` - Получить список лидов
- `create_lead(fields)` - Создать новый лид
- `update_lead(lead_id, fields)` - Обновить лид

#### Сделки
- `get_deals(filter, select, start)` - Получить список сделок
- `get_deal(deal_id)` - Получить сделку по ID
- `create_deal(fields)` - Создать новую сделку
- `update_deal(deal_id, fields)` - Обновить сделку
- `delete_deal(deal_id)` - Удалить сделку

#### Универсальные списки
- `get_list_elements(iblock_id, filter, select)` - Получить элементы списка
- `create_list_element(iblock_id, fields)` - Создать элемент списка
- `update_list_element(iblock_id, element_id, fields)` - Обновить элемент списка

### Пример использования

```python
from app.services import bitrix24_client

# Поиск контакта по email
result = bitrix24_client.get_contacts(
    filter={"EMAIL": "test@example.com"},
    select=["ID", "NAME", "EMAIL"]
)

# Создание сделки
deal_fields = {
    "TITLE": "Новая сделка",
    "CONTACT_IDS": [123],
    "STAGE_ID": "NEW"
}
result = bitrix24_client.create_deal(deal_fields)
```

---

## 🎯 integration_service.py

Сервис для реализации бизнес-логики интеграции опросов с Bitrix24.

### Класс: `BitrixIntegrationService`

Реализует полный цикл обработки ответов из опросных форм согласно INTEGRATION.md.

### Константы

```python
POLL_FORMS_LIST_ID = 17              # ID списка "Опросные формы"
EDUCATIONAL_PROGRAMS_LIST_ID = 18    # ID списка "Образовательные программы"
POLL_ID_PROPERTY = "PROPERTY_64"     # Код свойства poll_id
PROGRAM_ID_PROPERTY = "PROPERTY_73"  # Код свойства program_id
```

### Методы

#### 1. `find_poll_form(poll_id: int)` → `Optional[Dict]`

Поиск опросной формы в универсальном списке (IBLOCK_ID=17).

**Параметры:**
- `poll_id` - ID опросной формы из внешней системы

**Возвращает:**
- Словарь с данными опросной формы

**Исключения:**
- `Exception` - Если форма не найдена (HTTP 404)

**Пример:**
```python
from app.services import integration_service

try:
    poll_form = integration_service.find_poll_form(430131691)
    print(f"Форма найдена: {poll_form['NAME']}")
except Exception as e:
    print(f"Форма не найдена: {e}")
```

---

#### 2. `find_or_create_contact(...)` → `int`

Поиск контакта по email, если не найден - создание нового.

**Параметры:**
- `email: str` - Email контакта (обязательный)
- `firstname: Optional[str]` - Имя
- `lastname: Optional[str]` - Фамилия
- `middlename: Optional[str]` - Отчество
- `phone: Optional[str]` - Телефон
- `analytics: Optional[Analytics]` - Аналитические данные (UTM)

**Возвращает:**
- `int` - ID контакта (существующего или созданного)

**Пример:**
```python
from app.services import integration_service

contact_id = integration_service.find_or_create_contact(
    email="ivan@example.com",
    firstname="Иван",
    lastname="Иванов",
    phone="+79991234567"
)
print(f"Contact ID: {contact_id}")
```

---

#### 3. `find_educational_programs(program_names: List[str])` → `List[Dict]`

Поиск образовательных программ в универсальном списке (IBLOCK_ID=18).

**Параметры:**
- `program_names` - Список названий программ

**Возвращает:**
- Список найденных программ с полями `ID` и `NAME`

**Исключения:**
- `Exception` - Если хотя бы одна программа не найдена (HTTP 404)

**Пример:**
```python
from app.services import integration_service

programs = integration_service.find_educational_programs([
    "Цифровой юрист",
    "Античность"
])

for prog in programs:
    print(f"{prog['NAME']} - ID: {prog['ID']}")
```

---

#### 4. `find_or_create_deal(...)` → `Tuple[int, bool]`

Поиск сделки по контакту и программе, если не найдена - создание новой.

**Параметры:**
- `contact_id: int` - ID контакта
- `program_id: Optional[int]` - ID образовательной программы
- `poll_form_id: Optional[int]` - ID опросной формы

**Возвращает:**
- `Tuple[int, bool]` - (ID сделки, флаг `is_new`)

**Пример:**
```python
from app.services import integration_service

deal_id, is_new = integration_service.find_or_create_deal(
    contact_id=123,
    program_id=456,
    poll_form_id=789
)

if is_new:
    print(f"Создана новая сделка: {deal_id}")
else:
    print(f"Найдена существующая сделка: {deal_id}")
```

---

#### 5. `enrich_deal(...)` → `bool`

Обогащение сделки дополнительными данными из формы.

**Записывает в сделку:**
- UTM метки (source, medium, campaign, content, term)
- Cookies в JSON формате в поле `COMMENTS`
- Roistat ID в поле `UF_CRM_1755626174`

**Параметры:**
- `deal_id: int` - ID сделки
- `data: WebhookData` - Данные из формы
- `analytics: Optional[Analytics]` - Аналитические данные

**Возвращает:**
- `bool` - True если успешно

**Пример:**
```python
from app.services import integration_service
from app.schemas.webhook import WebhookData

success = integration_service.enrich_deal(
    deal_id=123,
    data=webhook_payload.data,
    analytics=webhook_payload.header_data.analytics
)

if success:
    print("Сделка обогащена")
```

---

#### 6. `process_answer(payload: WebhookPayload)` → `Dict`

**Главный метод** - полный цикл обработки ответа из опросной формы.

**Выполняет все 5 шагов:**
1. Поиск опросной формы
2. Поиск/создание контакта
3. Поиск образовательных программ
4. Поиск/создание сделки
5. Обогащение сделки

**Параметры:**
- `payload: WebhookPayload` - Полные данные webhook

**Возвращает:**
```python
{
    "poll_id": int,           # ID опросной формы
    "answer_id": int,         # ID ответа
    "poll_form_id": int,      # ID в Bitrix24
    "contact_id": int,        # ID контакта
    "deal_id": int,           # ID сделки
    "deal_is_new": bool,      # Флаг новой сделки
    "programs": List[Dict]    # Найденные программы
}
```

**Пример использования:**
```python
from app.services import integration_service
from app.schemas.webhook import WebhookPayload

# В роутере FastAPI
@router.post("/postAnswer")
async def post_answer(payload: WebhookPayload):
    try:
        result = integration_service.process_answer(payload)

        return {
            "status": "success",
            "poll_id": result["poll_id"],
            "answer_id": result["answer_id"],
            "is_successful": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "is_successful": False
        }
```

---

## 🔄 Рабочий процесс

### Диаграмма обработки webhook

```
┌─────────────────────────────────────────────────────────────────┐
│                      Входящий Webhook                           │
│                    (WebhookPayload)                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ШАГ 1: find_poll_form(poll_id)                                 │
│  ├─ Поиск в списке IBLOCK_ID=17                                 │
│  ├─ Фильтр: PROPERTY_64 = poll_id                               │
│  └─ Если не найден → HTTP 404                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ШАГ 2: find_or_create_contact(email, ...)                      │
│  ├─ Поиск контакта по email                                     │
│  ├─ Если не найден → создать новый                              │
│  └─ Записать: ФИО, email, телефон, UTM метки                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ШАГ 3: find_educational_programs(program_names)                │
│  ├─ Поиск в списке IBLOCK_ID=18                                 │
│  ├─ Фильтр: NAME = program_name                                 │
│  └─ Если хоть одна не найдена → HTTP 404                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ШАГ 4: find_or_create_deal(contact_id, program_id, ...)        │
│  ├─ Поиск сделки по CONTACT_ID + UF_CRM_1755626160              │
│  ├─ Если не найдена → создать новую                             │
│  └─ Записать: контакт, программу                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ШАГ 5: enrich_deal(deal_id, data, analytics)                   │
│  ├─ Записать UTM метки                                          │
│  ├─ Записать cookies в JSON (поле COMMENTS)                     │
│  └─ Записать Roistat ID (UF_CRM_1755626174)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Результат обработки                          │
│  {contact_id, deal_id, programs, ...}                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Тестирование

Для тестирования сервиса используйте `test_integration_service.py`:

```bash
source .venv/bin/activate
python test_integration_service.py
```

**ВНИМАНИЕ:** Тесты выполняют РЕАЛЬНЫЕ запросы к Bitrix24!

---

## 📝 Логирование

Сервис использует стандартный модуль `logging` Python.

Для включения логов добавьте в код:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Логи включают:
- Поиск опросных форм и программ
- Создание/обновление контактов и сделок
- Ошибки при работе с API
- Результаты обработки webhook

---

## ⚙️ Конфигурация

Сервис использует `field_mapping.json` для маппинга полей.

Основные параметры берутся из файла:
- ID списков (IBLOCK_ID)
- Коды свойств (PROPERTY_XX)
- Пользовательские поля (UF_CRM_XXXX)

При изменении структуры Bitrix24 обновите `field_mapping.json`.

---

## 🔒 Безопасность

1. **Webhook URL** хранится в `.env` файле
2. **Не коммитьте** `.env` в Git
3. **Логируйте** все операции для аудита
4. **Валидируйте** входные данные через Pydantic схемы

---

## 🚀 Использование в продакшене

1. Добавьте обработку ошибок с повторными попытками
2. Настройте мониторинг логов
3. Используйте асинхронную версию клиента для высокой нагрузки
4. Добавьте кеширование для часто запрашиваемых данных
