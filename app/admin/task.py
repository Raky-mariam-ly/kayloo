from starlette_admin.fields import (
    DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.task import TaskRepository
from services.task import TaskService


TASK_TYPE_CHOICES = [
    ("call", "Call"),
    ("email", "Email"),
    ("visit", "Visit"),
    ("follow_up", "Follow-up"),
    ("document", "Document"),
    ("other", "Other"),
]

TASK_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("urgent", "Urgent"),
]


class TaskView(AdminModelView):
    service_class = TaskService
    repository_class = TaskRepository
    agency_scoped = True
    fields = [
        StringField("title", label="Title", required=True),
        TextAreaField("description", label="Description", exclude_from_list=True),
        EnumField("task_type", choices=TASK_TYPE_CHOICES, label="Type"),
        EnumField("status", choices=TASK_STATUS_CHOICES, label="Status"),
        EnumField("priority", choices=PRIORITY_CHOICES, label="Priority"),
        DateTimeField("due_date", label="Due Date"),
        DateTimeField("completed_at", label="Completed On", read_only=True, exclude_from_list=True),
        StringField("lead_id", label="Lead ID", exclude_from_list=True),
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("assigned_to", label="Assigned To", exclude_from_list=True),
        StringField("assigned_by", label="Assigned By", read_only=True, exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["completed_at", "created_at", "updated_at", "assigned_by"]
    exclude_fields_from_edit = ["completed_at", "created_at", "updated_at", "assigned_by"]
