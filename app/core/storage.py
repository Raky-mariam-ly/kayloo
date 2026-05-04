# core/storage.py

import logging
import os
from libcloud.storage.drivers.s3 import S3StorageDriver
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerDoesNotExistError
from sqlalchemy_file.storage import StorageManager
from core.config import get_settings

logger = logging.getLogger(__name__)
UPLOAD_DIR = "static/uploads"

_DO_REGIONS = {
    "fra1": "fra1.digitaloceanspaces.com",
    "nyc3": "nyc3.digitaloceanspaces.com",
    "ams3": "ams3.digitaloceanspaces.com",
    "sfo2": "sfo2.digitaloceanspaces.com",
    "sfo3": "sfo3.digitaloceanspaces.com",
    "sgp1": "sgp1.digitaloceanspaces.com",
    "blr1": "blr1.digitaloceanspaces.com",
    "syd1": "syd1.digitaloceanspaces.com",
    "tor1": "tor1.digitaloceanspaces.com",
}

class _DOSpacesDriver(S3StorageDriver):
    def __init__(self, key: str, secret: str, region: str = "fra1", **kwargs):
        host = _DO_REGIONS.get(region, f"{region}.digitaloceanspaces.com")
        super().__init__(key, secret, host=host, **kwargs)
        self.region_name = region

def _get_or_create_container(driver, name: str):
    try:
        return driver.get_container(name)
    except ContainerDoesNotExistError:
        return driver.create_container(name)

def configure_storage() -> None:
    settings = get_settings()

    if (
        settings.s3_access_key
        and settings.s3_secret_key
        and settings.s3_bucket
    ):
        driver = _DOSpacesDriver(
            settings.s3_access_key,
            settings.s3_secret_key,
            region=settings.s3_region,
        )
        container = _get_or_create_container(driver, settings.s3_bucket)
        StorageManager.add_storage("images", container)
        
        logger.info("Storage: DO Spaces active — bucket=%s region=%s", settings.s3_bucket, settings.s3_region)
        return

    # Stockage local (fallback)
    os.makedirs(UPLOAD_DIR, mode=0o755, exist_ok=True)
    from libcloud.storage.providers import get_driver
    cls = get_driver("local")
    driver = cls(UPLOAD_DIR)
    StorageManager.add_storage("images", _get_or_create_container(driver, "images"))
    logger.warning("Storage: LOCAL backend active (%s) — S3 variables missing", UPLOAD_DIR)