from typing import Protocol

from validation_service.models.validation_models import ValidationResult


class ResultPublisherProtocol(Protocol):

    async def connect(self) -> None:
        ...

    async def close(self) -> None:
        ...

    async def publish_result(self, result: ValidationResult) -> None:
        ...
