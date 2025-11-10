import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bff_service.app.routes import permissions, health, resources, accesses, groups, conflicts
from bff_service.app.dependencies import close_all_clients
from bff_service.config.settings import get_settings

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

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    logger.debug("BFF Service запускается...")
    yield
    logger.debug("BFF Service завершает работу, закрытие HTTP клиентов...")
    await close_all_clients()
    logger.debug("BFF Service остановлен")


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

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(permissions.router, prefix="", tags=["Permissions"])
app.include_router(resources.router, prefix="", tags=["Resources"])
app.include_router(accesses.router, prefix="", tags=["Accesses"])
app.include_router(groups.router, prefix="", tags=["Groups"])
app.include_router(conflicts.router, prefix="", tags=["Conflicts"])


