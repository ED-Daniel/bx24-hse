from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Создание синхронного движка
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Функция для создания таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)


# Функция для удаления таблиц (для разработки)
def drop_tables():
    Base.metadata.drop_all(bind=engine)
