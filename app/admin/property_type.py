from typing import Any, Dict

from fastapi import Request
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import BooleanField, StringField, TextAreaField, DateTimeField
from admin.base import AdminModelView


class PropertyTypeView(AdminModelView):
    fields = [
        StringField("code", required=True),
        StringField("label", required=True),
        TextAreaField("description"),
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
        if data["code"] is None or len(data["code"]) < 2:
            errors["code"] = "Ensure code has at least 02 characters"
        if data["label"] is None or len(data["label"]) < 5:
            errors["label"] = "Ensure label has at least 05 characters"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    # async def count(
    #     self,
    #     request: Request,
    #     where: Union[Dict[str, Any], str, None] = None,
    # ) -> int:
    #     session = request.state.session
    #     service = PropertyTypeService(session)
    #     return await service.count(where)

    # async def find_all(
    #     self,
    #     request: Request,
    #     skip: int = 0,
    #     limit: int = 100,
    #     where: Union[Dict[str, Any], str, None] = None,
    #     order_by: Optional[List[str]] = None,
    # ) -> List[PropertyType]:
    #     service = PropertyTypeService(request.state.session)
    #     data: List[PropertyType] = await service.find(skip=skip, limit=limit, where=where, order_by=order_by)
    #     print(
    #         f"PropertyTypeView.find_all: Found {len(data)} entities, data: {data}")
    #     return data

    # async def find_by_pk(self, request: Request, pk):
    #     service = PropertyTypeService(request.state.session)
    #     return await service.get(pk)

    # async def find_by_pks(self, request: Request, pks):
    #     service = PropertyTypeService(request.state.session)
    #     results = []
    #     for pk in pks:
    #         result = await service.get(pk)
    #         if result:
    #             results.append(result)
    #     return results

    # async def create(self, request: Request, data: Dict):
    #     await self.validate_data(data)
    #     service = PropertyTypeService(request.state.session)
    #     return await service.create(PropertyType(**data))

    # async def edit(self, request: Request, pk, data: Dict):
    #     await self.validate_data(data)
    #     service = PropertyTypeService(request.state.session)
    #     return await service.update(pk, PropertyType(**data))

    # async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
    #     service = PropertyTypeService(request.state.session)
    #     count = 0
    #     for pk in pks:
    #         deleted = await service.delete(pk)
    #         if deleted:
    #             count += 1
    #     return count
