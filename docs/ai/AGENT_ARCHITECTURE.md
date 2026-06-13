# GHARMIND AI — Agent Architecture
## Multi-Agent System Design

---

## Overview

GHARMIND AI uses a **cooperative multi-agent architecture** powered by AWS Bedrock. Rather than one monolithic AI, three specialized agents collaborate through a central orchestrator — each with a distinct cognitive role.

This mirrors how a household actually functions: different people have different expertise (the person who knows the water schedule, the one who tracks school routines, the one who plans for festivals). GHARMIND's agents work the same way.

---

## Agent Architecture Diagram

```
                    ┌──────────────────────────────────────┐
                    │         Agent Orchestrator            │
                    │  (Routes context → agents → actions)  │
                    └───────┬──────────┬──────────┬────────┘
                            │          │          │
              ┌─────────────▼──┐  ┌────▼──────┐  ┌▼─────────────────┐
              │  ContextAgent  │  │ Prediction│  │  ReasoningAgent  │
              │                │  │  Agent    │  │                  │
              │ "What is       │  │           │  │ "Why? What-If?   │
              │  happening     │  │ "What     │  │  Explain?"       │
              │  right now?"   │  │  will     │  │                  │
              │                │  │  happen?" │  │ Claude Sonnet    │
              │ Context Graph  │  │           │  │ Deep Reasoning   │
              │ Builder        │  │ Pattern   │  │ Conversation     │
              │                │  │ Matcher   │  │ What-If Engine   │
              └────────┬───────┘  └─────┬─────┘  └────────┬─────────┘
                       │                │                   │
                       └────────────────┴───────────────────┘
                                        │
                              ┌─────────▼──────────┐
                              │   WhatIfAgent       │
                              │                     │
                              │ "Simulate alternate │
                              │  household states"  │
                              │                     │
                              │ Scenario Runner     │
                              │ Impact Analyzer     │
                              └─────────────────────┘
```

---

## Agent 1: ContextAgent

### Role
The ContextAgent is the **situational awareness engine**. It continuously assembles a rich, structured understanding of what is happening in the household right now — synthesizing the Digital Twin state, calendar context, family member status, and long-term memory.

### Responsibilities
- Read the latest twin state snapshot
- Identify active festivals, exam periods, or special events
- Determine which family members are home, their activities, and emotional context
- Query pgvector memory for relevant historical patterns
- Produce a **Household Context Object (HCO)** — a structured JSON + natural language summary

### Input → Output

**Input:**
```json
{
  "twin_snapshot": { ... },        // Latest household twin state
  "calendar_context": {
    "ist_now": "2024-10-28T06:15:00+05:30",
    "day_of_week": "Monday",
    "festivals_active": ["Diwali Prep Week"],
    "is_holiday": false,
    "season": "winter_onset"
  },
  "recent_executions": [ ... ],    // Last 3 routine executions
  "memory_query_results": [ ... ]  // Relevant pgvector memories
}
```

**Output (Household Context Object):**
```json
{
  "context_id": "uuid",
  "generated_at": "2024-10-28T06:15:05+05:30",
  "phase_of_day": "early_morning",
  "household_mood": "festive_preparation",
  "active_routines": ["morning_pooja", "school_prep"],
  "imminent_routines": ["water_motor", "chai"],
  "key_members": {
    "Anjali (Mother)": "in_kitchen_preparing_pooja",
    "Rahul (Father)": "asleep",
    "Priya (Daughter)": "getting_ready_school"
  },
  "contextual_flags": [
    "diwali_prep_week",
    "exam_week_starts_tomorrow",
    "water_motor_overdue_15min",
    "power_cut_forecast_evening"
  ],
  "summary": "Festive Monday morning. Diwali prep begins today. Anjali is doing extended morning pooja — motor needs to run soon. Priya has school despite upcoming exams. Power cut expected at 7:30pm.",
  "urgency_score": 72
}
```

### Bedrock Call
- **Model**: `amazon.titan-embed-text-v1` for embedding the context summary
- **pgvector query**: Find top-5 most similar past mornings to build prediction confidence

---

## Agent 2: PredictionAgent

### Role
The PredictionAgent is the **foresight engine**. Given the Household Context Object, it generates a prioritized list of predictions about what will happen in the next 2 hours, today, and this week.

### Responsibilities
- Analyze HCO for predictable near-term events
- Cross-reference with routine schedules and historical deviation patterns
- Generate ranked predictions with confidence scores
- Assign actionable suggestions to each prediction
- Identify anomalies (routine that should have happened but didn't)

### Prediction Generation Process

```
1. SCAN — What routines are due in the next 2 hours?
2. COMPARE — How similar is today's context to historical same-time contexts?
3. FACTOR — Apply contextual multipliers (festival, season, holiday)
4. SCORE — Assign confidence based on historical accuracy
5. ENRICH — Generate action suggestion via Claude Sonnet mini-call
6. RANK — Sort by (priority × confidence × time_urgency)
7. STORE — Save to predictions table with evidence trail
```

### Confidence Model

```
base_confidence = historical_occurrence_rate(routine, day_of_week, time_window)
                                                    ↓
festival_multiplier = if festival_active: apply_festival_behavior_model(festival)
                                                    ↓
deviation_penalty = 1.0 - (avg_deviation_mins / 120)  # Penalize unpredictable routines
                                                    ↓
recency_bonus = if last_executed_within_24h: +0.1
                                                    ↓
final_confidence = clip(base_confidence × festival_multiplier × deviation_penalty + recency_bonus, 0.05, 0.99)
```

### Sample Predictions Output

```json
[
  {
    "type": "routine_start",
    "title": "Water Motor — Run Now",
    "predicted_for": "06:30 IST",
    "confidence": 0.94,
    "priority": "critical",
    "action": "Start motor now. Tank level is low. School rush begins at 7:15am.",
    "evidence": ["Ran at 06:20 yesterday", "06:15 avg across last 14 Mondays", "Diwali: +30% water usage this week"]
  },
  {
    "type": "festival_prep",
    "title": "Extended Morning Pooja",
    "predicted_for": "06:15–07:00 IST",
    "confidence": 0.88,
    "priority": "high",
    "action": "Pooja room is occupied. Delay loud appliances until 7am.",
    "evidence": ["Diwali Prep Week active", "Anjali in pooja room", "Pattern: 45-min pooja during festival weeks"]
  },
  {
    "type": "power_event",
    "title": "Load Shedding Expected",
    "predicted_for": "19:30–20:30 IST",
    "confidence": 0.79,
    "priority": "normal",
    "action": "Charge devices before 7pm. Dinner prep should complete before 7:30pm.",
    "evidence": ["Mon/Tue 7:30pm cut for 14 of last 20 weeks", "MSEDCL schedule pattern"]
  }
]
```

### Bedrock Call
- **Model**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Purpose**: Enrich raw predictions with natural language action suggestions and reasoning
- **Token budget**: ~500 tokens per prediction enrichment call
- **Optimization**: Batch up to 5 predictions per Claude call

---

## Agent 3: ReasoningAgent

### Role
The ReasoningAgent is the **deep intelligence core**. It handles complex reasoning tasks that require multi-step thinking: natural language conversation with the household, explanation of predictions, and complex What-If reasoning.

### Responsibilities
- Handle natural language queries from family members ("Why does Gharji say to run the motor now?")
- Explain prediction reasoning in simple, friendly language (Hindi/English/Hinglish)
- Handle complex household planning questions ("How should we prepare for Ganesh Chaturthi this year?")
- Serve as the fallback for anything the other agents cannot handle

### System Prompt Design

```
You are Gharji, the AI household companion for the {household_name} family in {city}.

You speak {language_preference} and understand Indian household rhythms deeply.

You know:
- The family members: {member_summary}
- Current household context: {hco_summary}
- Active routines: {active_routines}
- Upcoming predictions: {top_5_predictions}
- Recent household memories: {relevant_memories}

Your personality:
- Warm, helpful, like a knowledgeable family member
- Proactive: you tell people things before they ask
- Culturally aware: you respect pooja, festivals, quiet hours
- Practical: your advice is always actionable

Always respond in {language_preference}. Be concise. Use household-specific context.
```

### Conversation Capability Examples

| User Query | Agent Response |
|---|---|
| "Gharji, should I run the motor now?" | "Haan, abhi chalao! Tank 40% hai, aur 7:15 par Priya ka school bus hai. Diwali week mein paani zyada lagta hai." |
| "Why are you alerting about power cut?" | "Monday evenings mein MSEDCL ka pattern hai 7:30 baje. Last 3 hafte mein hua bhi. Dinner 7 baje tak ready kar lo." |
| "Plan this Diwali for me" | Returns a full Diwali preparation plan with day-by-day household activity schedule |

---

## Agent 4: WhatIfAgent

### Role
The WhatIfAgent is the **scenario simulation engine**. It takes a user-defined "what if" scenario, applies perturbations to the Digital Twin state, runs a forward simulation, and explains the impact.

### Responsibilities
- Accept scenario definitions (natural language or structured)
- Apply perturbations to a cloned twin state
- Simulate household behavior over the specified window
- Identify which routines are impacted and how
- Generate risk flags and mitigation recommendations

### Detailed design in: [`WHATIF_SIMULATOR.md`](../simulator/WHATIF_SIMULATOR.md)

---

## Agent Orchestrator

### Role
The Orchestrator coordinates the multi-agent pipeline on every tick and on demand.

### Orchestration Logic

```
ON TIMER (every 5 minutes):
    1. TwinEngine.snapshot() → twin_state
    2. ContextAgent.build(twin_state) → hco
    3. PredictionAgent.generate(hco) → predictions
    4. Store predictions in DB
    5. Emit WebSocket event to connected dashboards
    6. Evaluate notification triggers

ON USER QUERY:
    1. Classify query type (conversation / whatif / explanation)
    2. Route to ReasoningAgent or WhatIfAgent
    3. Inject current HCO + relevant memories as context
    4. Stream response back to user

ON ROUTINE_ANOMALY:
    1. ContextAgent detects missed/early routine
    2. PredictionAgent recalculates downstream impacts
    3. ReasoningAgent generates proactive alert
    4. NotificationEngine delivers alert
```

---

## Agent State & Memory Model

```
┌─────────────────────────────────────────────────────────┐
│                   AGENT MEMORY LAYERS                   │
├─────────────────┬───────────────────┬───────────────────┤
│  WORKING MEMORY │  SHORT-TERM MEM   │  LONG-TERM MEM    │
│                 │                   │                   │
│ Current HCO     │ Last 24h events   │ pgvector memories │
│ Active predict. │ This week patterns│ Festival patterns │
│ Conversation    │ Recent anomalies  │ Seasonal behav.   │
│ context         │                   │ Learned prefs     │
│                 │                   │                   │
│ Redis (TTL 5m)  │ PostgreSQL (7d)   │ pgvector (forever)│
└─────────────────┴───────────────────┴───────────────────┘
```

---

## Bedrock Model Configuration

| Agent | Model | Use Case | Avg Latency |
|---|---|---|---|
| ContextAgent | Titan Embed Text v1 | Context embedding | ~100ms |
| PredictionAgent | Claude 3 Sonnet | Prediction enrichment | ~800ms |
| ReasoningAgent | Claude 3 Sonnet | Deep reasoning, conversation | ~1.5s |
| WhatIfAgent | Claude 3 Sonnet | Scenario simulation | ~2s |

---

## Agent Invocation Rate (Per Household)

| Agent | Frequency | Trigger |
|---|---|---|
| ContextAgent | Every 5 minutes | Timer |
| PredictionAgent | Every 5 minutes | After ContextAgent |
| ReasoningAgent | On demand | User query |
| WhatIfAgent | On demand | User What-If request |

---

## Cost Optimization Strategy

1. **Caching**: ContextAgent results cached for 5 minutes in Redis
2. **Batching**: PredictionAgent batches 5 predictions per Claude call
3. **Tiered invocation**: Background timer runs light models; user queries run full Claude
4. **Embedding reuse**: Twin snapshot embeddings computed once, stored permanently
5. **Lazy reasoning**: ReasoningAgent only invoked when user asks; summaries pre-computed
