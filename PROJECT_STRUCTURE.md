# GHARMIND AI — Complete Project Structure

```
gharmind-ai/
│
├── README.md                          # Project overview & hackathon pitch
├── ARCHITECTURE_OVERVIEW.md           # High-level system architecture
├── PROJECT_STRUCTURE.md               # This file
├── PHASE1_TASK_LIST.md                # Phase 1 completion tracker
├── docker-compose.yml                 # Local development orchestration
├── .env.example                       # Environment variable template
│
├── docs/                              # All architecture documentation
│   ├── database/
│   │   ├── SCHEMA.md                  # Complete PostgreSQL schema
│   │   └── ERD.md                     # Entity relationship diagram
│   ├── ai/
│   │   ├── AGENT_ARCHITECTURE.md      # Multi-agent system design
│   │   ├── BEDROCK_INTEGRATION.md     # AWS Bedrock configuration
│   │   ├── PREDICTION_ENGINE.md       # Prediction engine design
│   │   └── CONTEXT_ENGINE.md          # Context graph design
│   ├── api/
│   │   ├── API_DESIGN.md              # REST + WebSocket API spec
│   │   └── OPENAPI_SPEC.yaml          # OpenAPI 3.0 specification
│   ├── twin/
│   │   ├── DIGITAL_TWIN_DESIGN.md     # Household Digital Twin design
│   │   └── ROUTINE_PATTERNS.md        # Indian routine catalog
│   ├── simulator/
│   │   └── WHATIF_SIMULATOR.md        # What-If simulator design
│   ├── flows/
│   │   ├── DATA_FLOW.md               # System data flow diagrams
│   │   └── USER_JOURNEY.md            # End-to-end user journeys
│   ├── frontend/
│   │   └── FRONTEND_ARCHITECTURE.md   # Next.js component architecture
│   └── infra/
│       └── INFRASTRUCTURE.md          # AWS deployment architecture
│
├── backend/                           # FastAPI Python backend
│   ├── pyproject.toml                 # Python project config (Poetry)
│   ├── Dockerfile                     # Backend container
│   ├── alembic/                       # Database migrations
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/                  # Migration files
│   │
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # App configuration & env vars
│   │   ├── dependencies.py            # FastAPI dependency injection
│   │   │
│   │   ├── api/                       # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py          # Aggregate all v1 routes
│   │   │   │   ├── households.py      # Household management
│   │   │   │   ├── twin.py            # Digital Twin endpoints
│   │   │   │   ├── predictions.py     # Prediction feed endpoints
│   │   │   │   ├── routines.py        # Routine CRUD
│   │   │   │   ├── members.py         # Family member management
│   │   │   │   ├── events.py          # Event stream endpoints
│   │   │   │   ├── simulator.py       # What-If simulator endpoints
│   │   │   │   ├── chat.py            # Conversational AI endpoint
│   │   │   │   └── insights.py        # Household insights
│   │   │   └── ws/
│   │   │       ├── __init__.py
│   │   │       └── twin_stream.py     # WebSocket: live twin stream
│   │   │
│   │   ├── core/                      # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # Auth, JWT, Cognito integration
│   │   │   ├── exceptions.py          # Custom exception hierarchy
│   │   │   └── middleware.py          # Request logging, tracing
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model class
│   │   │   ├── household.py           # Household model
│   │   │   ├── member.py              # Family member model
│   │   │   ├── room.py                # Room model
│   │   │   ├── appliance.py           # Appliance model
│   │   │   ├── routine.py             # Routine model
│   │   │   ├── routine_event.py       # Routine event log
│   │   │   ├── prediction.py          # Prediction model
│   │   │   ├── memory_vector.py       # pgvector memory model
│   │   │   ├── festival_calendar.py   # Indian festival calendar
│   │   │   ├── household_context.py   # Snapshot of household context
│   │   │   └── simulation_run.py      # What-If simulation results
│   │   │
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── household.py
│   │   │   ├── member.py
│   │   │   ├── room.py
│   │   │   ├── appliance.py
│   │   │   ├── routine.py
│   │   │   ├── prediction.py
│   │   │   ├── twin_state.py
│   │   │   ├── chat.py
│   │   │   └── simulator.py
│   │   │
│   │   ├── services/                  # Business service layer
│   │   │   ├── __init__.py
│   │   │   ├── household_service.py   # Household CRUD + onboarding
│   │   │   ├── twin_service.py        # Digital Twin state management
│   │   │   ├── routine_service.py     # Routine detection & management
│   │   │   ├── prediction_service.py  # Orchestrates prediction pipeline
│   │   │   ├── calendar_service.py    # Festival/event calendar logic
│   │   │   ├── memory_service.py      # Vector memory CRUD
│   │   │   └── notification_service.py # Push / in-app notifications
│   │   │
│   │   ├── agents/                    # AI Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py          # Abstract base agent
│   │   │   ├── context_agent.py       # Context graph builder
│   │   │   ├── prediction_agent.py    # Prediction generator
│   │   │   ├── reasoning_agent.py     # Claude deep reasoner
│   │   │   ├── whatif_agent.py        # What-If simulation agent
│   │   │   └── orchestrator.py        # Agent pipeline coordinator
│   │   │
│   │   ├── twin/                      # Household Digital Twin engine
│   │   │   ├── __init__.py
│   │   │   ├── twin_engine.py         # Core twin state machine
│   │   │   ├── event_simulator.py     # Synthetic event generation
│   │   │   ├── pattern_detector.py    # Routine pattern detection
│   │   │   ├── occupancy_model.py     # Simulated occupancy
│   │   │   ├── appliance_model.py     # Appliance state simulation
│   │   │   ├── power_model.py         # Power cut simulation
│   │   │   ├── water_model.py         # Water supply simulation
│   │   │   └── time_model.py          # Indian temporal context
│   │   │
│   │   ├── bedrock/                   # AWS Bedrock client wrappers
│   │   │   ├── __init__.py
│   │   │   ├── client.py              # boto3 Bedrock Runtime client
│   │   │   ├── claude_client.py       # Claude Sonnet wrapper
│   │   │   ├── titan_client.py        # Titan Embeddings wrapper
│   │   │   └── prompts/               # Prompt templates
│   │   │       ├── context_prompt.py
│   │   │       ├── prediction_prompt.py
│   │   │       ├── reasoning_prompt.py
│   │   │       └── whatif_prompt.py
│   │   │
│   │   ├── db/                        # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── session.py             # Async SQLAlchemy session
│   │   │   ├── repositories/          # Repository pattern
│   │   │   │   ├── __init__.py
│   │   │   │   ├── household_repo.py
│   │   │   │   ├── routine_repo.py
│   │   │   │   ├── prediction_repo.py
│   │   │   │   └── memory_repo.py
│   │   │   └── seeds/                 # Demo data seeds
│   │   │       ├── festival_data.py   # Indian festival calendar data
│   │   │       ├── demo_household.py  # Sharma family demo household
│   │   │       └── routine_templates.py # Common Indian routines
│   │   │
│   │   └── utils/                     # Utility modules
│   │       ├── __init__.py
│   │       ├── time_utils.py          # IST timezone handling
│   │       ├── indian_calendar.py     # Festival date calculations
│   │       └── hinglish_utils.py      # Hindi/Hinglish processing
│   │
│   └── tests/
│       ├── unit/
│       │   ├── test_twin_engine.py
│       │   ├── test_pattern_detector.py
│       │   ├── test_context_agent.py
│       │   └── test_prediction_agent.py
│       └── integration/
│           ├── test_api_households.py
│           ├── test_api_twin.py
│           └── test_prediction_pipeline.py
│
├── frontend/                          # Next.js 15 frontend
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── components.json                # shadcn/ui config
│   ├── Dockerfile
│   │
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing / splash
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── onboarding/
│   │   │       ├── page.tsx           # Household setup wizard
│   │   │       └── steps/             # Multi-step onboarding
│   │   └── (dashboard)/
│   │       ├── layout.tsx             # Dashboard shell layout
│   │       ├── dashboard/page.tsx     # Main OS dashboard
│   │       ├── twin/page.tsx          # Live Digital Twin view
│   │       ├── predictions/page.tsx   # Prediction timeline
│   │       ├── routines/page.tsx      # Routine manager
│   │       ├── simulator/page.tsx     # What-If simulator
│   │       ├── insights/page.tsx      # Household intelligence insights
│   │       └── chat/page.tsx          # Conversational AI interface
│   │
│   ├── components/
│   │   ├── ui/                        # shadcn/ui base components
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx            # OS-style sidebar navigation
│   │   │   ├── TopBar.tsx             # Context status bar
│   │   │   └── NotificationPanel.tsx  # Prediction alerts panel
│   │   ├── twin/
│   │   │   ├── HouseholdMap.tsx       # Floor plan visualization
│   │   │   ├── RoomCard.tsx           # Room state card
│   │   │   ├── ApplianceStatus.tsx    # Appliance state indicator
│   │   │   └── OccupancyView.tsx      # Family member location
│   │   ├── predictions/
│   │   │   ├── PredictionTimeline.tsx # Next 24h timeline
│   │   │   ├── PredictionCard.tsx     # Individual prediction card
│   │   │   └── ConfidenceMeter.tsx    # AI confidence indicator
│   │   ├── routines/
│   │   │   ├── RoutineList.tsx        # All household routines
│   │   │   ├── RoutineEditor.tsx      # Create/edit routine
│   │   │   └── PatternInsight.tsx     # Detected pattern display
│   │   ├── simulator/
│   │   │   ├── ScenarioBuilder.tsx    # What-If scenario builder
│   │   │   ├── SimulationResult.tsx   # Simulation output display
│   │   │   └── ImpactMatrix.tsx       # Impact analysis grid
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx      # Conversational AI window
│   │   │   ├── MessageBubble.tsx      # Chat message component
│   │   │   └── ContextChip.tsx        # Context tag display
│   │   └── shared/
│   │       ├── FestivalBanner.tsx     # Festival awareness banner
│   │       ├── PowerCutAlert.tsx      # Power cut warning
│   │       ├── HouseholdMoodRing.tsx  # Overall household state visual
│   │       └── IST_Clock.tsx          # Indian Standard Time clock
│   │
│   ├── lib/
│   │   ├── api/                       # API client functions
│   │   │   ├── client.ts              # Axios/fetch base client
│   │   │   ├── twin.ts                # Twin API calls
│   │   │   ├── predictions.ts         # Prediction API calls
│   │   │   └── simulator.ts           # Simulator API calls
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useTwinStream.ts       # WebSocket twin stream hook
│   │   │   ├── usePredictions.ts      # Prediction data hook
│   │   │   └── useHousehold.ts        # Household context hook
│   │   ├── store/                     # Zustand state store
│   │   │   ├── householdStore.ts
│   │   │   ├── twinStore.ts
│   │   │   └── predictionStore.ts
│   │   └── utils/
│   │       ├── formatters.ts          # Time, number formatting
│   │       └── indianCalendar.ts      # Festival calendar utils
│   │
│   └── types/
│       ├── household.ts               # TypeScript type definitions
│       ├── twin.ts
│       ├── prediction.ts
│       └── api.ts
│
├── infra/                             # Infrastructure as Code
│   ├── docker-compose.yml             # Full local stack
│   ├── docker-compose.dev.yml         # Dev overrides
│   └── aws/
│       ├── ecs-task-definition.json   # ECS Fargate task def
│       ├── rds-config.json            # RDS PostgreSQL config
│       └── bedrock-iam-policy.json    # Bedrock IAM policy
│
└── scripts/                           # Developer utility scripts
    ├── seed_demo_data.py              # Populate demo household
    ├── generate_twin_events.py        # Generate synthetic events
    └── test_bedrock_connection.py     # Verify Bedrock connectivity
```

---

## Key Architectural Decisions

### Why FastAPI?
- Native async support — critical for Bedrock streaming responses
- Automatic OpenAPI docs generation
- Type-safe with Pydantic, matching our PostgreSQL schema

### Why Next.js App Router?
- Server Components for fast initial dashboard load
- Streaming UI for real-time prediction updates
- Native WebSocket support for twin stream

### Why pgvector?
- Household routine memories stored as embeddings
- Semantic search: "find routines similar to this morning pattern"
- No separate vector DB — one PostgreSQL instance for everything

### Why Separate Services (twin/, agents/, bedrock/)?
- Clean separation allows independent testing
- Twin engine runs on a clock tick — independently of web requests
- Agents are stateless — can be called from API or background workers
