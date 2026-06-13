# GHARMIND AI — AWS Bedrock Integration Design

---

## Bedrock Services Used

| Service | Model ID | Purpose |
|---|---|---|
| Amazon Bedrock | `anthropic.claude-3-sonnet-20240229-v1:0` | Reasoning, conversation, prediction enrichment |
| Amazon Bedrock | `amazon.titan-embed-text-v1` | Household context embeddings, semantic memory |
| Amazon Bedrock | `anthropic.claude-3-haiku-20240307-v1:0` | Fast classification, short summaries (cost optimization) |

---

## Architecture

```
FastAPI Application
       │
       │  boto3 bedrock-runtime client
       ▼
┌─────────────────────────────────────────────────┐
│              AWS Bedrock Runtime                 │
│         (us-east-1 or ap-south-1)               │
│                                                  │
│   ┌──────────────────┐   ┌─────────────────────┐│
│   │  Claude 3 Sonnet  │   │  Titan Embed Text   ││
│   │  invoke_model()   │   │  invoke_model()     ││
│   │                   │   │                     ││
│   │  - Streaming      │   │  - Batch embed      ││
│   │  - JSON mode      │   │  - 1536 dimensions  ││
│   │  - Tool use       │   │  - ~100ms latency   ││
│   └──────────────────┘   └─────────────────────┘│
└─────────────────────────────────────────────────┘
       │
       │  Embeddings → PostgreSQL pgvector
       │  Completions → Response objects
       ▼
   Application Logic
```

---

## Claude Sonnet — Invocation Design

### Request Configuration

```python
# Model invocation parameters
CLAUDE_CONFIG = {
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "max_tokens": 2048,
    "temperature": 0.3,        # Lower = more deterministic for predictions
    "top_p": 0.9,
    "stop_sequences": [],
    "anthropic_version": "bedrock-2023-05-31"
}

# For streaming responses (chat interface)
CLAUDE_STREAMING_CONFIG = {
    **CLAUDE_CONFIG,
    "stream": True
}

# For structured JSON output (predictions, context)
CLAUDE_STRUCTURED_CONFIG = {
    **CLAUDE_CONFIG,
    "temperature": 0.1,        # Very deterministic for JSON output
    "max_tokens": 1024
}
```

### Message Structure

```python
# Standard prediction enrichment call
def build_prediction_message(context: HouseholdContext, raw_predictions: list) -> dict:
    return {
        "messages": [
            {
                "role": "user",
                "content": f"""
You are the prediction engine for GHARMIND AI, a household operating system.

CURRENT HOUSEHOLD CONTEXT:
{context.to_json()}

RAW PREDICTIONS (from pattern engine):
{json.dumps(raw_predictions, indent=2)}

For each prediction, provide:
1. A natural language action suggestion (in {context.language_preference})
2. A brief reasoning chain (2-3 sentences)
3. Any risks or dependencies I should flag

Respond in valid JSON format matching this schema:
{PREDICTION_ENRICHMENT_SCHEMA}
"""
            }
        ]
    }
```

---

## Titan Embeddings — Configuration

### Embedding Dimensions & Use Cases

```python
TITAN_EMBED_CONFIG = {
    "model_id": "amazon.titan-embed-text-v1",
    "dimensions": 1536,         # Fixed for titan-embed-text-v1
    "normalize": True           # L2 normalization for cosine similarity
}

# Text size limits
MAX_EMBED_CHARS = 8000         # Titan's input limit
CONTEXT_SUMMARY_MAX = 500      # Keep summaries concise for embedding
```

### What Gets Embedded

| Data | Text Template | Vector Table Column |
|---|---|---|
| Household context snapshot | `"Monday morning, Diwali week, 6:15am IST. Pooja active, motor overdue..."` | `twin_state_snapshots.context_embedding` |
| Household memory | Content field verbatim | `household_memories.embedding` |
| Routine pattern | `"Routine: {name}. Runs at {time} on {days}. Involves {members}. During {season}."` | `routines.pattern_embedding` |

### Similarity Search Pattern

```python
# Find memories relevant to current context
async def find_relevant_memories(
    household_id: UUID,
    context_text: str,
    top_k: int = 5,
    memory_type: str | None = None
) -> list[HouseholdMemory]:

    # 1. Embed current context
    embedding = await titan_client.embed(context_text)

    # 2. pgvector cosine similarity search
    query = """
        SELECT id, title, content, memory_type, confidence,
               1 - (embedding <=> $1::vector) AS similarity
        FROM household_memories
        WHERE household_id = $2
          AND ($3::VARCHAR IS NULL OR memory_type = $3)
          AND confidence > 0.5
        ORDER BY embedding <=> $1::vector
        LIMIT $4
    """

    results = await db.fetch(query, embedding, household_id, memory_type, top_k)
    return [HouseholdMemory(**r) for r in results if r['similarity'] > 0.7]
```

---

## Prompt Templates

### 1. Context Synthesis Prompt

```
System: You are the ContextAgent for GHARMIND AI.
Your job is to synthesize household state into a structured context object.
Always output valid JSON.

User: Synthesize the following household data into a context object:

TWIN STATE:
{twin_state_json}

CALENDAR:
- Current IST time: {ist_time}
- Day: {day_of_week}
- Season: {season}
- Active festivals: {festivals}
- School status: {school_status}

FAMILY STATUS:
{member_status_summary}

RECENT PATTERNS:
{recent_3_pattern_descriptions}

SIMILAR PAST CONTEXTS (from memory):
{top_3_similar_memories}

Output a Household Context Object with fields:
phase_of_day, household_mood, active_routines, imminent_routines,
key_members, contextual_flags, summary, urgency_score (0-100)
```

### 2. Prediction Enrichment Prompt

```
System: You are the PredictionAgent for GHARMIND AI.
Generate actionable household predictions in {language}.
Be specific, practical, and aware of Indian household customs.

User: Given this household context:
{hco_summary}

Enrich these pattern-detected predictions:
{raw_predictions_json}

For each prediction provide:
- action_suggestion: What the family should do (in {language})
- reasoning: Why you're confident (2-3 sentences)
- dependencies: Other events this prediction depends on
- risk_if_ignored: What happens if family ignores this

JSON output only.
```

### 3. Reasoning / Conversation Prompt

```
System: You are Gharji, the AI companion for the {household_name} family.
{gharji_personality_description}

Current household context:
{hco_json}

Recent predictions:
{top_5_predictions_summary}

Memory context:
{relevant_memories_summary}

Respond in {language_preference}. Be warm, practical, culturally aware.
Maximum 150 words unless a detailed plan is requested.

User: {user_message}
```

### 4. What-If Simulation Prompt

```
System: You are the WhatIfAgent for GHARMIND AI.
You simulate household scenarios by reasoning about cause and effect.

HOUSEHOLD PROFILE:
{household_summary}

NORMAL HOUSEHOLD STATE (baseline):
{baseline_state_json}

SCENARIO BEING TESTED:
{scenario_description}

PERTURBATIONS APPLIED:
{perturbations_json}

SIMULATION WINDOW: {start_time} to {end_time}

Simulate the household's day with these perturbations active.
For each major routine, describe: what changes, what risk exists, what to do.
Output a structured impact analysis and risk flags.
```

---

## Error Handling & Resilience

```python
class BedrockClientError(Exception):
    pass

class BedrockThrottleError(BedrockClientError):
    pass

# Retry strategy for Bedrock calls
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay_ms": 500,
    "backoff_multiplier": 2.0,
    "retry_on": [
        "ThrottlingException",
        "ServiceUnavailableException",
        "ModelTimeoutException"
    ]
}

# Fallback: if Bedrock unavailable, use cached predictions
# No prediction is always better than a crash
```

---

## IAM Policy (Least Privilege)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
            ]
        }
    ]
}
```

---

## Cost Model (Estimated, per household per month)

| Component | Usage | Cost Estimate |
|---|---|---|
| Context generation (Titan) | 288 calls/day × 30 | ~$0.30 |
| Prediction enrichment (Claude Sonnet) | 288 calls/day, 500 tok each | ~$4.50 |
| User conversations (Claude Sonnet) | ~30 calls/day, 1000 tok each | ~$2.50 |
| What-If simulations (Claude Sonnet) | ~10 calls/day, 2000 tok each | ~$1.20 |
| **Total per household** | | **~$8.50/month** |

*Pricing based on Claude 3 Sonnet: $0.003/1K input tokens, $0.015/1K output tokens*
*Aggressive caching reduces real cost by ~40%*
