# GHARMIND AI — Prediction Engine Design

---

## Philosophy

The GHARMIND Prediction Engine is not a rules engine. It does not say "if time = 6am, run motor." It *learns* that *this household*, on *this day of the week*, in *this season*, given *these family members at home*, *typically runs the motor between 6:15 and 6:45am*.

The distinction matters: a rules engine breaks when context changes. The prediction engine *adapts* — recognizing that Diwali week shifts schedules, that monsoon means earlier motor runs, that exam weeks quiet the morning rush.

---

## Prediction Engine Architecture

```
                    ┌──────────────────────────────────────┐
                    │        PREDICTION ENGINE              │
                    │                                       │
 [HCO Input] ──────►│  1. Pattern Scanner                  │
                    │     (What's due in next 2 hours?)    │
                    │            │                          │
                    │            ▼                          │
                    │  2. Similarity Matcher                │
                    │     (pgvector: find similar pasts)   │
                    │            │                          │
                    │            ▼                          │
                    │  3. Context Multiplier Engine         │
                    │     (Festival/Season/Holiday mods)   │
                    │            │                          │
                    │            ▼                          │
                    │  4. Confidence Calculator             │
                    │     (Bayesian-style scoring)          │
                    │            │                          │
                    │            ▼                          │
                    │  5. Claude Enrichment                 │
                    │     (Natural language + reasoning)    │
                    │            │                          │
                    │            ▼                          │
                    │  6. Anomaly Detector                  │
                    │     (Missed/late routine flags)       │
                    │            │                          │
                    │            ▼                          │
                    │  7. Prediction Ranker                 │
                    │     (Priority × Confidence × Urgency)│
                    └──────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Prediction Store      │
                    │   (PostgreSQL + Redis)   │
                    └─────────────────────────┘
```

---

## Step 1: Pattern Scanner

Scans the current household for predictable near-term events.

### Sources Scanned

| Source | Description |
|---|---|
| `routines` table | All active routines with `next_expected_at` in next 2h |
| `household_calendar_events` | Scheduled events in next 24h |
| `festival_calendar` | Active festival behavior models |
| `appliance` schedules | Appliances with auto-schedules due |
| `family_members` schedules | Member arrivals/departures |

### Pattern Types Generated

```python
PREDICTION_TYPES = {
    "routine_start":     "A scheduled household routine is about to begin",
    "routine_overdue":   "A routine should have started but hasn't",
    "appliance_action":  "An appliance needs to be turned on/off",
    "member_arrival":    "A family member is expected home",
    "member_departure":  "A family member is about to leave",
    "festival_prep":     "Festival preparation activity required",
    "power_event":       "Power cut or restoration predicted",
    "water_event":       "Water supply change predicted",
    "meal_time":         "Meal preparation time approaching",
    "study_reminder":    "Study/exam schedule event upcoming",
    "maintenance":       "Scheduled maintenance or replenishment needed"
}
```

---

## Step 2: Similarity Matcher

For each candidate prediction, find historical instances of the same pattern.

```python
class SimilarityMatcher:
    """
    Given a prediction candidate and current context,
    find the N most similar historical contexts and their outcomes.
    """

    async def find_similar_executions(
        self,
        routine_id: UUID,
        current_context_embedding: list[float],
        day_of_week: int,
        window_hours: int = 2
    ) -> list[SimilarExecution]:

        # Step 1: Exact temporal match (same day/time window)
        temporal_matches = await self.db.fetch("""
            SELECT re.*, ts.context_embedding
            FROM routine_executions re
            JOIN twin_state_snapshots ts ON ts.household_id = re.household_id
                AND ts.snapshot_at BETWEEN re.executed_at - INTERVAL '5 minutes'
                                       AND re.executed_at + INTERVAL '5 minutes'
            WHERE re.routine_id = $1
              AND re.day_of_week = $2
              AND re.executed_at > NOW() - INTERVAL '90 days'
        """, routine_id, day_of_week)

        # Step 2: Semantic context match (similar household state)
        semantic_matches = await self.db.fetch("""
            SELECT 1 - (context_embedding <=> $1::vector) AS similarity, *
            FROM twin_state_snapshots
            WHERE household_id = $2
            ORDER BY context_embedding <=> $1::vector
            LIMIT 10
        """, current_context_embedding, self.household_id)

        return self._merge_and_score(temporal_matches, semantic_matches)
```

---

## Step 3: Context Multiplier Engine

Cultural and seasonal context modifies prediction confidence and timing.

### Multiplier Table

| Context Factor | Affected Routines | Multiplier Effect |
|---|---|---|
| **Diwali Week** | Pooja duration, cleaning, shopping | +30% duration, -1h start time |
| **Exam Week** | Study routines, sleep schedules | +20% study time, -2h screen time |
| **Monsoon Season** | Water motor (faster tank fill), laundry | -15 min motor runtime, +1 extra laundry |
| **Summer** | AC usage, water consumption | +40% power for cooling, +20% water |
| **School Holiday** | Morning routine, wake time | +45 min wake shift, reduced school prep |
| **Power Cut History** | Evening routines, dinner timing | Shift by cut window, charge devices before |
| **Guest Expected** | Cleaning, cooking, sleeping arrangements | +90 min cleaning, +1 meal prep round |
| **WFH Day** | Quiet hours, tea schedule, noise | Extended quiet hours, 3-4 chai times |

### Festival Impact Models

```python
FESTIVAL_BEHAVIOR_MODELS = {
    "diwali": {
        "prep_days": 5,
        "morning_shift_hours": -1.0,
        "pooja_duration_multiplier": 2.5,
        "cleaning_cycles_extra": 3,
        "water_usage_multiplier": 1.4,
        "power_usage_multiplier": 1.6,  # Lights, decoration
        "sleep_shift_hours": -1.5,      # Later nights
        "shopping_trips": 4,
        "guest_probability": 0.85
    },
    "ganesh_chaturthi": {
        "prep_days": 3,
        "morning_shift_hours": -0.75,
        "pooja_duration_multiplier": 3.0,  # Major pooja
        "community_activity": True,
        "noise_level": "festive",
        "water_usage_multiplier": 1.3
    },
    "navratri": {
        "prep_days": 2,
        "evening_shift_hours": 2.0,  # Garba at night
        "sleep_shift_hours": -2.0,
        "fasting_members_possible": True
    },
    "eid": {
        "prep_days": 2,
        "cooking_sessions_extra": 4,
        "guest_probability": 0.90,
        "water_usage_multiplier": 1.3
    },
    "holi": {
        "water_usage_multiplier": 3.0,  # Major spike
        "morning_shift_hours": -1.0,
        "outdoor_activity": True
    }
}
```

---

## Step 4: Confidence Calculator

```python
def calculate_confidence(
    base_rate: float,           # Historical occurrence rate (0-1)
    temporal_evidence: int,     # Number of matching historical instances
    semantic_similarity: float, # pgvector cosine similarity to past contexts
    festival_multiplier: float, # Context multiplier from Step 3
    deviation_history: list[int] # Historical deviation in minutes
) -> float:

    # Bayesian-style update
    # Prior: base rate from temporal patterns
    prior = base_rate

    # Likelihood: how similar is today to past successful occurrences
    evidence_strength = min(temporal_evidence / 10, 1.0)  # Cap at 10 instances
    likelihood = (semantic_similarity * 0.6) + (evidence_strength * 0.4)

    # Posterior update
    posterior = (prior * 0.5) + (likelihood * 0.5)

    # Festival adjustment
    posterior *= festival_multiplier

    # Penalize high-variance routines
    if deviation_history:
        std_dev = statistics.stdev(deviation_history) if len(deviation_history) > 1 else 0
        stability_score = max(0.5, 1.0 - (std_dev / 120))  # 120 min = full penalty
        posterior *= stability_score

    return round(min(max(posterior, 0.05), 0.99), 2)
```

---

## Step 5: Claude Enrichment

Each prediction gets a Claude Sonnet call to add:
- Natural language action suggestion
- Reasoning chain
- Risk if ignored

Batched for efficiency: 5 predictions per call.

---

## Step 6: Anomaly Detector

Identifies deviations from expected patterns.

```python
ANOMALY_TYPES = {
    "routine_missed": {
        "trigger": "routine due > 20 mins ago, not started",
        "severity": "depends on routine criticality",
        "action": "Alert family, reschedule or investigate"
    },
    "routine_early": {
        "trigger": "routine started > 30 mins before expected",
        "severity": "informational",
        "action": "Log, adjust future predictions"
    },
    "unexpected_absence": {
        "trigger": "member expected home but not arrived",
        "severity": "high if school child",
        "action": "Alert primary contact"
    },
    "appliance_overrun": {
        "trigger": "appliance running > 2x typical duration",
        "severity": "medium",
        "action": "Flag for attention (possible issue)"
    },
    "power_anomaly": {
        "trigger": "power restored/cut outside normal window",
        "severity": "informational",
        "action": "Update power model, adjust predictions"
    }
}
```

---

## Step 7: Prediction Ranker

```python
def rank_predictions(predictions: list[Prediction]) -> list[Prediction]:
    """
    Final ranking before delivering to dashboard/notifications.
    Balances urgency, confidence, and user fatigue.
    """

    PRIORITY_SCORES = {
        "critical": 100,
        "high": 70,
        "normal": 40,
        "low": 10
    }

    for p in predictions:
        # Time urgency: exponential decay (closer = higher score)
        minutes_away = (p.predicted_for - datetime.now(IST)).total_seconds() / 60
        urgency = math.exp(-minutes_away / 60)  # Peaks when <15 min away

        # Composite rank score
        p.rank_score = (
            PRIORITY_SCORES[p.priority] * 0.4 +
            p.confidence_score * 100 * 0.4 +
            urgency * 100 * 0.2
        )

    # Anti-flood: max 3 predictions per 30-minute window
    return deduplicate_and_limit(sorted(predictions, key=lambda p: p.rank_score, reverse=True))
```

---

## Prediction Horizon Design

| Horizon | Content | Refresh Rate |
|---|---|---|
| **Next 30 minutes** | High-confidence imminent events | Every 5 minutes |
| **Next 2 hours** | Routine schedule, member movements | Every 15 minutes |
| **Today** | Full day planning view | Hourly |
| **This week** | Festival prep, exam schedule, major events | Every 6 hours |
| **This month** | Maintenance, seasonal planning | Daily |

---

## Prediction Accuracy Feedback Loop

```
User sees prediction → Takes action → Confirms / Dismisses
                                           │
                                    Outcome stored
                                           │
                               ┌───────────▼────────────┐
                               │   Accuracy Analysis    │
                               │   (weekly batch job)   │
                               │                        │
                               │  - Confidence tuning   │
                               │  - Timing adjustment   │
                               │  - Pattern refinement  │
                               └────────────────────────┘
                                           │
                               pgvector memory updated
                               with improved patterns
```

---

## Demo: Prediction Timeline for Sharma Family (Monday, Diwali Prep Week)

```
06:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ [CRITICAL 94%] Water Motor — Run now. Tank at 40%.
06:15 ────────────────────────────────────────────────────
  🪔 [HIGH 88%] Extended Morning Pooja begins (Diwali week pattern)
07:15 ────────────────────────────────────────────────────
  🚌 [HIGH 95%] Priya's school bus. Ensure breakfast done.
08:30 ────────────────────────────────────────────────────
  ☕ [NORMAL 82%] Morning chai round 2 (Rahul's WFH day)
10:00 ────────────────────────────────────────────────────
  💼 [NORMAL 91%] Rahul's Zoom call. Quiet mode on.
13:00 ────────────────────────────────────────────────────
  🍽️ [NORMAL 78%] Lunch prep. Extended — festival cooking likely.
14:30 ────────────────────────────────────────────────────
  🚌 [HIGH 93%] Priya returns from school.
17:00 ────────────────────────────────────────────────────
  📚 [HIGH 86%] Tuition batch at home (5 students). Quiet living room needed.
19:30 ────────────────────────────────────────────────────
  ⚡ [HIGH 79%] Load shedding expected. Charge devices by 7pm.
20:00 ────────────────────────────────────────────────────
  🍽️ [NORMAL 85%] Dinner. Festival meal — longer than usual.
22:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
