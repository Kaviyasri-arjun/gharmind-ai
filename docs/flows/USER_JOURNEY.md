# GHARMIND AI — User Journey Design

---

## Persona: The Sharma Family

**Anjali Sharma** (Primary User)
- 42 years old, homemaker and home tuition teacher
- Manages household for 5 family members
- Runs 3 tuition batches per week from home
- Pain points: Water motor forgetting, power cut disruptions, festival planning stress
- Device: Android smartphone, laptop
- Language: Hinglish preference

**Rahul Sharma** (Secondary User)
- 45 years old, IT manager
- WFH Monday-Thursday
- Cares about: Zoom calls not disrupted, electricity for home office, quiet hours
- Language: English preference

**Priya Sharma** (Tertiary User)
- 16 years old, JEE aspirant
- Primary concern: Study schedule, tuition timing, exam reminders
- Language: English

---

## Journey 1: First-Time Onboarding

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ONBOARDING JOURNEY                                │
│                   Duration: ~5 minutes                               │
└─────────────────────────────────────────────────────────────────────┘

STEP 1 ─── LANDING
─────────────────────────────────────────────────────────────────────
User sees:  Splash page — "Your home should know you."
            Animated illustration of an Indian home with flowing context
            "Namaste! GHARMIND AI samjhega tumhara ghar."
            [Get Started] button

User feels: Intrigued. This is different from other smart home apps.


STEP 2 ─── SIGNUP
─────────────────────────────────────────────────────────────────────
User enters: Name, phone/email
System:      AWS Cognito OTP verification
             "Welcome, Anjali! Let's set up your ghar."


STEP 3 ─── HOUSEHOLD BASICS
─────────────────────────────────────────────────────────────────────
Screen:  Clean wizard, one question at a time.

         "What do you call your home?"
         → "Sharma Residence" ✓

         "Which city are you in?"
         → Pune (autocomplete) ✓

         "What type of home?"
         → [Apartment] [Villa] [Row House] [Independent]
         → Apartment ✓

         "How many floors / family members?"
         → 1 floor, 5 members ✓


STEP 4 ─── MEET YOUR FAMILY
─────────────────────────────────────────────────────────────────────
Screen:  "Who lives in Sharma Residence?"
         [+ Add Member] cards

Anjali adds:
  → Anjali (Mother, homemaker)       — wake 5:30, sleep 22:30
  → Rahul (Father, IT)               — WFH Mon-Thu, office Fri
  → Priya (Daughter, student, JEE)   — school 7:15am, tuition 5pm
  → Dadi (Grandmother)               — early riser 4:30am
  → Kaka (Uncle)                     — irregular

System:  AI infers household type: "Joint family, working+student home"


STEP 5 ─── MAP YOUR HOME
─────────────────────────────────────────────────────────────────────
Screen:  Simple floor plan builder with drag-and-drop room tiles

Anjali places:
  Master Bedroom | Bedroom 2 | Living Room
  Kitchen | Pooja Room | Bathroom
  Balcony | Study Nook

System highlights: "I see you have a Pooja Room! I'll watch morning
                   prayer timings carefully."


STEP 6 ─── YOUR APPLIANCES
─────────────────────────────────────────────────────────────────────
Screen:  "What appliances do you have?"
         Grid of appliance icons — tap to add

Anjali taps:
  ✓ Water Motor    ✓ Geyser      ✓ Air Conditioner
  ✓ Washing Machine ✓ TV         ✓ WiFi Router
  ✓ Fridge        ✓ Gas Stove

System: "Water Motor detected! This is super important for Indian homes.
         What time do you usually run it?"
         → "Around 6am" → stored


STEP 7 ─── KNOWN ROUTINES
─────────────────────────────────────────────────────────────────────
Screen:  "Tell me about your daily routines"
         [Template cards with Indian routine patterns]

         ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
         │ 🪔 Morning     │ │ 💧 Water Motor │ │ 🚌 School Rush │
         │    Pooja       │ │    Schedule    │ │                │
         │  [+ Add]       │ │  [+ Add]       │ │  [+ Add]       │
         └────────────────┘ └────────────────┘ └────────────────┘
         ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
         │ ☕ Evening     │ │ 📚 Home        │ │ ⚡ Power Cut   │
         │    Chai        │ │    Tuition     │ │    Protocol    │
         │  [+ Add]       │ │  [+ Add]       │ │  [+ Add]       │
         └────────────────┘ └────────────────┘ └────────────────┘

         Or: [Describe in your own words]

Anjali adds: Morning Pooja, Water Motor, School Rush, Evening Chai,
             Home Tuition (Mon/Wed/Fri, 5pm), Power Cut Protocol


STEP 8 ─── MEET GHARJI
─────────────────────────────────────────────────────────────────────
Screen:  "Your home AI is ready! What should I call myself?"
         Default: "Gharji"
         Anjali: "Gharji" ✓

         "And I'll talk to you in..."
         → [English] [Hindi] [Hinglish ✓]

         [ACTIVATE GHARJI →]


STEP 9 ─── INITIALIZATION (Loading screen)
─────────────────────────────────────────────────────────────────────
Screen:  "Gharji is learning your home..."
         Animated sequence:
         ✓ Mapping Sharma Residence
         ✓ Loading Pune water schedule
         ✓ Loading MSEDCL power patterns
         ✓ Simulating last 30 days...
         ✓ Learning your routines...
         ✓ Your first predictions are ready!

Duration: ~90 seconds


STEP 10 ─── DASHBOARD REVEAL
─────────────────────────────────────────────────────────────────────
Screen:  Dashboard animates in with:

         "Good morning, Anjali! 🙏
          Today is Monday. Diwali is in 4 days.
          I have 3 things that need your attention."

User feels: Wow. This thing already knows my life.
```

---

## Journey 2: Morning Routine (Returning User)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  MORNING ROUTINE EXPERIENCE                          │
│                   Monday, 6:05am, Diwali Prep Week                  │
└─────────────────────────────────────────────────────────────────────┘

Anjali opens phone, taps GHARMIND icon (or notification woke her):

  ┌─────────────────────────────────────┐
  │ 🔴 CRITICAL ALERT                   │
  │                                     │
  │ 💧 Water Motor — Run Now!           │
  │                                     │
  │ Tank is at 38%. School bus at 7:15. │
  │ Diwali week mein zyada paani lagta  │
  │ hai. Motor abhi chalao!             │
  │                                     │
  │ [Confirm Done ✓] [Remind in 5 min] │
  └─────────────────────────────────────┘

Anjali goes to motor switch, turns it on.
Taps [Confirm Done ✓]

Twin updates: water_motor.state = "on"
Prediction: marked as "accurate, acted on"

Dashboard now shows:

  ┌─────────────────────────────────────────────┐
  │  Good morning, Anjali! ☀️                   │
  │  6:08am · Monday · Diwali Prep Week 🪔       │
  │                                             │
  │  SHARMA RESIDENCE                           │
  │  🟢 All good now • Urgency: 25/100          │
  │                                             │
  │  📍 RIGHT NOW                               │
  │  Dadi: Pooja Room (aarti)                   │
  │  Anjali: Kitchen                            │
  │  Rahul: Master Bedroom (sleeping)           │
  │  Priya: Bedroom 2 (getting ready)           │
  │                                             │
  │  ⏰ COMING UP TODAY                         │
  │  7:15am  Priya's school bus     [95%]       │
  │  10:00am Rahul's Zoom call      [91%]       │
  │  5:00pm  Tuition batch (3 kids) [88%]       │
  │  7:30pm  Load shedding expected [79%]       │
  │                                             │
  │  🪔 DIWALI IN 4 DAYS                        │
  │  "Deep cleaning should start today.         │
  │   Anjali, decoration shopping Friday?"      │
  └─────────────────────────────────────────────┘

Anjali taps the Diwali insight ─►

  ┌─────────────────────────────────────────────┐
  │  🪔 Diwali Preparation Plan                 │
  │                                             │
  │  Gharji says:                               │
  │  "Aaj se shuru karo, stress free Diwali     │
  │   hogi!"                                    │
  │                                             │
  │  TODAY (Mon) Deep cleaning sweep            │
  │  TUE      Decoration shopping               │
  │  WED      Mithai + snack prep               │
  │  THU      Final cleaning + setup            │
  │  FRI      Diwali! 🪔                        │
  │                                             │
  │  [Run What-If: Power cut on Diwali night]   │
  └─────────────────────────────────────────────┘
```

---

## Journey 3: What-If Simulation

```
┌─────────────────────────────────────────────────────────────────────┐
│                     WHAT-IF SIMULATION JOURNEY                       │
│                    Anjali plans for Diwali evening                   │
└─────────────────────────────────────────────────────────────────────┘

Anjali taps: [Run What-If: Power cut on Diwali night]

  ┌─────────────────────────────────────────────┐
  │  🔮 What-If Simulator                        │
  │                                             │
  │  Scenario: Power Cut on Diwali Evening      │
  │                                             │
  │  When?  [Friday 28 Oct ▾] [7:30pm ▾]       │
  │  How long? [1.5 hours ▾]                    │
  │                                             │
  │  [▶ Simulate This]                          │
  └─────────────────────────────────────────────┘

[Simulation running... 2 seconds]

  ┌─────────────────────────────────────────────┐
  │  📊 SIMULATION RESULT                        │
  │  "Diwali Raat Mein Light Gayi"              │
  │                                             │
  │  ⚠️ SIGNIFICANT IMPACT                      │
  │                                             │
  │  Gharji says:                               │
  │  "Diwali ki raat 7:30 baje agar light gayi, │
  │   toh dinner 7 baje se pehle ready hona     │
  │   chahiye. Diyas aur lights inverter pe     │
  │   chalenge — 3 ghante ka backup hai.        │
  │   Pehle se taiyari karo!"                   │
  │                                             │
  │  IMPACT MAP                                 │
  │  ✅ Diya lighting: Fine (battery backup)    │
  │  ✅ Evening aarti: Not affected             │
  │  ⚠️  Dinner: Must be ready by 7pm           │
  │  ⚠️  Sweets warming: Complete before cut    │
  │  🔴 Inverter: Only 3hr backup              │
  │  🔴 Fridge: Monitor after 2hr cut           │
  │                                             │
  │  🎯 ACTION PLAN                             │
  │  6:00pm  Start dinner prep early            │
  │  6:30pm  Charge all devices fully           │
  │  7:00pm  Dinner must be served              │
  │  7:25pm  Switch to inverter mode            │
  │  7:30pm  Expected power cut                 │
  │  8:00pm  Diwali puja & celebration 🪔       │
  │                                             │
  │  [📅 Add to Calendar] [📤 Share with Rahul] │
  └─────────────────────────────────────────────┘
```

---

## Journey 4: Exam Week Adjustment

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXAM WEEK JOURNEY                                │
│                  Priya's JEE Mains next Monday                       │
└─────────────────────────────────────────────────────────────────────┘

Anjali adds event: "Priya — JEE Mains — Monday Nov 4"

GHARMIND AI responds immediately:

  ┌─────────────────────────────────────────────┐
  │  📚 Exam Week Mode Activated                 │
  │  JEE Mains: Monday, November 4               │
  │                                             │
  │  Gharji says:                               │
  │  "Priya ki JEE ke liye poora ghar           │
  │   ready hai. Yeh changes kar raha hoon:"    │
  │                                             │
  │  HOUSEHOLD ADJUSTMENTS                      │
  │  🔇 Quiet hours: 6am — 11pm all week        │
  │  📺 TV: Evenings only (8-9pm)               │
  │  🎓 Tuition: Cancelled Mon/Wed (exam days)  │
  │  ☕ Chai: Delivered to study room 5pm, 9pm  │
  │  🚗 Sunday drop-off plan set: 8:15am        │
  │                                             │
  │  STUDY SCHEDULE SUGGESTION                  │
  │  5:30am  Morning session (2 hrs)            │
  │  6:00pm  Evening session (3 hrs)            │
  │  9:00pm  Night session (2 hrs — light)      │
  │                                             │
  │  [Activate Exam Mode] [Customize]           │
  └─────────────────────────────────────────────┘
```

---

## Journey 5: Conversational Interaction

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GHARJI CHAT EXPERIENCE                           │
└─────────────────────────────────────────────────────────────────────┘

  Anjali (3:55pm):
  ┌─────────────────────────────────────────────┐
  │ "Gharji, aaj tuition ke liye living room    │
  │  ready hai?"                                │
  └─────────────────────────────────────────────┘

  Gharji:
  ┌─────────────────────────────────────────────┐
  │  Haan Anjali! Tuition 5 baje hai, aur       │
  │  living room abhi khali hai. Dadi bedroom   │
  │  mein hain aur Priya school se 4:30 baje    │
  │  wapas aayi thi.                            │
  │                                             │
  │  Ek baat: aaj Rahul ka 4:30 ka call late    │
  │  hua tha — check karo woh 5 baje khatam     │
  │  ho jayega ya nahi. Agar call overlap hua,  │
  │  toh study nook better rahega.              │
  └─────────────────────────────────────────────┘

  Anjali: "Motor aaj dobaara chalana hai?"

  Gharji:
  ┌─────────────────────────────────────────────┐
  │  Subah chalaya tha 6:10 baje — tank abhi    │
  │  68% hai. Diwali week mein usage zyada hai, │
  │  toh kal subah 5:45 baje chalao.            │
  │                                             │
  │  Aaj sham mein chalane ki zaroorat nahi     │
  │  hai. 🟢                                   │
  └─────────────────────────────────────────────┘

  Anjali: "This week ka plan batao"

  Gharji:
  ┌─────────────────────────────────────────────┐
  │  📅 Sharma Residence — This Week             │
  │  (Diwali Prep Week 🪔)                      │
  │                                             │
  │  MON (today)  Deep cleaning + motor 6am     │
  │  TUE          Decoration shopping           │
  │               Power cut 7:30pm expected     │
  │  WED          Mithai prep + extra cooking   │
  │               Tuition (Priya's last before) │
  │  THU          Final setup, guest calls      │
  │               Rahul WFH, Zoom 10am          │
  │  FRI          DIWALI! 🪔                    │
  │               Extended pooja 5am           │
  │               Dinner early (power cut risk) │
  │  SAT          Guest visits, Govardhan puja  │
  │  SUN          Wind down, laundry, rest      │
  └─────────────────────────────────────────────┘
```

---

## Journey 6: Power Cut Proactive Response

```
┌─────────────────────────────────────────────────────────────────────┐
│                  POWER CUT PROACTIVE RESPONSE                        │
│                   Tuesday evening, 7:00pm                            │
└─────────────────────────────────────────────────────────────────────┘

6:58pm — GHARMIND notification:

  ┌─────────────────────────────────────────────┐
  │ ⚡ Power Cut in ~30 minutes                  │
  │                                             │
  │ MSEDCL Tuesday cut: 7:30pm expected.        │
  │                                             │
  │ Gharji suggests:                            │
  │ • Dinner cooking? Finish by 7:15            │
  │ • Charge phones NOW (15 min window)         │
  │ • Rahul's laptop — save work                │
  │ • Inverter ready for fans + lights          │
  └─────────────────────────────────────────────┘

7:30pm — Power cut occurs:

  ┌─────────────────────────────────────────────┐
  │ 🔴 Power Cut Active                          │
  │                                             │
  │ Inverter mode ON                            │
  │ Estimated: 60-90 min                        │
  │                                             │
  │ Load management:                            │
  │ • 2 fans running (normal)                   │
  │ • Motor: OFF (protect inverter)             │
  │ • AC: OFF (protect inverter)                │
  │ • Fridge: monitoring (off > 2 hrs = alert)  │
  │                                             │
  │ Estimated battery remaining: 2hr 15min      │
  └─────────────────────────────────────────────┘

8:45pm — Power restored:

  ┌─────────────────────────────────────────────┐
  │ 🟢 Power Restored!                           │
  │                                             │
  │ Duration: 75 minutes                        │
  │                                             │
  │ Auto-resuming:                              │
  │ ✓ WiFi router restarting                    │
  │ ✓ Fridge temperature normal                 │
  │                                             │
  │ Reminder: Run motor tomorrow morning        │
  │ (missed tonight's refill)                   │
  └─────────────────────────────────────────────┘
```

---

## Emotional Journey Map

```
                    ANJALI'S EMOTIONAL JOURNEY

High  ┤
      │                                                    ★ DELIGHT
      │                                              ╭─────────────────
Conf  │                              ╭───────────────╯
iden  │                    ╭─────────╯
ce &  │            ╭───────╯
Trust │   ╭─────╯
      │───╯
Low   │
      ├──────────────────────────────────────────────────────────────
      │ Sign Up  Onboard  Day 1   Week 1  Month 1  Festival  Long-term
      │         "5 min"  "works!"  "wow"  "habit"  "clutch"   "family"
      │
      │ MOMENTS OF DELIGHT:
      │  • "It already knows our motor schedule!"
      │  • "Gharji predicted the power cut exactly"
      │  • "The Diwali plan was exactly what I needed"
      │  • "Priya's exam week — it adjusted everything automatically"
```

---

## Accessibility & Inclusion Notes

| Feature | Consideration |
|---|---|
| Language | English, Hindi, Hinglish — per-member preference |
| Font size | Large text mode for Dadi's usage |
| Voice | Text-to-speech for chat responses |
| Notifications | WhatsApp fallback (phone number stored) |
| Low data | Compressed API payloads, offline cache for current state |
| Low-end devices | PWA works on 2GB RAM Android phones |
