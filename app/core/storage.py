import logging
import os
from urllib.parse import urlparse

from libcloud.storage.drivers.s3 import S3StorageDriver
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerDoesNotExistError
from sqlalchemy_file.storage import StorageManager
from core.config import get_settings

# sqlalchemy_file's delete_file does path.split("/") which breaks on nested
# paths like "images/agency/property/uuid/file.ext". Also, calling
# container.delete(file_id) is wrong for libcloud — the correct call is
# container.get_object(name).delete(). Both issues fixed here.
@classmethod  # type: ignore[misc]
def _delete_file_fixed(cls, path: str) -> None:
    upload_storage, file_id = path.split("/", 1)
    container = cls.get(upload_storage)
    try:
        obj = container.get_object(file_id)
        obj.delete()
    except Exception:
        pass  # file already gone or inaccessible — safe to ignore

StorageManager.delete_file = _delete_file_fixed

logger = logging.getLogger(__name__)

UPLOAD_DIR = "static/uploads"

# DigitalOcean Spaces regions not present in libcloud's built-in lists.
# Subclassing S3StorageDriver overrides VALID_REGIONS so the parent's
# validation check (self.VALID_REGIONS — polymorphic) accepts DO regions,
# while still using v4 signing with the correct host and region name.
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
    VALID_REGIONS = list(_DO_REGIONS.keys())

    def __init__(self, key: str, secret: str, region: str = "fra1", **kwargs):
        host = _DO_REGIONS.get(region, f"{region}.digitaloceanspaces.com")
        super().__init__(key, secret, host=host, region=region, **kwargs)


def _get_or_create_container(driver, name: str):
    try:
        return driver.get_container(name)
    except ContainerDoesNotExistError:
        return driver.create_container(name)


def configure_storage() -> None:
    """
    Configure the file storage backend via apache-libcloud.

    Development: local storage in static/uploads/.
    Production: DigitalOcean Spaces — set S3_* environment variables.
    """
    settings = get_settings()

    if (
        settings.s3_access_key
        and settings.s3_secret_key
        and settings.s3_endpoint
        and settings.s3_bucket
    ):
        driver = _DOSpacesDriver(
            settings.s3_access_key,
            settings.s3_secret_key,
            region=settings.s3_region,
        )
        StorageManager.add_storage(
            "images", _get_or_create_container(driver, settings.s3_bucket)
        )
        logger.info("Storage: DO Spaces active — bucket=%s region=%s", settings.s3_bucket, settings.s3_region)
        return

    os.makedirs(UPLOAD_DIR, mode=0o755, exist_ok=True)
    cls = get_driver("local")
    driver = cls(UPLOAD_DIR)
    StorageManager.add_storage("images", _get_or_create_container(driver, "images"))
    logger.warning("Storage: LOCAL backend active (%s) — S3 variables missing", UPLOAD_DIR)
