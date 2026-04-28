from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, StringField, DateTimeField
from admin.base import AdminModelView, SafeEnumField
from admin.choices import load_city_choices


class AreaView(AdminModelView):
    list_template = "generic_list.html"

    fields = [
        SafeEnumField("city", choices_loader=load_city_choices, required=True, label="City"),
        StringField("name", required=True),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        StringField("updated_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("name") or len(data["name"]) < 2:
            errors["name"] = "Ensure name has at least 2 characters"
        if not data.get("city"):
            errors["city"] = "City is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
