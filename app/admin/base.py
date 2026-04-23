import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request
from starlette_admin import BaseField, ExportType, ImageField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import EnumField
from starlette_admin.helpers import RequestAction

from core.agency_scope import get_user_agency_id

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
            absolute_url = base + \
                raw_url if raw_url.startswith("/") else raw_url
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
    page_size = 10
    page_size_options = [10, 25, 50, 100]
    export_types = [ExportType.EXCEL, ExportType.CSV]

    service_class: Optional[Type] = None
    repository_class: Optional[Type] = None

    # Agency scoping — set in CRM subclasses
    agency_scoped: bool = False

    def get_service(self, request: Request):
        """Build a service instance from the request's DB session."""
        return self.service_class(self.repository_class(request.state.session))

    @property
    def _has_service(self) -> bool:
        return self.service_class is not None and self.repository_class is not None

    async def _get_agency_id(self, request: Request) -> Optional[UUID]:
        """Resolve agency_id for the current admin user. Cached on request.state."""
        if hasattr(request.state, "_agency_id"):
            return request.state._agency_id
        user = getattr(request.state, "user", None)
        if not user:
            request.state._agency_id = None
            return None
        agency_id = await get_user_agency_id(request.state.session, user)
        request.state._agency_id = agency_id
        return agency_id

    def _apply_agency_filter(self, query, agency_id):
        """Apply agency filter to a SQLAlchemy query. Override in subclasses for custom join logic."""
        if hasattr(self.model, "agency_id"):
            return query.filter(self.model.agency_id == agency_id)
        return query

    async def is_accessible(self, request: Request) -> bool:
        if not self.agency_scoped:
            return await super().is_accessible(request)
        agency_id = await self._get_agency_id(request)
        return agency_id is not None

    async def count(
        self,
        request: Request,
        where: Union[Dict[str, Any], str, None] = None,
    ) -> int:
        if not self._has_service:
            return await super().count(request, where)
        svc = self.get_service(request)
        if self.agency_scoped:
            agency_id = await self._get_agency_id(request)
            if agency_id and hasattr(svc.repository, "count_by_agency"):
                return await svc.repository.count_by_agency(agency_id, where)
        return await svc.count(where)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[Dict[str, Any], str, None] = None,
        order_by: Optional[List[str]] = None,
    ) -> list:
        if not self._has_service:
            return await super().find_all(request, skip, limit, where, order_by)
        svc = self.get_service(request)
        if self.agency_scoped:
            agency_id = await self._get_agency_id(request)
            if agency_id and hasattr(svc.repository, "list_by_agency"):
                return await svc.repository.list_by_agency(agency_id, skip, limit, where, order_by)
        return await svc.list(skip=skip, limit=limit, where=where, order_by=order_by)

    async def find_by_pk(self, request: Request, pk: Any) -> Any:
        if not self._has_service:
            return await super().find_by_pk(request, pk)
        return await self.get_service(request).get(pk)

    async def find_by_pks(self, request: Request, pks: List[Any]) -> list:
        if not self._has_service:
            return await super().find_by_pks(request, pks)
        svc = self.get_service(request)
        return [r for pk in pks if (r := await svc.get(pk))]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        if not self._has_service:
            return await super().create(request, data)
        await self.validate(request, data)
        # Auto-inject agency_id on creation for agency-scoped models
        if self.agency_scoped and hasattr(self.model, "agency_id"):
            agency_id = await self._get_agency_id(request)
            if agency_id and "agency_id" not in data:
                data["agency_id"] = agency_id
        obj = self.model(**data)
        setattr(obj, "_current_user_id",
                request.state.user.email if request.state.user else None)
        return await self.get_service(request).create(obj)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        if not self._has_service:
            return await super().edit(request, pk, data)
        await self.validate(request, data)
        data["_current_user_id"] = (
            request.state.user.email if request.state.user else None
        )
        return await self.get_service(request).update(pk, data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        if not self._has_service:
            return await super().delete(request, pks)
        svc = self.get_service(request)
        count = 0
        for pk in pks:
            await svc.delete(pk)
            count += 1
        return count
