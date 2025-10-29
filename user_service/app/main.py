from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from user_service.app.routes import permissions, health, admin
from user_service.db.database import db
import user_service.db  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: инициализация БД
    await db.connect()
    await db.init_db()
    yield
    # Shutdown: закрытие подключений
    await db.close()
    # TODO: закрытие подключений к RabbitMQ, Redis


app = FastAPI(
    title="User Service",
    description="Сервис управления пользователями, заявками и правами",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для MVP разрешаем все
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(permissions.router, prefix="", tags=["Permissions"])
app.include_router(admin.router, tags=["Admin"])

