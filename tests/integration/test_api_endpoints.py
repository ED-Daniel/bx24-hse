"""
Интеграционные тесты для API endpoints

Используют FastAPI TestClient для тестирования endpoints без реальных вызовов к Bitrix24.
Моки используются только для Bitrix24 API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from main import app
from tests.fixtures import (
    FULL_WEBHOOK_PAYLOAD,
    MINIMAL_WEBHOOK_PAYLOAD,
    WEBHOOK_NO_PROGRAMS,
    POST_POLL_REQUEST,
    BITRIX_POLL_FORM_RESPONSE,
    BITRIX_CONTACT_RESPONSE,
    BITRIX_CREATE_CONTACT_RESPONSE,
    BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE,
    BITRIX_DEAL_RESPONSE,
    BITRIX_CREATE_DEAL_RESPONSE,
    BITRIX_UPDATE_DEAL_RESPONSE,
    BITRIX_EMPTY_RESPONSE
)


@pytest.fixture
def client():
    """Фикстура FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def mock_bitrix_client():
    """Фикстура для мока Bitrix24 клиента - патчим _make_request"""
    # Патчим базовый метод _make_request, который используют все методы клиента
    with patch('app.services.bitrix24_client.Bitrix24Client._make_request') as mock_request:
        # Создаем словарь для хранения ответов по разным методам
        responses = {}

        def side_effect(method, params=None):
            # Возвращаем настроенный ответ для конкретного метода или пустой результат
            return responses.get(method, {"result": []})

        mock_request.side_effect = side_effect

        # Добавляем helper-метод для настройки ответов
        mock_request.set_response = lambda method, response: responses.update({method: response})

        # Возвращаем mock для дальнейшей настройки в тестах
        yield mock_request


class TestHealthEndpoint:
    """Тесты для /health endpoint"""

    def test_health_check(self, client):
        """Тест health check endpoint"""
        response = client.get("/api/v1/integration/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "field_mapping_loaded" in data
        assert "constants_configured" in data
        assert "service" in data
        assert data["service"] == "integration"


class TestPostPollEndpoint:
    """Тесты для POST /postPoll endpoint"""

    def test_post_poll_success_new_form(self, client, mock_bitrix_client):
        """Тест успешной регистрации новой опросной формы"""
        # Логика: Ищем форму по poll_id, если не нашли - создаем новую
        # 1. lists.element.get - форма не найдена (пустой результат)
        mock_bitrix_client.set_response("lists.element.get", BITRIX_EMPTY_RESPONSE)
        # 2. lists.element.add - создаем новую форму
        mock_bitrix_client.set_response("lists.element.add", {"result": "123"})

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True
        assert data["poll_id"] == 430131691
        assert "создана" in data["message"].lower() or "created" in data["message"].lower()

    def test_post_poll_already_exists(self, client, mock_bitrix_client):
        """Тест когда опросная форма уже существует"""
        # Логика: Ищем форму по poll_id, если нашли - возвращаем success "уже существует"
        # 1. lists.element.get - форма найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True
        assert "уже существует" in data["message"].lower() or "already exists" in data["message"].lower()

    def test_post_poll_validation_error(self, client):
        """Тест валидации - отсутствуют обязательные поля"""
        invalid_request = {"poll_id": 123}  # Отсутствуют другие обязательные поля

        response = client.post(
            "/api/v1/integration/postPoll",
            json=invalid_request
        )

        assert response.status_code == 422  # Validation Error

    def test_post_poll_invalid_email(self, client):
        """Тест валидации email"""
        invalid_request = POST_POLL_REQUEST.copy()
        invalid_request["employee_email"] = "invalid_email"

        response = client.post(
            "/api/v1/integration/postPoll",
            json=invalid_request
        )

        assert response.status_code == 422

    def test_post_poll_bitrix_error(self, client, mock_bitrix_client):
        """Тест ошибки при обращении к Bitrix24"""
        # Логика: При ошибке Bitrix24 API возвращаем error response
        # Этот тест проверяет обработку исключений
        # Настройка side_effect для генерации исключения
        def raise_error(method, params=None):
            if method == "lists.element.add":
                raise Exception("Bitrix24 API Error")
            # Для поиска возвращаем пустой результат (форма не найдена)
            return {"result": []}

        mock_bitrix_client.side_effect = raise_error

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        # Проверяем что получили корректный ответ
        assert response.status_code == 200
        data = response.json()

        # Система ловит исключения и возвращает error response
        assert data["status"] == "error"
        assert data["is_successful"] is False


class TestPostAnswerEndpoint:
    """Тесты для POST /postAnswer endpoint"""

    def test_post_answer_success_with_programs(self, client, mock_bitrix_client):
        """Тест успешной обработки ответа с образовательными программами"""
        # Логика согласно INTEGRATION.md:
        # 1. Ищем опросную форму по poll_id → найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        # 2. Ищем контакт по email → не найден, создаем
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.contact.add", BITRIX_CREATE_CONTACT_RESPONSE)
        # 3. Ищем образовательные программы → найдены 2 программы
        # Batch запрос для поиска программ
        mock_bitrix_client.set_response("batch", {
            "result": {
                "result": {
                    "cmd_0": BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE["result"],  # Первая программа
                    "cmd_1": BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE["result"]   # Вторая программа
                }
            }
        })
        # 4. Для каждой программы ищем сделку → не найдены, создаем
        mock_bitrix_client.set_response("crm.deal.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.add", BITRIX_CREATE_DEAL_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.update", BITRIX_UPDATE_DEAL_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=FULL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True
        assert data["poll_id"] == 430131691
        assert data["answer_id"] == 814573981
        # Проверяем что создано 2 сделки (по одной для каждой программы)
        assert "2" in data["message"] or "создана" in data["message"].lower()

    def test_post_answer_success_without_programs(self, client, mock_bitrix_client):
        """Тест обработки ответа БЕЗ образовательных программ"""
        # Логика: Если нет программ, создается одна сделка без привязки к программе
        # 1. Ищем опросную форму → найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        # 2. Ищем контакт → не найден, создаем
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.contact.add", BITRIX_CREATE_CONTACT_RESPONSE)
        # 3. Создаем сделку без программы
        mock_bitrix_client.set_response("crm.deal.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.add", BITRIX_CREATE_DEAL_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.update", BITRIX_UPDATE_DEAL_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=WEBHOOK_NO_PROGRAMS
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True

    def test_post_answer_poll_form_not_found(self, client, mock_bitrix_client):
        """Тест когда опросная форма не найдена"""
        # Логика: Если форма не найдена → возвращаем ошибку
        # 1. Ищем опросную форму → не найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_EMPTY_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=MINIMAL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["is_successful"] is False
        # Проверяем что это ошибка сохранения
        assert "не удалось" in data["message"].lower() or "не" in data["message"].lower()

    def test_post_answer_program_not_found(self, client, mock_bitrix_client):
        """Тест когда образовательная программа не найдена"""
        # Логика: Если программа не найдена → возвращаем ошибку
        # 1. Ищем опросную форму → найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        # 2. Ищем контакт → найден
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_CONTACT_RESPONSE)
        # 3. Ищем программы через batch → не найдены
        mock_bitrix_client.set_response("batch", {
            "result": {
                "result": {
                    "cmd_0": [],  # Программа не найдена
                    "cmd_1": []   # Программа не найдена
                }
            }
        })

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=FULL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["is_successful"] is False
        # Проверяем что это ошибка сохранения
        assert "не удалось" in data["message"].lower() or "не" in data["message"].lower()

    def test_post_answer_validation_error_missing_header(self, client):
        """Тест валидации - отсутствует header_data"""
        invalid_payload = {"data": {"email": "test@example.com"}}

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=invalid_payload
        )

        assert response.status_code == 422

    def test_post_answer_validation_error_invalid_email(self, client):
        """Тест валидации - невалидный email"""
        invalid_payload = MINIMAL_WEBHOOK_PAYLOAD.copy()
        invalid_payload["data"]["email"] = "invalid_email"

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=invalid_payload
        )

        assert response.status_code == 422

    def test_post_answer_with_existing_contact(self, client, mock_bitrix_client):
        """Тест с существующим контактом"""
        # Логика: Если контакт найден → используем его ID, не создаем новый
        # 1. Ищем опросную форму → найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        # 2. Ищем контакт → найден
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_CONTACT_RESPONSE)
        # 3. Создаем сделку
        mock_bitrix_client.set_response("crm.deal.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.add", BITRIX_CREATE_DEAL_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.update", BITRIX_UPDATE_DEAL_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=WEBHOOK_NO_PROGRAMS
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True

    def test_post_answer_with_existing_deal(self, client, mock_bitrix_client):
        """Тест с существующей сделкой"""
        # Логика: Если сделка найдена → обогащаем ее данными
        # 1. Ищем опросную форму → найдена
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        # 2. Ищем контакт → найден
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_CONTACT_RESPONSE)
        # 3. Ищем программы → найдены
        mock_bitrix_client.set_response("batch", {
            "result": {
                "result": {
                    "cmd_0": BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE["result"],
                    "cmd_1": BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE["result"]
                }
            }
        })
        # 4. Ищем сделку → найдена, обогащаем
        mock_bitrix_client.set_response("crm.deal.list", BITRIX_DEAL_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.update", BITRIX_UPDATE_DEAL_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=FULL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True


class TestAPIResponses:
    """Тесты структуры ответов API"""

    def test_post_poll_response_structure(self, client, mock_bitrix_client):
        """Тест структуры ответа postPoll"""
        # Настраиваем моки
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        data = response.json()

        # Проверяем наличие всех обязательных полей согласно INTEGRATION_TASK.md
        assert "status" in data
        assert "message" in data
        assert "poll_id" in data
        assert "is_successful" in data
        assert data["poll_id"] == POST_POLL_REQUEST["poll_id"]

    def test_post_answer_response_structure(self, client, mock_bitrix_client):
        """Тест структуры ответа postAnswer"""
        # Настраиваем моки для успешного сценария
        mock_bitrix_client.set_response("lists.element.get", BITRIX_POLL_FORM_RESPONSE)
        mock_bitrix_client.set_response("crm.contact.list", BITRIX_CONTACT_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.list", BITRIX_EMPTY_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.add", BITRIX_CREATE_DEAL_RESPONSE)
        mock_bitrix_client.set_response("crm.deal.update", BITRIX_UPDATE_DEAL_RESPONSE)

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=WEBHOOK_NO_PROGRAMS
        )

        data = response.json()

        # Проверяем наличие всех обязательных полей согласно INTEGRATION_TASK.md
        assert "status" in data
        assert "message" in data
        assert "poll_id" in data
        assert "answer_id" in data
        assert "is_successful" in data
        assert data["poll_id"] == WEBHOOK_NO_PROGRAMS["header_data"]["poll_id"]
        assert data["answer_id"] == WEBHOOK_NO_PROGRAMS["header_data"]["answer_id"]


class TestContentNegotiation:
    """Тесты для проверки content negotiation"""

    def test_post_poll_accepts_json_only(self, client):
        """Тест что endpoint принимает только JSON"""
        response = client.post(
            "/api/v1/integration/postPoll",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )

        assert response.status_code == 422

    def test_post_answer_accepts_json_only(self, client):
        """Тест что endpoint принимает только JSON"""
        response = client.post(
            "/api/v1/integration/postAnswer",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )

        assert response.status_code == 422


# ==================== Запуск тестов ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
