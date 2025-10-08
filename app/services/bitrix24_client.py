import httpx
from typing import Optional, Dict, Any, List
from app.config import settings


class Bitrix24Client:
    """Клиент для работы с Bitrix24 REST API"""

    def __init__(self):
        self.base_url = settings.BITRIX24_WEBHOOK_URL.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        """Закрываем клиент при удалении объекта"""
        if hasattr(self, "client"):
            self.client.close()

    def _make_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполнить запрос к Bitrix24 API

        Args:
            method: Название метода API (например, 'crm.contact.list')
            params: Параметры запроса

        Returns:
            Ответ от API в виде словаря
        """
        url = f"{self.base_url}{method}"

        try:
            response = self.client.post(url, json=params or {})
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Exception(f"Bitrix24 API Error: {data.get('error_description', data['error'])}")

            return data
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    # ==================== CONTACTS ====================

    def get_contacts(
        self,
        filter: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Получить список контактов

        Args:
            filter: Фильтр (например, {'NAME': 'Иван'})
            select: Список полей для выборки
            start: Смещение для пагинации

        Returns:
            Словарь с результатами
        """
        params = {"start": start}
        if filter:
            params["filter"] = filter
        if select:
            params["select"] = select

        return self._make_request("crm.contact.list", params)

    def get_contact(self, contact_id: int) -> Dict[str, Any]:
        """
        Получить контакт по ID

        Args:
            contact_id: ID контакта

        Returns:
            Данные контакта
        """
        params = {"id": contact_id}
        return self._make_request("crm.contact.get", params)

    def create_contact(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новый контакт

        Args:
            fields: Поля контакта (NAME, PHONE, EMAIL и т.д.)

        Returns:
            ID созданного контакта
        """
        params = {"fields": fields}
        return self._make_request("crm.contact.add", params)

    def update_contact(self, contact_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновить контакт

        Args:
            contact_id: ID контакта
            fields: Поля для обновления

        Returns:
            Результат обновления
        """
        params = {"id": contact_id, "fields": fields}
        return self._make_request("crm.contact.update", params)

    def delete_contact(self, contact_id: int) -> Dict[str, Any]:
        """
        Удалить контакт

        Args:
            contact_id: ID контакта

        Returns:
            Результат удаления
        """
        params = {"id": contact_id}
        return self._make_request("crm.contact.delete", params)

    # ==================== LEADS ====================

    def get_leads(
        self,
        filter: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Получить список лидов

        Args:
            filter: Фильтр
            select: Список полей для выборки
            start: Смещение для пагинации

        Returns:
            Словарь с результатами
        """
        params = {"start": start}
        if filter:
            params["filter"] = filter
        if select:
            params["select"] = select

        return self._make_request("crm.lead.list", params)

    def get_lead(self, lead_id: int) -> Dict[str, Any]:
        """
        Получить лид по ID

        Args:
            lead_id: ID лида

        Returns:
            Данные лида
        """
        params = {"id": lead_id}
        return self._make_request("crm.lead.get", params)

    def create_lead(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новый лид

        Args:
            fields: Поля лида (TITLE, NAME, PHONE, EMAIL и т.д.)

        Returns:
            ID созданного лида
        """
        params = {"fields": fields}
        return self._make_request("crm.lead.add", params)

    def update_lead(self, lead_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновить лид

        Args:
            lead_id: ID лида
            fields: Поля для обновления

        Returns:
            Результат обновления
        """
        params = {"id": lead_id, "fields": fields}
        return self._make_request("crm.lead.update", params)

    def delete_lead(self, lead_id: int) -> Dict[str, Any]:
        """
        Удалить лид

        Args:
            lead_id: ID лида

        Returns:
            Результат удаления
        """
        params = {"id": lead_id}
        return self._make_request("crm.lead.delete", params)

    # ==================== DEALS ====================

    def get_deals(
        self,
        filter: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Получить список сделок

        Args:
            filter: Фильтр
            select: Список полей для выборки
            start: Смещение для пагинации

        Returns:
            Словарь с результатами
        """
        params = {"start": start}
        if filter:
            params["filter"] = filter
        if select:
            params["select"] = select

        return self._make_request("crm.deal.list", params)

    def get_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Получить сделку по ID

        Args:
            deal_id: ID сделки

        Returns:
            Данные сделки
        """
        params = {"id": deal_id}
        return self._make_request("crm.deal.get", params)

    def create_deal(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новую сделку

        Args:
            fields: Поля сделки (TITLE, OPPORTUNITY, CONTACT_ID и т.д.)

        Returns:
            ID созданной сделки
        """
        params = {"fields": fields}
        return self._make_request("crm.deal.add", params)

    def update_deal(self, deal_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновить сделку

        Args:
            deal_id: ID сделки
            fields: Поля для обновления

        Returns:
            Результат обновления
        """
        params = {"id": deal_id, "fields": fields}
        return self._make_request("crm.deal.update", params)

    def delete_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Удалить сделку

        Args:
            deal_id: ID сделки

        Returns:
            Результат удаления
        """
        params = {"id": deal_id}
        return self._make_request("crm.deal.delete", params)


# Создаем глобальный экземпляр клиента
bitrix24_client = Bitrix24Client()
