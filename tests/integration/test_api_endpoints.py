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
    """Фикстура для мока Bitrix24 клиента"""
    with patch('app.services.integration_service.bitrix24_client') as mock:
        yield mock


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
        # Форма не найдена, будет создана новая
        mock_bitrix_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_list_element.return_value = {"result": "123"}

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True
        assert data["poll_id"] == 430131691

    def test_post_poll_already_exists(self, client, mock_bitrix_client):
        """Тест когда опросная форма уже существует"""
        mock_bitrix_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True
        assert "уже существует" in data["message"]

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
        mock_bitrix_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_list_element.side_effect = Exception("Bitrix24 API Error")

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["is_successful"] is False
        assert "Bitrix24 API Error" in data["description"]


class TestPostAnswerEndpoint:
    """Тесты для POST /postAnswer endpoint"""

    def test_post_answer_success_with_programs(self, client, mock_bitrix_client):
        """Тест успешной обработки ответа с образовательными программами"""
        # Настройка моков для успешного сценария
        mock_bitrix_client.get_list_elements.side_effect = [
            BITRIX_POLL_FORM_RESPONSE,  # find_poll_form
            BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE  # find_educational_programs
        ]
        mock_bitrix_client.get_contacts.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_contact.return_value = BITRIX_CREATE_CONTACT_RESPONSE
        mock_bitrix_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE
        mock_bitrix_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

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
        assert "Создано сделок: 2" in data["message"] or "создана" in data["message"].lower()

    def test_post_answer_success_without_programs(self, client, mock_bitrix_client):
        """Тест обработки ответа БЕЗ образовательных программ"""
        mock_bitrix_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE
        mock_bitrix_client.get_contacts.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_contact.return_value = BITRIX_CREATE_CONTACT_RESPONSE
        mock_bitrix_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE
        mock_bitrix_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

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
        mock_bitrix_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=MINIMAL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["is_successful"] is False
        assert "не найдена" in data["description"]

    def test_post_answer_program_not_found(self, client, mock_bitrix_client):
        """Тест когда образовательная программа не найдена"""
        mock_bitrix_client.get_list_elements.side_effect = [
            BITRIX_POLL_FORM_RESPONSE,  # poll form found
            BITRIX_EMPTY_RESPONSE  # programs not found
        ]
        mock_bitrix_client.get_contacts.return_value = BITRIX_CONTACT_RESPONSE

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=FULL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "error"
        assert data["is_successful"] is False
        assert "не найдены" in data["description"] or "не найдена" in data["description"]

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
        mock_bitrix_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE
        mock_bitrix_client.get_contacts.return_value = BITRIX_CONTACT_RESPONSE  # Contact found
        mock_bitrix_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE
        mock_bitrix_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=WEBHOOK_NO_PROGRAMS
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["is_successful"] is True

        # Проверяем что create_contact НЕ был вызван
        mock_bitrix_client.create_contact.assert_not_called()

    def test_post_answer_with_existing_deal(self, client, mock_bitrix_client):
        """Тест с существующей сделкой"""
        mock_bitrix_client.get_list_elements.side_effect = [
            BITRIX_POLL_FORM_RESPONSE,
            BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE
        ]
        mock_bitrix_client.get_contacts.return_value = BITRIX_CONTACT_RESPONSE
        mock_bitrix_client.get_deals.return_value = BITRIX_DEAL_RESPONSE  # Deal found
        mock_bitrix_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=FULL_WEBHOOK_PAYLOAD
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        # Сделка должна быть обновлена, а не создана
        mock_bitrix_client.create_deal.assert_not_called()


class TestAPIResponses:
    """Тесты структуры ответов API"""

    def test_post_poll_response_structure(self, client, mock_bitrix_client):
        """Тест структуры ответа postPoll"""
        mock_bitrix_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE

        response = client.post(
            "/api/v1/integration/postPoll",
            json=POST_POLL_REQUEST
        )

        data = response.json()

        # Проверяем наличие всех обязательных полей
        assert "status" in data
        assert "message" in data
        assert "poll_id" in data
        assert "is_successful" in data
        assert data["poll_id"] == POST_POLL_REQUEST["poll_id"]

    def test_post_answer_response_structure(self, client, mock_bitrix_client):
        """Тест структуры ответа postAnswer"""
        mock_bitrix_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE
        mock_bitrix_client.get_contacts.return_value = BITRIX_CONTACT_RESPONSE
        mock_bitrix_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_bitrix_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE
        mock_bitrix_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

        response = client.post(
            "/api/v1/integration/postAnswer",
            json=WEBHOOK_NO_PROGRAMS
        )

        data = response.json()

        # Проверяем наличие всех обязательных полей
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
