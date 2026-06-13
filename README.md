# 🏠 GHARMIND AI
## India's First Household Operating System

> *"Your home doesn't need commands. It needs to understand you."*

---

## 🎯 The Problem

Indian homes are alive with rhythm — morning pooja at 6am, school bus at 7:15, water motor before the tank runs dry, chai at 4pm, load-shedding at 8pm, Diwali preparations, JEE exam week, monsoon routines. These aren't random events. They are **deeply patterned, culturally rich, and entirely predictable** — yet no smart home system understands them.

Existing smart home products fail India because:
- They require explicit commands ("Hey Alexa, turn on the motor")
- They have no concept of Indian household rhythms
- They treat every home identically, ignoring cultural context
- They cannot anticipate — only react

**GHARMIND AI** solves this by building an AI Household Operating System that *thinks* like a family member — one who knows the house, the family, the festivals, and the neighborhood.

---

## 💡 The Solution

GHARMIND AI is a **fully software-based, AI-powered Household Operating System** that:

1. **Learns** your household's unique patterns through a Household Digital Twin
2. **Anticipates** needs before they arise using a multi-agent prediction engine
3. **Understands context** — festivals, exams, seasons, power cuts, water schedules
4. **Simulates** "What-If" scenarios for proactive planning
5. **Communicates** in a natural, conversational way — in Hindi, English, or Hinglish

---

## 🚀 Hackathon Innovation Points

| Dimension | Innovation |
|---|---|
| **Cultural AI** | First AI system trained on Indian household context — festivals, rituals, seasons |
| **Digital Twin** | Full simulation of household state without any IoT hardware |
| **Proactive Intelligence** | Predicts and acts before the user asks |
| **What-If Engine** | "What if there's a power cut during dinner?" — full scenario simulation |
| **Bedrock Native** | Claude Sonnet for reasoning, Titan for semantic memory, all on AWS |
| **Zero Hardware** | 100% software — runs in any browser, no sensors needed |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.12 |
| **AI Core** | AWS Bedrock — Claude 3 Sonnet, Titan Embeddings |
| **Database** | PostgreSQL 16 + pgvector |
| **Cache** | Redis |
| **Message Bus** | AWS EventBridge |
| **Auth** | AWS Cognito |
| **Deployment** | AWS ECS Fargate + Vercel |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    GHARMIND AI                          │
│              Household Operating System                 │
├─────────────────┬───────────────────┬───────────────────┤
│   PERCEPTION    │   INTELLIGENCE    │      ACTION       │
│                 │                   │                   │
│ Digital Twin    │  Context Engine   │  Prediction Feed  │
│ Event Stream    │  Agent Orchestr.  │  What-If Engine   │
│ Pattern Learn.  │  Memory Graph     │  Notification Sys │
└─────────────────┴───────────────────┴───────────────────┘
          │                 │                   │
          └─────────────────┴───────────────────┘
                            │
                    AWS Bedrock Core
                (Claude Sonnet + Titan)
```

---

## 📁 Repository Structure

See [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) for the complete folder tree.

---

## 📚 Documentation Index

| Document | Description |
|---|---|
| [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) | High-level system design |
| [Database Schema](./docs/database/SCHEMA.md) | PostgreSQL + pgvector tables |
| [AI Agent Architecture](./docs/ai/AGENT_ARCHITECTURE.md) | Multi-agent system design |
| [Prediction Engine](./docs/ai/PREDICTION_ENGINE.md) | How predictions work |
| [Digital Twin Design](./docs/twin/DIGITAL_TWIN_DESIGN.md) | Household simulation model |
| [API Design](./docs/api/API_DESIGN.md) | REST + WebSocket API spec |
| [What-If Simulator](./docs/simulator/WHATIF_SIMULATOR.md) | Scenario simulation design |
| [Data Flow](./docs/flows/DATA_FLOW.md) | System-wide data flows |
| [User Journey](./docs/flows/USER_JOURNEY.md) | End-to-end user experience |
| [Frontend Architecture](./docs/frontend/FRONTEND_ARCHITECTURE.md) | UI component design |

---

## 🗺️ Development Phases

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | Architecture & Design | ✅ Complete |
| **Phase 2** | Backend Core + Digital Twin | 🔜 Next |
| **Phase 3** | AI Agents + Prediction Engine | 🔜 Planned |
| **Phase 4** | Frontend Dashboard | 🔜 Planned |
| **Phase 5** | Integration + Demo Polish | 🔜 Planned |

---

## 👥 Target Demo Scenario

> **Sharma family, Pune, Maharashtra**
> Morning: AI detects it's Ganesh Chaturthi prep week. Water motor needs to run early. School exams are this week — quiet hours enforced. Father's WFH Zoom call at 10am. Mother's tuition batch at 5pm. Evening power cut expected at 7pm.
>
> GHARMIND AI has already anticipated all of this. No commands needed.

---

*Built for India. Built for Bharat. Built to win.*
