"""
GHARMIND AI — Routines API Endpoints
CRUD for household routines and execution history.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select

from app.dependencies import AuthUser, DBSession
from app.models.routine import Routine, RoutineExecution

router = APIRouter(prefix="/households/{household_id}/routines", tags=["Routines"])
IST = ZoneInfo("Asia/Kolkata")


class CreateRoutineRequest(BaseModel):
    name: str = Field(..., max_length=200)
    routine_type: str
    recurrence: str = "daily"
    description: str | None = None
    schedule_expression: dict[str, Any] | None = None
    primary_member_id: str | None = None
    is_active: bool = True


@router.get("")
async def list_routines(
    household_id: str,
    db: DBSession,
    user: AuthUser,
    active_only: bool = Query(default=True),
) -> dict[str, Any]:
    """List all household routines."""
    query = select(Routine).where(Routine.household_id == UUID(household_id))
    if active_only:
        query = query.where(Routine.is_active.is_(True))

    result = await db.execute(query.order_by(Routine.name))
    routines = result.scalars().all()

    return {
        "total": len(routines),
        "routines": [
            {
                "id": str(r.id),
                "name": r.name,
                "routine_type": r.routine_type,
                "recurrence": r.recurrence,
                "is_active": r.is_active,
                "is_ai_detected": r.is_ai_detected,
                "confidence_score": float(r.confidence_score) if r.confidence_score else None,
                "next_expected_at": r.next_expected_at.isoformat() if r.next_expected_at else None,
                "last_executed_at": r.last_executed_at.isoformat() if r.last_executed_at else None,
                "execution_count": r.execution_count,
            }
            for r in routines
        ],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_routine(
    household_id: str,
    body: CreateRoutineRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Create a new household routine."""
    routine = Routine(
        household_id=UUID(household_id),
        name=body.name,
        routine_type=body.routine_type,
        recurrence=body.recurrence,
        description=body.description,
        schedule_expression=body.schedule_expression,
        primary_member_id=UUID(body.primary_member_id) if body.primary_member_id else None,
        is_active=body.is_active,
        is_ai_detected=False,
    )
    db.add(routine)
    await db.flush()

    return {
        "id": str(routine.id),
        "name": routine.name,
        "routine_type": routine.routine_type,
        "recurrence": routine.recurrence,
        "is_active": routine.is_active,
    }


@router.get("/upcoming")
async def get_upcoming_routines(
    household_id: str,
    db: DBSession,
    user: AuthUser,
    hours: int = Query(default=24, le=168),
) -> dict[str, Any]:
    """Get routines expected in the next N hours."""
    now = datetime.now(IST)
    horizon = now + timedelta(hours=hours)

    result = await db.execute(
        select(Routine).where(
            Routine.household_id == UUID(household_id),
            Routine.is_active.is_(True),
            Routine.next_expected_at.between(now, horizon),
        ).order_by(Routine.next_expected_at)
    )
    routines = result.scalars().all()

    return {
        "horizon_hours": hours,
        "upcoming": [
            {
                "id": str(r.id),
                "name": r.name,
                "routine_type": r.routine_type,
                "expected_at": r.next_expected_at.isoformat() if r.next_expected_at else None,
                "confidence": float(r.confidence_score) if r.confidence_score else 0.7,
            }
            for r in routines
        ],
    }


@router.delete("/{routine_id}")
async def delete_routine(
    household_id: str,
    routine_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Deactivate (soft-delete) a routine."""
    result = await db.execute(
        select(Routine).where(
            Routine.id == UUID(routine_id),
            Routine.household_id == UUID(household_id),
        )
    )
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    routine.is_active = False
    await db.flush()
    return {"deleted": True, "routine_id": routine_id}
