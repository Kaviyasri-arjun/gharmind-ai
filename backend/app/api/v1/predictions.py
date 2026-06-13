"""
GHARMIND AI — Predictions API Endpoints
Prediction feed, timeline, detail, feedback, and refresh.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, select, update

from app.dependencies import AuthUser, DBSession
from app.models.prediction import Prediction
from app.services.household_service import household_service
from app.services.prediction_engine import prediction_engine
from app.services.twin_service import twin_service

router = APIRouter(prefix="/households/{household_id}/predictions", tags=["Predictions"])


class PredictionFeedbackRequest(BaseModel):
    feedback: str  # helpful | not_helpful | wrong
    note: str | None = None


@router.get("")
async def get_predictions(
    household_id: str,
    db: DBSession,
    user: AuthUser,
    horizon: str = Query(default="2h", pattern="^(30min|2h|today|week)$"),
    priority: str = Query(default="all", pattern="^(critical|high|all)$"),
    limit: int = Query(default=10, le=50),
) -> dict[str, Any]:
    """
    Get the current prediction feed.
    Returns ranked, enriched predictions for the household.
    """
    # Get latest twin state
    twin_state = await twin_service.advance_tick(db, household_id)
    household = await household_service.get_household(db, household_id)

    # Build member summary
    members = await household_service.list_members(db, household_id)
    member_summary = ", ".join(
        f"{m.name} ({m.role})" for m in members
    )

    # Generate fresh predictions
    predictions = await prediction_engine.generate_predictions(
        db=db,
        household_id=household_id,
        twin_state=twin_state,
        household_name=household.name,
        city=household.city,
        state_name=household.state,
        language=household.language_preference,
    )

    # Apply filters
    if priority != "all":
        predictions = [p for p in predictions if p.get("priority") == priority]

    predictions = predictions[:limit]

    critical_count = sum(1 for p in predictions if p.get("priority") == "critical")
    high_count = sum(1 for p in predictions if p.get("priority") == "high")

    return {
        "household_id": household_id,
        "generated_at": twin_state.get("snapshot_at"),
        "horizon": horizon,
        "predictions": predictions,
        "summary": {
            "critical_count": critical_count,
            "high_count": high_count,
            "normal_count": len(predictions) - critical_count - high_count,
            "total": len(predictions),
        },
    }


@router.post("/refresh")
async def refresh_predictions(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Force regenerate predictions now."""
    twin_state = await twin_service.advance_tick(db, household_id)
    household = await household_service.get_household(db, household_id)

    predictions = await prediction_engine.generate_predictions(
        db=db,
        household_id=household_id,
        twin_state=twin_state,
        household_name=household.name,
        city=household.city,
        state_name=household.state,
        language=household.language_preference,
    )

    return {
        "refreshed": True,
        "count": len(predictions),
        "critical": sum(1 for p in predictions if p.get("priority") == "critical"),
    }


@router.post("/{prediction_id}/feedback")
async def submit_feedback(
    household_id: str,
    prediction_id: str,
    body: PredictionFeedbackRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Submit feedback on a prediction (helpful / not_helpful / wrong)."""
    if body.feedback not in ("helpful", "not_helpful", "wrong"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="feedback must be: helpful, not_helpful, or wrong",
        )

    result = await db.execute(
        select(Prediction).where(
            Prediction.id == UUID(prediction_id),
            Prediction.household_id == UUID(household_id),
        )
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction.user_feedback = body.feedback
    prediction.status = "confirmed" if body.feedback == "helpful" else "dismissed"
    await db.flush()

    return {"success": True, "feedback": body.feedback}
