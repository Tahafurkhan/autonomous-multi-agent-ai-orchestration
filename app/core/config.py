import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "TripMate AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-120b"
    )

    LLM_MAX_TOKENS: int = int(
        os.getenv("LLM_MAX_TOKENS", "1000")
    )

    LLM_REASONING_EFFORT: str = os.getenv(
        "LLM_REASONING_EFFORT",
        "low"
    )

    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


settings = Settings()


def validate_settings() -> None:

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing."
        )

    if not settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is missing."
        )