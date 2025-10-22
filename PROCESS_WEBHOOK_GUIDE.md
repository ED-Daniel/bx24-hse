# 🚀 Руководство по обработчику process_webhook

## Обзор

Метод `process_webhook` в классе `BitrixIntegrationService` - это главный обработчик для интеграции опросных форм с Bitrix24 CRM. Он реализует полную бизнес-логику согласно INTEGRATION.md.

---

## 📋 Основная логика

### Шаг 1: Валидация входящих данных
- Проверка наличия обязательного поля `email`
- Логирование входящих данных
- Валидация происходит автоматически через Pydantic схемы

### Шаг 2: Поиск опросной формы
- Поиск в универсальном списке "Опросные формы" (IBLOCK_ID=17)
- Фильтр по `PROPERTY_64` (POLL_ID) = `poll_id`
- **Если не найдена → HTTP 404 (Exception)**

### Шаг 3: Поиск/создание контакта
- Поиск контакта по `email` через `crm.contact.list`
- Если найден → используем существующий
- Если не найден → создаем новый с:
  - ФИО (firstname, lastname, middlename)
  - Email и телефон
  - UTM метками из analytics

### Шаг 4: Обработка образовательных программ
Два сценария:

#### 4A. Если указаны программы (`educational_program_1` не пусто)
**Для КАЖДОЙ программы:**
1. Поиск программы в списке IBLOCK_ID=18 по полю `NAME`
2. **Если хоть одна не найдена → HTTP 404 (Exception)**
3. Поиск/создание сделки по фильтру:
   - `CONTACT_ID` = contact_id
   - `UF_CRM_1755626160` (Образовательная программа) = program_id
4. Обогащение сделки:
   - UTM метки
   - Roistat ID
   - Cookies + additional fields + question fields в JSON (поле COMMENTS)

**Результат:** Создается/обновляется НЕСКОЛЬКО сделок (по одной на каждую ОП)

#### 4B. Если программы НЕ указаны
1. Создается одна общая сделка без привязки к программе
2. Обогащается теми же данными

---

## 🎯 Извлечение дополнительных полей

### Метод `_extract_additional_fields(data)`

Автоматически извлекает все поля из формы, **кроме стандартных:**
- `firstname`, `lastname`, `middlename`
- `email`, `telephone`
- `birthdate`, `address`, `city`, `country`
- `educational_program_1`
- `hse_school`

**Все остальные поля** (additionalfield1, question1, question2, etc.) попадают в `additional_fields` и сохраняются в COMMENTS сделки.

### Метод `_build_deal_comment(analytics, additional_fields)`

Создает JSON для поля COMMENTS:

```json
{
  "cookies": {
    "roistat_visit": "8467460",
    "ga": "GA1.2.564819297",
    "ym_uid": "1607603521955414288",
    "tracking": "...",
    "rete_uid": "..."
  },
  "additional_fields": {
    "additionalfield1": "Учащийся 9-10 классов",
    "additionalfield3": "Москва",
    "question1": "Ответ на вопрос 1",
    "question2": "Ответ на вопрос 2",
    "hse_school": "52"
  },
  "analytics": {
    "ip": "185.117.121.169",
    "url": "https://example.com/poll/123",
    "date": "2023-02-15 13:16",
    "timeZone": "Europe/Moscow"
  },
  "mailingListSubscription": true
}
```

---

## 📊 Возвращаемый результат

```python
{
    "poll_id": 430131691,
    "answer_id": 814573981,
    "poll_form_id": "123",
    "contact_id": 456,
    "deals": [
        {
            "program_name": "Цифровой юрист",
            "program_id": "789",
            "deal_id": 1001,
            "is_new": True
        },
        {
            "program_name": "Античность",
            "program_id": "790",
            "deal_id": 1002,
            "is_new": False
        }
    ],
    "total_deals": 2
}
```

---

## 🎨 Пример логов

При обработке webhook вы увидите детальные логи:

```
======================================================================
🚀 START PROCESSING WEBHOOK
   Poll ID: 430131691
   Answer ID: 814573981
   Email: test@example.com
======================================================================

📋 STEP 1: Validating incoming data...
✅ Validation passed
   Email: test@example.com
   Name: Иван Иванов
   Programs: ['Цифровой юрист', 'Античность']

🔍 STEP 2: Finding poll form...
✅ Poll form found
   Bitrix ID: 123
   Name: Опрос по образовательным программам

👤 STEP 3: Finding or creating contact...
✅ Contact ready
   Contact ID: 456

🎓 STEP 4: Processing 2 educational programs...

   📚 Processing program: Цифровой юрист
      Program ID: 789
      🔍 Finding or creating deal...
      ✅ Created new deal
         Deal ID: 1001
      💎 Enriching deal with additional data...
      ✅ Deal enriched successfully

   📚 Processing program: Античность
      Program ID: 790
      🔍 Finding or creating deal...
      ✅ Found existing deal
         Deal ID: 1002
      💎 Enriching deal with additional data...
      ✅ Deal enriched successfully

======================================================================
✅ WEBHOOK PROCESSED SUCCESSFULLY
   Contact ID: 456
   Total Deals: 2
   - Deal 1001: Цифровой юрист (NEW)
   - Deal 1002: Античность (EXISTING)
======================================================================
```

---

## 💡 Использование в роутерах

### Базовый пример

```python
from fastapi import APIRouter, HTTPException
from app.services import integration_service
from app.schemas import WebhookPayload, create_success_answer_response, create_error_answer_response

router = APIRouter()

@router.post("/postAnswer")
async def post_answer(payload: WebhookPayload):
    """Обработка ответа из опросной формы"""
    try:
        # Вся обработка в одном вызове
        result = integration_service.process_webhook(payload)

        return create_success_answer_response(
            poll_id=result["poll_id"],
            answer_id=result["answer_id"],
            message=f"Создано сделок: {result['total_deals']}"
        )

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Webhook processing failed: {e}")

        return create_error_answer_response(
            poll_id=payload.header_data.poll_id,
            answer_id=payload.header_data.answer_id,
            description=str(e)
        )
```

### Пример с детальным логированием

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@router.post("/postAnswer")
async def post_answer(payload: WebhookPayload):
    try:
        result = integration_service.process_webhook(payload)

        # Можно обработать результат
        for deal in result["deals"]:
            if deal["is_new"]:
                logger.info(f"New deal created: {deal['deal_id']} for {deal['program_name']}")

        return create_success_answer_response(
            poll_id=result["poll_id"],
            answer_id=result["answer_id"]
        )

    except Exception as e:
        return create_error_answer_response(
            poll_id=payload.header_data.poll_id,
            answer_id=payload.header_data.answer_id,
            description=str(e)
        )
```

---

## ⚠️ Обработка ошибок

### Типы ошибок:

1. **Опросная форма не найдена (404)**
   ```python
   Exception: "Опросная форма с ID 123 не найдена в системе"
   ```

2. **Образовательная программа не найдена (404)**
   ```python
   Exception: "Образовательные программы не найдены в системе: Цифровой юрист, Античность"
   ```

3. **Email не указан**
   ```python
   Exception: "Email обязателен для создания контакта"
   ```

4. **Ошибки Bitrix24 API**
   ```python
   Exception: "Bitrix24 API Error: ..."
   Exception: "Не удалось создать контакт: ..."
   Exception: "Не удалось создать сделку: ..."
   ```

---

## 🧪 Тестирование

### Запуск тестов

```bash
source .venv/bin/activate
python test_integration_service.py
```

### Тестовые данные

```python
from app.schemas import WebhookPayload

payload = WebhookPayload(**{
    "header_data": {
        "poll_id": 123,
        "answer_id": 999,
        "create_time": "2025-10-22T10:00:00Z",
        "form_kind": 2,
        "analytics": {
            "url": "https://example.com",
            "params": {"utm_source": "test"},
            "cookies": {"roistat_visit": "12345"},
            "ip": "127.0.0.1",
            "date": "2025-10-22 13:00",
            "timeZone": "Europe/Moscow"
        }
    },
    "data": {
        "firstname": "Тест",
        "lastname": "Тестов",
        "email": "test@example.com",
        "educational_program_1": ["Цифровой юрист"],
        "additionalfield1": "Дополнительное поле"
    }
})

result = integration_service.process_webhook(payload)
```

---

## 🔧 Настройка

### field_mapping.json

Сервис использует конфигурацию из `field_mapping.json`:

```json
{
  "universal_lists": {
    "polls": {
      "iblock_id": 17,
      "fields": {
        "PROPERTY_64": {"code": "POLL_ID"}
      }
    },
    "educational_programs": {
      "iblock_id": 18
    }
  },
  "bitrix24_entities": {
    "deals": {
      "custom_fields": {
        "UF_CRM_1755626160": {"title": "Образовательная программа"},
        "UF_CRM_1755626174": {"title": "ID Roistat"}
      }
    }
  }
}
```

---

## 📈 Производительность

- **Один вызов API** для поиска опросной формы
- **Один вызов API** для поиска контакта
- **Один вызов API** для поиска всех ОП сразу
- **По одному вызову API** на сделку (поиск + создание/обновление + обогащение)

**Для 2 программ:** ~7-8 запросов к Bitrix24 API

---

## 🔄 Backward Compatibility

Для обратной совместимости сохранен алиас:

```python
process_answer = process_webhook
```

Можно использовать оба варианта:
- `integration_service.process_webhook(payload)` ✅ Новый
- `integration_service.process_answer(payload)` ✅ Работает
