from __future__ import annotations

import json
import logging
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractQueue

from user_service.db.database import db
from user_service.services.redis_client import redis_client
from user_service.services.permissions_service import PermissionService
from user_service.services.rabbitmq_manager import rabbitmq_manager

logger = logging.getLogger(__name__)


class ResultConsumer:
    """Consumer для обработки результатов валидации из result_queue."""

    def __init__(self) -> None:
        """Инициализация consumer."""

        self._consuming = False

    async def start_consuming(self) -> None:
        """Начинает потребление сообщений из result_queue."""

        if not rabbitmq_manager.is_connected:
            logger.error("RabbitMQ не подключён, невозможно начать потребление")
            raise RuntimeError("RabbitMQ не подключён. Вызовите connect() сначала.")

        result_queue = rabbitmq_manager.result_queue
        if not result_queue:
            logger.error("Очередь result_queue не объявлена")
            raise RuntimeError("Очередь result_queue не объявлена")

        self._consuming = True
        logger.info("Начато потребление сообщений из очереди result_queue")

        try:
            async with result_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self._consuming:
                        logger.info("Получен сигнал остановки потребления")
                        break

                    await self._handle_message(message)
        except Exception as exc:
            logger.exception("Критическая ошибка в цикле потребления сообщений")
            raise
        finally:
            logger.info("Потребление сообщений из result_queue остановлено")

    async def stop_consuming(self) -> None:
        """Останавливает потребление сообщений из очереди."""

        self._consuming = False
        logger.info("Запрошена остановка потребления сообщений")

    async def _handle_message(self, message: aio_pika.IncomingMessage) -> None:
        """Обрабатывает одно сообщение из result_queue.

        ***ВАЖНО для Validation Service***: Ожидает сообщение в формате ValidationResult от Validation Service.
        Формат JSON-сообщения: ``{"request_id": str, "approved": bool, "user_id": int, "permission_type": "access"|"group",
        "item_id": int, "reason": Optional[str]}``. Очередь: ``result_queue``. Validation Service должен отправлять
        результаты валидации именно в этом формате.

        Логика обработки:
        1. Парсит JSON-сообщение в формат ValidationResult.
        2. Создаёт сессию БД и экземпляр PermissionService.
        3. Вызывает apply_validation_result для обновления статуса заявки.
        4. Подтверждает обработку (ack) или отклоняет (nack) сообщение.

        Parameters
        ----------
        message:
            Входящее сообщение из RabbitMQ.
        """

        async with message.process():
            try:
                # Парсим сообщение
                try:
                    body = message.body.decode("utf-8")
                    result_data = json.loads(body)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    logger.error(
                        "Ошибка парсинга сообщения из result_queue: %s, "
                        "body: %s",
                        exc,
                        message.body.decode("utf-8", errors="ignore"),
                    )
                    await message.nack(requeue=False)
                    return

                # Извлекаем поля из результата валидации
                # ***ВАЖНО для Validation Service***: Validation Service должен отправлять все эти поля:
                # request_id (str), approved (bool), user_id (int), permission_type (str), item_id (int)
                request_id = result_data.get("request_id")
                approved = result_data.get("approved")
                user_id = result_data.get("user_id")
                permission_type = result_data.get("permission_type")
                item_id = result_data.get("item_id")

                # Валидация обязательных полей
                if not all([request_id, approved is not None, user_id, permission_type, item_id]):
                    logger.error(
                        "Неполные данные в сообщении result_queue: request_id=%s, "
                        "approved=%s, user_id=%s, permission_type=%s, item_id=%s",
                        request_id,
                        approved,
                        user_id,
                        permission_type,
                        item_id,
                    )
                    await message.nack(requeue=False)
                    return

                logger.info(
                    "Получен результат валидации: request_id=%s, approved=%s, "
                    "user_id=%s, permission_type=%s, item_id=%s",
                    request_id,
                    approved,
                    user_id,
                    permission_type,
                    item_id,
                )

                if db.AsyncSessionLocal is None:
                    logger.error("БД не инициализирована, невозможно обработать сообщение")
                    await message.nack(requeue=True)
                    return

                async with db.AsyncSessionLocal() as session:
                    try:
                        redis_conn = await redis_client.get_connection()
                        service = PermissionService(session=session, redis_conn=redis_conn)

                        permission = await service.apply_validation_result(
                            request_id=request_id,
                            approved=approved,
                            user_id=user_id,
                            permission_type=permission_type,
                            item_id=item_id,
                        )

                        if permission is None:
                            logger.warning(
                                "Заявка не найдена в БД: request_id=%s, user_id=%s, "
                                "permission_type=%s, item_id=%s. Возможно, заявка была удалена "
                                "или request_id некорректен.",
                                request_id,
                                user_id,
                                permission_type,
                                item_id,
                            )
                        else:
                            await session.commit()
                            # Детальное логирование результата обновления
                            if approved:
                                logger.info(
                                    "Заявка одобрена и активирована: request_id=%s, user_id=%s, "
                                    "permission_type=%s, item_id=%s, новый статус=%s",
                                    request_id,
                                    user_id,
                                    permission_type,
                                    item_id,
                                    permission.status,
                                )
                            else:
                                logger.info(
                                    "Заявка отклонена: request_id=%s, user_id=%s, "
                                    "permission_type=%s, item_id=%s, новый статус=%s%s",
                                    request_id,
                                    user_id,
                                    permission_type,
                                    item_id,
                                    permission.status,
                                    f", причина: {reason}" if reason else "",
                                )
                    except Exception as exc:
                        await session.rollback()
                        logger.exception(
                            "Ошибка при применении результата валидации: request_id=%s",
                            request_id,
                        )
                        raise

            except Exception as exc:
                logger.exception(
                    "Ошибка обработки сообщения из result_queue: request_id=%s",
                    result_data.get("request_id") if "result_data" in locals() else "unknown",
                )
                await message.nack(requeue=False)


# Глобальный экземпляр consumer
result_consumer = ResultConsumer()

