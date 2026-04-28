from starlette_admin.fields import (
    DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.activity import ActivityRepository
from services.activity import ActivityService


ACTIVITY_TYPE_CHOICES = [
    ("call", "Call"),
    ("email", "Email"),
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("visit", "Visit"),
    ("meeting", "Meeting"),
    ("note", "Note"),
    ("status_change", "Status Change"),
    ("document_sent", "Document Sent"),
    ("offer_made", "Offer Made"),
    ("offer_accepted", "Offer Accepted"),
    ("offer_rejected", "Offer Rejected"),
]


class ActivityView(AdminModelView):
    service_class = ActivityService
    repository_class = ActivityRepository
    agency_scoped = True
    fields = [
        EnumField("activity_type", choices=ACTIVITY_TYPE_CHOICES, label="Type"),
        StringField("title", label="Title"),
        TextAreaField("description", label="Description", exclude_from_list=True),
        StringField("lead_id", label="Lead ID", exclude_from_list=True),
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("agent_id", label="Agent ID", exclude_from_list=True),
        DateTimeField("scheduled_at", label="Scheduled", exclude_from_list=True),
        DateTimeField("completed_at", label="Completed", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
    ]

    row_actions = ['view']
