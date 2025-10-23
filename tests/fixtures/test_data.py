"""
Тестовые данные для всех тестов

Содержит примеры payloads согласно INTEGRATION.md
"""

from typing import Dict, Any


# Пример полного webhook payload из INTEGRATION.md
FULL_WEBHOOK_PAYLOAD: Dict[str, Any] = {
    "header_data": {
        "poll_id": 430131691,
        "answer_id": 814573981,
        "create_time": "2023-02-15T13:16:00.000Z",
        "form_kind": 2,
        "gid": "group_12345",
        "analytics": {
            "url": "https://docs.google.com/forms/d/e/1FAIpQLSeXXXXXX/viewform",
            "params": {
                "utm_source": "yandex",
                "utm_medium": "cpc",
                "utm_campaign": "spring_admission_2023",
                "utm_content": "main_banner",
                "utm_term": "digital_law"
            },
            "cookies": {
                "tracking": "some_tracking_value",
                "_ym_uid": "1607603521955414288",
                "_ga": "GA1.2.564819297.1607603522",
                "rete_uid": "rete_value_123",
                "roistat_visit": "8467460"
            },
            "ip": "185.117.121.169",
            "date": "2023-02-15 13:16",
            "timeZone": "Europe/Moscow",
            "mailingListSubscription": True
        }
    },
    "data": {
        "firstname": "Иван",
        "lastname": "Иванов",
        "middlename": "Петрович",
        "email": "ivan.ivanov@example.com",
        "telephone": "+79991234567",
        "birthdate": "2005-05-15",
        "address": "ул. Пушкина, д. 10",
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

# Минимальный webhook payload (только обязательные поля)
MINIMAL_WEBHOOK_PAYLOAD: Dict[str, Any] = {
    "header_data": {
        "poll_id": 123,
        "answer_id": 456,
        "create_time": "2025-10-22T10:00:00.000Z",
        "form_kind": 2,
        "analytics": {
            "url": "https://example.com",
            "params": {},
            "cookies": {},
            "ip": "127.0.0.1",
            "date": "2025-10-22 10:00",
            "timeZone": "UTC"
        }
    },
    "data": {
        "email": "test@example.com"
    }
}

# Webhook без образовательных программ
WEBHOOK_NO_PROGRAMS: Dict[str, Any] = {
    "header_data": {
        "poll_id": 789,
        "answer_id": 101112,
        "create_time": "2025-10-22T10:00:00.000Z",
        "form_kind": 2,
        "analytics": {
            "url": "https://example.com",
            "params": {"utm_source": "direct"},
            "cookies": {"roistat_visit": "999888"},
            "ip": "192.168.1.1",
            "date": "2025-10-22 10:00",
            "timeZone": "Europe/Moscow"
        }
    },
    "data": {
        "firstname": "Мария",
        "lastname": "Петрова",
        "email": "maria.petrova@example.com",
        "telephone": "+79001112233"
    }
}

# PostPoll request
POST_POLL_REQUEST: Dict[str, Any] = {
    "poll_id": 430131691,
    "poll_name": "Опрос абитуриентов 2023",
    "poll_language": "ru",
    "employee_email": "admin@hse.ru"
}

# Bitrix24 API мок-ответы
BITRIX_POLL_FORM_RESPONSE: Dict[str, Any] = {
    "result": [
        {
            "ID": "123",
            "NAME": "Опрос абитуриентов 2023",
            "PROPERTY_64": "430131691"
        }
    ],
    "total": 1
}

BITRIX_CONTACT_RESPONSE: Dict[str, Any] = {
    "result": [
        {
            "ID": "456",
            "NAME": "Иван",
            "LAST_NAME": "Иванов",
            "EMAIL": [{"VALUE": "ivan.ivanov@example.com", "VALUE_TYPE": "WORK"}]
        }
    ],
    "total": 1
}

BITRIX_CREATE_CONTACT_RESPONSE: Dict[str, Any] = {
    "result": 789
}

BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE: Dict[str, Any] = {
    "result": [
        {
            "ID": "101",
            "NAME": "Цифровой юрист"
        },
        {
            "ID": "102",
            "NAME": "Античность"
        }
    ],
    "total": 2
}

BITRIX_DEAL_RESPONSE: Dict[str, Any] = {
    "result": [
        {
            "ID": "1001",
            "TITLE": "Сделка по ОП: Цифровой юрист",
            "CONTACT_ID": "456",
            "UF_CRM_1755626160": "101"
        }
    ],
    "total": 1
}

BITRIX_CREATE_DEAL_RESPONSE: Dict[str, Any] = {
    "result": 2002
}

BITRIX_UPDATE_DEAL_RESPONSE: Dict[str, Any] = {
    "result": True
}

BITRIX_EMPTY_RESPONSE: Dict[str, Any] = {
    "result": [],
    "total": 0
}
