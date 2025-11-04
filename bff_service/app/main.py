from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from bff_service.app.routes import permissions, health
# TODO: импорт для RabbitMQ consumer когда будет реализован


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: инициализация подключений
    # TODO: Подключение к RabbitMQ для consumer result_queue
    # TODO: Проверка доступности User Service и Access Control Service
    yield
    # Shutdown: закрытие подключений
    # TODO: Закрытие подключений к RabbitMQ
    # TODO: Закрытие HTTP клиентов (httpx.AsyncClient)


app = FastAPI(
    title="BFF Service",
    description="Backend for Frontend - единая точка входа для клиентов",
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

# TODO: Подключить RabbitMQ consumer для обработки результатов валидации
# app.include_router(rabbitmq_consumer.router, tags=["Internal"])

