# GHARMIND AI — Entity Relationship Diagram

## ERD (Text/ASCII Format)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          GHARMIND AI — ERD                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

                              ┌─────────────────────┐
                              │      households      │
                              │─────────────────────│
                              │ PK id (UUID)         │
                              │    name              │
                              │    owner_user_id     │
                              │    city, state       │
                              │    pincode           │
                              │    timezone          │
                              │    language_pref     │
                              │    home_type         │
                              │    floors            │
                              │    tags[]            │
                              │    ai_persona_name   │
                              │    subscription_tier │
                              └──────────┬──────────┘
                                         │ 1
              ┌──────────────────────────┼────────────────────────────────┐
              │                          │                                 │
              │ N                        │ N                               │ N
   ┌──────────┴────────┐    ┌────────────┴───────────┐    ┌───────────────┴──────┐
   │   family_members  │    │        rooms            │    │      appliances      │
   │───────────────────│    │─────────────────────────│    │──────────────────────│
   │ PK id             │    │ PK id                   │    │ PK id                │
   │ FK household_id   │    │ FK household_id         │    │ FK household_id      │
   │    name, nickname │    │    name, room_type      │    │ FK room_id (opt.)    │
   │    role, age      │    │    floor, area_sqft     │    │    name, type        │
   │    work_schedule  │    │    position_x/y         │    │    power_state       │
   │    school_sched.  │    │    is_occupied          │    │    power_watts       │
   │    wake/sleep     │    │    occupants[]          │    │    is_critical       │
   │    preferences    │    │    lighting_state       │    │    auto_schedule     │
   │    phone_number   │    │    temperature_c        │    │    health_score      │
   └──────────┬────────┘    └────────────┬────────────┘    └───────────┬──────────┘
              │                          │                              │
              │                          └──────────────────────────────┘
              │                                     Aggregated into
              │                                          │
              │                          ┌──────────────▼─────────────────┐
              │                          │    twin_state_snapshots        │
              │                          │────────────────────────────────│
              │                          │ PK id                          │
              │                          │ FK household_id                │
              │                          │    snapshot_at (TIMESTAMPTZ)   │
              │                          │    ist_time, day_of_week       │
              │                          │    season, festival_context[]  │
              │                          │    rooms_state (JSONB)         │
              │                          │    appliances_state (JSONB)    │
              │                          │    members_state (JSONB)       │
              │                          │    power/water/internet avail. │
              │                          │    context_summary (TEXT)      │
              │                          │    context_embedding (vector)  │◄── pgvector
              │                          └──────────────┬─────────────────┘
              │                                         │ referenced by
              │                                         │
   ┌──────────┴────────┐                 ┌──────────────▼─────────────────┐
   │      routines     │                 │         predictions             │
   │───────────────────│                 │────────────────────────────────│
   │ PK id             │◄────────────────│ FK linked_routine_id (opt.)    │
   │ FK household_id   │                 │ PK id                          │
   │ FK primary_member │                 │ FK household_id                │
   │    name, type     │                 │ FK context_snapshot_id         │
   │    recurrence     │                 │    prediction_type             │
   │    schedule_expr  │                 │    title, description          │
   │    cond_trigger   │                 │    action_suggestion           │
   │    participant_ids│                 │    predicted_for               │
   │    appliance_ids  │                 │    confidence_score            │
   │    is_ai_detected │                 │    priority, category          │
   │    confidence     │                 │    reasoning, evidence         │
   │    pattern_embed. │◄── pgvector     │    status, was_accurate        │
   └──────────┬────────┘                 │    user_feedback               │
              │ 1                        └────────────────────────────────┘
              │ N
   ┌──────────▼────────┐
   │ routine_executions│
   │───────────────────│
   │ PK id             │
   │ FK routine_id     │
   │    household_id   │
   │    executed_at    │
   │    duration_mins  │
   │    season         │
   │    festival_ctx[] │
   │    was_predicted  │
   │    deviation_mins │
   │    execution_type │
   └───────────────────┘


   ┌────────────────────────┐         ┌───────────────────────────────────┐
   │   household_memories   │         │        festival_calendar          │
   │────────────────────────│         │───────────────────────────────────│
   │ PK id                  │         │ PK id                             │
   │ FK household_id        │         │    festival_name                  │
   │    memory_type         │         │    local_names (JSONB)            │
   │    title, content      │         │    festival_type                  │
   │    structured_data     │         │    region[]                       │
   │    embedding (vector)  │◄─pgvec  │    gregorian_date                 │
   │    valid_seasons[]     │         │    lunar_month/tithi              │
   │    valid_months[]      │         │    household_impact (JSONB)       │
   │    confidence          │         │    prep_days_before               │
   │    importance_score    │         │    is_public_holiday              │
   │    observation_count   │         │    is_school_holiday              │
   └────────────────────────┘         └───────────────────────────────────┘


   ┌──────────────────────────────────┐    ┌────────────────────────────────┐
   │       simulation_runs            │    │   household_calendar_events    │
   │──────────────────────────────────│    │────────────────────────────────│
   │ PK id                            │    │ PK id                          │
   │ FK household_id                  │    │ FK household_id                │
   │ FK run_by_member_id (opt.)       │    │ FK member_id (opt.)            │
   │    scenario_name, type           │    │    event_name, type            │
   │    hypothesis                    │    │    start_at, end_at            │
   │    perturbations (JSONB)         │    │    is_recurring                │
   │    sim_start_time                │    │    recurrence_rule             │
   │    sim_duration_hours            │    │    impact_tags[]               │
   │    status                        │    └────────────────────────────────┘
   │    result_summary                │
   │    impact_analysis (JSONB)       │    ┌────────────────────────────────┐
   │    risk_flags (JSONB)            │    │     household_event_log        │
   │    recommendations (JSONB)       │    │────────────────────────────────│
   │    timeline (JSONB)              │    │ PK id (BIGSERIAL)              │
   └──────────────────────────────────┘    │    household_id (UUID)         │
                                           │    event_type                  │
                                           │    event_source                │
                                           │    payload (JSONB)             │
                                           │    ist_timestamp               │
                                           │    event_date (PARTITIONED)    │
                                           └────────────────────────────────┘
```

---

## Relationship Summary

| Relationship | Cardinality | Notes |
|---|---|---|
| household → family_members | 1:N | Multiple members per household |
| household → rooms | 1:N | Multiple rooms per household |
| household → appliances | 1:N | Multiple appliances, optionally in rooms |
| rooms → appliances | 1:N (optional) | Appliance may be room-independent |
| household → twin_state_snapshots | 1:N | Taken every minute by twin engine |
| household → routines | 1:N | Many routines per household |
| routines → routine_executions | 1:N | Full execution history |
| family_members → routines | 1:N | Primary member owns routines |
| household → predictions | 1:N | AI-generated, expire after time |
| predictions → routines | N:1 (optional) | Prediction may reference a routine |
| predictions → twin_state_snapshots | N:1 | Context snapshot that led to prediction |
| household → household_memories | 1:N | Long-term AI memory (pgvector) |
| household → simulation_runs | 1:N | What-If simulations |
| festival_calendar | standalone | Global reference table, no household FK |
| household → household_calendar_events | 1:N | Household-specific events |
| household → household_event_log | 1:N | Audit log, partitioned |

---

## Index Strategy

| Table | Index | Purpose |
|---|---|---|
| twin_state_snapshots | (household_id, day_of_week, ist_time) | Find same-time-yesterday patterns |
| twin_state_snapshots | context_embedding ivfflat | Semantic context matching |
| routines | (household_id, next_expected_at) | Upcoming routine lookups |
| routines | pattern_embedding ivfflat | Routine similarity search |
| household_memories | embedding ivfflat | Semantic memory retrieval |
| predictions | (household_id, priority, predicted_for) | Active prediction feed |
| household_event_log | PARTITIONED BY DATE | Time-range queries at scale |

---

## Data Volume Estimates (Per Household, 1 Year)

| Table | Estimated Rows | Notes |
|---|---|---|
| twin_state_snapshots | ~525,600 | One per minute |
| household_event_log | ~2M | ~5-6 events per minute |
| routine_executions | ~5,000-15,000 | ~10-40 routines/day |
| predictions | ~10,000-30,000 | ~25-80 predictions/day |
| household_memories | ~500-2,000 | Grows slowly as AI learns |
