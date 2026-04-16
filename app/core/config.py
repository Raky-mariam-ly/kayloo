import logging
from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/db"
    secret: str = "ff9e2b240fb9be53ac77358a4b667d68b1c8e9a0c9f2e5b4c8e7a1d2f3"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    logging.info("Loading config settings from the environment...")
    return Settings()


# 1. Configure basic logging
logging.basicConfig()

# 2. Get the specific SQLAlchemy engine logger and set its level
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)
