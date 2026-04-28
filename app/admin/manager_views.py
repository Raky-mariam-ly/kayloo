import logging

from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from admin.base import _is_agent

_log = logging.getLogger(__name__)


async def _get_dashboard_stats(session: AsyncSession, email: str) -> dict:
    from models.property import Property

    stats = {
        "my_listings": 0,
        "published_listings": 0,
        "pending_listings": 0,
        "expired_listings": 0,
        "my_prospects": 0,
        "my_requests": 0,
    }
    try:
        base = select(func.count(Property.id)).where(Property.created_by == email)

        stats["my_listings"] = (await session.execute(base)).scalar() or 0
        stats["published_listings"] = (
            await session.execute(base.where(Property.status == "for_sale"))
        ).scalar() or 0
        stats["pending_listings"] = (
            await session.execute(base.where(Property.status == "reserved"))
        ).scalar() or 0
        stats["expired_listings"] = (
            await session.execute(base.where(Property.status == "sold"))
        ).scalar() or 0
    except Exception:
        _log.exception("Failed to load dashboard stats for %s", email)
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
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        user = request.state.user
        stats = await _get_dashboard_stats(request.state.session, user.email)
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"user": user, "stats": stats},
        )


class ManagerActivitiesView(CustomView):
    def __init__(self):
        super().__init__(
            label="Activities",
            icon="fa fa-list",
            path="/activities",
            template_path="manager_placeholder.html",
            name="manager_activities",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Activities", "icon": "fa-list"},
        )


class ManagerStatisticsView(CustomView):
    def __init__(self):
        super().__init__(
            label="Statistics",
            icon="fa fa-bar-chart",
            path="/statistics",
            template_path="manager_placeholder.html",
            name="manager_statistics",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Statistics", "icon": "fa-bar-chart"},
        )


class ManagerOffersView(CustomView):
    def __init__(self):
        super().__init__(
            label="Offers",
            icon="fa fa-tag",
            path="/offers",
            template_path="manager_placeholder.html",
            name="manager_offers",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Offers", "icon": "fa-tag"},
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
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Prospects", "icon": "fa-users"},
        )


class ManagerRequestsView(CustomView):
    def __init__(self):
        super().__init__(
            label="Requests",
            icon="fa fa-comments",
            path="/requests",
            template_path="manager_placeholder.html",
            name="manager_requests",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        return _is_agent(request)

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Information Requests", "icon": "fa-comments"},
        )
