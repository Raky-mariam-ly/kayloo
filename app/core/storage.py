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
    Configure le backend de stockage de fichiers via apache-libcloud.

    En développement : stockage local dans static/uploads/.
    En production, remplacer le driver local par S3 ou MinIO :

        from libcloud.storage.types import Provider
        cls = get_driver(Provider.S3)
        driver = cls("access_key", "secret_key", region="eu-west-1")
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
            # region non passé : DigitalOcean Spaces utilise l'host, pas une région AWS
        )
        StorageManager.add_storage(
            "images", _get_or_create_container(driver, settings.s3_bucket)
        )
        logger.info("Storage: S3 backend actif — bucket=%s endpoint=%s", settings.s3_bucket, host)
        return

    os.makedirs(UPLOAD_DIR, mode=0o755, exist_ok=True)
    cls = get_driver("local")
    driver = cls(UPLOAD_DIR)
    StorageManager.add_storage("images", _get_or_create_container(driver, "images"))
    logger.warning("Storage: backend LOCAL actif (%s) — variables S3 manquantes", UPLOAD_DIR)
