from fastapi import FastAPI

from app.config import settings
from app.routers import bitrix24, integration, logs

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="FastAPI project with PostgreSQL database and Bitrix24 integration",
)

# Include routers
app.include_router(logs.router, prefix="/api/v1")
app.include_router(bitrix24.router, prefix="/api/v1")
app.include_router(integration.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
