from __future__ import annotations

import json
import logging

import aio_pika
from aio_pika.abc import AbstractQueue

from user_service.db.protocols import (
    DatabaseProtocol,
    RedisClientProtocol,
    RabbitMQManagerProtocol,
    PermissionServiceProtocol,
)
from user_service.dependencies import create_permission_service
from user_service.models.enums import PermissionType

logger = logging.getLogger(__name__)


class ResultConsumer:
    """Consumer для обработки результатов валидации из result_queue."""

    def __init__(
        self,
        db: DatabaseProtocol,
        redis_client: RedisClientProtocol,
        rabbitmq_manager: RabbitMQManagerProtocol,
    ) -> None:
        self._db = db
        self._redis_client = redis_client
        self._rabbitmq_manager = rabbitmq_manager
        self._consuming = False

    async def start_consuming(self) -> None:
        """Начинает потребление сообщений из result_queue."""

        if not self._rabbitmq_manager.is_connected:
            raise RuntimeError("RabbitMQ не подключён. Вызовите connect() сначала.")

        result_queue = self._rabbitmq_manager.result_queue
        if not result_queue:
            raise RuntimeError("Очередь result_queue не объявлена")

        self._consuming = True
        logger.debug("Начато потребление сообщений из очереди result_queue")

        try:
            async with result_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self._consuming:
                        logger.debug("Получен сигнал остановки потребления")
                        break

                    await self._handle_message(message)
        except Exception as exc:
            logger.exception("Критическая ошибка в цикле потребления сообщений")
            raise
        finally:
            logger.debug("Потребление сообщений из result_queue остановлено")

    async def stop_consuming(self) -> None:
        """Останавливает потребление сообщений из очереди."""

        self._consuming = False
        logger.debug("Запрошена остановка потребления сообщений")

    async def _handle_message(self, message: aio_pika.IncomingMessage) -> None:
        """Обрабатывает одно сообщение из result_queue."""

        async with message.process():
            try:
                try:
                    body = message.body.decode("utf-8")
                    result_data = json.loads(body)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    logger.error(
                        f"Ошибка парсинга сообщения из result_queue: {exc}, "
                        f"body: {message.body.decode('utf-8', errors='ignore')}"
                    )
                    await message.nack(requeue=False)
                    return

                request_id = result_data.get("request_id")
                approved = result_data.get("approved")
                user_id = result_data.get("user_id")
                permission_type_str = result_data.get("permission_type")
                item_id = result_data.get("item_id")

                if not all([request_id, approved is not None, user_id, permission_type_str, item_id]):
                    logger.error(
                        f"Неполные данные в сообщении result_queue: request_id={request_id}, "
                        f"approved={approved}, user_id={user_id}, permission_type={permission_type_str}, item_id={item_id}"
                    )
                    await message.nack(requeue=False)
                    return

                try:
                    permission_type = PermissionType(permission_type_str)
                except ValueError:
                    logger.error(
                        f"Некорректный permission_type в сообщении: {permission_type_str}"
                    )
                    await message.nack(requeue=False)
                    return

                logger.debug(
                    f"Получен результат валидации: request_id={request_id}, approved={approved}, "
                    f"user_id={user_id}, permission_type={permission_type.value}, item_id={item_id}"
                )

                if self._db.AsyncSessionLocal is None:
                    logger.error("БД не инициализирована, невозможно обработать сообщение")
                    await message.nack(requeue=True)
                    return

                async with self._db.AsyncSessionLocal() as session:
                    try:
                        redis_conn = self._redis_client.connection
                        service: PermissionServiceProtocol = create_permission_service(
                            session=session, redis_conn=redis_conn
                        )

                        permission = await service.apply_validation_result(
                            request_id=request_id,
                            approved=approved,
                            user_id=user_id,
                            permission_type=permission_type,
                            item_id=item_id,
                        )

                        if permission is None:
                            logger.warning(
                                f"Заявка не найдена в БД: request_id={request_id}, user_id={user_id}, "
                                f"permission_type={permission_type}, item_id={item_id}. Возможно, заявка была удалена "
                                f"или request_id некорректен."
                            )
                        else:
                            await session.commit()
                            if approved:
                                logger.debug(
                                    f"Заявка одобрена и активирована: request_id={request_id}, user_id={user_id}, "
                                    f"permission_type={permission_type}, item_id={item_id}, новый статус={permission.status}"
                                )
                            else:
                                logger.debug(
                                    f"Заявка отклонена: request_id={request_id}, user_id={user_id}, "
                                    f"permission_type={permission_type}, item_id={item_id}, новый статус={permission.status}"
                                )
                    except Exception as exc:
                        await session.rollback()
                        logger.exception(
                            f"Ошибка при применении результата валидации: request_id={request_id}"
                        )
                        raise

            except Exception as exc:
                request_id_value = result_data.get("request_id") if "result_data" in locals() else "unknown"
                logger.exception(
                    f"Ошибка обработки сообщения из result_queue: request_id={request_id_value}"
                )
                await message.nack(requeue=False)

