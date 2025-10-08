from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models.log import Log

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)


@router.get("/")
def get_logs(db: Session = Depends(get_db)):
    """Получить список всех логов"""
    logs = db.execute(select(Log)).scalars().all()
    return {
        "logs": [
            {
                "id": log.id,
                "created_at": log.created_at.isoformat(),
                "message": log.message
            }
            for log in logs
        ]
    }


@router.get("/{log_id}")
def get_log(log_id: int, db: Session = Depends(get_db)):
    """Получить лог по ID"""
    log = db.execute(select(Log).where(Log.id == log_id)).scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Лог не найден")

    return {
        "id": log.id,
        "created_at": log.created_at.isoformat(),
        "message": log.message
    }


@router.post("/")
def create_log(message: str, db: Session = Depends(get_db)):
    """Создать новый лог"""
    new_log = Log(message=message)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "message": "Лог создан",
        "log": {
            "id": new_log.id,
            "created_at": new_log.created_at.isoformat(),
            "message": new_log.message
        }
    }


@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    """Удалить лог"""
    log = db.execute(select(Log).where(Log.id == log_id)).scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Лог не найден")

    db.delete(log)
    db.commit()

    return {"message": "Лог удален"}
