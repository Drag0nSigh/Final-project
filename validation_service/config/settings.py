from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    USER_SERVICE_URL: str = "http://user_service:8000"
    ACCESS_CONTROL_SERVICE_URL: str = "http://access_control_service:8000"
    
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    VALIDATION_QUEUE: str = "validation_queue"
    RESULT_QUEUE: str = "result_queue"
    
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    HTTP_TIMEOUT: float = 30.0
    
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
        )

