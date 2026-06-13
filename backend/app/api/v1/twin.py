"""
GHARMIND AI — Digital Twin API Endpoints
Real-time household state, snapshots, and resource status.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import desc, select

from app.dependencies import AuthUser, DBSession
from app.models.twin import TwinStateSnapshot
from app.services.twin_service import twin_service

router = APIRouter(prefix="/households/{household_id}/twin", tags=["Digital Twin"])


@router.get("/state")
async def get_twin_state(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """
    Get the current household Digital Twin state.
    Advances the twin by one tick before returning.
    """
    state = await twin_service.advance_tick(db, household_id)
    if not state:
        return {"error": "Twin not initialized", "household_id": household_id}
    return state


@router.get("/history")
async def get_twin_history(
    household_id: str,
    db: DBSession,
    user: AuthUser,
    limit: int = Query(default=24, le=288),
) -> dict[str, Any]:
    """Get recent twin state snapshots (default: last 24 snapshots)."""
    result = await db.execute(
        select(TwinStateSnapshot)
        .where(TwinStateSnapshot.household_id == UUID(household_id))
        .order_by(desc(TwinStateSnapshot.snapshot_at))
        .limit(limit)
    )
    snapshots = result.scalars().all()

    return {
        "household_id": household_id,
        "total": len(snapshots),
        "snapshots": [
            {
                "id": str(s.id),
                "snapshot_at": s.snapshot_at.isoformat(),
                "context_summary": s.context_summary,
                "season": s.season,
                "power_available": s.power_available,
                "water_available": s.water_available,
            }
            for s in snapshots
        ],
    }


@router.get("/resources")
async def get_resources(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Get current resource status (water/power/internet)."""
    snapshot = await twin_service.get_latest_snapshot(db, household_id)
    if not snapshot:
        return {
            "power": {"available": True, "quality": "unknown"},
            "water": {"available": True, "tank_level_pct": 50},
            "internet": {"available": True},
        }

    return {
        "household_id": household_id,
        "as_of": snapshot.snapshot_at.isoformat(),
        "power": {
            "available": snapshot.power_available,
            "quality": "stable" if snapshot.power_available else "cut",
        },
        "water": {
            "available": snapshot.water_available,
        },
        "internet": {
            "available": snapshot.internet_available,
        },
    }
