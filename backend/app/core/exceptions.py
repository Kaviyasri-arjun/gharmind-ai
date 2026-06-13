"""
GHARMIND AI — Custom Exception Hierarchy
RFC 7807-compliant problem details for all HTTP errors.
"""
from typing import Any


class GharmindError(Exception):
    """Base exception for all GHARMIND AI errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "GHARMIND_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


# ── HTTP Exceptions ────────────────────────────────────────────────────


class NotFoundError(GharmindError):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} not found: {identifier}",
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class ForbiddenError(GharmindError):
    """Access denied to resource (403)."""

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message, error_code="FORBIDDEN")


class ConflictError(GharmindError):
    """Resource conflict (409)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, error_code="CONFLICT")


class ValidationError(GharmindError):
    """Input validation error (422)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        details = {"field": field} if field else {}
        super().__init__(message=message, error_code="VALIDATION_ERROR", details=details)


# ── Service Exceptions ─────────────────────────────────────────────────


class BedrockError(GharmindError):
    """AWS Bedrock service error."""

    def __init__(self, message: str, model_id: str = "") -> None:
        super().__init__(
            message=message,
            error_code="BEDROCK_ERROR",
            details={"model_id": model_id},
        )


class BedrockThrottleError(BedrockError):
    """AWS Bedrock rate limit exceeded."""

    def __init__(self, model_id: str = "") -> None:
        super().__init__(
            message="Bedrock rate limit exceeded — retrying",
            model_id=model_id,
        )
        self.error_code = "BEDROCK_THROTTLE"


class TwinEngineError(GharmindError):
    """Digital Twin engine error."""

    def __init__(self, message: str, household_id: str = "") -> None:
        super().__init__(
            message=message,
            error_code="TWIN_ENGINE_ERROR",
            details={"household_id": household_id},
        )


class PredictionError(GharmindError):
    """Prediction engine error."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, error_code="PREDICTION_ERROR")


class DatabaseError(GharmindError):
    """Database operation error."""

    def __init__(self, message: str, operation: str = "") -> None:
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={"operation": operation},
        )
