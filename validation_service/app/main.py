"""
Главное приложение Validation Service

Точка входа и управление жизненным циклом приложения.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import httpx

from validation_service.config.settings import Settings
from validation_service.services.redis_cache import RedisCache
from validation_service.services.user_service_client import UserServiceClient
from validation_service.services.access_control_client import AccessControlClient
from validation_service.app.services.validation_service import ValidationService
from validation_service.app.publishers.result_publisher import ResultPublisher
from validation_service.app.consumers.validation_consumer import ValidationConsumer

# Глобальные переменные для хранения компонентов
cache: RedisCache = None
user_client: UserServiceClient = None
access_control_client: AccessControlClient = None
validation_service: ValidationService = None
publisher: ResultPublisher = None
consumer: ValidationConsumer = None
consumer_task: asyncio.Task = None

settings = Settings()
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("redis").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""

    global cache, user_client, access_control_client
    global validation_service, publisher, consumer, consumer_task, settings
    
    logger.debug("Запуск Validation Service...")
    
    try:
        logger.debug(f"Настройки загружены, уровень логирования: {settings.LOG_LEVEL}")
        
        try:
            logger.debug("Инициализация Redis кэша...")
            cache = RedisCache(
                redis_host=settings.REDIS_HOST,
                redis_port=settings.REDIS_PORT
            )
            await cache.connect()
            logger.debug("Redis кэш подключен")
        except Exception as e:
            logger.exception(f"Ошибка инициализации Redis кэша: {e}")
            raise
        
        try:
            logger.debug("Инициализация HTTP клиентов...")
            user_client = UserServiceClient(
                base_url=settings.USER_SERVICE_URL,
                cache=cache,
                timeout=settings.HTTP_TIMEOUT
            )
            access_control_client = AccessControlClient(
                base_url=settings.ACCESS_CONTROL_SERVICE_URL,
                cache=cache,
                timeout=settings.HTTP_TIMEOUT
            )
            logger.debug("HTTP клиенты инициализированы")
        except Exception as e:
            logger.exception(f"Ошибка инициализации HTTP клиентов: {e}")
            raise
        
        try:
            logger.debug("Инициализация ValidationService...")
            validation_service = ValidationService(
                user_client=user_client,
                access_control_client=access_control_client
            )
            logger.debug("ValidationService инициализирован")
        except Exception as e:
            logger.exception(f"Ошибка инициализации ValidationService: {e}")
            raise
        
        try:
            logger.debug("Инициализация ResultPublisher...")
            publisher = ResultPublisher(
                rabbitmq_url=settings.rabbitmq_url,
                result_queue_name=settings.RESULT_QUEUE
            )
            await publisher.connect()
            logger.debug("ResultPublisher подключен")
        except Exception as e:
            logger.exception(f"Ошибка инициализации ResultPublisher: {e}")
            raise
        
        try:
            logger.debug("Инициализация ValidationConsumer...")
            consumer = ValidationConsumer(
                validation_service=validation_service,
                publisher=publisher,
                rabbitmq_url=settings.rabbitmq_url,
                validation_queue_name=settings.VALIDATION_QUEUE
            )
            await consumer.connect()
            logger.debug("ValidationConsumer подключен")
        except Exception as e:
            logger.exception(f"Ошибка инициализации ValidationConsumer: {e}")
            raise
        
        try:
            logger.debug("Запуск ValidationConsumer в фоновом режиме...")
            consumer_task = asyncio.create_task(consumer.start_consuming())
            logger.debug("Validation Service запущен и готов к работе")
        except Exception as e:
            logger.exception(f"Ошибка запуска ValidationConsumer: {e}")
            raise
        
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске Validation Service: {e}")
        raise
    
    yield
    
    logger.debug("Остановка Validation Service...")
    
    if consumer_task and not consumer_task.done():
        try:
            logger.debug("Остановка ValidationConsumer...")
            consumer._consuming = False
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
            if consumer:
                await consumer.close()
            logger.debug("ValidationConsumer остановлен")
        except Exception as e:
            logger.exception(f"Ошибка при остановке ValidationConsumer: {e}")
    
    if publisher:
        try:
            logger.debug("Закрытие ResultPublisher...")
            await publisher.close()
            logger.debug("ResultPublisher закрыт")
        except Exception as e:
            logger.exception(f"Ошибка при закрытии ResultPublisher: {e}")
    
    if user_client:
        try:
            logger.debug("Закрытие UserServiceClient...")
            await user_client.close()
        except Exception as e:
            logger.exception(f"Ошибка при закрытии UserServiceClient: {e}")
    
    if access_control_client:
        try:
            logger.debug("Закрытие AccessControlClient...")
            await access_control_client.close()
        except Exception as e:
            logger.exception(f"Ошибка при закрытии AccessControlClient: {e}")
    
    logger.debug("HTTP клиенты закрыты")
    
    if cache:
        try:
            logger.debug("Закрытие Redis кэша...")
            await cache.close()
            logger.debug("Redis кэш закрыт")
        except Exception as e:
            logger.exception(f"Ошибка при закрытии Redis кэша: {e}")
    
    logger.debug("Validation Service остановлен")


app = FastAPI(
    title="Validation Service",
    description="Асинхронная проверка конфликтов прав",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "validation-service"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check"""

    checks = {
        "redis": False,
        "rabbitmq": False,
        "user_service": False,
        "access_control_service": False
    }
    
    try:
        if cache and cache.client:
            await cache.client.ping()
            checks["redis"] = True
    except Exception as e:
        logger.warning(f"Redis недоступен: {e}")
    
    try:
        if consumer and consumer.connection and not consumer.connection.is_closed:
            checks["rabbitmq"] = True
        elif publisher and publisher.connection and not publisher.connection.is_closed:
            checks["rabbitmq"] = True
    except Exception as e:
        logger.warning(f"RabbitMQ недоступен: {e}")
    
    try:
        if user_client:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{user_client.base_url}/health")
                if response.status_code == 200:
                    checks["user_service"] = True
    except Exception as e:
        logger.warning(f"User Service недоступен: {e}")
    
    try:
        if access_control_client:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{access_control_client.base_url}/health")
                if response.status_code == 200:
                    checks["access_control_service"] = True
    except Exception as e:
        logger.warning(f"Access Control Service недоступен: {e}")
    
    if all(checks.values()):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "service": "validation-service",
                "checks": checks
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "service": "validation-service",
                "checks": checks
            }
        )

