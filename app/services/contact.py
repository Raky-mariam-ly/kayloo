from typing import List, Optional
from uuid import UUID

from models.contact import Contact
from repositories.contact import ContactRepository
from services.base import BaseService


class ContactService(BaseService[Contact]):
    def __init__(self, repository: ContactRepository):
        super().__init__(repository)

    async def get_by_email(self, email: str) -> Optional[Contact]:
        return await self.repository.get_by_email(email)

    async def get_by_user_id(self, user_id: UUID) -> Optional[Contact]:
        return await self.repository.get_by_user_id(user_id)

    async def list_by_type(self, contact_type: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        return await self.repository.list_by_type(contact_type, skip, limit)

    async def search(self, term: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        return await self.repository.search(term, skip, limit)

    async def get_or_create_from_inquiry(self, first_name: str, last_name: str, email: str,
                                          phone_number: str = None, user_id: UUID = None) -> Contact:
        """Get existing contact by email or create a new one."""
        existing = await self.repository.get_by_email(email) if email else None
        if existing:
            return existing
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            user_id=user_id,
            contact_type="buyer",
        )
        return await self.repository.create(contact)
