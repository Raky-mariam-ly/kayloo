from starlette_admin.fields import (
    DateTimeField, StringField,
)

from starlette.requests import Request

from admin.base import AdminModelView
from repositories.conversation import ConversationRepository, MessageRepository
from services.conversation import ConversationService


class ConversationView(AdminModelView):
    service_class = ConversationService
    repository_class = ConversationRepository
    agency_scoped = True

    def get_service(self, request: Request):
        session = request.state.session
        return ConversationService(
            ConversationRepository(session),
            MessageRepository(session),
        )

    fields = [
        StringField("subject", label="Subject"),
        StringField("property_id", label="Property ID", exclude_from_list=True),
        StringField("lead_id", label="Lead ID", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    row_actions = ['view', 'edit']
