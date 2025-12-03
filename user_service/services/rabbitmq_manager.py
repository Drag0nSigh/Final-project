from __future__ import annotations

import json
import logging
from typing import Literal

import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue

from user_service.config.settings import get_settings

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """Менеджер подключения к RabbitMQ для User Service."""

    def __init__(self) -> None:
        """Инициализация менеджера с настройками из конфигурации."""

        self._settings = get_settings()
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._validation_queue: AbstractQueue | None = None
        self._result_queue: AbstractQueue | None = None

    @property
    def is_connected(self) -> bool:
        """Показывает, установлено ли соединение с RabbitMQ."""

        return (
            self._connection is not None
            and not self._connection.is_closed
        )

    @property
    def channel(self) -> AbstractChannel | None:
        """Возвращает текущий канал RabbitMQ (если подключение установлено)."""

        return self._channel

    @property
    def validation_queue(self) -> AbstractQueue | None:
        """Возвращает объект очереди `validation_queue` (если объявлена)."""

        return self._validation_queue

    @property
    def result_queue(self) -> AbstractQueue | None:
        """Возвращает объект очереди `result_queue` (если объявлена)."""

        return self._result_queue

    async def connect(self) -> None:
        """Подключение к RabbitMQ и объявление очередей."""

        if self.is_connected:
            logger.warning("RabbitMQ уже подключён, повторное подключение пропущено")
            return

        try:
            rabbitmq_url = self._settings.build_rabbitmq_url()
            logger.debug(f"Подключение к RabbitMQ: {self._settings.rabbitmq_host}:{self._settings.rabbitmq_port}")

            self._connection = await aio_pika.connect_robust(rabbitmq_url)
            self._channel = await self._connection.channel()

            # Объявление очереди validation_queue (для отправки запросов на валидацию)
            validation_queue_name = self._settings.rabbitmq_validation_queue
            self._validation_queue = await self._channel.declare_queue(
                validation_queue_name,
                durable=True,
            )
            logger.debug(f"Очередь объявлена: {validation_queue_name}")

            # Объявление очереди result_queue (для получения результатов валидации)
            result_queue_name = self._settings.rabbitmq_result_queue
            self._result_queue = await self._channel.declare_queue(
                result_queue_name,
                durable=True,
            )
            logger.debug(f"Очередь объявлена: {result_queue_name}")

            logger.debug("RabbitMQ менеджер успешно подключён, все очереди объявлены")

        except Exception as exc:
            logger.exception("Ошибка при подключении к RabbitMQ или объявлении очередей")
            await self._cleanup()
            raise

    async def close(self) -> None:
        """Закрытие соединения с RabbitMQ."""

        await self._cleanup()
        logger.info("RabbitMQ соединение закрыто")

    async def _cleanup(self) -> None:
        """Внутренний метод для очистки ресурсов RabbitMQ."""

        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
        except Exception as exc:
            logger.exception("Ошибка при закрытии канала RabbitMQ")

        try:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
        except Exception as exc:
            logger.exception("Ошибка при закрытии соединения RabbitMQ")

        self._channel = None
        self._connection = None
        self._validation_queue = None
        self._result_queue = None

    async def publish_validation_request(
        self,
        user_id: int,
        permission_type: Literal["access", "group"],
        item_id: int,
        request_id: str,
    ) -> None:
        """Публикует запрос на валидацию в очередь `validation_queue`."""

        if not self.is_connected or not self._channel:
            raise RuntimeError("RabbitMQ не подключён. Вызовите connect() сначала.")

        if not self._validation_queue:
            raise RuntimeError("Очередь validation_queue не объявлена")

        try:

            message_data = {
                "user_id": user_id,
                "permission_type": permission_type,
                "item_id": item_id,
                "request_id": request_id,
            }
            message_body = json.dumps(message_data).encode("utf-8")

            await self._channel.default_exchange.publish(
                aio_pika.Message(
                    message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=self._settings.rabbitmq_validation_queue,
            )

            logger.debug(
                f"Запрос на валидацию опубликован в очередь: request_id={request_id}, user_id={user_id}, "
                f"permission_type={permission_type}, item_id={item_id}"
            )

        except Exception as exc:
            logger.exception(
                f"Ошибка при публикации запроса на валидацию: request_id={request_id}"
            )
            raise


# Глобальный singleton, который будем импортировать в зависимостях.
rabbitmq_manager = RabbitMQManager()
