from typing import Any, Dict

from fastapi import Request
from sqlalchemy import select
from starlette_admin.fields import ImageField

from admin.base import AdminModelView, _is_full_admin
from models.site_settings import SiteSettings


class SiteSettingsView(AdminModelView):
    fields = [
        ImageField("logo_url", label="Logo du site", exclude_from_list=False),
    ]

    def is_accessible(self, request: Request) -> bool:
        return _is_full_admin(request)

    def can_create(self, request: Request) -> bool:
        return _is_full_admin(request)

    def can_edit(self, request: Request) -> bool:
        return _is_full_admin(request)

    def can_delete(self, request: Request) -> bool:
        return False

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        session = request.state.session
        result = await session.execute(select(SiteSettings))
        existing = result.scalar_one_or_none()
        if existing:
            return await self.edit(request, existing.id, data)
        return await super().create(request, data)

    async def after_create(self, request: Request, obj: Any) -> None:
        await self._reload_logo(request)

    async def after_edit(self, request: Request, obj: Any) -> None:
        await self._reload_logo(request)

    @staticmethod
    async def _reload_logo(request: Request) -> None:
        from admin.choices import load_site_logo
        await load_site_logo(request.state.session)
