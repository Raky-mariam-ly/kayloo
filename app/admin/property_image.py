import uuid as _uuid
from typing import Any, Dict

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import DateTimeField, ImageField, StringField
from admin.base import AdminModelView, SectionField, UUIDEnumField
from admin.choices import load_property_choices
from core.files import PropertyImageFile
from models.property import Property as PropertyModel


class PropertyImageView(AdminModelView):
    fields = [
        SectionField("_sec_property", label="Associated Property"),
        UUIDEnumField("property_id", choices_loader=load_property_choices,
                      label="Property", coerce=_uuid.UUID, required=True),

        SectionField("_sec_images", label="Images (select one or more)"),
        ImageField("url", label="Photos", required=True, multiple=True),

        DateTimeField("created_at", read_only=True, exclude_from_list=True),
        StringField("created_by", read_only=True, exclude_from_list=True),
        DateTimeField("updated_at", read_only=True, exclude_from_list=True),
        StringField("updated_by", read_only=True, exclude_from_list=True),
    ]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        data = await self._arrange_data(request, data)
        await self.validate(request, data)
        session: AsyncSession = request.state.session

        url_raw = data.get("url")
        files = []
        if isinstance(url_raw, tuple) and len(url_raw) == 2:
            val, should_delete = url_raw
            if not should_delete and val is not None:
                files = val if isinstance(val, list) else [val]

        if not files:
            raise FormValidationError({"url": "At least one image is required"})

        pid_raw = data.get("property_id")
        property_id = None
        if pid_raw is not None:
            try:
                property_id = _uuid.UUID(str(pid_raw))
            except (ValueError, AttributeError):
                property_id = pid_raw

        agency_name = None
        if property_id is not None:
            from models.agency import Agency
            row = await session.execute(
                select(Agency.name)
                .join(PropertyModel, PropertyModel.agency_id == Agency.id)
                .where(PropertyModel.id == property_id)
            )
            agency_name = row.scalar_one_or_none()

        first_obj = None
        for file in files:
            obj = self.model()
            obj.property_id = property_id
            obj.url = PropertyImageFile(
                content=file.file,
                filename=file.filename,
                content_type=file.content_type,
                agency_name=agency_name,
                property_id=property_id,
            )
            session.add(obj)
            if first_obj is None:
                first_obj = obj

        await self.before_create(request, data, first_obj)
        await session.commit()
        await session.refresh(first_obj)
        await self.after_create(request, first_obj)
        return first_obj

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = {}
        if not data.get("property_id"):
            errors["property_id"] = "Property is required"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)
