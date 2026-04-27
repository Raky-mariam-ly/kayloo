from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, StringField, DateTimeField
from admin.base import AdminModelView
from models.country import Country
from repositories.country import CountryRepository
from services.country import CountryService


class CountryView(AdminModelView):
    list_template = "generic_list.html"

    service_class = CountryService
    repository_class = CountryRepository

    fields = [
        StringField("code", required=True, label="Country Code (ISO-2)"),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        StringField("updated_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        code = (data.get("code") or "").strip().upper()
        data["code"] = code

        if not code or len(code) != 2:
            errors["code"] = "Ensure code has exactly 02 characters"

        if len(errors) > 0:
            raise FormValidationError(errors)

        return await super().validate(request, data)
