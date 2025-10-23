from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException

from app.services.bitrix24_client import bitrix24_client

router = APIRouter(prefix="/bitrix24", tags=["bitrix24"])


# ==================== CONTACTS ====================


@router.get("/contacts")
def list_contacts(start: int = 0, name: Optional[str] = None, phone: Optional[str] = None):
    """Получить список контактов с фильтрацией"""
    try:
        filter_params = {}
        if name:
            filter_params["NAME"] = name
        if phone:
            filter_params["PHONE"] = phone

        result = bitrix24_client.get_contacts(
            filter=filter_params if filter_params else None, start=start
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contacts/{contact_id}")
def get_contact(contact_id: int):
    """Получить контакт по ID"""
    try:
        result = bitrix24_client.get_contact(contact_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contacts")
def create_contact(fields: Dict[str, Any] = Body(...)):
    """
    Создать новый контакт

    Пример:
    {
        "NAME": "Иван",
        "LAST_NAME": "Иванов",
        "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
        "EMAIL": [{"VALUE": "ivan@example.com", "VALUE_TYPE": "WORK"}]
    }
    """
    try:
        result = bitrix24_client.create_contact(fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contacts/{contact_id}")
def update_contact(contact_id: int, fields: Dict[str, Any] = Body(...)):
    """Обновить контакт"""
    try:
        result = bitrix24_client.update_contact(contact_id, fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int):
    """Удалить контакт"""
    try:
        result = bitrix24_client.delete_contact(contact_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LEADS ====================


@router.get("/leads")
def list_leads(start: int = 0, title: Optional[str] = None, status_id: Optional[str] = None):
    """Получить список лидов с фильтрацией"""
    try:
        filter_params = {}
        if title:
            filter_params["TITLE"] = title
        if status_id:
            filter_params["STATUS_ID"] = status_id

        result = bitrix24_client.get_leads(
            filter=filter_params if filter_params else None, start=start
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    """Получить лид по ID"""
    try:
        result = bitrix24_client.get_lead(lead_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads")
def create_lead(fields: Dict[str, Any] = Body(...)):
    """
    Создать новый лид

    Пример:
    {
        "TITLE": "Новый лид",
        "NAME": "Иван",
        "LAST_NAME": "Петров",
        "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
        "EMAIL": [{"VALUE": "ivan@example.com", "VALUE_TYPE": "WORK"}]
    }
    """
    try:
        result = bitrix24_client.create_lead(fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, fields: Dict[str, Any] = Body(...)):
    """Обновить лид"""
    try:
        result = bitrix24_client.update_lead(lead_id, fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    """Удалить лид"""
    try:
        result = bitrix24_client.delete_lead(lead_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DEALS ====================


@router.get("/deals")
def list_deals(start: int = 0, title: Optional[str] = None, stage_id: Optional[str] = None):
    """Получить список сделок с фильтрацией"""
    try:
        filter_params = {}
        if title:
            filter_params["TITLE"] = title
        if stage_id:
            filter_params["STAGE_ID"] = stage_id

        result = bitrix24_client.get_deals(
            filter=filter_params if filter_params else None, start=start
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deals/{deal_id}")
def get_deal(deal_id: int):
    """Получить сделку по ID"""
    try:
        result = bitrix24_client.get_deal(deal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deals")
def create_deal(fields: Dict[str, Any] = Body(...)):
    """
    Создать новую сделку

    Пример:
    {
        "TITLE": "Новая сделка",
        "OPPORTUNITY": 100000,
        "CURRENCY_ID": "RUB",
        "CONTACT_ID": 1
    }
    """
    try:
        result = bitrix24_client.create_deal(fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/deals/{deal_id}")
def update_deal(deal_id: int, fields: Dict[str, Any] = Body(...)):
    """Обновить сделку"""
    try:
        result = bitrix24_client.update_deal(deal_id, fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deals/{deal_id}")
def delete_deal(deal_id: int):
    """Удалить сделку"""
    try:
        result = bitrix24_client.delete_deal(deal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
