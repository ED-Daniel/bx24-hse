"""
Сервис интеграции с Bitrix24 для обработки опросных форм

Реализует бизнес-логику согласно INTEGRATION.md:
1. Поиск опросной формы по poll_id
2. Поиск/создание контакта по email
3. Поиск образовательной программы
4. Поиск/создание/обогащение сделки
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.schemas.webhook import Analytics, WebhookData, WebhookPayload
from app.services.bitrix24_client import bitrix24_client
from app.utils.cache import cache_manager

# Настройка логирования
logger = logging.getLogger(__name__)


class BitrixIntegrationService:
    """
    Сервис для интеграции опросов с Bitrix24

    Использует field_mapping.json для правильного маппинга полей
    """

    # ID списков в Bitrix24
    POLL_FORMS_LIST_ID = 17  # Опросные формы
    EDUCATIONAL_PROGRAMS_LIST_ID = 18  # Образовательные программы

    # Коды свойств из field_mapping.json
    POLL_ID_PROPERTY = "PROPERTY_64"  # Код для poll_id в списке опросных форм
    PROGRAM_ID_PROPERTY = "PROPERTY_73"  # Код для program_id в списке ОП

    # Пользовательские поля сделки
    DEAL_EDUCATIONAL_PROGRAM_FIELD = "UF_CRM_1755626160"  # Образовательная программа
    DEAL_ROISTAT_FIELD = "UF_CRM_1755626174"  # ID Roistat

    def __init__(self):
        """Инициализация сервиса"""
        self.client = bitrix24_client
        self.cache = cache_manager
        self._load_field_mapping()
        logger.info("BitrixIntegrationService инициализирован")

    def _load_field_mapping(self):
        """Загрузить маппинг полей из field_mapping.json"""
        try:
            mapping_path = Path(__file__).parent.parent.parent / "field_mapping.json"
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.field_mapping = json.load(f)
            logger.info("Field mapping loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load field mapping: {e}")
            self.field_mapping = {}

    # ==================== STEP 1: Find Poll Form ====================

    def find_poll_form(self, poll_id: int) -> Optional[Dict[str, Any]]:
        """
        Поиск опросной формы в списке по poll_id

        Args:
            poll_id: ID опросной формы из внешней системы

        Returns:
            Словарь с данными опросной формы или None, если не найдена

        Raises:
            Exception: Если опросная форма не найдена (должен вернуться HTTP 404)
        """
        logger.info(f"Searching for poll form with poll_id={poll_id}")

        # Проверяем кеш
        if settings.CACHE_ENABLED:
            cached = self.cache.get("poll_form", poll_id)
            if cached:
                logger.info(f"Poll form found in cache: poll_id={poll_id}")
                return cached

        try:
            # Поиск в списке "Опросные формы" (IBLOCK_ID=17)
            result = self.client.get_list_elements(
                iblock_id=self.POLL_FORMS_LIST_ID,
                filter={f"={self.POLL_ID_PROPERTY}": str(poll_id)},
            )

            if result.get("result") and len(result["result"]) > 0:
                poll_form = result["result"][0]
                logger.info(f"Poll form found: ID={poll_form.get('ID')}")

                # Кешируем результат
                if settings.CACHE_ENABLED:
                    self.cache.set(
                        "poll_form", poll_id, poll_form, ttl=settings.CACHE_TTL_POLL_FORMS
                    )

                return poll_form
            else:
                logger.warning(f"Poll form with poll_id={poll_id} not found")
                raise Exception(f"Опросная форма с ID {poll_id} не найдена в системе")

        except Exception as e:
            logger.error(f"Error finding poll form: {e}")
            raise

    # ==================== STEP 2: Find or Create Contact ====================

    def find_or_create_contact(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        middlename: Optional[str] = None,
        phone: Optional[str] = None,
        analytics: Optional[Analytics] = None,
    ) -> int:
        """
        Поиск контакта по email, если не найден - создание нового

        Args:
            email: Email контакта (обязательное поле для поиска)
            firstname: Имя
            lastname: Фамилия
            middlename: Отчество
            phone: Телефон
            analytics: Аналитические данные (UTM метки)

        Returns:
            ID контакта (существующего или созданного)
        """
        logger.info(f"Searching for contact with email={email}")

        # Шаг 1: Поиск контакта по email
        try:
            result = self.client.get_contacts(
                filter={"EMAIL": email}, select=["ID", "NAME", "LAST_NAME", "EMAIL"]
            )

            if result.get("result") and len(result["result"]) > 0:
                contact_id = result["result"][0]["ID"]
                logger.info(f"Contact found: ID={contact_id}")
                return int(contact_id)

        except Exception as e:
            logger.warning(f"Error searching for contact: {e}")

        # Шаг 2: Создание нового контакта
        logger.info(f"Creating new contact for email={email}")

        contact_fields = {
            "NAME": firstname or "",
            "LAST_NAME": lastname or "",
            "SECOND_NAME": middlename or "",
            "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}],
        }

        # Добавляем телефон, если указан
        if phone:
            contact_fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]

        # Добавляем UTM метки из аналитики
        if analytics and analytics.params:
            contact_fields.update(
                {
                    "UTM_SOURCE": analytics.params.utm_source,
                    "UTM_MEDIUM": analytics.params.utm_medium,
                    "UTM_CAMPAIGN": analytics.params.utm_campaign,
                    "UTM_CONTENT": analytics.params.utm_content,
                    "UTM_TERM": analytics.params.utm_term,
                }
            )

        try:
            result = self.client.create_contact(contact_fields)
            contact_id = result.get("result")
            logger.info(f"Contact created: ID={contact_id}")
            return int(contact_id)

        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            raise Exception(f"Не удалось создать контакт: {e}")

    # ==================== STEP 3: Find Educational Programs ====================

    def find_educational_programs(self, program_names: List[str]) -> List[Dict[str, Any]]:
        """
        Поиск образовательных программ по названиям

        Args:
            program_names: Список названий образовательных программ

        Returns:
            Список найденных программ с полями ID и NAME

        Raises:
            Exception: Если хотя бы одна программа не найдена (должен вернуться HTTP 404)
        """
        if not program_names:
            logger.info("No educational programs to search")
            return []

        logger.info(f"Searching for educational programs: {program_names}")

        found_programs = []
        not_found = []
        programs_to_search = []

        # Проверяем кеш для каждой программы
        for program_name in program_names:
            if settings.CACHE_ENABLED:
                cached = self.cache.get("educational_program", program_name)
                if cached:
                    logger.info(f"Program found in cache: {program_name}")
                    found_programs.append(cached)
                    continue

            programs_to_search.append(program_name)

        # Если все программы в кеше - возвращаем результат
        if not programs_to_search:
            return found_programs

        # Пытаемся использовать batch запрос если программ больше одной
        if settings.BATCH_ENABLED and len(programs_to_search) > 1:
            logger.info(f"Using batch request for {len(programs_to_search)} programs")
            try:
                batch_results = self.client.batch_get_educational_programs(programs_to_search)

                # Обрабатываем результаты batch запроса
                programs_found_in_batch = []
                for program_name in programs_to_search:
                    if program_name in batch_results:
                        program = batch_results[program_name]
                        program_data = {"ID": program.get("ID"), "NAME": program.get("NAME")}
                        found_programs.append(program_data)
                        programs_found_in_batch.append(program_name)
                        logger.info(
                            f"Program found (batch): {program_name} (ID={program.get('ID')})"
                        )

                        # Кешируем
                        if settings.CACHE_ENABLED:
                            self.cache.set(
                                "educational_program",
                                program_name,
                                program_data,
                                ttl=settings.CACHE_TTL_EDUCATIONAL_PROGRAMS,
                            )

                # Обновляем список программ для последовательного поиска
                # Ищем только те, которые не нашли через batch
                programs_to_search = [
                    p for p in programs_to_search if p not in programs_found_in_batch
                ]

            except Exception as e:
                logger.warning(f"Batch request failed, falling back to sequential: {e}")
                # При ошибке batch - ищем все программы последовательно

        # Последовательный поиск для оставшихся программ
        for program_name in programs_to_search:
            try:
                # Поиск в списке "Образовательные программы" (IBLOCK_ID=18)
                result = self.client.get_list_elements(
                    iblock_id=self.EDUCATIONAL_PROGRAMS_LIST_ID, filter={"NAME": program_name}
                )

                if result.get("result") and len(result["result"]) > 0:
                    program = result["result"][0]
                    program_data = {"ID": program.get("ID"), "NAME": program.get("NAME")}
                    found_programs.append(program_data)
                    logger.info(f"Program found: {program_name} (ID={program.get('ID')})")

                    # Кешируем результат
                    if settings.CACHE_ENABLED:
                        self.cache.set(
                            "educational_program",
                            program_name,
                            program_data,
                            ttl=settings.CACHE_TTL_EDUCATIONAL_PROGRAMS,
                        )
                else:
                    not_found.append(program_name)
                    logger.warning(f"Program not found: {program_name}")

            except Exception as e:
                logger.error(f"Error searching for program '{program_name}': {e}")
                not_found.append(program_name)

        # Если есть программы, которые не найдены, возвращаем ошибку
        if not_found:
            raise Exception(
                f"Образовательные программы не найдены в системе: {', '.join(not_found)}"
            )

        return found_programs

    # ==================== STEP 4: Find or Create Deal ====================

    def find_or_create_deal(
        self, contact_id: int, program_id: Optional[int] = None, poll_form_id: Optional[int] = None
    ) -> Tuple[int, bool]:
        """
        Поиск сделки по CONTACT_ID и образовательной программе,
        если не найдена - создание новой

        Args:
            contact_id: ID контакта
            program_id: ID образовательной программы (элемента списка IBLOCK_ID=18)
            poll_form_id: ID опросной формы (для названия сделки)

        Returns:
            Tuple[int, bool]: (ID сделки, флаг is_new - True если создана новая)
        """
        logger.info(f"Searching for deal with contact_id={contact_id}, program_id={program_id}")

        # Шаг 1: Поиск существующей сделки
        try:
            filter_params = {"CONTACT_ID": contact_id}

            # Если указана образовательная программа, ищем по ней
            if program_id:
                filter_params[self.DEAL_EDUCATIONAL_PROGRAM_FIELD] = program_id

            result = self.client.get_deals(
                filter=filter_params,
                select=["ID", "TITLE", "CONTACT_IDS", self.DEAL_EDUCATIONAL_PROGRAM_FIELD],
            )

            if result.get("result") and len(result["result"]) > 0:
                deal_id = result["result"][0]["ID"]
                logger.info(f"Deal found: ID={deal_id}")
                return int(deal_id), False

        except Exception as e:
            logger.warning(f"Error searching for deal: {e}")

        # Шаг 2: Создание новой сделки
        logger.info(f"Creating new deal for contact_id={contact_id}")

        deal_fields = {
            "TITLE": f"Регистрация на опрос #{poll_form_id}" if poll_form_id else "Регистрация",
            "CONTACT_IDS": [contact_id],
        }

        # Добавляем образовательную программу, если указана
        if program_id:
            deal_fields[self.DEAL_EDUCATIONAL_PROGRAM_FIELD] = program_id

        try:
            result = self.client.create_deal(deal_fields)
            deal_id = result.get("result")
            logger.info(f"Deal created: ID={deal_id}")
            return int(deal_id), True

        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            raise Exception(f"Не удалось создать сделку: {e}")

    # ==================== Helper Methods ====================

    def _extract_additional_fields(self, data: WebhookData) -> Dict[str, Any]:
        """
        Извлечение дополнительных полей (additional fields и question fields)

        Args:
            data: Данные из формы опроса

        Returns:
            Словарь с дополнительными полями
        """
        additional_fields = {}

        # Получаем все поля из data
        data_dict = data.model_dump(exclude_none=True)

        # Фильтруем стандартные поля
        # hse_school - это дополнительное поле, которое должно сохраняться в JSON
        standard_fields = {
            "firstname",
            "lastname",
            "middlename",
            "email",
            "telephone",
            "birthdate",
            "address",
            "city",
            "country",
            "educational_program_1",
        }

        # Собираем все дополнительные поля
        for key, value in data_dict.items():
            if key not in standard_fields:
                additional_fields[key] = value

        logger.info(f"Extracted {len(additional_fields)} additional fields")
        return additional_fields

    def _build_deal_comment(
        self, analytics: Optional[Analytics], additional_fields: Dict[str, Any]
    ) -> str:
        """
        Создание JSON комментария для сделки

        Записывает:
        - cookies
        - additional_fields
        - question_fields
        - ip, url, date

        Args:
            analytics: Аналитические данные
            additional_fields: Дополнительные поля из формы

        Returns:
            JSON строка для поля COMMENTS
        """
        comment_data = {}

        # Добавляем cookies
        if analytics and analytics.cookies:
            comment_data["cookies"] = analytics.cookies.model_dump(exclude_none=True)

        # Добавляем дополнительные поля формы
        if additional_fields:
            comment_data["additional_fields"] = additional_fields

        # Добавляем аналитику
        if analytics:
            comment_data["analytics"] = {
                "ip": analytics.ip,
                "url": analytics.url,
                "date": analytics.date,
                "timeZone": analytics.timeZone,
            }

            # Добавляем mailingListSubscription если есть
            if analytics.mailingListSubscription is not None:
                comment_data["mailingListSubscription"] = analytics.mailingListSubscription

        return json.dumps(comment_data, ensure_ascii=False, indent=2)

    # ==================== STEP 5: Enrich Deal ====================

    def enrich_deal(
        self,
        deal_id: int,
        data: WebhookData,
        analytics: Optional[Analytics] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Обогащение сделки дополнительными данными

        Записывает в сделку:
        - UTM метки
        - Cookies, additional fields, question fields в JSON формате в поле COMMENTS
        - Roistat ID
        - Дополнительные поля из формы

        Args:
            deal_id: ID сделки
            data: Данные из формы опроса
            analytics: Аналитические данные
            additional_fields: Дополнительные поля из формы

        Returns:
            bool: True если обновление успешно
        """
        logger.info(f"Enriching deal ID={deal_id}")

        update_fields = {}

        # Добавляем UTM метки
        if analytics and analytics.params:
            update_fields.update(
                {
                    "UTM_SOURCE": analytics.params.utm_source,
                    "UTM_MEDIUM": analytics.params.utm_medium,
                    "UTM_CAMPAIGN": analytics.params.utm_campaign,
                    "UTM_CONTENT": analytics.params.utm_content,
                    "UTM_TERM": analytics.params.utm_term,
                }
            )

        # Добавляем Roistat ID
        if analytics and analytics.cookies and analytics.cookies.roistat_visit:
            update_fields[self.DEAL_ROISTAT_FIELD] = analytics.cookies.roistat_visit

        # Извлекаем дополнительные поля если не переданы
        if additional_fields is None:
            additional_fields = self._extract_additional_fields(data)

        # Создаем JSON комментарий с cookies и дополнительными полями
        comments_json = self._build_deal_comment(analytics, additional_fields)
        update_fields["COMMENTS"] = comments_json

        # Обновляем сделку
        try:
            self.client.update_deal(deal_id, update_fields)
            logger.info(
                f"Deal {deal_id} enriched successfully with {len(additional_fields)} additional fields"
            )
            return True

        except Exception as e:
            logger.error(f"Error enriching deal {deal_id}: {e}")
            raise Exception(f"Не удалось обогатить сделку: {e}")

    # ==================== Main Integration Flow ====================

    def process_webhook(self, payload: WebhookPayload) -> Dict[str, Any]:
        """
        Главный метод обработки webhook от системы опросов

        Реализует полный цикл согласно INTEGRATION.md:
        1. Валидация входящих данных
        2. Поиск опросной формы (404 если не найдена)
        3. Поиск/создание контакта
        4. Для каждой ОП из educational_program_1:
           - Поиск ОП (404 если не найдена)
           - Поиск/создание сделки
           - Обогащение сделки (cookies, additional fields, question fields)
        5. Обработка ошибок и логирование

        Args:
            payload: Полные данные webhook (WebhookPayload)

        Returns:
            Словарь с результатами обработки:
            {
                "poll_id": int,
                "answer_id": int,
                "poll_form_id": str,
                "contact_id": int,
                "deals": [
                    {
                        "program_name": str,
                        "program_id": str,
                        "deal_id": int,
                        "is_new": bool
                    }
                ],
                "total_deals": int
            }

        Raises:
            Exception: При ошибках обработки (опросная форма не найдена,
                      образовательная программа не найдена, и т.д.)
        """
        logger.info("=" * 70)
        logger.info(f"🚀 START PROCESSING WEBHOOK")
        logger.info(f"   Poll ID: {payload.header_data.poll_id}")
        logger.info(f"   Answer ID: {payload.header_data.answer_id}")
        logger.info(f"   Email: {payload.data.email}")
        logger.info("=" * 70)

        result = {
            "poll_id": payload.header_data.poll_id,
            "answer_id": payload.header_data.answer_id,
            "poll_form_id": None,
            "contact_id": None,
            "deals": [],
            "total_deals": 0,
        }

        try:
            # ========== ШАГ 1: Валидация входящих данных ==========
            logger.info("📋 STEP 1: Validating incoming data...")

            if not payload.data.email:
                raise Exception("Email обязателен для создания контакта")

            logger.info(f"✅ Validation passed")
            logger.info(f"   Email: {payload.data.email}")
            logger.info(f"   Name: {payload.data.firstname} {payload.data.lastname}")
            logger.info(f"   Programs: {payload.data.educational_program_1}")

            # ========== ШАГ 2: Поиск опросной формы ==========
            logger.info("\n🔍 STEP 2: Finding poll form...")

            poll_form = self.find_poll_form(payload.header_data.poll_id)
            result["poll_form_id"] = poll_form.get("ID")

            logger.info(f"✅ Poll form found")
            logger.info(f"   Bitrix ID: {poll_form.get('ID')}")
            logger.info(f"   Name: {poll_form.get('NAME')}")

            # ========== ШАГ 3: Поиск/создание контакта ==========
            logger.info("\n👤 STEP 3: Finding or creating contact...")

            contact_id = self.find_or_create_contact(
                email=payload.data.email,
                firstname=payload.data.firstname,
                lastname=payload.data.lastname,
                middlename=payload.data.middlename,
                phone=payload.data.telephone,
                analytics=payload.header_data.analytics,
            )
            result["contact_id"] = contact_id

            logger.info(f"✅ Contact ready")
            logger.info(f"   Contact ID: {contact_id}")

            # Извлекаем дополнительные поля один раз для всех сделок
            additional_fields = self._extract_additional_fields(payload.data)

            # ========== ШАГ 4: Обработка образовательных программ ==========
            if payload.data.educational_program_1 and len(payload.data.educational_program_1) > 0:
                logger.info(
                    f"\n🎓 STEP 4: Processing {len(payload.data.educational_program_1)} educational programs..."
                )

                # Поиск всех программ сразу (404 если хоть одна не найдена)
                programs = self.find_educational_programs(payload.data.educational_program_1)

                # Для каждой найденной программы создаем/обновляем сделку
                for program in programs:
                    program_id = int(program["ID"])
                    program_name = program["NAME"]

                    logger.info(f"\n   📚 Processing program: {program_name}")
                    logger.info(f"      Program ID: {program_id}")

                    # Поиск/создание сделки для этой программы
                    logger.info(f"      🔍 Finding or creating deal...")
                    deal_id, is_new = self.find_or_create_deal(
                        contact_id=contact_id,
                        program_id=program_id,
                        poll_form_id=poll_form.get("ID"),
                    )

                    deal_status = "Created new" if is_new else "Found existing"
                    logger.info(f"      ✅ {deal_status} deal")
                    logger.info(f"         Deal ID: {deal_id}")

                    # Обогащение сделки
                    logger.info(f"      💎 Enriching deal with additional data...")
                    self.enrich_deal(
                        deal_id=deal_id,
                        data=payload.data,
                        analytics=payload.header_data.analytics,
                        additional_fields=additional_fields,
                    )
                    logger.info(f"      ✅ Deal enriched successfully")

                    # Сохраняем результат
                    result["deals"].append(
                        {
                            "program_name": program_name,
                            "program_id": program_id,
                            "deal_id": deal_id,
                            "is_new": is_new,
                        }
                    )

                result["total_deals"] = len(result["deals"])

            else:
                # Нет образовательных программ - создаем одну сделку без программы
                logger.info(
                    "\n📝 STEP 4: No educational programs specified, creating generic deal..."
                )

                deal_id, is_new = self.find_or_create_deal(
                    contact_id=contact_id, program_id=None, poll_form_id=poll_form.get("ID")
                )

                logger.info(f"✅ Deal {'created' if is_new else 'found'}: ID={deal_id}")

                # Обогащение сделки
                self.enrich_deal(
                    deal_id=deal_id,
                    data=payload.data,
                    analytics=payload.header_data.analytics,
                    additional_fields=additional_fields,
                )

                result["deals"].append(
                    {
                        "program_name": "Общая сделка",
                        "program_id": None,
                        "deal_id": deal_id,
                        "is_new": is_new,
                    }
                )
                result["total_deals"] = 1

            # ========== ЗАВЕРШЕНИЕ ==========
            logger.info("\n" + "=" * 70)
            logger.info("✅ WEBHOOK PROCESSED SUCCESSFULLY")
            logger.info(f"   Contact ID: {result['contact_id']}")
            logger.info(f"   Total Deals: {result['total_deals']}")
            for deal in result["deals"]:
                logger.info(
                    f"   - Deal {deal['deal_id']}: {deal['program_name']} ({"NEW" if deal['is_new'] else "EXISTING"})"
                )
            logger.info("=" * 70)

            return result

        except Exception as e:
            logger.error("\n" + "=" * 70)
            logger.error("❌ ERROR PROCESSING WEBHOOK")
            logger.error(f"   Error: {str(e)}")
            logger.error("=" * 70)
            raise

    # Backward compatibility alias
    process_answer = process_webhook


# Создаем глобальный экземпляр сервиса
integration_service = BitrixIntegrationService()
