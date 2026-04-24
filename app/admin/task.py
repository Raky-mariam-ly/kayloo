from starlette_admin.fields import (
    DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.task import TaskRepository
from services.task import TaskService


TASK_TYPE_CHOICES = [
    ("call", "Appel"),
    ("email", "Email"),
    ("visit", "Visite"),
    ("follow_up", "Relance"),
    ("document", "Document"),
    ("other", "Autre"),
]

TASK_STATUS_CHOICES = [
    ("pending", "En attente"),
    ("in_progress", "En cours"),
    ("completed", "Terminé"),
    ("cancelled", "Annulé"),
]

PRIORITY_CHOICES = [
    ("low", "Basse"),
    ("medium", "Moyenne"),
    ("high", "Haute"),
    ("urgent", "Urgente"),
]


class TaskView(AdminModelView):
    service_class = TaskService
    repository_class = TaskRepository
    agency_scoped = True
    fields = [
        StringField("title", label="Titre", required=True),
        TextAreaField("description", label="Description", exclude_from_list=True),
        EnumField("task_type", choices=TASK_TYPE_CHOICES, label="Type"),
        EnumField("status", choices=TASK_STATUS_CHOICES, label="Statut"),
        EnumField("priority", choices=PRIORITY_CHOICES, label="Priorité"),
        DateTimeField("due_date", label="Échéance"),
        DateTimeField("completed_at", label="Terminé le", read_only=True, exclude_from_list=True),
        StringField("lead_id", label="Lead ID", exclude_from_list=True),
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("assigned_to", label="Assigné à", exclude_from_list=True),
        StringField("assigned_by", label="Assigné par", read_only=True, exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["completed_at", "created_at", "updated_at", "assigned_by"]
    exclude_fields_from_edit = ["completed_at", "created_at", "updated_at", "assigned_by"]
