import logging
import os
from urllib.parse import urlparse

from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerDoesNotExistError
from sqlalchemy_file.storage import StorageManager
from core.config import get_settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = "static/uploads"


def _get_or_create_container(driver, name: str):
    try:
        return driver.get_container(name)
    except ContainerDoesNotExistError:
        return driver.create_container(name)


def configure_storage() -> None:
    """
    Configure the file storage backend via apache-libcloud.

    Development: local storage in static/uploads/.
    Production: S3 or MinIO — set S3_* environment variables to activate.
    """
    settings = get_settings()

    if (
        settings.s3_access_key
        and settings.s3_secret_key
        and settings.s3_endpoint
        and settings.s3_bucket
    ):
        endpoint = urlparse(settings.s3_endpoint)
        host = endpoint.netloc or endpoint.path
        # Accept both endpoint styles:
        # - fra1.digitaloceanspaces.com
        # - <bucket>.fra1.digitaloceanspaces.com
        bucket_prefix = f"{settings.s3_bucket}."
        if host.startswith(bucket_prefix):
            host = host[len(bucket_prefix) :]
        cls = get_driver("s3")
        driver = cls(
            settings.s3_access_key,
            settings.s3_secret_key,
            host=host,
            secure=settings.s3_secure,
            # DigitalOcean Spaces uses the host, not an AWS-style region
        )
        StorageManager.add_storage(
            "images", _get_or_create_container(driver, settings.s3_bucket)
        )
        logger.info("Storage: S3 backend active — bucket=%s endpoint=%s", settings.s3_bucket, host)
        return

    os.makedirs(UPLOAD_DIR, mode=0o755, exist_ok=True)
    cls = get_driver("local")
    driver = cls(UPLOAD_DIR)
    StorageManager.add_storage("images", _get_or_create_container(driver, "images"))
    logger.warning("Storage: LOCAL backend active (%s) — S3 variables missing", UPLOAD_DIR)
