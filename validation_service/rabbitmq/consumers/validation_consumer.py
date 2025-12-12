import json
import logging
import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel

from validation_service.models.validation_models import ValidationRequest
from validation_service.services.protocols import ValidationServiceProtocol
from validation_service.rabbitmq.protocols import ResultPublisherProtocol

logger = logging.getLogger(__name__)


class ValidationConsumer:
    
    def __init__(
        self,
        validation_service: ValidationServiceProtocol,
        publisher: ResultPublisherProtocol,
        rabbitmq_url: str,
        validation_queue_name: str
    ):

        self._validation_service = validation_service
        self._publisher = publisher
        self._rabbitmq_url = rabbitmq_url
        self._validation_queue_name = validation_queue_name
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None
        self._consuming = False

    async def connect(self):

        if self._connection and not self._connection.is_closed:
            logger.warning("Consumer уже подключен к RabbitMQ")
            return

        try:
            self._connection = await aio_pika.connect_robust(self._rabbitmq_url)
            self._channel = await self._connection.channel()

            await self._channel.set_qos(prefetch_count=1)

            self._queue = await self._channel.declare_queue(
                self._validation_queue_name,
                durable=True
            )

            logger.info(
                f"ValidationConsumer подключен к RabbitMQ, очередь: {self._validation_queue_name}"
            )
        except Exception as e:
            logger.error(f"Ошибка подключения ValidationConsumer к RabbitMQ: {e}")
            raise

    async def close(self):
        self._consuming = False
        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            logger.info("ValidationConsumer отключен от RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при закрытии ValidationConsumer: {e}")

    async def start_consuming(self):
        if not self._queue:
            raise RuntimeError("Consumer не подключен к RabbitMQ. Вызовите connect() сначала.")

        self._consuming = True
        logger.info(f"Начато потребление сообщений из очереди {self._validation_queue_name}")

        async with self._queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._consuming:
                    break
                await self._handle_message(message)

    async def _handle_message(self, message: aio_pika.IncomingMessage):

        async with message.process():
            try:
                try:
                    body = message.body.decode('utf-8')
                    request_data = json.loads(body)
                    request = ValidationRequest(**request_data)
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.error(
                        f"Ошибка парсинга сообщения: {e}, "
                        f"body: {message.body.decode('utf-8', errors='ignore')}"
                    )
                    await message.nack(requeue=False)
                    return

                logger.info(
                    f"Получен запрос на валидацию: request_id={request.request_id}, "
                    f"user_id={request.user_id}, {request.permission_type}={request.item_id}"
                )

                result = await self._validation_service.validate(request)

                await self._publisher.publish_result(result)

                logger.debug(
                    f"Запрос {request.request_id} обработан успешно, "
                    f"результат: approved={result.approved}"
                )

            except Exception as e:
                logger.exception(
                    f"Ошибка обработки сообщения: {e}, "
                    f"message_id={message.message_id if hasattr(message, 'message_id') else 'unknown'}"
                )
                await message.nack(requeue=False)
