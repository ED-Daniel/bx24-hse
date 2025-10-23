import httpx
import logging
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.retry import retry_on_network_error

logger = logging.getLogger(__name__)


class Bitrix24Client:
    """Клиент для работы с Bitrix24 REST API"""

    def __init__(self):
        self.base_url = settings.BITRIX24_WEBHOOK_URL.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        """Закрываем клиент при удалении объекта"""
        if hasattr(self, "client"):
            self.client.close()

    @retry_on_network_error(
        max_attempts=settings.BITRIX24_RETRY_MAX_ATTEMPTS,
        delay=settings.BITRIX24_RETRY_DELAY
    )
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
            logger.debug(f"Bitrix24 API: {method} with params: {params}")
            response = self.client.post(url, json=params or {})
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = f"Bitrix24 API Error: {data.get('error_description', data['error'])}"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.debug(f"Bitrix24 API: {method} success")
            return data
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

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

    # ==================== UNIVERSAL LISTS ====================

    def get_list_elements(
        self,
        iblock_id: int,
        filter: Optional[Dict[str, Any]] = None,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Получить элементы универсального списка

        Args:
            iblock_id: ID списка (инфоблока)
            filter: Фильтр (например, {'=PROPERTY_64': '123'})
            select: Список полей для выборки

        Returns:
            Словарь с результатами
        """
        params = {
            "IBLOCK_TYPE_ID": "lists",
            "IBLOCK_ID": iblock_id
        }
        if filter:
            params["FILTER"] = filter
        if select:
            params["SELECT"] = select

        return self._make_request("lists.element.get", params)

    def create_list_element(
        self,
        iblock_id: int,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать элемент универсального списка

        Args:
            iblock_id: ID списка (инфоблока)
            fields: Поля элемента

        Returns:
            ID созданного элемента
        """
        params = {
            "IBLOCK_TYPE_ID": "lists",
            "IBLOCK_ID": iblock_id,
            "ELEMENT_CODE": fields.get("CODE"),
            "FIELDS": fields
        }
        return self._make_request("lists.element.add", params)

    def update_list_element(
        self,
        iblock_id: int,
        element_id: int,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить элемент универсального списка

        Args:
            iblock_id: ID списка (инфоблока)
            element_id: ID элемента
            fields: Поля для обновления

        Returns:
            Результат обновления
        """
        params = {
            "IBLOCK_TYPE_ID": "lists",
            "IBLOCK_ID": iblock_id,
            "ELEMENT_ID": element_id,
            "FIELDS": fields
        }
        return self._make_request("lists.element.update", params)

    # ==================== BATCH OPERATIONS ====================

    def batch(self, commands: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Выполнить batch запрос к Bitrix24 API

        Позволяет выполнить до 50 команд за один запрос.

        Args:
            commands: Словарь команд вида:
                {
                    "cmd1": {"method": "crm.contact.get", "params": {"id": 1}},
                    "cmd2": {"method": "crm.deal.get", "params": {"id": 2}}
                }

        Returns:
            Результаты всех команд

        Example:
            >>> commands = {
            ...     "get_contact": {
            ...         "method": "crm.contact.get",
            ...         "params": {"id": 123}
            ...     },
            ...     "get_deal": {
            ...         "method": "crm.deal.get",
            ...         "params": {"id": 456}
            ...     }
            ... }
            >>> results = client.batch(commands)
            >>> contact = results["result"]["result"]["get_contact"]
            >>> deal = results["result"]["result"]["get_deal"]
        """
        if not settings.BATCH_ENABLED:
            logger.warning("Batch operations disabled, executing commands sequentially")
            results = {}
            for cmd_name, cmd_data in commands.items():
                results[cmd_name] = self._make_request(
                    cmd_data["method"],
                    cmd_data.get("params")
                )
            return {"result": {"result": results}}

        if len(commands) > settings.BATCH_SIZE:
            raise ValueError(
                f"Batch size {len(commands)} exceeds maximum {settings.BATCH_SIZE}"
            )

        # Формируем batch команды
        cmd_params = {}
        for cmd_name, cmd_data in commands.items():
            method = cmd_data["method"]
            params = cmd_data.get("params", {})

            # Формируем строку вызова метода
            # Битрикс24 ожидает: "crm.contact.get?id=123"
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            cmd_params[cmd_name] = f"{method}?{param_str}" if param_str else method

        logger.info(f"Batch request with {len(commands)} commands")
        return self._make_request("batch", {"cmd": cmd_params})

    def batch_get_educational_programs(
        self, program_names: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Получить несколько образовательных программ за один batch запрос

        Args:
            program_names: Список названий программ

        Returns:
            Словарь {program_name: program_data}
        """
        if not settings.BATCH_ENABLED or len(program_names) <= 1:
            # Fallback на обычные запросы
            return {}

        # Формируем batch команды
        commands = {}
        for i, name in enumerate(program_names):
            commands[f"program_{i}"] = {
                "method": "lists.element.get",
                "params": {
                    "IBLOCK_TYPE_ID": "lists",
                    "IBLOCK_ID": "18",
                    "FILTER": {"=NAME": name}
                }
            }

        result = self.batch(commands)

        # Парсим результаты
        programs = {}
        batch_results = result.get("result", {}).get("result", {})

        for i, name in enumerate(program_names):
            cmd_result = batch_results.get(f"program_{i}", {})
            if cmd_result and cmd_result.get("result"):
                programs[name] = cmd_result["result"][0]

        return programs


# Создаем глобальный экземпляр клиента
bitrix24_client = Bitrix24Client()
