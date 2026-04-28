import io
import os
import re
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy_file.file import File


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[àáâãäå]", "a", text)
    text = re.sub(r"[èéêë]", "e", text)
    text = re.sub(r"[ìíîï]", "i", text)
    text = re.sub(r"[òóôõö]", "o", text)
    text = re.sub(r"[ùúûü]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "agency"


def _do_spaces_public_url(name: str) -> Optional[str]:
    """Build a permanent public URL for a DigitalOcean Spaces object."""
    try:
        from core.config import get_settings
        s = get_settings()
        if s.s3_bucket and s.s3_region:
            return f"https://{s.s3_bucket}.{s.s3_region}.digitaloceanspaces.com/{name}"
    except Exception:
        pass
    return None


class PropertyImageFile(File):
    """Stores images under {agency_name}/property/{property_id}/{uuid}.ext with public-read ACL."""

    def __init__(self, content=None, filename=None, content_type=None,
                 content_path=None, agency_name=None, property_id=None, **kwargs):
        super().__init__(
            content=content,
            filename=filename,
            content_type=content_type,
            content_path=content_path,
            **kwargs,
        )
        if agency_name:
            self["_agency_slug"] = _slugify(str(agency_name))
        if property_id:
            self["_property_id"] = str(property_id)

    def save_to_storage(self, upload_storage: Optional[str] = None) -> None:
        extra = self.get("extra", {})
        extra.update({"content_type": self.content_type, "acl": "public-read"})
        if extra.get("meta_data") is None:
            extra["meta_data"] = {}
        extra["meta_data"].update({
            "filename": self.filename,
            "content_type": self.content_type,
        })

        agency_slug = self.pop("_agency_slug", None)
        property_id = self.pop("_property_id", None)
        image_id = str(uuid.uuid4())
        _, ext = os.path.splitext(self.filename or "")

        if agency_slug and property_id:
            name = f"{agency_slug}/property/{property_id}/{image_id}{ext}"
        else:
            name = f"{image_id}{ext}"

        stored_file = self.store_content(
            self.original_content,
            upload_storage,
            name=name,
            extra=extra,
            headers=self.get("headers", None),
            content_path=self.content_path,
        )
        self["file_id"] = stored_file.name
        self["upload_storage"] = upload_storage
        self["uploaded_at"] = datetime.utcnow().isoformat()
        self["path"] = f"{upload_storage}/{stored_file.name}"
        self["url"] = _do_spaces_public_url(name) or stored_file.get_cdn_url()
        self["saved"] = True


class AvatarFile(File):
    """Stores avatars under avatars/{user_id}/{uuid}.ext with public-read ACL."""

    def __init__(self, content=None, filename=None, content_type=None,
                 content_path=None, user_id=None, **kwargs):
        super().__init__(
            content=content,
            filename=filename,
            content_type=content_type,
            content_path=content_path,
            **kwargs,
        )
        if user_id:
            self["_user_id"] = str(user_id)

    def save_to_storage(self, upload_storage: Optional[str] = None) -> None:
        extra = self.get("extra", {})
        extra.update({"content_type": self.content_type, "acl": "public-read"})
        if extra.get("meta_data") is None:
            extra["meta_data"] = {}
        extra["meta_data"].update({
            "filename": self.filename,
            "content_type": self.content_type,
        })

        user_id = self.pop("_user_id", None)
        image_id = str(uuid.uuid4())
        _, ext = os.path.splitext(self.filename or "")

        name = f"avatars/{user_id}/{image_id}{ext}" if user_id else f"avatars/{image_id}{ext}"

        stored_file = self.store_content(
            self.original_content,
            upload_storage,
            name=name,
            extra=extra,
            headers=self.get("headers", None),
            content_path=self.content_path,
        )
        self["file_id"] = stored_file.name
        self["upload_storage"] = upload_storage
        self["uploaded_at"] = datetime.utcnow().isoformat()
        self["path"] = f"{upload_storage}/{stored_file.name}"
        self["url"] = _do_spaces_public_url(name) or stored_file.get_cdn_url()
        self["saved"] = True
