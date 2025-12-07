from __future__ import annotations

from typing import Any
import json
import logging

import redis.asyncio as redis

from access_control_service.config.settings import get_settings

logger = logging.getLogger(__name__)


CONFLICTS_MATRIX_KEY = "conflicts:matrix"


async def get_conflicts_matrix_from_cache(
    redis_conn: redis.Redis[Any],
) -> list[dict[str, int]] | None:

    cached_value = await redis_conn.get(CONFLICTS_MATRIX_KEY)
    if cached_value is None:
        logger.debug("Матрица конфликтов не найдена в кэше")
        return None

    try:
        conflicts = json.loads(cached_value)
        logger.debug(f"Матрица конфликтов загружена из кэша: {len(conflicts)} пар")
        return conflicts
    except json.JSONDecodeError as e:
        await redis_conn.delete(CONFLICTS_MATRIX_KEY)
        return None


async def set_conflicts_matrix_cache(
    redis_conn: redis.Redis[Any],
    conflicts: list[dict[str, int]],
) -> None:

    ttl = get_settings().cache_ttl_conflicts_matrix_seconds
    await redis_conn.setex(
        CONFLICTS_MATRIX_KEY,
        ttl,
        json.dumps(conflicts)
    )
    logger.debug(
        f"Матрица конфликтов сохранена в кэш: {len(conflicts)} пар, TTL={ttl}с"
    )


async def invalidate_conflicts_matrix_cache(
    redis_conn: redis.Redis[Any],
) -> None:

    await redis_conn.delete(CONFLICTS_MATRIX_KEY)
    logger.debug("Кэш матрицы конфликтов инвалидирован")


def _build_group_accesses_key(group_id: int) -> str:

    return f"group:{group_id}:accesses"


async def get_group_accesses_from_cache(
    redis_conn: redis.Redis[Any],
    group_id: int,
) -> list[dict[str, Any]] | None:

    key = _build_group_accesses_key(group_id)
    cached_value = await redis_conn.get(key)
    if cached_value is None:
        logger.debug(f"Доступы группы {group_id} не найдены в кэше")
        return None

    try:
        accesses = json.loads(cached_value)
        logger.debug(f"Доступы группы {group_id} загружены из кэша: {len(accesses)} доступов")
        return accesses
    except json.JSONDecodeError as e:
        await redis_conn.delete(key)
        return None


async def set_group_accesses_cache(
    redis_conn: redis.Redis[Any],
    group_id: int,
    accesses: list[dict[str, Any]],
) -> None:

    key = _build_group_accesses_key(group_id)
    ttl = get_settings().cache_ttl_group_accesses_seconds
    await redis_conn.setex(
        key,
        ttl,
        json.dumps(accesses)
    )
    logger.debug(
        f"Доступы группы {group_id} сохранены в кэш: {len(accesses)} доступов, TTL={ttl}с"
    )


async def invalidate_group_accesses_cache(
    redis_conn: redis.Redis[Any],
    group_id: int,
) -> None:

    key = _build_group_accesses_key(group_id)
    await redis_conn.delete(key)
    logger.debug(f"Кэш доступов группы {group_id} инвалидирован")


def _build_access_groups_key(access_id: int) -> str:

    return f"access:{access_id}:groups"


async def get_access_groups_from_cache(
    redis_conn: redis.Redis[Any],
    access_id: int,
) -> list[dict[str, Any]] | None:

    key = _build_access_groups_key(access_id)
    cached_value = await redis_conn.get(key)
    if cached_value is None:
        logger.debug(f"Группы доступа {access_id} не найдены в кэше")
        return None

    try:
        groups = json.loads(cached_value)
        logger.debug(f"Группы доступа {access_id} загружены из кэша: {len(groups)} групп")
        return groups
    except json.JSONDecodeError as e:
        logger.warning(f"Ошибка декодирования кэша групп доступа {access_id}: {e}")
        await redis_conn.delete(key)
        return None


async def set_access_groups_cache(
    redis_conn: redis.Redis[Any],
    access_id: int,
    groups: list[dict[str, Any]],
) -> None:

    key = _build_access_groups_key(access_id)
    ttl = get_settings().cache_ttl_access_groups_seconds
    await redis_conn.setex(
        key,
        ttl,
        json.dumps(groups)
    )
    logger.info(
        f"Группы доступа {access_id} сохранены в кэш: {len(groups)} групп, TTL={ttl}с"
    )


async def invalidate_access_groups_cache(
    redis_conn: redis.Redis[Any],
    access_id: int,
) -> None:

    key = _build_access_groups_key(access_id)
    await redis_conn.delete(key)
    logger.debug(f"Кэш групп доступа {access_id} инвалидирован")

