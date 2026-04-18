from typing import Any, Dict, Optional, Union, List

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, CountryField, StringField, DateTimeField
from admin.base import AdminModelView
from models.country import Country
from repositories.country import CountryRepository
from services.country import CountryService


class CountryView(AdminModelView):
    fields = [
        # StringField("code", required=True),
        CountryField("code", required=True, label="Country"),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        StringField("created_by", read_only=True),
        StringField("updated_by", read_only=True),
        DateTimeField("updated_at", read_only=True),
    ]

    exclude_fields_from_create = ["created_at",
                                  "updated_at", "created_by", "updated_by"]
    exclude_fields_from_edit = ["created_at",
                                "updated_at", "created_by", "updated_by"]

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        """Raise FormValidationError to display error in forms"""
        errors: Dict[str, str] = dict()
        if data["code"] is None or len(data["code"]) != 2:
            errors["code"] = "Ensure code has exactly 02 characters"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    async def count(
        self,
        request: Request,
        where: Union[Dict[str, Any], str, None] = None,
    ) -> int:
        service = CountryService(CountryRepository(request.state.session))
        return await service.count(where)

    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[Dict[str, Any], str, None] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[Country]:
        print(
            f"Request attributes: user = {request.state.user}")
        service = CountryService(CountryRepository(request.state.session))

        data: List[Country] = await service.list(skip=skip, limit=limit, where=where, order_by=order_by)
        print(
            f"CountryView.find_all: Found {len(data)} entities, data: {data}")
        return data

    async def find_by_pk(self, request: Request, pk):
        service = CountryService(CountryRepository(request.state.session))
        return await service.get(pk)

    async def find_by_pks(self, request: Request, pks):
        service = CountryService(CountryRepository(request.state.session))
        results = []
        for pk in pks:
            result = await service.get(pk)
            if result:
                results.append(result)
        return results

    async def create(self, request: Request, data: Dict):
        await self.validate(request, data)
        service = CountryService(CountryRepository(request.state.session))
        country = Country(**data)
        setattr(country, "_current_user_id",
                request.state.user.email if request.state.user else None)
        return await service.create(country)

    async def edit(self, request: Request, pk, data: Dict):
        await self.validate(request, data)
        data['_current_user_id'] = request.state.user.email if request.state.user else None
        service = CountryService(CountryRepository(request.state.session))
        return await service.update(pk, data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        service = CountryService(CountryRepository(request.state.session))
        count = 0
        for pk in pks:
            deleted = await service.delete(pk)
            if deleted:
                count += 1
        return count
