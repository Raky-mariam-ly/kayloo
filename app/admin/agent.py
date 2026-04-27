import uuid
from typing import Any, Dict, Sequence
from fastapi import Request
from starlette_admin import BaseField
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import StringField, DateTimeField
from starlette_admin.helpers import RequestAction
from admin.base import AdminModelView, UUIDEnumField, _is_full_admin, _is_agent
from admin.choices import load_user_choices, load_agency_choices


class AgentView(AdminModelView):
    list_template = "agent_list.html"
    detail_template = "agent_detail.html"

    def is_accessible(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_create(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_edit(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_delete(self, request) -> bool:
        return _is_full_admin(request)

    fields = [
        UUIDEnumField("user_id", choices_loader=load_user_choices, required=True,
                      label="User", coerce=uuid.UUID),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices, required=True,
                      label="Agency", coerce=uuid.UUID),
        StringField("slug", label="Slug (e.g. firstname-lastname-city)"),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    def get_fields_list(self, request: Request, action: RequestAction = None) -> Sequence[BaseField]:
        fields = list(super().get_fields_list(request, action))
        if action in (RequestAction.CREATE, RequestAction.EDIT) and _is_agent(request):
            if getattr(request.state, "agent_agency_id", None):
                fields = [f for f in fields if f.name != "agency_id"]
        return fields

    def get_list_query(self, request):
        query = super().get_list_query(request)
        if _is_agent(request):
            from models.agent import Agent
            agency_id = getattr(request.state, "agent_agency_id", None)
            if agency_id:
                query = query.where(Agent.agency_id == agency_id)
        return query

    def get_count_query(self, request):
        query = super().get_count_query(request)
        if _is_agent(request):
            from models.agent import Agent
            agency_id = getattr(request.state, "agent_agency_id", None)
            if agency_id:
                query = query.where(Agent.agency_id == agency_id)
        return query

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if not data.get("user_id"):
            errors["user_id"] = "User is required"
        if _is_agent(request):
            agency_id = getattr(request.state, "agent_agency_id", None)
            if not agency_id and not data.get("agency_id"):
                errors["agency_id"] = "Agency is required (your account is not yet linked to an agency)"
        elif not data.get("agency_id"):
            errors["agency_id"] = "Agency is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        if _is_agent(request):
            agency_id = getattr(request.state, "agent_agency_id", None)
            if agency_id:
                data["agency_id"] = agency_id
        return await super().create(request, data)
