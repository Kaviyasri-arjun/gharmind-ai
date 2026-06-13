"""
GHARMIND AI — Household Event Log Model
Immutable audit log for all significant household events.
"""
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class HouseholdEventLog(Base):
    """
    Immutable audit log of all significant household events.
    Used for pattern learning and debugging.
    Production table is PARTITIONED BY RANGE (event_date) — handled in migration.
    """

    __tablename__ = "household_event_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # examples: twin.state_change, routine.started, prediction.generated, agent.called

    event_source: Mapped[str] = mapped_column(String(50), nullable=False)
    # values: twin_engine, context_agent, prediction_agent, user, system

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    ist_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # event_date is a generated column in PostgreSQL (for partitioning)
    # It's not mapped here to avoid SQLAlchemy conflicts with generated columns
    # The partitioned table is created manually in the migration.

    def __repr__(self) -> str:
        return (
            f"<HouseholdEventLog {self.event_type!r} "
            f"source={self.event_source} at={self.ist_timestamp}>"
        )
