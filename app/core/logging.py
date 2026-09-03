import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:

    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO"
    ).upper()

    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        "logs/tripmate.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(log_level)

    # Prevent duplicate handlers when reload happens
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)