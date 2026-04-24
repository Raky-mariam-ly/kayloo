from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, StringField, DateTimeField
from admin.base import AdminModelView, SafeEnumField
from admin.choices import load_country_choices


class CityView(AdminModelView):
    list_template = "generic_list.html"

    fields = [
        SafeEnumField("country", choices_loader=load_country_choices, required=True, label="Country"),
        StringField("code", required=True),
        StringField("name"),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        StringField("updated_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("code") or len(data["code"]) < 2:
            errors["code"] = "Ensure code has at least 2 characters"
        if not data.get("country"):
            errors["country"] = "Country is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
