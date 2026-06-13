# GHARMIND AI — Database Schema
## PostgreSQL 16 + pgvector

---

## Design Principles

1. **Household isolation**: Every table with household data is partitioned by `household_id`
2. **Temporal richness**: All events capture IST timezone with season/festival context
3. **Vector-native memory**: Routine patterns and household memories stored as pgvector embeddings
4. **Audit trail**: All significant events logged with timestamps for pattern learning

---

## Extensions Required

```sql
-- Enable vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable trigram search for Hinglish text
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable time-series helpers
CREATE EXTENSION IF NOT EXISTS btree_gist;
```

---

## Schema: `core` — Household & Members

```sql
-- ============================================================
-- TABLE: households
-- The root entity. One row per registered home.
-- ============================================================
CREATE TABLE households (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(200) NOT NULL,           -- "Sharma Residence"
    owner_user_id       VARCHAR(200) NOT NULL,           -- Cognito user ID
    city                VARCHAR(100) NOT NULL,           -- "Pune"
    state               VARCHAR(100) NOT NULL,           -- "Maharashtra"
    pincode             VARCHAR(10),
    timezone            VARCHAR(50) DEFAULT 'Asia/Kolkata',
    language_preference VARCHAR(20) DEFAULT 'hinglish',  -- en, hi, hinglish
    home_type           VARCHAR(50),                     -- apartment, villa, row_house
    floors              SMALLINT DEFAULT 1,
    total_rooms         SMALLINT DEFAULT 4,

    -- Contextual tags (array of household characteristics)
    tags                TEXT[],                          -- ['joint_family', 'has_students', 'working_couple']

    -- Onboarding & config
    onboarding_complete BOOLEAN DEFAULT FALSE,
    twin_initialized    BOOLEAN DEFAULT FALSE,
    ai_persona_name     VARCHAR(100) DEFAULT 'Gharji',  -- Name of household AI

    -- Subscription
    subscription_tier   VARCHAR(50) DEFAULT 'free',     -- free, pro, family

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ                      -- soft delete
);

CREATE INDEX idx_households_owner ON households(owner_user_id);
CREATE INDEX idx_households_city  ON households(city, state);


-- ============================================================
-- TABLE: family_members
-- People who live in or are associated with the household
-- ============================================================
CREATE TABLE family_members (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,
    nickname            VARCHAR(50),
    role                VARCHAR(50) NOT NULL,            -- parent, child, grandparent, help, tenant
    age                 SMALLINT,
    gender              VARCHAR(20),

    -- Schedules (JSONB for flexibility)
    work_schedule       JSONB,  -- {"type": "office", "days": ["mon","tue","wed","thu","fri"], "start": "09:00", "end": "18:00"}
    school_schedule     JSONB,  -- {"school_name": "...", "bus_time": "07:15", "return_time": "14:30"}
    typical_wake_time   TIME,
    typical_sleep_time  TIME,

    -- Behavioral profile
    is_primary_contact  BOOLEAN DEFAULT FALSE,
    receives_alerts     BOOLEAN DEFAULT TRUE,
    phone_number        VARCHAR(20),                     -- For WhatsApp alerts
    preferences         JSONB,  -- {"chai_time": "16:00", "quiet_hours": ["22:00","06:00"]}

    -- Device/presence tracking (simulated)
    last_seen_at        TIMESTAMPTZ,
    simulated_location  VARCHAR(50),                     -- current room in twin

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_members_household ON family_members(household_id);
CREATE INDEX idx_members_role      ON family_members(household_id, role);
```

---

## Schema: `twin` — Household Digital Twin

```sql
-- ============================================================
-- TABLE: rooms
-- Physical spaces in the household
-- ============================================================
CREATE TABLE rooms (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name                VARCHAR(100) NOT NULL,           -- "Pooja Room", "Kitchen", "Study"
    room_type           VARCHAR(50) NOT NULL,            -- bedroom, kitchen, bathroom, pooja_room, study, living, balcony, garage
    floor               SMALLINT DEFAULT 0,
    area_sqft           DECIMAL(6,2),
    position_x          DECIMAL(5,2),                   -- For floor plan rendering (0-100 grid)
    position_y          DECIMAL(5,2),

    -- Current simulated state (updated by twin engine)
    is_occupied         BOOLEAN DEFAULT FALSE,
    occupants           TEXT[],                          -- member IDs currently in room
    lighting_state      VARCHAR(20) DEFAULT 'off',       -- off, dim, on, auto
    temperature_c       DECIMAL(4,1),
    air_quality         VARCHAR(20),                     -- good, moderate, poor
    noise_level         VARCHAR(20),                     -- quiet, moderate, noisy

    -- Twin metadata
    last_state_change   TIMESTAMPTZ DEFAULT NOW(),

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rooms_household ON rooms(household_id);
CREATE INDEX idx_rooms_type      ON rooms(household_id, room_type);


-- ============================================================
-- TABLE: appliances
-- All simulated household appliances/systems
-- ============================================================
CREATE TABLE appliances (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    room_id             UUID REFERENCES rooms(id),
    name                VARCHAR(100) NOT NULL,           -- "Water Motor", "Geyser", "WiFi Router"
    appliance_type      VARCHAR(50) NOT NULL,            -- motor, geyser, fan, ac, tv, fridge, washing_machine, wifi
    brand               VARCHAR(100),

    -- Simulated state
    power_state         VARCHAR(20) DEFAULT 'off',       -- off, on, standby, error
    power_watts         SMALLINT,                        -- Current wattage consumption
    is_critical         BOOLEAN DEFAULT FALSE,           -- Water motor, fridge = critical
    auto_schedule       JSONB,                           -- {"on": "05:30", "off": "06:30", "days": ["*"]}
    health_score        SMALLINT DEFAULT 100,            -- 0-100 simulated health

    -- Usage patterns (learned by twin)
    avg_daily_runtime_mins  SMALLINT,
    last_on_at          TIMESTAMPTZ,
    last_off_at         TIMESTAMPTZ,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_appliances_household ON appliances(household_id);
CREATE INDEX idx_appliances_type      ON appliances(household_id, appliance_type);


-- ============================================================
-- TABLE: twin_state_snapshots
-- Point-in-time snapshot of the entire household state
-- Used by AI for pattern learning and What-If comparison
-- ============================================================
CREATE TABLE twin_state_snapshots (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    snapshot_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Temporal context at snapshot time
    ist_time            TIME NOT NULL,
    day_of_week         SMALLINT NOT NULL,               -- 0=Monday, 6=Sunday
    week_number         SMALLINT,
    month               SMALLINT,
    season              VARCHAR(20),                     -- summer, monsoon, winter, spring
    festival_context    TEXT[],                          -- Active festivals at this time
    is_holiday          BOOLEAN DEFAULT FALSE,
    is_exam_period      BOOLEAN DEFAULT FALSE,

    -- Compressed household state (JSONB)
    rooms_state         JSONB NOT NULL,                  -- {room_id: {occupied, lights, temp...}}
    appliances_state    JSONB NOT NULL,                  -- {appliance_id: {power, watts...}}
    members_state       JSONB NOT NULL,                  -- {member_id: {room, activity...}}
    power_available     BOOLEAN DEFAULT TRUE,
    water_available     BOOLEAN DEFAULT TRUE,
    internet_available  BOOLEAN DEFAULT TRUE,

    -- AI-generated context summary
    context_summary     TEXT,                            -- "Morning routine peak, school prep active"
    context_embedding   vector(1536),                   -- Titan embedding of context summary

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_household_time ON twin_state_snapshots(household_id, snapshot_at DESC);
CREATE INDEX idx_snapshots_day_time       ON twin_state_snapshots(household_id, day_of_week, ist_time);
CREATE INDEX idx_snapshots_embedding      ON twin_state_snapshots
    USING ivfflat (context_embedding vector_cosine_ops) WITH (lists = 100);
```

---

## Schema: `routines` — Routine & Pattern Engine

```sql
-- ============================================================
-- TABLE: routines
-- Named, recurring household activities
-- ============================================================
CREATE TABLE routines (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name                VARCHAR(200) NOT NULL,           -- "Morning Pooja", "Water Motor Schedule"
    description         TEXT,
    routine_type        VARCHAR(50) NOT NULL,            -- pooja, motor, tuition, meal, study, chai, cleaning, exercise, commute, festival

    -- Scheduling
    recurrence          VARCHAR(50) NOT NULL,            -- daily, weekly, monthly, annual, conditional
    schedule_expression JSONB,                           -- Cron-like: {"days": ["mon","wed","fri"], "time": "06:00", "duration_mins": 30}
    conditional_trigger TEXT,                            -- "when season=monsoon AND time=05:30"

    -- Participants
    primary_member_id   UUID REFERENCES family_members(id),
    participant_ids     UUID[],                          -- All involved members

    -- Appliances involved
    appliance_ids       UUID[],                          -- Appliances used in this routine

    -- AI learning metadata
    is_ai_detected      BOOLEAN DEFAULT FALSE,           -- Detected by pattern engine vs manually added
    confidence_score    DECIMAL(3,2),                   -- AI detection confidence 0.00-1.00
    detection_method    VARCHAR(50),                     -- pattern_match, explicit, inferred

    -- State
    is_active           BOOLEAN DEFAULT TRUE,
    last_executed_at    TIMESTAMPTZ,
    next_expected_at    TIMESTAMPTZ,
    execution_count     INTEGER DEFAULT 0,

    -- Vector representation of this routine's pattern
    pattern_embedding   vector(1536),                   -- For semantic similarity matching

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_routines_household      ON routines(household_id);
CREATE INDEX idx_routines_type           ON routines(household_id, routine_type);
CREATE INDEX idx_routines_next_expected  ON routines(household_id, next_expected_at)
    WHERE is_active = TRUE;
CREATE INDEX idx_routines_embedding      ON routines
    USING ivfflat (pattern_embedding vector_cosine_ops) WITH (lists = 50);


-- ============================================================
-- TABLE: routine_executions
-- Log of every time a routine runs (actual or simulated)
-- ============================================================
CREATE TABLE routine_executions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    routine_id          UUID NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
    household_id        UUID NOT NULL,
    executed_at         TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    duration_mins       SMALLINT,

    -- Context at execution time
    ist_time            TIME NOT NULL,
    day_of_week         SMALLINT NOT NULL,
    season              VARCHAR(20),
    festival_context    TEXT[],
    was_predicted       BOOLEAN DEFAULT FALSE,
    prediction_accuracy DECIMAL(3,2),

    -- Deviation tracking
    was_on_schedule     BOOLEAN DEFAULT TRUE,
    deviation_mins      SMALLINT DEFAULT 0,             -- +/- from expected time
    deviation_reason    TEXT,

    -- Type: real (user confirmed) or simulated (twin-generated)
    execution_type      VARCHAR(20) DEFAULT 'real',     -- real, simulated

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_executions_routine     ON routine_executions(routine_id, executed_at DESC);
CREATE INDEX idx_executions_household   ON routine_executions(household_id, executed_at DESC);
CREATE INDEX idx_executions_day_time    ON routine_executions(household_id, day_of_week, ist_time);
```

---

## Schema: `ai` — Predictions & Memory

```sql
-- ============================================================
-- TABLE: predictions
-- AI-generated predictions about upcoming household events
-- ============================================================
CREATE TABLE predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    generated_at        TIMESTAMPTZ DEFAULT NOW(),

    -- What is predicted
    prediction_type     VARCHAR(50) NOT NULL,            -- routine_start, appliance_action, member_return, festival_prep, power_cut, water_issue
    title               VARCHAR(300) NOT NULL,           -- "Water motor should run in 15 minutes"
    description         TEXT NOT NULL,                   -- Full prediction rationale
    action_suggestion   TEXT,                            -- "Start motor now to ensure tank fills before 7am school rush"

    -- When it will happen
    predicted_for       TIMESTAMPTZ NOT NULL,
    prediction_window   INTERVAL DEFAULT '30 minutes',   -- Uncertainty window

    -- Confidence & priority
    confidence_score    DECIMAL(3,2) NOT NULL,           -- 0.00-1.00
    priority            VARCHAR(20) DEFAULT 'normal',    -- low, normal, high, critical
    category            VARCHAR(50),                     -- water, power, routine, family, festival

    -- Context that led to this prediction
    context_snapshot_id UUID REFERENCES twin_state_snapshots(id),
    reasoning           TEXT,                            -- Claude's reasoning chain
    evidence            JSONB,                           -- Supporting data points

    -- Linked routine (if applicable)
    linked_routine_id   UUID REFERENCES routines(id),

    -- Outcome tracking (for model improvement)
    status              VARCHAR(30) DEFAULT 'pending',  -- pending, confirmed, dismissed, expired
    was_accurate        BOOLEAN,
    actual_occurred_at  TIMESTAMPTZ,
    user_feedback       VARCHAR(20),                    -- helpful, not_helpful, wrong

    expires_at          TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_household_time ON predictions(household_id, predicted_for)
    WHERE status = 'pending';
CREATE INDEX idx_predictions_priority       ON predictions(household_id, priority, predicted_for)
    WHERE status = 'pending';


-- ============================================================
-- TABLE: household_memories
-- Long-term semantic memory stored as vectors
-- The "remembering" brain of GHARMIND AI
-- ============================================================
CREATE TABLE household_memories (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    memory_type         VARCHAR(50) NOT NULL,            -- routine_pattern, preference, exception, festival_behavior, seasonal_pattern
    title               VARCHAR(300) NOT NULL,
    content             TEXT NOT NULL,                   -- Human-readable memory description
    structured_data     JSONB,                           -- Machine-readable structured form

    -- Vector representation (Titan Embeddings)
    embedding           vector(1536) NOT NULL,

    -- Temporal context
    observed_at         TIMESTAMPTZ,
    valid_seasons       TEXT[],                          -- ['monsoon', 'summer']
    valid_months        SMALLINT[],                      -- [10, 11] for Diwali season
    recurrence          VARCHAR(50),                     -- how often this pattern repeats

    -- Confidence & importance
    confidence          DECIMAL(3,2) DEFAULT 1.00,
    importance_score    SMALLINT DEFAULT 50,             -- 0-100
    observation_count   INTEGER DEFAULT 1,              -- How many times observed

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memories_household ON household_memories(household_id, memory_type);
CREATE INDEX idx_memories_embedding ON household_memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- ============================================================
-- TABLE: simulation_runs
-- Results of What-If scenario simulations
-- ============================================================
CREATE TABLE simulation_runs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    run_by_member_id    UUID REFERENCES family_members(id),
    run_at              TIMESTAMPTZ DEFAULT NOW(),

    -- Scenario definition
    scenario_name       VARCHAR(200) NOT NULL,           -- "Power cut during dinner prep"
    scenario_type       VARCHAR(50),                     -- power_cut, water_shortage, guest_arrival, exam_week, festival
    hypothesis          TEXT NOT NULL,                   -- What is being tested
    perturbations       JSONB NOT NULL,                  -- Changes applied to twin state

    -- Simulation parameters
    sim_start_time      TIMESTAMPTZ NOT NULL,
    sim_duration_hours  SMALLINT DEFAULT 24,
    sim_resolution_mins SMALLINT DEFAULT 15,             -- Granularity of simulation

    -- Results
    status              VARCHAR(30) DEFAULT 'running',  -- running, complete, failed
    result_summary      TEXT,                            -- Claude's plain-English summary
    impact_analysis     JSONB,                           -- {routine_id: impact_description}
    risk_flags          JSONB,                           -- Identified risks
    recommendations     JSONB,                           -- Mitigation suggestions
    confidence          DECIMAL(3,2),

    -- Full simulation timeline (compressed)
    timeline            JSONB,                           -- Array of simulated state snapshots

    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_simulations_household ON simulation_runs(household_id, run_at DESC);
```

---

## Schema: `calendar` — Indian Festival & Event Calendar

```sql
-- ============================================================
-- TABLE: festival_calendar
-- Pre-populated Indian festival and event calendar
-- ============================================================
CREATE TABLE festival_calendar (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    festival_name       VARCHAR(200) NOT NULL,
    local_names         JSONB,                           -- {"hi": "दीपावली", "mr": "दिवाळी"}
    festival_type       VARCHAR(50) NOT NULL,            -- hindu, muslim, christian, sikh, national, regional
    region              TEXT[],                          -- ['all_india'] or ['maharashtra', 'goa']

    -- Date info
    gregorian_date      DATE,                            -- NULL if lunar/variable
    lunar_month         VARCHAR(30),                     -- For lunar calendar festivals
    lunar_tithi         VARCHAR(50),
    calculation_rule    TEXT,                            -- How to compute if variable

    -- Household impact model
    household_impact    JSONB NOT NULL,                  -- How this festival changes household behavior
    -- Example: {
    --   "preparation_days": 3,
    --   "peak_activity": "morning",
    --   "typical_routines": ["extended_pooja", "sweet_making", "cleaning"],
    --   "water_usage_multiplier": 1.5,
    --   "power_usage_multiplier": 1.3,
    --   "sleep_shift_hours": -1
    -- }

    -- Pre/post festival windows
    prep_days_before    SMALLINT DEFAULT 1,
    celebration_days    SMALLINT DEFAULT 1,
    recovery_days       SMALLINT DEFAULT 0,

    is_public_holiday   BOOLEAN DEFAULT FALSE,
    is_school_holiday   BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_festival_date   ON festival_calendar(gregorian_date);
CREATE INDEX idx_festival_type   ON festival_calendar(festival_type);
CREATE INDEX idx_festival_region ON festival_calendar USING GIN(region);


-- ============================================================
-- TABLE: household_calendar_events
-- Custom events for a specific household
-- (Tuition schedules, exams, family events, etc.)
-- ============================================================
CREATE TABLE household_calendar_events (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    member_id           UUID REFERENCES family_members(id),
    event_name          VARCHAR(200) NOT NULL,
    event_type          VARCHAR(50) NOT NULL,            -- exam, tuition, guest, travel, medical, birthday
    start_at            TIMESTAMPTZ NOT NULL,
    end_at              TIMESTAMPTZ,
    is_recurring        BOOLEAN DEFAULT FALSE,
    recurrence_rule     JSONB,                           -- {"frequency": "weekly", "day": "tuesday"}

    -- How this event should affect AI predictions
    impact_tags         TEXT[],                          -- ['quiet_hours', 'no_interruptions', 'extra_water', 'early_wake']
    description         TEXT,
    notes               TEXT,

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hh_events_household ON household_calendar_events(household_id, start_at);
CREATE INDEX idx_hh_events_member    ON household_calendar_events(member_id, start_at);
```

---

## Schema: `audit` — Event Log

```sql
-- ============================================================
-- TABLE: household_event_log
-- Immutable audit log of all significant household events
-- Used for pattern learning and debugging
-- ============================================================
CREATE TABLE household_event_log (
    id                  BIGSERIAL PRIMARY KEY,
    household_id        UUID NOT NULL,
    event_type          VARCHAR(100) NOT NULL,           -- twin.state_change, routine.started, prediction.generated, agent.called
    event_source        VARCHAR(50) NOT NULL,            -- twin_engine, context_agent, prediction_agent, user, system
    payload             JSONB NOT NULL,
    ist_timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Partition key for performance
    event_date          DATE GENERATED ALWAYS AS (ist_timestamp::DATE) STORED
) PARTITION BY RANGE (event_date);

-- Create monthly partitions
CREATE TABLE household_event_log_2024_01 PARTITION OF household_event_log
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- (additional partitions created automatically by migration)

CREATE INDEX idx_event_log_household ON household_event_log(household_id, ist_timestamp DESC);
CREATE INDEX idx_event_log_type      ON household_event_log(household_id, event_type, ist_timestamp DESC);
```

---

## Vector Search Queries (Examples)

```sql
-- Find memories most similar to current context
SELECT id, title, content, confidence,
       1 - (embedding <=> $1::vector) AS similarity
FROM household_memories
WHERE household_id = $2
ORDER BY embedding <=> $1::vector
LIMIT 10;

-- Find historical snapshots similar to current state
SELECT id, snapshot_at, context_summary,
       1 - (context_embedding <=> $1::vector) AS similarity
FROM twin_state_snapshots
WHERE household_id = $2
  AND snapshot_at > NOW() - INTERVAL '90 days'
ORDER BY context_embedding <=> $1::vector
LIMIT 5;

-- Find routines matching a described pattern
SELECT id, name, routine_type, confidence_score,
       1 - (pattern_embedding <=> $1::vector) AS similarity
FROM routines
WHERE household_id = $2
  AND is_active = TRUE
ORDER BY pattern_embedding <=> $1::vector
LIMIT 5;
```

---

## Database Configuration

```sql
-- Performance tuning for pgvector
SET work_mem = '256MB';
SET maintenance_work_mem = '1GB';
SET max_parallel_workers_per_gather = 4;

-- pgvector index parameters
SET ivfflat.probes = 10;  -- Balance between accuracy and speed
```

---

## Seed Data Requirements

The following reference data must be seeded on deployment:
1. `festival_calendar` — 50+ Indian festivals with household impact models
2. Demo household: Sharma family (Pune) with 5 members, 8 rooms, 12 appliances
3. 15 pre-defined routine templates for Indian households
4. 6 months of simulated historical twin snapshots for the demo household
