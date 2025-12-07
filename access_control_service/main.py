from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys

from access_control_service.routes import resources, accesses, groups, conflicts, health, admin
from access_control_service.dependencies import get_database, get_redis_client
from access_control_service.config.settings import get_settings

settings = get_settings()
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logging.getLogger("redis").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    redis_client = get_redis_client()

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
        yield
    finally:
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
    title="Access Control Service",
    description="Сервис управления ресурсами, доступами, группами прав и конфликтами",
    version="1.0.0",
    lifespan=lifespan
)



app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(accesses.router, prefix="/accesses", tags=["Accesses"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(conflicts.router, prefix="/conflicts", tags=["Conflicts"])
app.include_router(admin.router, tags=["Admin"])

