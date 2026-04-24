from typing import Any, Dict

from starlette.requests import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import EnumField, StringField, PasswordField, DateTimeField, BooleanField, TextAreaField

from core.auth import User, create_user
from admin.base import AdminModelView, AVAILABLE_USER_ROLES, GENDER_TYPES


class UserView(AdminModelView):
    list_template = "user_list.html"
    detail_template = "user_detail.html"
    edit_template = "user_edit.html"

    fields = [
        StringField("email", label="Email", required=True),
        PasswordField("hashed_password", label="Mot de passe"),
        StringField("last_name", label="Nom"),
        StringField("first_name", label="Prénom"),
        EnumField("gender", choices=GENDER_TYPES, select2=False, label="Genre"),
        StringField("phone_number", label="Téléphone"),
        StringField("office_phone", label="Téléphone bureau", exclude_from_list=True),
        StringField("whatsapp_number", label="WhatsApp", exclude_from_list=True),
        StringField("company_name", label="Compagnie", exclude_from_list=True),
        StringField("address", label="Adresse", exclude_from_list=True),
        TextAreaField("bio", label="Bio", exclude_from_list=True),
        EnumField("role", choices=AVAILABLE_USER_ROLES, select2=False, label="Rôle"),
        BooleanField("is_active", label="Actif"),
        BooleanField("is_verified", label="Vérifié"),
        BooleanField("is_superuser", label="Super admin"),
        StringField("avatar_url", label="Avatar URL"),
        StringField("facebook_url", label="Facebook", exclude_from_list=True),
        StringField("x_url", label="X (Twitter)", exclude_from_list=True),
        StringField("linkedin_url", label="LinkedIn", exclude_from_list=True),
        StringField("instagram_url", label="Instagram", exclude_from_list=True),
        StringField("youtube_url", label="YouTube", exclude_from_list=True),
        StringField("tiktok_url", label="TikTok", exclude_from_list=True),
        StringField("siteweb_url", label="Site web", exclude_from_list=True),
        DateTimeField("created_at", label="Créé le", read_only=True),
        DateTimeField("updated_at", label="Modifié le", read_only=True),
        StringField("created_by", label="Créé par", read_only=True),
        StringField("updated_by", label="Modifié par", read_only=True),
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

    _GENDER_NORMALIZE = {'male': 'M', 'Male': 'M', 'MALE': 'M',
                         'female': 'F', 'Female': 'F', 'FEMALE': 'F'}

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        if data.get('gender') in self._GENDER_NORMALIZE:
            data['gender'] = self._GENDER_NORMALIZE[data['gender']]
        return await super().edit(request, pk, data)

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        try:
            user = await create_user(
                email=data["email"],
                password=data["hashed_password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone_number=data["phone_number"],
                gender=data["gender"],
            )
        except Exception:
            raise FormValidationError({"email": "Cet email est déjà utilisé ou invalide."})
        if user is None:
            raise FormValidationError({"email": "Cet email est déjà utilisé."})
        return user
