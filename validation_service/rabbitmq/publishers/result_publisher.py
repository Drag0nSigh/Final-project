import logging
import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel

from validation_service.models.validation_models import ValidationResult

logger = logging.getLogger(__name__)


class ResultPublisher:

    def __init__(
        self,
        rabbitmq_url: str,
        result_queue_name: str
    ):

        self._rabbitmq_url = rabbitmq_url
        self._result_queue_name = result_queue_name
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None

    async def connect(self):
        try:
            self._connection = await aio_pika.connect_robust(self._rabbitmq_url)
            self._channel = await self._connection.channel()

            self._queue = await self._channel.declare_queue(
                self._result_queue_name,
                durable=True
            )

            logger.info(
                f"Publisher подключен к RabbitMQ, очередь: {self._result_queue_name}"
            )
        except Exception as e:
            logger.error(f"Ошибка подключения Publisher к RabbitMQ: {e}")
            raise

    async def close(self):
        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            logger.info("Publisher отключен от RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при закрытии Publisher: {e}")

    async def publish_result(self, result: ValidationResult):
        if not self._channel or self._channel.is_closed:
            logger.error("Канал RabbitMQ не открыт, невозможно отправить результат")
            raise RuntimeError("Publisher не подключен к RabbitMQ")

        try:
            message_body = result.model_dump_json().encode('utf-8')

            await self._channel.default_exchange.publish(
                aio_pika.Message(
                    message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self._result_queue_name
            )

            logger.info(
                f"Результат валидации отправлен в очередь {self._result_queue_name}: "
                f"request_id={result.request_id}, approved={result.approved}"
            )
        except Exception as msg:
            logger.error(
                f"Ошибка при отправке результата валидации в очередь: {msg}, "
                f"request_id={result.request_id}"
            )
            raise
