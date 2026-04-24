from starlette.requests import Request
from starlette.responses import Response
from starlette_admin import CustomView
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CrmDashboardView(CustomView):
    def __init__(self):
        super().__init__(
            path="/crm-dashboard",
            label="Tableau de bord",
            icon="fa fa-chart-bar",
            template_path="crm/dashboard.html",
            add_to_menu=True,
        )

    async def render(self, request: Request, templates) -> Response:
        from models.lead import Lead
        from models.contact import Contact
        from models.task import Task
        from models.activity import Activity
        from models.notification import Notification
        from models.conversation import Conversation
        from models.agent import Agent
        from core.agency_scope import get_user_agency_id

        session: AsyncSession = request.state.session
        user = getattr(request.state, "user", None)

        # Resolve agency — block if not linked
        agency_id = await get_user_agency_id(session, user) if user else None
        if not agency_id:
            return templates.TemplateResponse(
                request,
                self.template_path,
                {"title": "CRM — Accès refusé", "no_agency": True},
            )

        # All queries scoped to agency
        agency_filter = Lead.agency_id == agency_id

        # Lead pipeline stats
        lead_stats_result = await session.execute(
            select(Lead.status, func.count(Lead.id).label("count"))
            .filter(agency_filter)
            .group_by(Lead.status)
        )
        lead_stats = {row.status: row.count for row in lead_stats_result.all()}
        total_leads = sum(lead_stats.values())
        won = lead_stats.get("won", 0)
        lost = lead_stats.get("lost", 0)
        conversion_rate = round((won / total_leads * 100),
                                1) if total_leads > 0 else 0

        # Lead sources
        source_result = await session.execute(
            select(Lead.source, func.count(Lead.id).label("count"))
            .filter(agency_filter)
            .group_by(Lead.source)
        )
        lead_sources = [{"source": r.source, "count": r.count}
                        for r in source_result.all()]

        # Contacts count (contacts linked to agency leads)
        contact_subq = Contact.id.in_(
            select(Lead.contact_id).filter(agency_filter)
        )
        contact_count = await session.execute(
            select(func.count(Contact.id)).filter(contact_subq)
        )
        total_contacts = contact_count.scalar_one()

        # Tasks stats (tasks linked to agency leads)
        task_subq = Task.lead_id.in_(
            select(Lead.id).filter(agency_filter)
        )
        task_stats_result = await session.execute(
            select(Task.status, func.count(Task.id).label("count"))
            .filter(task_subq)
            .group_by(Task.status)
        )
        task_stats = {row.status: row.count for row in task_stats_result.all()}

        overdue_result = await session.execute(
            select(func.count(Task.id)).filter(
                task_subq,
                Task.status.in_(["pending", "in_progress"]),
                Task.due_date < func.now(),
            )
        )
        overdue_tasks = overdue_result.scalar_one()

        # Recent activities (linked to agency leads)
        activity_subq = Activity.lead_id.in_(
            select(Lead.id).filter(agency_filter)
        )
        recent_activities_result = await session.execute(
            select(Activity)
            .filter(activity_subq)
            .order_by(Activity.created_at.desc())
            .limit(10)
        )
        recent_activities = recent_activities_result.scalars().all()

        # Unread notifications (for agency users)
        agent_users_subq = Notification.user_id.in_(
            select(Agent.user_id).filter(Agent.agency_id == agency_id)
        )
        notif_result = await session.execute(
            select(func.count(Notification.id)).filter(
                agent_users_subq, Notification.is_read == False
            )
        )
        unread_notifications = notif_result.scalar_one()

        # Active conversations (linked to agency leads)
        conv_subq = Conversation.lead_id.in_(
            select(Lead.id).filter(agency_filter)
        )
        conv_result = await session.execute(
            select(func.count(Conversation.id)).filter(
                conv_subq, Conversation.is_archived == False
            )
        )
        active_conversations = conv_result.scalar_one()

        # Recent leads
        recent_leads_result = await session.execute(
            select(Lead).filter(agency_filter)
            .order_by(Lead.created_at.desc()).limit(5)
        )
        recent_leads = recent_leads_result.scalars().all()

        # Pipeline order for chart
        pipeline_order = ["new", "contacted",
                          "qualified", "negotiation", "won", "lost"]
        pipeline_data = [lead_stats.get(s, 0) for s in pipeline_order]

        return templates.TemplateResponse(
            request,
            self.template_path,
            {
                "title": "CRM — Tableau de bord",
                # KPIs
                "total_leads": total_leads,
                "total_contacts": total_contacts,
                "conversion_rate": conversion_rate,
                "won_leads": won,
                "lost_leads": lost,
                "overdue_tasks": overdue_tasks,
                "unread_notifications": unread_notifications,
                "active_conversations": active_conversations,
                # Charts
                "lead_stats": lead_stats,
                "pipeline_order": pipeline_order,
                "pipeline_data": pipeline_data,
                "lead_sources": lead_sources,
                "task_stats": task_stats,
                # Lists
                "recent_activities": recent_activities,
                "recent_leads": recent_leads,
            },
        )
