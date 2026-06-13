# GHARMIND AI — Frontend Architecture
## Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui

---

## Design Philosophy

The GHARMIND AI dashboard should feel like an **Operating System**, not a settings panel.
- Dense but calm — lots of information, never cluttered
- Live — the home is always "breathing" with real-time updates
- Culturally resonant — Indian color palette, festival awareness, Hindi text support
- Action-forward — every piece of information leads to a clear next action

---

## App Router Structure

```
app/
├── layout.tsx                    # Root: fonts, providers, Cognito auth
├── page.tsx                      # Landing/splash page
├── error.tsx                     # Global error boundary
│
├── (auth)/                       # Auth group — no sidebar
│   ├── login/
│   │   └── page.tsx              # Login form + Cognito
│   └── onboarding/
│       ├── page.tsx              # Onboarding wizard shell
│       └── steps/
│           ├── 1-basics.tsx      # Household name, city
│           ├── 2-members.tsx     # Add family members
│           ├── 3-rooms.tsx       # Floor plan builder
│           ├── 4-appliances.tsx  # Appliance setup
│           ├── 5-routines.tsx    # Known routines
│           └── 6-persona.tsx     # AI name, language
│
└── (dashboard)/                  # Dashboard group — with sidebar
    ├── layout.tsx                # Sidebar + TopBar + NotificationPanel
    ├── dashboard/
    │   └── page.tsx              # Main OS home view
    ├── twin/
    │   └── page.tsx              # Live Digital Twin visualization
    ├── predictions/
    │   └── page.tsx              # Full prediction timeline
    ├── routines/
    │   └── page.tsx              # Routine manager
    ├── simulator/
    │   └── page.tsx              # What-If simulator
    ├── insights/
    │   └── page.tsx              # Intelligence insights
    └── chat/
        └── page.tsx              # Gharji chat interface
```

---

## Component Architecture

### Layout Components

#### Sidebar.tsx
```
Purpose: OS-style navigation sidebar
Features:
  - Household name + city at top
  - Navigation items with live badge counts
  - "Urgency indicator" — color ring showing household urgency
  - Mini prediction summary at bottom
  - Gharji quick-access button

Design:
  - Dark sidebar (slate-900) for OS feel
  - Active item: accent orange (India's saffron)
  - Subtle animations on state changes

Navigation items:
  🏠 Dashboard           (main hub)
  🔮 Digital Twin        (live visualization)
  ⚡ Predictions         (with count badge)
  📋 Routines            (active count)
  🎯 What-If Simulator
  💡 Insights
  💬 Gharji (Chat)
  ⚙️  Settings
```

#### TopBar.tsx
```
Purpose: Contextual status bar at the top of every dashboard page
Shows:
  Left:   Page title
  Center: Current IST time | Phase of day | Season | Active festival
  Right:  Power status • Water status • Internet status
          [Notification bell with count]

Live updates: WebSocket-driven, updates every minute
Color coding:
  - Green: all good
  - Yellow: attention needed
  - Red: critical issue
```

#### NotificationPanel.tsx
```
Purpose: Slide-in panel with active predictions/alerts
Trigger: Bell icon in TopBar
Content:
  - Grouped by priority (Critical first)
  - Each card: title, action suggestion, confidence bar
  - [Confirm Done] [Dismiss] [Tell me more] buttons
  - Auto-dismisses confirmed predictions

Animation: Slides in from right, subtle spring physics
```

---

### Dashboard Page Components

#### HouseholdMoodRing.tsx
```
Purpose: Hero visual — the "pulse" of the household
Design:  Circular animated ring
         Color: warm orange (festive) → calm green (normal) → alert red
         Center: household name + urgency score
         Rings: animated breathing effect based on activity level

States:
  - calm (urgency 0-30): slow green pulse
  - active (urgency 31-60): moderate orange pulse
  - festive (festival active): warm saffron glow
  - alert (urgency 61-80): faster amber ring
  - critical (urgency 81-100): red urgent pulse
```

#### PredictionTimeline.tsx (Dashboard preview)
```
Purpose: Mini timeline of next 6 hours
Shows:   3-4 highest priority upcoming predictions
Format:  Horizontal scroll timeline
         Each item: icon + title + time + confidence dot
         Critical items: highlighted with border
Action:  Click → navigates to full Predictions page
```

#### QuickStats.tsx
```
Purpose: At-a-glance household metrics
4 stat cards:
  💧 Water: tank level % with trend arrow
  ⚡ Power: stable/unstable/cut with next cut prediction
  👥 Active: N members home, brief locations
  🪔 Context: "Diwali Prep Week - Day 2 of 5"
```

---

### Digital Twin Page

#### HouseholdMap.tsx
```
Purpose: Visual floor plan of the household
Design:  SVG-based floor plan rendered from room data
         Rooms laid out on a grid (position_x, position_y from DB)
         Real-time occupancy shown with member avatars

Features:
  - Room cards with current occupant dots
  - Appliance state indicators within rooms
  - Click room → RoomDetailPanel slides in
  - Animated member movement transitions
  - Color coding: occupied (warm), empty (cool)

Room types have distinct visual treatment:
  - Pooja Room: warm amber, lamp icon
  - Kitchen: terracotta, activity indicator
  - Bedroom: soft lavender, occupancy dots
  - Balcony: green tint
```

#### RoomCard.tsx
```
Shows for each room:
  - Room name + type icon
  - Current occupants (avatar chips)
  - Appliances in this room + their states
  - Lighting state
  - Recent activity

Interaction: Click → full detail panel
```

#### ResourcePanel.tsx
```
Shows: Water tank (animated fill level graphic)
       Power grid (waveform simulation)
       Internet connectivity
       Gas level indicator

Special: Water tank shows predicted time to empty at current usage
```

---

### Predictions Page

#### PredictionFeed.tsx
```
Purpose: Full prediction timeline for today + this week

Layout:
  Left panel:  Filter controls (horizon, priority, category)
  Center:      Scrollable prediction timeline
  Right panel: Prediction detail when one is selected

Timeline design:
  - Time markers on left (6am, 7am, etc.)
  - Prediction cards positioned at their predicted time
  - Priority color coding:
    Critical: red border
    High:     orange border
    Normal:   gray border
    
Each prediction card shows:
  - Icon (category) + title
  - Time + confidence percentage
  - Action suggestion (1 line)
  - [✓ Done] [✕ Dismiss] [💬 Ask Gharji]
```

#### ConfidenceMeter.tsx
```
Purpose: Visual confidence indicator (0-100%)
Design:  Horizontal bar with gradient
         0-40%: gray (low confidence)
         41-70%: blue (moderate)
         71-90%: green (high)
         91-99%: orange glow (very high)
```

---

### What-If Simulator Page

#### ScenarioBuilder.tsx
```
Purpose: Build and run What-If scenarios

Layout:
  Top: Natural language input "What if..."
       OR scenario template grid

  Template grid (4×2):
  [⚡ Power Cut] [💧 Water Issue] [👥 Guests] [📚 Exams]
  [🎉 Festival] [😷 Sick Member] [🔧 Motor Fail] [🛢️ Gas Empty]

  Selecting template → pre-fills parameter form:
    Power Cut: start time, duration, inverter available
    Guests: arrival time, count, duration
    Exam Week: member, exam type, date

  [▶ Run Simulation] button → animated loading state
```

#### SimulationResult.tsx
```
Purpose: Display simulation outcome
Sections:
  1. Gharji narrative (conversation bubble style)
  2. Severity badge (minimal/moderate/significant/critical)
  3. Impact Matrix (table)
  4. Cascade Chain (animated flowchart)
  5. Action Plan (numbered steps with times)
  6. Risk Flags (warning cards)

Actions:
  [📅 Save as Calendar Plan]
  [📤 Share with Family]
  [🔄 Modify Scenario]
```

---

### Chat Page (Gharji)

#### ChatInterface.tsx
```
Purpose: Conversational AI interface

Layout:
  Left panel:  Context sidebar (current HCO summary)
  Center:      Chat message history
  Bottom:      Input bar with language selector

Features:
  - Streaming responses (tokens appear word by word)
  - Context chips above input showing what Gharji knows
  - Quick suggestion bubbles:
    "Motor chalana chahiye?" | "Today's plan?" | "Diwali prep?"
  - Message references: predictions it mentions are clickable
  - Voice input button (future)

Design:
  Gharji's messages: warm cream bubbles on left
  User messages: saffron/orange bubbles on right
  Gharji avatar: stylized "G" with warm Indian motif
```

#### ContextChip.tsx
```
Small indicator chips above the chat input:
  🏠 Sharma Residence  •  🕕 6:05am  •  🪔 Diwali Prep  •  ⚡ Motor overdue
```

---

### Shared/Cross-Cutting Components

#### FestivalBanner.tsx
```
Appears: When a festival is active or within 3 days
Design:  Thin accent bar at top of dashboard
         Festival colors (Diwali: saffron+gold, Holi: spectrum, etc.)
Content: "🪔 Diwali is in 3 days • Anjali's prep plan is ready"
Click:   Expands to festival impact analysis
```

#### IST_Clock.tsx
```
Always-visible IST time display
Shows:  Current time in IST
        Phase of day
        Day + date
        Current season icon (☀️🌧️❄️)
Updates: Every second
```

#### PowerCutAlert.tsx
```
Appears: When power cut is detected or imminent
Design:  Full-width banner, yellow/amber for warning, red for active
Content (warning): "⚡ Load shedding expected at 7:30pm — 25 minutes away"
Content (active):  "🔴 Power cut active — Inverter on — Est. 45 min remaining"
Actions: Dismiss, View Plan
```

---

## Design System

### Color Palette
```
Primary Background:    #0F0F0F (near-black, OS feel)
Secondary Background:  #1A1A2E (dark blue-black)
Card Background:       #16213E
Sidebar:               #0A0A1A

Accent - Saffron:      #FF6B35 (primary actions, active states)
Accent - Gold:         #FFB347 (festival mode)
Accent - Turquoise:    #00D4AA (success, power OK, water OK)
Alert - Amber:         #FFC107 (warnings)
Alert - Red:           #EF4444 (critical)

Text Primary:          #F5F5F5
Text Secondary:        #A0A0B0
Text Muted:            #606070

Festival Override:
  Diwali:              #FF6B35 + #FFB347 glow effects
  Holi:                Rainbow gradient elements
  Christmas:           Red + green accents
```

### Typography
```
Heading font:  Inter (clean, modern)
Body font:     Inter
Devanagari:    Noto Sans Devanagari (Hindi text)
Monospace:     JetBrains Mono (timestamps, code values)
```

### Motion Design
```
Page transitions:     Fade + slight vertical slide (50ms)
Card animations:      Spring physics (framer-motion)
Twin state updates:   Smooth state transitions (200ms)
Notification entry:   Slide-in from top (150ms spring)
Loading states:       Skeleton screens (no spinners)
Prediction cards:     Subtle pulse on new arrival
```

---

## State Management (Zustand)

```typescript
// householdStore.ts
interface HouseholdStore {
  household: Household | null;
  members: FamilyMember[];
  setHousehold: (h: Household) => void;
  updateMember: (id: string, update: Partial<FamilyMember>) => void;
}

// twinStore.ts
interface TwinStore {
  twinState: TwinStateSnapshot | null;
  isConnected: boolean;                // WebSocket connection status
  lastUpdate: Date | null;
  urgencyScore: number;
  updateTwinState: (state: TwinStateSnapshot) => void;
  setConnectionStatus: (connected: boolean) => void;
}

// predictionStore.ts
interface PredictionStore {
  predictions: Prediction[];
  criticalCount: number;
  lastRefreshed: Date | null;
  setPredictions: (p: Prediction[]) => void;
  dismissPrediction: (id: string) => void;
  confirmPrediction: (id: string) => void;
}
```

## Real-Time Hooks

```typescript
// useTwinStream.ts
// Connects to WebSocket, updates twinStore on every tick
export function useTwinStream(householdId: string) {
  const { updateTwinState, setConnectionStatus } = useTwinStore();

  useEffect(() => {
    const ws = new WebSocket(
      `${WS_BASE}/twin-stream/${householdId}`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event_type === 'state_update') {
        updateTwinState(data.full_state);
      }
    };

    ws.onopen = () => setConnectionStatus(true);
    ws.onclose = () => setConnectionStatus(false);

    return () => ws.close();
  }, [householdId]);
}
```

---

## Performance Strategy

| Concern | Solution |
|---|---|
| Initial page load | Server Components for static content |
| Twin state updates | WebSocket + optimistic UI updates |
| Large prediction lists | Virtual scrolling (react-window) |
| Simulator results | Progressive loading with skeleton |
| Chat streaming | SSE with ReadableStream |
| Image assets | Next.js Image with AVIF format |
| Bundle size | Route-level code splitting |

---

## Accessibility

| Feature | Implementation |
|---|---|
| ARIA labels | All interactive elements labeled |
| Keyboard nav | Full keyboard navigation |
| Color contrast | WCAG AA minimum |
| Screen readers | Semantic HTML + live regions for updates |
| Language | `lang` attribute updated per content language |
| Focus management | Proper focus trap in modals |
| Motion | `prefers-reduced-motion` respected |
