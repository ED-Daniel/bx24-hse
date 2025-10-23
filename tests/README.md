# 🧪 Руководство по тестированию

## Структура тестов

```
tests/
├── __init__.py
├── fixtures/
│   ├── __init__.py
│   └── test_data.py          # Тестовые данные из INTEGRATION.md
├── unit/
│   ├── __init__.py
│   └── test_integration_service.py  # Юнит-тесты с моками
└── integration/
    ├── __init__.py
    └── test_api_endpoints.py  # Интеграционные тесты endpoints
```

---

## Типы тестов

### 1. Unit Tests (tests/unit/)

**Что тестируют:** Изолированные методы `BitrixIntegrationService` с моками для Bitrix24 API.

**Особенности:**
- ✅ Быстрые (нет реальных API вызовов)
- ✅ Не требуют запущенного сервера
- ✅ Не требуют доступа к Bitrix24
- ✅ Тестируют бизнес-логику изолированно

**Тестируемые методы:**
- `find_poll_form()`
- `find_or_create_contact()`
- `find_educational_programs()`
- `find_or_create_deal()`
- `enrich_deal()`
- `_extract_additional_fields()`
- `_build_deal_comment()`
- `process_webhook()`

### 2. Integration Tests (tests/integration/)

**Что тестируют:** API endpoints через FastAPI TestClient с моками для Bitrix24 API.

**Особенности:**
- ✅ Средняя скорость (используется TestClient)
- ✅ Не требуют запущенного сервера
- ✅ Не требуют доступа к Bitrix24
- ✅ Тестируют полный цикл HTTP request → response

**Тестируемые endpoints:**
- `GET /api/v1/integration/health`
- `POST /api/v1/integration/postPoll`
- `POST /api/v1/integration/postAnswer`

---

## Запуск тестов

### Установка зависимостей

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Запуск всех тестов

```bash
pytest tests/
```

### Запуск только unit тестов

```bash
pytest tests/unit/ -v
```

### Запуск только integration тестов

```bash
pytest tests/integration/ -v
```

### Запуск конкретного теста

```bash
pytest tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_success -v
```

### Запуск с покрытием кода

```bash
pytest tests/ --cov=app --cov-report=html
```

HTML отчет будет создан в `test_reports/coverage/index.html`

### Запуск с подробным выводом

```bash
pytest tests/ -v --tb=long
```

---

## Использование маркеров

### Запуск только юнит тестов

```bash
pytest -m unit
```

### Запуск только интеграционных тестов

```bash
pytest -m integration
```

### Пропустить медленные тесты

```bash
pytest -m "not slow"
```

---

## test_webhook.py - Ручное тестирование

**Назначение:** Отправка реальных HTTP запросов к запущенному API.

### Запуск сервера

```bash
source .venv/bin/activate
python main.py
```

В отдельном терминале:

### Тест health endpoint

```bash
python test_webhook.py --endpoint health
```

### Тест postPoll

```bash
python test_webhook.py --endpoint postPoll
```

### Тест postAnswer (все варианты)

```bash
python test_webhook.py --endpoint postAnswer
```

### Тест postAnswer (только полный payload)

```bash
python test_webhook.py --endpoint postAnswer --variant full
```

### Тест postAnswer (только минимальный payload)

```bash
python test_webhook.py --endpoint postAnswer --variant minimal
```

### Тест всех endpoints

```bash
python test_webhook.py --endpoint all
```

### Указать другой URL

```bash
python test_webhook.py --base-url http://example.com:8000 --endpoint all
```

---

## Docker тестирование

### Запуск тестов в Docker

```bash
# Собрать и запустить контейнеры
docker-compose -f docker-compose.test.yml up --build

# Запустить только pytest контейнер
docker-compose -f docker-compose.test.yml run --rm pytest

# Остановить и удалить контейнеры
docker-compose -f docker-compose.test.yml down -v
```

### Запуск API в Docker для ручного тестирования

```bash
# Запустить API
docker-compose -f docker-compose.test.yml up api

# В отдельном терминале - отправить тестовый webhook
python test_webhook.py --base-url http://localhost:8000 --endpoint all
```

---

## Continuous Integration

### GitHub Actions (пример)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Интерпретация результатов

### Успешный запуск

```
tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_success PASSED
tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_not_found PASSED
...
===================== 35 passed in 2.15s =====================
```

### Тест упал

```
tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_success FAILED

_________________________________ test_find_poll_form_success _________________________________

    def test_find_poll_form_success(self, service, mock_client):
>       result = service.find_poll_form(430131691)
E       AssertionError: expected result not None
```

**Действия:**
1. Проверьте тело теста
2. Проверьте моки
3. Запустите тест с `-v --tb=long` для полного traceback

---

## Покрытие кода

### Просмотр покрытия в терминале

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Вывод:
```
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
app/__init__.py                            0      0   100%
app/services/integration_service.py      156     12    92%   45-48, 67, 89
app/routers/integration.py                78      5    94%   123-127
--------------------------------------------------------------------
TOTAL                                    234     17    93%
```

### HTML отчет

```bash
pytest tests/ --cov=app --cov-report=html
open test_reports/coverage/index.html
```

---

## Отладка тестов

### Использование pytest.set_trace()

```python
import pytest

def test_something():
    result = some_function()
    pytest.set_trace()  # Точка останова
    assert result == expected
```

### Использование -s для вывода print()

```bash
pytest tests/unit/test_integration_service.py -s
```

### Запуск только упавших тестов

```bash
pytest --lf  # Last failed
```

### Запуск до первой ошибки

```bash
pytest -x
```

---

## Best Practices

### 1. Именование тестов

✅ **Хорошо:**
```python
def test_find_poll_form_returns_form_when_exists()
def test_find_poll_form_raises_exception_when_not_found()
```

❌ **Плохо:**
```python
def test_1()
def test_form()
```

### 2. Изоляция тестов

- Каждый тест должен быть независимым
- Используйте фикстуры для setup/teardown
- Не полагайтесь на порядок выполнения тестов

### 3. Моки

```python
# ✅ Мокайте только внешние зависимости
@patch('app.services.integration_service.bitrix24_client')
def test_something(mock_client):
    mock_client.get_contacts.return_value = {...}

# ❌ Не мокайте то что тестируете
@patch('app.services.integration_service.BitrixIntegrationService.find_poll_form')
def test_find_poll_form(mock_find):  # Бессмысленно!
```

### 4. Assertions

```python
# ✅ Четкие assertions
assert result["poll_id"] == 123
assert len(deals) == 2
assert "error" in response.json()

# ❌ Слабые assertions
assert result is not None
assert True
```

---

## Troubleshooting

### Проблема: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'app'
```

**Решение:**
```bash
# Убедитесь что запускаете из корневой директории проекта
pwd  # Должно быть .../new-bx
pytest tests/
```

### Проблема: Fixture not found

```
fixture 'service' not found
```

**Решение:**
Проверьте что фикстура определена в том же классе или в conftest.py

### Проблема: Import Error для тестовых данных

```
ImportError: cannot import name 'FULL_WEBHOOK_PAYLOAD'
```

**Решение:**
```bash
# Проверьте структуру директорий
ls -la tests/fixtures/__init__.py
```

---

## Полезные команды

```bash
# Показать доступные фикстуры
pytest --fixtures

# Показать доступные маркеры
pytest --markers

# Запуск с verbose и показ всех print
pytest -vv -s

# Параллельный запуск (требует pytest-xdist)
pytest -n auto

# Генерация JUnit XML отчета
pytest --junit-xml=test_reports/junit.xml

# Создать coverage badge
coverage-badge -o coverage.svg
```

---

## Дополнительные ресурсы

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

**Happy Testing! 🧪**
