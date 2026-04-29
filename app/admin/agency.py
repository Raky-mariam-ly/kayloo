from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, ImageField, StringField, URLField, DateTimeField
from admin.base import AdminModelView, SafeEnumField, _is_full_admin, _is_agent
from admin.choices import load_country_choices


class AgencyView(AdminModelView):
    list_template = "agency_list.html"
    detail_template = "agency_detail.html"

    def is_accessible(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_create(self, request) -> bool:
        return _is_full_admin(request)

    def can_edit(self, request) -> bool:
        return _is_full_admin(request)

    def can_delete(self, request) -> bool:
        return _is_full_admin(request)

    fields = [
        SafeEnumField("country", choices_loader=load_country_choices, required=True, label="Country"),
        StringField("name"),
        StringField("email"),
        StringField("phone_number", label="Phone Number"),
        ImageField("logo_url", label="Logo", exclude_from_list=True),
        StringField("logo_src", label="Logo", read_only=True,
                    exclude_from_create=True, exclude_from_edit=True, exclude_from_detail=True),
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

    def get_list_query(self, request):
        query = super().get_list_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        if agency_id:
            from models.agency import Agency
            query = query.where(Agency.id == agency_id)
        return query

    def get_count_query(self, request):
        query = super().get_count_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        if agency_id:
            from models.agency import Agency
            query = query.where(Agency.id == agency_id)
        return query

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("country"):
            errors["country"] = "Country is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
