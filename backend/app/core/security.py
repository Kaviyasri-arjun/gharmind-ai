"""
GHARMIND AI — Security & Authentication
JWT verification via AWS Cognito. Skip-auth mode for local development.
"""
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the authenticated user extracted from JWT."""

    def __init__(
        self,
        user_id: str,
        email: str = "",
        household_id: str | None = None,
    ) -> None:
        self.user_id = user_id
        self.email = email
        self.household_id = household_id

    def __repr__(self) -> str:
        return f"CurrentUser(user_id={self.user_id})"


# ── Demo user for local development ───────────────────────────────────
DEMO_USER = CurrentUser(
    user_id="demo-user-001",
    email="anjali@sharma.in",
    household_id="550e8400-e29b-41d4-a716-446655440001",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """
    Extract and verify the current user from JWT.
    In development mode (SKIP_AUTH=True), returns a demo user.
    """
    if settings.SKIP_AUTH:
        return DEMO_USER

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # In production: verify Cognito JWT
        # payload = verify_cognito_token(token)
        # For now, raise to indicate production auth is needed
        raise NotImplementedError("Production Cognito auth not yet implemented")
    except Exception as e:
        logger.warning("auth_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_household_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> str:
    """Extract household_id from the current user."""
    if not current_user.household_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No household associated with this account",
        )
    return current_user.household_id
