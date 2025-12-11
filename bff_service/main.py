import logging
import sys
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from bff_service.routes import permissions, health, resources, accesses, groups, conflicts
from bff_service.dependencies import close_all_clients, get_settings_dependency

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

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Ошибка валидации: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    logger.warning(
        f"Внешний сервис вернул ошибку: {exc.response.status_code} - {exc.response.text}"
    )
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": exc.response.text or "Ошибка при обработке запроса во внешнем сервисе"},
    )


@app.exception_handler(httpx.RequestError)
async def request_error_handler(request: Request, exc: httpx.RequestError):
    logger.error(f"Ошибка при запросе к внешнему сервису: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Внешний сервис недоступен"},
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
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(accesses.router, prefix="/accesses", tags=["Accesses"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(conflicts.router, prefix="/conflicts", tags=["Conflicts"])
