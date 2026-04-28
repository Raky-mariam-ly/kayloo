import logging
from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/db"
    secret: str = Field(
        default="ff9e2b240fb9be53ac77358a4b667d68b1c8e9a0c9f2e5b4c8e7a1d2f3",
        validation_alias="SECRET_KEY",
    )

    # ── URL publique de l'app (utilisée dans les emails) ──
    app_url: str = "http://localhost:8000"

    # ── CORS — en prod, mettre les domaines séparés par des virgules ──
    # Exemple : "https://kayloo.immo,https://app.kayloo.immo"
    cors_origins: str = "*"

    # ── SMTP (configurer via .env en prod) ──
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@kayloo.immo"

    # ── Google Maps ──
    google_maps_api_key: str = ""

    # ── S3 / DigitalOcean Spaces ──
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint: str = ""
    s3_bucket: str = ""
    s3_region: str = "fra1"
    s3_secure: bool = True

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
