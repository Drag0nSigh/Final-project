import sys
import asyncio
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from user_service.config.settings import get_settings
from user_service.db.base import Base
from user_service.db.user import User
from user_service.db.userpermission import UserPermission

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    settings = get_settings()
    return settings.build_database_url()


def get_metadata():
    return Base.registry.metadata if hasattr(Base, 'registry') else Base.metadata


target_metadata = get_metadata()


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
