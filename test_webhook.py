#!/usr/bin/env python3
"""
Скрипт для отправки тестовых webhook'ов к API

Использует данные из INTEGRATION.md для тестирования endpoints:
- POST /api/v1/integration/postPoll
- POST /api/v1/integration/postAnswer

Запуск:
    python test_webhook.py --help
    python test_webhook.py --endpoint postPoll
    python test_webhook.py --endpoint postAnswer
    python test_webhook.py --endpoint both
"""

import argparse
import sys
import requests
import json
from typing import Dict, Any
from datetime import datetime

# Цвета для консоли
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title: str):
    """Печать заголовка секции"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message: str):
    """Печать успешного сообщения"""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str):
    """Печать сообщения об ошибке"""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message: str):
    """Печать предупреждения"""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_info(message: str):
    """Печать информационного сообщения"""
    print(f"{BLUE}ℹ️  {message}{RESET}")


# ==================== Тестовые данные ====================

def get_post_poll_payload() -> Dict[str, Any]:
    """Получить тестовый payload для postPoll"""
    return {
        "poll_id": 430131691,
        "poll_name": "Опрос абитуриентов 2023 (ТЕСТ)",
        "poll_language": "ru",
        "employee_email": "test@hse.ru"
    }


def get_full_webhook_payload() -> Dict[str, Any]:
    """Получить полный тестовый webhook payload из INTEGRATION.md"""
    return {
        "header_data": {
            "poll_id": 430131691,
            "answer_id": 814573981,
            "create_time": datetime.utcnow().isoformat() + "Z",
            "form_kind": 2,
            "gid": "test_group_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "analytics": {
                "url": "https://docs.google.com/forms/test/viewform",
                "params": {
                    "utm_source": "yandex",
                    "utm_medium": "cpc",
                    "utm_campaign": "spring_admission_2023",
                    "utm_content": "main_banner",
                    "utm_term": "digital_law"
                },
                "cookies": {
                    "tracking": "test_tracking_value",
                    "_ym_uid": "1607603521955414288",
                    "_ga": "GA1.2.564819297.1607603522",
                    "rete_uid": "test_rete_value_123",
                    "roistat_visit": "8467460"
                },
                "ip": "127.0.0.1",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "timeZone": "Europe/Moscow",
                "mailingListSubscription": True
            }
        },
        "data": {
            "firstname": "Иван",
            "lastname": "Тестов",
            "middlename": "Петрович",
            "email": "ivan.testov@example.com",
            "telephone": "+79991234567",
            "birthdate": "2005-05-15",
            "address": "ул. Тестовая, д. 1",
            "city": "Москва",
            "country": "Россия",
            "educational_program_1": ["Цифровой юрист", "Античность"],
            "additionalfield1": "Учащийся 9-10 классов",
            "additionalfield3": "Москва",
            "hse_school": "52",
            "question1": "Почему вы выбрали эту образовательную программу?",
            "question2": "Каковы ваши карьерные планы после окончания программы?"
        }
    }


def get_minimal_webhook_payload() -> Dict[str, Any]:
    """Получить минимальный webhook payload"""
    return {
        "header_data": {
            "poll_id": 430131691,
            "answer_id": 999999,
            "create_time": datetime.utcnow().isoformat() + "Z",
            "form_kind": 2,
            "analytics": {
                "url": "https://example.com",
                "params": {},
                "cookies": {},
                "ip": "127.0.0.1",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "timeZone": "UTC"
            }
        },
        "data": {
            "firstname": "Тест",
            "lastname": "Минимальный",
            "email": "minimal.test@example.com"
        }
    }


def get_webhook_no_programs() -> Dict[str, Any]:
    """Получить webhook payload без образовательных программ"""
    return {
        "header_data": {
            "poll_id": 430131691,
            "answer_id": 888888,
            "create_time": datetime.utcnow().isoformat() + "Z",
            "form_kind": 2,
            "analytics": {
                "url": "https://example.com",
                "params": {"utm_source": "direct"},
                "cookies": {"roistat_visit": "999888"},
                "ip": "192.168.1.1",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "timeZone": "Europe/Moscow"
            }
        },
        "data": {
            "firstname": "Мария",
            "lastname": "Петрова",
            "email": "maria.petrova.test@example.com",
            "telephone": "+79001112233"
        }
    }


# ==================== Функции отправки ====================

def test_post_poll(base_url: str) -> bool:
    """Тестирование POST /postPoll"""
    print_section("TEST: POST /api/v1/integration/postPoll")

    url = f"{base_url}/api/v1/integration/postPoll"
    payload = get_post_poll_payload()

    print_info(f"URL: {url}")
    print_info("Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 200:
            data = response.json()
            if data.get("is_successful"):
                print_success("postPoll request successful")
                return True
            else:
                print_error(f"postPoll failed: {data.get('description')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_post_answer_full(base_url: str) -> bool:
    """Тестирование POST /postAnswer с полными данными"""
    print_section("TEST: POST /api/v1/integration/postAnswer (FULL)")

    url = f"{base_url}/api/v1/integration/postAnswer"
    payload = get_full_webhook_payload()

    print_info(f"URL: {url}")
    print_info("Payload: (сокращенно)")
    print(f"  poll_id: {payload['header_data']['poll_id']}")
    print(f"  answer_id: {payload['header_data']['answer_id']}")
    print(f"  email: {payload['data']['email']}")
    print(f"  programs: {payload['data']['educational_program_1']}")
    print()

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 200:
            data = response.json()
            if data.get("is_successful"):
                print_success("postAnswer request successful")
                print_info(f"Message: {data.get('message')}")
                return True
            else:
                print_error(f"postAnswer failed: {data.get('description')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_post_answer_minimal(base_url: str) -> bool:
    """Тестирование POST /postAnswer с минимальными данными"""
    print_section("TEST: POST /api/v1/integration/postAnswer (MINIMAL)")

    url = f"{base_url}/api/v1/integration/postAnswer"
    payload = get_minimal_webhook_payload()

    print_info(f"URL: {url}")
    print_info("Payload: (минимальный)")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 200:
            data = response.json()
            if data.get("is_successful"):
                print_success("postAnswer (minimal) request successful")
                return True
            else:
                print_error(f"postAnswer failed: {data.get('description')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_post_answer_no_programs(base_url: str) -> bool:
    """Тестирование POST /postAnswer без образовательных программ"""
    print_section("TEST: POST /api/v1/integration/postAnswer (NO PROGRAMS)")

    url = f"{base_url}/api/v1/integration/postAnswer"
    payload = get_webhook_no_programs()

    print_info(f"URL: {url}")
    print_info("Payload: (без программ)")
    print(f"  email: {payload['data']['email']}")
    print(f"  educational_program_1: НЕТ")
    print()

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 200:
            data = response.json()
            if data.get("is_successful"):
                print_success("postAnswer (no programs) request successful")
                return True
            else:
                print_error(f"postAnswer failed: {data.get('description')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_health_check(base_url: str) -> bool:
    """Тестирование health endpoint"""
    print_section("TEST: GET /api/v1/integration/health")

    url = f"{base_url}/api/v1/integration/health"

    print_info(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["healthy", "degraded"]:
                print_success("Health check passed")
                return True
            else:
                print_warning(f"Health status: {data.get('status')}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


# ==================== Главная функция ====================

def main():
    parser = argparse.ArgumentParser(
        description="Тестирование webhook endpoints для Bitrix24 интеграции"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL API (по умолчанию: http://localhost:8000)"
    )
    parser.add_argument(
        "--endpoint",
        choices=["postPoll", "postAnswer", "both", "all"],
        default="all",
        help="Какой endpoint тестировать"
    )
    parser.add_argument(
        "--variant",
        choices=["full", "minimal", "no-programs"],
        help="Вариант payload для postAnswer (только для --endpoint postAnswer)"
    )

    args = parser.parse_args()

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ТЕСТИРОВАНИЕ WEBHOOK ENDPOINTS" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print(f"Base URL: {args.base_url}")
    print(f"Endpoint: {args.endpoint}")
    print()

    print_warning("⚠️  ВНИМАНИЕ: Эти тесты отправляют РЕАЛЬНЫЕ запросы к API!")
    print_warning("⚠️  Убедитесь, что сервер запущен: python main.py")
    print()

    input("Нажмите Enter для продолжения или Ctrl+C для отмены...")

    results = []

    # Проверка health
    print()
    health_ok = test_health_check(args.base_url)
    if not health_ok:
        print_warning("Health check failed - продолжаем тестирование...")

    # Тестирование postPoll
    if args.endpoint in ["postPoll", "both", "all"]:
        results.append(("postPoll", test_post_poll(args.base_url)))

    # Тестирование postAnswer
    if args.endpoint in ["postAnswer", "both", "all"]:
        if args.variant == "minimal":
            results.append(("postAnswer (minimal)", test_post_answer_minimal(args.base_url)))
        elif args.variant == "no-programs":
            results.append(("postAnswer (no programs)", test_post_answer_no_programs(args.base_url)))
        elif args.variant == "full":
            results.append(("postAnswer (full)", test_post_answer_full(args.base_url)))
        else:
            # Все варианты
            results.append(("postAnswer (full)", test_post_answer_full(args.base_url)))
            results.append(("postAnswer (minimal)", test_post_answer_minimal(args.base_url)))
            results.append(("postAnswer (no programs)", test_post_answer_no_programs(args.base_url)))

    # Итоги
    print_section("ИТОГИ ТЕСТИРОВАНИЯ")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print()
    print("=" * 80)
    if passed == total:
        print_success(f"ВСЕ ТЕСТЫ ПРОШЛИ: {passed}/{total}")
    else:
        print_warning(f"УСПЕШНО: {passed}/{total}, НЕУДАЧНО: {total - passed}")
    print("=" * 80)
    print()

    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n" + RED + "Тестирование отменено пользователем" + RESET)
        sys.exit(130)
