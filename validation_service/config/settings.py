"""
Настройки Validation Service через переменные окружения

Использует Pydantic Settings для загрузки конфигурации из .env файла
и переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Validation Service"""
    
    # Service URLs
    USER_SERVICE_URL: str = "http://user_service:8000"
    ACCESS_CONTROL_SERVICE_URL: str = "http://access_control_service:8000"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    VALIDATION_QUEUE: str = "validation_queue"
    RESULT_QUEUE: str = "result_queue"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Timeouts
    HTTP_TIMEOUT: float = 30.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Конфигурация Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def rabbitmq_url(self) -> str:
        """URL для подключения к RabbitMQ"""
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
        )

