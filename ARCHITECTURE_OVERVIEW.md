# GHARMIND AI — System Architecture Overview

## Design Philosophy

GHARMIND AI is architected as an **Operating System for the household**, not a smart home controller. Just as an OS manages processes, memory, and I/O without the user thinking about hardware — GHARMIND manages household context, routines, and anticipations without the user issuing commands.

The three core architectural principles:

1. **Context-First**: Every decision starts with household context, not user commands
2. **Proactive over Reactive**: The system predicts and prepares; it doesn't wait
3. **Culturally Grounded**: Indian temporal patterns (festivals, seasons, rituals) are first-class citizens

---

## System Layers

```
╔══════════════════════════════════════════════════════════════════════╗
║                        PRESENTATION LAYER                            ║
║   Next.js 15 Dashboard │ Mobile PWA │ WhatsApp Bot │ Voice Interface ║
╚══════════════════════════════╤═══════════════════════════════════════╝
                               │ HTTPS / WebSocket
╔══════════════════════════════╧═══════════════════════════════════════╗
║                         API GATEWAY LAYER                            ║
║              FastAPI │ Auth (Cognito) │ Rate Limiting                 ║
╚══════════╤════════════════════════╤════════════════════════╤═════════╝
           │                        │                        │
╔══════════╧══════╗      ╔══════════╧══════╗      ╔══════════╧══════╗
║  DIGITAL TWIN   ║      ║  AI INTELLIGENCE ║      ║  ACTION ENGINE  ║
║  SERVICE        ║      ║  SERVICE         ║      ║  SERVICE        ║
║                 ║      ║                  ║      ║                 ║
║ Household State ║      ║ Context Engine   ║      ║ Prediction Feed ║
║ Event Simulator ║      ║ Agent Orchestra. ║      ║ What-If Engine  ║
║ Pattern Tracker ║      ║ Memory Graph     ║      ║ Notif. Engine   ║
╚════════╤════════╝      ╚══════════╤═══════╝      ╚════════╤════════╝
         │                          │                        │
╔════════╧══════════════════════════╧════════════════════════╧════════╗
║                         DATA LAYER                                   ║
║   PostgreSQL+pgvector │ Redis Cache │ S3 (Media) │ EventBridge       ║
╚══════════════════════════════════════════════════════════════════════╝
                               │
╔══════════════════════════════╧═══════════════════════════════════════╗
║                       AWS BEDROCK LAYER                              ║
║         Claude 3 Sonnet (Reasoning) │ Titan Embeddings (Memory)      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Core Subsystems

### 1. Household Digital Twin (HDT)
The HDT is the central nervous system. It maintains a real-time simulation of:
- **Physical state**: Rooms, appliances, occupancy (all simulated)
- **Temporal state**: Time of day, day of week, season, festival calendar
- **Behavioral state**: Who is home, what routines are active
- **Environmental state**: Simulated weather, power grid status, water supply

The HDT emits a continuous **event stream** that feeds the AI Intelligence layer.

### 2. AI Intelligence Service
Three cooperative agents powered by AWS Bedrock:

- **ContextAgent**: Maintains the current household context graph. Knows *what is happening* right now.
- **PredictionAgent**: Uses context + historical patterns to predict *what will happen* in the next 2 hours, today, this week.
- **ReasoningAgent**: Claude Sonnet-powered deep reasoner that handles complex scenarios, What-If queries, and natural language interaction.

### 3. Action Engine
Converts predictions into actionable outputs:
- **Prediction Feed**: Real-time stream of upcoming predicted events
- **What-If Simulator**: User-driven scenario exploration
- **Notification Engine**: Smart, non-intrusive alerts

---

## Data Flow Summary

```
[Household Digital Twin]
        │
        │  (Event Stream: state changes, time events, routine triggers)
        ▼
[Context Engine] ──── (pgvector semantic search) ──→ [Memory Store]
        │
        │  (Enriched context object)
        ▼
[Prediction Agent] ─── (Claude Sonnet inference) ──→ [Prediction Store]
        │
        │  (Ranked predictions with confidence)
        ▼
[Action Engine] ──────────────────────────────────→ [User Interface]
        │
        │  (What-If queries)
        ▼
[Reasoning Agent] ──── (Claude Sonnet deep reasoning) → [Simulation Results]
```

---

## AWS Bedrock Integration Architecture

```
FastAPI Backend
     │
     ├─── boto3 client ──→ AWS Bedrock Runtime
     │                          │
     │                    ┌─────┴──────┐
     │                    │            │
     │              Claude 3 Sonnet   Titan Embeddings
     │              (anthropic.       (amazon.titan-
     │               claude-3-        embed-text-v1)
     │               sonnet-20240229) │
     │                    │           │
     │              [Reasoning]  [Vector Search]
     │              [Planning]   [Semantic Memory]
     │              [What-If]    [Pattern Match]
     │
     └─── pgvector ──────→ PostgreSQL
                           (vector similarity search
                            for routine pattern matching)
```

---

## Scalability Design

| Concern | Solution |
|---|---|
| **Multi-tenancy** | One household = one isolated data partition |
| **Prediction latency** | Redis cache for hot predictions, async background jobs |
| **Bedrock cost** | Intelligent caching of embeddings, batched inference |
| **Real-time updates** | WebSocket per dashboard session, SSE for mobile |
| **Scale out** | ECS Fargate auto-scaling, stateless microservices |

---

## Security Architecture

```
User → Cognito JWT → API Gateway → Service Auth
                                        │
                     Row-Level Security in PostgreSQL
                     (household_id isolation)
                                        │
                     Bedrock IAM Role (least privilege)
                     S3 bucket policies (household-scoped)
```

---

## Innovation Differentiators (Judge View)

| Feature | Why It Wins |
|---|---|
| **Cultural Calendar Engine** | First system to treat Indian festivals as first-class operational events |
| **No-Hardware Digital Twin** | Democratizes smart home for 300M Indian households |
| **Anticipatory AI** | Moves from "smart" to "wise" — the OS analogy is literal |
| **What-If Simulator** | Lets families rehearse scenarios: power cuts, exams, guests |
| **Hinglish NLU** | Understands "kal subah motor chalana hai" naturally |
| **Bedrock-Native** | Fully on AWS, showcases Bedrock capabilities end-to-end |
