# GHARMIND AI — What-If Simulator Design

---

## Overview

The What-If Simulator is GHARMIND AI's **household scenario planning engine**. It answers questions like:

> "What if we have a power cut during Diwali dinner?"
> "What if my daughter's JEE exam is tomorrow — how should the household adjust?"
> "What if guests arrive unexpectedly at 7pm?"
> "What if the water motor fails during monsoon season?"

The simulator takes the current or baseline household state, applies a set of perturbations (hypothetical changes), runs a forward simulation over a specified time window, and returns a detailed impact analysis.

This transforms GHARMIND from a reactive monitor into a **proactive household planning tool** — one of its most distinctive features.

---

## Simulator Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   WHAT-IF SIMULATOR                          │
│                                                              │
│  1. SCENARIO INTAKE                                          │
│     Natural language OR structured scenario definition       │
│     NLU: "power cut during dinner" → structured scenario     │
│                                                              │
│  2. BASELINE FORK                                            │
│     Clone current twin state (or any historical snapshot)    │
│     Create isolated simulation sandbox (no DB writes)        │
│                                                              │
│  3. PERTURBATION APPLIER                                     │
│     Apply what-if changes to cloned state                    │
│     e.g., set power_available = False at 19:30              │
│                                                              │
│  4. FORWARD SIMULATOR                                        │
│     Advance cloned state through time window                 │
│     Every 15-minute tick: apply routine logic, propagate     │
│     cascading effects                                         │
│                                                              │
│  5. IMPACT ANALYZER                                          │
│     Compare simulation outcome vs baseline outcome           │
│     Identify: disrupted routines, resource risks, member     │
│     impacts, required actions                                │
│                                                              │
│  6. CLAUDE REASONING LAYER                                   │
│     Feed impact analysis to Claude Sonnet                    │
│     Get: plain-English summary, recommendations, risk flags  │
│                                                              │
│  7. RESULT PRESENTATION                                      │
│     Structured result object returned to frontend            │
│     Rendered as impact matrix + narrative                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Perturbation Types

```python
PERTURBATION_CATALOG = {

    # Resource perturbations
    "power_cut": {
        "params": ["start_time", "duration_hours", "affects_inverter"],
        "description": "Simulates power grid failure",
        "cascade": ["inverter_drain", "no_wifi", "fridge_off_after_2h", "motor_stops"]
    },
    "water_shortage": {
        "params": ["severity", "duration_hours"],
        "description": "Municipal water supply failure or motor failure",
        "cascade": ["no_motor", "tank_drain_only", "morning_panic"]
    },
    "internet_outage": {
        "params": ["start_time", "duration_hours"],
        "description": "ISP failure or WiFi router issue",
        "cascade": ["wfh_disruption", "no_streaming", "mobile_data_fallback"]
    },

    # Event perturbations
    "unexpected_guest": {
        "params": ["arrival_time", "count", "duration_hours"],
        "description": "Unplanned guest arrival",
        "cascade": ["extra_cooking", "room_preparation", "extra_water", "chai_rounds"]
    },
    "member_absent": {
        "params": ["member_id", "start_time", "duration"],
        "description": "Family member unexpectedly absent",
        "cascade": ["dependent_routines_shift", "meals_adjust", "tasks_redistribute"]
    },
    "member_sick": {
        "params": ["member_id", "severity"],
        "description": "Family member falls ill",
        "cascade": ["caregiver_routines", "quiet_mode", "medical_supplies", "school_skip"]
    },

    # Contextual perturbations
    "exam_week": {
        "params": ["member_id", "exam_type", "start_date", "end_date"],
        "description": "Competitive exam period begins",
        "cascade": ["quiet_hours_extended", "schedule_rigidity", "screen_time_limit"]
    },
    "festival_tomorrow": {
        "params": ["festival_name"],
        "description": "Major festival is tomorrow",
        "cascade": ["extended_prep", "shopping", "cooking_surge", "guest_high_probability"]
    },
    "school_holiday": {
        "params": ["duration_days"],
        "description": "School unexpectedly closed",
        "cascade": ["child_home_all_day", "routine_shift", "lunch_at_home"]
    },

    # Infrastructure perturbations
    "motor_failure": {
        "params": ["failure_type"],
        "description": "Water motor fails to start",
        "cascade": ["manual_water_management", "tank_drain_only", "urgency_spike"]
    },
    "gas_cylinder_empty": {
        "params": ["discovery_time"],
        "description": "Cooking gas runs out",
        "cascade": ["meal_disruption", "reorder_needed", "induction_fallback"]
    }
}
```

---

## Scenario Definitions

### Built-In Scenarios (Demo-Ready)

#### Scenario 1: Power Cut During Diwali Dinner
```json
{
  "scenario_id": "s001",
  "name": "Power Cut During Diwali Dinner",
  "description": "MSEDCL load shedding starts at 7:30pm on Diwali evening",
  "perturbations": [
    {
      "type": "power_cut",
      "start_time": "19:30",
      "duration_hours": 1.5,
      "affects_inverter": false
    }
  ],
  "sim_start": "17:00",
  "sim_duration_hours": 8,
  "expected_impacts": [
    "Dinner cooking must complete by 7:15pm",
    "Diwali lights on inverter — limited capacity",
    "Children's firecrackers window shortened",
    "Fridge preservation concern if cut extends"
  ]
}
```

#### Scenario 2: JEE Mains Tomorrow
```json
{
  "scenario_id": "s002",
  "name": "JEE Mains Tomorrow",
  "description": "Priya's JEE Mains exam is tomorrow at 9am",
  "perturbations": [
    {
      "type": "exam_week",
      "member_id": "priya_id",
      "exam_type": "JEE_Mains",
      "start_date": "tomorrow",
      "intensity": "critical"
    }
  ],
  "sim_start": "today_18:00",
  "sim_duration_hours": 16,
  "expected_impacts": [
    "Study session 7pm-11pm — quiet enforced",
    "Early wake at 6am — all alarms set",
    "Mother prepares exam-day meal plan",
    "Father drops Priya at center by 8:30am",
    "Household in support mode all day"
  ]
}
```

#### Scenario 3: Unexpected Guests on Sunday
```json
{
  "scenario_id": "s003",
  "name": "Unexpected Guests Sunday 4pm",
  "description": "Rahul's friends call to visit at 4pm with families (8 people)",
  "perturbations": [
    {
      "type": "unexpected_guest",
      "arrival_time": "16:00",
      "count": 8,
      "duration_hours": 4,
      "includes_children": true
    }
  ],
  "sim_start": "14:00",
  "sim_duration_hours": 8,
  "expected_impacts": [
    "Extra snack prep starting 3pm",
    "Living room needs immediate cleaning",
    "Chai for 12 people at arrival",
    "Dinner quantity doubled",
    "Children creating noise — study time lost"
  ]
}
```

#### Scenario 4: Water Motor Failure in Summer
```json
{
  "scenario_id": "s004",
  "name": "Motor Fails — Summer Peak",
  "description": "Water motor doesn't start on a 40°C May morning",
  "perturbations": [
    {
      "type": "motor_failure",
      "failure_type": "mechanical",
      "time": "06:10"
    },
    {
      "type": "season_context",
      "season": "peak_summer",
      "temperature_c": 40
    }
  ],
  "sim_start": "06:00",
  "sim_duration_hours": 12,
  "expected_impacts": [
    "Tank at 35% — will last 4-5 hours at summer usage",
    "Call plumber immediately (before 10am)",
    "Reduce water usage: skip laundry, quick showers only",
    "Crisis by 11am if not resolved",
    "Order water tanker if no repair by noon"
  ]
}
```

---

## Forward Simulation Engine

```python
class ForwardSimulator:
    """
    Advances cloned household state through time window,
    applying routine logic and cascade effects.
    """

    TICK_MINUTES = 15  # 15-minute simulation resolution

    async def run(
        self,
        baseline_state: HouseholdTwinState,
        perturbations: list[Perturbation],
        start_time: datetime,
        duration_hours: int
    ) -> SimulationResult:

        # Fork the baseline state
        sim_state = deepcopy(baseline_state)

        # Apply perturbations to forked state
        sim_state = self.perturbation_applier.apply(sim_state, perturbations)

        # Run simulation ticks
        timeline = []
        current_time = start_time

        while current_time < start_time + timedelta(hours=duration_hours):
            # Advance state by one tick
            tick_result = self._advance_tick(sim_state, current_time)

            # Record state snapshot
            timeline.append({
                "time": current_time.isoformat(),
                "state": sim_state.to_dict(),
                "events": tick_result.events,
                "anomalies": tick_result.anomalies
            })

            # Propagate cascade effects
            sim_state = self._apply_cascades(sim_state, tick_result)

            current_time += timedelta(minutes=self.TICK_MINUTES)

        # Run impact analysis
        impact = await self._analyze_impact(timeline, baseline_state)

        # Get Claude narrative
        narrative = await self._generate_narrative(impact, perturbations)

        return SimulationResult(
            timeline=timeline,
            impact=impact,
            narrative=narrative,
            risk_flags=self._extract_risks(timeline),
            recommendations=narrative.recommendations
        )

    def _advance_tick(
        self, state: HouseholdTwinState, tick_time: datetime
    ) -> TickResult:
        events = []
        anomalies = []

        # Check routine triggers
        for routine in state.active_routines:
            if self._should_trigger(routine, tick_time, state):
                events.append(RoutineStartEvent(routine, tick_time))
                state = self._apply_routine_start(state, routine)

        # Check resource changes
        state = self.water_model.advance(state, self.TICK_MINUTES)
        state = self.power_model.advance(state, tick_time)

        # Apply cascade effects from active perturbations
        state = self._apply_active_cascades(state, tick_time)

        # Detect anomalies
        anomalies = self._detect_anomalies(state, tick_time)

        return TickResult(state=state, events=events, anomalies=anomalies)
```

---

## Impact Analysis Model

```python
@dataclass
class ImpactAnalysis:
    """
    Structured impact analysis comparing baseline vs simulated outcome.
    """

    # Routine impacts
    disrupted_routines: list[RoutineImpact]
    # e.g., [{"routine": "Dinner Prep", "impact": "delayed 45 min", "severity": "high"}]

    # Resource impacts
    resource_impacts: list[ResourceImpact]
    # e.g., [{"resource": "water", "impact": "tank critical by 11am", "severity": "critical"}]

    # Member impacts
    member_impacts: list[MemberImpact]
    # e.g., [{"member": "Priya", "impact": "study disrupted 2 hours", "severity": "medium"}]

    # Cascade chain
    cascade_chain: list[str]
    # e.g., ["Power cut → WiFi off → Rahul's Zoom cut → WFH disrupted → Dinner rushed"]

    # Overall severity
    overall_severity: str  # minimal, moderate, significant, critical

    # Action urgency score
    action_urgency: int  # 0-100

    # Time-critical windows
    critical_windows: list[TimeWindow]
    # Windows where household must act or consequences worsen


@dataclass
class RoutineImpact:
    routine_name: str
    baseline_time: str
    simulated_time: str
    deviation_mins: int
    impact_description: str
    severity: str  # none, low, medium, high, critical
    mitigation: str
```

---

## Claude Simulation Prompt

```
You are the WhatIfAgent for GHARMIND AI.

HOUSEHOLD: {household_name}, {city}
FAMILY: {member_summary}
BASELINE STATE: {baseline_state_summary}

WHAT-IF SCENARIO: {scenario_description}
PERTURBATIONS APPLIED: {perturbations_summary}

SIMULATION RESULTS:
Timeline: {timeline_summary}
Disrupted Routines: {disrupted_routines_json}
Resource Impacts: {resource_impacts_json}
Cascade Chain: {cascade_chain}

Please provide:
1. A plain English summary (3-4 sentences) of what happens to this family if this scenario occurs
2. The top 3 risks they should be aware of
3. A step-by-step preparation plan if they want to minimize disruption
4. Any silver linings or opportunities in this scenario

Language: {language_preference}
Tone: Practical, warm, actionable. Like advice from a knowledgeable family friend.
```

---

## Simulator UI Design (Frontend)

### Scenario Builder Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🔮 What-If Simulator                                        │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  "What if..." ___________________________________    │    │
│  │               power cut at 7:30pm tonight            │    │
│  └─────────────────────────────────────────────────────┘    │
│  [OR choose a scenario]                                      │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │⚡ Power  │ │💧 Water  │ │👥 Guests │ │📚 Exams  │       │
│  │   Cut    │ │ Shortage │ │ Arrive   │ │  Week    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │🎉 Fest.  │ │😷 Sick   │ │🔧 Motor  │ │🛢️ Gas    │       │
│  │  Tomorrow│ │ Member   │ │  Broken  │ │  Empty   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│         [▶ RUN SIMULATION]                                   │
└─────────────────────────────────────────────────────────────┘
```

### Simulation Result Display

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Simulation Result: Power Cut During Diwali Dinner        │
│                                                              │
│  ⚠️ OVERALL IMPACT: SIGNIFICANT                             │
│                                                              │
│  Gharji says:                                                │
│  "Agar aaj 7:30 baje light gayi, toh dinner 7:15 tak        │
│   complete karna padega. Diwali lights inverter pe chalenge  │
│   — 3 ghante backup. Priya ki puja ka diwa jala rakho."     │
│                                                              │
│  📋 IMPACT MATRIX                                            │
│  ┌────────────────┬────────────┬───────────┬──────────────┐ │
│  │ Routine        │ Baseline   │ With Cut  │ Severity     │ │
│  ├────────────────┼────────────┼───────────┼──────────────┤ │
│  │ Dinner Prep    │ 8:00pm     │ 7:00pm ⬆️ │ 🔴 High     │ │
│  │ Evening Aarti  │ 7:15pm     │ ✓ On time │ 🟢 None     │ │
│  │ Diwali Lights  │ All night  │ Inverter  │ 🟡 Medium   │ │
│  │ Kids Firecrac. │ 8-9pm      │ Curtailed │ 🟡 Medium   │ │
│  │ Fridge Safety  │ N/A        │ Monitor   │ 🟡 Medium   │ │
│  └────────────────┴────────────┴───────────┴──────────────┘ │
│                                                              │
│  🎯 ACTION PLAN                                              │
│  6:30pm  Charge all devices (phones, tablets)               │
│  7:00pm  Dinner cooking must START now                       │
│  7:15pm  Dinner must be served (before cut)                 │
│  7:25pm  Switch all lights to inverter                      │
│  7:30pm  Expected power cut                                  │
│                                                              │
│  [SAVE PLAN] [SHARE WITH FAMILY] [SET REMINDERS]            │
└─────────────────────────────────────────────────────────────┘
```

---

## What-If Cascade Rules

```python
CASCADE_RULES = {
    "power_cut": [
        Rule("wifi_router.off", "when power_cut starts"),
        Rule("wfh_disruption", "if work_hours AND internet needed"),
        Rule("inverter.on", "if inverter_available"),
        Rule("inverter.drain_rate_increase", "proportional to load"),
        Rule("motor.off", "immediately on power cut"),
        Rule("cooking.disrupted", "if induction only AND no gas"),
        Rule("fridge.temperature_rise", "after 4 hours without power"),
    ],
    "water_shortage": [
        Rule("motor.ineffective", "when water_shortage is True"),
        Rule("tank_drain_only", "no refill possible"),
        Rule("morning_panic", "if tank < 20% AND school_day"),
        Rule("laundry.postpone", "automatically"),
        Rule("showers.limit", "alert sent"),
    ],
    "unexpected_guest_8": [
        Rule("kitchen.activity_increase", "x1.8 from arrival-2h"),
        Rule("water_usage.increase", "x1.5"),
        Rule("living_room.occupied", "for guest duration"),
        Rule("study.disrupted", "if guests include children"),
        Rule("noise_level.elevated", "during guest hours"),
    ]
}
```

---

## Simulator Performance Requirements

| Metric | Target |
|---|---|
| Scenario parse time | < 200ms |
| 24-hour simulation execution | < 3 seconds |
| Claude narrative generation | < 2 seconds |
| Total What-If response time | < 6 seconds |
| Concurrent simulations per user | Up to 3 |
| Simulation result storage | 30 days |
