from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
import sys

from user_service.routes import permissions, health, admin
from user_service.dependencies import (
    get_database,
    get_redis_client,
    get_rabbitmq_manager,
    get_settings_dependency,
)
from user_service.services.result_consumer import ResultConsumer
from user_service.services.permission_service_factory import PermissionServiceFactory

settings = get_settings_dependency()
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("redis").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = get_database()
    redis_client = get_redis_client()
    rabbitmq_manager = get_rabbitmq_manager()

    try:
        await db.connect()
        await db.init_db()
        logger.debug("База данных подключена и схема инициализирована")
    except Exception:
        logger.exception("Не удалось подключиться к базе данных")
        raise

    try:
        await redis_client.connect()
        logger.debug("Redis соединение установлено")
    except Exception:  
        logger.exception("Не удалось подключиться к Redis")
        await db.close()
        raise

    try:
        await rabbitmq_manager.connect()
        logger.debug("RabbitMQ менеджер инициализирован")
    except Exception:  
        logger.exception("Не удалось инициализировать RabbitMQ менеджер")
        await redis_client.close()
        await db.close()
        raise

    service_factory = PermissionServiceFactory(
        db=db,
        redis_client=redis_client,
    )

    result_consumer = ResultConsumer(
        service_factory=service_factory,
        rabbitmq_manager=rabbitmq_manager,
        db=db
    )

    consumer_task: asyncio.Task | None = None
    try:
        consumer_task = asyncio.create_task(result_consumer.start_consuming())
        logger.debug("Consumer для result_queue запущен как фоновая задача")
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
                logger.debug("Consumer для result_queue остановлен")
            except Exception:
                logger.exception("Ошибка при остановке consumer")

        try:
            await rabbitmq_manager.close()
            logger.debug("RabbitMQ соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии RabbitMQ соединения")

        try:
            await redis_client.close()
            logger.debug("Redis соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии Redis соединения")

        try:
            await db.close()
            logger.debug("База данных соединение закрыто")
        except Exception:  
            logger.exception("Ошибка при закрытии базы данных соединения")


app = FastAPI(
    title="User Service",
    description="Сервис управления пользователями, заявками и правами",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Ошибка валидации: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Непредвиденная ошибка")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(permissions.router, prefix="", tags=["Permissions"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
