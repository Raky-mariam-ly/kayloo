import contextlib
import uuid
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import Column, ForeignKey, DateTime, String, Text, UniqueConstraint, func
from schemas.user import UserCreate
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from core.db import get_db
from core.config import get_settings

settings = get_settings()

Base = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    gender = Column(String(1), nullable=True)
    phone_number = Column(Text, nullable=True)
    role = Column(Text, nullable=False, default="viewer")
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Text, ForeignKey("user.email"), nullable=True)
    updated_by = Column(Text, ForeignKey("user.email"), nullable=True)

    __table_args__ = (
        UniqueConstraint("email", name="ux_user_email"),
    )


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(
            f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


# bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600, cookie_secure=True)


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt-cookie",
    # transport=bearer_transport,
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

get_async_session_context = contextlib.asynccontextmanager(get_db)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: str, password: str, first_name: str, last_name: str, phone_number: str, gender: str, is_superuser: bool = False) -> User | None:
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email, password=password, is_superuser=is_superuser,
                            first_name=first_name, last_name=last_name, phone_number=phone_number,
                            gender=gender, is_active=True, is_verified=True,
                            role="admin" if is_superuser else "viewer",
                        )
                    )
                    print(f"User created {user}")
                    return user
    except UserAlreadyExists:
        print(f"User {email} already exists")
        return None


class FastapiUsersAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        session = request.state.session
        user_manager = UserManager(SQLAlchemyUserDatabase(session, User))
        token_manager = DatabaseStrategy(SQLAlchemyAccessTokenDatabase(
            session, AccessToken), lifetime_seconds=3600)

        # validation logic

        user = await user_manager.authenticate(OAuth2PasswordRequestForm(username=username, password=password))

        if user is None or not user.is_active:
            raise LoginFailed("Email ou mot de passe incorrect")

        if not user.is_superuser:
            raise LoginFailed("Accès refusé : compte non autorisé")

        request.session.update({"session": await token_manager.write_token(user)})

        return response

    async def is_authenticated(self, request) -> bool:
        session: AsyncSession = request.state.session
        user_manager = UserManager(SQLAlchemyUserDatabase(session, User))
        token_manager = DatabaseStrategy(SQLAlchemyAccessTokenDatabase(
            session, AccessToken), lifetime_seconds=3600)

        token = request.session.get("session", None)
        user: User = await token_manager.read_token(token, user_manager)

        if user and user.is_active:
            request.state.user = user
            return True
        return False

    def get_admin_user(self, request: Request) -> AdminUser | None:
        user: User = request.state.user  # Retrieve current user
        photo_url = None
        if user.avatar_url is not None:
            photo_url = request.url_for("static", path=user.avatar_url)
        return AdminUser(username=user.email, photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
