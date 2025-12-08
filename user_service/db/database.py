from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy import text
import os
from typing import AsyncGenerator

from user_service.db.base import Base
from user_service.db.user import User  # noqa: F401
from user_service.db.userpermission import UserPermission  # noqa: F401


class Database:
    
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST", "postgres")
        self.DB_PORT = "5432"
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
            print(f"Ошибка проверки существования БД: {e}")
            return False
    
    async def _create_database(self):
        exists = await self._check_database_exists()
        
        if exists:
            print(f"База данных '{self.DB_NAME}' уже существует")
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
                print(f"Database '{self.DB_NAME}' created successfully")
            
            await temp_engine.dispose()
        except Exception as e:
            print(f"Ошибка создания БД: {e}")
            raise
    
    async def connect(self):
        if self.engine is not None:
            print("База данных уже подключена")
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
        
        print(f"Подключено к базе данных '{self.DB_NAME}'")
    
    async def init_db(self):
        if self.engine is None:
            await self.connect()
        
        async with self.engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT EXISTS ("
                    "SELECT FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'users'"
                    ")"
                )
            )
            tables_exist = result.scalar()
            
            if tables_exist:
                print("База данных уже содержит таблицы")
                return
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Таблицы базы данных созданы успешно")
    
    async def close(self):
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.AsyncSessionLocal = None
            print(f"Отключено от базы данных '{self.DB_NAME}'")


db = Database()
