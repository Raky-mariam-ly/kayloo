import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request
from starlette_admin import BaseField, ExportType, ImageField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import EnumField
from starlette_admin.helpers import RequestAction

UPLOAD_DIR = "static/uploads"


class UUIDEnumField(EnumField):
    """EnumField qui convertit les UUID en string avant la comparaison avec les choices."""

    async def serialize_value(self, request: Request, value: any, action: RequestAction) -> any:
        if value is not None:
            value = str(value)
        return await super().serialize_value(request, value, action)


@dataclass
class SectionField(BaseField):
    """Affiche un titre de section dans le formulaire create/edit."""

    form_template: str = "forms/section.html"
    display_template: str = "forms/section.html"
    searchable: bool = False
    orderable: bool = False
    exclude_from_list: bool = True
    exclude_from_detail: bool = True

    async def parse_form_data(
        self, request: Request, form_data: FormData, action: RequestAction
    ) -> Any:
        return None

    async def serialize_value(
        self, request: Request, value: Any, action: RequestAction
    ) -> Any:
        return None


async def _save_upload_file(file: UploadFile) -> str:
    """Sauvegarde un UploadFile sur disque et retourne l'URL."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if not ext:
        ext = ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    content = await file.read()
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(content)
    return f"/static/uploads/{filename}"


@dataclass
class ImageUploadField(ImageField):
    """ImageField qui sauvegarde le fichier(s) uploadé(s) sur disque et stocke l'URL."""

    async def parse_form_data(
        self, request: Request, form_data: FormData, action: RequestAction
    ) -> Any:
        file_value, should_delete = await super().parse_form_data(
            request, form_data, action
        )
        if should_delete:
            return None, True
        if file_value is None:
            return None, False

        # Cas multiple : liste de fichiers
        if isinstance(file_value, list):
            urls = [await _save_upload_file(f) for f in file_value if isinstance(f, UploadFile)]
            return (urls if urls else None), False

        # Cas simple : un seul fichier
        if isinstance(file_value, UploadFile):
            return await _save_upload_file(file_value), False

        return None, False

    async def serialize_value(
        self, request: Request, value: Any, action: RequestAction
    ) -> Any:
        if not isinstance(value, str) or not value:
            return None
        # Le JS de starlette-admin utilise new URL(d.url) → URL absolue requise
        base = str(request.base_url).rstrip("/")
        absolute_url = base + value if value.startswith("/") else value
        img = {
            "url": absolute_url,
            "filename": value.split("/")[-1],
            "content-type": "image/jpeg",
        }
        # multiple=True : le template itère sur data → retourner une liste
        return [img] if self.multiple else img


@dataclass
class PropertyImagesField(ImageUploadField):
    """Champ multi-upload lié à la relation Property.images (liste de PropertyImage)."""

    multiple: bool = True

    async def serialize_value(
        self, request: Request, value: Any, action: RequestAction
    ) -> Any:
        if not value:
            return []
        base = str(request.base_url).rstrip("/")
        result = []
        for item in value:
            raw_url = item.url if hasattr(item, "url") else str(item)
            absolute_url = base + raw_url if raw_url.startswith("/") else raw_url
            result.append({
                "url": absolute_url,
                "filename": raw_url.split("/")[-1],
                "content-type": "image/jpeg",
            })
        return result


AVAILABLE_USER_ROLES = [
    ("superadmin", "Super Admin"),
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("viewer", "Viewer"),
]

GENDER_TYPES = [
    ("M", "Male"),
    ("F", "Female"),
]


class AdminModelView(ModelView):
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    export_types = [ExportType.EXCEL, ExportType.CSV]
