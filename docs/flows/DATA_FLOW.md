# GHARMIND AI — Data Flow Diagrams

---

## Flow 1: Twin Engine Tick Cycle (Every Minute)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TWIN ENGINE TICK CYCLE                            │
│                       Every 60 seconds                               │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │  SCHEDULER   │ ← APScheduler job, every 60s
  │  (APScheduler)│
  └──────┬───────┘
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                      TWIN ENGINE                                  │
  │                                                                   │
  │  1. Read current household config from Redis cache                │
  │     └── If cache miss: load from PostgreSQL + repopulate Redis    │
  │                                                                   │
  │  2. Advance state models:                                         │
  │     ├── TimeModel.advance()      → IST time, phase, season       │
  │     ├── CalendarModel.check()    → Festivals, holidays            │
  │     ├── OccupancyModel.advance() → Member locations               │
  │     ├── ApplianceModel.advance() → Appliance states               │
  │     ├── WaterModel.advance()     → Tank level, supply status      │
  │     └── PowerModel.advance()     → Grid status, cut prediction    │
  │                                                                   │
  │  3. Detect routine triggers                                       │
  │     └── Compare current state vs routine schedules               │
  │                                                                   │
  │  4. Detect anomalies                                              │
  │     └── Overdue routines, unexpected member absence               │
  │                                                                   │
  │  5. Generate state snapshot                                       │
  └──────────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
  ┌──────────────────┐             ┌───────────────────┐
  │   PostgreSQL     │             │   Redis Pub/Sub   │
  │                  │             │                   │
  │  INSERT INTO     │             │  PUBLISH          │
  │  twin_state_     │             │  household:{id}   │
  │  snapshots       │             │  channel:         │
  │                  │             │  "state_update"   │
  │  (full state +   │             │                   │
  │   embedding)     │             │  → WebSocket hub  │
  └──────────────────┘             └───────────┬───────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  Connected Dashboard  │
                                    │  (Next.js WebSocket   │
                                    │   client)             │
                                    │                       │
                                    │  Real-time UI update  │
                                    └──────────────────────┘


Every 5th tick (every 5 minutes):

         ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   CONTEXT + PREDICTION PIPELINE                   │
  │                                                                   │
  │  1. ContextAgent.build(twin_state)                                │
  │     ├── Load calendar context                                     │
  │     ├── Load recent routine executions                            │
  │     ├── Embed context via Titan (AWS Bedrock)                     │
  │     ├── pgvector search: find similar past contexts               │
  │     └── Build Household Context Object (HCO)                     │
  │     → Cache HCO in Redis (TTL 5min)                               │
  │                                                                   │
  │  2. PredictionAgent.generate(HCO)                                 │
  │     ├── Pattern Scanner: find due routines                        │
  │     ├── Similarity Matcher: pgvector lookup                       │
  │     ├── Context Multiplier: apply festival/season factors         │
  │     ├── Confidence Calculator                                     │
  │     ├── Claude Sonnet: enrich predictions (Bedrock call)          │
  │     ├── Anomaly Detector: flag overdue routines                   │
  │     └── Ranker: sort by priority × confidence × urgency           │
  │                                                                   │
  │  3. Store predictions in PostgreSQL                               │
  │     └── Expire old predictions                                    │
  │                                                                   │
  │  4. Push high-priority predictions via WebSocket                  │
  │     └── Critical predictions → immediate notification             │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Flow 2: User Query / Chat Message

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER CHAT MESSAGE FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

  User types: "Motor chalana chahiye abhi?"
       │
       ▼
  ┌──────────────────────┐
  │  Next.js Frontend    │
  │  ChatInterface.tsx   │
  │                      │
  │  POST /v1/households/│
  │  {id}/chat/message   │
  └──────────┬───────────┘
             │  HTTPS + JWT
             ▼
  ┌──────────────────────┐
  │   FastAPI            │
  │   /api/v1/chat.py    │
  │                      │
  │  1. Validate JWT     │
  │  2. Extract           │
  │     household_id      │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   REASONING AGENT                                 │
  │                                                                   │
  │  1. Load HCO from Redis cache (or rebuild if expired)            │
  │                                                                   │
  │  2. Retrieve relevant memories:                                   │
  │     ├── Embed query via Titan                                     │
  │     └── pgvector search: household_memories                      │
  │                                                                   │
  │  3. Load top 5 active predictions                                 │
  │                                                                   │
  │  4. Build Claude prompt:                                          │
  │     ├── System: Gharji persona + household context                │
  │     ├── Memory context: relevant memories                         │
  │     ├── Active predictions                                        │
  │     └── User message                                              │
  │                                                                   │
  │  5. Claude Sonnet API call (AWS Bedrock)                         │
  │     └── Streaming response enabled                                │
  └──────────────────────────────────────────────────────────────────┘
             │
             │  Streaming response
             ▼
  ┌──────────────────────┐         ┌──────────────────────┐
  │   FastAPI            │         │   PostgreSQL          │
  │   SSE stream         │────────►│   INSERT INTO         │
  │   to client          │         │   chat_messages       │
  └──────────┬───────────┘         └──────────────────────┘
             │
             ▼ (streamed tokens)
  ┌──────────────────────┐
  │  Next.js Frontend    │
  │                      │
  │  Message appears     │
  │  word by word        │
  │  (streaming UI)      │
  └──────────────────────┘

  Response: "Haan, bilkul abhi chalao! Tank 38% hai aur..."
```

---

## Flow 3: What-If Simulation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WHAT-IF SIMULATION FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

  User configures scenario: "Power cut at 7:30pm"
       │
       ▼
  ┌──────────────────────┐
  │  Next.js             │
  │  SimulatorPage.tsx   │
  │                      │
  │  POST /simulator/run │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   SIMULATOR SERVICE                               │
  │                                                                   │
  │  1. Parse scenario → validate perturbation types                 │
  │                                                                   │
  │  2. FORK baseline state:                                          │
  │     └── Clone current twin state (PostgreSQL read)               │
  │         OR use specified historical snapshot                      │
  │                                                                   │
  │  3. Apply perturbations to cloned state                          │
  │     └── power_available = False at 19:30                         │
  │                                                                   │
  │  4. Forward Simulator loop (15-min ticks × duration):            │
  │     For each tick:                                                │
  │     ├── Advance time                                              │
  │     ├── Apply routine logic to sim state                          │
  │     ├── Propagate cascade rules                                   │
  │     ├── Track: disruptions, resource changes, anomalies           │
  │     └── Record tick snapshot to in-memory timeline               │
  │                                                                   │
  │  5. Analyze impact:                                               │
  │     ├── Compare simulated timeline vs baseline                    │
  │     ├── Identify disrupted routines                               │
  │     ├── Calculate resource depletion curves                       │
  │     └── Build cascade chain                                       │
  │                                                                   │
  │  6. Claude Sonnet reasoning:                                      │
  │     ├── Feed impact analysis to Bedrock                          │
  │     ├── Get plain-English narrative                               │
  │     ├── Get action plan                                           │
  │     └── Get risk flags                                            │
  │                                                                   │
  │  7. Store simulation_run in PostgreSQL                            │
  └──────────────────────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────┐
  │  Next.js             │
  │  SimulationResult.   │
  │  tsx                 │
  │                      │
  │  Render impact matrix│
  │  + action plan       │
  └──────────────────────┘
```

---

## Flow 4: Household Onboarding

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HOUSEHOLD ONBOARDING FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

  New user signs up
       │
       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   ONBOARDING WIZARD                               │
  │                   (Next.js multi-step form)                       │
  │                                                                   │
  │  Step 1: Household basics (name, city, home type)                │
  │  Step 2: Add family members (name, role, schedule)               │
  │  Step 3: Map rooms (type, count)                                  │
  │  Step 4: Add appliances (motor, geyser, AC, etc.)                │
  │  Step 5: Known routines (select from templates or describe)       │
  │  Step 6: Language & AI persona name                               │
  └──────────────────────────────────────────────────────────────────┘
       │  POST /households/{id}/onboard
       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   HOUSEHOLD SERVICE                               │
  │                                                                   │
  │  1. Create household record + members + rooms + appliances        │
  │  2. Load city-specific models (power cut, water supply)           │
  │  3. Apply routine templates for selected patterns                  │
  └──────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │               BACKGROUND: HISTORICAL SIMULATION                   │
  │                   (Async task — ~90 seconds)                      │
  │                                                                   │
  │  1. Simulate last 30 days of household activity                  │
  │     └── 43,200 state snapshots (1 per minute)                    │
  │                                                                   │
  │  2. Embed each snapshot summary via Titan                        │
  │     └── Batch embedding calls to Bedrock                         │
  │                                                                   │
  │  3. Extract initial patterns from simulation history             │
  │     └── Build initial household_memories (pgvector)              │
  │                                                                   │
  │  4. Generate first predictions                                    │
  │     └── ContextAgent → PredictionAgent → Store                   │
  │                                                                   │
  │  5. Mark household.twin_initialized = TRUE                        │
  └──────────────────────────────────────────────────────────────────┘
       │
       ▼
  Dashboard is live — predictions ready, twin populated
```

---

## Flow 5: Pattern Learning Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PATTERN LEARNING LOOP                             │
│                     (Continuous improvement)                         │
└─────────────────────────────────────────────────────────────────────┘

  Routine executes in the real world
       │
       ▼ (user confirms OR twin auto-detects)
  ┌──────────────────┐
  │  routine_        │
  │  executions      │
  │  INSERT          │
  └────────┬─────────┘
           │
           │  Weekly batch job (or on 10+ new executions)
           ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   PATTERN ANALYZER                                │
  │                                                                   │
  │  1. Pull last 90 days of routine executions                      │
  │  2. Compute statistics:                                           │
  │     ├── Mean, stddev of execution times by day_of_week           │
  │     ├── Festival-period deviations                               │
  │     ├── Seasonal patterns                                         │
  │     └── Correlation between routines                              │
  │  3. Identify new patterns not yet in memory                      │
  │  4. Update existing memories (increase observation_count)         │
  │  5. Deprecate stale patterns (not seen in 60+ days)              │
  └──────────────────────────────────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   MEMORY UPDATER                                  │
  │                                                                   │
  │  For each new/updated pattern:                                    │
  │  1. Generate natural language description                         │
  │     └── Claude Haiku (cost-efficient)                             │
  │  2. Embed description via Titan                                   │
  │  3. Upsert household_memories record                              │
  │  4. Update routines.pattern_embedding                             │
  └──────────────────────────────────────────────────────────────────┘
           │
           ▼
  Prediction engine now has richer context for future predictions
  → Accuracy improves over time (learning loop)
```

---

## Flow 6: Prediction Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                   PREDICTION FEEDBACK LOOP                           │
└─────────────────────────────────────────────────────────────────────┘

  Prediction displayed to user
       │
       ├── User acts on it → marks as "confirmed"
       ├── User dismisses it → marks as "not_helpful"
       └── Time passes, prediction expires → auto-evaluate
                                   │
                          (Did the event happen?)
                                   │
                    ┌──────────────┼────────────────┐
                    ▼              ▼                 ▼
               Accurate       Not accurate       Expired
                    │              │                 │
                    └──────────────┴─────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────┐
                    │  Accuracy score stored in         │
                    │  predictions.was_accurate         │
                    └──────────────────────────────────┘
                                   │
                     Weekly confidence recalibration:
                    ┌──────────────────────────────────┐
                    │  For each routine:               │
                    │  new_base_rate = EMA(accuracy,   │
                    │                    alpha=0.1)    │
                    │                                  │
                    │  Update routines.confidence_     │
                    │  score                           │
                    └──────────────────────────────────┘
```

---

## System-Wide Data Flow Summary

```
                        GHARMIND AI — DATA FLOWS

 ┌───────────────┐      ┌───────────────┐      ┌─────────────────┐
 │   INPUTS      │      │  PROCESSING   │      │    OUTPUTS      │
 │               │      │               │      │                 │
 │ User setup    │─────►│ Digital Twin  │─────►│ Twin state feed │
 │ City config   │      │ (1min ticks)  │      │ (WebSocket)     │
 │ Routines      │      │               │      │                 │
 │               │      ├───────────────┤      │ Prediction feed │
 │ Time (IST)    │─────►│ Context Engine│─────►│ (5min refresh)  │
 │ Festivals     │      │ (5min cycle)  │      │                 │
 │ Season        │      │               │      │ Gharji chat     │
 │               │      ├───────────────┤      │ (on demand)     │
 │ User queries  │─────►│ Reasoning     │─────►│                 │
 │ (chat)        │      │ Agent         │      │ What-If results │
 │               │      │               │      │ (on demand)     │
 │ Scenario      │─────►│ WhatIf Agent  │─────►│                 │
 │ (simulator)   │      │               │      │ Insights &      │
 │               │      ├───────────────┤      │ patterns        │
 │ Feedback      │─────►│ Pattern       │─────►│ (weekly)        │
 │ (prediction   │      │ Learner       │      │                 │
 │  ratings)     │      │               │      │                 │
 └───────────────┘      └───────────────┘      └─────────────────┘
                                │
                    ┌───────────┴────────────┐
                    │     AWS BEDROCK         │
                    │                         │
                    │  Claude 3 Sonnet        │
                    │  Titan Embeddings       │
                    └─────────────────────────┘
```
