"""
Настройка логирования для Validation Service
"""

import logging
import sys
from typing import Optional


def setup_logging(service_name: str, log_level: str = "INFO"):
    """
    Настройка логирования
    
    Формат:
    [validation-service] 2024-01-01 12:00:00 - module - INFO - message
    """

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    log_format = (
        f"[{service_name}] "
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)

