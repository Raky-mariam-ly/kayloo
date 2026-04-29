import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import DateTimeField, FloatField, ImageField, StringField, URLField
from admin.base import AdminModelView, UUIDEnumField
from admin.choices import load_agency_choices, load_city_id_choices


class BuildingView(AdminModelView):
    list_template = "generic_list.html"

    fields = [
        StringField("name", label="Name", required=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agency", coerce=uuid.UUID, exclude_from_list=True),
        UUIDEnumField("city_id", choices_loader=load_city_id_choices,
                      label="City", coerce=uuid.UUID, exclude_from_list=True),
        StringField("address", label="Address", exclude_from_list=True),
        FloatField("lat", label="Latitude", exclude_from_list=True),
        FloatField("lng", label="Longitude", exclude_from_list=True),
        StringField("slug", label="Slug", exclude_from_list=True),
        ImageField("image_url", label="Image", exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = {}
        if not data.get("name"):
            errors["name"] = "Name is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
