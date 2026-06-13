"""
GHARMIND AI — Cultural Intelligence Engine
Manages Indian festival calendar, seasonal context, and cultural pattern modifiers.
This is the knowledge layer that makes GHARMIND culturally aware.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.models.calendar import FestivalCalendar, HouseholdCalendarEvent

logger = get_logger(__name__)

IST = ZoneInfo("Asia/Kolkata")

# ── Season definitions (Indian agricultural calendar) ─────────────────

SEASON_MAP: dict[tuple[int, int], str] = {
    (3, 5): "summer",        # March–May: hot season
    (6, 9): "monsoon",       # June–September: rainy season
    (10, 11): "post_monsoon", # October–November: retreating monsoon
    (12, 2): "winter",       # December–February: cold season
}

# ── Phase-of-day classification (Indian household rhythms) ─────────────

PHASE_OF_DAY_MAP: list[tuple[int, int, str]] = [
    (4, 6, "brahma_muhurta"),   # 4:00–6:00 Early rising, spiritual
    (6, 8, "early_morning"),    # 6:00–8:00 Pooja, motor, school prep
    (8, 10, "morning_rush"),    # 8:00–10:00 Commute, school departure
    (10, 12, "late_morning"),   # 10:00–12:00 WFH, mid-morning tasks
    (12, 14, "midday"),         # 12:00–14:00 Lunch, afternoon quiet
    (14, 16, "afternoon"),      # 14:00–16:00 Rest, school return
    (16, 17, "chai_time"),      # 16:00–17:30 Chai, snacks, social
    (17, 20, "evening"),        # 17:30–19:30 Tuition, play, errands
    (20, 21, "dinner_time"),    # 19:30–21:00 Dinner prep, family
    (21, 23, "night"),          # 21:00–23:00 Wind down, study, TV
    (23, 28, "late_night"),     # 23:00–4:00 Sleep
]

# ── Festival behavior impact models ────────────────────────────────────

FESTIVAL_BEHAVIOR_MODELS: dict[str, dict[str, Any]] = {
    "diwali": {
        "prep_days": 5,
        "morning_shift_hours": -1.0,
        "pooja_duration_multiplier": 2.5,
        "cleaning_cycles_extra": 3,
        "water_usage_multiplier": 1.4,
        "power_usage_multiplier": 1.6,
        "sleep_shift_hours": -1.5,
        "shopping_trips": 4,
        "guest_probability": 0.85,
        "confidence_boost": 1.15,
    },
    "ganesh_chaturthi": {
        "prep_days": 3,
        "morning_shift_hours": -0.75,
        "pooja_duration_multiplier": 3.0,
        "water_usage_multiplier": 1.3,
        "noise_level": "festive",
        "confidence_boost": 1.10,
    },
    "navratri": {
        "prep_days": 2,
        "evening_shift_hours": 2.0,
        "sleep_shift_hours": -2.0,
        "fasting_members_possible": True,
        "confidence_boost": 1.10,
    },
    "eid": {
        "prep_days": 2,
        "cooking_sessions_extra": 4,
        "guest_probability": 0.90,
        "water_usage_multiplier": 1.3,
        "confidence_boost": 1.10,
    },
    "holi": {
        "prep_days": 1,
        "water_usage_multiplier": 3.0,
        "morning_shift_hours": -1.0,
        "outdoor_activity": True,
        "confidence_boost": 1.20,
    },
    "christmas": {
        "prep_days": 3,
        "cooking_sessions_extra": 2,
        "guest_probability": 0.60,
        "confidence_boost": 1.05,
    },
    "default": {
        "water_usage_multiplier": 1.0,
        "power_usage_multiplier": 1.0,
        "confidence_boost": 1.0,
    },
}

# ── City power cut patterns ─────────────────────────────────────────────

CITY_POWER_PATTERNS: dict[str, list[dict[str, Any]]] = {
    "pune": [
        {"day": "mon", "start_hour": 19, "start_min": 30, "duration_mins": 60, "probability": 0.75},
        {"day": "tue", "start_hour": 19, "start_min": 30, "duration_mins": 60, "probability": 0.70},
        {"day": "fri", "start_hour": 19, "start_min": 30, "duration_mins": 90, "probability": 0.79},
    ],
    "mumbai": [
        {"day": "wed", "start_hour": 14, "start_min": 0, "duration_mins": 90, "probability": 0.40},
    ],
    "delhi": [
        {"day": "thu", "start_hour": 15, "start_min": 0, "duration_mins": 60, "probability": 0.50},
    ],
    "bengaluru": [
        {"day": "sat", "start_hour": 10, "start_min": 0, "duration_mins": 120, "probability": 0.55},
    ],
    "default": [],
}

# ── City water supply windows ───────────────────────────────────────────

CITY_WATER_SUPPLY: dict[str, list[dict[str, Any]]] = {
    "pune": [{"start": "06:00", "duration_mins": 45, "city_type": "metro"}],
    "mumbai": [{"start": "06:00", "duration_mins": 60, "city_type": "metro"}],
    "delhi": [{"start": "07:00", "duration_mins": 45, "city_type": "metro"}],
    "bengaluru": [{"start": "06:30", "duration_mins": 30, "city_type": "metro"}],
    "default": [{"start": "06:00", "duration_mins": 30, "city_type": "tier2"}],
}


class CulturalIntelligenceEngine:
    """
    Provides cultural context enrichment for the GHARMIND AI system.
    Knows about festivals, seasons, power cut patterns, and household cultural rhythms.
    """

    def get_current_season(self, month: int) -> str:
        """Determine the Indian agricultural season for a given month."""
        for (start, end), season in SEASON_MAP.items():
            if start <= end:
                if start <= month <= end:
                    return season
            else:  # Wraps around year (Dec–Feb)
                if month >= start or month <= end:
                    return season
        return "post_monsoon"

    def get_phase_of_day(self, hour: int) -> str:
        """Classify the time of day using Indian household rhythm phases."""
        # Handle late night wrapping (23:00-04:00)
        h = hour if hour >= 4 else hour + 24
        for (start, end, phase) in PHASE_OF_DAY_MAP:
            if start <= h < end:
                return phase
        return "late_night"

    def get_festival_multiplier(
        self, festival_names: list[str]
    ) -> dict[str, float]:
        """
        Get behavioral multipliers for active festivals.
        Returns the highest-impact festival's multipliers.
        """
        if not festival_names:
            return FESTIVAL_BEHAVIOR_MODELS["default"]

        # Find the festival model with highest impact
        best_model = FESTIVAL_BEHAVIOR_MODELS["default"]
        for name in festival_names:
            key = name.lower().replace(" ", "_").split("_")[0]
            model = FESTIVAL_BEHAVIOR_MODELS.get(key)
            if model and model.get("confidence_boost", 1.0) > best_model.get("confidence_boost", 1.0):
                best_model = model

        return best_model

    def get_power_cut_risk(
        self, city: str, day_of_week: str, hour: int
    ) -> dict[str, Any]:
        """
        Calculate power cut risk for a city/time combination.
        Returns probability and expected duration.
        """
        city_key = city.lower()
        patterns = CITY_POWER_PATTERNS.get(city_key, CITY_POWER_PATTERNS["default"])

        day_short = day_of_week[:3].lower()
        for pattern in patterns:
            if pattern["day"] == day_short:
                cut_hour = pattern["start_hour"]
                # Check if we're within 2 hours of expected cut
                if abs(hour - cut_hour) <= 2:
                    return {
                        "risk_level": "high" if pattern["probability"] > 0.7 else "medium",
                        "probability": pattern["probability"],
                        "expected_start": f"{pattern['start_hour']:02d}:{pattern['start_min']:02d}",
                        "expected_duration_mins": pattern["duration_mins"],
                    }

        return {"risk_level": "low", "probability": 0.1, "expected_start": None}

    def get_water_supply_window(self, city: str) -> dict[str, Any]:
        """Get the municipal water supply window for a city."""
        city_key = city.lower()
        supply = CITY_WATER_SUPPLY.get(city_key, CITY_WATER_SUPPLY["default"])
        return supply[0] if supply else CITY_WATER_SUPPLY["default"][0]

    async def get_active_festivals(
        self,
        db: AsyncSession,
        target_date: date,
        city: str,
        state: str,
    ) -> list[dict[str, Any]]:
        """
        Query the festival calendar for festivals active on target_date.
        Includes prep window (days before) and celebration window.
        """
        result = await db.execute(select(FestivalCalendar))
        all_festivals = result.scalars().all()

        active: list[dict[str, Any]] = []
        for festival in all_festivals:
            if not festival.gregorian_date:
                continue

            fest_date = festival.gregorian_date
            prep_start = fest_date - timedelta(days=festival.prep_days_before)
            celebration_end = fest_date + timedelta(days=festival.celebration_days - 1)

            if prep_start <= target_date <= celebration_end:
                # Check regional relevance
                region = festival.region or []
                if "all_india" in region or state.lower() in [r.lower() for r in region]:
                    days_to = (fest_date - target_date).days
                    active.append({
                        "festival_name": festival.festival_name,
                        "festival_type": festival.festival_type,
                        "days_to_main": days_to,
                        "phase": "preparation" if days_to > 0 else "celebration",
                        "household_impact": festival.household_impact,
                        "is_public_holiday": festival.is_public_holiday,
                        "is_school_holiday": festival.is_school_holiday,
                    })

        return active

    async def get_household_events(
        self,
        db: AsyncSession,
        household_id: str,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[dict[str, Any]]:
        """Get household-specific calendar events in the given window."""
        from uuid import UUID
        result = await db.execute(
            select(HouseholdCalendarEvent).where(
                HouseholdCalendarEvent.household_id == UUID(household_id),
                HouseholdCalendarEvent.start_at >= from_dt,
                HouseholdCalendarEvent.start_at <= to_dt,
            )
        )
        events = result.scalars().all()
        return [
            {
                "event_name": e.event_name,
                "event_type": e.event_type,
                "start_at": e.start_at.isoformat(),
                "end_at": e.end_at.isoformat() if e.end_at else None,
                "impact_tags": e.impact_tags or [],
            }
            for e in events
        ]

    def calculate_urgency_score(
        self,
        overdue_routines: int,
        critical_appliance_alerts: int,
        tank_level_pct: float,
        power_available: bool,
        festivals_days_away: list[int],
        imminent_events_count: int,
    ) -> int:
        """
        Calculate household urgency score (0-100).
        Higher = more immediate attention required.
        """
        score = 0

        # Overdue routines
        score += min(overdue_routines * 15, 45)

        # Critical appliance issues
        score += min(critical_appliance_alerts * 10, 30)

        # Water tank level
        if tank_level_pct < 20:
            score += 20
        elif tank_level_pct < 40:
            score += 10

        # Power availability
        if not power_available:
            score += 25

        # Festival pressure (closer = more pressure)
        for days_away in festivals_days_away:
            if days_away <= 1:
                score += 15
            elif days_away <= 3:
                score += 8
            elif days_away <= 5:
                score += 4

        # Imminent events (< 30 min)
        score += min(imminent_events_count * 8, 24)

        return min(score, 100)

    def get_seasonal_routine_modifier(
        self, season: str, routine_type: str
    ) -> dict[str, Any]:
        """
        Get seasonal modifiers for a routine type.
        Returns timing adjustments and confidence factors.
        """
        modifiers: dict[str, dict[str, Any]] = {
            "summer": {
                "motor": {"start_time_shift_mins": -30, "duration_multiplier": 1.2},
                "ac": {"frequency_multiplier": 3.0},
                "geyser": {"skip_if_temp_above_c": 30},
            },
            "monsoon": {
                "motor": {"start_time_shift_mins": 0, "duration_multiplier": 0.8, "note": "Rain supplements supply"},
                "laundry": {"prefer_morning": True, "avoid_evening": True},
            },
            "winter": {
                "geyser": {"start_time_shift_mins": -15, "duration_multiplier": 1.3},
                "morning_pooja": {"start_time_shift_mins": 15, "note": "Cold mornings"},
            },
        }
        season_mods = modifiers.get(season, {})
        return season_mods.get(routine_type, {})


# ── Singleton instance ─────────────────────────────────────────────────
cultural_engine = CulturalIntelligenceEngine()
