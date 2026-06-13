# GHARMIND AI — Amazon HackOn 5-Minute Demo Script
## "Your Home Doesn't Need Commands. It Needs to Understand You."

---

## Demo Setup

| Parameter | Value |
|---|---|
| **Total runtime** | 5 minutes 00 seconds |
| **Household** | Sharma Residence, Kothrud, Pune, Maharashtra |
| **Demo date/time** | Friday, October 25, 2024 — 06:08 IST |
| **Context** | Diwali is in 3 days. Priya's JEE mock exam is Monday. |
| **Presenter note** | Speak in a calm, confident pace. Let the AI moments breathe — silence after a Gharji response is intentional. That's the magic. |

---

## Pre-Demo Checklist

- [ ] Browser open on `http://localhost:3000` — Sharma dashboard loaded
- [ ] Dashboard showing: 06:08am, Friday, Diwali Prep Day 2
- [ ] Twin state: Motor overdue 8 mins, Geyser ON, Dadi in Pooja Room, Rahul sleeping
- [ ] Predictions panel: 3 pending (motor critical, school bus high, Diwali prep normal)
- [ ] What-If simulator tab preloaded and ready
- [ ] Chat/Gharji panel ready on second monitor or browser tab
- [ ] MSEDCL power cut pattern seeded (Fri 7:30pm, historical)

---

# ═══════════════════════════════════════════
# MINUTE 0:00 — 0:45 | THE HOOK
# "The Problem Is Real"
# ═══════════════════════════════════════════

**[PRESENTER SPEAKS — no demo action yet]**

> "Every morning, 300 million Indian households wake up and manage the same invisible checklist.
> Did someone run the water motor? Will there be power tonight?
> Is the geyser off? Priya's school bus is in 45 minutes.
> Diwali is in 3 days.
>
> No smart speaker in the world knows any of this.
> Alexa doesn't know about your MSEDCL schedule.
> Google Home has no idea Diwali prep means 40% more water.
> They wait for commands. They don't think ahead.
>
> We built something different.
> GHARMIND AI — India's First Household Operating System.
> It doesn't wait. It anticipates."

**[Click: Show the dashboard for the first time]**

---

# ═══════════════════════════════════════════
# MINUTE 0:45 — 1:30 | THE DIGITAL TWIN
# "Your Home Is Already Alive"
# ═══════════════════════════════════════════

**[SCREEN: Main Dashboard — Sharma Residence]**

```
╔══════════════════════════════════════════════════════════════╗
║  🏠 SHARMA RESIDENCE           06:08 IST · Friday           ║
║  Kothrud, Pune                 🪔 Diwali in 3 Days          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   HOUSEHOLD MOOD RING                                        ║
║                                                              ║
║         ╭─────────────────╮                                  ║
║        ╱   ░░░░░░░░░░░░░   ╲  ← Amber pulse                 ║
║       │   SHARMA RESIDENCE   │    (Festive-Alert)           ║
║       │     Urgency: 68      │                              ║
║        ╲   ░░░░░░░░░░░░░   ╱                                ║
║         ╰─────────────────╯                                  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  📍 RIGHT NOW — LIVE TWIN STATE                              ║
║                                                              ║
║  Dadi     ──── Pooja Room      [Morning Aarti]  🪔          ║
║  Anjali   ──── Kitchen         [Chai prep]       ☕          ║
║  Rahul    ──── Master Bedroom  [Sleeping]         😴         ║
║  Priya    ──── Bedroom 2       [Getting ready]   📚          ║
║                                                              ║
║  💧 Water Motor    OFF   ⚠️ OVERDUE 8 MINS                  ║
║  🔥 Geyser         ON    Running 3 mins                      ║
║  ❄️  AC             OFF                                      ║
║  📡 WiFi           ON    Stable                             ║
║  🔋 Power Grid     STABLE  ─ Cut risk: tonight 7:30pm        ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER SPEAKS while pointing to screen]**

> "This is the Household Digital Twin. No sensors. No hardware. No IoT.
>
> Purely software — it knows Dadi wakes at 4:30am, so right now she's in the Pooja Room.
> It knows Anjali makes chai before 7am on Fridays.
> It knows Priya needs to leave in 67 minutes.
> It knows the water motor hasn't run yet — and that's a problem.
>
> Watch the urgency ring — it's amber. The house is in festive-alert mode.
> Three days before Diwali, water usage spikes 40%.
> The AI already knows this."

**[Pause 2 seconds — let the audience absorb the live Twin visualization]**

---

# ═══════════════════════════════════════════
# MINUTE 1:30 — 2:15 | THE PREDICTION ENGINE
# "AI That Thinks 6 Hours Ahead"
# ═══════════════════════════════════════════

**[Click: Predictions tab]**

```
╔══════════════════════════════════════════════════════════════╗
║  ⚡ PREDICTION FEED — Sharma Residence                       ║
║  Generated: 06:08 IST · Next refresh: 06:13 IST             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🔴 CRITICAL  ──────────────────── NOW                       ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │  💧 Water Motor — Run Immediately                    │   ║
║  │                                                      │   ║
║  │  Tank at 38%. Motor overdue 8 minutes.              │   ║
║  │  School bus in 67 minutes. Diwali week: +40%        │   ║
║  │  water usage. If not run NOW, tank hits 20%         │   ║
║  │  by 8am — CRITICAL threshold.                       │   ║
║  │                                                      │   ║
║  │  Gharji: "Anjali, motor abhi chalao! 🚨"            │   ║
║  │                                                      │   ║
║  │  Confidence: ████████████████████░  94%             │   ║
║  │  Evidence: 14 Fridays / 3 Diwali weeks / tank data  │   ║
║  │                          [✓ Done] [⏰ 5 min]        │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  🟠 HIGH  ───────────────────── 07:15 IST (67 min)          ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │  🚌 Priya's School Bus                               │   ║
║  │  Breakfast must be served by 6:55am.                │   ║
║  │  Bag check by 7:05am. Confidence: 95%               │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  🟠 HIGH  ───────────────────── 10:00 IST                   ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │  💼 Rahul's Zoom Call — Quiet Mode Required          │   ║
║  │  WFH Friday (pattern: 91% consistent).              │   ║
║  │  Living room noise must stay low 9:45–10:45am.      │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  🟡 NORMAL  ─────────────────── 16:30 IST                   ║
║  ☕ Evening chai + Diwali snack prep begins                  ║
║     JEE mock exam on Monday — Priya's last free evening     ║
║                                                              ║
║  🟡 NORMAL  ─────────────────── 17:30 IST                   ║
║  ⚡ Load shedding expected 7:30pm (MSEDCL Fri pattern)       ║
║     79% confidence · 3 of last 4 Fridays confirmed          ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER SPEAKS]**

> "This is the Prediction Engine. It's not a calendar. It didn't read a schedule.
>
> It learned. Fourteen consecutive Fridays of water motor data.
> Cross-referenced with: Diwali week water usage multiplier, Priya's school departure,
> and the tank level right now.
>
> It produces one output: *Run the motor. Now. Here's exactly why.*
>
> Not a notification after the tank runs out.
> Not a reminder at a fixed time.
> A context-aware, evidence-backed, proactive instruction — 8 minutes before the problem becomes a crisis.
>
> Notice it also sees this evening. Power cut at 7:30pm with 79% confidence.
> It knows the MSEDCL schedule for this zone in Pune.
> That prediction is already queued."

**[Hover over the 94% confidence bar — show the evidence trail popup]**

```
Evidence Trail:
  ✓ Motor ran between 06:00-06:30 on 14/14 Fridays (last 3.5 months)
  ✓ Tank was below 45% on 11/14 of those mornings
  ✓ Diwali week context: water_usage_multiplier = 1.40 active
  ✓ Similar past morning (Oct 18, similarity 0.94): motor ran at 06:12
  ✓ School bus at 07:15 — 67 min window closing
  ─────────────────────────────────────────────
  Final confidence: 94%   Priority: CRITICAL
```

**[PRESENTER]**
> "Every prediction shows its work. This is AI you can trust — not a black box."

---

# ═══════════════════════════════════════════
# MINUTE 2:15 — 2:50 | THE AI REASONING
# "Gharji Speaks — Hinglish, Context, Culture"
# ═══════════════════════════════════════════

**[Click: Chat / Gharji tab]**
**[Type — visibly, slowly so audience can read it being typed]:**

```
User types: "Gharji, aaj Diwali ki taiyari kaise karein?"
           ("Gharji, how should we prepare for Diwali today?")
```

**[PRESENTER while Claude call is processing — ~1.5 seconds]**
> "This is a live call to AWS Bedrock — Claude 3 Sonnet.
> The model receives the full household context: who's home, what's pending,
> what the festival calendar says, what memories we've learned about this family.
> Watch."

**[Gharji response streams in — tokens appear word by word]**

```
╔══════════════════════════════════════════════════════════════╗
║  💬 GHARJI                                        06:09 IST  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Anjali ji, Diwali 3 din baad hai — aaj se planning         ║
║  karo toh stress-free rahega! 🪔                            ║
║                                                              ║
║  AAJ (Friday) — Sabse pehle:                                 ║
║  • Motor ABHI chalao (tank 38% hai!)                        ║
║  • Sham ko 5 baje: Decoration shopping — Rahul              ║
║    WFH hai toh usse saath le jao                            ║
║  • Pooja ki thali ki samagri check karo                     ║
║                                                              ║
║  LEKIN ek important baat:                                    ║
║  Aaj sham 7:30 baje light jaane ka chance 79% hai.          ║
║  Raat ka khaana 7 baje tak ready karo.                      ║
║  Decoration shopping 6:30 se pehle wapas aao.              ║
║                                                              ║
║  Priya ka JEE mock Monday hai — Friday evening uski         ║
║  study ke liye protect karo. TV band rakho 5-9pm.           ║
║                                                              ║
║  SAT: Mithai banao (ghee, sugar — kya stock hai?)           ║
║  SUN: Final safai + decoration setup                         ║
║  MON: Diwali! Pooja 5:30am — extended (I'll remind you)     ║
║                                                              ║
║  Sab theek ho jayega. 🪔✨                                  ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER — speaking during the streaming response]**

> "It's not reading from a script. It's reasoning.
>
> It cross-referenced: Diwali 3 days away, Priya's JEE exam Monday, tonight's power cut risk,
> Rahul's WFH status, the motor emergency right now, and it built a coherent family plan —
> in Hinglish, the way Anjali actually thinks.
>
> No other AI product in the world does this for an Indian household.
> This is what we mean by an Operating System."

---

# ═══════════════════════════════════════════
# MINUTE 2:50 — 3:50 | THE WHAT-IF ENGINE
# "Simulate Before It Happens"
# ═══════════════════════════════════════════

**[Click: What-If Simulator tab]**

**[PRESENTER]**
> "Now let's show the most powerful feature — the What-If Simulator.
>
> Anjali is going decoration shopping this evening.
> The power cut is predicted at 7:30pm with 79% confidence.
> What actually happens if they're caught unprepared?
>
> Let's simulate it."

**[Click the ⚡ Power Cut scenario tile — parameters auto-fill]**

```
╔══════════════════════════════════════════════════════════════╗
║  🔮 WHAT-IF SIMULATOR                                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Scenario:  Power Cut on Diwali Prep Evening                ║
║  ─────────────────────────────────────────────              ║
║  Perturbation:  ⚡ power_available = FALSE                   ║
║  Start time:    19:30 IST tonight (Friday Oct 25)           ║
║  Duration:      90 minutes                                   ║
║  Inverter:      Available (2.5 hr capacity)                 ║
║                                                              ║
║  Simulation window:  17:00 → 23:00 (6 hours)                ║
║  Resolution:         15-minute ticks                         ║
║                                                              ║
║  HOUSEHOLD STATE AT SIM START:                               ║
║  • Anjali: shopping (out of house until ~6:45pm)            ║
║  • Rahul: WFH, active Zoom session                          ║
║  • Priya: Study room (JEE prep, DO NOT DISTURB)             ║
║  • Dadi: Living room, TV                                    ║
║  • Cooking: Dinner prep expected 7:00pm (Anjali)            ║
║                                                              ║
║                    [▶ RUN SIMULATION]                        ║
╚══════════════════════════════════════════════════════════════╝
```

**[Click ▶ RUN SIMULATION]**
**[Show a 2-second animated progress: "Forking twin state... running 24 ticks... analyzing impact... Claude reasoning..."]**

**[Result appears — this is the climax of the demo]**

```
╔══════════════════════════════════════════════════════════════╗
║  📊 SIMULATION COMPLETE                                      ║
║  "Diwali Prep Evening — Power Cut at 7:30pm"                ║
║  Overall Severity:  🔴 SIGNIFICANT                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  GHARJI'S ANALYSIS:                                         ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │                                                      │   ║
║  │  "Anjali ji, agar aap 6:45 tak ghar nahi aayi       │   ║
║  │   aur 7:30 baje light gayi, toh Rahul ka Zoom        │   ║
║  │   call abruptly cut ho jayega aur dinner 9 baje     │   ║
║  │   tak delay ho sakta hai — Dadi ke liye yeh         │   ║
║  │   theek nahi. Ek chhota plan change sab fix         │   ║
║  │   kar sakta hai."                                   │   ║
║  │                                                      │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  CASCADE CHAIN:                                              ║
║  ─────────────────────────────────────────────────────────  ║
║  ⚡ 7:30pm: Power cut                                        ║
║     ↓ WiFi router off (3 sec)                               ║
║     ↓ Rahul's Zoom call DROPS — mid-presentation           ║
║     ↓ Inverter kicks in — 2.5hr capacity begins draining   ║
║     ↓ Cooking not started yet (Anjali still out)           ║
║     ↓ Motor CANNOT run (inverter protection mode)          ║
║     ↓ Tank drains overnight — morning crisis risk          ║
║     ↓ Fridge: fine for 2h, risk if cut extends             ║
║                                                              ║
║  IMPACT MATRIX:                                              ║
║  ┌────────────────────┬──────────┬───────────┬───────────┐  ║
║  │ Routine            │ Baseline │ Simulated │ Severity  │  ║
║  ├────────────────────┼──────────┼───────────┼───────────┤  ║
║  │ Rahul's Zoom call  │ Complete │ DROPPED🔴 │ Critical  │  ║
║  │ Dinner prep        │ 7:00pm   │ 8:45pm 🔴 │ High      │  ║
║  │ Dadi's TV time     │ 7–9pm    │ Inverter  │ Medium    │  ║
║  │ Priya's study      │ Quiet ✅ │ Quiet ✅  │ None      │  ║
║  │ Diwali decoration  │ 8pm work │ Delayed 🟡│ Medium    │  ║
║  │ Motor (tomorrow)   │ 6:10am   │ Risk! 🔴  │ High      │  ║
║  └────────────────────┴──────────┴───────────┴───────────┘  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎯 PROACTIVE ACTION PLAN — GENERATED BY GHARJI             ║
║  ─────────────────────────────────────────────────────────  ║
║                                                              ║
║  17:00  Anjali leaves for shopping                          ║
║  18:00  ⚠️  RETURN BY THIS TIME (not 6:45!)                 ║
║  18:15  Start dinner prep immediately on return             ║
║  18:30  Rahul: save all work, send Zoom "back at 8" note    ║
║  18:45  Charge phones, tablets, Priya's laptop FULLY        ║
║  19:00  Dinner must be SERVED (family eating by 7pm)        ║
║  19:15  Water motor: LAST CHANCE before cut — run now       ║
║  19:25  Switch inverter to standby-ready mode               ║
║  19:30  ⚡ Expected power cut — HOUSEHOLD PREPARED           ║
║  19:30  Diwali decoration work CONTINUES by diya/torch      ║
║  21:00  Power restored (estimated) — resume normal          ║
║                                                              ║
║  [📅 Save as Tonight's Plan]  [📤 Share with Rahul]         ║
║  [🔔 Set 18:00 reminder for Anjali]                         ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER — with energy]**

> "The AI found something we missed.
>
> Rahul has a Zoom call at 7:30pm — exactly when the power cut hits.
> Without GHARMIND, he'd be mid-presentation when the internet drops.
> And dinner wouldn't be ready until 9pm — that's Dadi eating at 9pm, which never happens.
>
> The system generated a complete corrective plan:
> Return by 6pm, not 6:45.
> Start dinner at 6:15.
> Run the motor by 7:15 — last window before the cut.
>
> It didn't just warn. It solved."

---

# ═══════════════════════════════════════════
# MINUTE 3:50 — 4:30 | THE MAGIC MOMENT
# "Exam Week × Festival Week Collision"
# ═══════════════════════════════════════════

**[PRESENTER]**

> "One more. The hardest scenario. Two things collide at once.
> Diwali is Monday. Priya's JEE mock is also Monday.
> Anjali doesn't know yet — but Gharji has already calculated the conflict."

**[Click back to Predictions, scroll to the "This Week" horizon]**

```
╔══════════════════════════════════════════════════════════════╗
║  📅 THIS WEEK — INTELLIGENT FORECAST                        ║
║  Context: Diwali Prep Week + JEE Mock Collision             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🔴 CONFLICT DETECTED: Monday, October 28                   ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │                                                      │   ║
║  │  ⚠️  SCHEDULE CONFLICT — Monday                      │   ║
║  │                                                      │   ║
║  │  DIWALI: Extended pooja starts 5:00am               │   ║
║  │          Family members home, festive noise          │   ║
║  │          Guest arrivals expected 11am–7pm            │   ║
║  │          Cooking: all-day kitchen activity           │   ║
║  │                                                      │   ║
║  │  JEE MOCK:  Priya needs quiet, 6am–9am prep          │   ║
║  │            Leave by 8:15am (exam center 40min)       │   ║
║  │            NO festive noise during 6–8am window      │   ║
║  │                                                      │   ║
║  │  CONFLICT ZONES:                                     │   ║
║  │    06:00–08:00  Pooja bells vs Priya's concentration │   ║
║  │    08:00–09:00  Guest arrivals vs exam departure     │   ║
║  │    All day      Cooking smells/noise vs focus return │   ║
║  │                                                      │   ║
║  │  Confidence this causes disruption: 81%             │   ║
║  │                                                      │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  GHARJI'S RESOLUTION PLAN:                                  ║
║  ──────────────────────────────────────────────────────────  ║
║                                                              ║
║  "Dono ho sakta hai — bas thodi planning chahiye." 🙏       ║
║                                                              ║
║  MON MORNING REVISED PLAN:                                  ║
║  04:30  Dadi's private aarti (bedroom, quiet)              ║
║  05:00  Pooja starts — bells MUTED until 8am               ║
║  05:30  Priya wakes — study session begins in study nook   ║
║  08:00  Rahul drops Priya at exam center (8:15 departure)  ║
║  08:30  Main Diwali puja with full bells, guests OK        ║
║  10:00  First guest wave — living room ready               ║
║  14:00  Priya returns — quiet study room reserved          ║
║                                                              ║
║  HOUSEHOLD MODE: Diwali + Exam Hybrid 🪔📚                   ║
║  Quiet zones: Study, Bedroom 2 (all day)                   ║
║  Festive zones: Living room, Kitchen, Balcony              ║
║                                                              ║
║  [Activate Hybrid Mode for Monday]                          ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER — measured, impactful]**

> "It identified a conflict that no one in the family had consciously noticed.
> Diwali bells and JEE exam prep in the same house, same morning.
>
> And instead of just flagging the problem — it zoned the house.
> Quiet side. Festive side. Both happen. Nobody loses.
>
> This is what we mean by a Household Operating System.
> It manages context like an OS manages processes — allocating attention,
> resolving conflicts, keeping everything running."

---

# ═══════════════════════════════════════════
# MINUTE 4:30 — 5:00 | THE CLOSE
# "Scale, Vision, AWS"
# ═══════════════════════════════════════════

**[PRESENTER — slow down, make eye contact, close strong]**

> "Everything you just saw runs entirely on AWS.
>
> The Digital Twin — pure Python state machine, zero hardware.
> The predictions — pattern matching on pgvector embeddings via Titan.
> The reasoning — Claude 3 Sonnet on AWS Bedrock.
> The What-If simulator — forward simulation with Claude narrative generation.
>
> One architecture. One family. But this scales to 300 million Indian households —
> metro apartments, tier-2 city homes, joint families, single working professionals.
>
> Each one has its own Gharji.
> Each one gets predictions shaped by its city's power schedule,
> its family's festival traditions, its children's exam calendar.
>
> GHARMIND AI doesn't just connect your home to the internet.
> It connects your home to intelligence.
>
> The home that knows you. Before you ask."

**[Final screen: Switch to the Household Mood Ring — now GREEN, urgency 18]**

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                                                              ║
║           ╭─────────────────────╮                            ║
║          ╱  ░░░░░░░░░░░░░░░░░░   ╲   ← Green glow           ║
║         │                         │     (Calm + Prepared)   ║
║         │    SHARMA RESIDENCE     │                         ║
║         │      Urgency: 18 ✅     │                         ║
║          ╲  ░░░░░░░░░░░░░░░░░░   ╱                          ║
║           ╰─────────────────────╯                            ║
║                                                              ║
║         Motor running  ✅                                   ║
║         Diwali plan set  ✅                                  ║
║         Power cut plan ready  ✅                            ║
║         JEE exam day planned  ✅                            ║
║         Priya leaves at 7:15  ✅                            ║
║                                                              ║
║                                                              ║
║    "Your home is ready for the day. And for Diwali."        ║
║                              — Gharji 🪔                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**[PRESENTER — final line, quiet and confident]**

> "GHARMIND AI. India's First Household Operating System.
> Thank you."

---
---

# APPENDIX A: Demo Timing Breakdown

| Segment | Start | End | Duration | Content |
|---|---|---|---|---|
| The Hook | 0:00 | 0:45 | 45s | Problem statement, India context |
| Digital Twin | 0:45 | 1:30 | 45s | Live twin visualization, family members |
| Prediction Engine | 1:30 | 2:15 | 45s | Motor prediction, evidence trail |
| AI Reasoning (Gharji) | 2:15 | 2:50 | 35s | Hinglish Diwali plan via Claude |
| What-If Simulator | 2:50 | 3:50 | 60s | Power cut simulation, cascade, action plan |
| Conflict Detection | 3:50 | 4:30 | 40s | JEE × Diwali collision, household zoning |
| The Close | 4:30 | 5:00 | 30s | AWS tech, scale, vision, final line |

---

# APPENDIX B: AWS Services Showcase (For Judge Q&A)

| What Was Shown | AWS Service | How Used |
|---|---|---|
| AI predictions + reasoning | **AWS Bedrock** | Claude 3 Sonnet — all reasoning, narrative, planning |
| Context embeddings | **AWS Bedrock** | Titan Embed Text v1 — 1536-dim vectors for pgvector |
| Digital twin state | **Amazon RDS PostgreSQL** | twin_state_snapshots, pgvector similarity search |
| Real-time updates | **Amazon ElastiCache (Redis)** | Pub/sub for WebSocket, HCO caching |
| Authentication | **Amazon Cognito** | JWT auth, Anjali's login |
| Deployment | **Amazon ECS Fargate** | FastAPI container, twin engine container |
| Event routing | **Amazon EventBridge** | Scheduled tick events, anomaly routing |
| Monitoring | **Amazon CloudWatch** | Prediction accuracy metrics, agent latency |

---

# APPENDIX C: Anticipated Judge Questions

**Q: "This is just a rule engine with a chatbot UI."**

A: "A rule engine would say 'run motor at 6am every day.' GHARMIND said run the motor *now*, at 6:08am on a Friday, because it's Diwali week, the tank is at 38%, the school bus is in 67 minutes, and historical data shows 14 consecutive Fridays confirming this pattern. No rule was written for that. The confidence was computed, not configured."

---

**Q: "Without real sensors, how reliable are the predictions?"**

A: "The twin is probabilistic, not deterministic — which actually models real life better than binary sensor readings. A sensor tells you the door is open. GHARMIND tells you *why* it's probably open right now, and what it means for the next 2 hours. Reliability improves every week as the feedback loop tightens prediction confidence using actual vs predicted outcomes."

---

**Q: "How does this scale beyond one demo family?"**

A: "Every household is an isolated data partition. The festival calendar, power cut patterns, and occupancy models are parameterized by city and household type — not hardcoded. A new household onboards in 5 minutes, gets 30 days of synthetic history generated automatically, and has a functioning prediction engine from Day 1. The AWS architecture auto-scales horizontally — ECS Fargate, RDS read replicas, ElastiCache clustering."

---

**Q: "What's the Bedrock-specific innovation here?"**

A: "Three things. First, we use Titan Embeddings to create semantic household memory — so the system doesn't just remember *what* happened, it can find *similar* mornings from the past using vector search. Second, Claude's structured output mode produces machine-parseable impact analyses directly from the What-If simulator — not just narrative text. Third, the streaming API enables the Gharji chat experience where responses feel alive, not batch-generated. The entire intelligence layer is Bedrock-native — no external AI APIs."

---

**Q: "What happens if Bedrock is down?"**

A: "Graceful degradation. The prediction engine falls back to cached predictions (Redis, 5-minute TTL). The twin engine continues running autonomously — it doesn't require Bedrock. Chat returns 'Gharji is thinking... try again in a moment.' The household never goes dark. This is an OS — it cannot crash."

---

# APPENDIX D: Backup Demo Flows (If Primary Demo Has Issues)

**Plan B: Pure Chat Demo**
Navigate to Gharji chat only. Type 3 questions:
1. "Motor chalana chahiye?" → Shows real-time motor decision with tank %
2. "Diwali ke liye prepare karo" → Shows full week plan
3. "Power cut ho gayi 7:30 baje" → Shows live household response plan

**Plan C: Static Screenshots**
Pre-load: `/demo/screenshots/` folder with all 6 key screens as fallback images.

**Plan D: Prediction-only demo**
Show the prediction feed with evidence trail expansion for each card.
Walk through 5 predictions verbally, expand evidence for the motor prediction.

---

# APPENDIX E: The One-Line Pitch

> *"Every Indian home has invisible intelligence — in the grandmother who knows the motor schedule, the mother who tracks the festival calendar, the father who remembers the power cut pattern. GHARMIND AI is all of them, running 24/7, one step ahead."*
