from typing import Any, Dict, List, Optional
from uuid import UUID

from models.lead import Lead
from repositories.lead import LeadRepository
from services.base import BaseService


VALID_STATUSES = {"new", "contacted", "qualified", "negotiation", "won", "lost"}
VALID_TRANSITIONS = {
    "new": {"contacted", "lost"},
    "contacted": {"qualified", "lost"},
    "qualified": {"negotiation", "lost"},
    "negotiation": {"won", "lost"},
    "won": set(),
    "lost": {"new"},  # allow re-opening
}

# Default probability when entering a pipeline stage
DEFAULT_PROBABILITY = {
    "new": 10,
    "contacted": 25,
    "qualified": 50,
    "negotiation": 75,
    "won": 100,
    "lost": 0,
}


class LeadService(BaseService[Lead]):
    def __init__(self, repository: LeadRepository):
        super().__init__(repository)

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Lead]:
        return await self.repository.list_by_status(status, skip, limit)

    async def list_by_agent(self, agent_id: UUID, skip: int = 0, limit: int = 100) -> List[Lead]:
        return await self.repository.list_by_agent(agent_id, skip, limit)

    async def list_by_agency(self, agency_id: UUID, skip: int = 0, limit: int = 100) -> List[Lead]:
        return await self.repository.list_by_agency(agency_id, skip, limit)

    async def list_by_contact(self, contact_id: UUID, skip: int = 0, limit: int = 100) -> List[Lead]:
        return await self.repository.list_by_contact(contact_id, skip, limit)

    async def transition_status(self, lead_id: UUID, new_status: str) -> Optional[Lead]:
        """Transition lead to a new pipeline status, enforcing valid transitions."""
        lead = await self.repository.get(lead_id)
        if not lead:
            return None
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        allowed = VALID_TRANSITIONS.get(lead.status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot transition from '{lead.status}' to '{new_status}'")
        updates: Dict[str, Any] = {
            "status": new_status,
            "probability": DEFAULT_PROBABILITY.get(new_status, lead.probability),
        }
        return await self.repository.update(lead_id, updates)

    async def assign_agent(self, lead_id: UUID, agent_id: UUID) -> Optional[Lead]:
        return await self.repository.update(lead_id, {"agent_id": agent_id})

    async def count_by_status(self) -> List[Dict[str, Any]]:
        return await self.repository.count_by_status()

    async def pipeline_stats(self, agency_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        return await self.repository.pipeline_stats(agency_id)
