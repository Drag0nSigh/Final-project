from __future__ import annotations

import json
import logging

import aio_pika
from aio_pika.abc import AbstractQueue

from user_service.db.protocols import (
    RabbitMQManagerProtocol,
    PermissionServiceFactoryProtocol,
    DatabaseProtocol,
)
from user_service.models.enums import PermissionType

logger = logging.getLogger(__name__)


class ResultConsumer:

    def __init__(
        self,
        service_factory: PermissionServiceFactoryProtocol,
        rabbitmq_manager: RabbitMQManagerProtocol,
        db: DatabaseProtocol,
    ) -> None:
        self._service_factory = service_factory
        self._rabbitmq_manager = rabbitmq_manager
        self._db = db
        self._consuming = False

    async def start_consuming(self) -> None:

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

                    try:
                        await self._handle_message(message)
                    except Exception:
                        logger.exception("Ошибка при обработке сообщения, продолжаем обработку следующих сообщений")
        except Exception as exc:
            logger.exception("Критическая ошибка в цикле потребления сообщений")
            raise
        finally:
            logger.debug("Потребление сообщений из result_queue остановлено")

    async def stop_consuming(self) -> None:

        self._consuming = False
        logger.debug("Запрошена остановка потребления сообщений")

    async def _handle_message(self, message: aio_pika.IncomingMessage) -> None:

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

                async with self._service_factory.create_with_session() as service:
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

            except RuntimeError as exc:
                if "БД не инициализирована" in str(exc):
                    logger.error("БД не инициализирована, невозможно обработать сообщение")
                    await message.nack(requeue=True)
                    return
                raise
            except Exception as exc:
                request_id_value = result_data.get("request_id") if "result_data" in locals() else "unknown"
                logger.exception(
                    f"Ошибка обработки сообщения из result_queue: request_id={request_id_value}"
                )
                await message.nack(requeue=False)
                raise

