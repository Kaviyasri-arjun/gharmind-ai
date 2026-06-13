"""
GHARMIND AI — Prediction, HouseholdMemory, SimulationRun Models
AI-generated predictions, semantic memory store, and What-If runs.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Prediction(Base):
    """
    AI-generated prediction about an upcoming household event.
    Includes confidence score, evidence trail, and Claude reasoning.
    """

    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── What is predicted ───────────────────────────────────────────
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: routine_start, routine_overdue, appliance_action, member_arrival,
    #        member_departure, festival_prep, power_event, water_event, meal_time

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_suggestion: Mapped[str | None] = mapped_column(Text)

    # ── Timing ──────────────────────────────────────────────────────
    predicted_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # prediction_window is an interval, stored as text for portability
    prediction_window_mins: Mapped[int] = mapped_column(SmallInteger, server_default="30")

    # ── Confidence & priority ────────────────────────────────────────
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), server_default="'normal'")
    # values: low, normal, high, critical
    category: Mapped[str | None] = mapped_column(String(50))
    # values: water, power, routine, family, festival

    # ── Context trail ───────────────────────────────────────────────
    context_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("twin_state_snapshots.id", ondelete="SET NULL"),
    )
    reasoning: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    linked_routine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="SET NULL"),
    )

    # ── Outcome tracking ────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(30), server_default="'pending'")
    # values: pending, confirmed, dismissed, expired

    was_accurate: Mapped[bool | None] = mapped_column(Boolean)
    actual_occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_feedback: Mapped[str | None] = mapped_column(String(20))
    # values: helpful, not_helpful, wrong

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="predictions")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Prediction {self.title!r} conf={self.confidence_score} priority={self.priority}>"


class HouseholdMemory(Base, TimestampMixin):
    """
    Long-term semantic memory for the household AI.
    Stored as pgvector embeddings (1536 dimensions via Titan).
    Used for: routine pattern recall, preference memory, festival behavior.
    """

    __tablename__ = "household_memories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: routine_pattern, preference, exception, festival_behavior, seasonal_pattern

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # pgvector embedding stored as text, cast to vector(1536) in queries
    embedding_text: Mapped[str | None] = mapped_column(
        "embedding", Text, nullable=True
    )

    # ── Temporal validity ───────────────────────────────────────────
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_seasons: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    valid_months: Mapped[list[int] | None] = mapped_column(ARRAY(SmallInteger))
    recurrence: Mapped[str | None] = mapped_column(String(50))

    # ── Confidence ──────────────────────────────────────────────────
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default="1.00")
    importance_score: Mapped[int] = mapped_column(SmallInteger, server_default="50")
    observation_count: Mapped[int] = mapped_column(Integer, server_default="1")

    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="memories")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<HouseholdMemory {self.title!r} type={self.memory_type}>"


class SimulationRun(Base):
    """
    A What-If simulation run with full timeline and impact analysis.
    """

    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_by_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("family_members.id", ondelete="SET NULL"),
    )
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Scenario ────────────────────────────────────────────────────
    scenario_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scenario_type: Mapped[str | None] = mapped_column(String(50))
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    perturbations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # ── Parameters ──────────────────────────────────────────────────
    sim_start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sim_duration_hours: Mapped[int] = mapped_column(SmallInteger, server_default="24")
    sim_resolution_mins: Mapped[int] = mapped_column(SmallInteger, server_default="15")

    # ── Results ─────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(30), server_default="'running'")
    # values: running, complete, failed

    result_summary: Mapped[str | None] = mapped_column(Text)
    impact_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    risk_flags: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    timeline: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="simulation_runs")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<SimulationRun {self.scenario_name!r} status={self.status}>"
