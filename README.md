# 🚀 CRM Integration Service - Bitrix24

FastAPI приложение для интеграции опросных форм с Bitrix24 CRM.

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Функциональность](#функциональность)
- [API Endpoints](#api-endpoints)
- [Тестирование](#тестирование)
- [Docker](#docker)
- [Документация](#документация)
- [Разработка](#разработка)

---

## ⚡ Быстрый старт

### 1. Клонирование и установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd new-bx

# Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте `.env` файл:

```env
# Bitrix24 API
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/your_webhook_key/

# FastAPI
APP_NAME="CRM Integration Service"
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database (опционально)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 3. Запуск сервера

```bash
source .venv/bin/activate
python main.py
```

Сервер будет доступен на: http://localhost:8000

Swagger UI документация: http://localhost:8000/docs

---

## 🎯 Функциональность

### Основные возможности

✅ **Регистрация опросных форм** - создание форм в Bitrix24 через `/postPoll`

✅ **Обработка ответов** - полный цикл обработки webhook через `/postAnswer`:
- Поиск опросной формы
- Создание/поиск контакта по email
- Обработка множественных образовательных программ
- Создание отдельной сделки для каждой программы
- Сохранение UTM меток, cookies, дополнительных полей

✅ **Валидация данных** - через Pydantic schemas

✅ **Детальное логирование** - всех этапов обработки

✅ **Health check** - проверка состояния сервиса

### Бизнес-логика

Полное описание бизнес-логики в [INTEGRATION.md](INTEGRATION.md)

Подробное руководство по `process_webhook` в [PROCESS_WEBHOOK_GUIDE.md](PROCESS_WEBHOOK_GUIDE.md)

---

## 📡 API Endpoints

### POST /api/v1/integration/postPoll

Регистрация новой опросной формы в Bitrix24.

**Request:**
```json
{
    "poll_id": 430131691,
    "poll_name": "Опрос абитуриентов 2023",
    "poll_language": "ru",
    "employee_email": "admin@hse.ru"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Связанная опросная форма создана в CRM",
    "poll_id": 430131691,
    "is_successful": true
}
```

### POST /api/v1/integration/postAnswer

Обработка ответа из опросной формы.

**Request:** См. [INTEGRATION.md](INTEGRATION.md) для полной структуры

**Response:**
```json
{
    "status": "success",
    "message": "Успешно обработано. Создано сделок: 2",
    "poll_id": 430131691,
    "answer_id": 814573981,
    "is_successful": true
}
```

### GET /api/v1/integration/health

Проверка состояния сервиса.

**Response:**
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

**Подробная документация:** [INTEGRATION_API_GUIDE.md](INTEGRATION_API_GUIDE.md)

---

## 🧪 Тестирование

### Структура тестов

```
tests/
├── fixtures/          # Тестовые данные
├── unit/             # Unit тесты (с моками)
└── integration/      # Integration тесты (TestClient)
```

### Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# Только unit тесты
pytest tests/unit/ -v

# Только integration тесты
pytest tests/integration/ -v

# С покрытием кода
pytest tests/ --cov=app --cov-report=html
open test_reports/coverage/index.html
```

### Покрытие кода

- **Unit tests:** 21 тест
- **Integration tests:** 15+ тестов
- **Покрытие:** ~90% для core modules

### Ручное тестирование

```bash
# Запустить сервер
python main.py

# В другом терминале - отправить тестовые запросы
python test_webhook.py --endpoint all
```

**Подробная документация:**
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - руководство пользователя
- [tests/README.md](tests/README.md) - техническая документация
- [TESTING_SUMMARY.md](TESTING_SUMMARY.md) - итоговый отчет

---

## 🐳 Docker

### Development

```bash
# Собрать и запустить
docker-compose up --build

# Остановить
docker-compose down
```

### Testing

```bash
# Запустить тесты в Docker
docker-compose -f docker-compose.test.yml up --build

# Только pytest
docker-compose -f docker-compose.test.yml run --rm pytest
```

---

## 📚 Документация

### Основные документы

| Документ | Описание |
|----------|----------|
| [INTEGRATION.md](INTEGRATION.md) | Описание бизнес-логики интеграции |
| [INTEGRATION_TASK.md](INTEGRATION_TASK.md) | Техническое задание на API |
| [INTEGRATION_API_GUIDE.md](INTEGRATION_API_GUIDE.md) | Полное руководство по API |
| [PROCESS_WEBHOOK_GUIDE.md](PROCESS_WEBHOOK_GUIDE.md) | Руководство по process_webhook |
| [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) | Чеклист для запуска |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Итоговая сводка |

### Тестирование

| Документ | Описание |
|----------|----------|
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Руководство по тестированию |
| [tests/README.md](tests/README.md) | Техническая документация тестов |
| [TESTING_SUMMARY.md](TESTING_SUMMARY.md) | Итоговый отчет по тестам |

### Технические документы

| Документ | Описание |
|----------|----------|
| [app/services/README.md](app/services/README.md) | Документация сервисов |
| [app/schemas/README.md](app/schemas/README.md) | Документация схем |

---

## 🛠️ Разработка

### Структура проекта

```
new-bx/
├── app/
│   ├── routers/          # API endpoints
│   ├── services/         # Бизнес-логика
│   ├── schemas/          # Pydantic модели
│   ├── models/           # SQLAlchemy модели
│   ├── config.py         # Конфигурация
│   └── database.py       # Database setup
├── tests/                # Тесты
├── alembic/             # Database migrations
├── field_mapping.json   # Маппинг полей Bitrix24
├── main.py              # Точка входа
└── requirements.txt     # Зависимости
```

### Технологии

- **FastAPI** - веб-фреймворк
- **Pydantic v2** - валидация данных
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Alembic** - миграции БД
- **httpx** - HTTP клиент для Bitrix24 API
- **Pytest** - тестирование

---

## 🐛 Troubleshooting

### Bitrix24 API недоступен

```bash
# Проверить health endpoint
curl http://localhost:8000/api/v1/integration/health

# Проверить BITRIX24_WEBHOOK_URL в .env
# Проверить права вебхука в Bitrix24
```

### Опросная форма не найдена

```
Error: "Опросная форма с ID 123 не найдена"
```

**Решение:** Сначала зарегистрируйте форму через POST /postPoll

### Образовательная программа не найдена

```
Error: "Программы не найдены: Цифровой юрист"
```

**Решение:** Проверьте точное название программы в Bitrix24 (регистр важен!)

**Подробнее:** [INTEGRATION_API_GUIDE.md](INTEGRATION_API_GUIDE.md)

---

## 📄 Лицензия

MIT

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-10-22
