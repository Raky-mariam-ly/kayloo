import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    DateField, DateTimeField, EnumField, NumberField, StringField, TextAreaField,
)

from admin.base import AdminModelView, UUIDEnumField
from admin.choices import load_agency_choices
from repositories.lead import LeadRepository
from services.lead import LeadService


SOURCE_CHOICES = [
    ("website", "Website"),
    ("mobile_app", "Mobile App"),
    ("phone", "Phone"),
    ("walk_in", "Walk-in"),
    ("referral", "Referral"),
    ("social_media", "Social Media"),
]

STATUS_CHOICES = [
    ("new", "New"),
    ("contacted", "Contacted"),
    ("qualified", "Qualified"),
    ("negotiation", "Negotiation"),
    ("won", "Won"),
    ("lost", "Lost"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("urgent", "Urgent"),
]


class LeadView(AdminModelView):
    service_class = LeadService
    repository_class = LeadRepository
    agency_scoped = True

    list_template = "crm/lead_list.html"

    fields = [
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("property_id", label="Property ID", exclude_from_list=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agency", coerce=uuid.UUID, exclude_from_list=True),
        EnumField("source", choices=SOURCE_CHOICES, label="Source"),
        EnumField("status", choices=STATUS_CHOICES, label="Status"),
        EnumField("priority", choices=PRIORITY_CHOICES, label="Priority"),
        NumberField("probability", label="Probability (%)",
                    help_text="0-100 — auto-updated on transitions"),
        DateField("expected_close", label="Expected Close"),
        NumberField("deal_value", label="Deal Value",
                    help_text="Leave empty to use property price"),
        StringField("lost_reason", label="Lost Reason", exclude_from_list=True),
        TextAreaField("notes", label="Notes", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

