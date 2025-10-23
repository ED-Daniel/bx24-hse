# 🐳 Docker Guide - CRM Integration Service

Руководство по запуску проекта в Docker контейнерах.

---

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Development режим](#development-режим)
3. [Testing режим](#testing-режим)
4. [Production режим](#production-режим)
5. [Troubleshooting](#troubleshooting)

---

## ⚡ Быстрый старт

### Требования

- Docker Desktop или Docker Engine (20.10+)
- Docker Compose V2 (встроен в Docker Desktop)

### Проверка установки

```bash
docker --version
# Docker version 24.0.0 или выше

docker compose version
# Docker Compose version v2.20.0 или выше
```

### Запуск в один клик

```bash
# 1. Создать .env файл
cp .env.example .env

# 2. Отредактировать .env (установить BITRIX24_WEBHOOK_URL)
nano .env

# 3. Запустить все сервисы
docker compose up -d

# 4. Проверить статус
docker compose ps

# 5. Проверить логи
docker compose logs -f app
```

**Приложение доступно на:** http://localhost:8000

**Swagger документация:** http://localhost:8000/docs

---

## 💻 Development режим

### Файл: docker-compose.yml

#### Сервисы

**app** - FastAPI приложение
- Порт: 8000
- Hot reload: включен
- Volume mounting: весь проект

**postgres** - PostgreSQL база данных
- Порт: 5432
- Volume: persistent storage

### Команды

**Запустить:**
```bash
docker compose up
```

**Запустить в фоне:**
```bash
docker compose up -d
```

**Остановить:**
```bash
docker compose down
```

**Пересобрать после изменений:**
```bash
docker compose up --build
```

**Просмотр логов:**
```bash
# Все сервисы
docker compose logs -f

# Только app
docker compose logs -f app

# Только postgres
docker compose logs -f postgres

# Последние 100 строк
docker compose logs --tail=100 app
```

**Выполнить команду внутри контейнера:**
```bash
# Запустить bash
docker compose exec app bash

# Запустить pytest
docker compose exec app pytest tests/ -v

# Проверить миграции
docker compose exec app alembic current

# Применить миграции
docker compose exec app alembic upgrade head
```

**Очистить всё (включая volumes):**
```bash
docker compose down -v
```

### Переменные окружения

Все переменные берутся из `.env` файла:

```env
# Обязательные
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/token/

# Опциональные (есть defaults)
CACHE_ENABLED=True
BATCH_ENABLED=True
BITRIX24_RETRY_MAX_ATTEMPTS=3
LOG_LEVEL=INFO
```

### Hot Reload

При изменении Python файлов uvicorn автоматически перезагрузит приложение:

```bash
# Редактируйте файлы в ./app/
# Uvicorn автоматически перезагрузится
# Проверьте логи:
docker compose logs -f app
```

---

## 🧪 Testing режим

### Файл: docker-compose.test.yml

#### Сервисы

**api** - FastAPI приложение для тестов
- Health check включен
- Read-only volumes

**db** - PostgreSQL для тестов
- Отдельная база данных
- Health check включен

**pytest** - контейнер для запуска тестов
- Запускается по требованию
- Зависит от api health check

### Команды

**Запустить API для тестов:**
```bash
docker compose -f docker-compose.test.yml up -d api db
```

**Запустить тесты:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest
```

**Запустить всё вместе:**
```bash
docker compose -f docker-compose.test.yml up --build
```

**Только unit тесты:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest pytest tests/unit/ -v
```

**Только integration тесты:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest pytest tests/integration/ -v
```

**С покрытием кода:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest \
  pytest tests/ --cov=app --cov-report=html
```

**Очистка:**
```bash
docker compose -f docker-compose.test.yml down -v
```

### Health Checks

**API health check:**
```bash
# Проверяется автоматически каждые 10 секунд
curl http://localhost:8000/api/v1/integration/health
```

**DB health check:**
```bash
# PostgreSQL готовность
docker compose -f docker-compose.test.yml exec db pg_isready -U postgres
```

---

## 🚀 Production режим

### Рекомендации

#### 1. Создать production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.13-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только необходимое
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY field_mapping.json .
COPY main.py .

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Production команда (без --reload!)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. Создать docker-compose.prod.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: crm-integration-prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
      - LOG_LEVEL=WARNING
      # ... остальные переменные из .env
    env_file:
      - .env.production
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - prod-network
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/integration/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:16-alpine
    container_name: postgres-prod
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups  # Для бэкапов
    networks:
      - prod-network
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx reverse proxy (опционально)
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - prod-network
    restart: always

networks:
  prod-network:
    driver: bridge

volumes:
  postgres_prod_data:
```

#### 3. Production переменные окружения

Создать `.env.production`:

```env
# Application
ENVIRONMENT=production
DEBUG=False
APP_NAME="CRM Integration Service"

# Security
SECRET_KEY=super-secret-key-change-this-in-production

# Bitrix24
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/token/

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/crm_prod

# Cache (более долгий TTL для production)
CACHE_ENABLED=True
CACHE_TTL_POLL_FORMS=1800  # 30 минут
CACHE_TTL_EDUCATIONAL_PROGRAMS=1800

# Batch
BATCH_ENABLED=True
BATCH_SIZE=50

# Retry (больше попыток для production)
BITRIX24_RETRY_MAX_ATTEMPTS=5
BITRIX24_RETRY_DELAY=2.0
BITRIX24_RETRY_BACKOFF=1.5

# Logging
LOG_LEVEL=WARNING  # Меньше логов в production
```

#### 4. Запуск production

```bash
# Сборка
docker compose -f docker-compose.prod.yml build

# Запуск
docker compose -f docker-compose.prod.yml up -d

# Проверка
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f app

# Миграции
docker compose -f docker-compose.prod.yml exec app alembic upgrade head
```

### Production чеклист

- [ ] SECRET_KEY изменен на случайный
- [ ] DEBUG=False
- [ ] LOG_LEVEL=WARNING или ERROR
- [ ] Database credentials надежные
- [ ] Настроен Nginx reverse proxy
- [ ] SSL сертификаты установлены
- [ ] Настроен firewall
- [ ] Настроены бэкапы БД
- [ ] Настроен мониторинг (Prometheus, Grafana)
- [ ] Настроены alerts
- [ ] Health checks работают

---

## 🐛 Troubleshooting

### Проблема: Контейнер не запускается

**Проверить логи:**
```bash
docker compose logs app
```

**Возможные причины:**
1. Порт 8000 занят
   ```bash
   lsof -i :8000
   # Убить процесс или изменить порт в docker-compose.yml
   ```

2. .env файл отсутствует
   ```bash
   cp .env.example .env
   ```

3. Bitrix24 URL неверный
   ```bash
   # Проверить в .env
   cat .env | grep BITRIX24_WEBHOOK_URL
   ```

### Проблема: База данных не подключается

**Проверить статус postgres:**
```bash
docker compose ps postgres
docker compose logs postgres
```

**Проверить подключение:**
```bash
docker compose exec postgres psql -U postgres -d fastapi_db -c "SELECT 1;"
```

**Пересоздать базу:**
```bash
docker compose down -v
docker compose up -d
```

### Проблема: Health check не проходит

**Проверить health endpoint:**
```bash
curl http://localhost:8000/api/v1/integration/health
```

**Проверить статус контейнера:**
```bash
docker compose ps
# Должно быть "healthy" не "unhealthy"
```

**Увеличить timeout:**
```yaml
healthcheck:
  timeout: 10s  # Было 5s
  retries: 10   # Было 5
```

### Проблема: Hot reload не работает

**На macOS могут быть проблемы с file watching:**

```yaml
# В docker-compose.yml добавить:
environment:
  - WATCHFILES_FORCE_POLLING=true
```

### Проблема: Медленная сборка

**Использовать BuildKit:**
```bash
export DOCKER_BUILDKIT=1
docker compose build
```

**Очистить кеш:**
```bash
docker builder prune
```

### Проблема: Тесты падают в Docker

**Проверить переменные окружения:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest env | grep BITRIX
```

**Запустить один тест для отладки:**
```bash
docker compose -f docker-compose.test.yml run --rm pytest \
  pytest tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_success -v
```

---

## 📊 Мониторинг

### Проверка ресурсов

```bash
# CPU и память
docker stats

# Disk usage
docker system df

# Детали по образам
docker images

# Детали по контейнерам
docker ps -a --size
```

### Логирование

**Настроить log driver в docker-compose.yml:**

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Экспорт логов:**
```bash
# В файл
docker compose logs app > app.log

# Через journald (Linux)
docker compose logs --since 1h app
```

---

## 🔧 Полезные команды

### Очистка

```bash
# Удалить все остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Удалить всё неиспользуемое
docker system prune -a

# Удалить volumes
docker volume prune
```

### Отладка

```bash
# Подключиться к контейнеру
docker compose exec app bash

# Проверить переменные окружения
docker compose exec app env

# Проверить Python packages
docker compose exec app pip list

# Проверить сеть
docker network ls
docker network inspect new-bx_app-network
```

### Бэкапы

**База данных:**
```bash
# Создать бэкап
docker compose exec postgres pg_dump -U postgres fastapi_db > backup.sql

# Восстановить бэкап
cat backup.sql | docker compose exec -T postgres psql -U postgres fastapi_db
```

**Volumes:**
```bash
# Бэкап volume
docker run --rm -v new-bx_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup.tar.gz -C /data .

# Восстановление volume
docker run --rm -v new-bx_postgres_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/postgres_backup.tar.gz -C /data
```

---

## 📖 Дополнительная информация

### Документация Docker
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Документация проекта
- [README.md](README.md) - Основная документация
- [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) - Оптимизации
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Тестирование

---

**Версия:** 1.0
**Дата:** 2025-10-23
**Статус:** ✅ Готово к использованию
