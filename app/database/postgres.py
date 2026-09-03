import psycopg

from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import (
    PostgresSaver,
)

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import DatabaseException


logger = get_logger(__name__)


def get_database_url() -> str:

    url = settings.DATABASE_URL

    if not url:
        raise DatabaseException(
            "DATABASE_URL is missing.",
            "DATABASE_URL_MISSING"
        )

    if "sslmode=" not in url:

        separator = (
            "&"
            if "?" in url
            else "?"
        )

        url = (
            f"{url}"
            f"{separator}"
            f"sslmode=require"
        )

    return url


def get_checkpointer():

    try:

        url = get_database_url()

        conn = psycopg.connect(
            url,
            autocommit=True,
            row_factory=dict_row,
        )

        checkpointer = PostgresSaver(
            conn
        )

        checkpointer.setup()

        logger.info(
            "PostgreSQL checkpointing initialized"
        )

        return checkpointer

    except Exception as exc:

        logger.exception(
            "PostgreSQL initialization failed"
        )

        raise DatabaseException(
            "Unable to initialize PostgreSQL.",
            "DATABASE_INIT_ERROR"
        ) from exc