import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    BooleanField, DateField, DateTimeField, DecimalField, EnumField,
    FloatField, IntegerField, StringField, TextAreaField,
)
from admin.base import AdminModelView, ImageUploadField, PropertyImagesField, SectionField, UUIDEnumField
from admin.choices import (
    load_agency_choices,
    load_building_choices,
    load_country_choices,
    load_city_choices,
    load_property_type_choices,
    load_property_rent_type_choices,
)

STATUS_CHOICES = [
    ("free", "Libre"),
    ("for_sale", "À vendre"),
    ("for_rent", "À louer"),
    ("reserved", "Réservé"),
    ("rented", "Loué"),
    ("sold", "Vendu"),
    ("under_construction", "En construction"),
]

USAGE_CHOICES = [
    ("residential", "Résidentiel"),
    ("commercial", "Commercial"),
    ("office", "Bureau"),
    ("industrial", "Industriel"),
    ("land", "Terrain"),
    ("mixed", "Mixte"),
]

BASE_PRICE_TYPE_CHOICES = [
    ("fixed", "Prix fixe"),
    ("per_night", "Par nuit"),
    ("per_week", "Par semaine"),
    ("per_month", "Par mois"),
    ("per_year", "Par an"),
]

RENTAL_PERIOD_CHOICES = [
    ("daily", "Journalier"),
    ("weekly", "Hebdomadaire"),
    ("monthly", "Mensuel"),
    ("yearly", "Annuel"),
]

MANAGED_BY_CHOICES = [
    ("agency", "Agence"),
    ("owner", "Propriétaire"),
    ("platform", "Plateforme"),
]

CURRENCY_CHOICES = [
    ("XOF", "XOF — Franc CFA (BCEAO)"),
    ("XAF", "XAF — Franc CFA (BEAC)"),
    ("GNF", "GNF — Franc guinéen"),
    ("MAD", "MAD — Dirham marocain"),
    ("EUR", "EUR — Euro"),
    ("USD", "USD — Dollar américain"),
]


class PropertyView(AdminModelView):
    create_template = "property_create.html"
    edit_template = "property_edit.html"
    detail_template = "property_detail.html"

    fields = [
        # ── Identification ──
        SectionField("_sec_identification", label="Identification"),
        StringField("code", label="Code"),
        StringField("label", label="Label"),
        EnumField("status", choices=STATUS_CHOICES, label="Statut"),
        EnumField("type", choices_loader=load_property_type_choices, label="Type"),
        EnumField("usage", choices=USAGE_CHOICES, label="Usage", exclude_from_list=True),

        # ── Relations ──
        SectionField("_sec_relations", label="Relations", exclude_from_list=True),
        UUIDEnumField("building_id", choices_loader=load_building_choices,
                      label="Immeuble", coerce=uuid.UUID, exclude_from_list=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agence", coerce=uuid.UUID, exclude_from_list=True),

        # ── Classification ──
        SectionField("_sec_classification", label="Classification", exclude_from_list=True),
        EnumField("status_before_reserved", choices=STATUS_CHOICES,
                  label="Statut avant réservation", exclude_from_list=True),
        EnumField("rent_type", choices_loader=load_property_rent_type_choices,
                  label="Type de location", exclude_from_list=True),
        EnumField("rental_period", choices=RENTAL_PERIOD_CHOICES,
                  label="Période de location", exclude_from_list=True),
        EnumField("managed_by", choices=MANAGED_BY_CHOICES,
                  label="Géré par", exclude_from_list=True),

        # ── Localisation ──
        SectionField("_sec_localisation", label="Localisation", exclude_from_list=True),
        EnumField("country", choices_loader=load_country_choices,
                  label="Pays", exclude_from_list=True),
        EnumField("city", choices_loader=load_city_choices,
                  label="Ville", exclude_from_list=True),
        StringField("zone", label="Zone", exclude_from_list=True),
        StringField("street", label="Rue", exclude_from_list=True),
        StringField("address", label="Adresse", exclude_from_list=True),
        StringField("level", label="Niveau", exclude_from_list=True),
        StringField("position", label="Position", exclude_from_list=True),
        StringField("apartment_number", label="N° Appartement", exclude_from_list=True),

        # ── Description ──
        SectionField("_sec_description", label="Description", exclude_from_list=True),
        TextAreaField("description", label="Description", exclude_from_list=True),
        ImageUploadField("image_url", label="Image de couverture", exclude_from_list=True),
        PropertyImagesField("images", label="Photos du bien", exclude_from_list=True),

        # ── Caractéristiques physiques ──
        SectionField("_sec_physique", label="Caractéristiques", exclude_from_list=True),
        DecimalField("surface", label="Surface (m²)", min=0, step="0.01"),
        IntegerField("bed_room_count", label="Chambres", min=0),
        IntegerField("bath_room_count", label="Salles de bain", min=0, exclude_from_list=True),
        IntegerField("kitchen_count", label="Cuisines", min=0, exclude_from_list=True),
        IntegerField("living_room_count", label="Salons", min=0, exclude_from_list=True),
        IntegerField("build_year", label="Année", min=1800, max=2100, exclude_from_list=True),
        DecimalField("lng", label="Longitude", min=-180, max=180, step="0.000001", exclude_from_list=True),
        DecimalField("lat", label="Latitude", min=-90, max=90, step="0.000001", exclude_from_list=True),

        # ── Acquisition ──
        SectionField("_sec_acquisition", label="Acquisition", exclude_from_list=True),
        DateField("acquisition_date", label="Date d'acquisition", exclude_from_list=True),
        FloatField("acquisition_price", label="Prix d'acquisition", exclude_from_list=True),
        FloatField("acquisition_fee", label="Frais d'acquisition", exclude_from_list=True),
        DateField("free_since", label="Libre depuis", exclude_from_list=True),

        # ── Financier ──
        SectionField("_sec_financier", label="Financier", exclude_from_list=True),
        EnumField("currency", choices=CURRENCY_CHOICES, label="Devise", exclude_from_list=True),
        EnumField("base_price_type", choices=BASE_PRICE_TYPE_CHOICES,
                  label="Type prix de base", exclude_from_list=True),
        FloatField("price", label="Prix"),
        FloatField("base_price", label="Prix de base", exclude_from_list=True),
        FloatField("extra_price", label="Prix extra", exclude_from_list=True),
        FloatField("sale_price", label="Prix de vente", exclude_from_list=True),
        FloatField("rent_price", label="Loyer", exclude_from_list=True),
        FloatField("syndic_amount", label="Charges syndic", exclude_from_list=True),

        # ── Taux ──
        SectionField("_sec_taux", label="Taux", exclude_from_list=True),
        DecimalField("vat_rate", label="TVA", min=0, max=100, step="0.01", exclude_from_list=True),
        DecimalField("tom_rate", label="TOM", min=0, max=100, step="0.01", exclude_from_list=True),
        DecimalField("ir_rate", label="IR", min=0, max=100, step="0.01", exclude_from_list=True),
        DecimalField("mgmt_rate", label="Gestion", min=0, max=100, step="0.01", exclude_from_list=True),
        DecimalField("commission_rate", label="Commission", min=0, max=100, step="0.01", exclude_from_list=True),
        DecimalField("deposit_rate", label="Caution", min=0, max=100, step="0.01", exclude_from_list=True),

        # ── Flags ──
        SectionField("_sec_flags", label="Options", exclude_from_list=True),
        BooleanField("is_hidden", label="Caché"),
        BooleanField("is_exposed", label="Exposé"),
        BooleanField("is_saleable", label="En vente"),
        BooleanField("is_managed", label="Géré"),
        BooleanField("archived", label="Archivé"),
        BooleanField("is_featured", label="En vedette", exclude_from_list=True),

        # ── Audit ──
        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    exclude_fields_from_create = ["created_at", "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at", "updated_at", "created_by", "updated_by"]

    async def _populate_obj(self, request: Request, obj: Any, data: Dict[str, Any], is_edit: bool = False) -> Any:
        from models.property_image import PropertyImage
        # Extraire les images et mettre un tuple neutre (None, False) pour que
        # le parent ne lève pas ValueError via not_none() et ne touche pas la relation
        images_raw = data.get("images")
        data["images"] = (None, False)

        await super()._populate_obj(request, obj, data, is_edit)

        # Traitement des images uploadées
        if images_raw is not None:
            val, should_delete = images_raw if isinstance(images_raw, tuple) else (images_raw, False)
            if should_delete:
                obj.images.clear()
            elif val:
                urls = val if isinstance(val, list) else [val]
                for url in urls:
                    obj.images.append(PropertyImage(url=url))
        return obj

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = {}
        rate_fields = ["vat_rate", "tom_rate", "ir_rate", "mgmt_rate", "commission_rate", "deposit_rate"]
        for f in rate_fields:
            val = data.get(f)
            if val is not None:
                try:
                    v = float(val)
                    if v < 0 or v > 100:
                        errors[f] = "Doit être entre 0 et 100"
                except (ValueError, TypeError):
                    errors[f] = "Valeur numérique invalide"
        if errors:
            from starlette_admin.exceptions import FormValidationError
            raise FormValidationError(errors)
        return await super().validate(request, data)
