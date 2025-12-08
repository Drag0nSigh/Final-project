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

        self.rabbitmq_url = rabbitmq_url
        self.result_queue_name = result_queue_name
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None
    
    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            self.queue = await self.channel.declare_queue(
                self.result_queue_name,
                durable=True
            )
            
            logger.info(
                f"Publisher подключен к RabbitMQ, очередь: {self.result_queue_name}"
            )
        except Exception as e:
            logger.error(f"Ошибка подключения Publisher к RabbitMQ: {e}")
            raise
    
    async def close(self):
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
            logger.info("Publisher отключен от RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при закрытии Publisher: {e}")
    
    async def publish_result(self, result: ValidationResult):
        if not self.channel or self.channel.is_closed:
            logger.error("Канал RabbitMQ не открыт, невозможно отправить результат")
            raise RuntimeError("Publisher не подключен к RabbitMQ")
        
        try:
            message_body = result.model_dump_json().encode('utf-8')
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self.result_queue_name
            )
            
            logger.info(
                f"Результат валидации отправлен в очередь {self.result_queue_name}: "
                f"request_id={result.request_id}, approved={result.approved}"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при отправке результата валидации в очередь: {e}, "
                f"request_id={result.request_id}"
            )
            raise

