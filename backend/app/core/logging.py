"""Structured JSON logging configuration for FieldMind AI."""

import logging
import sys
from typing import Any, Dict


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured formatters for stdout."""
    logger = logging.getLogger("fieldmind")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
