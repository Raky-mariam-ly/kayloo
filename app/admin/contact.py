from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    BooleanField, DateTimeField, EnumField, StringField, TextAreaField,
)

from admin.base import AdminModelView
from repositories.contact import ContactRepository
from services.contact import ContactService


CONTACT_TYPE_CHOICES = [
    ("buyer", "Buyer"),
    ("seller", "Seller"),
    ("tenant", "Tenant"),
    ("landlord", "Landlord"),
    ("investor", "Investor"),
]


class ContactView(AdminModelView):
    service_class = ContactService
    repository_class = ContactRepository
    agency_scoped = True

    fields = [
        StringField("first_name", label="First Name", required=True),
        StringField("last_name", label="Last Name", required=True),
        StringField("email", label="Email"),
        StringField("phone_number", label="Phone"),
        EnumField("contact_type", choices=CONTACT_TYPE_CHOICES, label="Type"),
        StringField("country", label="Country", exclude_from_list=True),
        StringField("city", label="City", exclude_from_list=True),
        StringField("address", label="Address", exclude_from_list=True),
        BooleanField("is_active", label="Active"),
        TextAreaField("notes", label="Notes", exclude_from_list=True),
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

