#!/usr/bin/env python3
"""
Тестовый скрипт для проверки BitrixIntegrationService

ВНИМАНИЕ: Этот скрипт выполняет РЕАЛЬНЫЕ запросы к Bitrix24 API!
Используйте с осторожностью.

Запуск: python test_integration_service.py
"""

import sys
from app.services.integration_service import BitrixIntegrationService
from app.schemas.webhook import WebhookPayload


def print_section(title: str):
    """Печать заголовка секции"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_service_initialization():
    """Тест 1: Инициализация сервиса"""
    print_section("Тест 1: Инициализация BitrixIntegrationService")

    try:
        service = BitrixIntegrationService()
        print("✅ Сервис успешно инициализирован")
        print(f"   Poll Forms List ID: {service.POLL_FORMS_LIST_ID}")
        print(f"   Educational Programs List ID: {service.EDUCATIONAL_PROGRAMS_LIST_ID}")
        print(f"   Field mapping loaded: {bool(service.field_mapping)}")
        return service
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return None


def test_find_poll_form(service: BitrixIntegrationService):
    """Тест 2: Поиск опросной формы"""
    print_section("Тест 2: Поиск опросной формы")

    # Используем тестовый poll_id (замените на реальный)
    test_poll_id = 123

    print(f"Ищем опросную форму с poll_id={test_poll_id}...")
    print("⚠️  ВНИМАНИЕ: Этот тест выполнит РЕАЛЬНЫЙ запрос к Bitrix24!")
    print("   Для продолжения нажмите Enter, для пропуска - введите 'skip'")

    user_input = input("> ").strip().lower()
    if user_input == 'skip':
        print("⏭️  Тест пропущен")
        return

    try:
        poll_form = service.find_poll_form(test_poll_id)
        print("✅ Опросная форма найдена:")
        print(f"   ID в Bitrix24: {poll_form.get('ID')}")
        print(f"   Название: {poll_form.get('NAME')}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("   Это ожидаемо, если опросная форма с таким ID не существует")


def test_find_or_create_contact(service: BitrixIntegrationService):
    """Тест 3: Поиск/создание контакта"""
    print_section("Тест 3: Поиск/создание контакта")

    test_email = "test_integration@example.com"

    print(f"Ищем или создаем контакт с email={test_email}...")
    print("⚠️  ВНИМАНИЕ: Этот тест может СОЗДАТЬ контакт в Bitrix24!")
    print("   Для продолжения нажмите Enter, для пропуска - введите 'skip'")

    user_input = input("> ").strip().lower()
    if user_input == 'skip':
        print("⏭️  Тест пропущен")
        return None

    try:
        contact_id = service.find_or_create_contact(
            email=test_email,
            firstname="Тест",
            lastname="Интеграция",
            middlename="Сервисович",
            phone="+79991234567"
        )
        print("✅ Операция успешна:")
        print(f"   Contact ID: {contact_id}")
        return contact_id
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def test_find_educational_programs(service: BitrixIntegrationService):
    """Тест 4: Поиск образовательных программ"""
    print_section("Тест 4: Поиск образовательных программ")

    # Замените на реальные названия программ из вашей системы
    test_programs = ["Цифровой юрист", "Античность"]

    print(f"Ищем образовательные программы: {test_programs}...")
    print("⚠️  ВНИМАНИЕ: Этот тест выполнит РЕАЛЬНЫЙ запрос к Bitrix24!")
    print("   Для продолжения нажмите Enter, для пропуска - введите 'skip'")

    user_input = input("> ").strip().lower()
    if user_input == 'skip':
        print("⏭️  Тест пропущен")
        return []

    try:
        programs = service.find_educational_programs(test_programs)
        print("✅ Программы найдены:")
        for prog in programs:
            print(f"   - {prog['NAME']} (ID: {prog['ID']})")
        return programs
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("   Это ожидаемо, если программы с такими названиями не существуют")
        return []


def test_full_workflow():
    """Тест 5: Полный цикл обработки webhook"""
    print_section("Тест 5: Полный цикл обработки webhook (process_webhook)")

    print("Этот тест симулирует полную обработку webhook от опросной формы")
    print("⚠️  ВНИМАНИЕ: Может создать контакт и НЕСКОЛЬКО сделок в Bitrix24!")
    print("   (по одной на каждую образовательную программу)")
    print("   Для продолжения нажмите Enter, для пропуска - введите 'skip'")

    user_input = input("> ").strip().lower()
    if user_input == 'skip':
        print("⏭️  Тест пропущен")
        return

    # Создаем тестовый payload с множественными ОП
    test_data = {
        "header_data": {
            "poll_id": 123,
            "answer_id": 999,
            "create_time": "2025-10-22T10:00:00.000Z",
            "form_kind": 2,
            "gid": "test_group_123",
            "analytics": {
                "url": "https://example.com/poll/123",
                "params": {
                    "utm_source": "test",
                    "utm_medium": "integration",
                    "utm_campaign": "test_campaign",
                    "utm_term": "test_term",
                    "utm_content": "test_content"
                },
                "cookies": {
                    "roistat_visit": "test_123456",
                    "_ga": "GA1.2.123456789",
                    "_ym_uid": "987654321"
                },
                "ip": "127.0.0.1",
                "date": "2025-10-22 13:00",
                "timeZone": "Europe/Moscow",
                "mailingListSubscription": True
            }
        },
        "data": {
            "firstname": "Тест",
            "lastname": "Полного",
            "middlename": "Цикла",
            "email": "test_full_workflow@example.com",
            "telephone": "+79001112233",
            "educational_program_1": ["Цифровой юрист", "Античность"],
            "additionalfield1": "Учащийся 9-10 классов",
            "additionalfield3": "Москва",
            "hse_school": "52",
            "question1": "Ответ на вопрос 1",
            "question2": "Ответ на вопрос 2"
        }
    }

    try:
        print("\n📦 Создаем WebhookPayload...")
        payload = WebhookPayload(**test_data)
        print("✅ Payload создан успешно")
        print(f"   Email: {payload.data.email}")
        print(f"   Programs: {payload.data.educational_program_1}")

        print("\n🔧 Инициализируем сервис...")
        service = BitrixIntegrationService()
        print("✅ Сервис инициализирован")

        print("\n" + "=" * 70)
        print("🚀 Запускаем обработку webhook...")
        print("⚠️  Сейчас будут выполнены РЕАЛЬНЫЕ запросы к Bitrix24")
        print("=" * 70 + "\n")

        # Включаем логирование для наглядности
        import logging
        logging.basicConfig(level=logging.INFO, format='%(message)s')

        result = service.process_webhook(payload)

        print("\n" + "=" * 70)
        print("✅ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 70)
        print(f"\n📊 Результаты:")
        print(f"   Poll ID: {result.get('poll_id')}")
        print(f"   Answer ID: {result.get('answer_id')}")
        print(f"   Contact ID: {result.get('contact_id')}")
        print(f"   Total Deals: {result.get('total_deals')}")
        print(f"\n   Созданные сделки:")
        for i, deal in enumerate(result.get('deals', []), 1):
            print(f"   {i}. Deal ID: {deal['deal_id']}")
            print(f"      Program: {deal['program_name']}")
            print(f"      Status: {'NEW' if deal['is_new'] else 'EXISTING'}")
            print()

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ОШИБКА ОБРАБОТКИ")
        print("=" * 70)
        print(f"Ошибка: {e}\n")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция тестирования"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ТЕСТИРОВАНИЕ BitrixIntegrationService" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")

    print("\n⚠️  ВАЖНО: Эти тесты выполняют РЕАЛЬНЫЕ запросы к Bitrix24 API!")
    print("Убедитесь, что:")
    print("  1. В .env указан правильный BITRIX24_WEBHOOK_URL")
    print("  2. У вас есть доступ к Bitrix24")
    print("  3. Вы понимаете, что могут быть созданы тестовые данные\n")

    print("Продолжить? (yes/no)")
    user_input = input("> ").strip().lower()

    if user_input not in ['yes', 'y', 'да', 'д']:
        print("\n❌ Тестирование отменено")
        sys.exit(0)

    # Запускаем тесты
    service = test_service_initialization()

    if service:
        test_find_poll_form(service)
        contact_id = test_find_or_create_contact(service)
        programs = test_find_educational_programs(service)

        # Полный цикл
        test_full_workflow()

    print("\n" + "=" * 70)
    print("  Тестирование завершено")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
