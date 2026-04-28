from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, StringField, TextAreaField, DateTimeField
from admin.base import AdminModelView


class PropertyRentTypeView(AdminModelView):
    list_template = "generic_list.html"

    fields = [
        StringField("code", required=True),
        StringField("label", required=True),
        BooleanField("is_active"),
        TextAreaField("description"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
        StringField("updated_by", read_only=True),
    ]

    exclude_fields_from_list = ["description"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        """Raise FormValidationError to display error in forms"""
        errors: Dict[str, str] = dict()
        if data["code"] is None or len(data["code"]) < 2:
            errors["code"] = "Ensure code has at least 02 characters"
        if data["label"] is None or len(data["label"]) < 5:
            errors["label"] = "Ensure label has at least 05 characters"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)
