import uuid
from typing import Any, Dict

from fastapi import Request
from starlette_admin.fields import (
    BooleanField, DateField, DateTimeField, EnumField,
    FloatField, ImageField, IntegerField, StringField, TextAreaField,
)
from starlette_admin.exceptions import FormValidationError

from admin.base import AdminModelView, SafeEnumField, SectionField, SmartDecimalField, UUIDEnumField, _is_full_admin, _is_agent
from admin.choices import (
    load_agency_choices,
    load_building_choices,
    load_country_choices,
    load_city_choices,
    load_zone_choices,
    load_property_type_choices,
    load_property_rent_type_choices,
)
from core.files import PropertyImageFile
from models.property import Property
from models.property_gallery import PropertyGallery


STATUS_CHOICES = [
    ("free", "Free"),
    ("for_sale", "For Sale"),
    ("for_rent", "For Rent"),
    ("for_rent_furnished", "Location meublée"),
    ("reserved", "Reserved"),
    ("rented", "Rented"),
    ("sold", "Sold"),
    ("under_construction", "Under Construction"),
]

USAGE_CHOICES = [
    ("residential", "Residential"),
    ("commercial", "Commercial"),
    ("office", "Office"),
    ("industrial", "Industrial"),
    ("land", "Land"),
    ("mixed", "Mixed"),
]

BASE_PRICE_TYPE_CHOICES = [
    ("fixed", "Fixed Price"),
    ("per_night", "Per Night"),
    ("per_week", "Per Week"),
    ("per_month", "Per Month"),
    ("per_year", "Per Year"),
]

RENTAL_PERIOD_CHOICES = [
    ("daily", "Weekly" if False else "Daily"),
    ("weekly", "Weekly"),
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
]

MANAGED_BY_CHOICES = [
    ("agency", "Agency"),
    ("owner", "Owner"),
    ("platform", "Platform"),
]

CURRENCY_CHOICES = [
    ("XOF", "XOF — CFA Franc (BCEAO)"),
    ("XAF", "XAF — CFA Franc (BEAC)"),
    ("GNF", "GNF — Guinean Franc"),
    ("MAD", "MAD — Moroccan Dirham"),
    ("EUR", "EUR — Euro"),
    ("USD", "USD — US Dollar"),
]

RATE_FIELDS = ["vat_rate", "tom_rate", "ir_rate", "mgmt_rate", "commission_rate", "deposit_rate"]
DECIMAL_FIELDS = ["surface", "lng", "lat", "acquisition_price", "acquisition_fee", "price", "base_price", "extra_price", "sale_price", "rent_price", "syndic_amount", "vat_rate", "tom_rate", "ir_rate", "mgmt_rate", "commission_rate", "deposit_rate"]



def validate_rate_fields(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    for field in RATE_FIELDS:
        val = data.get(field)
        if val is not None and val != "":
            try:
                v = float(val)
                if v < 0 or v > 100:
                    errors[field] = "Must be between 0 and 100"
            except (ValueError, TypeError):
                errors[field] = "Invalid numeric value"
    return errors


def clean_decimal_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = data.copy()
    for field in DECIMAL_FIELDS:
        if field in cleaned and cleaned[field] == "":
            cleaned[field] = None
    return cleaned


def clean_data_for_populate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Nettoie les données pour _populate_obj en supprimant les valeurs None problématiques."""
    cleaned = {}
    for key, value in data.items():
        if key in ["image_url", "gallery_images"]:
            continue
        # Convert empty strings to None
        if value == "":
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


def unpack_cover(raw: Any, agency_name: str = None, property_id: Any = None) -> tuple[Any, bool]:
    if raw is None:
        return None, False
    if isinstance(raw, tuple) and len(raw) == 2:
        val, should_delete = raw
        if should_delete:
            return None, True
        if val is None:
            return None, False
        return PropertyImageFile(
            content=val.file,
            filename=val.filename,
            content_type=val.content_type,
            agency_name=agency_name,
            property_id=property_id,
        ), False
    return None, False


def unpack_gallery(raw: Any, agency_name: str = None, property_id: Any = None) -> tuple[list, bool]:
    if raw is None:
        return [], False
    if isinstance(raw, tuple) and len(raw) == 2:
        files, should_delete = raw
        if should_delete:
            return [], True
        if not files:
            return [], False
        files = files if isinstance(files, list) else [files]
        return [
            PropertyImageFile(
                content=f.file,
                filename=f.filename,
                content_type=f.content_type,
                agency_name=agency_name,
                property_id=property_id,
            )
            for f in files
        ], False
    return [], False


class PropertyView(AdminModelView):
    list_template = "property_list.html"
    create_template = "property_create.html"
    edit_template = "property_edit.html"
    detail_template = "property_detail.html"

    fields = [
        SectionField("_sec_identification", label="Identification"),
        StringField("code", label="Code"),
        StringField("label", label="Label"),
        EnumField("status", choices=STATUS_CHOICES, label="Status"),
        SafeEnumField("type", choices_loader=load_property_type_choices, label="Type"),
        EnumField("usage", choices=USAGE_CHOICES, label="Usage", exclude_from_list=True),

        SectionField("_sec_relations", label="Relations", exclude_from_list=True),
        UUIDEnumField("building_id", choices_loader=load_building_choices,
                      label="Building", coerce=uuid.UUID, exclude_from_list=True),
        UUIDEnumField("agency_id", choices_loader=load_agency_choices,
                      label="Agency", coerce=uuid.UUID, exclude_from_list=True),

        SectionField("_sec_classification", label="Classification", exclude_from_list=True),
        EnumField("status_before_reserved", choices=STATUS_CHOICES,
                  label="Status Before Reservation", exclude_from_list=True),
        SafeEnumField("rent_type", choices_loader=load_property_rent_type_choices,
                      label="Rental Type", exclude_from_list=True),
        EnumField("rental_period", choices=RENTAL_PERIOD_CHOICES,
                  label="Rental Period", exclude_from_list=True),
        EnumField("managed_by", choices=MANAGED_BY_CHOICES,
                  label="Managed By", exclude_from_list=True),

        SectionField("_sec_location", label="Location", exclude_from_list=True),
        SafeEnumField("country", choices_loader=load_country_choices,
                      label="Country", exclude_from_list=True),
        SafeEnumField("city", choices_loader=load_city_choices,
                      label="City", exclude_from_list=True),
        SafeEnumField("zone", choices_loader=load_zone_choices,
                      label="Zone", exclude_from_list=True),
        StringField("street", label="Street", exclude_from_list=True),
        StringField("address", label="Address", exclude_from_list=True),
        StringField("level", label="Level", exclude_from_list=True),
        StringField("position", label="Position", exclude_from_list=True),
        StringField("apartment_number", label="Apt Number", exclude_from_list=True),

        SectionField("_sec_description", label="Description", exclude_from_list=True),
        TextAreaField("description", label="Description", exclude_from_list=True),
        ImageField("image_url", label="Cover Image", exclude_from_list=True),
        ImageField("gallery_images", label="Photo Gallery", multiple=True, exclude_from_list=True),

        SectionField("_sec_features", label="Features", exclude_from_list=True),
        SmartDecimalField("surface", label="Surface (m²)", min=0, step="0.01"),
        IntegerField("bed_room_count", label="Bedrooms", min=0),
        IntegerField("bath_room_count", label="Bathrooms", min=0),
        IntegerField("kitchen_count", label="Kitchens", min=0),
        IntegerField("living_room_count", label="Living Rooms", min=0),
        IntegerField("build_year", label="Year Built", min=1800, max=2100, exclude_from_list=True),
        SmartDecimalField("lng", label="Longitude", min=-180, max=180, step="0.000001", exclude_from_list=True),
        SmartDecimalField("lat", label="Latitude", min=-90, max=90, step="0.000001", exclude_from_list=True),

        SectionField("_sec_acquisition", label="Acquisition", exclude_from_list=True),
        DateField("acquisition_date", label="Acquisition Date", exclude_from_list=True),
        FloatField("acquisition_price", label="Acquisition Price", exclude_from_list=True),
        FloatField("acquisition_fee", label="Acquisition Fee", exclude_from_list=True),
        DateField("free_since", label="Available Since", exclude_from_list=True),

        SectionField("_sec_financial", label="Financial", exclude_from_list=True),
        EnumField("currency", choices=CURRENCY_CHOICES, label="Currency", exclude_from_list=True),
        EnumField("base_price_type", choices=BASE_PRICE_TYPE_CHOICES,
                  label="Base Price Type", exclude_from_list=True),
        FloatField("price", label="Price"),
        FloatField("base_price", label="Base Price", exclude_from_list=True),
        FloatField("extra_price", label="Extra Price", exclude_from_list=True),
        FloatField("sale_price", label="Sale Price", exclude_from_list=True),
        FloatField("rent_price", label="Rent", exclude_from_list=True),
        FloatField("syndic_amount", label="Condo Fees", exclude_from_list=True),

        SectionField("_sec_rates", label="Rates", exclude_from_list=True),
        SmartDecimalField("vat_rate", label="VAT", min=0, max=100, step="0.01", exclude_from_list=True),
        SmartDecimalField("tom_rate", label="TOM", min=0, max=100, step="0.01", exclude_from_list=True),
        SmartDecimalField("ir_rate", label="IR", min=0, max=100, step="0.01", exclude_from_list=True),
        SmartDecimalField("mgmt_rate", label="Management", min=0, max=100, step="0.01", exclude_from_list=True),
        SmartDecimalField("commission_rate", label="Commission", min=0, max=100, step="0.01", exclude_from_list=True),
        SmartDecimalField("deposit_rate", label="Deposit", min=0, max=100, step="0.01", exclude_from_list=True),

        SectionField("_sec_flags", label="Options", exclude_from_list=True),
        BooleanField("is_hidden", label="Hidden"),
        BooleanField("is_exposed", label="Exposed"),
        BooleanField("is_saleable", label="For Sale"),
        BooleanField("is_managed", label="Managed"),
        BooleanField("archived", label="Archived"),
        BooleanField("is_featured", label="Featured", exclude_from_list=True),

        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    def is_accessible(self, request: Request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_create(self, request: Request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_edit(self, request: Request) -> bool:
        return _is_full_admin(request) or _is_agent(request)

    def can_delete(self, request: Request) -> bool:
        return _is_full_admin(request)

    def _apply_agency_filter(self, query, agency_id):
        if agency_id:
            return query.where(Property.agency_id == agency_id)
        return query

    def get_list_query(self, request: Request):
        query = super().get_list_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        return self._apply_agency_filter(query, agency_id)

    def get_count_query(self, request: Request):
        query = super().get_count_query(request)
        agency_id = getattr(request.state, "agent_agency_id", None)
        return self._apply_agency_filter(query, agency_id)

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        cleaned_data = clean_decimal_fields(data)
        data.update(cleaned_data)
        
        errors = validate_rate_fields(data)
        if errors:
            raise FormValidationError(errors)
        
        return await super().validate(request, data)

    async def _arrange_data(self, request: Request, data: Dict[str, Any], is_edit: bool = False) -> Dict[str, Any]:
        return data

    async def _populate_obj(self, request, obj, data, **kwargs):
        # Inject no-op sentinels for ImageFields: starlette_admin iterates over ALL view fields
        # (not just keys in data) and calls not_none(data.get(name)) → crash if None.
        # (None, False) = "no upload, no deletion" → starlette_admin leaves the attribute untouched.
        clean = dict(data)
        clean["image_url"] = (None, False)
        clean["gallery_images"] = (None, False)
        return await super()._populate_obj(request, obj, clean, **kwargs)

    async def serialize(self, obj: Any, request: Request, action: Any, **kwargs: Any) -> Dict[str, Any]:
        result = await super().serialize(obj, request, action, **kwargs)
        file_data = getattr(obj, "image_url", None)
        if isinstance(file_data, dict):
            url = file_data.get("url")
            if not url or not str(url).startswith("http"):
                from core.files import _do_spaces_public_url
                file_id = file_data.get("file_id") or ""
                url = _do_spaces_public_url(file_id) or url
            if url:
                result["image_url"] = {"url": url, "filename": str(url).split("/")[-1]}
        return result

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        # Extract images BEFORE cleaning the data
        raw_gallery = data.pop("gallery_images", None)
        raw_cover = data.pop("image_url", None)

        # Clean data for _populate_obj
        clean_data = clean_data_for_populate(data)
        clean_data = await self._arrange_data(request, clean_data)
        await self.validate(request, clean_data)

        session = request.state.session
        obj = await self._populate_obj(request, self.model(), clean_data)
        session.add(obj)
        await self.before_create(request, clean_data, obj)
        await session.flush()

        # Force-load the agency relationship
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Property)
            .where(Property.id == obj.id)
            .options(selectinload(Property.agency))
        )
        obj = result.unique().scalar_one()
        
        agency_name = obj.agency.name if obj.agency else None

        cover_file, _ = unpack_cover(raw_cover, agency_name=agency_name, property_id=obj.id)
        if cover_file is not None:
            obj.image_url = cover_file

        gallery_files, _ = unpack_gallery(raw_gallery, agency_name=agency_name, property_id=obj.id)
        if gallery_files:
            session.add(PropertyGallery(property_id=obj.id, images=gallery_files))

        await session.commit()
        await session.refresh(obj)
        await self.after_create(request, obj)
        return obj

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        # Extract images BEFORE cleaning the data
        raw_gallery = data.pop("gallery_images", None)
        raw_cover = data.pop("image_url", None)

        # Clean data for _populate_obj
        clean_data = clean_data_for_populate(data)
        clean_data = await self._arrange_data(request, clean_data, is_edit=True)
        await self.validate(request, clean_data)

        session = request.state.session
        obj = await self.find_by_pk(request, pk)
        existing_cover = obj.image_url
        
        await self._populate_obj(request, obj, clean_data)
        await self.before_edit(request, clean_data, obj)

        # Force-load the agency relationship si nécessaire
        if obj.agency is None:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                select(Property)
                .where(Property.id == obj.id)
                .options(selectinload(Property.agency))
            )
            obj = result.unique().scalar_one()
        
        agency_name = obj.agency.name if obj.agency else None
        cover_file, delete_cover = unpack_cover(raw_cover, agency_name=agency_name, property_id=obj.id)

        if delete_cover:
            obj.image_url = None
        elif cover_file is not None:
            obj.image_url = cover_file
        else:
            obj.image_url = existing_cover

        gallery_files, delete_gallery = unpack_gallery(raw_gallery, agency_name=agency_name, property_id=obj.id)

        if gallery_files or delete_gallery:
            from sqlalchemy import select
            result = await session.execute(
                select(PropertyGallery).where(PropertyGallery.property_id == obj.id)
            )
            gallery = result.scalar_one_or_none()

            if delete_gallery:
                if gallery:
                    gallery.images = None
            elif gallery:
                gallery.images = gallery_files
            else:
                session.add(PropertyGallery(property_id=obj.id, images=gallery_files))

        await session.commit()
        await session.refresh(obj)
        await self.after_edit(request, obj)
        return obj