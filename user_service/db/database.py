import os
import logging
import asyncio
from typing import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from user_service.db.base import Base
from user_service.db.user import User  # noqa: F401
from user_service.db.userpermission import UserPermission  # noqa: F401


logger = logging.getLogger(__name__)


class Database:
    
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST", "postgres")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        self.DB_NAME = os.getenv("DB_NAME", "user_service")
        
        self.DATABASE_URL = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        
        self.SERVER_URL = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/postgres"
        )
        
        self.engine: AsyncEngine | None = None
        self.AsyncSessionLocal: async_sessionmaker | None = None
    
    async def _check_database_exists(self) -> bool:
        try:
            temp_engine = create_async_engine(
                self.SERVER_URL,
                echo=False,
                isolation_level="AUTOCOMMIT"
            )
            
            async with temp_engine.connect() as conn:
                result = await conn.execute(
                    text(
                        "SELECT 1 FROM pg_database WHERE datname = :dbname"
                    ),
                    {"dbname": self.DB_NAME}
                )
                exists = result.scalar() is not None
            
            await temp_engine.dispose()
            return exists
        except Exception as e:
            logger.debug(f"Ошибка проверки существования БД: {e}")
            return False
    
    async def _create_database(self):
        exists = await self._check_database_exists()
        
        if exists:
            logger.debug(f"База данных '{self.DB_NAME}' уже существует")
            return
        
        try:
            temp_engine = create_async_engine(
                self.SERVER_URL,
                echo=False,
                isolation_level="AUTOCOMMIT"
            )
            
            async with temp_engine.connect() as conn:
                await conn.execute(
                    text(f'CREATE DATABASE "{self.DB_NAME}"')
                )
                logger.debug(f"Database '{self.DB_NAME}' created successfully")
            
            await temp_engine.dispose()
        except Exception as e:
            logger.debug(f"Ошибка создания БД: {e}")
            raise
    
    async def connect(self):
        if self.engine is not None:
            logger.debug("База данных уже подключена")
            return
        
        await self._create_database()
        
        self.engine = create_async_engine(
            self.DATABASE_URL,
            echo=True,
            future=True,
        )
        
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        logger.debug(f"Подключено к базе данных '{self.DB_NAME}'")
    
    async def run_migrations(self):
        if self.engine is None:
            await self.connect()
        
        alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"
        if not alembic_ini_path.exists():
            raise FileNotFoundError(f"Alembic config file not found: {alembic_ini_path}")
        
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option(
            "script_location",
            str(alembic_ini_path.parent / "alembic"),
        )
        alembic_cfg.set_main_option("sqlalchemy.url", self.DATABASE_URL)

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
            logger.debug("Миграции Alembic применены успешно")
        except Exception as e:
            logger.debug(f"Ошибка при применении миграций Alembic: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def init_db(self):
        if self.engine is None:
            await self.connect()
        
        await self.run_migrations()
    
    async def close(self):
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.AsyncSessionLocal = None
            logger.debug(f"Отключено от базы данных '{self.DB_NAME}'")


db = Database()
