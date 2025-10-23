# 🔍 Linting & Code Quality Guide

Руководство по использованию линтеров и инструментов для поддержания качества кода.

---

## 📋 Установленные инструменты

### 1. autoflake - Unused Imports Remover
**Версия:** 2.3.1

**Что делает:**
- Автоматически удаляет неиспользуемые импорты
- Удаляет неиспользуемые переменные
- Очищает код от мертвого кода

**Использование:**
```bash
# Проверка без изменений
autoflake --check --remove-all-unused-imports app/ main.py -r

# Автоматическое удаление
autoflake --in-place --remove-all-unused-imports --remove-unused-variables app/ main.py -r
```

### 2. Black - Code Formatter
**Версия:** 25.9.0

**Что делает:**
- Автоматически форматирует Python код по PEP8
- Приводит к единому стилю весь проект
- Устраняет споры о форматировании

**Конфигурация:** `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py313']
```

### 3. isort - Import Sorter
**Версия:** 7.0.0

**Что делает:**
- Сортирует импорты в правильном порядке
- Группирует импорты: stdlib → third-party → local
- Удаляет дублирующиеся импорты

**Конфигурация:** `pyproject.toml`
```toml
[tool.isort]
profile = "black"
line_length = 100
```

### 4. Flake8 - Linter
**Версия:** 7.3.0

**Что делает:**
- Проверяет код на соответствие PEP8
- Находит логические ошибки
- Проверяет сложность кода (cyclomatic complexity)

**Конфигурация:** `.flake8`
```ini
[flake8]
max-line-length = 100
max-complexity = 10
```

### 5. MyPy - Type Checker
**Версия:** 1.18.2

**Что делает:**
- Проверяет типы данных
- Находит потенциальные ошибки до запуска
- Улучшает документацию кода

**Конфигурация:** `pyproject.toml`
```toml
[tool.mypy]
python_version = "3.13"
```

---

## 🚀 Использование

### Быстрый старт

```bash
# 1. Отформатировать код
make format

# 2. Проверить качество
make lint

# 3. Запустить тесты
make test

# 4. Всё вместе
make all
```

### Команды Make

**Форматирование:**
```bash
make format
# Выполняет: autoflake + black + isort
```

**Проверка:**
```bash
make lint
# Выполняет: flake8
```

**Автоисправление:**
```bash
make lint-fix
# Выполняет: autoflake + black + isort + flake8
```

**Тесты:**
```bash
make test
# Запускает pytest

make test-cov
# С покрытием кода
```

**Очистка:**
```bash
make clean
# Удаляет __pycache__, *.pyc
```

---

## 📝 Ручной запуск

### autoflake

**Проверка без изменений:**
```bash
autoflake --check --remove-all-unused-imports app/ main.py -r
```

**Удаление неиспользуемых импортов:**
```bash
autoflake --in-place --remove-all-unused-imports app/ main.py -r
```

**Удаление импортов и переменных:**
```bash
autoflake --in-place --remove-all-unused-imports --remove-unused-variables app/ main.py -r
```

**Проверка конкретного файла:**
```bash
autoflake --check --remove-all-unused-imports app/services/integration_service.py
```

### Black

**Проверка без изменений:**
```bash
black app/ main.py --check
```

**Форматирование:**
```bash
black app/ main.py
```

**Показать diff:**
```bash
black app/ main.py --diff
```

**Форматировать один файл:**
```bash
black app/services/integration_service.py
```

### isort

**Проверка:**
```bash
isort app/ main.py --check-only
```

**Сортировка:**
```bash
isort app/ main.py
```

**Показать diff:**
```bash
isort app/ main.py --diff
```

### Flake8

**Проверка всего проекта:**
```bash
flake8 app/ main.py
```

**Проверка с выводом:**
```bash
flake8 app/ main.py --show-source --statistics
```

**Проверка конкретного файла:**
```bash
flake8 app/services/integration_service.py
```

**Игнорировать определенные ошибки:**
```bash
flake8 app/ --ignore=E501,W503
```

### MyPy

**Проверка типов:**
```bash
mypy app/
```

**С детальным выводом:**
```bash
mypy app/ --show-error-codes
```

---

## 🔧 Конфигурация

### pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ['py313']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.venv
  | alembic/versions
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/alembic/versions/*", "*/.venv/*"]

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
follow_imports = "normal"
ignore_missing_imports = true
```

### .flake8

```ini
[flake8]
max-line-length = 100
max-complexity = 10

ignore =
    E203,  # whitespace before ':' (черт с black)
    W503,  # line break before binary operator
    E501,  # line too long (black контролирует)

exclude =
    .git,
    __pycache__,
    .venv,
    alembic/versions,

count = True
statistics = True
```

---

## 📊 Результаты линтинга

### После применения black и isort

```bash
$ make format
Formatting code with black...
reformatted 12 files
All done! ✨ 🍰 ✨

Sorting imports with isort...
Fixing 17 files
✅ Code formatted!
```

### Flake8 отчет

**Основные ошибки, которые были исправлены:**

1. **F401 - Unused imports** - Удалены неиспользуемые импорты
2. **F541 - f-string without placeholders** - Заменены на обычные строки
3. **E302 - Too few blank lines** - Добавлены пробелы между функциями
4. **W291 - Trailing whitespace** - Удалены пробелы в конце строк

**Оставшиеся предупреждения:**

- **C901 - Function too complex** - В некоторых функциях высокая цикломатическая сложность (это нормально для бизнес-логики)

---

## 🎯 Рекомендации

### Перед коммитом

```bash
# Обязательно!
make format
make lint
make test
```

### В IDE (VS Code)

**settings.json:**
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "python.sortImports.args": ["--profile", "black"]
}
```

### Pre-commit Hook

**Создайте `.git/hooks/pre-commit`:**
```bash
#!/bin/sh

echo "Running linters..."

# Remove unused imports
autoflake --in-place --remove-all-unused-imports --remove-unused-variables app/ main.py -r

# Format code
black app/ main.py
isort app/ main.py

# Lint
flake8 app/ main.py
if [ $? -ne 0 ]; then
    echo "❌ Flake8 failed! Please fix errors."
    exit 1
fi

# Test
pytest tests/unit/ -v
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Please fix tests."
    exit 1
fi

echo "✅ All checks passed!"
```

**Сделать исполняемым:**
```bash
chmod +x .git/hooks/pre-commit
```

---

## 🐛 Частые проблемы

### Проблема: Black и Flake8 конфликтуют

**Решение:** Настроить .flake8 игнорировать E203, W503, E501

```ini
ignore = E203,W503,E501
```

### Проблема: isort портит многострочные импорты

**Решение:** Использовать profile = "black" в pyproject.toml

```toml
[tool.isort]
profile = "black"
```

### Проблема: MyPy много ошибок

**Решение:** Начать постепенно, отключить strict mode

```toml
[tool.mypy]
disallow_untyped_defs = false
ignore_missing_imports = true
```

---

## 📈 Метрики качества кода

### До линтинга

```bash
$ flake8 app/ main.py
26 errors found
```

### После линтинга

```bash
$ flake8 app/ main.py
✅ All checks passed! (только предупреждения о сложности)
```

### Покрытие кода

```bash
$ pytest tests/ --cov=app --cov-report=term
TOTAL    1069    515    52%
```

---

## 🔍 CI/CD Integration

### GitHub Actions

**`.github/workflows/lint.yml`:**
```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Black check
        run: black app/ main.py --check
      - name: isort check
        run: isort app/ main.py --check-only
      - name: Flake8
        run: flake8 app/ main.py
      - name: Tests
        run: pytest tests/
```

---

## 📚 Дополнительные инструменты

### Опциональные линтеры

**pylint** - Более строгий линтер
```bash
pip install pylint
pylint app/
```

**bandit** - Проверка безопасности
```bash
pip install bandit
bandit -r app/
```

**vulture** - Поиск мертвого кода
```bash
pip install vulture
vulture app/
```

---

## ✅ Чеклист code quality

### Перед коммитом

- [ ] `make format` выполнен
- [ ] `make lint` прошел без ошибок
- [ ] `make test` все тесты зеленые
- [ ] Нет TODO комментариев без issue
- [ ] Код задокументирован (docstrings)
- [ ] Сложные места прокомментированы

### Перед pull request

- [ ] Все файлы отформатированы
- [ ] Flake8 без критических ошибок
- [ ] Покрытие кода ≥ 80%
- [ ] Документация обновлена
- [ ] CHANGELOG обновлен

---

## 🎓 Обучение команды

### Ресурсы

- [PEP 8 - Style Guide](https://pep8.org/)
- [autoflake Documentation](https://github.com/PyCQA/autoflake)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [isort Documentation](https://pycqa.github.io/isort/)

### Best Practices

1. **Форматировать часто** - не накапливать изменения
2. **Не игнорировать линтер** - исправлять проблемы сразу
3. **Писать тесты** - линтер не заменяет тесты
4. **Документировать код** - docstrings обязательны

---

## 📊 Итоговая таблица

| Инструмент | Цель | Статус | Команда |
|-----------|------|--------|---------|
| autoflake | Удаление unused imports | ✅ Настроен | `make format` |
| Black | Форматирование | ✅ Настроен | `make format` |
| isort | Сортировка импортов | ✅ Настроен | `make format` |
| Flake8 | Линтинг | ✅ Настроен | `make lint` |
| MyPy | Проверка типов | ✅ Настроен | `mypy app/` |
| Pytest | Тестирование | ✅ Работает | `make test` |

---

**Версия:** 1.0
**Дата:** 2025-10-23
**Статус:** ✅ Все линтеры настроены и работают!
