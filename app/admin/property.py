import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    BooleanField, DateField, DateTimeField, DecimalField, EnumField,
    FloatField, ImageField, IntegerField, StringField, TextAreaField,
)
from admin.base import AdminModelView, SafeEnumField, SectionField, UUIDEnumField, _is_full_admin, _is_agent
from admin.choices import (
    load_agency_choices,
    load_building_choices,
    load_country_choices,
    load_city_choices,
    load_zone_choices,
    load_property_type_choices,
    load_property_rent_type_choices,
)
from models.property_gallery import PropertyGallery

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
    list_template = "property_list.html"
    create_template = "property_create.html"
    edit_template = "property_edit.html"
    detail_template = "property_detail.html"

    fields = [
        # ── Identification ──
        SectionField("_sec_identification", label="Identification"),
        StringField("code", label="Code"),
        StringField("label", label="Label"),
        EnumField("status", choices=STATUS_CHOICES, label="Statut"),
        SafeEnumField("type", choices_loader=load_property_type_choices, label="Type"),
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
        SafeEnumField("rent_type", choices_loader=load_property_rent_type_choices,
                      label="Type de location", exclude_from_list=True),
        EnumField("rental_period", choices=RENTAL_PERIOD_CHOICES,
                  label="Période de location", exclude_from_list=True),
        EnumField("managed_by", choices=MANAGED_BY_CHOICES,
                  label="Géré par", exclude_from_list=True),

        # ── Localisation ──
        SectionField("_sec_localisation", label="Localisation", exclude_from_list=True),
        SafeEnumField("country", choices_loader=load_country_choices,
                      label="Pays", exclude_from_list=True),
        SafeEnumField("city", choices_loader=load_city_choices,
                      label="Ville", exclude_from_list=True),
        SafeEnumField("zone", choices_loader=load_zone_choices,
                      label="Zone", exclude_from_list=True),
        StringField("street", label="Rue", exclude_from_list=True),
        StringField("address", label="Adresse", exclude_from_list=True),
        StringField("level", label="Niveau", exclude_from_list=True),
        StringField("position", label="Position", exclude_from_list=True),
        StringField("apartment_number", label="N° Appartement", exclude_from_list=True),

        # ── Description ──
        SectionField("_sec_description", label="Description", exclude_from_list=True),
        TextAreaField("description", label="Description", exclude_from_list=True),
        ImageField("image_url", label="Image de couverture", exclude_from_list=True),
        ImageField("gallery_images", label="Galerie de photos", multiple=True, exclude_from_list=True),

        # ── Caractéristiques physiques ──
        SectionField("_sec_physique", label="Caractéristiques", exclude_from_list=True),
        DecimalField("surface", label="Surface (m²)", min=0, step="0.01"),
        IntegerField("bed_room_count", label="Chambres", min=0),
        IntegerField("bath_room_count", label="Salles de bain", min=0),
        IntegerField("kitchen_count", label="Cuisines", min=0),
        IntegerField("living_room_count", label="Salons", min=0),
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

    def is_accessible(self, request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_create(self, request) -> bool:
        return _is_full_admin(request)

    def can_edit(self, request) -> bool:
        return _is_full_admin(request)

    def can_delete(self, request) -> bool:
        return _is_full_admin(request)

    def get_list_query(self, request):
        query = super().get_list_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        if agency_id:
            from models.property import Property
            query = query.where(Property.agency_id == agency_id)
        return query

    def get_count_query(self, request):
        query = super().get_count_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        if agency_id:
            from models.property import Property
            query = query.where(Property.agency_id == agency_id)
        return query

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

    # ── Gallery — create / edit en une seule transaction ────────────────────

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            gallery_files = self._unpack_gallery(data.get("gallery_images"))
            self._prepare_file_fields_for_populate(data)
            await self.validate(request, data)

            session = request.state.session
            obj = await self._populate_obj(request, self.model(), data)
            session.add(obj)
            await self.before_create(request, data, obj)
            await session.flush()  # obtenir obj.id sans commit

            if gallery_files:
                session.add(PropertyGallery(property_id=obj.id, images=gallery_files))

            await session.commit()
            await session.refresh(obj)
            await self.after_create(request, obj)
            return obj
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            gallery_files = self._unpack_gallery(data.get("gallery_images"))
            self._prepare_file_fields_for_populate(data)
            await self.validate(request, data)

            session = request.state.session
            obj = await self.find_by_pk(request, pk)
            await self._populate_obj(request, obj, data, True)
            session.add(obj)
            await self.before_edit(request, data, obj)

            if gallery_files:
                from sqlalchemy import select
                result = await session.execute(
                    select(PropertyGallery).where(PropertyGallery.property_id == obj.id)
                )
                gallery = result.scalar_one_or_none()
                if gallery:
                    gallery.images = gallery_files
                else:
                    session.add(PropertyGallery(property_id=obj.id, images=gallery_files))

            await session.commit()
            await session.refresh(obj)
            await self.after_edit(request, obj)
            return obj
        except Exception as e:
            return self.handle_exception(e)

    async def after_create(self, request: Request, obj: Any) -> None:
        from admin.choices import warm_choices_cache
        await warm_choices_cache(request.state.session)

    async def after_edit(self, request: Request, obj: Any) -> None:
        from admin.choices import warm_choices_cache
        await warm_choices_cache(request.state.session)

    @staticmethod
    def _unpack_gallery(raw: Any) -> list:
        """Dépaquette le (files, should_delete) produit par ImageField.parse_form_data."""
        if raw is None:
            return []
        if isinstance(raw, tuple) and len(raw) == 2:
            files, should_delete = raw
            if should_delete or not files:
                return []
            return files if isinstance(files, list) else [files]
        return []

    @staticmethod
    def _prepare_file_fields_for_populate(data: Dict[str, Any]) -> None:
        """
        Ensure all FileField values are non-None for Starlette-Admin _populate_obj.
        Also neutralize gallery_images because it's not a Property model attribute.
        """
        if data.get("image_url") is None:
            data["image_url"] = (None, False)
        # Keep FileField non-None while preventing setattr on unknown attribute.
        data["gallery_images"] = ([], False)
