from starlette_admin.fields import (
    BooleanField, DateTimeField, EnumField, StringField,
)

from admin.base import AdminModelView
from repositories.notification import NotificationRepository
from services.notification import NotificationService


NOTIFICATION_TYPE_CHOICES = [
    ("new_lead", "Nouveau lead"),
    ("lead_assigned", "Lead assigné"),
    ("task_due", "Tâche à faire"),
    ("task_overdue", "Tâche en retard"),
    ("new_message", "Nouveau message"),
    ("review_posted", "Avis publié"),
    ("saved_search_match", "Alerte recherche"),
    ("system", "Système"),
]


class NotificationView(AdminModelView):
    service_class = NotificationService
    repository_class = NotificationRepository
    agency_scoped = True

    fields = [
        StringField("title", label="Titre"),
        StringField("body", label="Contenu"),
        EnumField("notification_type",
                  choices=NOTIFICATION_TYPE_CHOICES, label="Type"),
        StringField("reference_type", label="Ref. type",
                    exclude_from_list=True),
        StringField("reference_id", label="Ref. ID", exclude_from_list=True),
        BooleanField("is_read", label="Lu"),
        StringField("user_id", label="Utilisateur", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
    ]

    row_actions = ['view']
