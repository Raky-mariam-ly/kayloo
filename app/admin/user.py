from typing import Any, Dict
from starlette.requests import Request
from starlette_admin.fields import EnumField

from core.auth import User, create_user
from admin.base import AdminModelView, AVAILABLE_USER_ROLES, GENDER_TYPES


class UserView(AdminModelView):
    fields = [
        "email",
        "hashed_password",
        "last_name",
        "first_name",
        EnumField("gender", choices=GENDER_TYPES, select2=False),
        "phone_number",
        EnumField("role", choices=AVAILABLE_USER_ROLES, select2=False),
        "is_active",
        "is_verified",
        "is_superuser",
        "avatar_url",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    fields_default_sort = [User.last_name, ("first_name", True)]
    exclude_fields_from_create = ["created_at",
                                  "updated_at", "created_by", "updated_by"]
    exclude_fields_from_list = ["hashed_password"]
    exclude_fields_from_edit = [
        "hashed_password", "created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_detail = ["hashed_password"]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        # Validation logic before creation (e.g., check if email already exists)
        # await ModelView.validate(self, request, data)

        # Custom logic before creation (e.g., hash a password)
        user = await create_user(
            email=data["email"],
            password=data["hashed_password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            gender=data["gender"],
        )
        # Call the parent create method to save to the database
        # return await super().create(request, data)
        return user
