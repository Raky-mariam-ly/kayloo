from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


class ViewerFavorisView(CustomView):
    def __init__(self):
        super().__init__(
            label="Favoris",
            icon="fa fa-heart",
            path="/favoris",
            template_path="viewer_favoris.html",
            name="viewer_favoris",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "user", None)
        return user is not None and user.role in ("viewer", "manager", "agent")

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Mes favoris"},
        )


class ViewerMessagesView(CustomView):
    def __init__(self):
        super().__init__(
            label="Messages",
            icon="fa fa-envelope",
            path="/messages",
            template_path="viewer_messages.html",
            name="viewer_messages",
            methods=["GET"],
            add_to_menu=False,
        )

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "user", None)
        return user is not None and user.role in ("viewer", "manager", "agent")

    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=self.template_path,
            context={"title": "Messages"},
        )
