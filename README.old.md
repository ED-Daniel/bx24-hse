# FastAPI Project

Базовый проект на FastAPI с настройкой окружения и структурой роутеров.

## Структура проекта

```
.
├── main.py                 # Точка входа приложения
├── requirements.txt        # Зависимости проекта
├── .env                    # Переменные окружения
├── app/
│   ├── __init__.py
│   ├── config.py          # Конфигурация и чтение .env
│   ├── routers/           # API роутеры
│   │   ├── __init__.py
│   │   └── users.py       # Пример роутера для работы с пользователями
│   ├── models/            # Модели базы данных
│   └── schemas/           # Pydantic схемы
└── README.md
```

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения в файле `.env`

## Запуск

```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Главная страница
- `GET /health` - Проверка здоровья приложения
- `GET /api/v1/users/` - Получить список пользователей
- `GET /api/v1/users/{user_id}` - Получить пользователя по ID
- `POST /api/v1/users/` - Создать нового пользователя
- `DELETE /api/v1/users/{user_id}` - Удалить пользователя

## Документация API

После запуска приложения документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Переменные окружения

Основные переменные в `.env`:
- `APP_NAME` - Название приложения
- `ENVIRONMENT` - Окружение (development/production)
- `DEBUG` - Режим отладки
- `HOST` - Хост сервера
- `PORT` - Порт сервера
- `DATABASE_URL` - URL базы данных
- `SECRET_KEY` - Секретный ключ для безопасности
- `BITRIX24_WEBHOOK_URL` - URL вебхука Bitrix24

## Docker

### Запуск только сервисов (PostgreSQL)

Для разработки вы можете запустить только PostgreSQL в Docker, а приложение локально:

```bash
# Запустить PostgreSQL
docker-compose -f docker-compose.services.yml up -d

# Остановить
docker-compose -f docker-compose.services.yml down

# Остановить с удалением данных
docker-compose -f docker-compose.services.yml down -v
```

### Запуск всего проекта в Docker

Для запуска приложения и базы данных вместе:

```bash
# Собрать и запустить
docker compose up --build

# Запустить в фоновом режиме
docker compose up -d

# Остановить
docker compose down

# Посмотреть логи
docker compose logs -f app
```

**Важно:** При использовании Docker убедитесь, что в `.env` указан правильный `DATABASE_URL`:
- Для локальной разработки: `postgresql+psycopg2://postgres:postgres@localhost:5432/fastapi_db`
- Для Docker: `postgresql+psycopg2://postgres:postgres@postgres:5432/fastapi_db`

Или используйте `.env.docker` файл при запуске через docker-compose.

### Миграции в Docker

Применить миграции Alembic в контейнере:

```bash
# Создать миграцию
docker-compose exec app alembic revision --autogenerate -m "Migration message"

# Применить миграции
docker-compose exec app alembic upgrade head

# Откатить миграцию
docker-compose exec app alembic downgrade -1
```
