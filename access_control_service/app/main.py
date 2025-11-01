from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from access_control_service.app.routes import resources, accesses, groups, conflicts, health
from access_control_service.db.database import db
import access_control_service.db  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: инициализация БД
    await db.connect()
    await db.init_db()
    yield
    # Shutdown: закрытие подключений
    await db.close()


app = FastAPI(
    title="Access Control Service",
    description="Сервис управления ресурсами, доступами, группами прав и конфликтами",
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
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(accesses.router, prefix="/accesses", tags=["Accesses"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(conflicts.router, prefix="/conflicts", tags=["Conflicts"])

