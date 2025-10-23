"""
Pydantic модели для API интеграции с опросами

Схемы для запросов и ответов /postPoll и /postAnswer
Основаны на INTEGRATION_TASK.md
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ==================== postPoll Schemas ====================


class PostPollRequest(BaseModel):
    """
    Входящий запрос для регистрации/реактивации опроса

    Пример:
    {
        "poll_id": 123,
        "poll_name": "Какой у вас вопрос по ОП",
        "poll_language": "ru",
        "employee_email": "somebody@hse.ru"
    }
    """

    poll_id: int = Field(..., description="ID опросной формы")
    poll_name: str = Field(..., description="Короткое название опросной формы")
    poll_language: str = Field(..., description="Код языка по справочнику ('ru' или 'en')")
    employee_email: EmailStr = Field(
        ..., description="Email сотрудника, запросившего включение интеграции (для RBAC проверки)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "poll_id": 123,
                "poll_name": "Какой у вас вопрос по ОП",
                "poll_language": "ru",
                "employee_email": "somebody@hse.ru",
            }
        }


class PostPollResponse(BaseModel):
    """
    Ответ на запрос регистрации опроса

    Успешный ответ (HTTP 200):
    {
        "status": "success",
        "message": "Связанная опросная форма для ID 123 создана в CRM или уже существует",
        "description": "Подробности...",
        "poll_id": 123,
        "is_successful": true
    }

    Неуспешный ответ (HTTP != 200 или 200 с is_successful: false):
    {
        "status": "error",
        "message": "Опросная форма с ID 123 не создана",
        "description": "Недостаточно прав у пользователя...",
        "poll_id": 123,
        "is_successful": false
    }
    """

    status: str = Field(..., description="Статус операции: 'success' или 'error'")
    message: str = Field(..., description="Краткое сообщение о результате")
    description: Optional[str] = Field(None, description="Подробное описание результата или ошибки")
    poll_id: int = Field(..., description="ID опросной формы")
    is_successful: bool = Field(..., description="Флаг успешности операции (true/false)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": "success",
                    "message": "Связанная опросная форма для ID 123 создана в CRM или уже существует",
                    "description": "Опросная форма успешно зарегистрирована в системе",
                    "poll_id": 123,
                    "is_successful": True,
                },
                {
                    "status": "error",
                    "message": "Опросная форма с ID 123 не создана",
                    "description": "Недостаточно прав у пользователя somebody@hse.ru",
                    "poll_id": 123,
                    "is_successful": False,
                },
            ]
        }


# ==================== postAnswer Schemas ====================


class PostAnswerResponse(BaseModel):
    """
    Ответ на запрос сохранения ответа

    Успешный ответ (HTTP 200):
    {
        "status": "success",
        "message": "Ответ 345 успешно сохранён в CRM или был зарегистрирован ранее",
        "description": "Подробности...",
        "poll_id": 123,
        "answer_id": 345,
        "is_successful": true
    }

    Неуспешный ответ (HTTP != 200 или 200 с is_successful: false):
    {
        "status": "error",
        "message": "Не удалось сохранить ответ 345",
        "description": "Произошла ошибка...",
        "poll_id": 123,
        "answer_id": 345,
        "is_successful": false
    }
    """

    status: str = Field(..., description="Статус операции: 'success' или 'error'")
    message: str = Field(..., description="Краткое сообщение о результате")
    description: Optional[str] = Field(None, description="Подробное описание результата или ошибки")
    poll_id: int = Field(..., description="ID опросной формы")
    answer_id: int = Field(..., description="ID ответа")
    is_successful: bool = Field(..., description="Флаг успешности операции (true/false)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": "success",
                    "message": "Ответ 345 успешно сохранён в CRM или был зарегистрирован ранее",
                    "description": "Контакт и сделка созданы/обновлены успешно",
                    "poll_id": 123,
                    "answer_id": 345,
                    "is_successful": True,
                },
                {
                    "status": "error",
                    "message": "Не удалось сохранить ответ 345",
                    "description": "Образовательная программа 'Цифровой юрист' не найдена в системе",
                    "poll_id": 123,
                    "answer_id": 345,
                    "is_successful": False,
                },
            ]
        }


# ==================== Helper Response Creators ====================


def create_success_poll_response(poll_id: int, message: str = None) -> PostPollResponse:
    """Создать успешный ответ для postPoll"""
    return PostPollResponse(
        status="success",
        message=message
        or f"Связанная опросная форма для ID {poll_id} создана в CRM или уже существует",
        description="Опросная форма успешно зарегистрирована в системе",
        poll_id=poll_id,
        is_successful=True,
    )


def create_error_poll_response(
    poll_id: int, message: str = None, description: str = None
) -> PostPollResponse:
    """Создать ответ с ошибкой для postPoll"""
    return PostPollResponse(
        status="error",
        message=message or f"Опросная форма с ID {poll_id} не создана",
        description=description or "Произошла ошибка при обработке запроса",
        poll_id=poll_id,
        is_successful=False,
    )


def create_success_answer_response(
    poll_id: int, answer_id: int, message: str = None
) -> PostAnswerResponse:
    """Создать успешный ответ для postAnswer"""
    return PostAnswerResponse(
        status="success",
        message=message
        or f"Ответ {answer_id} успешно сохранён в CRM или был зарегистрирован ранее",
        description="Контакт и сделка созданы/обновлены успешно",
        poll_id=poll_id,
        answer_id=answer_id,
        is_successful=True,
    )


def create_error_answer_response(
    poll_id: int, answer_id: int, message: str = None, description: str = None
) -> PostAnswerResponse:
    """Создать ответ с ошибкой для postAnswer"""
    return PostAnswerResponse(
        status="error",
        message=message or f"Не удалось сохранить ответ {answer_id}",
        description=description or "Произошла ошибка при обработке запроса",
        poll_id=poll_id,
        answer_id=answer_id,
        is_successful=False,
    )
