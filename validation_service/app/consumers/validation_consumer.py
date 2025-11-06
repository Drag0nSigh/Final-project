"""
Consumer для обработки запросов на валидацию из RabbitMQ

Получает сообщения из validation_queue, обрабатывает их через ValidationService
и отправляет результаты через ResultPublisher.
"""

import json
import logging
from typing import Optional
import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel

from validation_service.models.validation_models import (
    ValidationRequest,
    ValidationResult
)
from validation_service.app.services.validation_service import ValidationService
from validation_service.app.publishers.result_publisher import ResultPublisher

logger = logging.getLogger(__name__)


class ValidationConsumer:
    """Consumer для обработки запросов на валидацию"""
    
    def __init__(
        self,
        validation_service: ValidationService,
        publisher: ResultPublisher,
        rabbitmq_url: str,
        validation_queue_name: str
    ):
        """Инициализация consumer"""

        self.validation_service = validation_service
        self.publisher = publisher
        self.rabbitmq_url = rabbitmq_url
        self.validation_queue_name = validation_queue_name
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.queue: Optional[aio_pika.abc.AbstractQueue] = None
        self._consuming = False
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        
        if self.connection and not self.connection.is_closed:
            logger.warning("Consumer уже подключен к RabbitMQ")
            return
        
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            await self.channel.set_qos(prefetch_count=1)
            
            self.queue = await self.channel.declare_queue(
                self.validation_queue_name,
                durable=True
            )
            
            logger.info(
                f"ValidationConsumer подключен к RabbitMQ, очередь: {self.validation_queue_name}"
            )
        except Exception as e:
            logger.error(f"Ошибка подключения ValidationConsumer к RabbitMQ: {e}")
            raise
    
    async def close(self):
        """Закрытие подключения"""
        self._consuming = False
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
            logger.info("ValidationConsumer отключен от RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при закрытии ValidationConsumer: {e}")
    
    async def start_consuming(self):
        """
        Начать потребление сообщений из validation_queue
        
        Логика:
        1. Объявить очередь validation_queue (уже сделано в connect)
        2. Начать потребление сообщений
        3. Для каждого сообщения вызывается _handle_message
        """
        if not self.queue:
            raise RuntimeError("Consumer не подключен к RabbitMQ. Вызовите connect() сначала.")
        
        self._consuming = True
        logger.info(f"Начато потребление сообщений из очереди {self.validation_queue_name}")
        
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._consuming:
                    break
                await self._handle_message(message)
    
    async def _handle_message(self, message: aio_pika.IncomingMessage):
        """
        Обработка одного сообщения
        
        Логика:
        1. Парсить ValidationRequest из JSON
        2. Вызвать validation_service.validate()
        3. Отправить результат в result_queue через publisher
        4. Подтвердить обработку (ack) или отклонить (nack)
        """

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
                
                result = await self.validation_service.validate(request)
                
                await self.publisher.publish_result(result)
                
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

