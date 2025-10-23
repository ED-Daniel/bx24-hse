# 📡 Руководство по Integration API

## Обзор

Integration API предоставляет два основных endpoint'а для интеграции системы опросных форм с Bitrix24 CRM:

1. **POST /api/v1/integration/postPoll** - Регистрация новой опросной формы
2. **POST /api/v1/integration/postAnswer** - Обработка ответа из опросной формы
3. **GET /api/v1/integration/health** - Проверка состояния сервиса

---

## 🔧 Запуск сервера

```bash
# Активировать виртуальное окружение
source .venv/bin/activate

# Запустить FastAPI сервер
python main.py

# Или через uvicorn напрямую
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: `http://localhost:8000`

Документация API (Swagger UI): `http://localhost:8000/docs`

---

## 📋 API Endpoints

### 1. POST /api/v1/integration/postPoll

Регистрация новой опросной формы в Bitrix24.

#### Request

```http
POST /api/v1/integration/postPoll
Content-Type: application/json

{
    "poll_id": 430131691,
    "poll_name": "Опрос абитуриентов 2025",
    "poll_language": "ru",
    "employee_email": "admin@hse.ru"
}
```

**Поля:**
- `poll_id` (int, обязательно) - Уникальный ID опросной формы
- `poll_name` (string, обязательно) - Короткое название опросной формы
- `poll_language` (string, обязательно) - Код языка ('ru' или 'en')
- `employee_email` (string, обязательно) - Email сотрудника, создающего интеграцию

#### Response (Success)

```json
{
    "status": "success",
    "message": "Связанная опросная форма для ID 430131691 создана в CRM или уже существует",
    "description": "Опросная форма успешно зарегистрирована в системе",
    "poll_id": 430131691,
    "is_successful": true
}
```

**HTTP Status:** 200 OK

#### Response (Error)

```json
{
    "status": "error",
    "message": "Опросная форма с ID 430131691 не создана",
    "description": "Недостаточно прав у пользователя admin@hse.ru",
    "poll_id": 430131691,
    "is_successful": false
}
```

**HTTP Status:** 200 OK (с `is_successful: false`)

#### Что происходит при вызове:

1. Проверка прав пользователя (по `employee_email`)
2. Поиск существующей формы с таким `poll_id`
3. Если форма существует → возврат успешного ответа
4. Если не существует → создание элемента в универсальном списке "Опросные формы" (IBLOCK_ID=17)

---

### 2. POST /api/v1/integration/postAnswer

Обработка ответа из опросной формы и создание/обновление данных в Bitrix24.

#### Request

```http
POST /api/v1/integration/postAnswer
Content-Type: application/json

{
    "header_data": {
        "poll_id": 430131691,
        "answer_id": 814573981,
        "create_time": "2025-10-22T10:00:00.000Z",
        "form_kind": 2,
        "gid": "group_123",
        "analytics": {
            "url": "https://example.com/poll/123",
            "params": {
                "utm_source": "yandex",
                "utm_medium": "cpc",
                "utm_campaign": "spring_2025",
                "utm_content": "banner_main",
                "utm_term": "abiturient"
            },
            "cookies": {
                "roistat_visit": "8467460",
                "_ga": "GA1.2.564819297",
                "_ym_uid": "1607603521955414288"
            },
            "ip": "185.117.121.169",
            "date": "2023-02-15 13:16",
            "timeZone": "Europe/Moscow",
            "mailingListSubscription": true
        }
    },
    "data": {
        "firstname": "Иван",
        "lastname": "Иванов",
        "middlename": "Петрович",
        "email": "ivan.ivanov@example.com",
        "telephone": "+79991234567",
        "educational_program_1": ["Цифровой юрист", "Античность"],
        "additionalfield1": "Учащийся 9-10 классов",
        "additionalfield3": "Москва",
        "hse_school": "52",
        "question1": "Почему вы выбрали эту программу?",
        "question2": "Каковы ваши карьерные планы?"
    }
}
```

**Структура header_data:**
- `poll_id` (int, обязательно) - ID опросной формы
- `answer_id` (int, обязательно) - ID ответа
- `create_time` (string) - Время создания ответа (ISO 8601)
- `form_kind` (int) - Тип формы
- `gid` (string) - Group ID
- `analytics` (object) - Аналитические данные

**Структура analytics:**
- `url` (string) - URL страницы с формой
- `params` (object) - UTM метки
- `cookies` (object) - Cookies пользователя
- `ip` (string) - IP адрес
- `date` (string) - Дата и время
- `timeZone` (string) - Часовой пояс
- `mailingListSubscription` (bool) - Согласие на рассылку

**Структура data:**
- `email` (string, обязательно) - Email респондента
- `firstname`, `lastname`, `middlename` (string) - ФИО
- `telephone` (string) - Телефон
- `educational_program_1` (array of strings) - Список выбранных образовательных программ
- Дополнительные поля формы (`additionalfield*`, `question*`, `hse_school`, и т.д.)

#### Response (Success)

```json
{
    "status": "success",
    "message": "Успешно обработано. Создано сделок: 2 - Цифровой юрист (NEW), Античность (EXISTING)",
    "description": "Контакт и сделка созданы/обновлены успешно",
    "poll_id": 430131691,
    "answer_id": 814573981,
    "is_successful": true
}
```

**HTTP Status:** 200 OK

#### Response (Error - Poll Form Not Found)

```json
{
    "status": "error",
    "message": "Не удалось сохранить ответ 814573981",
    "description": "Опросная форма с ID 430131691 не найдена в системе",
    "poll_id": 430131691,
    "answer_id": 814573981,
    "is_successful": false
}
```

**HTTP Status:** 200 OK (с `is_successful: false`)

#### Response (Error - Educational Program Not Found)

```json
{
    "status": "error",
    "message": "Не удалось сохранить ответ 814573981",
    "description": "Образовательные программы не найдены в системе: Цифровой юрист, Античность",
    "poll_id": 430131691,
    "answer_id": 814573981,
    "is_successful": false
}
```

**HTTP Status:** 200 OK (с `is_successful: false`)

#### Что происходит при вызове:

1. **Валидация данных**
   - Проверка обязательного поля `email`
   - Валидация структуры через Pydantic схемы

2. **Поиск опросной формы**
   - Поиск в универсальном списке "Опросные формы" (IBLOCK_ID=17) по `poll_id`
   - Если не найдена → ошибка 404

3. **Поиск/создание контакта**
   - Поиск контакта по email в Bitrix24
   - Если не найден → создание нового с ФИО, телефоном, UTM метками

4. **Обработка образовательных программ**

   **Если указаны программы** (`educational_program_1` не пусто):
   - Для КАЖДОЙ программы:
     1. Поиск программы в списке "Образовательные программы" (IBLOCK_ID=18)
     2. Если хоть одна не найдена → ошибка 404
     3. Поиск существующей сделки по контакту + программе
     4. Если не найдена → создание новой сделки
     5. Обогащение сделки:
        - UTM метки
        - Roistat ID
        - JSON в поле COMMENTS с:
          - cookies
          - additional_fields (все поля вида additionalfield*, question*, hse_school)
          - analytics (ip, url, date, timeZone)

   **Если программы НЕ указаны:**
   - Создается одна общая сделка без привязки к программе
   - Обогащается теми же данными

5. **Возврат результата**
   - Список созданных/обновленных сделок
   - Информация о том, какие сделки новые, а какие существующие

---

### 3. GET /api/v1/integration/health

Проверка работоспособности интеграционного сервиса.

#### Request

```http
GET /api/v1/integration/health
```

#### Response

```json
{
    "status": "healthy",
    "field_mapping_loaded": true,
    "constants_configured": true,
    "bitrix24_api_available": true,
    "service": "integration",
    "version": "1.0.0"
}
```

**Статусы:**
- `healthy` - Все компоненты работают
- `degraded` - Частичная работоспособность (например, Bitrix24 недоступен)
- `unhealthy` - Критические ошибки

---

## 🔍 Примеры использования

### Python (requests)

```python
import requests

# 1. Регистрация опросной формы
poll_response = requests.post(
    "http://localhost:8000/api/v1/integration/postPoll",
    json={
        "poll_id": 123456,
        "poll_name": "Опрос абитуриентов",
        "poll_language": "ru",
        "employee_email": "admin@hse.ru"
    }
)
print(poll_response.json())

# 2. Отправка ответа
answer_response = requests.post(
    "http://localhost:8000/api/v1/integration/postAnswer",
    json={
        "header_data": {
            "poll_id": 123456,
            "answer_id": 999,
            "create_time": "2025-10-22T10:00:00.000Z",
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
            "educational_program_1": ["Программа 1"]
        }
    }
)
print(answer_response.json())
```

### cURL

```bash
# 1. Регистрация опросной формы
curl -X POST "http://localhost:8000/api/v1/integration/postPoll" \
  -H "Content-Type: application/json" \
  -d '{
    "poll_id": 123456,
    "poll_name": "Опрос абитуриентов",
    "poll_language": "ru",
    "employee_email": "admin@hse.ru"
  }'

# 2. Отправка ответа
curl -X POST "http://localhost:8000/api/v1/integration/postAnswer" \
  -H "Content-Type: application/json" \
  -d '{
    "header_data": {
      "poll_id": 123456,
      "answer_id": 999,
      "create_time": "2025-10-22T10:00:00.000Z",
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
      "educational_program_1": ["Программа 1"]
    }
  }'

# 3. Health check
curl "http://localhost:8000/api/v1/integration/health"
```

---

## 🧪 Тестирование

### Запуск unit тестов

```bash
# Тест структуры endpoints (без реальных запросов к Bitrix24)
source .venv/bin/activate
python test_integration_endpoints.py
```

### Запуск интеграционных тестов

```bash
# Тест с РЕАЛЬНЫМИ запросами к Bitrix24
source .venv/bin/activate
python test_integration_service.py
```

**ВНИМАНИЕ:** `test_integration_service.py` выполняет реальные запросы к Bitrix24 API и может создавать тестовые данные!

---

## 📊 Схема обработки данных

```
┌─────────────────────────────────────────────────────────────────┐
│                   POST /postAnswer Request                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Валидация (email обязателен)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Поиск опросной формы (IBLOCK_ID=17)                    │
│  Если не найдена → HTTP 404                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Поиск/создание контакта по email                       │
│  - Поиск в Bitrix24                                             │
│  - Если не найден → создать с ФИО, телефоном, UTM               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Обработка образовательных программ                     │
│                                                                 │
│  ДЛЯ КАЖДОЙ программы из educational_program_1:                 │
│  ├─ Поиск программы (IBLOCK_ID=18)                              │
│  │  Если не найдена → HTTP 404                                  │
│  ├─ Поиск сделки (контакт + программа)                          │
│  │  Если не найдена → создать новую                             │
│  └─ Обогащение сделки:                                          │
│     ├─ UTM метки                                                │
│     ├─ Roistat ID                                               │
│     └─ COMMENTS (JSON):                                         │
│        ├─ cookies                                               │
│        ├─ additional_fields                                     │
│        └─ analytics                                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Response: список созданных/обновленных сделок                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Безопасность

1. **Аутентификация через Bitrix24 Webhook**
   - URL вебхука хранится в `.env` файле
   - Никогда не коммитьте `.env` в Git

2. **Валидация данных**
   - Все входящие данные валидируются через Pydantic
   - Email проверяется через `email-validator`

3. **RBAC (Role-Based Access Control)**
   - Поле `employee_email` в `/postPoll` используется для проверки прав
   - TODO: Реализовать проверку прав пользователя

4. **Логирование**
   - Все операции логируются
   - Логи содержат poll_id, answer_id, email для аудита

---

## 📝 Логирование

Логи включают детальную информацию о каждом этапе обработки:

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

======================================================================
✅ WEBHOOK PROCESSED SUCCESSFULLY
   Contact ID: 456
   Total Deals: 2
======================================================================
```

---

## ⚙️ Конфигурация

### .env файл

```env
# Bitrix24 API
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/your_webhook_key/

# FastAPI
APP_NAME="CRM Integration Service"
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### field_mapping.json

Содержит маппинг полей Bitrix24:

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

## 🚀 Развертывание

### Docker

```bash
# Собрать образ
docker build -t crm-integration .

# Запустить контейнер
docker run -d -p 8000:8000 --env-file .env crm-integration
```

### Docker Compose

```bash
docker-compose up -d
```

---

## 📚 Дополнительная документация

- **INTEGRATION.md** - Описание бизнес-логики интеграции
- **INTEGRATION_TASK.md** - Техническое задание на API
- **PROCESS_WEBHOOK_GUIDE.md** - Подробное руководство по методу `process_webhook`
- **app/services/README.md** - Документация по сервисам
- **app/schemas/README.md** - Документация по Pydantic схемам

---

## 🐛 Решение проблем

### Bitrix24 API недоступен

```python
# Проверьте health endpoint
GET /api/v1/integration/health

# Проверьте BITRIX24_WEBHOOK_URL в .env
# Проверьте права вебхука в Bitrix24
```

### Опросная форма не найдена

```
Error: "Опросная форма с ID 123 не найдена в системе"

Решение:
1. Сначала зарегистрируйте форму через POST /postPoll
2. Проверьте, что poll_id совпадает в обоих запросах
```

### Образовательная программа не найдена

```
Error: "Образовательные программы не найдены в системе: Цифровой юрист"

Решение:
1. Проверьте точное название программы в Bitrix24 (регистр важен!)
2. Создайте программу вручную в универсальном списке IBLOCK_ID=18
```

---

## 📞 Контакты и поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Проверьте health endpoint
3. Запустите тестовый скрипт `test_integration_endpoints.py`
4. Проверьте документацию в `/docs` (Swagger UI)
