import os
import uuid

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


AVATAR_UPLOAD_DIR = "static/uploads/avatars"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class ProfileView(CustomView):
    """Profile page — GET shows the form, POST saves it."""

    def __init__(self):
        super().__init__(
            label="Mon profil",
            icon="fa fa-user-circle",
            path="/profile",
            template_path="profile.html",
            name="profile",
            methods=["GET", "POST"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return getattr(request.state, "user", None) is not None

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        if request.method == "POST":
            return await self._save_profile(request)
        return await self._get_profile(request, templates)

    # ── GET ────────────────────────────────────────────────────────────────

    async def _get_profile(self, request: Request, templates: Jinja2Templates) -> Response:
        from sqlalchemy import select as sa_select
        from models.agent import Agent
        from models.agency import Agency

        user = request.state.user
        tab = request.query_params.get("tab", "profil")

        # Charger l'agence si l'utilisateur est manager
        agency = None
        if user.role in ("manager", "agent"):
            session = request.state.session
            result = await session.execute(
                sa_select(Agency)
                .join(Agent, Agent.agency_id == Agency.id)
                .where(Agent.user_id == user.id)
            )
            agency = result.scalar_one_or_none()

        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={
                "title": "Mon profil",
                "user": user,
                "agency": agency,
                "tab": tab,
                "success": request.query_params.get("success"),
                "error": request.query_params.get("error"),
            },
        )

    # ── POST: save profile info ────────────────────────────────────────────

    async def _save_profile(self, request: Request) -> Response:
        from core.auth import User
        from sqlalchemy import update as sa_update

        session = request.state.session
        user = request.state.user
        form = await request.form()

        tab = (form.get("_tab") or "profil").strip()

        updates = {}
        for field in [
            "first_name", "last_name", "phone_number", "bio",
            "office_phone", "whatsapp_number", "company_name", "address",
            "facebook_url", "x_url", "linkedin_url",
            "instagram_url", "youtube_url", "tiktok_url", "siteweb_url",
        ]:
            val = (form.get(field) or "").strip()
            updates[field] = val if val else None

        # Required fields must not be empty
        if not updates["first_name"]:
            updates["first_name"] = user.first_name
        if not updates["last_name"]:
            updates["last_name"] = user.last_name

        try:
            await session.execute(
                sa_update(User).where(User.id == user.id).values(**updates)
            )
            await session.commit()
            await session.refresh(user)
        except Exception:
            await session.rollback()
            return RedirectResponse(
                url=f"{request.url.path}?tab={tab}&error=save_failed",
                status_code=303,
            )

        return RedirectResponse(
            url=f"{request.url.path}?tab={tab}&success=1",
            status_code=303,
        )


class ProfileChangePasswordView(CustomView):
    """Change password — POST only."""

    def __init__(self):
        super().__init__(
            label="",
            path="/profile/change-password",
            template_path="profile.html",
            name="profile_change_password",
            methods=["POST"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return getattr(request.state, "user", None) is not None

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        from fastapi_users.db import SQLAlchemyUserDatabase
        from core.auth import User, UserManager

        profile_url = request.url.path.rsplit("/", 1)[0]
        session = request.state.session
        user = request.state.user
        form = await request.form()

        new_password = (form.get("new_password") or "").strip()
        confirm_password = (form.get("confirm_password") or "").strip()

        if not new_password:
            return RedirectResponse(url=profile_url + "?tab=password&error=password_empty", status_code=303)
        if new_password != confirm_password:
            return RedirectResponse(url=profile_url + "?tab=password&error=password_mismatch", status_code=303)
        if len(new_password) < 8:
            return RedirectResponse(url=profile_url + "?tab=password&error=password_short", status_code=303)

        from sqlalchemy import update as sa_update
        from fastapi_users.password import PasswordHelper
        hashed = PasswordHelper().hash(new_password)
        await session.execute(
            sa_update(User).where(User.id == user.id).values(hashed_password=hashed)
        )
        await session.commit()

        return RedirectResponse(url=profile_url + "?tab=password&success=password", status_code=303)


class ProfileDeleteView(CustomView):
    """Delete (deactivate) account — POST only."""

    def __init__(self):
        super().__init__(
            label="",
            path="/profile/delete",
            template_path="profile.html",
            name="profile_delete",
            methods=["POST"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return getattr(request.state, "user", None) is not None

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        from core.auth import User
        from sqlalchemy import update as sa_update

        session = request.state.session
        user = request.state.user

        # Deactivate instead of hard delete for safety
        await session.execute(
            sa_update(User).where(User.id == user.id).values(is_active=False)
        )
        await session.commit()

        # Clear session and redirect to login
        request.session.clear()
        return RedirectResponse(url="/admin/login", status_code=303)


class ProfileUploadView(CustomView):
    """Handles avatar file upload — POST only, no menu entry."""

    def __init__(self):
        super().__init__(
            label="",
            path="/profile/upload",
            template_path="profile.html",
            name="profile_upload",
            methods=["POST"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return getattr(request.state, "user", None) is not None

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        from core.auth import User
        from sqlalchemy import update as sa_update

        # Redirect target: strip /upload suffix
        profile_url = request.url.path.rsplit("/", 1)[0]

        session = request.state.session
        user = request.state.user
        form = await request.form()
        avatar = form.get("avatar")

        if not avatar or not getattr(avatar, "filename", None):
            return RedirectResponse(url=profile_url + "?error=no_file", status_code=303)

        ext = os.path.splitext(avatar.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return RedirectResponse(url=profile_url + "?error=invalid_format", status_code=303)

        os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4()}{ext}"
        dest = os.path.join(AVATAR_UPLOAD_DIR, filename)

        contents = await avatar.read()
        with open(dest, "wb") as f:
            f.write(contents)

        # Supprimer l'ancien avatar du disque
        old_avatar = getattr(user, "avatar_url", None)
        if old_avatar and old_avatar.startswith("uploads/avatars/"):
            old_path = os.path.join("static", old_avatar)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        await session.execute(
            sa_update(User).where(User.id == user.id).values(
                avatar_url=f"uploads/avatars/{filename}"
            )
        )
        await session.commit()
        await session.refresh(user)

        return RedirectResponse(url=profile_url + "?success=1", status_code=303)


class ProfileAgencyView(CustomView):
    """Saves agency info from the manager's profile page — POST only."""

    def __init__(self):
        super().__init__(
            label="",
            path="/profile/agency",
            template_path="profile.html",
            name="profile_agency",
            methods=["POST"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "user", None)
        return user is not None and user.role in ("manager", "agent")

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        from sqlalchemy import update as sa_update, select as sa_select
        from models.agent import Agent
        from models.agency import Agency

        profile_url = request.url.path.rsplit("/", 1)[0]
        session = request.state.session
        user = request.state.user
        form = await request.form()

        # Trouver l'agence du manager
        result = await session.execute(
            sa_select(Agency)
            .join(Agent, Agent.agency_id == Agency.id)
            .where(Agent.user_id == user.id)
        )
        agency = result.scalar_one_or_none()

        if agency is None:
            return RedirectResponse(url=profile_url + "?tab=agence&error=no_agency", status_code=303)

        updates = {}
        for field in ["name", "email", "phone_number", "siteweb_url",
                      "whatsapp_url", "facebook_url", "x_url",
                      "instagram_url", "youtube_url", "tiktok_url"]:
            val = (form.get(field) or "").strip()
            updates[field] = val if val else None

        await session.execute(
            sa_update(Agency).where(Agency.id == agency.id).values(**updates)
        )
        await session.commit()

        return RedirectResponse(url=profile_url + "?tab=agence&success=agency", status_code=303)
