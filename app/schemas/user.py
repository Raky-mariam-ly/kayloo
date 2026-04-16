import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    phone_number: str
    gender: str | None = None
    role: str
    avatar_url: str | None = None
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    phone_number: str
    gender: str | None = None
    role: str
    avatar_url: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    last_name: str
    phone_number: str
    gender: str | None = None
    role: str
    avatar_url: str | None = None
