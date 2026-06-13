"""
GHARMIND AI — AWS Bedrock Claude Client
Wraps boto3 Bedrock Runtime for Claude 3 Sonnet invocations.
Supports standard JSON responses and streaming (SSE) for chat.
Includes retry logic with exponential backoff for throttle errors.
"""
from __future__ import annotations

import json
import time
from typing import Any, AsyncGenerator

import boto3
from botocore.exceptions import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.core.exceptions import BedrockError, BedrockThrottleError
from app.logging_config import get_logger

logger = get_logger(__name__)

# ── Mock responses for local development (no AWS needed) ──────────────

_MOCK_RESPONSES: dict[str, str] = {
    "prediction_enrichment": json.dumps({
        "predictions": [
            {
                "id": "mock-pred-001",
                "action_suggestion": "Motor abhi chalao — tank 38% hai, school bus 67 min mein hai.",
                "reasoning": "Historical pattern: motor runs 06:00-06:30 on weekdays. Current tank level is below 40% threshold. Diwali week multiplier active.",
                "risk_if_ignored": "Tank hits critical 20% by 8am — morning routine disrupted.",
            }
        ]
    }),
    "context_synthesis": json.dumps({
        "phase_of_day": "early_morning",
        "household_mood": "festive_preparation",
        "urgency_score": 68,
        "summary": "Festive Friday morning. Motor overdue. Extended pooja active.",
        "contextual_flags": ["diwali_prep_week", "motor_overdue", "power_cut_tonight"],
    }),
    "chat_response": "Haan Anjali ji! Motor abhi chalao — tank 38% hai aur Priya ka school bus 67 minute mein aayega. Diwali week mein paani zyada lagta hai.",
    "whatif_simulation": json.dumps({
        "result_summary": "Power cut at 7:30pm will cause Rahul's Zoom to drop and delay dinner by 105 minutes. Start dinner by 6:15pm to avoid disruption.",
        "overall_severity": "significant",
        "action_plan": [
            {"time": "18:15", "action": "Start dinner prep immediately"},
            {"time": "18:45", "action": "Charge all devices fully"},
            {"time": "19:15", "action": "Run water motor — last window before cut"},
            {"time": "19:30", "action": "Expected power cut — household prepared"},
        ],
        "risk_flags": [
            {"risk": "Rahul Zoom drops mid-call", "severity": "critical", "mitigation": "Reschedule or use mobile hotspot"},
            {"risk": "Dadi dinner at 9pm", "severity": "high", "mitigation": "Light snack at 7pm as backup"},
        ],
        "cascade_chain": [
            "Power cut → WiFi drops → Rahul Zoom drops",
            "Cooking not started → Dinner delayed to 8:45pm",
            "Motor missed tonight → Tomorrow morning risk",
        ],
    }),
}


def _get_mock_response(prompt_type: str) -> str:
    """Return a mock Claude response for local development."""
    return _MOCK_RESPONSES.get(prompt_type, "Mock response: Gharji is ready to help!")


class ClaudeClient:
    """
    AWS Bedrock Claude 3 Sonnet client.
    Provides synchronous and streaming invocation with automatic retries.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self.model_id = settings.BEDROCK_CLAUDE_MODEL_ID
        self.haiku_model_id = settings.BEDROCK_CLAUDE_HAIKU_MODEL_ID

    @property
    def client(self) -> Any:
        """Lazy-initialize boto3 Bedrock Runtime client."""
        if self._client is None:
            kwargs: dict[str, Any] = {"region_name": settings.BEDROCK_REGION}
            if settings.AWS_ACCESS_KEY_ID:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            self._client = boto3.client("bedrock-runtime", **kwargs)
        return self._client

    def _build_request_body(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """Build the Anthropic Messages API request body."""
        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            body["system"] = system_prompt
        return body

    @retry(
        retry=retry_if_exception_type((BedrockThrottleError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def invoke(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        use_haiku: bool = False,
        mock_key: str | None = None,
    ) -> str:
        """
        Invoke Claude and return the full text response.

        Args:
            messages: Anthropic-format message list
            system_prompt: Optional system instructions
            max_tokens: Max tokens in response
            temperature: Sampling temperature (lower = more deterministic)
            use_haiku: Use Haiku model (faster/cheaper for classification tasks)
            mock_key: If BEDROCK_MOCK_RESPONSES=True, return this mock key

        Returns:
            Full text response from Claude
        """
        if settings.BEDROCK_MOCK_RESPONSES:
            logger.debug("bedrock_mock_invoke", mock_key=mock_key)
            return _get_mock_response(mock_key or "chat_response")

        model = self.haiku_model_id if use_haiku else self.model_id
        body = self._build_request_body(messages, system_prompt, max_tokens, temperature)

        t0 = time.perf_counter()
        try:
            response = self.client.invoke_model(
                modelId=model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            response_body = json.loads(response["body"].read())
            content = response_body["content"][0]["text"]
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            logger.info(
                "bedrock_invoke_success",
                model=model,
                input_tokens=response_body.get("usage", {}).get("input_tokens", 0),
                output_tokens=response_body.get("usage", {}).get("output_tokens", 0),
                latency_ms=latency_ms,
            )
            return content

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("ThrottlingException", "TooManyRequestsException"):
                logger.warning("bedrock_throttle", model=model)
                raise BedrockThrottleError(model_id=model) from e
            logger.error("bedrock_client_error", model=model, error=str(e))
            raise BedrockError(message=str(e), model_id=model) from e

    async def invoke_structured(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        mock_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Invoke Claude expecting a JSON response.
        Automatically parses and returns as dict.
        """
        raw = await self.invoke(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.1,  # Lower temperature for consistent JSON
            mock_key=mock_key,
        )
        try:
            # Strip markdown code fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1])
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.warning("bedrock_json_parse_error", raw_response=raw[:200])
            raise BedrockError(
                message=f"Claude returned non-JSON response: {str(e)}"
            ) from e

    async def stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Stream Claude response tokens for real-time chat UI.
        Yields text chunks as they arrive.
        """
        if settings.BEDROCK_MOCK_RESPONSES:
            mock_text = _get_mock_response("chat_response")
            for word in mock_text.split():
                yield word + " "
            return

        body = self._build_request_body(
            messages, system_prompt, max_tokens, temperature=0.7
        )
        try:
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            stream = response.get("body")
            for event in stream:
                chunk = event.get("chunk")
                if chunk:
                    chunk_data = json.loads(chunk.get("bytes", b"{}").decode())
                    if chunk_data.get("type") == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield delta.get("text", "")
        except ClientError as e:
            logger.error("bedrock_stream_error", error=str(e))
            raise BedrockError(message=str(e), model_id=self.model_id) from e


# ── Singleton instance ─────────────────────────────────────────────────
claude_client = ClaudeClient()
