"""
Юнит-тесты для BitrixIntegrationService

Используют моки для Bitrix24 API, не выполняют реальные запросы.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from app.services.integration_service import BitrixIntegrationService
from app.schemas.webhook import WebhookPayload, Analytics, HeaderData, WebhookData
from tests.fixtures import (
    FULL_WEBHOOK_PAYLOAD,
    MINIMAL_WEBHOOK_PAYLOAD,
    WEBHOOK_NO_PROGRAMS,
    BITRIX_POLL_FORM_RESPONSE,
    BITRIX_CONTACT_RESPONSE,
    BITRIX_CREATE_CONTACT_RESPONSE,
    BITRIX_EDUCATIONAL_PROGRAMS_RESPONSE,
    BITRIX_DEAL_RESPONSE,
    BITRIX_CREATE_DEAL_RESPONSE,
    BITRIX_UPDATE_DEAL_RESPONSE,
    BITRIX_EMPTY_RESPONSE
)


class TestBitrixIntegrationService:
    """Тесты для BitrixIntegrationService"""

    @pytest.fixture
    def service(self):
        """Фикстура для создания экземпляра сервиса"""
        with patch('app.services.integration_service.bitrix24_client'):
            service = BitrixIntegrationService()
            return service

    @pytest.fixture
    def mock_client(self, service):
        """Фикстура для мока Bitrix24 клиента"""
        return service.client

    # ==================== Тесты find_poll_form ====================

    def test_find_poll_form_success(self, service, mock_client):
        """Тест успешного поиска опросной формы"""
        mock_client.get_list_elements.return_value = BITRIX_POLL_FORM_RESPONSE

        result = service.find_poll_form(430131691)

        assert result is not None
        assert result["ID"] == "123"
        assert result["NAME"] == "Опрос абитуриентов 2023"
        mock_client.get_list_elements.assert_called_once_with(
            iblock_id=17,
            filter={"=PROPERTY_64": "430131691"}
        )

    def test_find_poll_form_not_found(self, service, mock_client):
        """Тест когда опросная форма не найдена"""
        mock_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE

        with pytest.raises(Exception) as exc_info:
            service.find_poll_form(999999)

        assert "не найдена в системе" in str(exc_info.value)

    # ==================== Тесты find_or_create_contact ====================

    def test_find_existing_contact(self, service, mock_client):
        """Тест поиска существующего контакта"""
        mock_client.get_contacts.return_value = BITRIX_CONTACT_RESPONSE

        contact_id = service.find_or_create_contact(
            email="ivan.ivanov@example.com",
            firstname="Иван",
            lastname="Иванов"
        )

        assert contact_id == 456
        mock_client.get_contacts.assert_called_once()
        mock_client.create_contact.assert_not_called()

    def test_create_new_contact(self, service, mock_client):
        """Тест создания нового контакта"""
        mock_client.get_contacts.return_value = BITRIX_EMPTY_RESPONSE
        mock_client.create_contact.return_value = BITRIX_CREATE_CONTACT_RESPONSE

        contact_id = service.find_or_create_contact(
            email="new.user@example.com",
            firstname="Новый",
            lastname="Пользователь",
            phone="+79001112233"
        )

        assert contact_id == 789
        mock_client.get_contacts.assert_called_once()
        mock_client.create_contact.assert_called_once()

    def test_create_contact_with_utm(self, service, mock_client):
        """Тест создания контакта с UTM метками"""
        mock_client.get_contacts.return_value = BITRIX_EMPTY_RESPONSE
        mock_client.create_contact.return_value = BITRIX_CREATE_CONTACT_RESPONSE

        payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)
        analytics = payload.header_data.analytics

        contact_id = service.find_or_create_contact(
            email="test@example.com",
            firstname="Test",
            analytics=analytics
        )

        assert contact_id == 789

        # Проверяем что UTM метки были переданы
        call_args = mock_client.create_contact.call_args[0][0]
        assert call_args["UTM_SOURCE"] == "yandex"
        assert call_args["UTM_MEDIUM"] == "cpc"
        assert call_args["UTM_CAMPAIGN"] == "spring_admission_2023"

    # ==================== Тесты find_educational_programs ====================

    def test_find_educational_programs_success(self, service, mock_client):
        """Тест успешного поиска образовательных программ"""
        # Мок для batch запроса (возвращает обе программы)
        mock_client.batch_get_educational_programs.return_value = {
            "Цифровой юрист": {"ID": "101", "NAME": "Цифровой юрист"},
            "Античность": {"ID": "102", "NAME": "Античность"}
        }

        programs = service.find_educational_programs(["Цифровой юрист", "Античность"])

        assert len(programs) == 2
        # Проверяем что обе программы найдены (порядок может быть любым)
        program_names = [p["NAME"] for p in programs]
        assert "Цифровой юрист" in program_names
        assert "Античность" in program_names

    def test_find_educational_programs_not_found(self, service, mock_client):
        """Тест когда программы не найдены"""
        mock_client.get_list_elements.return_value = BITRIX_EMPTY_RESPONSE

        with pytest.raises(Exception) as exc_info:
            service.find_educational_programs(["Несуществующая программа"])

        assert "не найдены в системе" in str(exc_info.value)

    def test_find_educational_programs_partial_match(self, service, mock_client):
        """Тест когда найдена только часть программ"""
        # Batch запрос находит только первую программу
        mock_client.batch_get_educational_programs.return_value = {
            "Цифровой юрист": {"ID": "101", "NAME": "Цифровой юрист"}
            # "Несуществующая" не найдена
        }

        with pytest.raises(Exception) as exc_info:
            service.find_educational_programs(["Цифровой юрист", "Несуществующая"])

        assert "не найдены в системе" in str(exc_info.value)
        assert "Несуществующая" in str(exc_info.value)

    # ==================== Тесты find_or_create_deal ====================

    def test_find_existing_deal(self, service, mock_client):
        """Тест поиска существующей сделки"""
        mock_client.get_deals.return_value = BITRIX_DEAL_RESPONSE

        deal_id, is_new = service.find_or_create_deal(
            contact_id=456,
            program_id=101,
            poll_form_id=123
        )

        assert deal_id == 1001
        assert is_new is False
        mock_client.get_deals.assert_called_once()
        mock_client.create_deal.assert_not_called()

    def test_create_new_deal(self, service, mock_client):
        """Тест создания новой сделки"""
        mock_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE

        deal_id, is_new = service.find_or_create_deal(
            contact_id=456,
            program_id=101,
            poll_form_id=123
        )

        assert deal_id == 2002
        assert is_new is True
        mock_client.get_deals.assert_called_once()
        mock_client.create_deal.assert_called_once()

    def test_create_deal_without_program(self, service, mock_client):
        """Тест создания сделки без образовательной программы"""
        mock_client.get_deals.return_value = BITRIX_EMPTY_RESPONSE
        mock_client.create_deal.return_value = BITRIX_CREATE_DEAL_RESPONSE

        deal_id, is_new = service.find_or_create_deal(
            contact_id=456,
            program_id=None,
            poll_form_id=123
        )

        assert deal_id == 2002
        assert is_new is True

        # Проверяем что программа не была добавлена в fields
        call_args = mock_client.create_deal.call_args[0][0]
        assert "UF_CRM_1755626160" not in call_args

    # ==================== Тесты enrich_deal ====================

    def test_enrich_deal_with_full_data(self, service, mock_client):
        """Тест обогащения сделки полными данными"""
        mock_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

        payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)
        analytics = payload.header_data.analytics

        result = service.enrich_deal(
            deal_id=1001,
            data=payload.data,
            analytics=analytics
        )

        assert result is True
        mock_client.update_deal.assert_called_once()

        # Проверяем переданные данные
        call_args = mock_client.update_deal.call_args[0]
        deal_id = call_args[0]
        fields = call_args[1]

        assert deal_id == 1001
        assert fields["UTM_SOURCE"] == "yandex"
        assert fields["UTM_MEDIUM"] == "cpc"
        assert fields["UF_CRM_1755626174"] == "8467460"  # Roistat ID
        assert "COMMENTS" in fields

        # Проверяем JSON в COMMENTS
        comments = json.loads(fields["COMMENTS"])
        assert "cookies" in comments
        assert "additional_fields" in comments
        assert "analytics" in comments

    def test_enrich_deal_minimal_data(self, service, mock_client):
        """Тест обогащения сделки минимальными данными"""
        mock_client.update_deal.return_value = BITRIX_UPDATE_DEAL_RESPONSE

        payload = WebhookPayload(**MINIMAL_WEBHOOK_PAYLOAD)

        result = service.enrich_deal(
            deal_id=1001,
            data=payload.data,
            analytics=None
        )

        assert result is True
        mock_client.update_deal.assert_called_once()

    # ==================== Тесты _extract_additional_fields ====================

    def test_extract_additional_fields(self, service):
        """Тест извлечения дополнительных полей"""
        payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)

        additional_fields = service._extract_additional_fields(payload.data)

        # Проверяем что стандартные поля НЕ включены
        assert "firstname" not in additional_fields
        assert "lastname" not in additional_fields
        assert "email" not in additional_fields
        assert "educational_program_1" not in additional_fields

        # Проверяем что дополнительные поля включены
        assert "additionalfield1" in additional_fields
        assert "additionalfield3" in additional_fields
        assert "hse_school" in additional_fields
        assert "question1" in additional_fields
        assert "question2" in additional_fields

    def test_extract_additional_fields_empty(self, service):
        """Тест когда нет дополнительных полей"""
        payload = WebhookPayload(**MINIMAL_WEBHOOK_PAYLOAD)

        additional_fields = service._extract_additional_fields(payload.data)

        assert additional_fields == {}

    # ==================== Тесты _build_deal_comment ====================

    def test_build_deal_comment_full(self, service):
        """Тест построения комментария с полными данными"""
        payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)
        analytics = payload.header_data.analytics
        additional_fields = service._extract_additional_fields(payload.data)

        comment = service._build_deal_comment(analytics, additional_fields)
        comment_data = json.loads(comment)

        assert "cookies" in comment_data
        assert "additional_fields" in comment_data
        assert "analytics" in comment_data
        assert "mailingListSubscription" in comment_data

        assert comment_data["cookies"]["roistat_visit"] == "8467460"
        assert comment_data["additional_fields"]["question1"] is not None
        assert comment_data["analytics"]["ip"] == "185.117.121.169"

    def test_build_deal_comment_minimal(self, service):
        """Тест построения комментария с минимальными данными"""
        comment = service._build_deal_comment(None, {})
        comment_data = json.loads(comment)

        assert comment_data == {}

    # ==================== Тесты process_webhook ====================

    @patch('app.services.integration_service.BitrixIntegrationService.find_poll_form')
    @patch('app.services.integration_service.BitrixIntegrationService.find_or_create_contact')
    @patch('app.services.integration_service.BitrixIntegrationService.find_educational_programs')
    @patch('app.services.integration_service.BitrixIntegrationService.find_or_create_deal')
    @patch('app.services.integration_service.BitrixIntegrationService.enrich_deal')
    def test_process_webhook_with_programs(
        self,
        mock_enrich,
        mock_deal,
        mock_programs,
        mock_contact,
        mock_poll_form,
        service
    ):
        """Тест полной обработки webhook с образовательными программами"""
        # Настройка моков
        mock_poll_form.return_value = {"ID": "123", "NAME": "Test Poll"}
        mock_contact.return_value = 456
        mock_programs.return_value = [
            {"ID": "101", "NAME": "Цифровой юрист"},
            {"ID": "102", "NAME": "Античность"}
        ]
        mock_deal.side_effect = [(1001, True), (1002, False)]
        mock_enrich.return_value = True

        payload = WebhookPayload(**FULL_WEBHOOK_PAYLOAD)
        result = service.process_webhook(payload)

        # Проверки результата
        assert result["poll_id"] == 430131691
        assert result["answer_id"] == 814573981
        assert result["contact_id"] == 456
        assert result["total_deals"] == 2
        assert len(result["deals"]) == 2

        assert result["deals"][0]["program_name"] == "Цифровой юрист"
        assert result["deals"][0]["deal_id"] == 1001
        assert result["deals"][0]["is_new"] is True

        assert result["deals"][1]["program_name"] == "Античность"
        assert result["deals"][1]["deal_id"] == 1002
        assert result["deals"][1]["is_new"] is False

        # Проверяем что все методы были вызваны
        mock_poll_form.assert_called_once_with(430131691)
        mock_contact.assert_called_once()
        mock_programs.assert_called_once()
        assert mock_deal.call_count == 2
        assert mock_enrich.call_count == 2

    @patch('app.services.integration_service.BitrixIntegrationService.find_poll_form')
    @patch('app.services.integration_service.BitrixIntegrationService.find_or_create_contact')
    @patch('app.services.integration_service.BitrixIntegrationService.find_or_create_deal')
    @patch('app.services.integration_service.BitrixIntegrationService.enrich_deal')
    def test_process_webhook_without_programs(
        self,
        mock_enrich,
        mock_deal,
        mock_contact,
        mock_poll_form,
        service
    ):
        """Тест обработки webhook БЕЗ образовательных программ"""
        mock_poll_form.return_value = {"ID": "789"}
        mock_contact.return_value = 999
        mock_deal.return_value = (3003, True)
        mock_enrich.return_value = True

        payload = WebhookPayload(**WEBHOOK_NO_PROGRAMS)
        result = service.process_webhook(payload)

        assert result["total_deals"] == 1
        assert result["deals"][0]["program_name"] == "Общая сделка"
        assert result["deals"][0]["deal_id"] == 3003

    @patch('app.services.integration_service.BitrixIntegrationService.find_poll_form')
    def test_process_webhook_poll_form_not_found(self, mock_poll_form, service):
        """Тест когда опросная форма не найдена"""
        mock_poll_form.side_effect = Exception("Опросная форма не найдена")

        payload = WebhookPayload(**MINIMAL_WEBHOOK_PAYLOAD)

        with pytest.raises(Exception) as exc_info:
            service.process_webhook(payload)

        assert "не найдена" in str(exc_info.value)

    @patch('app.services.integration_service.BitrixIntegrationService.find_poll_form')
    def test_process_webhook_email_missing(self, mock_poll_form, service):
        """Тест когда email отсутствует"""
        mock_poll_form.return_value = {"ID": "123"}

        # Создаем payload без email
        payload_data = MINIMAL_WEBHOOK_PAYLOAD.copy()
        payload_data["data"] = {}

        payload = WebhookPayload(**payload_data)

        with pytest.raises(Exception) as exc_info:
            service.process_webhook(payload)

        assert "обязателен" in str(exc_info.value)


# ==================== Запуск тестов ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
