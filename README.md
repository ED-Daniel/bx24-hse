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
