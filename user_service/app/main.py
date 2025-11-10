from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from user_service.app.routes import permissions, health, admin
from user_service.db.database import db
from user_service.services.redis_client import redis_client
from user_service.services.rabbitmq_manager import rabbitmq_manager
from user_service.services.result_consumer import result_consumer
import user_service.db  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Глобальный lifecycle User Service."""

    # --- Startup -------------------------------------------------------------
    try:
        await db.connect()
        await db.init_db()
        logger.info("База данных подключена и схема инициализирована")
    except Exception:
        logger.exception("Не удалось подключиться к базе данных")
        raise

    try:
        await redis_client.connect()
        logger.info("Redis соединение установлено")
    except Exception:  
        logger.exception("Не удалось подключиться к Redis")
        await db.close()
        raise

    try:
        await rabbitmq_manager.connect()
        logger.info("RabbitMQ менеджер инициализирован")
    except Exception:  
        logger.exception("Не удалось инициализировать RabbitMQ менеджер")
        await redis_client.close()
        await db.close()
        raise

    consumer_task: asyncio.Task | None = None
    try:
        consumer_task = asyncio.create_task(result_consumer.start_consuming())
        logger.info("Consumer для result_queue запущен как фоновая задача")
    except Exception:
        logger.exception("Не удалось запустить consumer для result_queue")
        await rabbitmq_manager.close()
        await redis_client.close()
        await db.close()
        raise

    try:
        yield
    finally:
        if consumer_task is not None:
            try:
                await result_consumer.stop_consuming()
                await asyncio.sleep(1)
                if not consumer_task.done():
                    consumer_task.cancel()
                    try:
                        await consumer_task
                    except asyncio.CancelledError:
                        pass
                logger.info("Consumer для result_queue остановлен")
            except Exception:
                logger.exception("Ошибка при остановке consumer")

        try:
            await rabbitmq_manager.close()
            logger.info("RabbitMQ соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии RabbitMQ соединения")

        try:
            await redis_client.close()
            logger.info("Redis соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии Redis соединения")

        try:
            await db.close()
            logger.info("База данных соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии базы данных соединения")


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

