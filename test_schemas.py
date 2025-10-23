#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Pydantic схем

Запуск: python test_schemas.py
"""

from app.schemas import (
    WebhookPayload,
    PostPollRequest,
    create_success_poll_response,
    create_success_answer_response,
    BitrixContactCreate,
    BitrixDealCreate,
    BitrixMultifield,
)


def test_webhook_payload():
    """Тест валидации входящего webhook"""

    print("=" * 60)
    print("Тест 1: WebhookPayload - валидация входящих данных")
    print("=" * 60)

    # Пример данных из INTEGRATION.md
    data = {
        "header_data": {
            "poll_id": 430131691,
            "answer_id": 814573981,
            "create_time": "2023-02-15T10:16:22.652Z",
            "analytics": {
                "url": "https://ba.hse.ru/polls/430131691.html",
                "params": {
                    "utm_source": "direct",
                    "utm_medium": "direct",
                    "utm_campaign": "direct",
                    "utm_term": "direct",
                    "utm_content": "direct"
                },
                "cookies": {
                    "_ym_uid": "1607603521955414288",
                    "tracking": "ZEsUBF/Yq9OBi6j1G3IiAg",
                    "_ga": "GA1.2.564819297.1608023318",
                    "rete_uid": "a33d94e4-1da7-458d-89db-3cfadc6d687c",
                    "roistat_visit": "8467460"
                },
                "ip": "185.117.121.169",
                "date": "2023-02-15 13:16",
                "timeZone": "Europe/Moscow",
                "mailingListSubscription": True
            },
            "form_kind": 2,
            "gid": None
        },
        "data": {
            "lastname": "Services TEST",
            "firstname": "CRM TEST",
            "email": "crmservices_server_test@example.com",
            "telephone": "+79104061652",
            "additionalfield1": "Учащийся 9-10 классов",
            "additionalfield3": "Москва",
            "hse_school": "52",
            "educational_program_1": [
                "Цифровой юрист",
                "Античность"
            ],
            "middlename": "52"
        }
    }

    try:
        payload = WebhookPayload(**data)
        print("✅ Валидация успешна!")
        print(f"   Poll ID: {payload.header_data.poll_id}")
        print(f"   Answer ID: {payload.header_data.answer_id}")
        print(f"   Email: {payload.data.email}")
        print(f"   Программы: {payload.data.educational_program_1}")
        print(f"   UTM Source: {payload.header_data.analytics.params.utm_source}")
        print(f"   Roistat Visit: {payload.header_data.analytics.cookies.roistat_visit}")
        print(f"   GA: {payload.header_data.analytics.cookies.ga}")
        print(f"   YM UID: {payload.header_data.analytics.cookies.ym_uid}")
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")

    print()


def test_educational_program_as_string():
    """Тест конвертации educational_program_1 из строки в список"""

    print("=" * 60)
    print("Тест 2: educational_program_1 - конвертация строки в список")
    print("=" * 60)

    data = {
        "header_data": {
            "poll_id": 123,
            "answer_id": 345,
            "create_time": "2023-02-15T10:16:22.652Z",
            "analytics": {
                "url": "https://example.com",
                "params": {"utm_source": "direct"},
                "cookies": {},
                "ip": "127.0.0.1",
                "date": "2023-02-15 13:16",
                "timeZone": "Europe/Moscow"
            }
        },
        "data": {
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.com",
            "educational_program_1": "Цифровой юрист"  # Строка вместо списка
        }
    }

    try:
        payload = WebhookPayload(**data)
        print("✅ Конвертация успешна!")
        print(f"   Тип: {type(payload.data.educational_program_1)}")
        print(f"   Значение: {payload.data.educational_program_1}")
        assert isinstance(payload.data.educational_program_1, list)
        print("   ✓ Строка успешно конвертирована в список")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print()


def test_post_poll_request():
    """Тест схемы PostPollRequest"""

    print("=" * 60)
    print("Тест 3: PostPollRequest - регистрация опроса")
    print("=" * 60)

    data = {
        "poll_id": 123,
        "poll_name": "Какой у вас вопрос по ОП",
        "poll_language": "ru",
        "employee_email": "somebody@hse.ru"
    }

    try:
        request = PostPollRequest(**data)
        print("✅ Валидация успешна!")
        print(f"   Poll ID: {request.poll_id}")
        print(f"   Poll Name: {request.poll_name}")
        print(f"   Employee: {request.employee_email}")
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")

    print()


def test_response_helpers():
    """Тест хелперов для создания ответов"""

    print("=" * 60)
    print("Тест 4: Хелперы для создания ответов")
    print("=" * 60)

    # Успешный ответ для postPoll
    poll_response = create_success_poll_response(poll_id=123)
    print("✅ PostPollResponse (success):")
    print(f"   Status: {poll_response.status}")
    print(f"   Is successful: {poll_response.is_successful}")
    print(f"   Message: {poll_response.message}")

    # Успешный ответ для postAnswer
    answer_response = create_success_answer_response(poll_id=123, answer_id=345)
    print("\n✅ PostAnswerResponse (success):")
    print(f"   Status: {answer_response.status}")
    print(f"   Is successful: {answer_response.is_successful}")
    print(f"   Answer ID: {answer_response.answer_id}")

    print()


def test_bitrix_contact_create():
    """Тест схемы создания контакта"""

    print("=" * 60)
    print("Тест 5: BitrixContactCreate - создание контакта")
    print("=" * 60)

    contact = BitrixContactCreate(
        NAME="Иван",
        LAST_NAME="Иванов",
        SECOND_NAME="Иванович",
        EMAIL=[BitrixMultifield(VALUE="ivan@example.com", VALUE_TYPE="WORK")],
        PHONE=[BitrixMultifield(VALUE="+79991234567", VALUE_TYPE="MOBILE")],
        UTM_SOURCE="direct",
        UTM_MEDIUM="cpc"
    )

    print("✅ Контакт создан успешно!")
    print(f"   Имя: {contact.NAME} {contact.LAST_NAME}")
    print(f"   Email: {contact.EMAIL[0].VALUE}")
    print(f"   Телефон: {contact.PHONE[0].VALUE}")

    # Конвертация в dict для API (исключаем None значения)
    contact_dict = contact.model_dump(exclude_none=True)
    print(f"\n   Dict для API (exclude_none=True):")
    print(f"   Количество полей: {len(contact_dict)}")

    print()


def test_bitrix_deal_create():
    """Тест схемы создания сделки"""

    print("=" * 60)
    print("Тест 6: BitrixDealCreate - создание сделки")
    print("=" * 60)

    deal = BitrixDealCreate(
        TITLE="Регистрация на программу 'Цифровой юрист'",
        CONTACT_IDS=[123, 456],
        UF_CRM_1755626160=789,  # ID образовательной программы
        UF_CRM_1755626174="8467460",  # Roistat ID
        UTM_SOURCE="direct",
        COMMENTS='{"cookies": {"roistat_visit": "8467460", "_ga": "GA1.2.564819297"}}'
    )

    print("✅ Сделка создана успешно!")
    print(f"   Название: {deal.TITLE}")
    print(f"   Контакты: {deal.CONTACT_IDS}")
    print(f"   Образовательная программа ID: {deal.UF_CRM_1755626160}")
    print(f"   Roistat ID: {deal.UF_CRM_1755626174}")

    print()


def test_extra_fields():
    """Тест обработки дополнительных полей"""

    print("=" * 60)
    print("Тест 7: Дополнительные поля (extra='allow')")
    print("=" * 60)

    data = {
        "header_data": {
            "poll_id": 123,
            "answer_id": 345,
            "create_time": "2023-02-15T10:16:22.652Z",
            "analytics": {
                "url": "https://example.com",
                "params": {"utm_source": "direct", "custom_param": "custom_value"},
                "cookies": {"custom_cookie": "value"},
                "ip": "127.0.0.1",
                "date": "2023-02-15 13:16",
                "timeZone": "Europe/Moscow"
            }
        },
        "data": {
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.com",
            "question1": "Ответ на вопрос 1",  # Дополнительное поле
            "question2": "Ответ на вопрос 2",  # Дополнительное поле
            "custom_field": "Кастомное значение"  # Дополнительное поле
        }
    }

    try:
        payload = WebhookPayload(**data)
        print("✅ Дополнительные поля приняты!")

        # Проверяем доступ к дополнительным полям через model_dump
        data_dict = payload.data.model_dump()
        print(f"   question1: {data_dict.get('question1')}")
        print(f"   question2: {data_dict.get('question2')}")
        print(f"   custom_field: {data_dict.get('custom_field')}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ТЕСТИРОВАНИЕ PYDANTIC СХЕМ" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    test_webhook_payload()
    test_educational_program_as_string()
    test_post_poll_request()
    test_response_helpers()
    test_bitrix_contact_create()
    test_bitrix_deal_create()
    test_extra_fields()

    print("=" * 60)
    print("✅ Все тесты завершены!")
    print("=" * 60)
    print()
