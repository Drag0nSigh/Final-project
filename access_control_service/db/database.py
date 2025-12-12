import logging
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from access_control_service.config.settings import Settings
from access_control_service.db.base import Base  # noqa: F401
from access_control_service.db.resource import Resource  # noqa: F401
from access_control_service.db.access import Access, AccessResource  # noqa: F401
from access_control_service.db.group import Group, GroupAccess  # noqa: F401
from access_control_service.db.conflict import Conflict  # noqa: F401

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine: AsyncEngine | None = None
        self._AsyncSessionLocal: async_sessionmaker | None = None

    @property
    def DATABASE_URL(self) -> str:
        return self._settings.build_database_url()

    @property
    def SERVER_URL(self) -> str:
        return self._settings.build_server_database_url()

    @property
    def DB_NAME(self) -> str:
        return self._settings.db_name

    @property
    def engine(self) -> AsyncEngine | None:
        return self._engine

    @property
    def AsyncSessionLocal(self) -> async_sessionmaker | None:
        return self._AsyncSessionLocal

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
                    {"dbname": self._settings.db_name}
                )
                exists = result.scalar() is not None

            await temp_engine.dispose()
            return exists
        except Exception as e:
            logger.warning(f"Ошибка проверки существования БД: {e}")
            return False

    async def _create_database(self):
        exists = await self._check_database_exists()

        if exists:
            logger.debug(f"База данных '{self._settings.db_name}' уже существует")
            return

        try:
            temp_engine = create_async_engine(
                self.SERVER_URL,
                echo=False,
                isolation_level="AUTOCOMMIT"
            )

            async with temp_engine.connect() as conn:
                await conn.execute(
                    text(f'CREATE DATABASE "{self._settings.db_name}"')
                )
                logger.debug(f"База данных '{self._settings.db_name}' создана успешно")

            await temp_engine.dispose()
        except Exception as e:
            logger.exception(f"Ошибка создания БД: {e}")
            raise

    async def connect(self):
        if self._engine is not None:
            logger.debug("База данных уже подключена")
            return

        await self._create_database()

        self._engine = create_async_engine(
            self.DATABASE_URL,
            echo=True,
            future=True,
        )

        self._AsyncSessionLocal = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        logger.debug(f"Подключено к базе данных '{self._settings.db_name}'")

    async def run_migrations(self):
        if self._engine is None:
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
        if self._engine is None:
            await self.connect()

        await self.run_migrations()

    async def close(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._AsyncSessionLocal = None
            logger.debug(f"Отключено от базы данных '{self._settings.db_name}'")
