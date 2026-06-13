"""
GHARMIND AI — Coimbatore Family Demo Seed Script
Seeds a realistic South Indian household into the database for API testing and demo.

Family: Sundaram household, R.S. Puram, Coimbatore, Tamil Nadu
- Lakshmi (Mother, 40) — Morning pooja at 6 AM, runs the household
- Venkat (Father, 44) — Office 9 AM, commutes by car
- Arjun (Son, 17) — 12th std, tuition at 6 PM, board exam tomorrow
- Paati (Grandmother, 68) — Early riser, temple visits

Key routines:
- Morning pooja 6:00 AM
- Water motor 6:15 AM (Coimbatore has 1-hour supply window at 6 AM)
- Father leaves at 9:00 AM
- Evening chai at 5:00 PM
- Tuition at 6:00 PM
- Power cut expected around 2:00 PM (TNEB pattern)
- Exam tomorrow — quiet hours enforced

Usage:
    cd backend
    python -m scripts.seed_coimbatore_demo
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

# Add parent to sys.path so 'app' is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import AsyncSessionLocal, engine, init_db_extensions
from app.models.base import Base
from app.models.calendar import FestivalCalendar, HouseholdCalendarEvent
from app.models.household import FamilyMember, Household
from app.models.prediction import HouseholdMemory, Prediction, SimulationRun
from app.models.routine import Routine, RoutineExecution
from app.models.twin import Appliance, Room, TwinStateSnapshot

IST = ZoneInfo("Asia/Kolkata")

# ═══════════════════════════════════════════════════════════════════════
# DEMO IDS (deterministic for easy API testing)
# ═══════════════════════════════════════════════════════════════════════

HOUSEHOLD_ID = "a1b2c3d4-e5f6-7890-abcd-111111111111"
MEMBER_LAKSHMI = "a1b2c3d4-e5f6-7890-abcd-222222222201"
MEMBER_VENKAT = "a1b2c3d4-e5f6-7890-abcd-222222222202"
MEMBER_ARJUN = "a1b2c3d4-e5f6-7890-abcd-222222222203"
MEMBER_PAATI = "a1b2c3d4-e5f6-7890-abcd-222222222204"

ROOM_MASTER = "a1b2c3d4-e5f6-7890-abcd-333333333301"
ROOM_ARJUN = "a1b2c3d4-e5f6-7890-abcd-333333333302"
ROOM_KITCHEN = "a1b2c3d4-e5f6-7890-abcd-333333333303"
ROOM_POOJA = "a1b2c3d4-e5f6-7890-abcd-333333333304"
ROOM_LIVING = "a1b2c3d4-e5f6-7890-abcd-333333333305"
ROOM_HALL = "a1b2c3d4-e5f6-7890-abcd-333333333306"

APPLIANCE_MOTOR = "a1b2c3d4-e5f6-7890-abcd-444444444401"
APPLIANCE_GEYSER = "a1b2c3d4-e5f6-7890-abcd-444444444402"
APPLIANCE_FRIDGE = "a1b2c3d4-e5f6-7890-abcd-444444444403"
APPLIANCE_FAN_M = "a1b2c3d4-e5f6-7890-abcd-444444444404"
APPLIANCE_WIFI = "a1b2c3d4-e5f6-7890-abcd-444444444405"
APPLIANCE_TV = "a1b2c3d4-e5f6-7890-abcd-444444444406"

ROUTINE_POOJA = "a1b2c3d4-e5f6-7890-abcd-555555555501"
ROUTINE_MOTOR = "a1b2c3d4-e5f6-7890-abcd-555555555502"
ROUTINE_CHAI = "a1b2c3d4-e5f6-7890-abcd-555555555503"
ROUTINE_TUITION = "a1b2c3d4-e5f6-7890-abcd-555555555504"
ROUTINE_OFFICE = "a1b2c3d4-e5f6-7890-abcd-555555555505"
ROUTINE_STUDY = "a1b2c3d4-e5f6-7890-abcd-555555555506"


async def drop_and_recreate_tables() -> None:
    """Drop all tables and recreate from ORM models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # Create pgvector extension before creating tables
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables recreated from ORM models")


async def seed_household(db: AsyncSession) -> None:
    """Seed the Sundaram household."""
    household = Household(
        id=UUID(HOUSEHOLD_ID),
        name="Sundaram Residence",
        owner_user_id="demo-user-001",
        city="Coimbatore",
        state="Tamil Nadu",
        pincode="641002",
        home_type="independent",
        floors=2,
        total_rooms=6,
        language_preference="hinglish",
        ai_persona_name="Gharji",
        tags=["nuclear_family", "has_students", "working_father", "exam_week"],
        onboarding_complete=True,
        twin_initialized=True,
        subscription_tier="pro",
    )
    db.add(household)
    print(f"✓ Household: {household.name} ({household.city})")


async def seed_members(db: AsyncSession) -> None:
    """Seed family members."""
    members = [
        FamilyMember(
            id=UUID(MEMBER_LAKSHMI),
            household_id=UUID(HOUSEHOLD_ID),
            name="Lakshmi",
            nickname="Amma",
            role="parent",
            age=40,
            gender="female",
            typical_wake_time=time(5, 30),
            typical_sleep_time=time(22, 0),
            is_primary_contact=True,
            receives_alerts=True,
            phone_number="+91-98420-12345",
            work_schedule={"type": "none"},
            preferences={
                "chai_time": "17:00",
                "quiet_hours": ["22:00", "05:30"],
                "language": "hinglish",
            },
            simulated_location="kitchen",
        ),
        FamilyMember(
            id=UUID(MEMBER_VENKAT),
            household_id=UUID(HOUSEHOLD_ID),
            name="Venkat",
            nickname="Appa",
            role="parent",
            age=44,
            gender="male",
            typical_wake_time=time(6, 30),
            typical_sleep_time=time(22, 30),
            is_primary_contact=False,
            receives_alerts=True,
            phone_number="+91-98420-67890",
            work_schedule={
                "type": "office",
                "days": ["mon", "tue", "wed", "thu", "fri"],
                "start": "09:00",
                "end": "18:00",
                "commute_mins": 35,
            },
            preferences={"language": "en"},
            simulated_location="master_bedroom",
        ),
        FamilyMember(
            id=UUID(MEMBER_ARJUN),
            household_id=UUID(HOUSEHOLD_ID),
            name="Arjun",
            nickname="Arjun",
            role="child",
            age=17,
            gender="male",
            typical_wake_time=time(6, 0),
            typical_sleep_time=time(23, 0),
            is_primary_contact=False,
            receives_alerts=False,
            school_schedule={
                "school_name": "PSG ICSE School",
                "bus_time": "08:00",
                "return_time": "15:30",
                "has_tuition": True,
            },
            preferences={
                "study_hours": ["18:00", "22:00"],
                "language": "en",
            },
            simulated_location="arjun_room",
        ),
        FamilyMember(
            id=UUID(MEMBER_PAATI),
            household_id=UUID(HOUSEHOLD_ID),
            name="Paati",
            nickname="Paati",
            role="grandparent",
            age=68,
            gender="female",
            typical_wake_time=time(4, 30),
            typical_sleep_time=time(21, 0),
            is_primary_contact=False,
            receives_alerts=False,
            preferences={"language": "hi", "temple_visit_days": ["tue", "fri"]},
            simulated_location="pooja_room",
        ),
    ]
    db.add_all(members)
    for m in members:
        print(f"  ✓ Member: {m.name} ({m.role}, {m.age}y)")


async def seed_rooms(db: AsyncSession) -> None:
    """Seed rooms."""
    rooms = [
        Room(id=UUID(ROOM_MASTER), household_id=UUID(HOUSEHOLD_ID),
             name="Master Bedroom", room_type="bedroom", floor=1,
             position_x=Decimal("10"), position_y=Decimal("10")),
        Room(id=UUID(ROOM_ARJUN), household_id=UUID(HOUSEHOLD_ID),
             name="Arjun's Room", room_type="bedroom", floor=1,
             position_x=Decimal("60"), position_y=Decimal("10")),
        Room(id=UUID(ROOM_KITCHEN), household_id=UUID(HOUSEHOLD_ID),
             name="Kitchen", room_type="kitchen", floor=0,
             position_x=Decimal("60"), position_y=Decimal("60")),
        Room(id=UUID(ROOM_POOJA), household_id=UUID(HOUSEHOLD_ID),
             name="Pooja Room", room_type="pooja_room", floor=0,
             position_x=Decimal("85"), position_y=Decimal("10")),
        Room(id=UUID(ROOM_LIVING), household_id=UUID(HOUSEHOLD_ID),
             name="Living Room", room_type="living_room", floor=0,
             position_x=Decimal("10"), position_y=Decimal("60")),
        Room(id=UUID(ROOM_HALL), household_id=UUID(HOUSEHOLD_ID),
             name="Hall", room_type="living_room", floor=0,
             position_x=Decimal("35"), position_y=Decimal("35")),
    ]
    db.add_all(rooms)
    print(f"  ✓ Rooms: {len(rooms)} created")


async def seed_appliances(db: AsyncSession) -> None:
    """Seed appliances."""
    appliances = [
        Appliance(id=UUID(APPLIANCE_MOTOR), household_id=UUID(HOUSEHOLD_ID),
                  name="Water Motor", appliance_type="motor", is_critical=True,
                  auto_schedule={"on": "06:15", "days": ["*"], "auto_off_after_mins": 25},
                  health_score=82),
        Appliance(id=UUID(APPLIANCE_GEYSER), household_id=UUID(HOUSEHOLD_ID),
                  room_id=UUID(ROOM_MASTER), name="Geyser", appliance_type="geyser",
                  auto_schedule={"on": "06:00", "days": ["*"], "auto_off_after_mins": 15},
                  health_score=90),
        Appliance(id=UUID(APPLIANCE_FRIDGE), household_id=UUID(HOUSEHOLD_ID),
                  room_id=UUID(ROOM_KITCHEN), name="Fridge", appliance_type="fridge",
                  is_critical=True, power_state="on", health_score=88),
        Appliance(id=UUID(APPLIANCE_FAN_M), household_id=UUID(HOUSEHOLD_ID),
                  room_id=UUID(ROOM_MASTER), name="Ceiling Fan (Master)",
                  appliance_type="fan", health_score=95),
        Appliance(id=UUID(APPLIANCE_WIFI), household_id=UUID(HOUSEHOLD_ID),
                  name="WiFi Router", appliance_type="wifi", is_critical=True,
                  power_state="on", health_score=97),
        Appliance(id=UUID(APPLIANCE_TV), household_id=UUID(HOUSEHOLD_ID),
                  room_id=UUID(ROOM_LIVING), name="TV (Living)", appliance_type="tv",
                  health_score=100),
    ]
    db.add_all(appliances)
    print(f"  ✓ Appliances: {len(appliances)} created")


async def seed_routines(db: AsyncSession) -> None:
    """Seed household routines."""
    now = datetime.now(IST)
    today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)

    routines = [
        Routine(
            id=UUID(ROUTINE_POOJA), household_id=UUID(HOUSEHOLD_ID),
            name="Morning Pooja", routine_type="pooja", recurrence="daily",
            description="Lakshmi and Paati do morning pooja with agarbatti and vilakku",
            schedule_expression={"days": ["*"], "time": "06:00", "duration_mins": 30},
            primary_member_id=UUID(MEMBER_LAKSHMI),
            confidence_score=Decimal("0.97"), is_active=True,
            next_expected_at=today_6am + timedelta(days=1),
            last_executed_at=today_6am,
            execution_count=340,
        ),
        Routine(
            id=UUID(ROUTINE_MOTOR), household_id=UUID(HOUSEHOLD_ID),
            name="Water Motor", routine_type="motor", recurrence="daily",
            description="Tank fill from CMWSSB supply (6 AM window, 45 min)",
            schedule_expression={"days": ["*"], "time": "06:15", "duration_mins": 25,
                                 "conditional": "tank_level < 60%"},
            appliance_ids=[APPLIANCE_MOTOR],
            confidence_score=Decimal("0.99"), is_active=True,
            next_expected_at=today_6am.replace(minute=15) + timedelta(days=1),
            last_executed_at=today_6am.replace(minute=15),
            execution_count=350,
        ),
        Routine(
            id=UUID(ROUTINE_OFFICE), household_id=UUID(HOUSEHOLD_ID),
            name="Venkat Office Departure", routine_type="commute", recurrence="weekly",
            description="Venkat leaves for office at 9 AM, drives to Tidel Park",
            schedule_expression={"days": ["mon", "tue", "wed", "thu", "fri"],
                                 "time": "09:00", "duration_mins": 35},
            primary_member_id=UUID(MEMBER_VENKAT),
            confidence_score=Decimal("0.94"), is_active=True,
            next_expected_at=today_6am.replace(hour=9) + timedelta(days=1),
            execution_count=220,
        ),
        Routine(
            id=UUID(ROUTINE_CHAI), household_id=UUID(HOUSEHOLD_ID),
            name="Evening Filter Coffee / Chai", routine_type="chai", recurrence="daily",
            description="5 PM family chai/coffee time — Coimbatore style filter kaapi",
            schedule_expression={"days": ["*"], "time": "17:00", "duration_mins": 20},
            primary_member_id=UUID(MEMBER_LAKSHMI),
            confidence_score=Decimal("0.92"), is_active=True,
            next_expected_at=today_6am.replace(hour=17),
            execution_count=300,
        ),
        Routine(
            id=UUID(ROUTINE_TUITION), household_id=UUID(HOUSEHOLD_ID),
            name="Arjun Tuition Class", routine_type="tuition", recurrence="weekly",
            description="Physics/Maths tuition at Vinayaka Academy, R.S. Puram",
            schedule_expression={"days": ["mon", "wed", "thu", "fri"],
                                 "time": "18:00", "duration_mins": 90},
            primary_member_id=UUID(MEMBER_ARJUN),
            confidence_score=Decimal("0.88"), is_active=True,
            next_expected_at=today_6am.replace(hour=18),
            execution_count=160,
        ),
        Routine(
            id=UUID(ROUTINE_STUDY), household_id=UUID(HOUSEHOLD_ID),
            name="Arjun Night Study", routine_type="study", recurrence="daily",
            description="Board exam prep — quiet hours enforced",
            schedule_expression={"days": ["*"], "time": "20:00", "duration_mins": 120},
            primary_member_id=UUID(MEMBER_ARJUN),
            confidence_score=Decimal("0.85"), is_active=True,
            next_expected_at=today_6am.replace(hour=20),
            execution_count=90,
        ),
    ]
    db.add_all(routines)
    print(f"  ✓ Routines: {len(routines)} created")


async def seed_predictions(db: AsyncSession) -> None:
    """Seed sample predictions for demo."""
    now = datetime.now(IST)

    predictions = [
        Prediction(
            household_id=UUID(HOUSEHOLD_ID),
            prediction_type="appliance_action",
            title="💧 Water Motor — Run at 6:15 AM",
            description="CMWSSB supply window starts at 6 AM. Tank at 42%. Motor should start at 6:15.",
            action_suggestion="Motor 6:15 ku chalao — tank 42% irukku, school ku paani venum.",
            predicted_for=now.replace(hour=6, minute=15) + timedelta(days=1),
            confidence_score=Decimal("0.96"),
            priority="critical",
            category="water",
            reasoning="Historical: motor ran at 06:15 on 14/14 weekdays. Tank below 45%. School day tomorrow.",
            evidence={"points": [
                "14 consecutive weekday motor runs at 06:10-06:20",
                "Tank at 42% (threshold: 60%)",
                "CMWSSB supply: 06:00-06:45 window",
            ]},
            status="pending",
            expires_at=now.replace(hour=7) + timedelta(days=1),
        ),
        Prediction(
            household_id=UUID(HOUSEHOLD_ID),
            prediction_type="power_event",
            title="⚡ TNEB Power Cut Expected — 2:00 PM",
            description="TNEB scheduled load shedding for this zone. Thursday pattern: 2-3pm cut.",
            action_suggestion="2 PM power cut — devices charge pannu, UPS check pannu. Arjun laptop charge.",
            predicted_for=now.replace(hour=14, minute=0),
            confidence_score=Decimal("0.76"),
            priority="high",
            category="power",
            reasoning="Thursday 2pm cut pattern: 5 of last 7 Thursdays. TNEB zone C2 schedule.",
            evidence={"points": [
                "TNEB zone C2: Thu 2pm pattern",
                "5/7 Thursdays confirmed",
                "Duration: 45-75 minutes typical",
            ]},
            status="pending",
            expires_at=now.replace(hour=15),
        ),
        Prediction(
            household_id=UUID(HOUSEHOLD_ID),
            prediction_type="routine_start",
            title="📚 Exam Tomorrow — Quiet Mode Required",
            description="Arjun's board exam is tomorrow. Household should enter quiet mode after 8 PM.",
            action_suggestion="Arjun exam naalaiku — TV 8 PM ku off pannu. Quiet mode from 8 PM.",
            predicted_for=now.replace(hour=20, minute=0),
            confidence_score=Decimal("0.92"),
            priority="high",
            category="study",
            reasoning="Calendar event: Board exam tomorrow. Study routine active. Noise disrupts focus.",
            evidence={"points": [
                "Calendar: 12th Board Exam (Physics) tomorrow 10 AM",
                "Study session 8-10 PM tonight is critical",
                "Last exam week: TV was off 7-10 PM every day",
            ]},
            status="pending",
            expires_at=now.replace(hour=22),
        ),
        Prediction(
            household_id=UUID(HOUSEHOLD_ID),
            prediction_type="routine_start",
            title="☕ Evening Filter Coffee — 5:00 PM",
            description="Family filter coffee time. Lakshmi will prepare by 4:50 PM.",
            action_suggestion="Coffee time 5 PM — Lakshmi already preparing. Enjoy!",
            predicted_for=now.replace(hour=17, minute=0),
            confidence_score=Decimal("0.93"),
            priority="normal",
            category="routine",
            status="pending",
            expires_at=now.replace(hour=18),
        ),
    ]
    db.add_all(predictions)
    print(f"  ✓ Predictions: {len(predictions)} created")


async def seed_calendar_events(db: AsyncSession) -> None:
    """Seed exam event and festivals."""
    now = datetime.now(IST)
    tomorrow = now + timedelta(days=1)

    events = [
        HouseholdCalendarEvent(
            household_id=UUID(HOUSEHOLD_ID),
            member_id=UUID(MEMBER_ARJUN),
            event_name="12th Board Exam — Physics",
            event_type="exam",
            start_at=tomorrow.replace(hour=10, minute=0),
            end_at=tomorrow.replace(hour=13, minute=0),
            impact_tags=["quiet_hours", "no_interruptions", "early_wake", "exam_stress"],
            description="Arjun's CBSE 12th Board Physics paper. Critical exam.",
        ),
        HouseholdCalendarEvent(
            household_id=UUID(HOUSEHOLD_ID),
            event_name="Pongal Preparation",
            event_type="guest",
            start_at=(now + timedelta(days=5)).replace(hour=8),
            end_at=(now + timedelta(days=5)).replace(hour=20),
            impact_tags=["extra_water", "extra_cooking", "festival_prep"],
            description="Pongal festival — sugarcane, new pots, kolam competition",
        ),
    ]
    db.add_all(events)
    print(f"  ✓ Calendar events: {len(events)} created")


async def seed_festivals(db: AsyncSession) -> None:
    """Seed festival calendar entries relevant to Tamil Nadu."""
    festivals = [
        FestivalCalendar(
            festival_name="Pongal",
            local_names={"ta": "பொங்கல்", "en": "Pongal", "hi": "पोंगल"},
            festival_type="hindu",
            region=["tamil_nadu", "andhra_pradesh", "karnataka"],
            gregorian_date=date(2025, 1, 14),
            household_impact={
                "preparation_days": 3,
                "peak_activity": "morning",
                "typical_routines": ["kolam", "pongal_cooking", "new_clothes"],
                "water_usage_multiplier": 1.5,
                "power_usage_multiplier": 1.2,
                "guest_probability": 0.70,
            },
            prep_days_before=3,
            celebration_days=4,
            is_public_holiday=True,
            is_school_holiday=True,
        ),
        FestivalCalendar(
            festival_name="Diwali",
            local_names={"ta": "தீபாவளி", "hi": "दीपावली", "en": "Diwali"},
            festival_type="hindu",
            region=["all_india"],
            gregorian_date=date(2025, 10, 20),
            household_impact={
                "preparation_days": 5,
                "water_usage_multiplier": 1.4,
                "power_usage_multiplier": 1.6,
                "guest_probability": 0.85,
            },
            prep_days_before=5,
            celebration_days=2,
            is_public_holiday=True,
            is_school_holiday=True,
        ),
        FestivalCalendar(
            festival_name="Navaratri",
            local_names={"ta": "நவராத்திரி", "hi": "नवरात्रि"},
            festival_type="hindu",
            region=["all_india"],
            gregorian_date=date(2025, 10, 2),
            household_impact={
                "preparation_days": 2,
                "evening_shift_hours": 2.0,
                "typical_routines": ["golu_setup", "evening_bhajan", "sundal_making"],
                "guest_probability": 0.80,
            },
            prep_days_before=2,
            celebration_days=9,
            is_public_holiday=False,
            is_school_holiday=False,
        ),
    ]
    db.add_all(festivals)
    print(f"  ✓ Festivals: {len(festivals)} seeded")


async def seed_twin_snapshot(db: AsyncSession) -> None:
    """Create a simulated twin state snapshot for the current moment."""
    now = datetime.now(IST)

    snapshot = TwinStateSnapshot(
        household_id=UUID(HOUSEHOLD_ID),
        snapshot_at=now,
        ist_time=now.time(),
        day_of_week=now.weekday(),
        week_number=now.isocalendar()[1],
        month=now.month,
        season="summer" if now.month in (3, 4, 5) else "post_monsoon",
        festival_context=[],
        is_holiday=False,
        is_exam_period=True,
        rooms_state={
            ROOM_POOJA: {"name": "Pooja Room", "occupied": True, "occupants": ["Paati"]},
            ROOM_KITCHEN: {"name": "Kitchen", "occupied": True, "occupants": ["Lakshmi"]},
            ROOM_MASTER: {"name": "Master Bedroom", "occupied": True, "occupants": ["Venkat"]},
            ROOM_ARJUN: {"name": "Arjun's Room", "occupied": True, "occupants": ["Arjun"]},
            ROOM_LIVING: {"name": "Living Room", "occupied": False, "occupants": []},
        },
        appliances_state={
            APPLIANCE_MOTOR: {"name": "Water Motor", "state": "off", "alert": "DUE IN 10 MIN"},
            APPLIANCE_GEYSER: {"name": "Geyser", "state": "on", "running_since": "06:00"},
            APPLIANCE_FRIDGE: {"name": "Fridge", "state": "on"},
            APPLIANCE_WIFI: {"name": "WiFi", "state": "on"},
            APPLIANCE_TV: {"name": "TV", "state": "off"},
        },
        members_state={
            MEMBER_LAKSHMI: {"name": "Lakshmi", "location": "kitchen", "activity": "morning_prep"},
            MEMBER_VENKAT: {"name": "Venkat", "location": "master_bedroom", "activity": "waking_up"},
            MEMBER_ARJUN: {"name": "Arjun", "location": "arjun_room", "activity": "studying"},
            MEMBER_PAATI: {"name": "Paati", "location": "pooja_room", "activity": "morning_pooja"},
        },
        power_available=True,
        water_available=True,
        internet_available=True,
        context_summary="Early morning, exam day prep. Paati doing pooja. Motor due in 10 min. Power cut expected 2 PM.",
    )
    db.add(snapshot)
    print("  ✓ Twin snapshot created for current time")


async def main() -> None:
    """Run the complete seed process."""
    print("=" * 70)
    print("  GHARMIND AI — Coimbatore Demo Data Seeder")
    print("  Household: Sundaram Residence, R.S. Puram, Coimbatore")
    print("=" * 70)
    print()

    # Recreate all tables
    await drop_and_recreate_tables()

    async with AsyncSessionLocal() as db:
        await seed_household(db)
        await seed_members(db)
        await seed_rooms(db)
        await seed_appliances(db)
        await seed_routines(db)
        await seed_predictions(db)
        await seed_calendar_events(db)
        await seed_festivals(db)
        await seed_twin_snapshot(db)
        await db.commit()

    print()
    print("=" * 70)
    print("  ✅ Seed complete!")
    print(f"  Household ID: {HOUSEHOLD_ID}")
    print("  Start backend: uvicorn app.main:app --reload")
    print("  Test: curl http://localhost:8000/v1/households/" + HOUSEHOLD_ID)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
