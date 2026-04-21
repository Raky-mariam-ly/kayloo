import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import User, current_active_user, require_role
from core.db import get_db
from models.lead import Lead
from models.task import Task

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def dashboard_overview(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """CRM overview: lead counts by status, task stats."""
    # Leads by status
    lead_stats = await session.execute(
        select(Lead.status, func.count(Lead.id).label("count"))
        .group_by(Lead.status)
    )
    leads = {row.status: row.count for row in lead_stats.all()}

    total_leads = sum(leads.values())
    won = leads.get("won", 0)
    conversion_rate = round((won / total_leads * 100), 1) if total_leads > 0 else 0

    # Tasks stats for current user
    task_stats = await session.execute(
        select(Task.status, func.count(Task.id).label("count"))
        .filter(Task.assigned_to == user.id)
        .group_by(Task.status)
    )
    tasks = {row.status: row.count for row in task_stats.all()}

    overdue = await session.execute(
        select(func.count(Task.id))
        .filter(
            Task.assigned_to == user.id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < func.now(),
        )
    )

    return {
        "leads": {
            "by_status": leads,
            "total": total_leads,
            "conversion_rate": conversion_rate,
        },
        "tasks": {
            "by_status": tasks,
            "overdue": overdue.scalar_one(),
        },
    }


@router.get("/pipeline")
async def dashboard_pipeline(
    agency_id: uuid.UUID | None = None,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Lead pipeline funnel."""
    query = select(
        Lead.status,
        func.count(Lead.id).label("count"),
    )
    if agency_id:
        query = query.filter(Lead.agency_id == agency_id)
    query = query.group_by(Lead.status)
    result = await session.execute(query)

    pipeline_order = ["new", "contacted", "qualified", "negotiation", "won", "lost"]
    stats = {row.status: row.count for row in result.all()}
    return [{"status": s, "count": stats.get(s, 0)} for s in pipeline_order]


@router.get("/agent-performance")
async def agent_performance(
    user: User = Depends(require_role("admin", "superadmin")),
    session: AsyncSession = Depends(get_db),
):
    """Performance stats per agent."""
    from models.agent import Agent
    from core.auth import User as UserModel

    result = await session.execute(
        select(
            Agent.id.label("agent_id"),
            UserModel.first_name,
            UserModel.last_name,
            func.count(Lead.id).label("total_leads"),
            func.count(Lead.id).filter(Lead.status == "won").label("won_leads"),
        )
        .outerjoin(Lead, Lead.agent_id == Agent.id)
        .join(UserModel, Agent.user_id == UserModel.id)
        .group_by(Agent.id, UserModel.first_name, UserModel.last_name)
    )
    rows = result.all()
    return [
        {
            "agent_id": str(row.agent_id),
            "name": f"{row.first_name} {row.last_name}",
            "total_leads": row.total_leads,
            "won_leads": row.won_leads,
            "conversion_rate": round((row.won_leads / row.total_leads * 100), 1) if row.total_leads > 0 else 0,
        }
        for row in rows
    ]
