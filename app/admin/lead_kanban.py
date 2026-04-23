from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette_admin import CustomView
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import uuid


PIPELINE_COLUMNS = [
    {"key": "new", "label": "Nouveau", "color": "#0ca678", "bg": "#e8f4f8"},
    {"key": "contacted", "label": "Contacté", "color": "#206bc4", "bg": "#e0f0ff"},
    {"key": "qualified", "label": "Qualifié", "color": "#6654a4", "bg": "#e8e0ff"},
    {"key": "negotiation", "label": "Négociation",
        "color": "#9654a4", "bg": "#f0e0ff"},
    {"key": "won", "label": "Gagné", "color": "#2fb344", "bg": "#d2f4e8"},
    {"key": "lost", "label": "Perdu", "color": "#d63939", "bg": "#fde0e0"},
]

VALID_TRANSITIONS = {
    "new":         ["contacted"],
    "contacted":   ["qualified", "lost"],
    "qualified":   ["negotiation", "lost"],
    "negotiation": ["won", "lost"],
    "won":         [],
    "lost":        ["new"],
}

SOURCE_LABELS = {
    "website": "Site web",
    "mobile_app": "App mobile",
    "phone": "Téléphone",
    "walk_in": "Visite",
    "referral": "Recommandation",
    "social_media": "Réseaux sociaux",
}

PRIORITY_META = {
    "low": {"label": "Basse", "color": "#a0aec0"},
    "medium": {"label": "Moyenne", "color": "#f59f00"},
    "high": {"label": "Haute", "color": "#fd7e14"},
    "urgent": {"label": "Urgente", "color": "#d63939"},
}


class LeadKanbanView(CustomView):
    def __init__(self):
        super().__init__(
            path="/crm-kanban",
            label="Kanban Leads",
            icon="fa fa-columns",
            template_path="crm/lead_kanban.html",
            add_to_menu=True,
            methods=["GET", "PATCH"],
        )

    async def render(self, request: Request, templates) -> Response:
        from core.agency_scope import get_user_agency_id

        user = getattr(request.state, "user", None)
        session: AsyncSession = request.state.session
        agency_id = await get_user_agency_id(session, user) if user else None
        if not agency_id:
            return JSONResponse({"detail": "Accès refusé — aucune agence liée"}, 403)

        request.state._agency_id = agency_id

        if request.method == "PATCH":
            return await self._handle_status_update(request, agency_id)
        return await self._render_board(request, templates, agency_id)

    async def _handle_status_update(self, request: Request, agency_id) -> JSONResponse:
        from models.lead import Lead

        session: AsyncSession = request.state.session

        try:
            body = await request.json()
            lead_id = uuid.UUID(body["lead_id"])
            new_status = body["status"]
        except (KeyError, ValueError):
            return JSONResponse({"detail": "lead_id and status required"}, 400)

        result = await session.execute(
            select(Lead).filter_by(id=lead_id)
        )
        lead = result.scalars().first()
        if not lead:
            return JSONResponse({"detail": "Lead not found"}, 404)

        # Verify lead belongs to user's agency
        if lead.agency_id != agency_id:
            return JSONResponse({"detail": "Accès refusé"}, 403)

        allowed = VALID_TRANSITIONS.get(lead.status, [])
        if new_status not in allowed:
            return JSONResponse(
                {"detail": f"Transition {lead.status} → {new_status} non autorisée"},
                400,
            )

        lead.status = new_status
        await session.commit()
        return JSONResponse({"ok": True, "status": new_status})

    async def _render_board(self, request: Request, templates, agency_id) -> Response:
        from models.lead import Lead
        from models.contact import Contact
        from models.property import Property
        from models.agent import Agent
        from core.auth import User

        agent_user = User.__table__.alias("agent_user")
        session: AsyncSession = request.state.session

        result = await session.execute(
            select(
                Lead.id,
                Lead.agent_id,
                Lead.property_id,
                Lead.status,
                Lead.source,
                Lead.priority,
                Lead.probability,
                Lead.deal_value,
                Lead.expected_close,
                Lead.notes,
                Lead.created_at,
                Contact.first_name,
                Contact.last_name,
                Contact.email,
                Contact.phone_number,
                Property.label.label("property_label"),
                agent_user.c.first_name.label("agent_first_name"),
                agent_user.c.last_name.label("agent_last_name"),
            )
            .filter(Lead.agency_id == agency_id)
            .join(Contact, Lead.contact_id == Contact.id)
            .outerjoin(Property, Lead.property_id == Property.id)
            .outerjoin(Agent, Lead.agent_id == Agent.id)
            .outerjoin(agent_user, Agent.user_id == agent_user.c.id)
            .order_by(Lead.created_at.desc())
        )
        rows = result.all()

        columns_data = {col["key"]: [] for col in PIPELINE_COLUMNS}
        for row in rows:
            agent_name = ""
            if row.agent_first_name:
                agent_name = f"{row.agent_first_name} {row.agent_last_name or ''}".strip()
            card = {
                "id": str(row.id),
                "lead_url": f"/admin/lead/detail/{row.id}",
                "property_url": f"/admin/property-property/detail/{row.property_id}" if row.property_id else "",
                "agent_name": agent_name,
                "agent_url": f"/admin/agent/detail/{row.agent_id}" if row.agent_id else "",
                "contact_name": f"{row.first_name} {row.last_name}",
                "email": row.email or "",
                "phone": row.phone_number or "",
                "source": SOURCE_LABELS.get(row.source, row.source),
                "priority": row.priority,
                "priority_label": PRIORITY_META.get(row.priority, {}).get("label", row.priority),
                "priority_color": PRIORITY_META.get(row.priority, {}).get("color", "#a0aec0"),
                "probability": row.probability or 0,
                "deal_value": f"{row.deal_value:,.0f}" if row.deal_value else "",
                "expected_close": row.expected_close.strftime("%d/%m/%Y") if row.expected_close else "",
                "property_label": row.property_label or "",
                "notes": (row.notes or "")[:80],
                "created_at": row.created_at.strftime("%d/%m/%Y") if row.created_at else "",
            }
            if row.status in columns_data:
                columns_data[row.status].append(card)

        total = len(rows)
        won = len(columns_data.get("won", []))
        conversion = round(won / total * 100, 1) if total else 0

        return templates.TemplateResponse(
            request,
            self.template_path,
            {
                "title": "CRM — Kanban Leads",
                "columns": PIPELINE_COLUMNS,
                "columns_data": columns_data,
                "total_leads": total,
                "conversion_rate": conversion,
            },
        )
