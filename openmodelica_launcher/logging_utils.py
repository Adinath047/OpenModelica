"""Logging helpers for launcher activity."""

from __future__ import annotations

import logging
from pathlib import Path

LOGGER_NAME = "openmodelica_launcher"


def get_logger() -> logging.Logger:
    """Return a configured logger for launcher events."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    log_path = log_file_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_file_path() -> Path:
    """Return the launcher log file path inside the project directory."""
    return Path.cwd() / "logs" / "launcher.log"
