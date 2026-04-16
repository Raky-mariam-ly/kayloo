from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, CountryField, StringField, DateTimeField
from admin.base import AdminModelView


class CountryView(AdminModelView):
    fields = [
        # StringField("code", required=True),
        CountryField("code", required=True, label="Country"),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        StringField("updated_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    exclude_fields_from_create = ["created_at",
                                  "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at",
                                "updated_at", "created_by", "updated_by"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        """Raise FormValidationError to display error in forms"""
        errors: Dict[str, str] = dict()
        if data["code"] is None or len(data["code"]) != 2:
            errors["code"] = "Ensure code has exactly 02 characters"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)
