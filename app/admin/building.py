import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import DateTimeField, FloatField, StringField, URLField
from admin.base import AdminModelView, UUIDEnumField
from admin.choices import load_agency_choices, load_city_id_choices


class BuildingView(AdminModelView):
    fields = [
        StringField("name", label="Nom", required=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agence", coerce=uuid.UUID, exclude_from_list=True),
        UUIDEnumField("city_id", choices_loader=load_city_id_choices,
                      label="Ville", coerce=uuid.UUID, exclude_from_list=True),
        StringField("address", label="Adresse", exclude_from_list=True),
        FloatField("lat", label="Latitude", exclude_from_list=True),
        FloatField("lng", label="Longitude", exclude_from_list=True),
        StringField("slug", label="Slug", exclude_from_list=True),
        URLField("image_url", label="Image URL", exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = {}
        if not data.get("name"):
            errors["name"] = "Le nom est obligatoire"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
