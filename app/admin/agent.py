import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import StringField, DateTimeField
from admin.base import AdminModelView, UUIDEnumField
from admin.choices import load_user_choices, load_agency_choices


class AgentView(AdminModelView):
    fields = [
        UUIDEnumField("user_id", choices_loader=load_user_choices, required=True,
                      label="Utilisateur", coerce=uuid.UUID),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices, required=True,
                      label="Agence", coerce=uuid.UUID),
        StringField("slug", label="Slug (ex: prenom-nom-ville)"),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("user_id"):
            errors["user_id"] = "L'utilisateur est requis"
        if not data.get("agency_id"):
            errors["agency_id"] = "L'agence est requise"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
