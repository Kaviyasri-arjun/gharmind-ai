"""
GHARMIND AI — What-If Simulator API Endpoints
Run simulations, list scenarios, and retrieve results.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select

from app.dependencies import AuthUser, DBSession
from app.models.prediction import SimulationRun
from app.services.household_service import household_service
from app.services.twin_service import twin_service
from app.services.whatif_simulator import whatif_simulator

router = APIRouter(
    prefix="/households/{household_id}/simulator", tags=["What-If Simulator"]
)

IST = ZoneInfo("Asia/Kolkata")


class Perturbation(BaseModel):
    type: str = Field(..., examples=["power_cut"])
    params: dict[str, Any] = {}


class RunSimulationRequest(BaseModel):
    scenario_name: str = Field(..., max_length=200)
    hypothesis: str = Field(..., description="What are you testing?")
    perturbations: list[Perturbation] = Field(..., min_length=1)
    sim_start: datetime | None = None  # Defaults to now
    sim_duration_hours: int = Field(default=6, ge=1, le=48)


# ── Built-in scenario templates ────────────────────────────────────────

SCENARIO_TEMPLATES = [
    {
        "id": "s001",
        "name": "Power Cut During Dinner",
        "description": "MSEDCL load shedding starts at 7:30pm",
        "icon": "⚡",
        "perturbation_types": ["power_cut"],
        "default_params": {
            "type": "power_cut",
            "params": {"start_time_offset_hours": 1, "duration_hours": 1.5},
        },
    },
    {
        "id": "s002",
        "name": "Water Motor Failure",
        "description": "Motor fails on a hot summer morning",
        "icon": "💧",
        "perturbation_types": ["motor_failure"],
        "default_params": {
            "type": "motor_failure",
            "params": {"failure_type": "mechanical"},
        },
    },
    {
        "id": "s003",
        "name": "Unexpected Guests",
        "description": "8 people arrive unannounced at 4pm",
        "icon": "👥",
        "perturbation_types": ["unexpected_guest"],
        "default_params": {
            "type": "unexpected_guest",
            "params": {"count": 8, "arrival_time": "16:00", "duration_hours": 4},
        },
    },
    {
        "id": "s004",
        "name": "Exam Week Mode",
        "description": "Competitive exam starts tomorrow",
        "icon": "📚",
        "perturbation_types": ["exam_week"],
        "default_params": {
            "type": "exam_week",
            "params": {"exam_type": "JEE", "duration_days": 5},
        },
    },
    {
        "id": "s005",
        "name": "Festival Tomorrow",
        "description": "Major festival preparation kicks in",
        "icon": "🪔",
        "perturbation_types": ["festival_tomorrow"],
        "default_params": {
            "type": "festival_tomorrow",
            "params": {"festival_name": "diwali"},
        },
    },
    {
        "id": "s006",
        "name": "Internet Outage",
        "description": "ISP failure during WFH day",
        "icon": "📡",
        "perturbation_types": ["internet_outage"],
        "default_params": {
            "type": "internet_outage",
            "params": {"duration_hours": 3},
        },
    },
]


@router.get("/scenarios")
async def list_scenarios(
    household_id: str,
    user: AuthUser,
) -> dict[str, Any]:
    """List all built-in What-If scenario templates."""
    return {"scenarios": SCENARIO_TEMPLATES}


@router.post("/run")
async def run_simulation(
    household_id: str,
    body: RunSimulationRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Run a What-If simulation."""
    sim_start = body.sim_start or datetime.now(IST)

    # Get baseline state
    baseline_state = await twin_service.advance_tick(db, household_id)
    household = await household_service.get_household(db, household_id)
    members = await household_service.list_members(db, household_id)
    member_summary = ", ".join(f"{m.name} ({m.role})" for m in members)

    result = await whatif_simulator.run_simulation(
        db=db,
        household_id=household_id,
        scenario_name=body.scenario_name,
        hypothesis=body.hypothesis,
        perturbations=[p.model_dump() for p in body.perturbations],
        sim_start=sim_start,
        sim_duration_hours=body.sim_duration_hours,
        baseline_state=baseline_state,
        household_name=household.name,
        city=household.city,
        member_summary=member_summary,
        language=household.language_preference,
    )

    return result


@router.get("/runs")
async def list_simulation_runs(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """List past simulation runs for this household."""
    result = await db.execute(
        select(SimulationRun)
        .where(SimulationRun.household_id == UUID(household_id))
        .order_by(desc(SimulationRun.run_at))
        .limit(20)
    )
    runs = result.scalars().all()

    return {
        "total": len(runs),
        "runs": [
            {
                "id": str(r.id),
                "scenario_name": r.scenario_name,
                "status": r.status,
                "run_at": r.run_at.isoformat(),
                "overall_severity": r.impact_analysis.get("overall_severity")
                if r.impact_analysis
                else None,
            }
            for r in runs
        ],
    }


@router.get("/runs/{run_id}")
async def get_simulation_result(
    household_id: str,
    run_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Get the full result of a simulation run."""
    result = await db.execute(
        select(SimulationRun).where(
            SimulationRun.id == UUID(run_id),
            SimulationRun.household_id == UUID(household_id),
        )
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")

    return {
        "run_id": str(run.id),
        "scenario_name": run.scenario_name,
        "hypothesis": run.hypothesis,
        "status": run.status,
        "result_summary": run.result_summary,
        "impact_analysis": run.impact_analysis,
        "risk_flags": run.risk_flags,
        "recommendations": run.recommendations,
        "run_at": run.run_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }
