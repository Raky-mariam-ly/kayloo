from starlette_admin.fields import (
    BooleanField, DateTimeField, EnumField, StringField,
)

from admin.base import AdminModelView
from repositories.notification import NotificationRepository
from services.notification import NotificationService


NOTIFICATION_TYPE_CHOICES = [
    ("new_lead", "New Lead"),
    ("lead_assigned", "Lead Assigned"),
    ("task_due", "Task Due"),
    ("task_overdue", "Task Overdue"),
    ("new_message", "New Message"),
    ("review_posted", "Review Posted"),
    ("saved_search_match", "Search Alert"),
    ("system", "System"),
]


class NotificationView(AdminModelView):
    service_class = NotificationService
    repository_class = NotificationRepository
    agency_scoped = True

    fields = [
        StringField("title", label="Title"),
        StringField("body", label="Content"),
        EnumField("notification_type", choices=NOTIFICATION_TYPE_CHOICES, label="Type"),
        StringField("reference_type", label="Ref. type", exclude_from_list=True),
        StringField("reference_id", label="Ref. ID", exclude_from_list=True),
        BooleanField("is_read", label="Read"),
        StringField("user_id", label="User", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
    ]

    row_actions = ['view']
