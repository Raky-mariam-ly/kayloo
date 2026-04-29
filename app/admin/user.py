import copy
from typing import Any, Dict, List, Sequence, Tuple

from starlette.requests import Request
from starlette_admin import BaseField
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import EnumField, StringField, PasswordField, DateTimeField, BooleanField, TextAreaField
from starlette_admin.helpers import RequestAction

from core.auth import User, create_user
from admin.base import AdminModelView, SafeEnumField, AVAILABLE_USER_ROLES, GENDER_TYPES, _is_full_admin, _is_agent

_MANAGER_ROLE_CHOICES: List[Tuple[str, str]] = [
    ("manager", "Manager"),
    ("viewer", "Viewer"),
]



class UserView(AdminModelView):
    list_template = "user_list.html"
    detail_template = "user_detail.html"
    edit_template = "user_edit.html"

    fields = [
        StringField("email", label="Email", required=True),
        PasswordField("hashed_password", label="Password"),
        StringField("last_name", label="Last Name"),
        StringField("first_name", label="First Name"),
        EnumField("gender", choices=GENDER_TYPES, select2=False, label="Gender"),
        StringField("phone_number", label="Phone"),
        StringField("office_phone", label="Office Phone", exclude_from_list=True),
        StringField("whatsapp_number", label="WhatsApp", exclude_from_list=True),
        StringField("company_name", label="Company", exclude_from_list=True),
        StringField("address", label="Address", exclude_from_list=True),
        TextAreaField("bio", label="Bio", exclude_from_list=True),
        SafeEnumField("role", choices=AVAILABLE_USER_ROLES, select2=False, label="Role"),
        BooleanField("is_active", label="Active"),
        BooleanField("is_verified", label="Verified"),
        BooleanField("is_superuser", label="Super Admin"),
        StringField("avatar_url", label="Avatar URL"),
        StringField("facebook_url", label="Facebook", exclude_from_list=True),
        StringField("x_url", label="X (Twitter)", exclude_from_list=True),
        StringField("linkedin_url", label="LinkedIn", exclude_from_list=True),
        StringField("instagram_url", label="Instagram", exclude_from_list=True),
        StringField("youtube_url", label="YouTube", exclude_from_list=True),
        StringField("tiktok_url", label="TikTok", exclude_from_list=True),
        StringField("siteweb_url", label="Website", exclude_from_list=True),
        DateTimeField("created_at", label="Created On", read_only=True),
        DateTimeField("updated_at", label="Updated On", read_only=True),
        StringField("created_by", label="Created By", read_only=True),
        StringField("updated_by", label="Updated By", read_only=True),
    ]
    fields_default_sort = [User.last_name, ("first_name", True)]
    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by",
                                   "office_phone", "whatsapp_number", "company_name", "address", "bio",
                                   "facebook_url", "x_url", "linkedin_url", "instagram_url",
                                   "youtube_url", "tiktok_url", "siteweb_url"]
    exclude_fields_from_list = ["hashed_password"]
    exclude_fields_from_edit = [
        "hashed_password", "created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_detail = ["hashed_password"]

    def get_fields_list(self, request: Request, action: RequestAction = None) -> Sequence[BaseField]:
        fields = list(super().get_fields_list(request, action))
        if _is_agent(request):
            fields = [f for f in fields if f.name != "is_superuser"]
            new_fields = []
            for f in fields:
                if f.name == "role":
                    f = copy.copy(f)
                    f.choices = _MANAGER_ROLE_CHOICES
                new_fields.append(f)
            fields = new_fields
        return fields

    def is_accessible(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_delete(self, request) -> bool:
        return _is_full_admin(request)

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        role = data.get("role") or "viewer"
        # Les managers ne peuvent créer que manager/viewer
        if _is_agent(request) and role not in ("manager", "viewer"):
            role = "viewer"

        user = await create_user(
            email=data["email"],
            password=data["hashed_password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data.get("phone_number") or "",
            gender=data.get("gender") or "",
            role=role,
        )
        if user is None:
            raise FormValidationError({"email": "This email is already used."})

        return user
