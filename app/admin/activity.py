from starlette_admin.fields import (
    DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.activity import ActivityRepository
from services.activity import ActivityService


ACTIVITY_TYPE_CHOICES = [
    ("call", "Appel"),
    ("email", "Email"),
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("visit", "Visite"),
    ("meeting", "Réunion"),
    ("note", "Note"),
    ("status_change", "Changement de statut"),
    ("document_sent", "Document envoyé"),
    ("offer_made", "Offre faite"),
    ("offer_accepted", "Offre acceptée"),
    ("offer_rejected", "Offre refusée"),
]


class ActivityView(AdminModelView):
    service_class = ActivityService
    repository_class = ActivityRepository
    agency_scoped = True
    fields = [
        EnumField("activity_type", choices=ACTIVITY_TYPE_CHOICES, label="Type"),
        StringField("title", label="Titre"),
        TextAreaField("description", label="Description",
                      exclude_from_list=True),
        StringField("lead_id", label="Lead ID", exclude_from_list=True),
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("agent_id", label="Agent ID", exclude_from_list=True),
        DateTimeField("scheduled_at", label="Planifié",
                      exclude_from_list=True),
        DateTimeField("completed_at", label="Terminé", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
    ]

    row_actions = ['view']
