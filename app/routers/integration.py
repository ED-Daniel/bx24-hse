"""
Роутер для обработки webhook'ов от системы опросных форм

Реализует API согласно INTEGRATION_TASK.md:
- POST /postPoll - Регистрация новой опросной формы
- POST /postAnswer - Обработка ответа из опросной формы
"""

import logging

from fastapi import APIRouter, status

from app.schemas.integration import (
    PostAnswerResponse,
    PostPollRequest,
    PostPollResponse,
    create_error_answer_response,
    create_error_poll_response,
    create_success_answer_response,
    create_success_poll_response,
)
from app.schemas.webhook import WebhookPayload
from app.services.integration_service import integration_service

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/integration", tags=["integration"])


@router.post("/postPoll", response_model=PostPollResponse)
async def post_poll(request: PostPollRequest):
    """
    Регистрация новой опросной формы в Bitrix24

    Создает элемент в универсальном списке "Опросные формы" (IBLOCK_ID=17)
    с указанием poll_id и других данных формы.

    Args:
        request: Данные новой опросной формы (poll_id, poll_name, poll_language, employee_email)

    Returns:
        PostPollResponse: Ответ с poll_id и статусом операции

    Example:
        POST /integration/postPoll
        {
            "poll_id": 430131691,
            "poll_name": "Опрос абитуриентов 2025",
            "poll_language": "ru",
            "employee_email": "admin@hse.ru"
        }

        Response:
        {
            "status": "success",
            "message": "Связанная опросная форма для ID 430131691 создана в CRM или уже существует",
            "description": "Опросная форма успешно зарегистрирована в системе",
            "poll_id": 430131691,
            "is_successful": true
        }
    """
    logger.info("=" * 70)
    logger.info(f"📝 Received POST /postPoll request")
    logger.info(f"   Poll ID: {request.poll_id}")
    logger.info(f"   Poll Name: {request.poll_name}")
    logger.info(f"   Language: {request.poll_language}")
    logger.info(f"   Employee: {request.employee_email}")
    logger.info("=" * 70)

    try:
        # TODO: Здесь может быть RBAC проверка на основе employee_email
        # Проверка прав пользователя на создание опросных форм

        # Проверяем, не существует ли уже такая форма
        try:
            existing_form = integration_service.find_poll_form(request.poll_id)
            if existing_form:
                logger.info(f"✅ Poll form already exists: Bitrix ID={existing_form.get('ID')}")
                return create_success_poll_response(
                    poll_id=request.poll_id,
                    message=f"Связанная опросная форма для ID {request.poll_id} уже существует в CRM",
                )
        except Exception:
            # Форма не найдена - создаем новую
            pass

        # Создаем новую опросную форму в универсальном списке
        fields = {
            "NAME": request.poll_name,
            "PROPERTY_64": str(request.poll_id),  # POLL_ID
            "PREVIEW_TEXT": f"Язык: {request.poll_language}, Создан: {request.employee_email}",
            "CODE": str(request.poll_id),
            "PROPERTY_65": f"https://portal.hse.ru/{str(request.poll_id)}",
            "PROPERTY_66": 0,
        }

        result = integration_service.client.create_list_element(
            iblock_id=integration_service.POLL_FORMS_LIST_ID, fields=fields
        )

        if result.get("result"):
            bitrix_id = result["result"]
            logger.info(f"✅ Poll form created successfully")
            logger.info(f"   Poll ID: {request.poll_id}")
            logger.info(f"   Bitrix ID: {bitrix_id}")

            return create_success_poll_response(poll_id=request.poll_id)
        else:
            raise Exception("Failed to create poll form in Bitrix24")

    except Exception as e:
        logger.error(f"❌ Error creating poll form: {e}")
        return create_error_poll_response(poll_id=request.poll_id, description=str(e))


@router.post("/postAnswer", response_model=PostAnswerResponse)
async def post_answer(payload: WebhookPayload):
    """
    Обработка ответа из опросной формы

    Выполняет полный цикл интеграции с Bitrix24:
    1. Валидация входящих данных
    2. Поиск опросной формы (404 если не найдена)
    3. Поиск/создание контакта
    4. Для каждой образовательной программы:
       - Поиск программы (404 если не найдена)
       - Поиск/создание сделки
       - Обогащение сделки (cookies, additional fields, question fields)

    Args:
        payload: Полные данные webhook от системы опросов

    Returns:
        PostAnswerResponse: Результат обработки с poll_id, answer_id и статусом

    Raises:
        HTTPException 404: Если опросная форма или образовательная программа не найдена
        HTTPException 400: Если данные невалидны (например, отсутствует email)
        HTTPException 500: При других ошибках обработки

    Example:
        POST /integration/postAnswer
        {
            "header_data": {
                "poll_id": 430131691,
                "answer_id": 814573981,
                "create_time": "2025-10-22T10:00:00.000Z",
                "form_kind": 2,
                "analytics": {
                    "url": "https://example.com/poll/123",
                    "params": {
                        "utm_source": "yandex",
                        "utm_medium": "cpc"
                    },
                    "cookies": {
                        "roistat_visit": "8467460"
                    },
                    "ip": "185.117.121.169",
                    "date": "2023-02-15 13:16",
                    "timeZone": "Europe/Moscow"
                }
            },
            "data": {
                "firstname": "Иван",
                "lastname": "Иванов",
                "email": "ivan@example.com",
                "telephone": "+79991234567",
                "educational_program_1": ["Цифровой юрист", "Античность"],
                "additionalfield1": "Учащийся 9-10 классов",
                "question1": "Ответ на вопрос 1"
            }
        }

        Response (success):
        {
            "poll_id": 430131691,
            "answer_id": 814573981,
            "is_successful": true,
            "description": "Успешно обработано. Создано сделок: 2"
        }

        Response (error - poll form not found):
        {
            "poll_id": 430131691,
            "answer_id": 814573981,
            "is_successful": false,
            "description": "Опросная форма с ID 430131691 не найдена в системе"
        }
    """
    logger.info("=" * 70)
    logger.info(f"📨 Received POST /postAnswer request")
    logger.info(f"   Poll ID: {payload.header_data.poll_id}")
    logger.info(f"   Answer ID: {payload.header_data.answer_id}")
    logger.info(f"   Email: {payload.data.email}")
    logger.info("=" * 70)

    try:
        # Запускаем полный цикл обработки через integration_service
        result = integration_service.process_webhook(payload)

        # Формируем сообщение о результате
        total_deals = result.get("total_deals", 0)

        if total_deals > 0:
            deals_info = []
            for deal in result.get("deals", []):
                status_text = "NEW" if deal["is_new"] else "EXISTING"
                deals_info.append(f"{deal['program_name']} ({status_text})")

            message = f"Успешно обработано. Создано сделок: {total_deals}"
            if deals_info:
                message += f" - {', '.join(deals_info)}"
        else:
            message = "Успешно обработано. Создана 1 общая сделка (без указания ОП)"

        logger.info(f"✅ Webhook processed successfully")
        logger.info(f"   {message}")

        return create_success_answer_response(
            poll_id=result["poll_id"], answer_id=result["answer_id"], message=message
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ Error processing webhook: {error_message}")

        # Определяем HTTP статус код на основе типа ошибки
        status.HTTP_500_INTERNAL_SERVER_ERROR

        if "не найдена" in error_message or "not found" in error_message.lower():
            status.HTTP_404_NOT_FOUND
        elif "обязателен" in error_message or "required" in error_message.lower():
            status.HTTP_400_BAD_REQUEST

        # Возвращаем структурированный ответ об ошибке
        # Важно: не raise HTTPException, а возвращаем PostAnswerResponse с is_successful=false
        # согласно INTEGRATION_TASK.md
        return create_error_answer_response(
            poll_id=payload.header_data.poll_id,
            answer_id=payload.header_data.answer_id,
            description=error_message,
        )


@router.get("/health")
async def health_check():
    """
    Проверка работоспособности интеграции

    Проверяет:
    - Доступность Bitrix24 API
    - Загрузку field_mapping.json
    - Наличие необходимых констант

    Returns:
        Dict с информацией о статусе сервиса
    """
    try:
        # Проверяем загрузку field_mapping
        has_mapping = bool(integration_service.field_mapping)

        # Проверяем константы
        has_constants = all(
            [
                integration_service.POLL_FORMS_LIST_ID,
                integration_service.EDUCATIONAL_PROGRAMS_LIST_ID,
                integration_service.POLL_ID_PROPERTY,
                integration_service.DEAL_EDUCATIONAL_PROGRAM_FIELD,
            ]
        )

        # Простая проверка доступности Bitrix24 API (пробуем получить пустой список контактов)
        try:
            integration_service.client.get_contacts(filter={"ID": 999999999})
            bitrix_available = True
        except Exception:
            bitrix_available = False

        return {
            "status": (
                "healthy" if (has_mapping and has_constants and bitrix_available) else "degraded"
            ),
            "field_mapping_loaded": has_mapping,
            "constants_configured": has_constants,
            "bitrix24_api_available": bitrix_available,
            "service": "integration",
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "integration",
            "version": "1.0.0",
        }
