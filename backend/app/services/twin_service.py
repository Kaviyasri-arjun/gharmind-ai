"""
GHARMIND AI — Household Digital Twin Service
Manages the twin state machine: member locations, appliance states,
water/power models, and 1-minute tick cycle.
This is the simulation engine — no IoT hardware required.
"""
from __future__ import annotations

import math
import random
from copy import deepcopy
from datetime import datetime, time, timedelta
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.models.household import FamilyMember, Household
from app.models.routine import Routine
from app.models.twin import Appliance, Room, TwinStateSnapshot
from app.services.cultural_intelligence import CulturalIntelligenceEngine, cultural_engine

logger = get_logger(__name__)

IST = ZoneInfo("Asia/Kolkata")


# ── Occupancy probability models per member role ───────────────────────

OCCUPANCY_MODELS: dict[str, dict[str, dict[str, float]]] = {
    "parent_f": {  # Mother/homemaker
        "04:00-06:00": {"pooja_room": 0.7, "bedroom": 0.3},
        "06:00-07:30": {"kitchen": 0.65, "pooja_room": 0.25, "bedroom": 0.10},
        "07:30-09:00": {"kitchen": 0.50, "living_room": 0.30, "balcony": 0.20},
        "09:00-12:00": {"kitchen": 0.40, "living_room": 0.35, "bedroom": 0.25},
        "12:00-14:00": {"kitchen": 0.80, "living_room": 0.20},
        "14:00-16:00": {"bedroom": 0.60, "living_room": 0.40},
        "16:00-17:30": {"kitchen": 0.70, "living_room": 0.30},
        "17:30-20:00": {"kitchen": 0.50, "living_room": 0.30, "study": 0.20},
        "20:00-22:00": {"living_room": 0.60, "kitchen": 0.30, "bedroom": 0.10},
        "22:00-04:00": {"bedroom": 0.98, "bathroom": 0.02},
    },
    "parent_m": {  # Father (WFH)
        "04:00-07:00": {"bedroom": 0.95, "bathroom": 0.05},
        "07:00-09:00": {"bedroom": 0.50, "bathroom": 0.30, "kitchen": 0.20},
        "09:00-18:00": {"study": 0.60, "bedroom": 0.20, "living_room": 0.20},
        "18:00-20:00": {"living_room": 0.50, "study": 0.30, "kitchen": 0.20},
        "20:00-22:00": {"living_room": 0.70, "bedroom": 0.30},
        "22:00-04:00": {"bedroom": 0.97, "bathroom": 0.03},
    },
    "child": {  # School student
        "04:00-06:30": {"bedroom": 0.97, "bathroom": 0.03},
        "06:30-07:15": {"bathroom": 0.40, "bedroom": 0.40, "kitchen": 0.20},
        "07:15-14:30": {},  # At school
        "14:30-17:00": {"bedroom": 0.40, "living_room": 0.40, "study": 0.20},
        "17:00-22:00": {"study": 0.55, "living_room": 0.30, "bedroom": 0.15},
        "22:00-04:00": {"bedroom": 0.98, "bathroom": 0.02},
    },
    "grandparent": {
        "04:00-06:30": {"bedroom": 0.30, "pooja_room": 0.60, "living_room": 0.10},
        "06:30-10:00": {"living_room": 0.40, "balcony": 0.35, "kitchen": 0.25},
        "10:00-12:00": {"living_room": 0.50, "balcony": 0.30, "bedroom": 0.20},
        "12:00-15:00": {"bedroom": 0.80, "living_room": 0.20},
        "15:00-20:00": {"living_room": 0.50, "balcony": 0.30, "pooja_room": 0.20},
        "20:00-04:00": {"bedroom": 0.96, "bathroom": 0.04},
    },
}


def _get_member_model_key(role: str, gender: str | None = None) -> str:
    if role == "parent":
        return "parent_f" if gender in ("female", "f") else "parent_m"
    if role == "child":
        return "child"
    if role == "grandparent":
        return "grandparent"
    return "parent_f"  # default


def _get_room_distribution(model_key: str, hour: int) -> dict[str, float]:
    """Get room probability distribution for a member at a given hour."""
    model = OCCUPANCY_MODELS.get(model_key, OCCUPANCY_MODELS["parent_f"])
    for time_range, distribution in model.items():
        start_h, end_h = (int(x.split(":")[0]) for x in time_range.split("-"))
        if start_h <= hour < end_h:
            return distribution
    return {"bedroom": 1.0}


def _sample_room(distribution: dict[str, float]) -> str | None:
    """Sample a room from a probability distribution. Returns None if empty (e.g., at school)."""
    if not distribution:
        return None  # Away from home
    r = random.random()
    cumulative = 0.0
    for room, prob in distribution.items():
        cumulative += prob
        if r <= cumulative:
            return room
    return list(distribution.keys())[-1]


class TwinService:
    """
    Manages the Household Digital Twin lifecycle.
    Provides: tick advancement, state snapshots, appliance transitions,
    member location simulation, and resource modeling.
    """

    def __init__(self, cultural: CulturalIntelligenceEngine) -> None:
        self.cultural = cultural

    async def get_household(
        self, db: AsyncSession, household_id: str
    ) -> Household | None:
        """Load a household with all its members, rooms, and appliances."""
        result = await db.execute(
            select(Household).where(
                Household.id == UUID(household_id),
                Household.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def advance_tick(
        self, db: AsyncSession, household_id: str
    ) -> dict[str, Any]:
        """
        Advance the Digital Twin by one 1-minute tick.
        Updates: time context, member locations, appliance states,
        resource levels, routine triggers, anomaly detection.
        Returns the new twin state dict.
        """
        ist_now = datetime.now(IST)

        # Load household data
        household = await self.get_household(db, household_id)
        if not household:
            logger.warning("twin_tick_no_household", household_id=household_id)
            return {}

        # Load members
        members_result = await db.execute(
            select(FamilyMember).where(
                FamilyMember.household_id == UUID(household_id)
            )
        )
        members = members_result.scalars().all()

        # Load rooms
        rooms_result = await db.execute(
            select(Room).where(Room.household_id == UUID(household_id))
        )
        rooms = rooms_result.scalars().all()

        # Load appliances
        appliances_result = await db.execute(
            select(Appliance).where(Appliance.household_id == UUID(household_id))
        )
        appliances = appliances_result.scalars().all()

        # Load active routines
        routines_result = await db.execute(
            select(Routine).where(
                Routine.household_id == UUID(household_id),
                Routine.is_active.is_(True),
            )
        )
        routines = routines_result.scalars().all()

        # ── Build state ──────────────────────────────────────────────
        hour = ist_now.hour
        season = self.cultural.get_current_season(ist_now.month)
        phase = self.cultural.get_phase_of_day(hour)
        day_name = ist_now.strftime("%A")

        # Simulate member locations
        member_states: dict[str, Any] = {}
        room_occupancy: dict[str, list[str]] = {str(r.id): [] for r in rooms}

        for member in members:
            model_key = _get_member_model_key(member.role, member.gender)
            distribution = _get_room_distribution(model_key, hour)
            room_name = _sample_room(distribution)

            # Map room name to room ID
            room_id = None
            if room_name:
                for r in rooms:
                    if room_name.lower().replace("_", " ") in r.name.lower() or \
                       r.room_type.lower() == room_name.lower().replace(" ", "_"):
                        room_id = str(r.id)
                        break

            activity = self._infer_activity(model_key, hour, room_name)
            status = "home" if room_name else "away"

            member_states[str(member.id)] = {
                "name": member.name,
                "location": room_name or "away",
                "room_id": room_id,
                "activity": activity,
                "status": status,
            }

            if room_id and status == "home":
                room_occupancy[room_id].append(str(member.id))

            # Update simulated_location in DB
            await db.execute(
                update(FamilyMember)
                .where(FamilyMember.id == member.id)
                .values(simulated_location=room_name)
            )

        # Simulate appliance states
        appliance_states: dict[str, Any] = {}
        for appliance in appliances:
            state = self._simulate_appliance_state(appliance, ist_now, season)
            appliance_states[str(appliance.id)] = state

            # Update DB state
            await db.execute(
                update(Appliance)
                .where(Appliance.id == appliance.id)
                .values(
                    power_state=state["state"],
                    power_watts=state.get("watts"),
                )
            )

        # Simulate resources
        water_state = self._simulate_water(appliances, ist_now, household.city)
        power_state = self._simulate_power(household.city, day_name, hour)

        # Update room occupancy in DB
        for room in rooms:
            occupants = room_occupancy.get(str(room.id), [])
            await db.execute(
                update(Room)
                .where(Room.id == room.id)
                .values(
                    is_occupied=len(occupants) > 0,
                    occupants=occupants,
                )
            )

        # Build rooms state
        rooms_state: dict[str, Any] = {}
        for room in rooms:
            occ = room_occupancy.get(str(room.id), [])
            rooms_state[str(room.id)] = {
                "name": room.name,
                "type": room.room_type,
                "occupied": len(occ) > 0,
                "occupants": occ,
                "lighting": "on" if occ else "off",
            }

        # Check overdue routines
        overdue_routines = self._check_overdue_routines(routines, ist_now)

        # Compute urgency
        urgency = self.cultural.calculate_urgency_score(
            overdue_routines=len(overdue_routines),
            critical_appliance_alerts=sum(
                1 for a in appliances
                if a.is_critical and appliance_states.get(str(a.id), {}).get("alert")
            ),
            tank_level_pct=water_state["tank_level_pct"],
            power_available=power_state["available"],
            festivals_days_away=[],
            imminent_events_count=0,
        )

        # Build context summary
        context_summary = self._build_context_summary(
            phase, season, urgency, overdue_routines, water_state, power_state
        )

        twin_state: dict[str, Any] = {
            "household_id": household_id,
            "snapshot_at": ist_now.isoformat(),
            "temporal": {
                "ist_time": ist_now.strftime("%H:%M:%S"),
                "date": ist_now.date().isoformat(),
                "day_of_week": day_name,
                "week_number": ist_now.isocalendar()[1],
                "month": ist_now.month,
                "season": season,
                "phase_of_day": phase,
                "is_school_day": ist_now.weekday() < 5,
            },
            "members": member_states,
            "rooms": rooms_state,
            "appliances": appliance_states,
            "resources": {
                "power": power_state,
                "water": water_state,
                "internet": {"available": True},
            },
            "overdue_routines": overdue_routines,
            "urgency_score": urgency,
            "context_summary": context_summary,
        }

        # Persist snapshot
        await self._save_snapshot(db, twin_state, household_id, ist_now)
        await db.commit()

        logger.debug(
            "twin_tick_complete",
            household_id=household_id,
            phase=phase,
            urgency=urgency,
        )
        return twin_state

    def _infer_activity(self, model_key: str, hour: int, room: str | None) -> str:
        """Infer the current activity based on model, time, and location."""
        if room is None:
            return "away_from_home"
        activity_map = {
            ("pooja_room", range(4, 8)): "morning_aarti",
            ("kitchen", range(5, 8)): "breakfast_preparation",
            ("kitchen", range(11, 14)): "lunch_preparation",
            ("kitchen", range(18, 21)): "dinner_preparation",
            ("bedroom", range(22, 28)): "sleeping",
            ("bedroom", range(13, 16)): "afternoon_rest",
            ("study", range(17, 23)): "studying",
            ("living_room", range(20, 23)): "family_time",
            ("balcony", range(6, 10)): "morning_walk_tea",
        }
        for (target_room, hour_range), activity in activity_map.items():
            if target_room in (room or "").lower() and hour in hour_range:
                return activity
        return "general_activity"

    def _simulate_appliance_state(
        self, appliance: Any, now: datetime, season: str
    ) -> dict[str, Any]:
        """Simulate appliance state based on schedule and current time."""
        state: dict[str, Any] = {
            "name": appliance.name,
            "type": appliance.appliance_type,
            "state": appliance.power_state or "off",
            "watts": appliance.power_watts,
            "alert": None,
        }

        schedule = appliance.auto_schedule or {}
        on_time = schedule.get("on")

        if on_time and appliance.appliance_type in ("motor", "geyser"):
            on_hour, on_min = (int(x) for x in on_time.split(":"))
            current_mins = now.hour * 60 + now.minute
            scheduled_mins = on_hour * 60 + on_min
            overdue_mins = current_mins - scheduled_mins

            if appliance.appliance_type == "motor":
                if overdue_mins > 10 and appliance.power_state == "off":
                    state["alert"] = f"OVERDUE {overdue_mins} MINUTES"
                    state["alert_severity"] = "critical" if overdue_mins > 20 else "high"
                elif overdue_mins > 0 and appliance.power_state == "off":
                    state["alert"] = "DUE NOW"
                    state["alert_severity"] = "high"

            if appliance.appliance_type == "geyser":
                auto_off = schedule.get("auto_off_after_mins", 20)
                if appliance.last_on_at:
                    running_mins = (now - appliance.last_on_at.replace(tzinfo=IST)).total_seconds() / 60
                    if running_mins > auto_off and appliance.power_state == "on":
                        state["state"] = "on"  # Should auto-off
                        state["alert"] = "RUNNING LONG — SHOULD AUTO-OFF"

        # Always-on appliances
        if appliance.appliance_type in ("fridge", "wifi"):
            state["state"] = "on"

        return state

    def _simulate_water(
        self, appliances: list[Any], now: datetime, city: str
    ) -> dict[str, Any]:
        """Simulate water tank level and supply status."""
        supply = cultural_engine.get_water_supply_window(city)
        supply_hour = int(supply["start"].split(":")[0])
        supply_end = supply_hour + supply["duration_mins"] // 60

        in_supply_window = supply_hour <= now.hour < supply_end

        # Simple tank model: drains 450L/day at ~0.31L/min
        # If motor is running or in supply window, tank fills
        motor_running = any(
            a.appliance_type == "motor" and a.power_state == "on" for a in appliances
        )

        # Base tank level (simplified — real engine uses persistent state)
        base_level = 60.0
        hour_factor = (now.hour * 60 + now.minute) / 1440  # fraction of day
        drained = hour_factor * 40  # drains 40% over the day
        tank_level = max(10.0, base_level - drained + (15.0 if motor_running else 0))

        alert = None
        if tank_level < 20:
            alert = "CRITICAL — Tank below 20%"
        elif tank_level < 40:
            alert = "LOW — Run motor soon"

        return {
            "available": True,
            "tank_level_pct": round(tank_level, 1),
            "motor_running": motor_running,
            "supply_active": in_supply_window,
            "alert": alert,
        }

    def _simulate_power(
        self, city: str, day_name: str, hour: int
    ) -> dict[str, Any]:
        """Simulate power grid status based on city cut patterns."""
        risk = cultural_engine.get_power_cut_risk(city, day_name, hour)
        return {
            "available": True,  # Assume available; cut events trigger via anomaly
            "quality": "stable",
            "cut_risk": risk["risk_level"],
            "cut_probability": risk["probability"],
            "cut_prediction": risk.get("expected_start"),
        }

    def _check_overdue_routines(
        self, routines: list[Any], now: datetime
    ) -> list[dict[str, Any]]:
        """Find routines that should have started but haven't."""
        overdue = []
        for routine in routines:
            if not routine.next_expected_at:
                continue
            expected = routine.next_expected_at
            if hasattr(expected, "tzinfo") and expected.tzinfo is None:
                expected = expected.replace(tzinfo=IST)
            overdue_mins = (now - expected).total_seconds() / 60
            if 10 < overdue_mins < 120:  # Overdue 10–120 min
                overdue.append({
                    "routine_id": str(routine.id),
                    "name": routine.name,
                    "overdue_mins": int(overdue_mins),
                    "expected_at": expected.isoformat(),
                })
        return overdue

    def _build_context_summary(
        self,
        phase: str,
        season: str,
        urgency: int,
        overdue: list[dict[str, Any]],
        water: dict[str, Any],
        power: dict[str, Any],
    ) -> str:
        """Generate a one-line context summary."""
        parts: list[str] = [f"{phase.replace('_', ' ').title()} • {season.replace('_', ' ').title()}"]
        if urgency > 60:
            parts.append(f"Urgency {urgency}/100")
        if water.get("alert"):
            parts.append(water["alert"])
        if power.get("cut_prediction"):
            parts.append(f"Power cut risk at {power['cut_prediction']}")
        if overdue:
            parts.append(f"{len(overdue)} routine(s) overdue")
        return " • ".join(parts)

    async def _save_snapshot(
        self,
        db: AsyncSession,
        state: dict[str, Any],
        household_id: str,
        now: datetime,
    ) -> None:
        """Persist a twin state snapshot to the database."""
        snapshot = TwinStateSnapshot(
            household_id=UUID(household_id),
            snapshot_at=now,
            ist_time=now.time(),
            day_of_week=now.weekday(),
            week_number=now.isocalendar()[1],
            month=now.month,
            season=state["temporal"]["season"],
            festival_context=state.get("festival_context", []),
            is_holiday=not state["temporal"].get("is_school_day", True),
            rooms_state=state["rooms"],
            appliances_state=state["appliances"],
            members_state=state["members"],
            power_available=state["resources"]["power"]["available"],
            water_available=state["resources"]["water"]["available"],
            internet_available=state["resources"]["internet"]["available"],
            context_summary=state.get("context_summary"),
        )
        db.add(snapshot)

    async def get_latest_snapshot(
        self, db: AsyncSession, household_id: str
    ) -> TwinStateSnapshot | None:
        """Get the most recent twin state snapshot."""
        from sqlalchemy import desc
        result = await db.execute(
            select(TwinStateSnapshot)
            .where(TwinStateSnapshot.household_id == UUID(household_id))
            .order_by(desc(TwinStateSnapshot.snapshot_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def initialize_twin(
        self, db: AsyncSession, household_id: str
    ) -> bool:
        """
        Initialize the Digital Twin for a newly onboarded household.
        Runs a brief historical simulation to populate initial state.
        """
        logger.info("twin_initialization_start", household_id=household_id)
        try:
            # Run a single tick to create the initial snapshot
            state = await self.advance_tick(db, household_id)

            # Mark twin as initialized
            await db.execute(
                update(Household)
                .where(Household.id == UUID(household_id))
                .values(twin_initialized=True)
            )
            await db.commit()
            logger.info("twin_initialization_complete", household_id=household_id)
            return True
        except Exception as e:
            logger.error("twin_initialization_failed", household_id=household_id, error=str(e))
            return False


# ── Singleton instance ─────────────────────────────────────────────────
twin_service = TwinService(cultural_engine)
