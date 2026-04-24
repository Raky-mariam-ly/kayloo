from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from core.db import engine


def _is_manager(request: Request) -> bool:
    user = getattr(request.state, "user", None)
    return user is not None and user.role in ("manager", "agent")


async def _get_dashboard_stats(email: str) -> dict:
    from models.property import Property

    stats = {
        "mes_annonces": 0,
        "annonces_publiees": 0,
        "annonces_en_attente": 0,
        "annonces_expirees": 0,
        "mes_prospects": 0,
        "mes_demandes": 0,
    }
    try:
        async with AsyncSession(engine) as session:
            base = select(func.count(Property.id)).where(Property.created_by == email)

            stats["mes_annonces"] = (await session.execute(base)).scalar() or 0
            stats["annonces_publiees"] = (
                await session.execute(base.where(Property.status == "for_sale"))
            ).scalar() or 0
            stats["annonces_en_attente"] = (
                await session.execute(base.where(Property.status == "reserved"))
            ).scalar() or 0
            stats["annonces_expirees"] = (
                await session.execute(base.where(Property.status == "sold"))
            ).scalar() or 0
    except Exception:
        pass
    return stats


class ManagerDashboardView(CustomView):
    def __init__(self):
        super().__init__(
            label="Dashboard",
            icon="fa fa-th",
            path="/dashboard",
            template_path="manager_dashboard.html",
            name="manager_dashboard",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        user = request.state.user
        stats = await _get_dashboard_stats(user.email)
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"user": user, "stats": stats},
        )


class ManagerActivitesView(CustomView):
    def __init__(self):
        super().__init__(
            label="Activités",
            icon="fa fa-list",
            path="/activites",
            template_path="manager_placeholder.html",
            name="manager_activites",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Activités", "icon": "fa-list"},
        )


class ManagerStatistiquesView(CustomView):
    def __init__(self):
        super().__init__(
            label="Statistiques",
            icon="fa fa-bar-chart",
            path="/statistiques",
            template_path="manager_placeholder.html",
            name="manager_statistiques",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Statistiques", "icon": "fa-bar-chart"},
        )


class ManagerOffresView(CustomView):
    def __init__(self):
        super().__init__(
            label="Offres",
            icon="fa fa-tag",
            path="/offres",
            template_path="manager_placeholder.html",
            name="manager_offres",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Offres", "icon": "fa-tag"},
        )


class ManagerProspectsView(CustomView):
    def __init__(self):
        super().__init__(
            label="Prospects",
            icon="fa fa-users",
            path="/prospects-crm",
            template_path="manager_placeholder.html",
            name="manager_prospects",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Prospects", "icon": "fa-users"},
        )


class ManagerDemandesView(CustomView):
    def __init__(self):
        super().__init__(
            label="Demandes",
            icon="fa fa-comments",
            path="/demandes",
            template_path="manager_placeholder.html",
            name="manager_demandes",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_manager(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Demandes de renseignements", "icon": "fa-comments"},
        )
