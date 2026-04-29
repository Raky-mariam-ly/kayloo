from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, ImageField, StringField, URLField, DateTimeField
from admin.base import AdminModelView, SafeEnumField
from admin.choices import load_country_choices


class PartnerView(AdminModelView):
    list_template = "partner_list.html"

    fields = [
        SafeEnumField("country", choices_loader=load_country_choices, required=True, label="Country"),
        StringField("name", required=True),
        StringField("email", required=True),
        StringField("phone_number", required=True, label="Phone Number"),
        ImageField("logo_url", label="Logo", exclude_from_list=True),
        StringField("logo_src", label="Logo", read_only=True, sortable=False, searchable=False,
                    exclude_from_create=True, exclude_from_edit=True, exclude_from_detail=True),
        URLField("siteweb_url", label="Website URL", exclude_from_list=True),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("country"):
            errors["country"] = "Country is required"
        if not data.get("name"):
            errors["name"] = "Name is required"
        if not data.get("email"):
            errors["email"] = "Email is required"
        if not data.get("phone_number"):
            errors["phone_number"] = "Phone number is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
