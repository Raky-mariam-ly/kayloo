from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    BooleanField, DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.contact import ContactRepository
from services.contact import ContactService


CONTACT_TYPE_CHOICES = [
    ("buyer", "Acheteur"),
    ("seller", "Vendeur"),
    ("tenant", "Locataire"),
    ("landlord", "Propriétaire"),
    ("investor", "Investisseur"),
]


class ContactView(AdminModelView):
    service_class = ContactService
    repository_class = ContactRepository
    agency_scoped = True

    fields = [
        StringField("first_name", label="Prénom", required=True),
        StringField("last_name", label="Nom", required=True),
        StringField("email", label="Email"),
        StringField("phone_number", label="Téléphone"),
        EnumField("contact_type", choices=CONTACT_TYPE_CHOICES, label="Type"),
        StringField("country", label="Pays", exclude_from_list=True),
        StringField("city", label="Ville", exclude_from_list=True),
        StringField("address", label="Adresse", exclude_from_list=True),
        BooleanField("is_active", label="Actif"),
        TextAreaField("notes", label="Notes", exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]
