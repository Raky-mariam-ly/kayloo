from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import EnumField, BooleanField, StringField, URLField, DateTimeField
from admin.base import AdminModelView
from admin.choices import load_country_choices


class AgencyView(AdminModelView):
    fields = [
        EnumField("country", choices_loader=load_country_choices, required=True, label="Country"),
        StringField("name"),
        StringField("email"),
        StringField("phone_number", label="Phone Number"),
        URLField("logo_url", label="Logo URL", exclude_from_list=True),
        URLField("siteweb_url", label="Website URL", exclude_from_list=True),
        URLField("whatsapp_url", label="WhatsApp URL", exclude_from_list=True),
        URLField("x_url", label="X (Twitter) URL", exclude_from_list=True),
        URLField("facebook_url", label="Facebook URL", exclude_from_list=True),
        URLField("tiktok_url", label="TikTok URL", exclude_from_list=True),
        URLField("youtube_url", label="YouTube URL", exclude_from_list=True),
        URLField("instagram_url", label="Instagram URL", exclude_from_list=True),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("country"):
            errors["country"] = "Country is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
