from __future__ import annotations

from typing import Any
import json

import redis.asyncio as redis

from user_service.config.settings import get_settings


USER_GROUPS_KEY_PREFIX = "user:{user_id}:active_groups"


def _build_user_groups_key(user_id: int) -> str:

    return USER_GROUPS_KEY_PREFIX.format(user_id=user_id)


async def get_user_groups_from_cache(
    redis_conn: redis.Redis,
    user_id: int,
) -> list[dict[str, Any]] | None:

    key = _build_user_groups_key(user_id)
    cached_value = await redis_conn.get(key)
    if cached_value is None:
        return None

    try:
        return json.loads(cached_value)
    except json.JSONDecodeError:
        await redis_conn.delete(key)
        return None


async def set_user_groups_cache(
    redis_conn: redis.Redis,
    user_id: int,
    groups: list[dict[str, Any]],
) -> None:

    key = _build_user_groups_key(user_id)
    ttl = get_settings().cache_ttl_user_groups_seconds
    await redis_conn.setex(key, ttl, json.dumps(groups))


async def invalidate_user_groups_cache(
    redis_conn: redis.Redis,
    user_id: int,
) -> None:

    key = _build_user_groups_key(user_id)
    await redis_conn.delete(key)
