# GHARMIND AI — Context Engine Design

---

## What Is Household Context?

Household context is the answer to: **"What is happening in this home, right now, and why does it matter?"**

For a smart speaker, context is just "user said X." For GHARMIND AI, context is a rich graph:
- Who is home, where are they, what are they doing
- What time/season/festival is it
- What routines just ran, are running, are upcoming
- What resources (water, power, internet) are available
- What the household's emotional/activity state is
- What has historically happened in similar situations

The Context Engine assembles all of this into a **Household Context Object (HCO)** that every other agent consumes.

---

## Context Dimensions

```
┌────────────────────────────────────────────────────────────────┐
│                 HOUSEHOLD CONTEXT DIMENSIONS                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  TEMPORAL    │  │  SPATIAL     │  │     CULTURAL          │  │
│  │              │  │              │  │                        │  │
│  │ IST time     │  │ Room states  │  │ Active festival        │  │
│  │ Day/week     │  │ Occupancy    │  │ Season                 │  │
│  │ Season       │  │ Appliances   │  │ Regional customs       │  │
│  │ Festival cal │  │ Floor plan   │  │ Fasting/celebration    │  │
│  │ Holiday flag │  │              │  │ Auspicious timing      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  BEHAVIORAL  │  │  RESOURCE    │  │     HISTORICAL        │  │
│  │              │  │              │  │                        │  │
│  │ Member locs  │  │ Power status │  │ Similar past states   │  │
│  │ Activities   │  │ Water supply │  │ Pattern frequencies   │  │
│  │ Routines     │  │ Internet     │  │ Deviations            │  │
│  │ Mood signals │  │ Fuel/gas     │  │ Preference memory     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Household Context Object (HCO) Schema

```json
{
  "context_id": "uuid-v4",
  "household_id": "uuid-v4",
  "generated_at": "2024-10-28T06:15:05+05:30",
  "valid_for_seconds": 300,

  "temporal": {
    "ist_now": "06:15:05",
    "date": "2024-10-28",
    "day_of_week": "Monday",
    "week_number": 44,
    "month": 10,
    "season": "winter_onset",
    "phase_of_day": "early_morning",
    "minutes_to_sunrise": 22,
    "is_weekday": true,
    "is_holiday": false,
    "is_school_day": true
  },

  "cultural": {
    "active_festivals": ["Diwali Prep Week"],
    "festival_phase": "preparation",
    "days_to_main_festival": 4,
    "auspicious_window": "06:00-08:00",
    "fasting_members": [],
    "cultural_mood": "festive_anticipation"
  },

  "spatial": {
    "rooms": {
      "kitchen": {"occupied": true, "occupants": ["anjali"], "activity": "cooking"},
      "pooja_room": {"occupied": true, "occupants": ["anjali"], "activity": "prayer"},
      "master_bedroom": {"occupied": true, "occupants": ["rahul"], "activity": "sleeping"},
      "bedroom_2": {"occupied": false},
      "living_room": {"occupied": false}
    },
    "appliances": {
      "water_motor": {"state": "off", "last_run": "05:45 yesterday", "overdue_mins": 15},
      "geyser": {"state": "on", "running_since": "06:05"},
      "kitchen_chimney": {"state": "on"}
    }
  },

  "behavioral": {
    "members_home": ["anjali", "rahul", "priya"],
    "members_away": ["ajay (grandfather — temple)"],
    "active_routines": ["morning_pooja", "geyser_warmup", "school_prep"],
    "imminent_routines": [
      {"name": "water_motor", "due_in_mins": 0, "overdue": true},
      {"name": "school_bus", "due_in_mins": 60},
      {"name": "breakfast_prep", "due_in_mins": 20}
    ],
    "household_activity_level": "moderate_rising"
  },

  "resources": {
    "power": {"available": true, "quality": "stable", "cut_risk_score": 0.15},
    "water": {"available": true, "tank_level_pct": 38, "supply_expected_at": "06:00"},
    "internet": {"available": true, "speed": "normal"},
    "gas": {"status": "sufficient"}
  },

  "historical": {
    "similar_past_contexts": [
      {
        "date": "2024-10-21",
        "similarity": 0.94,
        "summary": "Monday 6am, Navratri week. Motor ran at 6:20. All normal.",
        "key_events": ["motor_6:20", "pooja_6:15-7:10", "school_bus_7:15"]
      }
    ],
    "relevant_memories": [
      "Anjali always extends pooja duration by 30-45 mins during festival weeks",
      "Water tank depletes 25% faster during Diwali (decoration filling, guest usage)",
      "Diwali week: Rahul WFH Monday-Thursday"
    ]
  },

  "derived": {
    "household_mood": "festive_preparation",
    "urgency_score": 72,
    "attention_required": true,
    "primary_alert": "Water motor overdue — run immediately",
    "summary": "Festive Monday morning. Diwali prep Week 1. Motor overdue by 15 min. Extended pooja active. School prep beginning. Rahul WFH. Power stable."
  }
}
```

---

## Context Graph Model

The Context Engine internally maintains a **directed context graph** — a lightweight knowledge graph that captures relationships between context elements.

```
[Festival: Diwali Prep]
        │
        ├──► modifies ──► [Routine: Morning Pooja] ──► extends duration by 45min
        ├──► increases ──► [Resource: Water] ──► usage +25%
        ├──► shifts ──► [Temporal: Wake Time] ──► -45 minutes
        └──► activates ──► [Behavioral: Cleaning Cycle] ──► extra 2x/day

[Member: Anjali] ─── in ──► [Room: Pooja Room]
        │
        └──► running ──► [Routine: Morning Pooja]

[Appliance: Water Motor]
        │
        ├──► state: OFF
        ├──► last_run: 05:45 yesterday
        └──► ALERT: overdue 15 minutes ──► CRITICAL flag

[Member: Priya] ─── activity: school_prep
        │
        └──► connected_to ──► [Event: School Bus 07:15]
                                    │
                                    └──► depends_on ──► [Routine: Breakfast] ──► not started
```

---

## Context Assembly Pipeline

```python
class ContextEngine:

    async def build_context(self, household_id: UUID) -> HouseholdContextObject:

        # Parallel data fetch
        twin_state, calendar, recent_executions = await asyncio.gather(
            self.twin_service.get_latest_snapshot(household_id),
            self.calendar_service.get_current_context(household_id),
            self.routine_service.get_recent_executions(household_id, hours=6)
        )

        # Build temporal context
        temporal = self._build_temporal_context()

        # Build cultural context from festival calendar
        cultural = self._build_cultural_context(calendar, temporal)

        # Build spatial context from twin state
        spatial = self._build_spatial_context(twin_state)

        # Build behavioral context
        behavioral = self._build_behavioral_context(
            twin_state, recent_executions, temporal, cultural
        )

        # Retrieve relevant memories via pgvector
        context_text = self._build_context_text(temporal, cultural, behavioral)
        context_embedding = await self.titan_client.embed(context_text)
        memories = await self.memory_service.find_relevant(
            household_id, context_embedding, top_k=5
        )

        # Derive summary and urgency
        derived = await self._derive_context(
            temporal, cultural, spatial, behavioral, memories
        )

        hco = HouseholdContextObject(
            household_id=household_id,
            temporal=temporal,
            cultural=cultural,
            spatial=spatial,
            behavioral=behavioral,
            resources=self._build_resource_context(twin_state),
            historical={"similar_past_contexts": [], "relevant_memories": memories},
            derived=derived
        )

        # Store embedding for future similarity search
        await self.twin_service.store_snapshot_embedding(
            household_id, context_embedding, derived.summary
        )

        return hco
```

---

## Phase-of-Day Classification

The context engine classifies time into culturally-aware household phases:

```python
INDIAN_HOUSEHOLD_PHASES = {
    "brahma_muhurta":  ("04:00", "06:00"),  # Early rising, spiritual activity
    "early_morning":   ("06:00", "08:00"),  # Pooja, motor, school prep
    "morning_rush":    ("08:00", "10:00"),  # Commute, school departure
    "late_morning":    ("10:00", "12:00"),  # WFH work, mid-morning tasks
    "midday":          ("12:00", "14:00"),  # Lunch prep, afternoon quiet
    "afternoon":       ("14:00", "16:00"),  # Nap time, return from school
    "chai_time":       ("16:00", "17:30"),  # Social, chai, snacks
    "evening":         ("17:30", "19:30"),  # Tuition, play, evening routines
    "dinner_time":     ("19:30", "21:00"),  # Dinner prep, family time
    "night":           ("21:00", "23:00"),  # Wind down, study, TV
    "late_night":      ("23:00", "04:00"),  # Sleep, critical power cut window
}
```

---

## Urgency Score Algorithm

```python
def calculate_urgency_score(hco: dict) -> int:
    """
    0 = No attention needed (everything calm)
    100 = Immediate attention required (multiple critical issues)
    """
    score = 0

    # Resource issues
    if hco["spatial"]["appliances"]["water_motor"]["overdue_mins"] > 10: score += 30
    if not hco["resources"]["power"]["available"]: score += 25
    if hco["resources"]["water"]["tank_level_pct"] < 20: score += 20

    # Upcoming time-critical events
    imminent = hco["behavioral"]["imminent_routines"]
    critical_in_15 = [r for r in imminent if r.get("due_in_mins", 999) < 15]
    score += len(critical_in_15) * 10

    # Festival prep pressure
    if hco["cultural"]["days_to_main_festival"] <= 2: score += 15
    elif hco["cultural"]["days_to_main_festival"] <= 5: score += 7

    # Overdue routines
    overdue = [r for r in imminent if r.get("overdue")]
    score += len(overdue) * 15

    return min(score, 100)
```

---

## Context Caching Strategy

| Data | TTL | Storage |
|---|---|---|
| Full HCO | 5 minutes | Redis |
| Context embedding | Permanent | PostgreSQL pgvector |
| Festival context | 1 hour | Redis |
| Member locations | 1 minute | Redis |
| Routine schedule | 15 minutes | Redis |

The 5-minute HCO cache means background timer jobs don't thrash Bedrock — the same context is reused across prediction generation, notification checks, and any incoming user queries during that window.
