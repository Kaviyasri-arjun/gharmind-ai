# GHARMIND AI — Infrastructure & Deployment Architecture

---

## Overview

GHARMIND AI is deployed on AWS with a focus on:
- **Bedrock-native**: All AI workloads run through AWS Bedrock
- **Serverless where possible**: ECS Fargate for containers, no server management
- **Cost-efficient**: Right-sized for a hackathon demo, scalable for production
- **Single-region**: ap-south-1 (Mumbai) for India-first latency

---

## AWS Architecture Diagram

```
                              USERS (India)
                                   │
                          ┌────────▼────────┐
                          │   CloudFront     │
                          │  (CDN + WAF)     │
                          │  Edge Mumbai     │
                          └────────┬────────┘
                                   │
               ┌───────────────────┼──────────────────┐
               │                   │                  │
               ▼                   ▼                  ▼
     ┌─────────────────┐  ┌────────────────┐  ┌─────────────────┐
     │    Vercel        │  │  API Gateway   │  │  S3 (Static)    │
     │  (Next.js 15)   │  │  (REST + WS)   │  │  Assets/Media   │
     │                 │  │                │  │                 │
     │  Frontend CDN   │  │  Rate Limiting │  │                 │
     └─────────────────┘  └───────┬────────┘  └─────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
          ┌──────────────┐ ┌──────────┐ ┌──────────────┐
          │  ECS Fargate  │ │   ECS    │ │   ECS Fargate │
          │  FastAPI      │ │ Fargate  │ │  Twin Engine  │
          │  (API Service)│ │  Worker  │ │  (Scheduler)  │
          │               │ │  Service │ │               │
          │  - REST API   │ │          │ │  - 1min ticks │
          │  - WebSocket  │ │  - Async │ │  - Background │
          │  - Chat SSE   │ │  - Jobs  │ │    simulation │
          └──────┬────────┘ └────┬─────┘ └──────┬────────┘
                 │               │               │
                 └───────────────┼───────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
          ┌──────────────┐ ┌─────────┐ ┌──────────────┐
          │     RDS      │ │  Redis  │ │  EventBridge │
          │  PostgreSQL  │ │(ElastiC.)│ │              │
          │  16 +        │ │         │ │ - Scheduled  │
          │  pgvector    │ │ - Cache  │ │   events     │
          │              │ │ - Pub/Sub│ │ - Event bus  │
          │  Multi-AZ    │ │         │ │              │
          └──────────────┘ └─────────┘ └──────────────┘
                                │
                    ┌───────────▼────────────┐
                    │      AWS BEDROCK        │
                    │      ap-south-1         │
                    │                         │
                    │  Claude 3 Sonnet        │
                    │  Titan Embeddings       │
                    └─────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Supporting Services   │
                    │                         │
                    │  Cognito (Auth)         │
                    │  Secrets Manager        │
                    │  CloudWatch (Logging)   │
                    │  X-Ray (Tracing)        │
                    └─────────────────────────┘
```

---

## Service Specifications

### FastAPI — API Service (ECS Fargate)

```yaml
Service: gharmind-api
Image:   gharmind/backend:latest
CPU:     512 vCPU (0.5 vCPU)
Memory:  1024 MB
Count:   2 (auto-scale up to 10)
Port:    8000

Auto-scaling:
  - CPU > 70%: scale out
  - Request rate > 100 rps: scale out
  - Scale-in: 10 min cooldown

Health check:
  - GET /system/health → 200 OK
  - Interval: 30s, Timeout: 5s, Retries: 3

Environment Variables (from Secrets Manager):
  DATABASE_URL, REDIS_URL, AWS_REGION,
  BEDROCK_ENDPOINT, COGNITO_USER_POOL_ID,
  COGNITO_APP_CLIENT_ID
```

### Twin Engine — Background Service (ECS Fargate)

```yaml
Service: gharmind-twin-engine
Image:   gharmind/backend:latest
Command: python -m app.twin.runner  # Background scheduler
CPU:     256 vCPU
Memory:  512 MB
Count:   1 per active household batch

Scheduler: APScheduler
  - tick_all_households: every 60 seconds
  - prediction_pipeline: every 5 minutes
  - pattern_analyzer: every Sunday 2am IST
  - historical_sim: on-demand (onboarding)
```

### PostgreSQL — Amazon RDS

```yaml
Engine:   PostgreSQL 16.x
Instance: db.t3.medium (demo), db.r6g.large (production)
Storage:  100 GB gp3, auto-scaling to 500 GB
Multi-AZ: Yes
Backups:  7 day retention, daily snapshots

Extensions:
  - vector (pgvector 0.6.0+)
  - uuid-ossp
  - pg_trgm
  - btree_gist

Parameters:
  work_mem:                256MB
  maintenance_work_mem:    1GB
  shared_buffers:          25% of RAM
  max_connections:         200
```

### Redis — Amazon ElastiCache

```yaml
Engine:  Redis 7.x
Mode:    Serverless (or cache.t3.micro for demo)
Purpose:
  - HCO cache (TTL: 5 minutes)
  - Prediction cache (TTL: 5 minutes)
  - WebSocket pub/sub channel per household
  - Session cache for WS connections
  - Rate limiting counters
```

---

## Networking

```yaml
VPC: gharmind-vpc
  CIDR: 10.0.0.0/16

Subnets:
  Public (2 AZs):      10.0.1.0/24, 10.0.2.0/24
    → ALB, NAT Gateway

  Private App (2 AZs): 10.0.10.0/24, 10.0.11.0/24
    → ECS Fargate services

  Private DB (2 AZs):  10.0.20.0/24, 10.0.21.0/24
    → RDS, ElastiCache

Security Groups:
  alb-sg:           0.0.0.0/0:443 → ALB
  api-sg:           alb-sg:8000 → API service
  twin-sg:          api-sg:5432 → Twin engine
  db-sg:            api-sg:5432, twin-sg:5432 → RDS
  redis-sg:         api-sg:6379, twin-sg:6379 → ElastiCache
```

---

## IAM Roles & Policies

```json
// ECS Task Role — API Service
{
  "Role": "gharmind-api-task-role",
  "Policies": [
    "BedrockInvokePolicy",      // Invoke Claude + Titan
    "RDSConnectPolicy",          // Connect to RDS (IAM auth)
    "SecretsManagerReadPolicy",  // Read DB credentials
    "S3HouseholdMediaPolicy",    // R/W household media bucket
    "CognitoVerifyPolicy"        // Verify user tokens
  ]
}

// Bedrock IAM Policy
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:ap-south-1::foundation-model/anthropic.claude-3-sonnet-*",
    "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v1"
  ]
}
```

---

## CI/CD Pipeline

```
Developer Push to GitHub
        │
        ▼
  GitHub Actions CI
  ├── Python tests (pytest)
  ├── TypeScript check
  ├── Docker build (backend)
  ├── Dockerfile lint
  └── Security scan (Snyk)
        │
        ▼ (on main branch)
  Build & Push
  ├── ECR push: gharmind/backend:sha
  └── Vercel deploy: frontend
        │
        ▼
  ECS Blue-Green Deployment
  ├── Register new task definition
  ├── Update service (CodeDeploy)
  ├── Health check validation
  └── Traffic shift (10% → 100% over 5 min)
```

---

## Monitoring & Observability

```yaml
Logging:
  - CloudWatch Logs (all ECS services)
  - Log groups: /gharmind/api, /gharmind/twin, /gharmind/workers
  - Retention: 30 days

Metrics:
  - Custom CloudWatch metrics:
    - predictions_generated_per_household
    - bedrock_call_latency_p99
    - twin_tick_duration_ms
    - ws_connections_active
    - prediction_accuracy_rate

Alarms:
  - API error rate > 1%: PagerDuty alert
  - Bedrock call failure > 5%: alert + fallback
  - RDS CPU > 80%: alert
  - Twin tick delay > 90s: warning

Tracing:
  - AWS X-Ray for distributed tracing
  - Traces: API → Agent → Bedrock → DB
```

---

## Cost Estimate (Demo Scale — 100 households)

| Service | Monthly Cost |
|---|---|
| ECS Fargate (API, 2 tasks) | ~$30 |
| ECS Fargate (Twin engine) | ~$15 |
| RDS PostgreSQL (t3.medium) | ~$65 |
| ElastiCache Redis (t3.micro) | ~$20 |
| AWS Bedrock (100 hh × $8.50) | ~$850 |
| CloudFront + S3 | ~$10 |
| EventBridge | ~$5 |
| CloudWatch, X-Ray | ~$15 |
| **Total** | **~$1,010/month** |

*Production at 10,000 households: ~$35,000/month before volume discounts*

---

## Local Development Setup

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: gharmind
      POSTGRES_PASSWORD: devpassword

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:devpassword@postgres/gharmind
      REDIS_URL: redis://redis:6379
      AWS_REGION: us-east-1
      # Bedrock: uses local AWS credentials/profile
    volumes:
      - ./backend:/app
    depends_on: [postgres, redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_WS_URL: ws://localhost:8000
    depends_on: [backend]
```

---

## Hackathon Demo Environment

For the live hackathon demo:

| Component | Setup |
|---|---|
| Backend | Single ECS task, t3.small |
| Database | RDS t3.small (pre-seeded Sharma family data) |
| Redis | ElastiCache t3.micro |
| Frontend | Vercel free tier |
| Bedrock | Real AWS account, us-east-1 |
| Demo data | 30 days pre-simulated history |
| Seed script | `scripts/seed_demo_data.py` |

**Demo startup time**: < 30 seconds from cold start
**Demo twin ready**: Pre-initialized (no 90s wait during demo)
**Fallback**: If Bedrock unavailable, cached predictions shown
