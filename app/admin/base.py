from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

from starlette.datastructures import FormData
from starlette.requests import Request
from starlette_admin import BaseField, ExportType
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import EnumField
from starlette_admin.helpers import RequestAction


class SafeEnumField(EnumField):
    """EnumField qui retourne la valeur brute si elle n'est pas trouvée dans les choices
    (ex : valeur inactive ou cache désynchronisé) au lieu de lever ValueError."""

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        try:
            return await super().serialize_value(request, value, action)
        except ValueError:
            return value


class UUIDEnumField(EnumField):
    """EnumField qui convertit les UUID en string avant la comparaison avec les choices."""

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        if value is not None:
            value = str(value)
        try:
            return await super().serialize_value(request, value, action)
        except ValueError:
            return value


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

AUDIT_FIELDS_EXCLUDE = ["created_at", "updated_at", "created_by", "updated_by"]


def _is_full_admin(request) -> bool:
    """Superadmin ou admin — accès complet."""
    user = getattr(request.state, "user", None)
    if user is None:
        return False
    return user.is_superuser or user.role in ("superadmin", "admin")


def _is_agent(request) -> bool:
    """Manager (= agent) — accès limité à son agence."""
    user = getattr(request.state, "user", None)
    return user is not None and user.role in ("manager", "agent")


class AdminModelView(ModelView):
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    export_types = [ExportType.EXCEL, ExportType.CSV]

    exclude_fields_from_create = AUDIT_FIELDS_EXCLUDE
    exclude_fields_from_edit = AUDIT_FIELDS_EXCLUDE

    def is_accessible(self, request) -> bool:
        return _is_full_admin(request)

    service_class: Optional[Type] = None
    repository_class: Optional[Type] = None

    def get_service(self, request: Request):
        """Build a service instance from the request's DB session."""
        return self.service_class(self.repository_class(request.state.session))

    @property
    def _has_service(self) -> bool:
        return self.service_class is not None and self.repository_class is not None

    async def count(
        self,
        request: Request,
        where: Union[Dict[str, Any], str, None] = None,
    ) -> int:
        if not self._has_service:
            return await super().count(request, where)
        return await self.get_service(request).count(where)

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
        return await self.get_service(request).list(
            skip=skip, limit=limit, where=where, order_by=order_by,
        )

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

    async def after_create(self, request: Request, obj: Any) -> None:
        from admin.choices import warm_choices_cache
        await warm_choices_cache(request.state.session)

    async def after_edit(self, request: Request, obj: Any) -> None:
        from admin.choices import warm_choices_cache
        await warm_choices_cache(request.state.session)
