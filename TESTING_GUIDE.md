# 🧪 Руководство по тестированию интеграции

## Обзор

Проект содержит три уровня тестирования:

1. **Unit Tests** - Тесты изолированных методов с моками (быстрые)
2. **Integration Tests** - Тесты API endpoints через TestClient (средние)
3. **Manual Tests** - Ручное тестирование с реальными HTTP запросами (медленные)

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск всех тестов

```bash
pytest tests/ -v
```

Ожидаемый результат:
```
tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_success PASSED
tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_find_poll_form_not_found PASSED
...
tests/integration/test_api_endpoints.py::TestPostPollEndpoint::test_post_poll_success_new_form PASSED
tests/integration/test_api_endpoints.py::TestPostAnswerEndpoint::test_post_answer_success_with_programs PASSED
...
===================== 35+ passed in ~5s =====================
```

---

## 📋 Структура тестов

```
tests/
├── fixtures/
│   ├── test_data.py           # Тестовые данные из INTEGRATION.md
│   └── __init__.py
├── unit/
│   ├── test_integration_service.py  # 20+ юнит тестов
│   └── __init__.py
├── integration/
│   ├── test_api_endpoints.py        # 15+ интеграционных тестов
│   └── __init__.py
└── README.md                    # Подробная документация
```

---

## 🔬 Unit Tests

### Что тестируют

- `find_poll_form()` - поиск опросных форм
- `find_or_create_contact()` - создание контактов
- `find_educational_programs()` - поиск программ
- `find_or_create_deal()` - создание сделок
- `enrich_deal()` - обогащение сделок
- `_extract_additional_fields()` - извлечение доп. полей
- `_build_deal_comment()` - построение JSON комментария
- `process_webhook()` - полный цикл обработки

### Запуск

```bash
# Все unit тесты
pytest tests/unit/ -v

# Конкретный тест
pytest tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_process_webhook_with_programs -v

# С покрытием кода
pytest tests/unit/ --cov=app.services.integration_service --cov-report=term-missing
```

### Примеры тестов

**Тест успешного поиска формы:**
```python
def test_find_poll_form_success(self, service, mock_client):
    mock_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE

    result = service.find_poll_form(430131691)

    assert result is not None
    assert result["ID"] == "123"
```

**Тест обработки webhook с программами:**
```python
def test_process_webhook_with_programs(self, service, mocks):
    payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)

    result = service.process_webhook(payload)

    assert result["total_deals"] == 2
    assert len(result["deals"]) == 2
```

---

## 🌐 Integration Tests

### Что тестируют

- `GET /api/v1/integration/health` - health check
- `POST /api/v1/integration/postPoll` - регистрация форм
- `POST /api/v1/integration/postAnswer` - обработка ответов

### Запуск

```bash
# Все integration тесты
pytest tests/integration/ -v

# Только тесты postPoll
pytest tests/integration/test_api_endpoints.py::TestPostPollEndpoint -v

# Только тесты postAnswer
pytest tests/integration/test_api_endpoints.py::TestPostAnswerEndpoint -v
```

### Примеры тестов

**Тест успешной регистрации формы:**
```python
def test_post_poll_success_new_form(client, mock_bitrix_client):
    mock_bitrix_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE
    mock_bitrix_client.create_list_element.return_value = {"result": "123"}

    response = client.post("/api/v1/integration/postPoll", json=POST_POLL_REQUEST)

    assert response.status_code == 200
    assert response.json()["is_successful"] is True
```

**Тест обработки ответа:**
```python
def test_post_answer_success_with_programs(client, mock_bitrix_client):
    # Setup mocks...

    response = client.post("/api/v1/integration/postAnswer", json=FULL_WEBHOOK_PAYLOAD)

    assert response.status_code == 200
    assert "Создано сделок: 2" in response.json()["message"]
```

---

## 🖱️ Ручное тестирование (test_webhook.py)

### Подготовка

1. Запустите сервер:
```bash
source .venv/bin/activate
python main.py
```

2. В отдельном терминале запустите тесты:

### Тест health endpoint

```bash
python test_webhook.py --endpoint health
```

Вывод:
```
======================================================================
  TEST: GET /api/v1/integration/health
======================================================================

ℹ️  URL: http://localhost:8000/api/v1/integration/health
Status Code: 200
Response:
{
  "status": "healthy",
  "field_mapping_loaded": true,
  ...
}

✅ Health check passed
```

### Тест postPoll

```bash
python test_webhook.py --endpoint postPoll
```

### Тест postAnswer (все варианты)

```bash
python test_webhook.py --endpoint postAnswer
```

Выполняет три теста:
- Полный payload с образовательными программами
- Минимальный payload
- Payload без образовательных программ

### Тест postAnswer (только один вариант)

```bash
# Только полный payload
python test_webhook.py --endpoint postAnswer --variant full

# Только минимальный
python test_webhook.py --endpoint postAnswer --variant minimal

# Без программ
python test_webhook.py --endpoint postAnswer --variant no-programs
```

### Тест всех endpoints

```bash
python test_webhook.py --endpoint all
```

### Использование другого URL

```bash
python test_webhook.py --base-url https://api.example.com --endpoint all
```

---

## 🐳 Docker тестирование

### Запуск тестов в Docker

```bash
# Собрать и запустить все контейнеры (API + DB + Pytest)
docker-compose -f docker-compose.test.yml up --build

# Запустить только pytest
docker-compose -f docker-compose.test.yml run --rm pytest

# Остановить и удалить
docker-compose -f docker-compose.test.yml down -v
```

### Запуск API в Docker

```bash
# Запустить только API
docker-compose -f docker-compose.test.yml up api

# API будет доступен на http://localhost:8000

# В другом терминале - отправить тестовые запросы
python test_webhook.py --base-url http://localhost:8000 --endpoint all
```

---

## 📊 Покрытие кода

### Генерация отчета о покрытии

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

Вывод в терминале:
```
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
app/services/integration_service.py     156     12    92%   45-48, 67
app/routers/integration.py                78      5    94%   123-127
app/schemas/webhook.py                    45      0   100%
--------------------------------------------------------------------
TOTAL                                    279     17    94%
```

### Просмотр HTML отчета

```bash
# Открыть отчет в браузере
open test_reports/coverage/index.html
```

HTML отчет показывает:
- Какие строки кода покрыты тестами (зеленым)
- Какие не покрыты (красным)
- Процент покрытия по файлам

---

## 🔍 Отладка тестов

### Запуск с подробным выводом

```bash
pytest tests/ -vv --tb=long
```

### Показать print() в тестах

```bash
pytest tests/ -s
```

### Запустить только упавшие тесты

```bash
pytest --lf
```

### Остановка на первой ошибке

```bash
pytest -x
```

### Запуск конкретного теста с дебаггером

```python
# В тесте добавить точку останова
import pytest

def test_something():
    result = service.process_webhook(payload)
    pytest.set_trace()  # Точка останова
    assert result["total_deals"] == 2
```

Запуск:
```bash
pytest tests/unit/test_integration_service.py::test_something -s
```

---

## ✅ Continuous Integration

### GitHub Actions пример

Создайте `.github/workflows/tests.yml`:

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

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Generate coverage report
        run: |
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 📈 Метрики качества

### Целевые метрики

- ✅ **Покрытие кода:** ≥ 90%
- ✅ **Успешность тестов:** 100%
- ✅ **Время выполнения unit тестов:** < 5 сек
- ✅ **Время выполнения integration тестов:** < 10 сек

### Текущие результаты

После создания всех тестов:

```bash
pytest tests/ --cov=app --durations=10
```

Вывод:
```
===================== 35 passed in 4.85s =====================

slowest 10 durations:
0.85s  tests/integration/test_api_endpoints.py::TestPostAnswerEndpoint::test_post_answer_success_with_programs
0.52s  tests/unit/test_integration_service.py::TestBitrixIntegrationService::test_process_webhook_with_programs
...
```

---

## 🛠️ Полезные команды

```bash
# Показать список доступных фикстур
pytest --fixtures

# Показать доступные маркеры
pytest --markers

# Запуск с параллелизацией (требует pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Генерация JUnit XML отчета (для CI)
pytest --junit-xml=test_reports/junit.xml

# Запуск с профилированием
pytest --profile

# Показать самые медленные тесты
pytest --durations=20
```

---

## 🐛 Troubleshooting

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

### Проблема: Тесты не находят фикстуры

```
fixture 'mock_bitrix_client' not found
```

**Решение:**
Проверьте что фикстуры определены в том же тестовом классе или используйте conftest.py

### Проблема: Import Error для тестовых данных

```
ImportError: cannot import name 'FULL_WEBHOOK_PAYLOAD'
```

**Решение:**
```bash
# Проверьте структуру
ls -la tests/fixtures/
# Должен быть __init__.py и test_data.py
```

### Проблема: pytest не установлен

```
bash: pytest: command not found
```

**Решение:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 Чеклист перед коммитом

- [ ] ✅ Все unit тесты проходят: `pytest tests/unit/`
- [ ] ✅ Все integration тесты проходят: `pytest tests/integration/`
- [ ] ✅ Покрытие кода ≥ 90%: `pytest --cov=app --cov-report=term`
- [ ] ✅ Нет warnings: `pytest -W error`
- [ ] ✅ Code style проверен: `flake8 app/ tests/`
- [ ] ✅ Type hints проверены: `mypy app/`

---

## 🎯 Следующие шаги

1. **Добавить E2E тесты** с реальным Bitrix24 API (опционально)
2. **Настроить CI/CD** (GitHub Actions, GitLab CI)
3. **Добавить performance тесты** (locust, pytest-benchmark)
4. **Настроить coverage badge** для README
5. **Добавить mutation testing** (mutmut)

---

## 📚 Дополнительные ресурсы

- [tests/README.md](tests/README.md) - Подробная документация по тестам
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mock Guide](https://realpython.com/python-mock-library/)

---

**Happy Testing! 🧪✨**
