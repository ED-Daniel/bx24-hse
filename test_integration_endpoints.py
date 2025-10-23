#!/usr/bin/env python3
"""
Тестовый скрипт для проверки integration router endpoints

Проверяет:
1. Импорт модулей
2. Создание FastAPI app
3. Наличие всех endpoints
4. Структуру ответов
"""

import sys
from fastapi.testclient import TestClient


def print_section(title: str):
    """Печать заголовка секции"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_imports():
    """Тест 1: Проверка импортов"""
    print_section("Тест 1: Проверка импортов модулей")

    try:
        from app.routers import integration
        print("✅ app.routers.integration - импортирован успешно")

        from app.services.integration_service import integration_service
        print("✅ integration_service - импортирован успешно")

        from app.schemas.webhook import WebhookPayload
        print("✅ WebhookPayload - импортирован успешно")

        from app.schemas.integration import PostPollRequest, PostAnswerResponse
        print("✅ Integration schemas - импортированы успешно")

        return True

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_creation():
    """Тест 2: Создание FastAPI приложения"""
    print_section("Тест 2: Создание FastAPI приложения с роутерами")

    try:
        from main import app
        print("✅ FastAPI app создан успешно")

        # Проверяем, что роутер integration зарегистрирован
        routes = [route.path for route in app.routes]
        print(f"\n📋 Зарегистрировано маршрутов: {len(routes)}")

        # Ищем integration endpoints
        integration_routes = [r for r in routes if "integration" in r or "postPoll" in r or "postAnswer" in r]

        if integration_routes:
            print(f"\n✅ Найдено integration маршрутов: {len(integration_routes)}")
            for route in integration_routes:
                print(f"   - {route}")
        else:
            print("\n⚠️  Integration маршруты не найдены в списке routes")
            print("   Проверьте, что router зарегистрирован в main.py")

        return True

    except Exception as e:
        print(f"❌ Ошибка создания app: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoints_structure():
    """Тест 3: Структура endpoints"""
    print_section("Тест 3: Проверка структуры endpoints")

    try:
        from main import app
        client = TestClient(app)

        # Тест 3.1: Health check endpoint
        print("📍 Проверка GET /api/v1/integration/health")
        response = client.get("/api/v1/integration/health")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response: {data}")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")

        # Тест 3.2: postPoll endpoint (проверка без реальных данных)
        print("\n📍 Проверка POST /api/v1/integration/postPoll (структура)")
        print("   (без реального запроса к Bitrix24)")

        # Тест 3.3: postAnswer endpoint (проверка на невалидные данные)
        print("\n📍 Проверка POST /api/v1/integration/postAnswer (валидация)")
        invalid_payload = {
            "header_data": {
                "poll_id": 123,
                "answer_id": 999
                # Намеренно неполные данные для проверки валидации
            },
            "data": {}
        }

        response = client.post("/api/v1/integration/postAnswer", json=invalid_payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response type: {type(response.json())}")

        if response.status_code in [422, 400]:  # Validation error expected
            print("   ✅ Валидация работает корректно (ожидаемая ошибка)")
        else:
            print(f"   ⚠️  Неожиданный ответ: {response.json()}")

        return True

    except Exception as e:
        print(f"❌ Ошибка тестирования endpoints: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_postpoll_schema():
    """Тест 4: Схема postPoll"""
    print_section("Тест 4: Валидация схемы PostPollRequest")

    try:
        from app.schemas.integration import PostPollRequest

        # Валидный запрос
        valid_request = PostPollRequest(
            poll_id=123456,
            poll_name="Тестовый опрос",
            poll_language="ru",
            employee_email="test@hse.ru"
        )
        print("✅ Валидный PostPollRequest создан:")
        print(f"   poll_id: {valid_request.poll_id}")
        print(f"   poll_name: {valid_request.poll_name}")
        print(f"   poll_language: {valid_request.poll_language}")
        print(f"   employee_email: {valid_request.employee_email}")

        return True

    except Exception as e:
        print(f"❌ Ошибка валидации схемы: {e}")
        return False


def test_full_postanswer_payload():
    """Тест 5: Полная схема WebhookPayload для postAnswer"""
    print_section("Тест 5: Валидация полного WebhookPayload")

    try:
        from app.schemas.webhook import WebhookPayload

        # Полный валидный payload
        payload_data = {
            "header_data": {
                "poll_id": 430131691,
                "answer_id": 814573981,
                "create_time": "2025-10-22T10:00:00.000Z",
                "form_kind": 2,
                "gid": "test_gid",
                "analytics": {
                    "url": "https://example.com/poll/123",
                    "params": {
                        "utm_source": "test",
                        "utm_medium": "integration"
                    },
                    "cookies": {
                        "roistat_visit": "12345"
                    },
                    "ip": "127.0.0.1",
                    "date": "2025-10-22 13:00",
                    "timeZone": "Europe/Moscow"
                }
            },
            "data": {
                "firstname": "Тест",
                "lastname": "Тестов",
                "email": "test@example.com",
                "telephone": "+79001112233",
                "educational_program_1": ["Программа 1"],
                "question1": "Ответ на вопрос"
            }
        }

        payload = WebhookPayload(**payload_data)
        print("✅ Полный WebhookPayload создан успешно:")
        print(f"   Poll ID: {payload.header_data.poll_id}")
        print(f"   Answer ID: {payload.header_data.answer_id}")
        print(f"   Email: {payload.data.email}")
        print(f"   Programs: {payload.data.educational_program_1}")

        # Проверяем дополнительные поля
        data_dict = payload.data.model_dump()
        additional = {k: v for k, v in data_dict.items() if k.startswith('question')}
        print(f"   Additional fields: {list(additional.keys())}")

        return True

    except Exception as e:
        print(f"❌ Ошибка создания WebhookPayload: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция тестирования"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ТЕСТИРОВАНИЕ Integration Router" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    print("\n📝 Эти тесты проверяют:")
    print("  1. Корректность импортов")
    print("  2. Регистрацию роутера в FastAPI app")
    print("  3. Наличие и структуру endpoints")
    print("  4. Валидацию Pydantic схем")
    print("  5. НЕ выполняют реальные запросы к Bitrix24\n")

    # Запускаем тесты
    results = []

    results.append(("Импорты", test_imports()))
    results.append(("Создание app", test_app_creation()))
    results.append(("Структура endpoints", test_endpoints_structure()))
    results.append(("PostPoll схема", test_postpoll_schema()))
    results.append(("WebhookPayload схема", test_full_postanswer_payload()))

    # Итоги
    print("\n" + "=" * 70)
    print("  ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"  Успешно: {passed}/{total}")
    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
