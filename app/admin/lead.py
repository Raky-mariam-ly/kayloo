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
    ("website", "Site web"),
    ("mobile_app", "Application mobile"),
    ("phone", "Téléphone"),
    ("walk_in", "Visite"),
    ("referral", "Recommandation"),
    ("social_media", "Réseaux sociaux"),
]

STATUS_CHOICES = [
    ("new", "Nouveau"),
    ("contacted", "Contacté"),
    ("qualified", "Qualifié"),
    ("negotiation", "Négociation"),
    ("won", "Gagné"),
    ("lost", "Perdu"),
]

PRIORITY_CHOICES = [
    ("low", "Basse"),
    ("medium", "Moyenne"),
    ("high", "Haute"),
    ("urgent", "Urgente"),
]


class LeadView(AdminModelView):
    service_class = LeadService
    repository_class = LeadRepository
    agency_scoped = True

    list_template = "crm/lead_list.html"

    fields = [
        StringField("contact_id", label="Contact ID", exclude_from_list=True),
        StringField("property_id", label="Bien ID", exclude_from_list=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agence", coerce=uuid.UUID, exclude_from_list=True),
        EnumField("source", choices=SOURCE_CHOICES, label="Source"),
        EnumField("status", choices=STATUS_CHOICES, label="Statut"),
        EnumField("priority", choices=PRIORITY_CHOICES, label="Priorité"),
        NumberField("probability", label="Probabilité (%)",
                    help_text="0-100 — mis à jour auto lors des transitions"),
        DateField("expected_close", label="Clôture prévue"),
        NumberField("deal_value", label="Valeur négociée",
                    help_text="Laissez vide pour utiliser le prix du bien"),
        StringField("lost_reason", label="Raison perte", exclude_from_list=True),
        TextAreaField("notes", label="Notes", exclude_from_list=True),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]
