from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from user_service.app.routes import permissions, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: подключение к БД, RabbitMQ, Redis
    # TODO: инициализация подключений
    yield
    # Shutdown: закрытие подключений
    # TODO: закрытие подключений


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

